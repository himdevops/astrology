"""
retrograde.py — Retrograde detection & period finder.
======================================================
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import PLANETS_9
from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc, date_range, date_to_datetime


def get_daily_status(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Retrograde status of all 9 planets for one date."""
    dt = date_to_datetime(target_date)
    jd = datetime_to_jd(local_to_utc(dt, tz_offset))
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
        "retrograde_count": sum(
            1 for s in statuses
            if s["retrograde"] and s["planet"] not in ("Rahu", "Ketu")
        ),
    }


def find_periods(
    planet: str, start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find all retrograde start/end dates for a planet in range."""
    if planet in ("Sun", "Moon"):
        return []

    set_ayanamsa(ayanamsa)
    periods, in_retro, retro_start, retro_sign = [], False, None, None

    for d in date_range(start_date, end_date):
        jd = datetime_to_jd(local_to_utc(date_to_datetime(d), tz_offset))
        pos = get_planet_position(jd, planet, ayanamsa)

        if pos.retrograde and not in_retro:
            in_retro, retro_start, retro_sign = True, d, pos.sign
        elif not pos.retrograde and in_retro:
            in_retro = False
            periods.append({
                "planet": planet, "start": retro_start.isoformat(),
                "end": d.isoformat(), "duration_days": (d - retro_start).days,
                "start_sign": retro_sign, "end_sign": pos.sign,
            })

    if in_retro:
        periods.append({
            "planet": planet, "start": retro_start.isoformat(),
            "end": end_date.isoformat(), "duration_days": (end_date - retro_start).days,
            "start_sign": retro_sign, "end_sign": "ongoing",
        })
    return periods


def get_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    return [get_daily_status(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
