"""
lunar_aspects.py — Moon's aspects to all other planets.
========================================================
Conjunction, Sextile, Square, Trine, Opposition.
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import PLANETS_9
from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import normalize_degree, datetime_to_jd, local_to_utc, date_range, date_to_datetime

LUNAR_ANGLES = {0: "Conjunction", 60: "Sextile", 90: "Square", 120: "Trine", 180: "Opposition"}
LUNAR_ORB = 8.0


def get_daily(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    jd = datetime_to_jd(local_to_utc(date_to_datetime(target_date), tz_offset))
    set_ayanamsa(ayanamsa)
    moon = get_planet_position(jd, "Moon", ayanamsa)
    aspects = []

    for planet in PLANETS_9:
        if planet == "Moon":
            continue
        pos = get_planet_position(jd, planet, ayanamsa)
        diff = normalize_degree(pos.longitude - moon.longitude)

        for angle, name in LUNAR_ANGLES.items():
            orb_diff = min(abs(diff - angle), abs(diff - angle + 360), abs(diff - angle - 360))
            if orb_diff <= LUNAR_ORB:
                aspects.append({
                    "planet": planet, "aspect": name, "aspect_angle": angle,
                    "orb": round(orb_diff, 2),
                    "moon_sign": moon.sign, "moon_degree": round(moon.degree_in_sign, 2),
                    "moon_nakshatra": moon.nakshatra,
                    "planet_sign": pos.sign, "planet_degree": round(pos.degree_in_sign, 2),
                    "planet_nakshatra": pos.nakshatra,
                    "applying": moon.speed > pos.speed,
                    "status": "Applying" if moon.speed > pos.speed else "Separating",
                })

    return {
        "date": target_date.isoformat(),
        "moon_position": {
            "sign": moon.sign, "degree": round(moon.degree_in_sign, 2),
            "nakshatra": moon.nakshatra, "pada": moon.nakshatra_pada,
            "speed": round(moon.speed, 4),
        },
        "aspects": aspects, "total_aspects": len(aspects),
    }


def get_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    return [get_daily(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
