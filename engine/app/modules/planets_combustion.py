"""
Planets Combustion (Asta / Combust) — Track when planets are combust (too close to Sun).
A planet is combust when it's within a certain degree range of the Sun.

Combustion degrees (traditional):
  Moon:    12°
  Mars:    17°
  Mercury: 14° (12° when retrograde)
  Jupiter: 11°
  Venus:   10° (8° when retrograde)
  Saturn:  15°
  Rahu/Ketu: Not applicable (shadow planets)
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Dict, Any

from app.core import (
    PLANETS_9, get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, normalize_degree, date_range,
)

# Combustion orbs (degrees from Sun)
COMBUSTION_ORB = {
    "Moon":    12.0,
    "Mars":    17.0,
    "Mercury": 14.0,
    "Jupiter": 11.0,
    "Venus":   10.0,
    "Saturn":  15.0,
}

COMBUSTION_ORB_RETRO = {
    "Mercury": 12.0,
    "Venus":   8.0,
}


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes."""
    diff = abs(normalize_degree(lon1) - normalize_degree(lon2))
    return min(diff, 360 - diff)


def check_combustion(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Check combustion status of all planets for a given date."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    sun = get_planet_position(jd, "Sun", ayanamsa)
    results = []

    for planet in ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]:
        pos = get_planet_position(jd, planet, ayanamsa)
        dist = _angular_distance(sun.longitude, pos.longitude)

        # Use retrograde orb if applicable
        orb = COMBUSTION_ORB[planet]
        if pos.retrograde and planet in COMBUSTION_ORB_RETRO:
            orb = COMBUSTION_ORB_RETRO[planet]

        is_combust = dist <= orb

        results.append({
            "planet": planet,
            "combust": is_combust,
            "distance_from_sun": round(dist, 4),
            "combustion_orb": orb,
            "sign": pos.sign,
            "degree": round(pos.degree_in_sign, 4),
            "retrograde": pos.retrograde,
            "sun_sign": sun.sign,
            "sun_degree": round(sun.degree_in_sign, 4),
        })

    return {
        "date": target_date.isoformat(),
        "sun_position": f"{sun.degree_display}",
        "planets": results,
        "combust_count": sum(1 for r in results if r["combust"]),
    }


def find_combustion_periods(
    planet: str,
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find all combustion periods for a planet in a date range."""
    if planet in ("Sun", "Rahu", "Ketu"):
        return []

    set_ayanamsa(ayanamsa)
    periods = []
    in_combustion = False
    comb_start = None

    for d in date_range(start_date, end_date):
        dt = datetime(d.year, d.month, d.day, 6, 0, 0)
        utc_dt = local_to_utc(dt, tz_offset)
        jd = datetime_to_jd(utc_dt)

        sun = get_planet_position(jd, "Sun", ayanamsa)
        pos = get_planet_position(jd, planet, ayanamsa)
        dist = _angular_distance(sun.longitude, pos.longitude)

        orb = COMBUSTION_ORB[planet]
        if pos.retrograde and planet in COMBUSTION_ORB_RETRO:
            orb = COMBUSTION_ORB_RETRO[planet]

        is_combust = dist <= orb

        if is_combust and not in_combustion:
            in_combustion = True
            comb_start = d
        elif not is_combust and in_combustion:
            in_combustion = False
            periods.append({
                "planet": planet,
                "start": comb_start.isoformat(),
                "end": d.isoformat(),
                "duration_days": (d - comb_start).days,
            })

    if in_combustion:
        periods.append({
            "planet": planet,
            "start": comb_start.isoformat(),
            "end": end_date.isoformat(),
            "duration_days": (end_date - comb_start).days,
        })

    return periods


def get_combustion_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get combustion status for date range."""
    return [check_combustion(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
