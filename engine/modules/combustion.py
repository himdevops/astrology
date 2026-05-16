"""
combustion.py — Planets Combustion (Asta) detection.
=====================================================
Planet is combust when too close to the Sun.
Traditional orbs per Surya Siddhanta.
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import COMBUSTION_ORB, COMBUSTION_ORB_RETRO
from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import angular_distance, datetime_to_jd, local_to_utc, date_range, date_to_datetime

COMBUSTIBLE = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def check_daily(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Check combustion status of all combustible planets."""
    jd = datetime_to_jd(local_to_utc(date_to_datetime(target_date), tz_offset))
    set_ayanamsa(ayanamsa)
    sun = get_planet_position(jd, "Sun", ayanamsa)

    results = []
    for planet in COMBUSTIBLE:
        pos = get_planet_position(jd, planet, ayanamsa)
        dist = angular_distance(sun.longitude, pos.longitude)
        orb = COMBUSTION_ORB[planet]
        if pos.retrograde and planet in COMBUSTION_ORB_RETRO:
            orb = COMBUSTION_ORB_RETRO[planet]

        results.append({
            "planet": planet, "combust": dist <= orb,
            "distance_from_sun": round(dist, 4), "combustion_orb": orb,
            "sign": pos.sign, "degree": round(pos.degree_in_sign, 4),
            "retrograde": pos.retrograde,
            "sun_sign": sun.sign, "sun_degree": round(sun.degree_in_sign, 4),
        })

    return {
        "date": target_date.isoformat(),
        "sun_position": sun.degree_display,
        "planets": results,
        "combust_count": sum(1 for r in results if r["combust"]),
    }


def find_periods(
    planet: str, start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find combustion periods for a planet."""
    if planet not in COMBUSTIBLE:
        return []
    set_ayanamsa(ayanamsa)
    periods, in_comb, comb_start = [], False, None

    for d in date_range(start_date, end_date):
        jd = datetime_to_jd(local_to_utc(date_to_datetime(d), tz_offset))
        sun = get_planet_position(jd, "Sun", ayanamsa)
        pos = get_planet_position(jd, planet, ayanamsa)
        dist = angular_distance(sun.longitude, pos.longitude)
        orb = COMBUSTION_ORB[planet]
        if pos.retrograde and planet in COMBUSTION_ORB_RETRO:
            orb = COMBUSTION_ORB_RETRO[planet]

        if dist <= orb and not in_comb:
            in_comb, comb_start = True, d
        elif dist > orb and in_comb:
            in_comb = False
            periods.append({
                "planet": planet, "start": comb_start.isoformat(),
                "end": d.isoformat(), "duration_days": (d - comb_start).days,
            })

    if in_comb:
        periods.append({
            "planet": planet, "start": comb_start.isoformat(),
            "end": end_date.isoformat(), "duration_days": (end_date - comb_start).days,
        })
    return periods


def get_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    return [check_daily(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
