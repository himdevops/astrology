"""
ashtakavarga.py — Ashtakavarga System with Transit Date Predictions
Implements Bhinnashtakavarga (BAV) and Sarvashtakavarga (SAV) for all 7 planets.
Generates transit predictions with exact date ranges for NSE/BSE markets.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

# ─────────────────────────────────────────────────────────────
# Ashtakavarga contribution tables (Parashara rules)
# Format: TABLE[planet_name][contributor] = [house_offsets...]
# house_offset 1 = same sign as contributor, 2 = next sign, etc.
# ─────────────────────────────────────────────────────────────
ASHTAKAVARGA_TABLE: Dict[str, Dict[str, List[int]]] = {
    "Sun": {
        "Sun":     [1, 2, 4, 7, 8, 9, 10, 11],
        "Moon":    [3, 6, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [5, 6, 9, 11],
        "Venus":   [6, 7, 12],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [3, 4, 6, 10, 11, 12],
    },
    "Moon": {
        "Sun":     [3, 6, 7, 8, 10, 11],
        "Moon":    [1, 3, 6, 7, 10, 11],
        "Mars":    [2, 3, 5, 6, 9, 10, 11],
        "Mercury": [1, 3, 4, 5, 7, 8, 10, 11],
        "Jupiter": [1, 4, 7, 8, 10, 11, 12],
        "Venus":   [3, 4, 5, 7, 9, 10, 11],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [3, 6, 10, 11],
    },
    "Mars": {
        "Sun":     [3, 5, 6, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [3, 5, 6, 11],
        "Jupiter": [6, 10, 11, 12],
        "Venus":   [6, 8, 11, 12],
        "Saturn":  [1, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 3, 6, 10, 11],
    },
    "Mercury": {
        "Sun":     [5, 6, 9, 11, 12],
        "Moon":    [2, 4, 6, 8, 10, 11],
        "Mars":    [1, 2, 4, 7, 8, 9, 10, 11],
        "Mercury": [1, 3, 5, 6, 9, 10, 11, 12],
        "Jupiter": [6, 8, 11, 12],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 11],
        "Saturn":  [1, 2, 4, 7, 8, 9, 10, 11],
        "Lagna":   [1, 2, 4, 6, 8, 10, 11],
    },
    "Jupiter": {
        "Sun":     [1, 2, 3, 4, 7, 8, 9, 10, 11],
        "Moon":    [2, 5, 7, 9, 11],
        "Mars":    [1, 2, 4, 7, 8, 10, 11],
        "Mercury": [1, 2, 4, 5, 6, 9, 10, 11],
        "Jupiter": [1, 2, 3, 4, 7, 8, 10, 11],
        "Venus":   [2, 5, 6, 9, 10, 11],
        "Saturn":  [3, 5, 6, 12],
        "Lagna":   [1, 2, 4, 5, 6, 7, 9, 10, 11],
    },
    "Venus": {
        "Sun":     [8, 11, 12],
        "Moon":    [1, 2, 3, 4, 5, 8, 9, 11, 12],
        "Mars":    [3, 4, 6, 9, 11, 12],
        "Mercury": [3, 5, 6, 9, 11],
        "Jupiter": [5, 8, 9, 10, 11],
        "Venus":   [1, 2, 3, 4, 5, 8, 9, 10, 11, 12],
        "Saturn":  [3, 4, 5, 8, 9, 10, 11],
        "Lagna":   [1, 2, 3, 4, 5, 8, 9, 11],
    },
    "Saturn": {
        "Sun":     [1, 2, 4, 7, 8, 10, 11],
        "Moon":    [3, 6, 11],
        "Mars":    [3, 5, 6, 10, 11, 12],
        "Mercury": [6, 8, 9, 10, 11, 12],
        "Jupiter": [5, 6, 11, 12],
        "Venus":   [6, 11, 12],
        "Saturn":  [3, 5, 6, 11],
        "Lagna":   [1, 3, 4, 6, 10, 11],
    },
}

PLANETS_FOR_BAV = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# Transit average speeds (degrees/day)
PLANET_SPEED = {
    "Sun":     1.0,
    "Moon":    13.2,
    "Mars":    0.524,
    "Mercury": 1.2,   # avg (goes retrograde)
    "Jupiter": 0.083,
    "Venus":   1.2,
    "Saturn":  0.034,
    "Rahu":   -0.053,
    "Ketu":   -0.053,
}

# NSE/BSE market signal thresholds
BAV_THRESHOLDS = {
    "very_strong": 6,   # ≥6 points: highly favorable transit
    "strong":      5,   # 5 points: favorable
    "moderate":    4,   # 4 points: neutral
    "weak":        3,   # 3 points: unfavorable
    "very_weak":   2,   # ≤2 points: highly unfavorable
}


def _sign_idx(longitude: float) -> int:
    return int((longitude % 360.0) / 30)


def calc_bhinnashtakavarga(
    planet_name: str,
    planets: List[Dict],
    ascendant_long: float,
) -> Dict:
    """
    Calculate Bhinnashtakavarga (BAV) for one planet.
    Returns scores for all 12 signs (0–8 points each).
    """
    table = ASHTAKAVARGA_TABLE.get(planet_name)
    if not table:
        return {}

    scores = [0] * 12  # one score per sign

    # Build contributor sign map
    contrib_signs: Dict[str, int] = {}
    for p in planets:
        if p["planet"] in PLANETS_FOR_BAV:
            contrib_signs[p["planet"]] = _sign_idx(p["longitude"])
    contrib_signs["Lagna"] = _sign_idx(ascendant_long)

    for contributor, offsets in table.items():
        contrib_sign = contrib_signs.get(contributor)
        if contrib_sign is None:
            continue
        for h in offsets:
            target_sign = (contrib_sign + h - 1) % 12
            scores[target_sign] += 1

    return {
        "planet": planet_name,
        "scores": {SIGNS[i]: scores[i] for i in range(12)},
        "total": sum(scores),
        "max_possible": 8,
        "sign_signals": {
            SIGNS[i]: _score_to_signal(scores[i]) for i in range(12)
        },
    }


def calc_sarvashtakavarga(
    planets: List[Dict],
    ascendant_long: float,
) -> Dict:
    """
    Sarvashtakavarga (SAV) = sum of all 7 planets' BAV scores per sign.
    Maximum = 56 points per sign. Normal average = 28.
    """
    sav = [0] * 12
    all_bav: Dict[str, Dict] = {}

    for planet_name in PLANETS_FOR_BAV:
        planet = next((p for p in planets if p["planet"] == planet_name), None)
        if planet is None:
            continue
        bav = calc_bhinnashtakavarga(planet_name, planets, ascendant_long)
        all_bav[planet_name] = bav
        for i, sign in enumerate(SIGNS):
            sav[i] += bav["scores"].get(sign, 0)

    sav_dict = {SIGNS[i]: sav[i] for i in range(12)}
    sav_signals = {SIGNS[i]: _sav_signal(sav[i]) for i in range(12)}

    return {
        "sarvashtakavarga": sav_dict,
        "sav_signals":      sav_signals,
        "total_sav":        sum(sav),
        "max_possible":     56,
        "average":          round(sum(sav) / 12, 2),
        "strongest_sign":   max(sav_dict, key=lambda k: sav_dict[k]),
        "weakest_sign":     min(sav_dict, key=lambda k: sav_dict[k]),
        "bhinnashtakavarga": all_bav,
    }


def _score_to_signal(score: int) -> str:
    if score >= BAV_THRESHOLDS["very_strong"]:
        return "VERY STRONG — Excellent transit"
    if score >= BAV_THRESHOLDS["strong"]:
        return "STRONG — Favorable transit"
    if score >= BAV_THRESHOLDS["moderate"]:
        return "MODERATE — Neutral transit"
    if score >= BAV_THRESHOLDS["weak"]:
        return "WEAK — Unfavorable transit"
    return "VERY WEAK — Avoid this sign transit"


def _sav_signal(score: int) -> str:
    if score >= 30:
        return "BULLISH"
    if score >= 25:
        return "MILDLY BULLISH"
    if score >= 20:
        return "NEUTRAL"
    if score >= 15:
        return "MILDLY BEARISH"
    return "BEARISH"


# ─────────────────────────────────────────────────────────────
# Transit Date Prediction Engine
# ─────────────────────────────────────────────────────────────

def calc_transit_dates_with_ashtakavarga(
    planets: List[Dict],
    ascendant_long: float,
    ayanamsa_key: str = "lahiri",
    from_date: Optional[datetime] = None,
    days_ahead: int = 180,
) -> Dict:
    """
    Calculate upcoming planetary transits with Ashtakavarga scores.
    For each planet, find when it enters a new sign and what the BAV score is.
    Generates NSE/BSE market impact predictions with exact dates.
    """
    if from_date is None:
        from_date = datetime.utcnow()

    # Pre-calculate BAV for all planets
    sav_data = calc_sarvashtakavarga(planets, ascendant_long)
    all_bav = sav_data["bhinnashtakavarga"]

    transit_alerts: List[Dict] = []

    ayanamsa_map = {
        "lahiri": swe.SIDM_LAHIRI,
        "raman": swe.SIDM_RAMAN,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
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

    for planet_name, planet_id in planet_ids.items():
        bav = all_bav.get(planet_name, {})
        if not bav:
            continue

        sign_entries = _find_sign_ingresses(
            planet_id, planet_name, from_date, days_ahead, flags
        )

        for entry in sign_entries:
            sign = entry["sign"]
            bav_score = bav.get("scores", {}).get(sign, 0)
            sav_score = sav_data["sarvashtakavarga"].get(sign, 0)
            signal = _score_to_signal(bav_score)
            market_impact = _market_impact(planet_name, sign, bav_score, sav_score)

            transit_alerts.append({
                "planet":           planet_name,
                "entering_sign":    sign,
                "exit_sign":        entry.get("prev_sign", ""),
                "ingress_date":     entry["date"],
                "ingress_datetime": entry["datetime"],
                "retrograde":       entry.get("retrograde", False),
                "bav_score":        bav_score,
                "sav_score":        sav_score,
                "bav_signal":       signal,
                "sav_signal":       _sav_signal(sav_score),
                "market_impact":    market_impact,
                "nse_action":       market_impact["action"],
                "duration_days":    entry.get("duration_days", 0),
                "exit_date":        entry.get("exit_date", ""),
            })

    # Sort by date
    transit_alerts.sort(key=lambda x: x["ingress_date"])

    return {
        "generated_for_date": from_date.strftime("%Y-%m-%d"),
        "days_ahead":         days_ahead,
        "total_alerts":       len(transit_alerts),
        "sarvashtakavarga":   sav_data["sarvashtakavarga"],
        "sav_signals":        sav_data["sav_signals"],
        "transit_alerts":     transit_alerts,
        "summary":            _transit_summary(transit_alerts),
    }


def _find_sign_ingresses(
    planet_id: int,
    planet_name: str,
    from_date: datetime,
    days_ahead: int,
    flags: int,
    step_days: float = 0.5,
) -> List[Dict]:
    """Scan forward to find all sign ingresses for a planet."""
    ingresses: List[Dict] = []

    jd_start = swe.julday(
        from_date.year, from_date.month, from_date.day,
        from_date.hour + from_date.minute / 60.0
    )

    result = swe.calc_ut(jd_start, planet_id, flags)
    prev_sign = int(result[0][0] / 30) % 12
    prev_long = result[0][0]
    jd_current = jd_start

    jd_end = jd_start + days_ahead

    while jd_current < jd_end:
        jd_current += step_days
        result = swe.calc_ut(jd_current, planet_id, flags)
        long = result[0][0] % 360.0
        speed = result[0][3]
        current_sign = int(long / 30)

        if current_sign != prev_sign:
            # Binary search for precise ingress time
            precise_jd = _binary_search_ingress(
                planet_id, flags, jd_current - step_days, jd_current, prev_sign
            )
            dt = _jd_to_datetime(precise_jd)

            # Find exit date (next ingress)
            exit_jd = _find_next_ingress(planet_id, flags, precise_jd, current_sign, days_ahead)
            exit_dt = _jd_to_datetime(exit_jd) if exit_jd else None
            duration = int(exit_jd - precise_jd) if exit_jd else 0

            ingresses.append({
                "sign":         SIGNS[current_sign],
                "prev_sign":    SIGNS[prev_sign],
                "date":         dt.strftime("%Y-%m-%d"),
                "datetime":     dt.strftime("%Y-%m-%d %H:%M"),
                "retrograde":   speed < 0,
                "jd":           precise_jd,
                "exit_date":    exit_dt.strftime("%Y-%m-%d") if exit_dt else "",
                "duration_days": duration,
            })
            prev_sign = current_sign

        prev_long = long

    return ingresses


def _binary_search_ingress(planet_id, flags, jd_low, jd_high, prev_sign, iterations=20):
    """Binary search for precise sign ingress time."""
    for _ in range(iterations):
        jd_mid = (jd_low + jd_high) / 2
        r = swe.calc_ut(jd_mid, planet_id, flags)
        mid_sign = int(r[0][0] / 30) % 12
        if mid_sign == prev_sign:
            jd_low = jd_mid
        else:
            jd_high = jd_mid
    return (jd_low + jd_high) / 2


def _find_next_ingress(planet_id, flags, from_jd, current_sign, max_days):
    """Find when planet leaves the current sign."""
    jd = from_jd + 0.5
    end_jd = from_jd + max_days
    while jd < end_jd:
        r = swe.calc_ut(jd, planet_id, flags)
        sign = int(r[0][0] / 30) % 12
        if sign != current_sign:
            return _binary_search_ingress(planet_id, flags, jd - 0.5, jd, current_sign)
        jd += 0.5
    return None


def _jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to datetime."""
    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    try:
        return datetime(y, m, d, hour, minute)
    except (ValueError, OverflowError):
        return datetime(2000, 1, 1)


def _market_impact(planet: str, sign: str, bav: int, sav: int) -> Dict:
    """Generate NSE/BSE market impact for a transit."""
    # Planetary financial weight
    bullish_planets  = {"Jupiter", "Venus", "Moon"}
    bearish_planets  = {"Saturn", "Mars", "Rahu", "Ketu"}
    neutral_planets  = {"Sun", "Mercury"}

    planet_bias = 1 if planet in bullish_planets else -1 if planet in bearish_planets else 0

    # Combined signal
    if bav >= 5 and sav >= 28 and planet_bias >= 0:
        action = "STRONG BUY — Highly favorable transit"
        score = 0.8
        color = "#00C851"
    elif bav >= 5 and planet_bias >= 0:
        action = "BUY — Favorable transit"
        score = 0.6
        color = "#4CAF50"
    elif bav <= 2 and planet_bias <= 0:
        action = "SELL/HEDGE — Very unfavorable transit"
        score = -0.8
        color = "#FF3D00"
    elif bav <= 2:
        action = "CAUTION — Unfavorable transit"
        score = -0.5
        color = "#FF6D00"
    elif bav >= 4 and planet_bias >= 0:
        action = "HOLD/ACCUMULATE"
        score = 0.3
        color = "#8BC34A"
    else:
        action = "NEUTRAL"
        score = 0.0
        color = "#9E9E9E"

    # Specific sector impacts
    sector_map = {
        "Jupiter": ["Banking", "Finance", "Education", "Pharma"],
        "Venus":   ["FMCG", "Auto", "Entertainment", "Luxury"],
        "Saturn":  ["Oil & Gas", "Mining", "Infrastructure", "Iron"],
        "Mars":    ["Defense", "Real Estate", "Steel", "Energy"],
        "Mercury": ["IT", "Telecom", "Media", "Trading"],
        "Moon":    ["FMCG", "Real Estate", "Consumer Goods"],
        "Sun":     ["PSU", "Power", "Government Infra"],
        "Rahu":    ["Tech", "Chemicals", "Aviation"],
        "Ketu":    ["Pharma", "Mystical sectors"],
    }

    return {
        "action":           action,
        "score":            score,
        "color":            color,
        "sectors_impacted": sector_map.get(planet, []),
        "bav_score":        bav,
        "sav_score":        sav,
    }


def _transit_summary(alerts: List[Dict]) -> Dict:
    """Generate overall market summary from transit alerts."""
    if not alerts:
        return {}
    bullish = [a for a in alerts if a["market_impact"]["score"] > 0.3]
    bearish = [a for a in alerts if a["market_impact"]["score"] < -0.3]
    avg_score = sum(a["market_impact"]["score"] for a in alerts) / len(alerts)

    if avg_score > 0.3:
        outlook = "BULLISH PERIOD"
        recommendation = "Increase equity exposure; favor growth sectors"
    elif avg_score > 0:
        outlook = "MILDLY BULLISH"
        recommendation = "Selective buying; focus on strong BAV transits"
    elif avg_score > -0.3:
        outlook = "CAUTIOUS"
        recommendation = "Hold existing positions; avoid new high-risk entries"
    else:
        outlook = "BEARISH PERIOD"
        recommendation = "Reduce equity; increase Gold/Bonds/Cash"

    return {
        "overall_outlook":     outlook,
        "avg_transit_score":   round(avg_score, 3),
        "bullish_transits":    len(bullish),
        "bearish_transits":    len(bearish),
        "recommendation":      recommendation,
        "next_key_transit":    alerts[0]["planet"] + " → " + alerts[0]["entering_sign"] + " on " + alerts[0]["ingress_date"] if alerts else "",
    }
