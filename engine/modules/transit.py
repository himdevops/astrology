"""
transit.py — Planet sign & nakshatra change (transit) detection.
================================================================
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import PLANETS_9
from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc, date_range, date_to_datetime


def find_sign_changes(
    planet: str, start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find all dates where planet changes sign."""
    set_ayanamsa(ayanamsa)
    changes, prev_sign = [], None

    for d in date_range(start_date, end_date):
        jd = datetime_to_jd(local_to_utc(date_to_datetime(d), tz_offset))
        pos = get_planet_position(jd, planet, ayanamsa)
        if prev_sign and pos.sign != prev_sign:
            changes.append({
                "planet": planet, "date": d.isoformat(),
                "from_sign": prev_sign, "to_sign": pos.sign,
                "degree": round(pos.degree_in_sign, 4),
                "nakshatra": pos.nakshatra, "retrograde": pos.retrograde,
            })
        prev_sign = pos.sign
    return changes


def find_nakshatra_changes(
    planet: str, start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find all dates where planet changes nakshatra."""
    set_ayanamsa(ayanamsa)
    changes, prev_nak = [], None

    for d in date_range(start_date, end_date):
        jd = datetime_to_jd(local_to_utc(date_to_datetime(d), tz_offset))
        pos = get_planet_position(jd, planet, ayanamsa)
        if prev_nak and pos.nakshatra != prev_nak:
            changes.append({
                "planet": planet, "date": d.isoformat(),
                "from_nakshatra": prev_nak, "to_nakshatra": pos.nakshatra,
                "sign": pos.sign, "degree": round(pos.degree_in_sign, 4),
            })
        prev_nak = pos.nakshatra
    return changes


def get_all_transits(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """All sign changes for all 9 planets in range."""
    all_changes, by_planet = [], {}
    for planet in PLANETS_9:
        changes = find_sign_changes(planet, start_date, end_date, tz_offset, ayanamsa)
        by_planet[planet] = changes
        all_changes.extend(changes)

    all_changes.sort(key=lambda x: x["date"])
    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_transits": len(all_changes),
        "by_planet": by_planet,
        "chronological": all_changes,
    }
