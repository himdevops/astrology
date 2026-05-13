"""
astro_events.py — Astrological Events Engine
=============================================
Calculates 9 types of planetary events over a date range:
1. Planets Combustion (planets too close to Sun)
2. Planets Retrograde (start/end dates)
3. Planets Transit (sign ingress)
4. Planetary Positions (daily snapshot)
5. Planets Mutual Aspects (Vedic drishti)
6. Lunar Aspects (Moon's aspects to other planets)
7. Planets Mutual Parallel (same declination)
8. Planets Ecliptic Crossings (latitude = 0)
9. Graha Yuddha (Planetary War — planets within 1°)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import swisseph as swe

from app.core import (
    AYANAMSA_MAP,
    PLANETS,
    SIGNS,
    normalize_degree,
    degree_to_sign,
    to_julian_day_utc,
)

# Combustion orbs per planet (degrees from Sun that render planet combust)
COMBUSTION_ORBS = {
    "Moon": 12.0,
    "Mars": 17.0,
    "Mercury": 14.0,   # 12° direct, 14° retrograde — use max
    "Jupiter": 11.0,
    "Venus": 10.0,      # 8° direct, 10° retrograde — use max
    "Saturn": 15.0,
}

# Vedic aspects (graha drishti): planet → list of house-offsets it aspects
# Every planet aspects 7th (180°). Mars also 4th & 8th, Jupiter 5th & 9th, Saturn 3rd & 10th
VEDIC_ASPECT_OFFSETS = {
    "Sun":     [180],
    "Moon":    [180],
    "Mercury": [180],
    "Venus":   [180],
    "Mars":    [90, 180, 210],        # 4th, 7th, 8th
    "Jupiter": [120, 180, 240],       # 5th, 7th, 9th
    "Saturn":  [60, 180, 270],        # 3rd, 7th, 10th
    "Rahu":    [120, 180, 240],       # 5th, 7th, 9th (like Jupiter)
    "Ketu":    [120, 180, 240],       # 5th, 7th, 9th (like Jupiter)
}

# Aspect orb for mutual aspect detection (degrees)
ASPECT_ORB = 8.0

# Parallel orb (declination difference)
PARALLEL_ORB = 1.0

# Graha Yuddha (planetary war) max distance
YUDDHA_ORB = 1.0

# Planets involved in Graha Yuddha (only Tara Grahas — Mars, Mercury, Jupiter, Venus, Saturn)
YUDDHA_PLANETS = {"Mars", "Mercury", "Jupiter", "Venus", "Saturn"}


def _jd_for_date(dt: datetime, tz_offset: int) -> float:
    """Convert datetime to Julian Day in UT."""
    return to_julian_day_utc(dt, tz_offset)


def _calc_planet_lon(jd: float, planet_id: int, ayanamsa_key: str, sidereal: bool = True) -> tuple:
    """Calculate sidereal longitude and speed for a planet at given JD."""
    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if sidereal:
        flags |= swe.FLG_SIDEREAL
    result = swe.calc_ut(jd, planet_id)
    xx = result[0]
    return normalize_degree(xx[0]), xx[3]  # lon, speed


def _calc_planet_lat_decl(jd: float, planet_id: int) -> tuple:
    """Get ecliptic latitude and equatorial declination (tropical)."""
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    result = swe.calc_ut(jd, planet_id, flags)
    xx = result[0]
    ecl_lat = xx[1]  # ecliptic latitude

    # Get equatorial coords for declination
    flags_eq = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    result_eq = swe.calc_ut(jd, planet_id, flags_eq)
    decl = result_eq[0][1]  # declination

    return ecl_lat, decl


def _get_all_positions(jd: float, ayanamsa_key: str) -> Dict[str, Dict]:
    """Get all planet positions at a given JD."""
    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    positions = {}

    rahu_degree = None
    for name, planet_id in PLANETS.items():
        result = swe.calc_ut(jd, planet_id, flags)
        xx = result[0]
        lon = normalize_degree(xx[0])
        speed = xx[3]
        sign, deg_in_sign = degree_to_sign(lon)
        positions[name] = {
            "longitude": round(lon, 4),
            "speed": round(speed, 6),
            "sign": sign,
            "degree_in_sign": round(deg_in_sign, 4),
            "retrograde": speed < 0,
        }
        if name == "Rahu":
            rahu_degree = lon

    if rahu_degree is not None:
        ketu_lon = normalize_degree(rahu_degree + 180)
        sign_k, deg_k = degree_to_sign(ketu_lon)
        positions["Ketu"] = {
            "longitude": round(ketu_lon, 4),
            "speed": -1.0,
            "sign": sign_k,
            "degree_in_sign": round(deg_k, 4),
            "retrograde": True,
        }

    return positions


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes."""
    diff = abs(lon1 - lon2) % 360
    return min(diff, 360 - diff)


def _date_from_jd(jd: float, tz_offset: int) -> str:
    """Convert JD back to date string."""
    y, m, d, h = swe.revjul(jd)
    utc_dt = datetime(y, m, d, int(h), int((h % 1) * 60))
    local_dt = utc_dt + timedelta(minutes=tz_offset)
    return local_dt.strftime("%Y-%m-%d %H:%M")


# ═══════════════════════════════════════════════════════════════
# 1. PLANETS COMBUSTION
# ═══════════════════════════════════════════════════════════════

def calc_combustion(start_jd: float, end_jd: float, step: float,
                    ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """Find periods when planets are combust (too close to Sun)."""
    events = []
    combust_state = {}  # planet → currently_combust

    jd = start_jd
    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)
        sun_lon = positions.get("Sun", {}).get("longitude", 0)

        for planet, orb in COMBUSTION_ORBS.items():
            if planet not in positions:
                continue
            p_lon = positions[planet]["longitude"]
            dist = _angular_distance(sun_lon, p_lon)
            is_combust = dist <= orb

            prev = combust_state.get(planet, False)
            if is_combust and not prev:
                events.append({
                    "event": "combustion_start",
                    "planet": planet,
                    "date": _date_from_jd(jd, tz_offset),
                    "distance_from_sun": round(dist, 2),
                    "orb": orb,
                    "sign": positions[planet]["sign"],
                })
            elif not is_combust and prev:
                events.append({
                    "event": "combustion_end",
                    "planet": planet,
                    "date": _date_from_jd(jd, tz_offset),
                    "distance_from_sun": round(dist, 2),
                    "orb": orb,
                    "sign": positions[planet]["sign"],
                })
            combust_state[planet] = is_combust

        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 2. PLANETS RETROGRADE
# ═══════════════════════════════════════════════════════════════

def calc_retrograde(start_jd: float, end_jd: float, step: float,
                    ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """Detect retrograde start/end for all planets."""
    retro_planets = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]
    events = []
    retro_state = {}

    jd = start_jd
    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)

        for planet in retro_planets:
            if planet not in positions:
                continue
            is_retro = positions[planet]["retrograde"]
            prev = retro_state.get(planet)

            if prev is not None and is_retro != prev:
                events.append({
                    "event": "retrograde_start" if is_retro else "retrograde_end",
                    "planet": planet,
                    "date": _date_from_jd(jd, tz_offset),
                    "sign": positions[planet]["sign"],
                    "degree": positions[planet]["degree_in_sign"],
                    "longitude": positions[planet]["longitude"],
                })
            retro_state[planet] = is_retro

        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 3. PLANETS TRANSIT (sign ingress)
# ═══════════════════════════════════════════════════════════════

def calc_transits(start_jd: float, end_jd: float, step: float,
                  ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """Detect when planets change zodiac signs."""
    events = []
    prev_signs = {}

    jd = start_jd
    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)

        for planet, data in positions.items():
            prev_sign = prev_signs.get(planet)
            cur_sign = data["sign"]

            if prev_sign is not None and cur_sign != prev_sign:
                events.append({
                    "event": "sign_ingress",
                    "planet": planet,
                    "date": _date_from_jd(jd, tz_offset),
                    "from_sign": prev_sign,
                    "to_sign": cur_sign,
                    "longitude": data["longitude"],
                    "retrograde": data["retrograde"],
                })
            prev_signs[planet] = cur_sign

        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 4. PLANETARY POSITIONS (snapshot at intervals)
# ═══════════════════════════════════════════════════════════════

def calc_positions(start_jd: float, end_jd: float, interval_days: float,
                   ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """Daily/weekly position snapshots for all planets."""
    snapshots = []
    jd = start_jd

    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)
        date_str = _date_from_jd(jd, tz_offset)

        planet_list = []
        for planet, data in positions.items():
            planet_list.append({
                "planet": planet,
                "sign": data["sign"],
                "degree": data["degree_in_sign"],
                "longitude": data["longitude"],
                "retrograde": data["retrograde"],
                "speed": data["speed"],
            })

        snapshots.append({
            "date": date_str,
            "planets": planet_list,
        })

        jd += interval_days

    return snapshots


# ═══════════════════════════════════════════════════════════════
# 5. PLANETS MUTUAL ASPECTS (Vedic Drishti)
# ═══════════════════════════════════════════════════════════════

def calc_mutual_aspects(start_jd: float, end_jd: float, step: float,
                        ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """
    Find mutual aspects between planets using Vedic drishti rules.
    A mutual aspect occurs when planet A aspects planet B AND B aspects A.
    """
    events = []
    prev_aspects = set()

    jd = start_jd
    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)
        current_aspects = set()

        planet_names = list(positions.keys())
        for i, p1 in enumerate(planet_names):
            for p2 in planet_names[i+1:]:
                lon1 = positions[p1]["longitude"]
                lon2 = positions[p2]["longitude"]

                # Check if p1 aspects p2
                p1_aspects_p2 = False
                for offset in VEDIC_ASPECT_OFFSETS.get(p1, [180]):
                    target = normalize_degree(lon1 + offset)
                    if _angular_distance(target, lon2) <= ASPECT_ORB:
                        p1_aspects_p2 = True
                        break

                # Check if p2 aspects p1
                p2_aspects_p1 = False
                for offset in VEDIC_ASPECT_OFFSETS.get(p2, [180]):
                    target = normalize_degree(lon2 + offset)
                    if _angular_distance(target, lon1) <= ASPECT_ORB:
                        p2_aspects_p1 = True
                        break

                if p1_aspects_p2 and p2_aspects_p1:
                    pair_key = tuple(sorted([p1, p2]))
                    current_aspects.add(pair_key)

        # Detect new aspects
        new_aspects = current_aspects - prev_aspects
        ended_aspects = prev_aspects - current_aspects

        for pair in new_aspects:
            events.append({
                "event": "mutual_aspect_start",
                "planet1": pair[0],
                "planet2": pair[1],
                "date": _date_from_jd(jd, tz_offset),
                "sign1": positions[pair[0]]["sign"],
                "sign2": positions[pair[1]]["sign"],
            })

        for pair in ended_aspects:
            events.append({
                "event": "mutual_aspect_end",
                "planet1": pair[0],
                "planet2": pair[1],
                "date": _date_from_jd(jd, tz_offset),
            })

        prev_aspects = current_aspects
        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 6. LUNAR ASPECTS (Moon's daily aspects)
# ═══════════════════════════════════════════════════════════════

def calc_lunar_aspects(start_jd: float, end_jd: float, step: float,
                       ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """Moon's aspects to other planets (conjunction, opposition, trine, square, sextile)."""
    LUNAR_ASPECTS = {
        "conjunction": 0,
        "sextile": 60,
        "square": 90,
        "trine": 120,
        "opposition": 180,
    }
    LUNAR_ORB = 6.0

    events = []
    prev_aspects = set()

    jd = start_jd
    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)
        moon_lon = positions.get("Moon", {}).get("longitude", 0)
        current_aspects = set()

        for planet, data in positions.items():
            if planet == "Moon":
                continue
            p_lon = data["longitude"]

            for aspect_name, angle in LUNAR_ASPECTS.items():
                diff = abs(normalize_degree(moon_lon - p_lon + 180) - 180)
                if abs(diff - angle) <= LUNAR_ORB:
                    key = (planet, aspect_name)
                    current_aspects.add(key)

        new = current_aspects - prev_aspects
        for planet, aspect_name in new:
            events.append({
                "event": "lunar_aspect",
                "aspect": aspect_name,
                "planet": planet,
                "date": _date_from_jd(jd, tz_offset),
                "moon_sign": positions["Moon"]["sign"],
                "planet_sign": positions[planet]["sign"],
            })

        prev_aspects = current_aspects
        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 7. PLANETS MUTUAL PARALLEL (same declination)
# ═══════════════════════════════════════════════════════════════

def calc_mutual_parallel(start_jd: float, end_jd: float, step: float,
                         tz_offset: int) -> List[Dict]:
    """Find when two planets have the same declination (parallel/contra-parallel)."""
    events = []
    prev_parallels = set()

    all_planets = list(PLANETS.items()) + [("Ketu", None)]

    jd = start_jd
    while jd <= end_jd:
        # Get declinations
        decl_map = {}
        for name, pid in PLANETS.items():
            _, decl = _calc_planet_lat_decl(jd, pid)
            decl_map[name] = decl
        # Ketu = Rahu + 180 but declination is just -Rahu declination
        if "Rahu" in decl_map:
            decl_map["Ketu"] = -decl_map["Rahu"]

        current_parallels = set()
        planet_names = list(decl_map.keys())

        for i, p1 in enumerate(planet_names):
            for p2 in planet_names[i+1:]:
                d1 = decl_map[p1]
                d2 = decl_map[p2]

                # Parallel: same sign declination within orb
                if abs(d1 - d2) <= PARALLEL_ORB:
                    pair_key = (tuple(sorted([p1, p2])), "parallel")
                    current_parallels.add(pair_key)

                # Contra-parallel: opposite sign declination within orb
                if abs(d1 + d2) <= PARALLEL_ORB:
                    pair_key = (tuple(sorted([p1, p2])), "contra_parallel")
                    current_parallels.add(pair_key)

        new = current_parallels - prev_parallels
        for (pair, ptype) in new:
            events.append({
                "event": ptype,
                "planet1": pair[0],
                "planet2": pair[1],
                "date": _date_from_jd(jd, tz_offset),
                "decl1": round(decl_map[pair[0]], 4),
                "decl2": round(decl_map[pair[1]], 4),
            })

        prev_parallels = current_parallels
        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 8. PLANETS ECLIPTIC CROSSINGS (latitude = 0)
# ═══════════════════════════════════════════════════════════════

def calc_ecliptic_crossings(start_jd: float, end_jd: float, step: float,
                            tz_offset: int) -> List[Dict]:
    """Find when planets cross the ecliptic (latitude goes from +/- to 0)."""
    events = []
    prev_lat = {}

    jd = start_jd
    while jd <= end_jd:
        for name, pid in PLANETS.items():
            if name in ("Sun", "Rahu"):
                continue  # Sun is always on ecliptic; Rahu defines nodes
            ecl_lat, _ = _calc_planet_lat_decl(jd, pid)

            prev = prev_lat.get(name)
            if prev is not None and prev * ecl_lat < 0:
                direction = "ascending" if ecl_lat > 0 else "descending"
                events.append({
                    "event": "ecliptic_crossing",
                    "planet": name,
                    "date": _date_from_jd(jd, tz_offset),
                    "direction": direction,
                    "latitude": round(ecl_lat, 4),
                })
            prev_lat[name] = ecl_lat

        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# 9. GRAHA YUDDHA (Planetary War)
# ═══════════════════════════════════════════════════════════════

def calc_graha_yuddha(start_jd: float, end_jd: float, step: float,
                      ayanamsa_key: str, tz_offset: int) -> List[Dict]:
    """
    Graha Yuddha: when two Tara Grahas are within 1° of each other.
    Only Mars, Mercury, Jupiter, Venus, Saturn participate.
    The planet with higher latitude wins.
    """
    events = []
    prev_wars = set()

    jd = start_jd
    while jd <= end_jd:
        positions = _get_all_positions(jd, ayanamsa_key)
        current_wars = set()

        yuddha_list = [p for p in positions if p in YUDDHA_PLANETS]

        for i, p1 in enumerate(yuddha_list):
            for p2 in yuddha_list[i+1:]:
                dist = _angular_distance(
                    positions[p1]["longitude"],
                    positions[p2]["longitude"]
                )
                if dist <= YUDDHA_ORB:
                    pair = tuple(sorted([p1, p2]))
                    current_wars.add(pair)

        new_wars = current_wars - prev_wars
        ended_wars = prev_wars - current_wars

        for pair in new_wars:
            p1, p2 = pair
            # Determine winner by ecliptic latitude
            pid1 = PLANETS.get(p1)
            pid2 = PLANETS.get(p2)
            lat1 = lat2 = 0.0
            if pid1 is not None:
                lat1, _ = _calc_planet_lat_decl(jd, pid1)
            if pid2 is not None:
                lat2, _ = _calc_planet_lat_decl(jd, pid2)

            winner = p1 if abs(lat1) > abs(lat2) else p2
            loser = p2 if winner == p1 else p1

            events.append({
                "event": "graha_yuddha_start",
                "planet1": p1,
                "planet2": p2,
                "date": _date_from_jd(jd, tz_offset),
                "distance": round(_angular_distance(
                    positions[p1]["longitude"], positions[p2]["longitude"]), 4),
                "sign": positions[p1]["sign"],
                "winner": winner,
                "loser": loser,
                "winner_latitude": round(lat1 if winner == p1 else lat2, 4),
            })

        for pair in ended_wars:
            events.append({
                "event": "graha_yuddha_end",
                "planet1": pair[0],
                "planet2": pair[1],
                "date": _date_from_jd(jd, tz_offset),
            })

        prev_wars = current_wars
        jd += step

    return events


# ═══════════════════════════════════════════════════════════════
# MASTER FUNCTION — Calculate ALL astrological events
# ═══════════════════════════════════════════════════════════════

def calculate_astro_events(
    start_date: datetime,
    end_date: datetime,
    ayanamsa: str = "lahiri",
    tz_offset_minutes: int = 330,
) -> Dict:
    """
    Calculate all 9 types of astrological events for a date range.
    """
    ayanamsa_key = ayanamsa.lower()
    if ayanamsa_key not in AYANAMSA_MAP:
        raise ValueError(f"Unsupported ayanamsa: {ayanamsa}")

    start_jd = _jd_for_date(start_date, tz_offset_minutes)
    end_jd = _jd_for_date(end_date, tz_offset_minutes)

    total_days = (end_date - start_date).days

    # Adaptive step sizes based on range
    fine_step = 0.5 if total_days <= 90 else 1.0     # combustion, retro, transit
    coarse_step = 1.0 if total_days <= 90 else 2.0   # aspects, parallel
    # Position snapshot interval
    pos_interval = 1.0 if total_days <= 31 else (7.0 if total_days <= 180 else 15.0)

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "total_days": total_days,
        "ayanamsa": ayanamsa_key,
        "combustion": calc_combustion(start_jd, end_jd, fine_step, ayanamsa_key, tz_offset_minutes),
        "retrograde": calc_retrograde(start_jd, end_jd, fine_step, ayanamsa_key, tz_offset_minutes),
        "transits": calc_transits(start_jd, end_jd, fine_step, ayanamsa_key, tz_offset_minutes),
        "positions": calc_positions(start_jd, end_jd, pos_interval, ayanamsa_key, tz_offset_minutes),
        "mutual_aspects": calc_mutual_aspects(start_jd, end_jd, coarse_step, ayanamsa_key, tz_offset_minutes),
        "lunar_aspects": calc_lunar_aspects(start_jd, end_jd, fine_step, ayanamsa_key, tz_offset_minutes),
        "mutual_parallel": calc_mutual_parallel(start_jd, end_jd, coarse_step, tz_offset_minutes),
        "ecliptic_crossings": calc_ecliptic_crossings(start_jd, end_jd, fine_step, tz_offset_minutes),
        "graha_yuddha": calc_graha_yuddha(start_jd, end_jd, fine_step, ayanamsa_key, tz_offset_minutes),
    }
