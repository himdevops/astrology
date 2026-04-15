"""
prediction_engine.py — Autonomous NSE/BSE Market Prediction Engine
Combines all astrology signals (Dasha, Nakshatra, Yogas, Transits, Ashtakavarga)
into a unified prediction with confidence score and sector recommendations.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.nakshatra import get_nakshatra, get_moon_nakshatra_signal
from app.dasha import DASHA_FINANCIAL
from app.yoga_detector import detect_all_yogas

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

# ─────────────────────────────────────────────────────────────
# Planetary weights for NSE/BSE market prediction
# ─────────────────────────────────────────────────────────────
PLANET_WEIGHTS = {
    "Jupiter": 0.25,   # Most important — market expansion/contraction
    "Saturn":  0.20,   # Long-term structural trend
    "Moon":    0.15,   # Sentiment + liquidity (daily)
    "Mars":    0.12,   # Market energy, momentum
    "Venus":   0.12,   # Consumer + liquidity
    "Mercury": 0.08,   # Trading activity, IT
    "Sun":     0.08,   # Government, authority
}

# Sign financial scores for quick lookup
SIGN_SCORES = {
    "Aries":       0.60, "Taurus":      0.80, "Gemini":      0.50,
    "Cancer":      0.55, "Leo":         0.65, "Virgo":       0.45,
    "Libra":       0.60, "Scorpio":     0.40, "Sagittarius": 0.70,
    "Capricorn":   0.50, "Aquarius":    0.55, "Pisces":      0.60,
}

# Planet-sign financial impact (overrides generic sign score when specific)
PLANET_SIGN_SCORES = {
    "Jupiter": {
        "Cancer":      +1.0, "Sagittarius": +0.85, "Pisces": +0.85,
        "Aries":       +0.70, "Taurus": +0.90, "Gemini": +0.50,
        "Leo": +0.60, "Virgo": -0.20, "Libra": +0.65,
        "Scorpio": +0.45, "Capricorn": -0.30, "Aquarius": +0.55,
    },
    "Saturn": {
        "Libra":       +0.40, "Capricorn": +0.50, "Aquarius": +0.45,
        "Aries":       -0.40, "Cancer": -0.35, "Leo": -0.50,
        "Taurus": -0.10, "Gemini": -0.20, "Virgo": +0.20,
        "Scorpio": -0.30, "Sagittarius": -0.20, "Pisces": -0.15,
    },
    "Mars": {
        "Capricorn":   +0.80, "Aries": +0.70, "Scorpio": +0.65,
        "Cancer":      -0.50, "Taurus": +0.30, "Gemini": +0.20,
        "Leo": +0.55, "Virgo": +0.25, "Libra": -0.10,
        "Sagittarius": +0.40, "Aquarius": +0.20, "Pisces": -0.20,
    },
    "Venus": {
        "Pisces":      +0.90, "Taurus": +0.80, "Libra": +0.85,
        "Virgo":       -0.30, "Aries": +0.50, "Gemini": +0.55,
        "Cancer": +0.60, "Leo": +0.45, "Scorpio": -0.10,
        "Sagittarius": +0.50, "Capricorn": +0.40, "Aquarius": +0.55,
    },
    "Mercury": {
        "Virgo":       +0.90, "Gemini": +0.85, "Aquarius": +0.70,
        "Pisces":      -0.30, "Sagittarius": -0.25, "Cancer": -0.10,
        "Aries": +0.40, "Taurus": +0.55, "Leo": +0.50,
        "Libra": +0.60, "Scorpio": +0.30, "Capricorn": +0.45,
    },
}

# Dasha lord weights
DASHA_WEIGHT = 0.20   # 20% weight for dasha lord
ANTARDASHA_WEIGHT = 0.10  # 10% for antardasha

# Nakshatra Moon signal weight
NAKSHATRA_WEIGHT = 0.15

# Yoga weight
YOGA_WEIGHT = 0.15

# Transit weight (remaining)
TRANSIT_WEIGHT = 0.20


def generate_market_prediction(
    current_planets: List[Dict],
    current_date: Optional[datetime] = None,
    current_dasha: Optional[Dict] = None,
    yoga_data: Optional[Dict] = None,
    transit_data: Optional[Dict] = None,
    natal_chart: Optional[Dict] = None,
) -> Dict:
    """
    Generate autonomous NSE/BSE market prediction.

    Inputs:
    - current_planets: List of current planetary positions (transits)
    - current_date: Date for prediction (default today)
    - current_dasha: Active dasha data for the natal chart
    - yoga_data: Yoga detection results from natal chart
    - transit_data: Transit alerts data
    - natal_chart: Full natal chart data

    Returns:
    - Comprehensive market prediction with confidence, sectors, and reasoning
    """
    if current_date is None:
        current_date = datetime.utcnow()

    # ── 1. Planetary Position Score (weighted) ──────────────
    planet_score, planet_breakdown = _calc_planet_score(current_planets)

    # ── 2. Moon Nakshatra Signal ────────────────────────────
    moon_planet = next((p for p in current_planets if p["planet"] == "Moon"), None)
    moon_nakshatra_signal = {}
    nakshatra_score = 0.0
    if moon_planet:
        moon_nakshatra_signal = get_moon_nakshatra_signal(moon_planet["longitude"])
        nakshatra_score = moon_nakshatra_signal.get("financial_score", 0.0)

    # ── 3. Dasha Score ──────────────────────────────────────
    dasha_score = 0.0
    dasha_info = {}
    if current_dasha:
        maha_lord = current_dasha.get("mahadasha")
        antar_lord = current_dasha.get("antardasha")
        maha_score = DASHA_FINANCIAL.get(maha_lord, {}).get("score", 0.0) if maha_lord else 0.0
        antar_score = DASHA_FINANCIAL.get(antar_lord, {}).get("score", 0.0) if antar_lord else 0.0
        dasha_score = maha_score * 0.65 + antar_score * 0.35
        dasha_info = {
            "mahadasha":   maha_lord,
            "antardasha":  antar_lord,
            "maha_score":  maha_score,
            "antar_score": antar_score,
            "combined":    round(dasha_score, 3),
        }

    # ── 4. Yoga Score ───────────────────────────────────────
    yoga_score = yoga_data.get("overall_yoga_score", 0.0) if yoga_data else 0.0

    # ── 5. Transit Alert Score ──────────────────────────────
    transit_score = transit_data.get("market_score", 0.0) if transit_data else 0.0

    # ── 6. Combined Weighted Score ──────────────────────────
    if current_dasha:
        final_score = (
            planet_score   * 0.30 +
            nakshatra_score * NAKSHATRA_WEIGHT +
            dasha_score    * DASHA_WEIGHT +
            yoga_score     * YOGA_WEIGHT +
            transit_score  * TRANSIT_WEIGHT
        )
    else:
        # Without natal chart — use transits only
        final_score = (
            planet_score    * 0.50 +
            nakshatra_score * 0.25 +
            transit_score   * 0.25
        )

    final_score = max(-1.0, min(1.0, final_score))

    # ── 7. Prediction Output ────────────────────────────────
    prediction = _score_to_prediction(final_score)

    # ── 8. Sector Recommendations ──────────────────────────
    sectors = _generate_sector_recommendations(
        current_planets, yoga_data, transit_data, final_score
    )

    # ── 9. Weekly Outlook (next 7 days) ────────────────────
    weekly = _weekly_moon_outlook(current_planets, current_date)

    # ── 10. Key Upcoming Events ─────────────────────────────
    key_events = _extract_key_events(transit_data)

    return {
        "prediction_date":    current_date.strftime("%Y-%m-%d"),
        "prediction_time":    current_date.strftime("%H:%M UTC"),
        "market":             "NSE/BSE",
        "index":              "NIFTY 50 / SENSEX",
        "overall_score":      round(final_score, 4),
        "confidence":         _calc_confidence(planet_score, dasha_score, yoga_score, transit_score),
        "prediction":         prediction,
        "score_breakdown": {
            "planetary_position_score": round(planet_score, 4),
            "moon_nakshatra_score":     round(nakshatra_score, 4),
            "dasha_score":              round(dasha_score, 4),
            "yoga_score":               round(yoga_score, 4),
            "transit_score":            round(transit_score, 4),
            "final_weighted_score":     round(final_score, 4),
        },
        "planetary_breakdown":  planet_breakdown,
        "moon_signal":          moon_nakshatra_signal,
        "dasha_context":        dasha_info,
        "sector_recommendations": sectors,
        "weekly_outlook":       weekly,
        "key_events":           key_events,
        "risk_factors":         _identify_risks(current_planets, transit_data),
        "methodology": (
            "Prediction combines: (1) Current planetary sign positions weighted by market influence, "
            "(2) Moon nakshatra daily signal, (3) Vimshottari Dasha period financial character, "
            "(4) Active yoga combinations, (5) Ashtakavarga transit scores. "
            "Based on classical Parashara and BPHS principles applied to NSE/BSE."
        ),
    }


def _calc_planet_score(planets: List[Dict]) -> tuple:
    """Calculate weighted planetary position score."""
    total_score = 0.0
    total_weight = 0.0
    breakdown = []

    for planet_name, weight in PLANET_WEIGHTS.items():
        planet = next((p for p in planets if p["planet"] == planet_name), None)
        if not planet:
            continue

        sign = planet["sign"]
        # Use specific planet-sign score if available, else generic sign score
        specific = PLANET_SIGN_SCORES.get(planet_name, {})
        score = specific.get(sign, SIGN_SCORES.get(sign, 0.5))

        # Retrograde adjustment
        if planet.get("retrograde"):
            score *= 0.7  # Reduce score for retrograde

        total_score += score * weight
        total_weight += weight
        breakdown.append({
            "planet":     planet_name,
            "sign":       sign,
            "retrograde": planet.get("retrograde", False),
            "score":      round(score, 3),
            "weight":     weight,
            "contribution": round(score * weight, 4),
        })

    final = total_score / total_weight if total_weight > 0 else 0.5
    return round(final, 4), sorted(breakdown, key=lambda x: -x["weight"])


def _score_to_prediction(score: float) -> Dict:
    """Convert final score to actionable prediction."""
    if score >= 0.65:
        return {
            "signal":       "STRONG BUY",
            "direction":    "BULLISH",
            "color":        "#00C851",
            "emoji":        "🚀",
            "nifty_bias":   "Expect 1–3% upside. Buy quality on dips.",
            "strategy":     "Aggressive: Increase equity allocation to 80%+. Focus on growth sectors.",
            "stop_loss":    "Trail stop-loss at 52-week highs. Don't overtrade.",
        }
    if score >= 0.40:
        return {
            "signal":       "BUY",
            "direction":    "BULLISH",
            "color":        "#4CAF50",
            "emoji":        "📈",
            "nifty_bias":   "Positive trend. Buy on dips near support.",
            "strategy":     "Moderate: 60–70% equity. Sector rotation active.",
            "stop_loss":    "Stop-loss at 5% below entry.",
        }
    if score >= 0.15:
        return {
            "signal":       "MILD BUY / ACCUMULATE",
            "direction":    "MILDLY BULLISH",
            "color":        "#8BC34A",
            "emoji":        "📊",
            "nifty_bias":   "Sideways to slightly up. Selective buying.",
            "strategy":     "Conservative: 50% equity. SIP approach recommended.",
            "stop_loss":    "Tight stop-loss 3% below entry.",
        }
    if score >= -0.15:
        return {
            "signal":       "HOLD / NEUTRAL",
            "direction":    "NEUTRAL",
            "color":        "#FFC107",
            "emoji":        "⚖️",
            "nifty_bias":   "Consolidation phase. No clear direction.",
            "strategy":     "Hold existing positions. No new large entries.",
            "stop_loss":    "Move to cash on breakdown below support.",
        }
    if score >= -0.40:
        return {
            "signal":       "SELL / REDUCE",
            "direction":    "BEARISH",
            "color":        "#FF9800",
            "emoji":        "📉",
            "nifty_bias":   "Correction likely 2–5%. Book profits on rallies.",
            "strategy":     "Defensive: Reduce to 40% equity. Increase Gold/Bonds.",
            "stop_loss":    "Hard stop-loss on existing positions.",
        }
    return {
        "signal":       "STRONG SELL",
        "direction":    "STRONGLY BEARISH",
        "color":        "#FF3D00",
        "emoji":        "🔻",
        "nifty_bias":   "Significant correction 5%+ risk. Exit non-core positions.",
        "strategy":     "Capital preservation: 20% equity max. Gold + Cash + Bonds.",
        "stop_loss":    "Exit on any bounce. Don't catch falling knife.",
    }


def _calc_confidence(p: float, d: float, y: float, t: float) -> Dict:
    """Calculate prediction confidence level."""
    # Confidence based on signal alignment
    scores = [p, d, y, t]
    non_zero = [s for s in scores if abs(s) > 0.05]
    if not non_zero:
        return {"level": "LOW", "percent": 40, "note": "Insufficient data for high confidence"}

    avg = sum(non_zero) / len(non_zero)
    # Variance measures disagreement
    variance = sum((s - avg) ** 2 for s in non_zero) / len(non_zero)

    if variance < 0.02 and len(non_zero) >= 3:
        return {"level": "HIGH", "percent": 85,
                "note": "Strong signal alignment across multiple factors"}
    if variance < 0.05 and len(non_zero) >= 2:
        return {"level": "MODERATE", "percent": 65,
                "note": "Mostly aligned signals with minor divergence"}
    return {"level": "LOW", "percent": 45,
            "note": "Mixed signals — trade with caution and strict stop-loss"}


def _generate_sector_recommendations(
    planets: List[Dict],
    yoga_data: Optional[Dict],
    transit_data: Optional[Dict],
    overall_score: float,
) -> Dict:
    """Generate specific NSE/BSE sector recommendations."""
    buy_sectors = set()
    avoid_sectors = set()
    hold_sectors = set()

    # From planet positions
    sector_map = {
        ("Jupiter", ["Cancer", "Sagittarius", "Pisces", "Taurus"]): ["Banking", "Finance", "Gold"],
        ("Venus",   ["Taurus", "Libra", "Pisces"]): ["FMCG", "Auto", "Luxury", "Real Estate"],
        ("Saturn",  ["Capricorn", "Aquarius", "Libra"]): ["Oil & Gas", "Mining", "Infrastructure"],
        ("Mars",    ["Aries", "Scorpio", "Capricorn"]): ["Defense", "Steel", "Energy"],
        ("Mercury", ["Gemini", "Virgo", "Aquarius"]): ["IT", "Telecom", "Media", "Banking"],
    }
    for (planet_name, bull_signs), sectors in sector_map.items():
        planet = next((p for p in planets if p["planet"] == planet_name), None)
        if planet:
            if planet["sign"] in bull_signs and not planet.get("retrograde"):
                buy_sectors.update(sectors)
            elif planet.get("retrograde"):
                hold_sectors.update(sectors)

    # From yogas
    if yoga_data:
        buy_sectors.update(yoga_data.get("favorable_sectors", []))
        avoid_sectors.update(yoga_data.get("avoid_sectors", []))

    # From transits
    if transit_data:
        buy_sectors.update(transit_data.get("nse_sectors", {}).get("buy", []))
        avoid_sectors.update(transit_data.get("nse_sectors", {}).get("avoid", []))

    # Remove overlap
    avoid_sectors -= buy_sectors

    # Always add Gold/Bonds for bearish prediction
    if overall_score < -0.3:
        avoid_sectors -= {"Gold", "Bonds", "FD"}
        buy_sectors.update(["Gold", "Bonds / Debt Funds", "Fixed Deposits"])

    return {
        "strong_buy":   list(buy_sectors)[:8],
        "hold":         list(hold_sectors)[:5],
        "avoid":        list(avoid_sectors)[:5],
        "top_sectors":  list(buy_sectors)[:3],
    }


def _weekly_moon_outlook(planets: List[Dict], from_date: datetime) -> List[Dict]:
    """Generate 7-day Moon nakshatra outlook for daily trading signals."""
    from app.nakshatra import NAKSHATRAS, NAKSHATRA_FINANCIAL, NAKSHATRA_SPAN_DEG

    moon = next((p for p in planets if p["planet"] == "Moon"), None)
    if not moon:
        return []

    # Moon moves ~13.2° per day
    moon_speed = 13.176  # degrees per day
    current_long = moon["longitude"]
    daily_signals = []

    for day_offset in range(7):
        dt = from_date + timedelta(days=day_offset)
        moon_long = (current_long + moon_speed * day_offset) % 360
        nak_info = next(
            (n for n in NAKSHATRAS if n["start"] <= moon_long < n["end"]),
            NAKSHATRAS[-1]
        )
        fin = NAKSHATRA_FINANCIAL.get(nak_info["name"], {})
        score = fin.get("score", 0.0)

        daily_signals.append({
            "date":           dt.strftime("%Y-%m-%d"),
            "day":            dt.strftime("%A"),
            "moon_degree":    round(moon_long, 2),
            "nakshatra":      nak_info["name"],
            "nakshatra_lord": nak_info["lord"],
            "financial_score": score,
            "nse_signal":     fin.get("nse_signal", "NEUTRAL"),
            "market_effect":  fin.get("market_effect", ""),
            "signal_color": (
                "#00C851" if score >= 0.7 else
                "#4CAF50" if score >= 0.4 else
                "#FFC107" if score >= 0.0 else
                "#FF9800" if score >= -0.4 else "#FF3D00"
            ),
        })

    return daily_signals


def _extract_key_events(transit_data: Optional[Dict]) -> List[Dict]:
    """Extract top 5 key upcoming events from transit data."""
    if not transit_data:
        return []
    all_alerts = (
        transit_data.get("high_priority_alerts", []) +
        transit_data.get("medium_priority_alerts", [])
    )
    # Sort by priority and date
    all_alerts = sorted(all_alerts, key=lambda x: (-x.get("priority", 0), x.get("date", "")))
    return all_alerts[:8]


def _identify_risks(planets: List[Dict], transit_data: Optional[Dict]) -> List[str]:
    """Identify key risk factors for the prediction."""
    risks = []

    # Check retrogrades
    for p in planets:
        if p.get("retrograde") and p["planet"] in {"Mercury", "Venus", "Mars", "Jupiter"}:
            risks.append(f"{p['planet']} retrograde in {p['sign']} — reduced {p['planet']} sector reliability")

    # Check debilitated planets
    debil = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
              "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo", "Saturn": "Aries"}
    for p in planets:
        if debil.get(p["planet"]) == p["sign"]:
            risks.append(f"{p['planet']} debilitated in {p['sign']} — sector weakness")

    # Eclipse risk
    if transit_data:
        for alert in transit_data.get("high_priority_alerts", []):
            if "ECLIPSE" in alert.get("type", ""):
                risks.append(f"Eclipse on {alert.get('date', '')} — major market event risk")

    return risks[:5]
