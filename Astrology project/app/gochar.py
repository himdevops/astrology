"""
gochar.py — Gochar (Transit) Panchang Engine

Calculates all planet transit events over a date range:
- Sign (Rashi) changes
- Nakshatra changes
- Pada changes
- Retrograde start/end dates
- Current positions with degrees

Like Drik Panchang's transit calendar but for all 9 planets.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import swisseph as swe

from app.core import PLANETS, SIGNS, AYANAMSA_MAP, normalize_degree, degree_to_sign
from app.nakshatra import NAKSHATRAS, NAKSHATRA_SPAN_DEG, PADA_SPAN_DEG, get_nakshatra


# ─────────────────────────────────────────────────────────────
# Planet scanning step sizes (days) — smaller = more precise
# ─────────────────────────────────────────────────────────────
PLANET_STEP = {
    "Moon":    0.5,     # Moon moves ~13°/day, changes sign every ~2.25 days
    "Sun":     1.0,     # ~1°/day
    "Mercury": 0.5,     # fast, can be retrograde
    "Venus":   0.5,     # fast, can be retrograde
    "Mars":    1.0,     # ~0.5°/day
    "Jupiter": 2.0,     # ~0.08°/day (slow)
    "Saturn":  3.0,     # ~0.03°/day (very slow)
    "Rahu":    3.0,     # ~0.05°/day (always retrograde)
    "Ketu":    3.0,     # same as Rahu
}

# Planets that are always retrograde (skip retro detection)
ALWAYS_RETRO = {"Rahu", "Ketu"}
NEVER_RETRO = {"Sun", "Moon"}

# Planet display colors
PLANET_COLORS = {
    "Sun": "#FFA500", "Moon": "#C0C0C0", "Mars": "#FF4444",
    "Mercury": "#00CED1", "Jupiter": "#FFD700", "Venus": "#FF69B4",
    "Saturn": "#4169E1", "Rahu": "#8B008B", "Ketu": "#808080",
    "Lagna": "#00FF88",
}


def _get_sidereal_longitude(jd_ut: float, planet_id: int, ayanamsa_key: str) -> tuple:
    """Get sidereal longitude and speed for a planet at a given JD."""
    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    result = swe.calc_ut(jd_ut, planet_id, flags)
    xx = result[0]
    return normalize_degree(xx[0]), xx[3]  # longitude, speed


def _jd_to_datetime(jd: float, tz_offset_minutes: int = 330) -> datetime:
    """Convert Julian Day to datetime with timezone offset."""
    # swe.revjul returns UTC
    y, m, d, h = swe.revjul(jd)
    hours = int(h)
    minutes = int((h - hours) * 60)
    utc_dt = datetime(y, m, d, hours, minutes)
    return utc_dt + timedelta(minutes=tz_offset_minutes)


def _datetime_to_jd(dt: datetime, tz_offset_minutes: int = 330) -> float:
    """Convert datetime (local) to Julian Day UTC."""
    utc_dt = dt - timedelta(minutes=tz_offset_minutes)
    return swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0 + utc_dt.second / 3600.0,
    )


def _get_sign_index(longitude: float) -> int:
    """Get zodiac sign index (0-11) from longitude."""
    return int(longitude / 30) % 12


def _get_nakshatra_index(longitude: float) -> int:
    """Get nakshatra index (0-26) from longitude."""
    return int(longitude / NAKSHATRA_SPAN_DEG) % 27


def _get_pada(longitude: float) -> int:
    """Get pada (1-4) from longitude."""
    nak_start = int(longitude / NAKSHATRA_SPAN_DEG) * NAKSHATRA_SPAN_DEG
    deg_in_nak = longitude - nak_start
    return min(int(deg_in_nak / PADA_SPAN_DEG) + 1, 4)


def _bisect_event(jd_start: float, jd_end: float, planet_id: int,
                  ayanamsa_key: str, check_fn, precision: float = 0.001) -> float:
    """
    Binary search to find the exact JD when a transit event occurs.
    check_fn(longitude) should return True for the 'before' state and
    False for the 'after' state (or vice versa — just needs to change).
    precision: in days (~1.4 minutes at 0.001)
    """
    lo, hi = jd_start, jd_end
    val_lo = check_fn(*_get_sidereal_longitude(lo, planet_id, ayanamsa_key))

    for _ in range(50):  # max iterations
        if (hi - lo) < precision:
            break
        mid = (lo + hi) / 2.0
        val_mid = check_fn(*_get_sidereal_longitude(mid, planet_id, ayanamsa_key))
        if val_mid == val_lo:
            lo = mid
        else:
            hi = mid

    return hi  # return the moment of change


def _get_lagna_longitude(jd_ut: float, lat: float, lon: float, ayanamsa_key: str) -> float:
    """Get sidereal Ascendant longitude for a given JD and location."""
    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL
    cusps, ascmc = swe.houses_ex(jd_ut, lat, lon, b'P', flags)
    return normalize_degree(ascmc[0])  # ascmc[0] = Ascendant


def _scan_lagna_transits(
    jd_start: float, jd_end: float,
    lat: float, lon: float,
    ayanamsa_key: str, tz_offset_minutes: int,
) -> List[Dict]:
    """Scan Lagna sign, nakshatra, pada changes. Step=0.04 days (~58 min)."""
    events = []
    step = 0.04  # ~58 minutes — Lagna changes sign every ~2 hours

    jd = jd_start
    prev_lon = _get_lagna_longitude(jd, lat, lon, ayanamsa_key)
    prev_sign = _get_sign_index(prev_lon)
    prev_nak = _get_nakshatra_index(prev_lon)
    prev_pada = _get_pada(prev_lon)

    while jd < jd_end:
        jd_next = min(jd + step, jd_end)
        cur_lon = _get_lagna_longitude(jd_next, lat, lon, ayanamsa_key)
        cur_sign = _get_sign_index(cur_lon)
        cur_nak = _get_nakshatra_index(cur_lon)
        cur_pada = _get_pada(cur_lon)

        # ── Lagna Sign Change ──
        if cur_sign != prev_sign:
            # Bisect for exact moment
            lo, hi = jd, jd_next
            for _ in range(40):
                if (hi - lo) < 0.0005:  # ~43 seconds precision
                    break
                mid = (lo + hi) / 2.0
                mid_lon = _get_lagna_longitude(mid, lat, lon, ayanamsa_key)
                if _get_sign_index(mid_lon) == prev_sign:
                    lo = mid
                else:
                    hi = mid
            exact_dt = _jd_to_datetime(hi, tz_offset_minutes)
            events.append({
                "jd":          hi,
                "planet":      "Lagna",
                "event_type":  "sign_change",
                "datetime":    exact_dt.strftime("%Y-%m-%d %H:%M"),
                "date":        exact_dt.strftime("%Y-%m-%d"),
                "time":        exact_dt.strftime("%H:%M"),
                "from_sign":   SIGNS[prev_sign],
                "to_sign":     SIGNS[cur_sign],
                "description": f"Lagna enters {SIGNS[cur_sign]}",
                "color":       PLANET_COLORS.get("Lagna", "#00FF88"),
                "importance":  "medium",
            })

        # ── Lagna Nakshatra Change ──
        if cur_nak != prev_nak:
            lo, hi = jd, jd_next
            for _ in range(40):
                if (hi - lo) < 0.0005:
                    break
                mid = (lo + hi) / 2.0
                mid_lon = _get_lagna_longitude(mid, lat, lon, ayanamsa_key)
                if _get_nakshatra_index(mid_lon) == prev_nak:
                    lo = mid
                else:
                    hi = mid
            exact_dt = _jd_to_datetime(hi, tz_offset_minutes)
            events.append({
                "jd":              hi,
                "planet":          "Lagna",
                "event_type":      "nakshatra_change",
                "datetime":        exact_dt.strftime("%Y-%m-%d %H:%M"),
                "date":            exact_dt.strftime("%Y-%m-%d"),
                "time":            exact_dt.strftime("%H:%M"),
                "from_nakshatra":  NAKSHATRAS[prev_nak]["name"],
                "to_nakshatra":    NAKSHATRAS[cur_nak]["name"],
                "to_nak_lord":     NAKSHATRAS[cur_nak]["lord"],
                "description":     f"Lagna enters {NAKSHATRAS[cur_nak]['name']} ({NAKSHATRAS[cur_nak]['lord']})",
                "color":           PLANET_COLORS.get("Lagna", "#00FF88"),
                "importance":      "low",
            })

        # ── Lagna Pada Change ──
        if cur_pada != prev_pada and cur_nak == prev_nak:
            lo, hi = jd, jd_next
            for _ in range(40):
                if (hi - lo) < 0.0005:
                    break
                mid = (lo + hi) / 2.0
                mid_lon = _get_lagna_longitude(mid, lat, lon, ayanamsa_key)
                if _get_pada(mid_lon) == prev_pada:
                    lo = mid
                else:
                    hi = mid
            exact_dt = _jd_to_datetime(hi, tz_offset_minutes)
            events.append({
                "jd":          hi,
                "planet":      "Lagna",
                "event_type":  "pada_change",
                "datetime":    exact_dt.strftime("%Y-%m-%d %H:%M"),
                "date":        exact_dt.strftime("%Y-%m-%d"),
                "time":        exact_dt.strftime("%H:%M"),
                "nakshatra":   NAKSHATRAS[cur_nak]["name"],
                "from_pada":   prev_pada,
                "to_pada":     cur_pada,
                "description": f"Lagna enters {NAKSHATRAS[cur_nak]['name']} Pada {cur_pada}",
                "color":       PLANET_COLORS.get("Lagna", "#00FF88"),
                "importance":  "low",
            })

        prev_lon = cur_lon
        prev_sign = cur_sign
        prev_nak = cur_nak
        prev_pada = cur_pada
        jd = jd_next

    return events


def calculate_gochar_transits(
    start_date: datetime,
    end_date: datetime,
    ayanamsa: str = "lahiri",
    tz_offset_minutes: int = 330,
    planets_filter: Optional[List[str]] = None,
    latitude: Optional[float] = None,
    longitude: Optional[float] = None,
) -> Dict:
    """
    Calculate all transit events for all planets over the given date range.

    Returns:
    - events: chronological list of all transit events
    - planet_positions: current position snapshot for each planet at start_date
    - planet_summaries: per-planet summary of sign/nakshatra stays
    """
    ayanamsa_key = ayanamsa.lower()
    if ayanamsa_key not in AYANAMSA_MAP:
        raise ValueError(f"Unsupported ayanamsa: {ayanamsa}")

    default_planets = [
        "Sun", "Moon", "Mars", "Mercury", "Jupiter",
        "Venus", "Saturn", "Rahu", "Ketu",
    ]
    if latitude is not None and longitude is not None:
        default_planets.append("Lagna")
    planet_list = planets_filter or default_planets

    jd_start = _datetime_to_jd(start_date, tz_offset_minutes)
    jd_end = _datetime_to_jd(end_date, tz_offset_minutes)

    all_events = []
    planet_positions = []
    planet_summaries = {}

    for planet_name in planet_list:
        # ── Lagna (Ascendant) — separate calculation ──
        if planet_name == "Lagna":
            if latitude is None or longitude is None:
                continue  # skip if no location provided
            events = _scan_lagna_transits(
                jd_start, jd_end, latitude, longitude,
                ayanamsa_key, tz_offset_minutes,
            )
            all_events.extend(events)

            # Current Lagna position at start
            lon = _get_lagna_longitude(jd_start, latitude, longitude, ayanamsa_key)
            sign, deg_in_sign = degree_to_sign(lon)
            nak_info = get_nakshatra(lon)
            pada = _get_pada(lon)
            # Lagna speed ~1 sign/2hrs ≈ 15°/hr ≈ 360°/day
            planet_positions.append({
                "planet":         "Lagna",
                "longitude":      round(lon, 4),
                "sign":           sign,
                "degree_in_sign": round(deg_in_sign, 4),
                "nakshatra":      nak_info["nakshatra"],
                "nakshatra_lord": nak_info["lord"],
                "pada":           pada,
                "speed":          360.0,
                "retrograde":     False,
                "color":          PLANET_COLORS.get("Lagna", "#00FF88"),
            })

            sign_changes = [e for e in events if e["event_type"] == "sign_change"]
            nak_changes = [e for e in events if e["event_type"] == "nakshatra_change"]
            pada_changes = [e for e in events if e["event_type"] == "pada_change"]
            planet_summaries["Lagna"] = {
                "sign_changes":     len(sign_changes),
                "nakshatra_changes": len(nak_changes),
                "pada_changes":     len(pada_changes),
                "retro_events":     0,
                "total_events":     len(events),
            }
            continue

        if planet_name == "Ketu":
            # Ketu = Rahu + 180°, use Rahu's planet ID
            planet_id = PLANETS["Rahu"]
            is_ketu = True
        else:
            planet_id = PLANETS.get(planet_name)
            is_ketu = False
            if planet_id is None:
                continue

        step = PLANET_STEP.get(planet_name, 1.0)
        events = _scan_planet_transits(
            planet_name, planet_id, is_ketu,
            jd_start, jd_end, step,
            ayanamsa_key, tz_offset_minutes,
        )
        all_events.extend(events)

        # Current position at start
        lon, spd = _get_sidereal_longitude(jd_start, planet_id, ayanamsa_key)
        if is_ketu:
            lon = normalize_degree(lon + 180)
            spd = -abs(spd)  # Ketu always retrograde
        sign, deg_in_sign = degree_to_sign(lon)
        nak_info = get_nakshatra(lon)
        pada = _get_pada(lon)

        planet_positions.append({
            "planet":         planet_name,
            "longitude":      round(lon, 4),
            "sign":           sign,
            "degree_in_sign": round(deg_in_sign, 4),
            "nakshatra":      nak_info["nakshatra"],
            "nakshatra_lord": nak_info["lord"],
            "pada":           pada,
            "speed":          round(spd, 4),
            "retrograde":     spd < 0,
            "color":          PLANET_COLORS.get(planet_name, "#888"),
        })

        # Summary for this planet
        sign_changes = [e for e in events if e["event_type"] == "sign_change"]
        nak_changes = [e for e in events if e["event_type"] == "nakshatra_change"]
        pada_changes = [e for e in events if e["event_type"] == "pada_change"]
        retro_events = [e for e in events if e["event_type"] in ("retro_start", "retro_end")]

        planet_summaries[planet_name] = {
            "sign_changes":     len(sign_changes),
            "nakshatra_changes": len(nak_changes),
            "pada_changes":     len(pada_changes),
            "retro_events":     len(retro_events),
            "total_events":     len(events),
        }

    # Sort all events chronologically
    all_events.sort(key=lambda e: e["jd"])

    # Remove internal jd from output
    for e in all_events:
        del e["jd"]

    return {
        "start_date":        start_date.strftime("%Y-%m-%d"),
        "end_date":          end_date.strftime("%Y-%m-%d"),
        "ayanamsa":          ayanamsa,
        "total_events":      len(all_events),
        "events":            all_events,
        "planet_positions":  planet_positions,
        "planet_summaries":  planet_summaries,
    }


def _scan_planet_transits(
    planet_name: str,
    planet_id: int,
    is_ketu: bool,
    jd_start: float,
    jd_end: float,
    step: float,
    ayanamsa_key: str,
    tz_offset_minutes: int,
) -> List[Dict]:
    """Scan a single planet for all transit events in the date range."""
    events = []

    jd = jd_start
    prev_lon, prev_speed = _get_sidereal_longitude(jd, planet_id, ayanamsa_key)
    if is_ketu:
        prev_lon = normalize_degree(prev_lon + 180)
        prev_speed = -abs(prev_speed)

    prev_sign = _get_sign_index(prev_lon)
    prev_nak = _get_nakshatra_index(prev_lon)
    prev_pada = _get_pada(prev_lon)
    prev_retro = prev_speed < 0

    while jd < jd_end:
        jd_next = min(jd + step, jd_end)
        cur_lon, cur_speed = _get_sidereal_longitude(jd_next, planet_id, ayanamsa_key)
        if is_ketu:
            cur_lon = normalize_degree(cur_lon + 180)
            cur_speed = -abs(cur_speed)

        cur_sign = _get_sign_index(cur_lon)
        cur_nak = _get_nakshatra_index(cur_lon)
        cur_pada = _get_pada(cur_lon)
        cur_retro = cur_speed < 0

        # ── Sign Change ──
        if cur_sign != prev_sign:
            # Bisect to find exact moment
            exact_jd = _bisect_event(
                jd, jd_next, planet_id, ayanamsa_key,
                lambda lon, spd: _get_sign_index(
                    normalize_degree(lon + 180) if is_ketu else lon
                ) == prev_sign,
            )
            exact_dt = _jd_to_datetime(exact_jd, tz_offset_minutes)
            events.append({
                "jd":            exact_jd,
                "planet":        planet_name,
                "event_type":    "sign_change",
                "datetime":      exact_dt.strftime("%Y-%m-%d %H:%M"),
                "date":          exact_dt.strftime("%Y-%m-%d"),
                "time":          exact_dt.strftime("%H:%M"),
                "from_sign":     SIGNS[prev_sign],
                "to_sign":       SIGNS[cur_sign],
                "description":   f"{planet_name} enters {SIGNS[cur_sign]}",
                "color":         PLANET_COLORS.get(planet_name, "#888"),
                "importance":    "high",
            })

        # ── Nakshatra Change ──
        if cur_nak != prev_nak:
            exact_jd = _bisect_event(
                jd, jd_next, planet_id, ayanamsa_key,
                lambda lon, spd: _get_nakshatra_index(
                    normalize_degree(lon + 180) if is_ketu else lon
                ) == prev_nak,
            )
            exact_dt = _jd_to_datetime(exact_jd, tz_offset_minutes)
            events.append({
                "jd":            exact_jd,
                "planet":        planet_name,
                "event_type":    "nakshatra_change",
                "datetime":      exact_dt.strftime("%Y-%m-%d %H:%M"),
                "date":          exact_dt.strftime("%Y-%m-%d"),
                "time":          exact_dt.strftime("%H:%M"),
                "from_nakshatra": NAKSHATRAS[prev_nak]["name"],
                "to_nakshatra":  NAKSHATRAS[cur_nak]["name"],
                "to_nak_lord":   NAKSHATRAS[cur_nak]["lord"],
                "description":   f"{planet_name} enters {NAKSHATRAS[cur_nak]['name']} ({NAKSHATRAS[cur_nak]['lord']})",
                "color":         PLANET_COLORS.get(planet_name, "#888"),
                "importance":    "medium",
            })

        # ── Pada Change (only if same nakshatra, otherwise covered by nak change) ──
        if cur_pada != prev_pada and cur_nak == prev_nak:
            exact_jd = _bisect_event(
                jd, jd_next, planet_id, ayanamsa_key,
                lambda lon, spd: _get_pada(
                    normalize_degree(lon + 180) if is_ketu else lon
                ) == prev_pada,
            )
            exact_dt = _jd_to_datetime(exact_jd, tz_offset_minutes)
            events.append({
                "jd":            exact_jd,
                "planet":        planet_name,
                "event_type":    "pada_change",
                "datetime":      exact_dt.strftime("%Y-%m-%d %H:%M"),
                "date":          exact_dt.strftime("%Y-%m-%d"),
                "time":          exact_dt.strftime("%H:%M"),
                "nakshatra":     NAKSHATRAS[cur_nak]["name"],
                "from_pada":     prev_pada,
                "to_pada":       cur_pada,
                "description":   f"{planet_name} enters {NAKSHATRAS[cur_nak]['name']} Pada {cur_pada}",
                "color":         PLANET_COLORS.get(planet_name, "#888"),
                "importance":    "low",
            })

        # ── Retrograde Start/End ──
        if planet_name not in ALWAYS_RETRO and planet_name not in NEVER_RETRO:
            if cur_retro != prev_retro:
                exact_jd = _bisect_event(
                    jd, jd_next, planet_id, ayanamsa_key,
                    lambda lon, spd: (spd < 0) == prev_retro,
                )
                exact_dt = _jd_to_datetime(exact_jd, tz_offset_minutes)
                exact_lon, _ = _get_sidereal_longitude(exact_jd, planet_id, ayanamsa_key)
                if is_ketu:
                    exact_lon = normalize_degree(exact_lon + 180)
                exact_sign, exact_deg = degree_to_sign(exact_lon)

                event_type = "retro_start" if cur_retro else "retro_end"
                label = "goes Retrograde" if cur_retro else "goes Direct"
                events.append({
                    "jd":            exact_jd,
                    "planet":        planet_name,
                    "event_type":    event_type,
                    "datetime":      exact_dt.strftime("%Y-%m-%d %H:%M"),
                    "date":          exact_dt.strftime("%Y-%m-%d"),
                    "time":          exact_dt.strftime("%H:%M"),
                    "sign":          exact_sign,
                    "degree":        round(exact_deg, 2),
                    "longitude":     round(exact_lon, 4),
                    "description":   f"{planet_name} {label} at {exact_deg:.2f}° {exact_sign}",
                    "color":         PLANET_COLORS.get(planet_name, "#888"),
                    "importance":    "high",
                })

        # Update previous values
        prev_lon = cur_lon
        prev_speed = cur_speed
        prev_sign = cur_sign
        prev_nak = cur_nak
        prev_pada = cur_pada
        prev_retro = cur_retro
        jd = jd_next

    return events
