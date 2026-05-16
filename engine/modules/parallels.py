"""
parallels.py — Declination-based parallel & contra-parallel.
=============================================================
Parallel (same declination) ≈ conjunction effect.
Contra-parallel (opposite declination) ≈ opposition effect.
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import PLANETS_9, PLANET_IDS
from core.ephemeris import get_planet_position, set_ayanamsa, calc_planet_equatorial
from core.utils import datetime_to_jd, local_to_utc, date_range, date_to_datetime

PARALLEL_ORB = 1.0


def _get_declination(jd: float, planet: str) -> float:
    if planet == "Ketu":
        _, dec = calc_planet_equatorial(jd, PLANET_IDS["Rahu"])
        return -dec
    _, dec = calc_planet_equatorial(jd, PLANET_IDS[planet])
    return dec


def get_daily(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    jd = datetime_to_jd(local_to_utc(date_to_datetime(target_date), tz_offset))
    set_ayanamsa(ayanamsa)

    declinations, positions = {}, {}
    for p in PLANETS_9:
        declinations[p] = _get_declination(jd, p)
        positions[p] = get_planet_position(jd, p, ayanamsa)

    parallels, checked = [], set()
    for p1 in PLANETS_9:
        for p2 in PLANETS_9:
            if p1 == p2:
                continue
            pair = tuple(sorted([p1, p2]))
            if pair in checked:
                continue
            checked.add(pair)

            d1, d2 = declinations[p1], declinations[p2]
            if abs(d1 - d2) <= PARALLEL_ORB:
                parallels.append({
                    "planet_1": p1, "planet_2": p2, "type": "Parallel",
                    "effect": "Conjunction-like",
                    "declination_1": round(d1, 4), "declination_2": round(d2, 4),
                    "orb": round(abs(d1 - d2), 4),
                    "sign_1": positions[p1].sign, "sign_2": positions[p2].sign,
                })
            if abs(abs(d1) - abs(d2)) <= PARALLEL_ORB and d1 * d2 < 0:
                parallels.append({
                    "planet_1": p1, "planet_2": p2, "type": "Contra-Parallel",
                    "effect": "Opposition-like",
                    "declination_1": round(d1, 4), "declination_2": round(d2, 4),
                    "orb": round(abs(abs(d1) - abs(d2)), 4),
                    "sign_1": positions[p1].sign, "sign_2": positions[p2].sign,
                })

    decl_table = [{
        "planet": p, "declination": round(declinations[p], 4),
        "direction": "North" if declinations[p] >= 0 else "South",
        "sign": positions[p].sign,
    } for p in PLANETS_9]

    return {
        "date": target_date.isoformat(),
        "declinations": decl_table, "parallels": parallels, "total": len(parallels),
    }


def get_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    return [get_daily(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
