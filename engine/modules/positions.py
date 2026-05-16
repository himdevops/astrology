"""
positions.py — Daily planetary positions module.
=================================================
Core module: get planet positions for any date or date range.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc, date_range, date_to_datetime


def get_daily_positions(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    latitude: float = 19.0760,
    longitude: float = 72.8777,
) -> Dict[str, Any]:
    """All 9 planet positions + Ascendant for a specific date (at 6:00 AM local)."""
    dt = date_to_datetime(target_date)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    planets = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, latitude, longitude, ayanamsa)

    # Put Ascendant first
    all_positions = [ascendant] + planets
    return {
        "date": target_date.isoformat(),
        "ayanamsa": ayanamsa,
        "ascendant": ascendant.to_dict(),
        "planets": [p.to_dict() for p in all_positions],
    }


def get_positions_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Planet positions for every date in range."""
    return [get_daily_positions(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
