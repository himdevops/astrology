"""
kaksha_transit.py — Advanced Kaksha-based transit engine (hourly/minute precision).
====================================================================================
Multi-layer Ashtakavarga transit prediction system per BPHS + Vinay Aditya's
"Practical Ashtakavarga" methodology:

Layer 1: BAV/SAV bindus — basic sign-level benefic points
Layer 2: Kaksha refinement — 8 sub-divisions per sign (3°45' each)
         Benefic kaksha → full strength, malefic → reduced
Layer 3: SAV Weighted Planetary Strength — sign-specific multiplication
         factors (Vinay Aditya method, avg=196 for average day)
Layer 4: Kaksha benefic count — how many of 7 planets are in benefic
         kakshas (3+ = good day per BPHS)
Layer 5: Moon nakshatra tracking — fastest planet, changes sub-daily

Kaksha lords in order: Saturn, Jupiter, Mars, Sun, Venus, Mercury, Moon, Lagna.
When a planet transits a kaksha whose lord contributed a benefic point
in that planet's BAV for that sign → BENEFIC transit (green).
Otherwise → MALEFIC transit (red).
"""
from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, List, Any, Callable, Optional, Tuple

from core.constants import SIGNS
from core.ashtakavarga import (
    ASHTAK_PLANETS, KAKSHA_LORDS, BAV_RULES,
    _get_sign_index, calc_kaksha,
)


# ═══════════════════════════════════════════════════════════════
# SAV Weighted Factors per sign (from Vinay Aditya "Practical Ashtakavarga")
# Based on planet's natural relationship with sign lords.
# Index 0=Aries, 1=Taurus, ... 11=Pisces
# ═══════════════════════════════════════════════════════════════
SAV_WEIGHT_FACTORS = {
    "Sun":     [1.5, 0.5, 1.0, 1.2, 1.4, 1.0, 0.4, 1.2, 1.2, 0.4, 0.5, 1.2],
    "Moon":    [1.0, 1.5, 1.2, 1.4, 1.2, 1.2, 1.0, 0.8, 1.0, 1.0, 0.8, 1.0],
    "Mars":    [1.4, 1.0, 0.5, 0.8, 1.2, 0.5, 1.0, 1.2, 1.2, 1.5, 0.8, 1.2],
    "Mercury": [0.5, 1.2, 1.4, 0.5, 1.2, 1.6, 1.2, 0.5, 1.0, 1.0, 1.0, 0.8],
    "Jupiter": [1.2, 0.5, 0.8, 1.5, 1.2, 0.8, 0.5, 1.2, 1.4, 0.4, 0.8, 1.4],
    "Venus":   [1.0, 1.2, 1.0, 0.5, 0.5, 0.8, 1.4, 1.0, 1.0, 1.2, 1.2, 1.5],
    "Saturn":  [0.4, 1.2, 1.2, 0.5, 0.5, 1.2, 1.5, 0.5, 1.0, 1.2, 1.4, 1.0],
}

# 27 Nakshatras with Vimshottari lords (for Moon nakshatra tracking)
NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury",
]
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# Planet weights for composite scoring
PLANET_WEIGHTS = {
    "Sun": 2.0, "Moon": 3.0, "Mars": 2.0, "Mercury": 1.5,
    "Jupiter": 2.5, "Venus": 1.5, "Saturn": 2.5,
}

# Average SAV weighted total for reference (per Vinay Aditya)
SAV_WEIGHTED_AVERAGE = 196.0


def _is_kaksha_benefic(
    planet: str,
    sign_idx: int,
    kaksha_lord: str,
    birth_signs: Dict[str, int],
) -> bool:
    """
    Check if a planet transiting a particular kaksha is benefic.

    The kaksha lord must have contributed a benefic point to this planet's
    BAV in this sign. We check: from kaksha_lord's birth position, is
    this sign a benefic house for the planet?

    Parameters:
        planet:      Transiting planet (Sun, Moon, etc.)
        sign_idx:    Sign the planet is transiting (0-11)
        kaksha_lord: Lord of the kaksha the planet is in
        birth_signs: Birth chart sign positions of all planets + Lagna
    """
    rules = BAV_RULES.get(planet, {})
    benefic_houses = rules.get(kaksha_lord, [])
    if not benefic_houses:
        return False

    contrib_sign = birth_signs.get(kaksha_lord)
    if contrib_sign is None:
        return False

    house_from_contrib = ((sign_idx - contrib_sign) % 12) + 1
    return house_from_contrib in benefic_houses


def _get_nakshatra(lon: float) -> Dict[str, Any]:
    """Get nakshatra info from longitude."""
    nak_idx = int(lon / (360.0 / 27)) % 27
    deg_in_nak = lon % (360.0 / 27)
    pada = int(deg_in_nak / (360.0 / 108)) + 1
    if pada > 4:
        pada = 4
    return {
        "index": nak_idx,
        "name": NAKSHATRA_NAMES[nak_idx],
        "lord": NAKSHATRA_LORDS[nak_idx],
        "pada": pada,
    }


def compute_moment_kaksha(
    transit_positions: Dict[str, Tuple[float, int]],
    all_bav: Dict[str, List[int]],
    sav: List[int],
    birth_signs: Dict[str, int],
) -> Dict[str, Any]:
    """
    Compute multi-layer kaksha details for a single moment in time.

    5 Layers of analysis:
      L1: BAV/SAV bindus (sign-level)
      L2: Kaksha benefic/malefic (sub-sign precision)
      L3: SAV Weighted Planetary Strength (sign-specific factors)
      L4: Kaksha benefic count (3+ out of 7 = good, per BPHS)
      L5: Moon nakshatra + lord analysis

    Parameters:
        transit_positions: Dict of planet → (longitude, sign_index) at this moment
        all_bav:          Birth chart BAV
        sav:              Birth chart SAV
        birth_signs:      Birth chart sign positions of all planets + Lagna

    Returns:
        Dict with per-planet kaksha info and multi-layer composite score.
    """
    planet_details = []
    total_weighted = 0.0
    total_weight = 0.0
    sav_weighted_total = 0.0
    moon_info = None

    for planet in ASHTAK_PLANETS:
        if planet not in transit_positions:
            continue

        lon, sign_idx = transit_positions[planet]
        bav_score = all_bav.get(planet, [0] * 12)[sign_idx]
        sav_score = sav[sign_idx]
        kaksha_info = calc_kaksha(lon)
        kaksha_lord = kaksha_info["kaksha_lord"]
        kaksha_num = kaksha_info["kaksha"]

        # L2: Kaksha benefic check
        benefic = _is_kaksha_benefic(planet, sign_idx, kaksha_lord, birth_signs)

        # L3: SAV Weighted factor
        sav_factor = SAV_WEIGHT_FACTORS.get(planet, [1.0] * 12)[sign_idx]
        sav_weighted = round(sav_score * sav_factor, 1)
        sav_weighted_total += sav_weighted

        # Composite: BAV with kaksha refinement
        # Benefic kaksha → full BAV strength; malefic → 40% (still some effect from sign)
        effective_bav = bav_score if benefic else (bav_score * 0.4)

        weight = PLANET_WEIGHTS.get(planet, 1.0)
        total_weighted += (effective_bav / 8.0) * weight
        total_weight += weight

        detail = {
            "planet": planet,
            "sign": SIGNS[sign_idx],
            "sign_idx": sign_idx,
            "longitude": round(lon, 4),
            "bav": bav_score,
            "sav": sav_score,
            "sav_weighted": sav_weighted,
            "sav_factor": sav_factor,
            "kaksha": kaksha_num,
            "kaksha_lord": kaksha_lord,
            "benefic": benefic,
        }

        # L5: Moon nakshatra tracking
        if planet == "Moon":
            nak = _get_nakshatra(lon)
            detail["nakshatra"] = nak["name"]
            detail["nakshatra_lord"] = nak["lord"]
            detail["nakshatra_pada"] = nak["pada"]
            # Check nakshatra lord's BAV placement
            nak_lord = nak["lord"]
            if nak_lord in birth_signs and nak_lord in all_bav:
                nak_lord_sign = birth_signs[nak_lord]
                nak_lord_bav = all_bav.get(nak_lord, [0] * 12)
                detail["nakshatra_lord_bav"] = sum(nak_lord_bav)
            moon_info = detail

        planet_details.append(detail)

    # L1+L2 Composite score (0-100)
    composite = round((total_weighted / total_weight) * 100, 1) if total_weight > 0 else 50.0

    # L4: Kaksha benefic count (BPHS: 3+ is good)
    benefic_count = sum(1 for p in planet_details if p["benefic"])

    # L3: SAV weighted total (avg 196 per Vinay Aditya)
    sav_weighted_total = round(sav_weighted_total, 1)
    sav_weighted_rating = (
        "excellent" if sav_weighted_total >= 240 else
        "good" if sav_weighted_total >= 210 else
        "neutral" if sav_weighted_total >= 180 else
        "bad" if sav_weighted_total >= 150 else
        "very_bad"
    )

    # Final multi-layer rating
    # Combine: kaksha composite (50%), benefic count (25%), SAV weighted (25%)
    benefic_norm = benefic_count / 7.0 * 100  # 0-100
    sav_norm = min((sav_weighted_total / SAV_WEIGHTED_AVERAGE) * 50, 100)  # 0-100
    final_score = round(composite * 0.50 + benefic_norm * 0.25 + sav_norm * 0.25, 1)

    if final_score >= 70:
        rating = "excellent"
    elif final_score >= 55:
        rating = "good"
    elif final_score >= 40:
        rating = "neutral"
    elif final_score >= 25:
        rating = "bad"
    else:
        rating = "very_bad"

    result = {
        "score": final_score,
        "rating": rating,
        "kaksha_score": composite,
        "benefic_count": benefic_count,
        "total_planets": len(planet_details),
        "sav_weighted_total": sav_weighted_total,
        "sav_weighted_rating": sav_weighted_rating,
        "planets": planet_details,
    }

    # Add Moon nakshatra info at top level
    if moon_info:
        result["moon_nakshatra"] = moon_info.get("nakshatra")
        result["moon_nakshatra_lord"] = moon_info.get("nakshatra_lord")
        result["moon_sign"] = moon_info.get("sign")

    return result


def compute_daily_kaksha_grid(
    target_date: date,
    all_bav: Dict[str, List[int]],
    sav: List[int],
    birth_signs: Dict[str, int],
    get_transit_positions: Callable,
    tz_offset: float = 5.5,
) -> Dict[str, Any]:
    """
    Compute hourly kaksha grid for a single day (24 hours).

    Returns per-planet kaksha transitions throughout the day,
    hourly composite scores, and best/worst hours.
    """
    from core.utils import datetime_to_jd

    hourly = []

    for hour in range(24):
        dt = datetime(target_date.year, target_date.month, target_date.day, hour, 0, 0)
        utc_dt = dt - timedelta(hours=tz_offset)
        jd = datetime_to_jd(utc_dt)

        transit_data = get_transit_positions(jd)
        moment = compute_moment_kaksha(transit_data, all_bav, sav, birth_signs)
        moment["hour"] = hour
        moment["time"] = f"{hour:02d}:00"
        hourly.append(moment)

    # Per-planet kaksha timeline (for the grid visualization)
    planet_timelines = {}
    for planet in ASHTAK_PLANETS:
        timeline = []
        for h in hourly:
            p_data = next((p for p in h["planets"] if p["planet"] == planet), None)
            if p_data:
                timeline.append({
                    "hour": h["hour"],
                    "kaksha": p_data["kaksha"],
                    "kaksha_lord": p_data["kaksha_lord"],
                    "benefic": p_data["benefic"],
                    "sign": p_data["sign"],
                    "bav": p_data["bav"],
                    "longitude": p_data["longitude"],
                })
        planet_timelines[planet] = timeline

    # Dominant kaksha lord per planet for the day (most frequent)
    planet_summary = {}
    for planet in ASHTAK_PLANETS:
        tl = planet_timelines.get(planet, [])
        if not tl:
            continue
        # Most frequent kaksha lord
        lord_counts = {}
        for t in tl:
            lord_counts[t["kaksha_lord"]] = lord_counts.get(t["kaksha_lord"], 0) + 1
        dominant_lord = max(lord_counts, key=lord_counts.get)
        benefic_hours = sum(1 for t in tl if t["benefic"])
        bav = tl[0]["bav"] if tl else 0
        sign = tl[0]["sign"] if tl else ""

        planet_summary[planet] = {
            "sign": sign,
            "bav": bav,
            "dominant_kaksha_lord": dominant_lord,
            "benefic_hours": benefic_hours,
            "malefic_hours": len(tl) - benefic_hours,
            "benefic_pct": round(benefic_hours / len(tl) * 100) if tl else 0,
        }

    # Best/worst hours
    scores = [(h["hour"], h["score"]) for h in hourly]
    scores_sorted = sorted(scores, key=lambda x: x[1], reverse=True)
    best_hours = scores_sorted[:3]
    worst_hours = scores_sorted[-3:]

    # Daily average
    avg_score = round(sum(h["score"] for h in hourly) / len(hourly), 1)
    avg_rating = "excellent" if avg_score >= 70 else "good" if avg_score >= 55 else "neutral" if avg_score >= 40 else "bad" if avg_score >= 25 else "very_bad"

    return {
        "date": target_date.strftime("%d-%m-%Y"),
        "weekday": target_date.strftime("%A"),
        "avg_score": avg_score,
        "avg_rating": avg_rating,
        "hourly": hourly,
        "planet_timelines": planet_timelines,
        "planet_summary": planet_summary,
        "best_hours": [{"hour": h, "time": f"{h:02d}:00", "score": s} for h, s in best_hours],
        "worst_hours": [{"hour": h, "time": f"{h:02d}:00", "score": s} for h, s in worst_hours],
    }


def compute_minute_detail(
    target_date: date,
    target_hour: int,
    all_bav: Dict[str, List[int]],
    sav: List[int],
    birth_signs: Dict[str, int],
    get_transit_positions: Callable,
    tz_offset: float = 5.5,
    interval_minutes: int = 10,
) -> Dict[str, Any]:
    """
    Compute minute-level kaksha detail for a specific hour.
    Default: every 10 minutes (6 slices per hour).
    """
    from core.utils import datetime_to_jd

    slices = []
    minutes = list(range(0, 60, interval_minutes))

    for minute in minutes:
        dt = datetime(target_date.year, target_date.month, target_date.day,
                      target_hour, minute, 0)
        utc_dt = dt - timedelta(hours=tz_offset)
        jd = datetime_to_jd(utc_dt)

        transit_data = get_transit_positions(jd)
        moment = compute_moment_kaksha(transit_data, all_bav, sav, birth_signs)
        moment["time"] = f"{target_hour:02d}:{minute:02d}"
        moment["minute"] = minute
        slices.append(moment)

    return {
        "date": target_date.strftime("%d-%m-%Y"),
        "hour": target_hour,
        "interval_minutes": interval_minutes,
        "slices": slices,
    }


def compute_monthly_kaksha_grid(
    start_date: date,
    end_date: date,
    all_bav: Dict[str, List[int]],
    sav: List[int],
    birth_signs: Dict[str, int],
    get_transit_positions: Callable,
    tz_offset: float = 5.5,
) -> Dict[str, Any]:
    """
    Compute the full monthly Gochara Kaksha grid (like Parashara Light).

    For each day, computes 24-hour kaksha timeline for all 7 planets.
    Returns a compact grid format optimized for visualization.
    """
    from core.utils import datetime_to_jd

    days = []
    current = start_date

    while current <= end_date:
        # Sample at 6 time points per day (every 4 hours) for grid overview
        # This captures major kaksha transitions without excessive data
        day_slices = []
        for hour in [0, 4, 8, 12, 16, 20]:
            dt = datetime(current.year, current.month, current.day, hour, 0, 0)
            utc_dt = dt - timedelta(hours=tz_offset)
            jd = datetime_to_jd(utc_dt)
            transit_data = get_transit_positions(jd)
            day_slices.append((hour, transit_data))

        # Build per-planet info for this day
        planet_day = {}
        for planet in ASHTAK_PLANETS:
            slices = []
            for hour, transit_data in day_slices:
                if planet not in transit_data:
                    continue
                lon, sign_idx = transit_data[planet]
                kaksha_info = calc_kaksha(lon)
                benefic = _is_kaksha_benefic(
                    planet, sign_idx, kaksha_info["kaksha_lord"], birth_signs
                )
                slices.append({
                    "h": hour,
                    "b": benefic,  # compact: benefic bool
                    "k": kaksha_info["kaksha_lord"][:2],  # compact: first 2 chars
                })

            if slices:
                # Noon position for the summary
                noon_data = day_slices[3][1]  # 12:00
                if planet in noon_data:
                    noon_lon, noon_sign = noon_data[planet]
                    noon_kaksha = calc_kaksha(noon_lon)
                    bav = all_bav.get(planet, [0] * 12)[noon_sign]
                    benefic_count = sum(1 for s in slices if s["b"])

                    planet_day[planet] = {
                        "sign": SIGNS[noon_sign],
                        "sign_idx": noon_sign,
                        "bav": bav,
                        "kaksha_lord": noon_kaksha["kaksha_lord"],
                        "benefic_pct": round(benefic_count / len(slices) * 100),
                        "slices": slices,
                    }

        # Compute daily composite score at noon
        noon_transit = day_slices[3][1]
        noon_moment = compute_moment_kaksha(noon_transit, all_bav, sav, birth_signs)

        days.append({
            "date": current.strftime("%d-%m-%Y"),
            "day": current.day,
            "weekday": current.strftime("%A")[:3],
            "score": noon_moment["score"],
            "rating": noon_moment["rating"],
            "planets": planet_day,
        })

        current += timedelta(days=1)

    # Monthly summary
    scores = [d["score"] for d in days]
    avg_score = round(sum(scores) / len(scores), 1) if scores else 0
    best_days = sorted(days, key=lambda d: d["score"], reverse=True)[:5]
    worst_days = sorted(days, key=lambda d: d["score"])[:5]

    rating_counts = {}
    for d in days:
        r = d["rating"]
        rating_counts[r] = rating_counts.get(r, 0) + 1

    return {
        "start": start_date.strftime("%d-%m-%Y"),
        "end": end_date.strftime("%d-%m-%Y"),
        "total_days": len(days),
        "avg_score": avg_score,
        "rating_counts": rating_counts,
        "best_days": [{"date": d["date"], "day": d["day"], "score": d["score"],
                       "rating": d["rating"]} for d in best_days],
        "worst_days": [{"date": d["date"], "day": d["day"], "score": d["score"],
                        "rating": d["rating"]} for d in worst_days],
        "days": days,
    }
