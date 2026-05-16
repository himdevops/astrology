"""
Planets Mutual Aspects — Vedic aspect (Drishti) analysis between planets.
Shows which planets are aspecting each other on any given date.

Vedic Aspects:
  All planets: 7th house aspect (180°, orb ±12°)
  Mars extra:  4th (90°) and 8th (210°) house aspects
  Jupiter extra: 5th (120°) and 9th (240°) house aspects
  Saturn extra: 3rd (60°) and 10th (270°) house aspects
  Rahu/Ketu: 5th, 7th, 9th house aspects (like Jupiter)
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any

from app.core import (
    PLANETS_9, get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, normalize_degree, date_range,
)

# Vedic aspects: planet → list of aspect angles
VEDIC_ASPECTS = {
    "Sun":     [180],
    "Moon":    [180],
    "Mars":    [90, 180, 210],
    "Mercury": [180],
    "Jupiter": [120, 180, 240],
    "Venus":   [180],
    "Saturn":  [60, 180, 270],
    "Rahu":    [120, 180, 240],
    "Ketu":    [120, 180, 240],
}

ASPECT_NAMES = {
    60:  "3rd aspect",
    90:  "4th aspect",
    120: "5th aspect",
    180: "7th aspect",
    210: "8th aspect",
    240: "9th aspect",
    270: "10th aspect",
}

ASPECT_ORB = 12.0  # degrees of orb allowed


def _check_aspect(lon1: float, lon2: float, aspect_angle: float, orb: float = ASPECT_ORB) -> bool:
    """Check if two longitudes form a specific aspect within orb."""
    diff = normalize_degree(lon2 - lon1)
    return abs(diff - aspect_angle) <= orb or abs(diff - aspect_angle + 360) <= orb


def get_mutual_aspects(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Get all mutual aspects between planets for a given date."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    positions = {}
    for planet in PLANETS_9:
        positions[planet] = get_planet_position(jd, planet, ayanamsa)

    aspects = []
    checked = set()

    for p1 in PLANETS_9:
        for p2 in PLANETS_9:
            if p1 == p2:
                continue
            pair_key = tuple(sorted([p1, p2]))
            # We check each direction separately (P1 aspecting P2)
            for angle in VEDIC_ASPECTS[p1]:
                if _check_aspect(positions[p1].longitude, positions[p2].longitude, angle):
                    actual_diff = round(normalize_degree(positions[p2].longitude - positions[p1].longitude), 2)
                    aspects.append({
                        "aspecting_planet": p1,
                        "aspected_planet": p2,
                        "aspect_angle": angle,
                        "aspect_name": ASPECT_NAMES.get(angle, f"{angle}°"),
                        "actual_distance": actual_diff,
                        "aspecting_sign": positions[p1].sign,
                        "aspected_sign": positions[p2].sign,
                        "aspecting_degree": round(positions[p1].degree_in_sign, 2),
                        "aspected_degree": round(positions[p2].degree_in_sign, 2),
                    })

    # Find mutual aspects (both aspecting each other)
    mutual = []
    for i, a1 in enumerate(aspects):
        for a2 in aspects[i+1:]:
            if a1["aspecting_planet"] == a2["aspected_planet"] and \
               a1["aspected_planet"] == a2["aspecting_planet"]:
                mutual.append({
                    "planet_1": a1["aspecting_planet"],
                    "planet_2": a1["aspected_planet"],
                    "aspect_1": a1["aspect_name"],
                    "aspect_2": a2["aspect_name"],
                })

    return {
        "date": target_date.isoformat(),
        "total_aspects": len(aspects),
        "aspects": aspects,
        "mutual_aspects": mutual,
        "mutual_count": len(mutual),
    }


def get_aspects_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get mutual aspects for date range."""
    return [get_mutual_aspects(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
