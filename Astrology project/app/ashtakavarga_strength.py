"""
ashtakavarga_strength.py — Daily/Monthly/Yearly Ashtakavarga Strength Calendar
Parashara Light-style strength tracker showing which planets are strong each period.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from app.ashtakavarga import (
    ASHTAKAVARGA_TABLE,
    PLANETS_FOR_BAV,
    SIGNS,
    calc_bhinnashtakavarga,
    calc_sarvashtakavarga,
    _score_to_signal,
)
from app.core import normalize_degree


def get_natal_planet_good_signs(
    planet_name: str,
    planets: List[Dict],
    ascendant_long: float,
) -> Dict[str, bool]:
    """
    For a natal planet, determine which signs are 'good' for it.
    A sign is good if the planet's BAV score in that sign is ≥5 (strong).
    """
    bav = calc_bhinnashtakavarga(planet_name, planets, ascendant_long)
    scores = bav.get("scores", {})
    
    return {
        sign: (scores.get(sign, 0) >= 5)
        for sign in SIGNS
    }


def calc_daily_strength(
    from_date: datetime,
    days: int,
    planets: List[Dict],
    ascendant_long: float,
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Calculate daily Ashtakavarga strength for each day.
    Shows which planets are strong (BAV ≥5) and their sign positions.
    Returns a calendar grid with daily strength ratings.
    """
    ayanamsa_map = {
        "lahiri":         swe.SIDM_LAHIRI,
        "raman":          swe.SIDM_RAMAN,
        "krishnamurti":   swe.SIDM_KRISHNAMURTI,
        "fagan_bradley":  swe.SIDM_FAGAN_BRADLEY,
    }
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key.lower(), swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    planet_ids = {
        "Sun":     swe.SUN,
        "Moon":    swe.MOON,
        "Mars":    swe.MARS,
        "Mercury": swe.MERCURY,
        "Jupiter": swe.JUPITER,
        "Venus":   swe.VENUS,
        "Saturn":  swe.SATURN,
    }

    # Pre-calculate natal good signs for each planet
    natal_good_signs = {
        pname: get_natal_planet_good_signs(pname, planets, ascendant_long)
        for pname in PLANETS_FOR_BAV
    }

    daily_data: List[Dict] = []
    
    for day_offset in range(days):
        current_date = from_date + timedelta(days=day_offset)
        jd = swe.julday(
            current_date.year, current_date.month, current_date.day,
            current_date.hour + current_date.minute / 60.0
        )

        # Calculate SAV for this day
        transit_planets = []
        for pname, pid in planet_ids.items():
            result = swe.calc_ut(jd, pid, flags)
            long = normalize_degree(result[0][0])
            speed = result[0][3]
            sign_idx = int(long / 30)
            sign = SIGNS[sign_idx]
            transit_planets.append({
                "planet": pname,
                "longitude": long,
                "sign": sign,
                "speed": speed,
                "retrograde": speed < 0,
            })

        sav = calc_sarvashtakavarga(transit_planets, ascendant_long)
        
        # Calculate strength for each planet
        planet_strengths: List[Dict] = []
        good_count = 0
        moderate_count = 0
        weak_count = 0

        for tp in transit_planets:
            pname = tp["planet"]
            sign = tp["sign"]
            bav = calc_bhinnashtakavarga(pname, transit_planets, ascendant_long)
            score = bav["scores"].get(sign, 0)
            is_natal_good = natal_good_signs.get(pname, {}).get(sign, False)
            
            if score >= 5:
                status = "STRONG"
                good_count += 1
            elif score >= 3:
                status = "MODERATE"
                moderate_count += 1
            else:
                status = "WEAK"
                weak_count += 1

            planet_strengths.append({
                "planet": pname,
                "sign": sign,
                "bav_score": score,
                "status": status,
                "retrograde": tp["retrograde"],
                "natal_good_sign": is_natal_good,
                "benefit": "HIGHLY BENEFICIAL" if (score >= 5 and is_natal_good) else
                           "BENEFICIAL" if (score >= 5 or is_natal_good) else
                           "NEUTRAL",
            })

        # Overall daily strength
        avg_sav = sav["average"]
        overall_strength = (
            "VERY STRONG" if avg_sav >= 32 else
            "STRONG" if avg_sav >= 28 else
            "MODERATE" if avg_sav >= 24 else
            "WEAK" if avg_sav >= 20 else
            "VERY WEAK"
        )

        daily_data.append({
            "date": current_date.strftime("%Y-%m-%d"),
            "day_of_week": current_date.strftime("%A"),
            "overall_strength": overall_strength,
            "avg_sav": round(avg_sav, 2),
            "strong_planets": good_count,
            "moderate_planets": moderate_count,
            "weak_planets": weak_count,
            "planet_strengths": planet_strengths,
            "strongest_planet": max(
                planet_strengths, key=lambda x: x["bav_score"]
            )["planet"] if planet_strengths else "",
            "recommendation": _daily_recommendation(good_count, weak_count, avg_sav),
        })

    return {
        "generated_date": datetime.utcnow().strftime("%Y-%m-%d"),
        "from_date": from_date.strftime("%Y-%m-%d"),
        "to_date": (from_date + timedelta(days=days-1)).strftime("%Y-%m-%d"),
        "total_days": days,
        "daily_data": daily_data,
        "strongest_days": sorted(
            daily_data,
            key=lambda x: (x["strong_planets"], x["avg_sav"]),
            reverse=True
        )[:7],
        "weakest_days": sorted(
            daily_data,
            key=lambda x: (x["strong_planets"], x["avg_sav"]),
        )[:7],
        "summary": _calendar_summary(daily_data),
    }


def calc_monthly_strength(
    year: int,
    month: int,
    planets: List[Dict],
    ascendant_long: float,
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Calculate monthly Ashtakavarga strength.
    Shows average strength for each day of the month.
    """
    import calendar
    
    days_in_month = calendar.monthrange(year, month)[1]
    from_date = datetime(year, month, 1)
    
    daily_strength = calc_daily_strength(
        from_date, days_in_month, planets, ascendant_long, ayanamsa_key
    )

    # Group by week
    weekly_data = []
    for week_num in range((days_in_month + 6) // 7):
        week_days = daily_strength["daily_data"][week_num * 7:(week_num + 1) * 7]
        if week_days:
            avg_sav = sum(d["avg_sav"] for d in week_days) / len(week_days)
            avg_strong = sum(d["strong_planets"] for d in week_days) / len(week_days)
            weekly_data.append({
                "week_number": week_num + 1,
                "avg_sav": round(avg_sav, 2),
                "avg_strong_planets": round(avg_strong, 1),
                "days": week_days,
            })

    return {
        "month": f"{calendar.month_name[month]} {year}",
        "days_in_month": days_in_month,
        "daily_data": daily_strength["daily_data"],
        "weekly_data": weekly_data,
        "strongest_day": max(
            daily_strength["daily_data"],
            key=lambda x: (x["strong_planets"], x["avg_sav"])
        )["date"],
        "weakest_day": min(
            daily_strength["daily_data"],
            key=lambda x: (x["strong_planets"], x["avg_sav"])
        )["date"],
        "avg_monthly_sav": round(
            sum(d["avg_sav"] for d in daily_strength["daily_data"]) / 
            len(daily_strength["daily_data"]), 2
        ),
        "month_strength": _monthly_rating(
            sum(d["avg_sav"] for d in daily_strength["daily_data"]) / 
            len(daily_strength["daily_data"])
        ),
    }


def calc_yearly_strength(
    year: int,
    planets: List[Dict],
    ascendant_long: float,
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Calculate yearly Ashtakavarga strength.
    Shows average strength for each month.
    """
    import calendar

    monthly_data = []
    
    for month in range(1, 13):
        monthly = calc_monthly_strength(year, month, planets, ascendant_long, ayanamsa_key)
        monthly_data.append({
            "month": calendar.month_name[month],
            "avg_sav": monthly["avg_monthly_sav"],
            "strength": monthly["month_strength"],
            "strongest_day": monthly["strongest_day"],
            "weakest_day": monthly["weakest_day"],
        })

    avg_yearly = sum(m["avg_sav"] for m in monthly_data) / 12
    
    return {
        "year": year,
        "monthly_data": monthly_data,
        "avg_yearly_sav": round(avg_yearly, 2),
        "yearly_strength": _monthly_rating(avg_yearly),
        "strongest_month": max(monthly_data, key=lambda x: x["avg_sav"])["month"],
        "weakest_month": min(monthly_data, key=lambda x: x["avg_sav"])["month"],
    }


def _daily_recommendation(strong: int, weak: int, avg_sav: float) -> str:
    """Generate daily recommendation based on strength."""
    if avg_sav >= 32 and strong >= 5:
        return "🟢 EXCELLENT — Initiate new ventures, major decisions, trading"
    elif avg_sav >= 28 and strong >= 4:
        return "🟢 GOOD — Favorable for most activities, buying, investments"
    elif avg_sav >= 24 and strong >= 3:
        return "🟡 NEUTRAL — Routine work OK, avoid major decisions"
    elif avg_sav >= 20:
        return "🟡 CAUTION — Hold; avoid initiations, risky trades"
    else:
        return "🔴 UNFAVORABLE — Avoid important events, max protection"


def _monthly_rating(avg_sav: float) -> str:
    if avg_sav >= 30:
        return "EXCELLENT"
    elif avg_sav >= 28:
        return "GOOD"
    elif avg_sav >= 24:
        return "MODERATE"
    elif avg_sav >= 20:
        return "WEAK"
    else:
        return "VERY WEAK"


def _calendar_summary(daily_data: List[Dict]) -> Dict:
    """Generate summary stats for the calendar period."""
    if not daily_data:
        return {}
    
    very_strong = sum(1 for d in daily_data if d["overall_strength"] == "VERY STRONG")
    strong = sum(1 for d in daily_data if d["overall_strength"] == "STRONG")
    moderate = sum(1 for d in daily_data if d["overall_strength"] == "MODERATE")
    weak = sum(1 for d in daily_data if d["overall_strength"] == "WEAK")
    very_weak = sum(1 for d in daily_data if d["overall_strength"] == "VERY WEAK")
    
    return {
        "total_days": len(daily_data),
        "very_strong_days": very_strong,
        "strong_days": strong,
        "moderate_days": moderate,
        "weak_days": weak,
        "very_weak_days": very_weak,
        "favorable_percentage": round(
            ((very_strong + strong) / len(daily_data)) * 100, 1
        ) if daily_data else 0,
        "best_window": f"{daily_data[0]['date']}" if daily_data else "",
        "avg_sav": round(sum(d["avg_sav"] for d in daily_data) / len(daily_data), 2) if daily_data else 0,
    }
