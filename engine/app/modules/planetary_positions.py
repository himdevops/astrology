"""
Planetary Positions — Daily positions of all 9 planets.
Like Drikpanchang's "Planetary Positions" page.
Shows sign, degree, nakshatra, pada, speed, retrograde status for each date.
"""
from __future__ import annotations

from datetime import date, datetime, timedelta
from typing import List, Dict, Any, Optional

from app.core import (
    PLANETS_9, get_all_planets, set_ayanamsa,
    datetime_to_jd, local_to_utc, date_range,
)


def get_daily_positions(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Get all planet positions for a specific date (at sunrise ~6:00 AM local)."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    set_ayanamsa(ayanamsa)
    planets = get_all_planets(jd, ayanamsa)

    return {
        "date": target_date.isoformat(),
        "ayanamsa": ayanamsa,
        "planets": [p.to_dict() for p in planets],
    }


def get_positions_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get planet positions for a range of dates."""
    results = []
    for d in date_range(start_date, end_date):
        results.append(get_daily_positions(d, tz_offset, ayanamsa))
    return results
