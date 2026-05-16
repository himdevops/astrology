"""
graha_yuddha.py — Planetary War detection.
============================================
War = two Tara Grahas within 1° longitude.
Winner = planet with higher latitude (further north).
Only: Mars, Mercury, Jupiter, Venus, Saturn.
"""
from __future__ import annotations

from datetime import date
from typing import List, Dict, Any

from core.constants import TARA_GRAHAS
from core.ephemeris import get_planet_position, set_ayanamsa
from core.utils import angular_distance, datetime_to_jd, local_to_utc, date_range, date_to_datetime

YUDDHA_ORB = 1.0


def check_daily(
    target_date: date, tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    jd = datetime_to_jd(local_to_utc(date_to_datetime(target_date), tz_offset))
    set_ayanamsa(ayanamsa)

    positions = {p: get_planet_position(jd, p, ayanamsa) for p in TARA_GRAHAS}
    wars, checked = [], set()

    for p1 in TARA_GRAHAS:
        for p2 in TARA_GRAHAS:
            if p1 == p2:
                continue
            pair = tuple(sorted([p1, p2]))
            if pair in checked:
                continue
            checked.add(pair)

            dist = angular_distance(positions[p1].longitude, positions[p2].longitude)
            if dist <= YUDDHA_ORB:
                lat1, lat2 = positions[p1].latitude, positions[p2].latitude
                winner = p1 if lat1 > lat2 else p2
                loser = p2 if winner == p1 else p1
                wars.append({
                    "planet_1": p1, "planet_2": p2, "distance": round(dist, 4),
                    "sign": positions[p1].sign,
                    "degree_1": round(positions[p1].degree_in_sign, 4),
                    "degree_2": round(positions[p2].degree_in_sign, 4),
                    "latitude_1": round(lat1, 4), "latitude_2": round(lat2, 4),
                    "winner": winner, "loser": loser,
                    "description": f"{winner} wins over {loser} (higher latitude)",
                })

    return {
        "date": target_date.isoformat(), "wars": wars,
        "war_count": len(wars), "is_yuddha_day": len(wars) > 0,
    }


def find_events(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    all_wars = []
    for d in date_range(start_date, end_date):
        result = check_daily(d, tz_offset, ayanamsa)
        for w in result["wars"]:
            w["date"] = d.isoformat()
            all_wars.append(w)
    return all_wars


def get_range(
    start_date: date, end_date: date,
    tz_offset: float = 5.5, ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    return [check_daily(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
