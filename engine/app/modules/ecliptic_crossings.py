"""
Planets Ecliptic Crossings — Track when planets cross the ecliptic plane.
A planet crosses the ecliptic when its latitude changes from positive to negative
(descending node) or negative to positive (ascending node).
This is significant in mundane and financial astrology.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any

from app.core import (
    PLANETS_9, get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, date_range,
)

# Only planets with significant latitude variation
# Sun always on ecliptic (lat=0), Rahu/Ketu are nodes themselves
ECLIPTIC_PLANETS = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def get_ecliptic_status(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Get ecliptic latitude and hemisphere for all planets."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    statuses = []
    for planet in ECLIPTIC_PLANETS:
        pos = get_planet_position(jd, planet, ayanamsa)
        statuses.append({
            "planet": planet,
            "latitude": round(pos.latitude, 4),
            "hemisphere": "North" if pos.latitude >= 0 else "South",
            "sign": pos.sign,
            "degree": round(pos.degree_in_sign, 4),
            "near_crossing": abs(pos.latitude) < 0.5,  # within 0.5° of ecliptic
        })

    return {
        "date": target_date.isoformat(),
        "planets": statuses,
        "near_ecliptic_count": sum(1 for s in statuses if s["near_crossing"]),
    }


def find_ecliptic_crossings(
    planet: str,
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find dates when a planet crosses the ecliptic plane."""
    if planet not in ECLIPTIC_PLANETS:
        return []

    set_ayanamsa(ayanamsa)
    crossings = []
    prev_lat = None

    for d in date_range(start_date, end_date):
        dt = datetime(d.year, d.month, d.day, 6, 0, 0)
        utc_dt = local_to_utc(dt, tz_offset)
        jd = datetime_to_jd(utc_dt)
        pos = get_planet_position(jd, planet, ayanamsa)

        if prev_lat is not None:
            # Check if latitude crossed zero
            if (prev_lat > 0 and pos.latitude <= 0) or (prev_lat < 0 and pos.latitude >= 0):
                crossing_type = "Descending" if prev_lat > 0 else "Ascending"
                crossings.append({
                    "planet": planet,
                    "date": d.isoformat(),
                    "type": crossing_type,
                    "node": f"{crossing_type} Node",
                    "latitude": round(pos.latitude, 4),
                    "sign": pos.sign,
                    "degree": round(pos.degree_in_sign, 4),
                    "nakshatra": pos.nakshatra,
                })

        prev_lat = pos.latitude

    return crossings


def get_all_crossings(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Find all ecliptic crossings for all planets in date range."""
    all_crossings = []
    by_planet = {}

    for planet in ECLIPTIC_PLANETS:
        crossings = find_ecliptic_crossings(planet, start_date, end_date, tz_offset, ayanamsa)
        by_planet[planet] = crossings
        all_crossings.extend(crossings)

    all_crossings.sort(key=lambda x: x["date"])

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_crossings": len(all_crossings),
        "by_planet": by_planet,
        "chronological": all_crossings,
    }
