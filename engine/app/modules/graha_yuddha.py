"""
Graha Yuddha (Planetary War) — When two planets are within 1° longitude.
Only applies to: Mars, Mercury, Jupiter, Venus, Saturn (Tara Grahas).
Sun, Moon, Rahu, Ketu are excluded.

The planet with higher latitude (further north) wins the war.
The loser is considered weakened in the chart.
"""
from __future__ import annotations

from datetime import date, datetime
from typing import List, Dict, Any

from app.core import (
    get_planet_position, set_ayanamsa,
    datetime_to_jd, local_to_utc, normalize_degree, date_range,
)

# Only Tara Grahas participate in Graha Yuddha
YUDDHA_PLANETS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

YUDDHA_ORB = 1.0  # degrees — planets within 1° are in war


def _angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes."""
    diff = abs(normalize_degree(lon1) - normalize_degree(lon2))
    return min(diff, 360 - diff)


def check_graha_yuddha(
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """Check for Graha Yuddha (planetary wars) on a given date."""
    dt = datetime(target_date.year, target_date.month, target_date.day, 6, 0, 0)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)
    set_ayanamsa(ayanamsa)

    positions = {}
    for planet in YUDDHA_PLANETS:
        positions[planet] = get_planet_position(jd, planet, ayanamsa)

    wars = []
    checked = set()

    for p1 in YUDDHA_PLANETS:
        for p2 in YUDDHA_PLANETS:
            if p1 == p2:
                continue
            pair = tuple(sorted([p1, p2]))
            if pair in checked:
                continue
            checked.add(pair)

            dist = _angular_distance(positions[p1].longitude, positions[p2].longitude)

            if dist <= YUDDHA_ORB:
                # Winner has higher latitude (further north)
                lat1 = positions[p1].latitude
                lat2 = positions[p2].latitude
                winner = p1 if lat1 > lat2 else p2
                loser = p2 if winner == p1 else p1

                wars.append({
                    "planet_1": p1,
                    "planet_2": p2,
                    "distance": round(dist, 4),
                    "sign": positions[p1].sign,
                    "degree_1": round(positions[p1].degree_in_sign, 4),
                    "degree_2": round(positions[p2].degree_in_sign, 4),
                    "latitude_1": round(lat1, 4),
                    "latitude_2": round(lat2, 4),
                    "winner": winner,
                    "loser": loser,
                    "winner_latitude": round(max(lat1, lat2), 4),
                    "description": f"{winner} wins war against {loser} (higher latitude)",
                })

    return {
        "date": target_date.isoformat(),
        "wars": wars,
        "war_count": len(wars),
        "is_yuddha_day": len(wars) > 0,
    }


def find_yuddha_periods(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Find all Graha Yuddha events in a date range."""
    all_wars = []
    for d in date_range(start_date, end_date):
        result = check_graha_yuddha(d, tz_offset, ayanamsa)
        if result["wars"]:
            for war in result["wars"]:
                war["date"] = d.isoformat()
                all_wars.append(war)

    return all_wars


def get_yuddha_range(
    start_date: date,
    end_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> List[Dict[str, Any]]:
    """Get graha yuddha status for date range."""
    return [check_graha_yuddha(d, tz_offset, ayanamsa) for d in date_range(start_date, end_date)]
