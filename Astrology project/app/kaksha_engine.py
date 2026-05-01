"""
kaksha_engine.py — Advanced Kaksha Ashtakavarga Engine
Prastara-style bindu timing, hourly Moon Kaksha windows,
daily/weekly guidance with BAV/SAV integration.

Ported from standalone advanced_ashtakavarga_kaksha_project
and adapted to use the main engine's core.py.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List

from app.core import (
    calculate_ascendant,
    calculate_planets,
    resolve_location_and_time,
    to_julian_day_utc,
)
from app.ashtakavarga import ASHTAKAVARGA_TABLE, PLANETS_FOR_BAV

# ── Constants ─────────────────────────────────────────────────

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# 8 Kaksha lords per sign (3°45' each within a 30° sign)
KAKSHA_LORDS = [
    "Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon", "Lagna",
]

KAKSHA_SIZE = 30.0 / 8.0  # 3.75°

DAILY_LABELS = {
    "excellent": "Excellent — best window",
    "good":      "Good — supportive",
    "average":   "Average — normal work",
    "caution":   "Caution — avoid risky decisions",
    "bad":       "Bad — rest, avoid big commitments",
}

# Dignity / ownership tables
_EXALTED = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra",
}
_DEBILITATED = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries",
}
_OWN = {
    "Sun": ["Leo"], "Moon": ["Cancer"],
    "Mars": ["Aries", "Scorpio"], "Mercury": ["Gemini", "Virgo"],
    "Jupiter": ["Sagittarius", "Pisces"], "Venus": ["Taurus", "Libra"],
    "Saturn": ["Capricorn", "Aquarius"],
}

_PLANET_NATURE_SCORE = {
    "Jupiter": 0.25, "Venus": 0.20, "Mercury": 0.10, "Moon": 0.05,
    "Sun": -0.05, "Mars": -0.15, "Saturn": -0.15,
    "Rahu": -0.20, "Ketu": -0.15,
}


# ── Helpers ───────────────────────────────────────────────────

def _sign_idx(longitude: float) -> int:
    return int((longitude % 360.0) / 30)


def _kaksha_index(degree_in_sign: float) -> int:
    return min(7, max(0, int(degree_in_sign // KAKSHA_SIZE)))


def _decimal_to_dms(x: float) -> str:
    x = x % 30
    deg = int(x)
    mf = (x - deg) * 60
    minute = int(mf)
    second = int(round((mf - minute) * 60))
    if second == 60:
        second = 0; minute += 1
    if minute == 60:
        minute = 0; deg += 1
    return f"{deg}°{minute:02d}'{second:02d}\""


def _dignity_modifier(planet: str, sign: str) -> float:
    if _EXALTED.get(planet) == sign:
        return 1.25
    if _DEBILITATED.get(planet) == sign:
        return 0.75
    if sign in _OWN.get(planet, []):
        return 1.15
    return 1.0


# ── BAV/SAV Calculation (Prastara-style) ─────────────────────

def calc_bhinnashtakavarga_kaksha(
    planet_name: str, planets: List[Dict], ascendant_long: float,
) -> Dict:
    """BAV with full Prastara matrix (contributor × sign → bindu)."""
    table = ASHTAKAVARGA_TABLE.get(planet_name, {})
    scores = [0] * 12
    contributors = {
        p["planet"]: _sign_idx(p["longitude"])
        for p in planets if p["planet"] in PLANETS_FOR_BAV
    }
    contributors["Lagna"] = _sign_idx(ascendant_long)

    prastara = {SIGNS[i]: {} for i in range(12)}
    for contributor, offsets in table.items():
        csign = contributors.get(contributor)
        if csign is None:
            continue
        for i, sign in enumerate(SIGNS):
            offset = ((i - csign) % 12) + 1
            has_bindu = offset in offsets
            prastara[sign][contributor] = 1 if has_bindu else 0
            if has_bindu:
                scores[i] += 1

    return {
        "planet": planet_name,
        "scores": {SIGNS[i]: scores[i] for i in range(12)},
        "prastara": prastara,
        "total": sum(scores),
    }


def calc_sarvashtakavarga_kaksha(
    planets: List[Dict], ascendant_long: float,
) -> Dict:
    """SAV with per-planet BAV and full Prastara matrices."""
    all_bav = {}
    sav = [0] * 12
    for planet in PLANETS_FOR_BAV:
        bav = calc_bhinnashtakavarga_kaksha(planet, planets, ascendant_long)
        all_bav[planet] = bav
        for i, sign in enumerate(SIGNS):
            sav[i] += bav["scores"][sign]
    return {
        "sav": {SIGNS[i]: sav[i] for i in range(12)},
        "bav": all_bav,
        "total_sav": sum(sav),
    }


# ── Kaksha Window Scoring ────────────────────────────────────

def _prastara_bindu_for_kaksha(
    transiting_planet: str, sign: str, kaksha_lord: str, bav_data: Dict,
) -> int:
    if kaksha_lord == "Lagna":
        return (
            1 if bav_data.get(transiting_planet, {})
                        .get("scores", {}).get(sign, 0) >= 4
            else 0
        )
    return (
        bav_data.get(transiting_planet, {})
                .get("prastara", {})
                .get(sign, {})
                .get(kaksha_lord, 0)
    )


def score_kaksha_window(tp: Dict, natal_av: Dict) -> Dict:
    """Score a single planet's Kaksha window against natal Ashtakavarga."""
    sign = tp["sign"]
    deg = tp["degree_in_sign"]
    kidx = _kaksha_index(deg)
    lord = KAKSHA_LORDS[kidx]
    planet = tp["planet"]

    bav = (
        natal_av["bav"].get(planet, {}).get("scores", {}).get(sign, 0)
        if planet in natal_av["bav"] else 4
    )
    sav = natal_av["sav"].get(sign, 28)
    bindu = (
        _prastara_bindu_for_kaksha(planet, sign, lord, natal_av["bav"])
        if planet in natal_av["bav"] else 0
    )

    base = (
        (sav - 28) / 20.0
        + (bav - 4) / 4.0
        + (0.35 if bindu else -0.35)
        + _PLANET_NATURE_SCORE.get(planet, 0)
    )
    base *= _dignity_modifier(planet, sign)
    if tp.get("retrograde"):
        base -= 0.12
    score = max(-1.0, min(1.0, base))

    if score >= 0.55:
        quality = "excellent"
    elif score >= 0.25:
        quality = "good"
    elif score >= -0.10:
        quality = "average"
    elif score >= -0.40:
        quality = "caution"
    else:
        quality = "bad"

    return {
        "planet": planet,
        "sign": sign,
        "degree": round(deg, 4),
        "degree_dms": _decimal_to_dms(deg),
        "kaksha_index": kidx + 1,
        "kaksha_lord": lord,
        "bindu": bindu,
        "bav_score": bav,
        "sav_score": sav,
        "score": round(score, 3),
        "quality": quality,
        "label": DAILY_LABELS[quality],
        "reason": (
            f"{planet} in {sign} {_decimal_to_dms(deg)}; "
            f"Kaksha {kidx+1} lord {lord}; "
            f"BAV={bav}, SAV={sav}, bindu={bindu}."
        ),
    }


# ── Natal AV calculation ─────────────────────────────────────

def _calculate_natal_av(payload) -> Dict:
    """Resolve birth data and compute full Ashtakavarga."""
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=getattr(payload, "latitude", None),
        longitude=getattr(payload, "longitude", None),
        timezone_offset_minutes=getattr(payload, "timezone_offset_minutes", None),
    )
    jd = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd, payload.ayanamsa)
    asc = calculate_ascendant(
        jd, resolved.latitude, resolved.longitude, payload.ayanamsa,
    )
    av = calc_sarvashtakavarga_kaksha(planets, asc["longitude"])
    return {
        "resolved": resolved,
        "local_dt": local_dt,
        "jd_ut": jd,
        "planets": planets,
        "ascendant": asc,
        "av": av,
    }


def _transit_planets_for(
    date_str: str, time_str: str, place: str, ayanamsa: str,
):
    resolved, dt = resolve_location_and_time(
        place=place, date_str=date_str, time_str=time_str,
        latitude=None, longitude=None, timezone_offset_minutes=None,
    )
    jd = to_julian_day_utc(dt, resolved.timezone_offset_minutes)
    return calculate_planets(jd, ayanamsa), resolved, dt


# ── Main Analysis Functions ──────────────────────────────────

FOCUS_PLANETS = ["Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn"]


def daily_kaksha_analysis(payload) -> Dict:
    """
    Full daily Kaksha analysis: natal AV → transit scoring →
    hourly Moon windows → best/avoid windows.
    """
    natal = _calculate_natal_av(payload)
    tdate = getattr(payload, "transit_date", None) or datetime.now().strftime("%Y-%m-%d")
    ttime = getattr(payload, "transit_time", "09:15")
    tplace = getattr(payload, "transit_place", "Mumbai, Maharashtra, India")

    tplanets, tloc, tdt = _transit_planets_for(tdate, ttime, tplace, payload.ayanamsa)

    planet_windows = [
        score_kaksha_window(tp, natal["av"])
        for tp in tplanets if tp["planet"] in FOCUS_PLANETS
    ]

    # Hourly Moon Kaksha windows (6 AM → midnight = 18 hours)
    hourly = []
    start = tdt.replace(hour=6, minute=0, second=0, microsecond=0)
    for h in range(18):
        dt = start + timedelta(hours=h)
        p, _, _ = _transit_planets_for(
            dt.strftime("%Y-%m-%d"), dt.strftime("%H:%M"), tplace, payload.ayanamsa,
        )
        moon = next(x for x in p if x["planet"] == "Moon")
        hourly.append({"time": dt.strftime("%H:%M"), **score_kaksha_window(moon, natal["av"])})

    avg = round(sum(x["score"] for x in planet_windows) / max(len(planet_windows), 1), 3)
    if avg >= 0.4:
        overall = "GOOD DAY"
    elif avg >= 0.1:
        overall = "MIXED TO GOOD"
    elif avg >= -0.2:
        overall = "MIXED / AVERAGE"
    else:
        overall = "CAUTION DAY"

    return {
        "type": "advanced_ashtakavarga_kaksha",
        "name": getattr(payload, "name", "Chart"),
        "natal": {
            "place": natal["resolved"].place,
            "ascendant": natal["ascendant"],
            "planets": natal["planets"],
        },
        "ashtakavarga": natal["av"],
        "transit": {
            "date": tdate,
            "time": ttime,
            "place": tloc.place,
            "timezone": tloc.timezone_name,
        },
        "overall": {"score": avg, "signal": overall},
        "planet_kaksha": planet_windows,
        "hourly_moon_kaksha": hourly,
        "best_windows": sorted(hourly, key=lambda x: x["score"], reverse=True)[:3],
        "avoid_windows": sorted(hourly, key=lambda x: x["score"])[:3],
    }


def timeline_analysis(payload) -> Dict:
    """Multi-day Kaksha timeline for best/worst trading days."""
    natal = _calculate_natal_av(payload)
    start_date = getattr(payload, "transit_date", None) or datetime.now().strftime("%Y-%m-%d")
    base_dt = datetime.strptime(start_date, "%Y-%m-%d")
    tplace = getattr(payload, "transit_place", "Mumbai, Maharashtra, India")
    num_days = getattr(payload, "days", 30)

    days = []
    for i in range(num_days):
        d = base_dt + timedelta(days=i)
        p, loc, dt = _transit_planets_for(
            d.strftime("%Y-%m-%d"), "09:15", tplace, payload.ayanamsa,
        )
        scores = [
            score_kaksha_window(tp, natal["av"])
            for tp in p if tp["planet"] in FOCUS_PLANETS
        ]
        avg = round(sum(x["score"] for x in scores) / max(len(scores), 1), 3)
        moon = next(s for s in scores if s["planet"] == "Moon")

        days.append({
            "date": d.strftime("%Y-%m-%d"),
            "weekday": d.strftime("%A"),
            "score": avg,
            "signal": (
                "Good" if avg >= 0.25 else
                "Average" if avg >= -0.1 else
                "Caution"
            ),
            "moon_kaksha": moon,
            "best_planet": max(scores, key=lambda x: x["score"])["planet"],
            "weakest_planet": min(scores, key=lambda x: x["score"])["planet"],
        })

    return {
        "type": "kaksha_timeline",
        "name": getattr(payload, "name", "Chart"),
        "start_date": start_date,
        "days_count": num_days,
        "days": days,
        "best_days": sorted(days, key=lambda x: x["score"], reverse=True)[:5],
        "worst_days": sorted(days, key=lambda x: x["score"])[:5],
        "ashtakavarga": natal["av"],
    }
