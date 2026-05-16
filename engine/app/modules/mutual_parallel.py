"""
Planets Mutual Parallel — Track when planets have same declination (parallel)
or opposite declination (contra-parallel).

Parallel = same declination (both N or both S) — acts like conjunction
Contra-parallel = opposite declination (one N, one S) — acts like opposition
Orb: typically 1° for exact parallels
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any

import swisseph as swe

from app.core import (
    PLANETS_9, PLANET_IDS, set_ayanamsa,
    datetime_to_jd, local_to_utc, normalize_degree, date_range,
    get_planet_position,
)

PARALLEL_ORB = 1.0  # degrees


def _get_declination(jd: float, planet: str) -> float:
    """Get planet's declination in degrees."""
    if planet == "Ketu":
        # Ketu = Rahu + 180
        flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
        result, _ = swe.calc_ut(jd, PLANET_IDS["Rahu"], flags)
        # Declination is result[1] for equatorial coordinates
        return -result[1]  # Ketu has opposite declination to Rahu

    planet_id = PLANET_IDS[planet]
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[1]  # declination


def get_mutual_parallels(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Find all parallel and contra-parallel aspects for a date."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    # Get declinations and positions
    declinations = {}
    positions = {}
    for planet in PLANETS_9:
        declinations[planet] = _get_declination(jd, planet)
        positions[planet] = get_planet_position(jd, planet, ayanamsa)

    parallels = []
    checked = set()

    for p1 in PLANETS_9:
        for p2 in PLANETS_9:
            if p1 == p2:
                continue
            pair = tuple(sorted([p1, p2]))
            if pair in checked:
                continue
            checked.add(pair)

            d1 = declinations[p1]
            d2 = declinations[p2]

            # Parallel: same sign declination, close value
            if abs(d1 - d2) <= PARALLEL_ORB:
                parallels.append({
                    "planet_1": p1,
                    "planet_2": p2,
                    "type": "Parallel",
                    "effect": "Conjunction-like",
                    "declination_1": round(d1, 4),
                    "declination_2": round(d2, 4),
                    "orb": round(abs(d1 - d2), 4),
                    "sign_1": positions[p1].sign,
                    "sign_2": positions[p2].sign,
                })

            # Contra-parallel: opposite sign declination, close absolute value
            if abs(abs(d1) - abs(d2)) <= PARALLEL_ORB and d1 * d2 < 0:
                parallels.append({
                    "planet_1": p1,
                    "planet_2": p2,
                    "type": "Contra-Parallel",
                    "effect": "Opposition-like",
                    "declination_1": round(d1, 4),
                    "declination_2": round(d2, 4),
                    "orb": round(abs(abs(d1) - abs(d2)), 4),
                    "sign_1": positions[p1].sign,
                    "sign_2": positions[p2].sign,
                })

    # Planet declinations table
    decl_table = [
        {
            "planet": p,
            "declination": round(declinations[p], 4),
            "direction": "North" if declinations[p] >= 0 else "South",
            "sign": positions[p].sign,
        }
        for p in PLANETS_9
    ]

    return {
        "date": target_date.isoformat(),
        "declinations": decl_table,
        "parallels": parallels,
        "total": len(parallels),
    }


def get_parallels_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get mutual parallels for date range."""
    return [get_mutual_parallels(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
