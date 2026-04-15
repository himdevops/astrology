"""
nakshatra.py — 27 Nakshatra Engine with Financial Astrology Significance
Includes nakshatra, pada, lord, sub-lord (KP), and NSE/BSE market impact data.
"""
from __future__ import annotations
from typing import Dict, List

# ─────────────────────────────────────────────────────────────
# 27 Nakshatras: each spans exactly 13°20' (13.3333°)
# ─────────────────────────────────────────────────────────────
NAKSHATRAS: List[Dict] = [
    {"id": 1,  "name": "Ashwini",           "lord": "Ketu",    "start": 0.000000,  "end": 13.333333},
    {"id": 2,  "name": "Bharani",           "lord": "Venus",   "start": 13.333333, "end": 26.666667},
    {"id": 3,  "name": "Krittika",          "lord": "Sun",     "start": 26.666667, "end": 40.000000},
    {"id": 4,  "name": "Rohini",            "lord": "Moon",    "start": 40.000000, "end": 53.333333},
    {"id": 5,  "name": "Mrigashira",        "lord": "Mars",    "start": 53.333333, "end": 66.666667},
    {"id": 6,  "name": "Ardra",             "lord": "Rahu",    "start": 66.666667, "end": 80.000000},
    {"id": 7,  "name": "Punarvasu",         "lord": "Jupiter", "start": 80.000000, "end": 93.333333},
    {"id": 8,  "name": "Pushya",            "lord": "Saturn",  "start": 93.333333, "end": 106.666667},
    {"id": 9,  "name": "Ashlesha",          "lord": "Mercury", "start": 106.666667,"end": 120.000000},
    {"id": 10, "name": "Magha",             "lord": "Ketu",    "start": 120.000000,"end": 133.333333},
    {"id": 11, "name": "Purva Phalguni",    "lord": "Venus",   "start": 133.333333,"end": 146.666667},
    {"id": 12, "name": "Uttara Phalguni",   "lord": "Sun",     "start": 146.666667,"end": 160.000000},
    {"id": 13, "name": "Hasta",             "lord": "Moon",    "start": 160.000000,"end": 173.333333},
    {"id": 14, "name": "Chitra",            "lord": "Mars",    "start": 173.333333,"end": 186.666667},
    {"id": 15, "name": "Swati",             "lord": "Rahu",    "start": 186.666667,"end": 200.000000},
    {"id": 16, "name": "Vishakha",          "lord": "Jupiter", "start": 200.000000,"end": 213.333333},
    {"id": 17, "name": "Anuradha",          "lord": "Saturn",  "start": 213.333333,"end": 226.666667},
    {"id": 18, "name": "Jyeshtha",          "lord": "Mercury", "start": 226.666667,"end": 240.000000},
    {"id": 19, "name": "Mula",              "lord": "Ketu",    "start": 240.000000,"end": 253.333333},
    {"id": 20, "name": "Purva Ashadha",     "lord": "Venus",   "start": 253.333333,"end": 266.666667},
    {"id": 21, "name": "Uttara Ashadha",    "lord": "Sun",     "start": 266.666667,"end": 280.000000},
    {"id": 22, "name": "Shravana",          "lord": "Moon",    "start": 280.000000,"end": 293.333333},
    {"id": 23, "name": "Dhanishtha",        "lord": "Mars",    "start": 293.333333,"end": 306.666667},
    {"id": 24, "name": "Shatabhisha",       "lord": "Rahu",    "start": 306.666667,"end": 320.000000},
    {"id": 25, "name": "Purva Bhadrapada",  "lord": "Jupiter", "start": 320.000000,"end": 333.333333},
    {"id": 26, "name": "Uttara Bhadrapada", "lord": "Saturn",  "start": 333.333333,"end": 346.666667},
    {"id": 27, "name": "Revati",            "lord": "Mercury", "start": 346.666667,"end": 360.000000},
]

# Dasha lord sequence (Vimshottari order)
NAKSHATRA_LORD_ORDER: List[str] = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]

# Dasha years
DASHA_YEARS: Dict[str, int] = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17
}
TOTAL_DASHA_YEARS: int = 120

# ─────────────────────────────────────────────────────────────
# Financial significance per nakshatra (NSE/BSE focus)
# score: -1.0 (very bearish) to +1.0 (very bullish)
# ─────────────────────────────────────────────────────────────
NAKSHATRA_FINANCIAL: Dict[str, Dict] = {
    "Ashwini":           {"nature": "Movable",  "quality": "Light & Swift",  "score": 0.70,
                          "market_effect": "Sudden upward moves; excellent for short-term trades. Ashwini Kumars = healers → pharma/biotech rally.",
                          "sectors": ["Pharma", "Healthcare", "Auto", "Quick-service"],
                          "nse_signal": "BUY short-term"},
    "Bharani":           {"nature": "Fierce",   "quality": "Sharp",          "score": -0.30,
                          "market_effect": "Transformation phase; volatile and destructive. Yama's nakshatra — avoid large positions.",
                          "sectors": ["Exit positions", "Restructuring plays"],
                          "nse_signal": "CAUTION"},
    "Krittika":          {"nature": "Mixed",    "quality": "Sharp & Fierce", "score": 0.20,
                          "market_effect": "Cutting/transformative energy. Momentum in fire sectors; sharp reversals possible.",
                          "sectors": ["Energy", "Defense", "Steel"],
                          "nse_signal": "HOLD with stop-loss"},
    "Rohini":            {"nature": "Fixed",    "quality": "Soft",           "score": 0.90,
                          "market_effect": "Most bullish nakshatra for markets. Taurus/wealth energy; sustained growth.",
                          "sectors": ["Banking", "FMCG", "Real Estate", "Luxury"],
                          "nse_signal": "STRONG BUY"},
    "Mrigashira":        {"nature": "Soft",     "quality": "Mild",           "score": 0.50,
                          "market_effect": "Searching/exploring energy. Moderate bullish with sector rotation.",
                          "sectors": ["Travel", "Research", "Textiles"],
                          "nse_signal": "BUY selectively"},
    "Ardra":             {"nature": "Sharp",    "quality": "Fierce",         "score": -0.60,
                          "market_effect": "Storm energy (Rudra). Market shocks, FII outflows, tech disruptions.",
                          "sectors": ["Avoid equities", "Buy Gold as hedge"],
                          "nse_signal": "SELL / HEDGE"},
    "Punarvasu":         {"nature": "Movable",  "quality": "Light",          "score": 0.60,
                          "market_effect": "Return/renewal energy. Recovery rallies after corrections.",
                          "sectors": ["Consumer Goods", "Education", "Housing"],
                          "nse_signal": "BUY on dip"},
    "Pushya":            {"nature": "Fixed",    "quality": "Light",          "score": 1.00,
                          "market_effect": "Best nakshatra for investments (nourishing). Akshaya Tritiya-level auspiciousness.",
                          "sectors": ["All sectors", "Banking", "Gold", "Long-term SIP"],
                          "nse_signal": "STRONG BUY — best day to enter"},
    "Ashlesha":          {"nature": "Sharp",    "quality": "Fierce/Deceptive","score": -0.70,
                          "market_effect": "Snake energy: trap rallies and false breakouts. Avoid new positions.",
                          "sectors": ["Exit Chemical stocks", "Avoid trading day"],
                          "nse_signal": "AVOID — trap day"},
    "Magha":             {"nature": "Fierce",   "quality": "Fixed",          "score": 0.40,
                          "market_effect": "Regal power moves. Large-cap leader stocks rally; mid/small caps lag.",
                          "sectors": ["Large-cap Blue Chips", "PSU Giants", "Political/Infra"],
                          "nse_signal": "BUY large-caps only"},
    "Purva Phalguni":    {"nature": "Fierce",   "quality": "Soft",           "score": 0.50,
                          "market_effect": "Enjoyment/luxury energy. Consumer discretionary and entertainment rally.",
                          "sectors": ["FMCG", "Media/Entertainment", "Hotels", "Gems"],
                          "nse_signal": "BUY consumer sector"},
    "Uttara Phalguni":   {"nature": "Fixed",    "quality": "Light",          "score": 0.70,
                          "market_effect": "Stable long-term wealth. Patron energy — wealth accumulation trend.",
                          "sectors": ["Banking", "Contracts/Legal", "IT Services"],
                          "nse_signal": "BUY for swing trade"},
    "Hasta":             {"nature": "Movable",  "quality": "Light & Swift",  "score": 0.60,
                          "market_effect": "Skillful trading day. Craftsmanship sectors excel; good for tactical entries.",
                          "sectors": ["Handicrafts", "Publishing", "Precision Engineering"],
                          "nse_signal": "BUY tactical"},
    "Chitra":            {"nature": "Soft",     "quality": "Bright/Variable","score": 0.30,
                          "market_effect": "Brilliant but volatile. Technical rallies; construction/architecture themes.",
                          "sectors": ["Construction", "Architecture", "Textiles", "Design"],
                          "nse_signal": "HOLD — volatile"},
    "Swati":             {"nature": "Movable",  "quality": "Scattered",      "score": 0.10,
                          "market_effect": "Independent/scattered energy. Mixed signals; FII-driven moves.",
                          "sectors": ["Trading range day", "Intraday only"],
                          "nse_signal": "NEUTRAL"},
    "Vishakha":          {"nature": "Mixed",    "quality": "Sharp & Soft",   "score": 0.40,
                          "market_effect": "Goal-oriented sector-specific gains. Agni/Indra: fire and weather sectors.",
                          "sectors": ["Agriculture", "Chemicals", "Weather-linked commodities"],
                          "nse_signal": "BUY sector-specific"},
    "Anuradha":          {"nature": "Soft",     "quality": "Mild & Fixed",   "score": 0.50,
                          "market_effect": "Friendship/devotion energy. Steady accumulation; cooperative sector gains.",
                          "sectors": ["Telecom", "Networking", "Hospitality"],
                          "nse_signal": "BUY for medium-term"},
    "Jyeshtha":          {"nature": "Sharp",    "quality": "Fierce",         "score": 0.20,
                          "market_effect": "Elder/chief energy. Market leaders rally but overconfidence risk; sudden fall.",
                          "sectors": ["Market leaders", "Index heavyweights"],
                          "nse_signal": "SELL into strength"},
    "Mula":              {"nature": "Sharp",    "quality": "Extremely Fierce","score": -0.80,
                          "market_effect": "Destruction to root level. Crashes, major sell-offs, systemic risk events.",
                          "sectors": ["EXIT ALL — capital preservation", "Short ETFs"],
                          "nse_signal": "STRONG SELL — crash risk"},
    "Purva Ashadha":     {"nature": "Fierce",   "quality": "Fierce",         "score": 0.60,
                          "market_effect": "Invincible/victorious energy. Commodities (water = Venus) rally strongly.",
                          "sectors": ["Commodities", "Oil & Gas", "Export-oriented"],
                          "nse_signal": "BUY commodities"},
    "Uttara Ashadha":    {"nature": "Fixed",    "quality": "Fixed",          "score": 0.80,
                          "market_effect": "Final victory. Sustained market rally confirmation; breakout confirmation.",
                          "sectors": ["All sectors", "Index funds", "Long-term investing"],
                          "nse_signal": "STRONG BUY — breakout confirmed"},
    "Shravana":          {"nature": "Movable",  "quality": "Mild",           "score": 0.40,
                          "market_effect": "Listening/news-driven. React fast to policy announcements; information edge.",
                          "sectors": ["Media", "News", "Education", "Telecom"],
                          "nse_signal": "NEWS-DRIVEN — watch announcements"},
    "Dhanishtha":        {"nature": "Movable",  "quality": "Sharp",          "score": 0.80,
                          "market_effect": "Wealth-giving nakshatra (Dhan = wealth). Very bullish for banking/finance.",
                          "sectors": ["Banking", "Finance", "Music/Media", "Real Estate"],
                          "nse_signal": "STRONG BUY — wealth sector"},
    "Shatabhisha":       {"nature": "Movable",  "quality": "Mild & Sharp",   "score": 0.30,
                          "market_effect": "100 physicians: healing + secretive. Pharma/Chemical/Tech R&D plays.",
                          "sectors": ["Pharma", "Biotech", "Chemicals", "IT R&D"],
                          "nse_signal": "BUY pharma/tech"},
    "Purva Bhadrapada":  {"nature": "Fierce",   "quality": "Fierce",         "score": -0.20,
                          "market_effect": "Two-faced: initial rally then sharp reversal. Trap for latecomers.",
                          "sectors": ["High-beta stocks", "Exit at highs"],
                          "nse_signal": "CAUTION — sell the rally"},
    "Uttara Bhadrapada": {"nature": "Fixed",    "quality": "Soft & Stable",  "score": 0.70,
                          "market_effect": "Deep roots/stable growth. Long-term accumulation; ocean-depth stability.",
                          "sectors": ["Shipping", "Ocean trade", "Long-term bonds"],
                          "nse_signal": "BUY long-term"},
    "Revati":            {"nature": "Soft",     "quality": "Soft & Nourishing","score": 0.50,
                          "market_effect": "Nourishing end-of-cycle. Banking/finance sector positive; closure of trades.",
                          "sectors": ["Banking", "Shipping", "Fish/Marine", "Travel"],
                          "nse_signal": "BOOK PROFITS / BANKING BUY"},
}

# ─────────────────────────────────────────────────────────────
# KP Sub-lord sequence (same as nakshatra lord order)
# Each nakshatra pada (3°20') is further divided into 9 sub-lords
# ─────────────────────────────────────────────────────────────
NAKSHATRA_SPAN_DEG: float = 360.0 / 27  # 13.333...°
PADA_SPAN_DEG: float = NAKSHATRA_SPAN_DEG / 4  # 3.333...°


def get_nakshatra(longitude: float) -> Dict:
    """
    Get complete nakshatra data for a given sidereal longitude (0–360°).
    Returns nakshatra name, lord, pada, sub-lord (KP), and financial data.
    """
    longitude = longitude % 360.0
    idx = int(longitude / NAKSHATRA_SPAN_DEG)
    idx = min(idx, 26)
    n = NAKSHATRAS[idx]

    degree_in_nakshatra = longitude - n["start"]
    pada = int(degree_in_nakshatra / PADA_SPAN_DEG) + 1
    pada = min(pada, 4)

    # KP sub-lord: divide each nakshatra by dasha proportions
    lord_start_idx = NAKSHATRA_LORD_ORDER.index(n["lord"])
    sub_lord = _get_kp_sublord(degree_in_nakshatra, lord_start_idx)

    financial = NAKSHATRA_FINANCIAL.get(n["name"], {})

    return {
        "nakshatra":             n["name"],
        "nakshatra_number":      n["id"],
        "lord":                  n["lord"],
        "pada":                  pada,
        "sub_lord":              sub_lord,
        "degree_in_nakshatra":   round(degree_in_nakshatra, 4),
        "financial_nature":      financial.get("nature", ""),
        "financial_quality":     financial.get("quality", ""),
        "financial_score":       financial.get("score", 0.0),
        "market_effect":         financial.get("market_effect", ""),
        "sectors":               financial.get("sectors", []),
        "nse_signal":            financial.get("nse_signal", "NEUTRAL"),
    }


def _get_kp_sublord(degree_in_nakshatra: float, lord_start_idx: int) -> str:
    """Calculate KP sub-lord within a nakshatra using dasha proportions."""
    fraction = degree_in_nakshatra / NAKSHATRA_SPAN_DEG  # 0 to 1
    cumulative = 0.0
    for i in range(9):
        sub_idx = (lord_start_idx + i) % 9
        sub_lord = NAKSHATRA_LORD_ORDER[sub_idx]
        sub_fraction = DASHA_YEARS[sub_lord] / TOTAL_DASHA_YEARS
        cumulative += sub_fraction
        if fraction <= cumulative:
            return sub_lord
    return NAKSHATRA_LORD_ORDER[lord_start_idx]


def get_all_planet_nakshatras(planets: List[Dict]) -> List[Dict]:
    """Get nakshatra data for all planets in a chart."""
    results = []
    for planet in planets:
        info = get_nakshatra(planet["longitude"])
        results.append({
            "planet":      planet["planet"],
            "longitude":   planet["longitude"],
            "sign":        planet["sign"],
            "retrograde":  planet.get("retrograde", False),
            **info,
        })
    return results


def get_moon_nakshatra_signal(moon_longitude: float) -> Dict:
    """
    Get current Moon nakshatra signal for NSE/BSE intraday trading.
    Moon changes nakshatra every ~1 day — key for daily signals.
    """
    info = get_nakshatra(moon_longitude)
    score = info["financial_score"]
    if score >= 0.7:
        overall = "BULLISH"
        color = "green"
    elif score >= 0.3:
        overall = "MODERATELY BULLISH"
        color = "lightgreen"
    elif score >= -0.1:
        overall = "NEUTRAL"
        color = "yellow"
    elif score >= -0.5:
        overall = "MODERATELY BEARISH"
        color = "orange"
    else:
        overall = "BEARISH"
        color = "red"

    return {
        "moon_nakshatra":   info["nakshatra"],
        "lord":             info["lord"],
        "pada":             info["pada"],
        "sub_lord":         info["sub_lord"],
        "overall_signal":   overall,
        "signal_color":     color,
        "financial_score":  score,
        "nse_action":       info["nse_signal"],
        "market_effect":    info["market_effect"],
        "sectors":          info["sectors"],
    }
