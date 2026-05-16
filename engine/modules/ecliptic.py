"""
ecliptic.py — Ecliptic plane crossings.
=========================================
Track when planets cross latitude = 0 (ascending/descending node).
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc, date_range, date_to_datetime

ECLIPTIC_PLANETS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def get_daily(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    jd = datetime_to_jd(local_to_utc(date_to_datetime(target_date), tz_offset))
    set_ayanamsa(ayanamsa)

    statuses = []
    for planet in ECLIPTIC_PLANETS:
        pos = get_planet_position(jd, planet, ayanamsa)
        statuses.append({
            "planet": planet, "latitude": round(pos.latitude, 4),
            "hemisphere": "North" if pos.latitude >= 0 else "South",
            "sign": pos.sign, "degree": round(pos.degree_in_sign, 4),
            "near_crossing": abs(pos.latitude) < 0.5,
        })

    return {
        "date": target_date.isoformat(), "planets": statuses,
        "near_ecliptic_count": sum(1 for s in statuses if s["near_crossing"]),
    }


def find_crossings(
    planet: str, start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find dates when planet crosses ecliptic (lat crosses zero)."""
    if planet not in ECLIPTIC_PLANETS:
        return []
    set_ayanamsa(ayanamsa)
    crossings, prev_lat = [], None

    for d in date_range(start_date, end_date):
        jd = datetime_to_jd(local_to_utc(date_to_datetime(d), tz_offset))
        pos = get_planet_position(jd, planet, ayanamsa)
        if prev_lat is not None:
            if (prev_lat > 0 and pos.latitude <= 0) or (prev_lat < 0 and pos.latitude >= 0):
                crossings.append({
                    "planet": planet, "date": d.isoformat(),
                    "type": "Descending" if prev_lat > 0 else "Ascending",
                    "latitude": round(pos.latitude, 4),
                    "sign": pos.sign, "degree": round(pos.degree_in_sign, 4),
                    "nakshatra": pos.nakshatra,
                })
        prev_lat = pos.latitude
    return crossings


def get_all_crossings(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    all_c, by_planet = [], {}
    for planet in ECLIPTIC_PLANETS:
        c = find_crossings(planet, start_date, end_date, tz_offset, ayanamsa)
        by_planet[planet] = c
        all_c.extend(c)
    all_c.sort(key=lambda x: x["date"])
    return {
        "start_date": start_date.isoformat(), "end_date": end_date.isoformat(),
        "total_crossings": len(all_c), "by_planet": by_planet, "chronological": all_c,
    }
