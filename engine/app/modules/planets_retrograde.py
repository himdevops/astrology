"""
Planets Retrograde — Track retrograde periods for all planets.
Shows when each planet goes retrograde/direct, duration, and affected signs.
Sun & Moon never retrograde. Rahu/Ketu are always retrograde (mean node).
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Dict, Any

from app.core import (
    PLANETS_9, get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, date_range,
)

# Planets that can go retrograde (exclude Sun, Moon — they never do)
# Rahu/Ketu are always retrograde (mean node), included for reference
RETROGRADE_PLANETS = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Rahu", "Ketu"]


def get_daily_retrograde_status(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Get retrograde status of all planets for a specific date."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    statuses = []
    for planet in PLANETS_9:
        pos = get_planet_position(jd, planet, ayanamsa)
        statuses.append({
            "planet": planet,
            "retrograde": pos.retrograde,
            "speed": round(pos.speed, 6),
            "sign": pos.sign,
            "degree": round(pos.degree_in_sign, 4),
            "nakshatra": pos.nakshatra,
            "status": "Retrograde" if pos.retrograde else "Direct",
        })

    return {
        "date": target_date.isoformat(),
        "planets": statuses,
        "retrograde_count": sum(1 for s in statuses if s["retrograde"] and s["planet"] not in ["Rahu", "Ketu"]),
    }


def find_retrograde_periods(
    planet: str,
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """
    Find all retrograde periods for a planet in a date range.
    Returns list of {start, end, duration_days, start_sign, end_sign}.
    """
    if planet in ("Sun", "Moon"):
        return []

    set_ayanamsa(ayanamsa)
    periods = []
    in_retro = False
    retro_start = None
    retro_start_sign = None

    for d in date_range(start_date, end_date):
        dt = datetime(d.year, d.month, d.day, 6, 0, 0)
        utc_dt = local_to_utc(dt, tz_offset)
        jd = datetime_to_jd(utc_dt)
        pos = get_planet_position(jd, planet, ayanamsa)

        if pos.retrograde and not in_retro:
            in_retro = True
            retro_start = d
            retro_start_sign = pos.sign
        elif not pos.retrograde and in_retro:
            in_retro = False
            periods.append({
                "planet": planet,
                "start": retro_start.isoformat(),
                "end": d.isoformat(),
                "duration_days": (d - retro_start).days,
                "start_sign": retro_start_sign,
                "end_sign": pos.sign,
            })

    # If still retrograde at end
    if in_retro:
        periods.append({
            "planet": planet,
            "start": retro_start.isoformat(),
            "end": end_date.isoformat(),
            "duration_days": (end_date - retro_start).days,
            "start_sign": retro_start_sign,
            "end_sign": "ongoing",
        })

    return periods


def get_retrograde_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get daily retrograde status for date range."""
    return [get_daily_retrograde_status(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
