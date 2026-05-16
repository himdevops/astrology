"""
aspects.py — Vedic Mutual Aspects (Drishti).
=============================================
Mars: 4th, 7th, 8th | Jupiter: 5th, 7th, 9th | Saturn: 3rd, 7th, 10th
Others: 7th only.
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import PLANETS_9, VEDIC_ASPECTS, ASPECT_NAMES, ASPECT_ORB
from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import normalize_degree, datetime_to_jd, local_to_utc, date_range, date_to_datetime


def _check_aspect(lon1: float, lon2: float, angle: float, orb: float = ASPECT_ORB) -> bool:
    diff = normalize_degree(lon2 - lon1)
    return abs(diff - angle) <= orb or abs(diff - angle + 360) <= orb


def get_daily(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """All Vedic aspects between planets for one date."""
    jd = datetime_to_jd(local_to_utc(date_to_datetime(target_date), tz_offset))
    set_ayanamsa(ayanamsa)

    positions = {p: get_planet_position(jd, p, ayanamsa) for p in PLANETS_9}
    aspects = []

    for p1 in PLANETS_9:
        for p2 in PLANETS_9:
            if p1 == p2:
                continue
            for angle in VEDIC_ASPECTS[p1]:
                if _check_aspect(positions[p1].longitude, positions[p2].longitude, angle):
                    aspects.append({
                        "aspecting_planet": p1, "aspected_planet": p2,
                        "aspect_angle": angle,
                        "aspect_name": ASPECT_NAMES.get(angle, f"{angle}°"),
                        "actual_distance": round(normalize_degree(positions[p2].longitude - positions[p1].longitude), 2),
                        "aspecting_sign": positions[p1].sign,
                        "aspected_sign": positions[p2].sign,
                        "aspecting_degree": round(positions[p1].degree_in_sign, 2),
                        "aspected_degree": round(positions[p2].degree_in_sign, 2),
                    })

    # Find mutual
    mutual = []
    for i, a1 in enumerate(aspects):
        for a2 in aspects[i+1:]:
            if (a1["aspecting_planet"] == a2["aspected_planet"] and
                    a1["aspected_planet"] == a2["aspecting_planet"]):
                mutual.append({
                    "planet_1": a1["aspecting_planet"], "planet_2": a1["aspected_planet"],
                    "aspect_1": a1["aspect_name"], "aspect_2": a2["aspect_name"],
                })

    return {
        "date": target_date.isoformat(),
        "total_aspects": len(aspects), "aspects": aspects,
        "mutual_aspects": mutual, "mutual_count": len(mutual),
    }


def get_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    return [get_daily(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
