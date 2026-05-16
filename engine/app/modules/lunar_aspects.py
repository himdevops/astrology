"""
Lunar Aspects — Track Moon's aspects to all other planets.
Moon moves ~13° per day, so aspects change rapidly.
Shows exact aspect times, applying/separating status.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any

from app.core import (
    PLANETS_9, get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, normalize_degree, date_range,
)

# Major aspects to track for Moon
LUNAR_ASPECT_ANGLES = {
    0:   "Conjunction",
    60:  "Sextile",
    90:  "Square",
    120: "Trine",
    180: "Opposition",
}

LUNAR_ORB = 8.0  # degrees


def get_lunar_aspects(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Get Moon's aspects to all planets for a given date."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    moon = get_planet_position(jd, "Moon", ayanamsa)
    aspects = []

    for planet in PLANETS_9:
        if planet == "Moon":
            continue

        pos = get_planet_position(jd, planet, ayanamsa)
        diff = normalize_degree(pos.longitude - moon.longitude)

        for angle, name in LUNAR_ASPECT_ANGLES.items():
            orb_diff = min(abs(diff - angle), abs(diff - angle + 360), abs(diff - angle - 360))
            if orb_diff <= LUNAR_ORB:
                # Applying or separating
                # Moon is faster, so if Moon is approaching the aspect it's applying
                applying = moon.speed > pos.speed

                aspects.append({
                    "planet": planet,
                    "aspect": name,
                    "aspect_angle": angle,
                    "orb": round(orb_diff, 2),
                    "moon_sign": moon.sign,
                    "moon_degree": round(moon.degree_in_sign, 2),
                    "moon_nakshatra": moon.nakshatra,
                    "planet_sign": pos.sign,
                    "planet_degree": round(pos.degree_in_sign, 2),
                    "planet_nakshatra": pos.nakshatra,
                    "applying": applying,
                    "status": "Applying" if applying else "Separating",
                })

    return {
        "date": target_date.isoformat(),
        "moon_position": {
            "sign": moon.sign,
            "degree": round(moon.degree_in_sign, 2),
            "nakshatra": moon.nakshatra,
            "pada": moon.nakshatra_pada,
            "speed": round(moon.speed, 4),
        },
        "aspects": aspects,
        "total_aspects": len(aspects),
    }


def get_lunar_aspects_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get lunar aspects for date range."""
    return [get_lunar_aspects(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
