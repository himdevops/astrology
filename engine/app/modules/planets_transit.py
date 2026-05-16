"""
Planets Transit — Track when planets change signs (Rashi Parivartan).
Like Drikpanchang's "Planets Transit" showing sign ingress dates.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Dict, Any

from app.core import (
    PLANETS_9, SIGNS, get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, date_range,
)


def find_sign_changes(
    planet: str,
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """
    Find all sign changes (transits) for a planet in a date range.
    Returns list of {date, from_sign, to_sign, planet}.
    """
    set_ayanamsa(ayanamsa)
    changes = []
    prev_sign = None

    for d in date_range(start_date, end_date):
        dt = datetime(d.year, d.month, d.day, 6, 0, 0)
        utc_dt = local_to_utc(dt, tz_offset)
        jd = datetime_to_jd(utc_dt)
        pos = get_planet_position(jd, planet, ayanamsa)

        if prev_sign is not None and pos.sign != prev_sign:
            changes.append({
                "planet": planet,
                "date": d.isoformat(),
                "from_sign": prev_sign,
                "to_sign": pos.sign,
                "degree": round(pos.degree_in_sign, 4),
                "nakshatra": pos.nakshatra,
                "retrograde": pos.retrograde,
            })
        prev_sign = pos.sign

    return changes


def get_all_transits(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Get all sign changes for all 9 planets in date range."""
    all_changes = []
    planet_changes = {}

    for planet in PLANETS_9:
        changes = find_sign_changes(planet, start_date, end_date, tz_offset, ayanamsa)
        planet_changes[planet] = changes
        all_changes.extend(changes)

    # Sort all changes by date
    all_changes.sort(key=lambda x: x["date"])

    return {
        "start_date": start_date.isoformat(),
        "end_date": end_date.isoformat(),
        "total_transits": len(all_changes),
        "by_planet": planet_changes,
        "chronological": all_changes,
    }


def find_nakshatra_changes(
    planet: str,
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find all nakshatra changes for a planet in date range."""
    set_ayanamsa(ayanamsa)
    changes = []
    prev_nak = None

    for d in date_range(start_date, end_date):
        dt = datetime(d.year, d.month, d.day, 6, 0, 0)
        utc_dt = local_to_utc(dt, tz_offset)
        jd = datetime_to_jd(utc_dt)
        pos = get_planet_position(jd, planet, ayanamsa)

        if prev_nak is not None and pos.nakshatra != prev_nak:
            changes.append({
                "planet": planet,
                "date": d.isoformat(),
                "from_nakshatra": prev_nak,
                "to_nakshatra": pos.nakshatra,
                "sign": pos.sign,
                "degree": round(pos.degree_in_sign, 4),
            })
        prev_nak = pos.nakshatra

    return changes
