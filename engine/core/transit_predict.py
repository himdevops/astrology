"""
transit_predict.py — Daily/Monthly/Yearly transit predictions using Ashtakavarga.
==================================================================================
Uses BAV + SAV + Kaksha to rate each day based on planetary transits.
"""
from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, List, Any

from core.constants import SIGNS
from core.ashtakavarga import (
    calc_kaksha, _get_sign_index, ASHTAK_PLANETS, KAKSHA_LORDS,
)


def _compute_daily_score(
    transit_signs: Dict[str, int],
    transit_lons: Dict[str, float],
    all_bav: Dict[str, List[int]],
    sav: List[int],
) -> Dict[str, Any]:
    """
    Compute a composite score for a single day.

    For each transiting planet:
      - BAV score in the transit sign (planet's own benefic points there)
      - SAV score in the transit sign (total points there)
      - Kaksha lord benefic check

    Weighted composite:
      Moon (fast, daily impact): weight 3
      Sun: weight 2
      Mercury, Venus: weight 1.5
      Mars, Jupiter, Saturn: weight 2 (slow, significant)
    """
    planet_weights = {
        "Sun": 2.0, "Moon": 3.0, "Mars": 2.0, "Mercury": 1.5,
        "Jupiter": 2.5, "Venus": 1.5, "Saturn": 2.5,
    }

    total_weighted_score = 0.0
    total_weight = 0.0
    planet_details = []

    for planet in ASHTAK_PLANETS:
        if planet not in transit_signs:
            continue

        sign_idx = transit_signs[planet]
        bav_score = all_bav.get(planet, [0]*12)[sign_idx]
        sav_score = sav[sign_idx]

        # Kaksha info
        kaksha_info = None
        if planet in transit_lons:
            kaksha_info = calc_kaksha(transit_lons[planet])

        # Planet rating based on BAV
        if bav_score >= 5:
            p_rating = "excellent"
        elif bav_score >= 4:
            p_rating = "good"
        elif bav_score >= 3:
            p_rating = "neutral"
        elif bav_score >= 2:
            p_rating = "bad"
        else:
            p_rating = "very_bad"

        weight = planet_weights.get(planet, 1.0)

        # Normalize BAV to 0-1 scale (max 8 points)
        norm_score = bav_score / 8.0
        total_weighted_score += norm_score * weight
        total_weight += weight

        detail = {
            "planet": planet,
            "sign": SIGNS[sign_idx],
            "bav": bav_score,
            "sav": sav_score,
            "rating": p_rating,
        }
        if kaksha_info:
            detail["kaksha"] = kaksha_info["kaksha"]
            detail["kaksha_lord"] = kaksha_info["kaksha_lord"]

        planet_details.append(detail)

    # Composite score (0-100)
    composite = round((total_weighted_score / total_weight) * 100, 1) if total_weight > 0 else 50.0

    # Day rating
    if composite >= 70:
        day_rating = "excellent"
    elif composite >= 55:
        day_rating = "good"
    elif composite >= 40:
        day_rating = "neutral"
    elif composite >= 25:
        day_rating = "bad"
    else:
        day_rating = "very_bad"

    return {
        "score": composite,
        "rating": day_rating,
        "planets": planet_details,
    }


def predict_date_range(
    start_date: date,
    end_date: date,
    all_bav: Dict[str, List[int]],
    sav: List[int],
    get_transit_positions,  # callable(jd) -> dict of planet -> (lon, sign_idx)
    tz_offset: float = 5.5,
) -> List[Dict[str, Any]]:
    """
    Generate daily predictions for a date range.

    Parameters:
        start_date, end_date: Date range
        all_bav: Birth chart BAV
        sav: Birth chart SAV
        get_transit_positions: Callable that takes Julian Day and returns
                               dict of planet → (longitude, sign_index)
        tz_offset: Timezone offset

    Returns:
        List of daily predictions with scores and ratings.
    """
    from core.utils import datetime_to_jd

    days = []
    current = start_date

    while current <= end_date:
        # Get transit positions at noon local time
        dt = datetime(current.year, current.month, current.day, 12, 0, 0)
        utc_dt = dt - timedelta(hours=tz_offset)
        jd = datetime_to_jd(utc_dt)

        transit_data = get_transit_positions(jd)
        transit_signs = {}
        transit_lons = {}

        for planet, (lon, sign_idx) in transit_data.items():
            transit_signs[planet] = sign_idx
            transit_lons[planet] = lon

        day_result = _compute_daily_score(transit_signs, transit_lons, all_bav, sav)
        day_result["date"] = current.strftime("%d-%m-%Y")
        day_result["weekday"] = current.strftime("%A")

        days.append(day_result)
        current += timedelta(days=1)

    return days


def summarize_month(daily_predictions: List[Dict]) -> Dict[str, Any]:
    """Summarize a month's predictions."""
    if not daily_predictions:
        return {}

    scores = [d["score"] for d in daily_predictions]
    ratings = [d["rating"] for d in daily_predictions]

    excellent_days = sum(1 for r in ratings if r == "excellent")
    good_days = sum(1 for r in ratings if r == "good")
    neutral_days = sum(1 for r in ratings if r == "neutral")
    bad_days = sum(1 for r in ratings if r in ("bad", "very_bad"))

    best_days = sorted(daily_predictions, key=lambda d: d["score"], reverse=True)[:5]
    worst_days = sorted(daily_predictions, key=lambda d: d["score"])[:5]

    return {
        "total_days": len(daily_predictions),
        "average_score": round(sum(scores) / len(scores), 1),
        "excellent_days": excellent_days,
        "good_days": good_days,
        "neutral_days": neutral_days,
        "bad_days": bad_days,
        "best_days": [{"date": d["date"], "score": d["score"], "rating": d["rating"]} for d in best_days],
        "worst_days": [{"date": d["date"], "score": d["score"], "rating": d["rating"]} for d in worst_days],
    }
