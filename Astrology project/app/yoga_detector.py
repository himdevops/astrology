"""
yoga_detector.py — Vedic Yoga Detection Engine for Financial Astrology
Detects Dhana Yogas, Raj Yogas, Gaja Kesari, Pancha Mahapurusha,
and malefic yogas with NSE/BSE buy/sell signals.
"""
from __future__ import annotations

from typing import Dict, List, Optional, Tuple

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_IDX = {s: i for i, s in enumerate(SIGNS)}

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Exaltation / Debilitation
EXALTATION   = {"Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
                 "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
                 "Saturn": "Libra", "Rahu": "Gemini", "Ketu": "Sagittarius"}
DEBILITATION = {"Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
                 "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
                 "Saturn": "Aries", "Rahu": "Sagittarius", "Ketu": "Gemini"}
OWN_SIGNS    = {"Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries","Scorpio"],
                 "Mercury": ["Gemini","Virgo"], "Jupiter": ["Sagittarius","Pisces"],
                 "Venus": ["Taurus","Libra"], "Saturn": ["Capricorn","Aquarius"]}

NATURAL_BENEFICS  = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS  = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
GREAT_MALEFICS    = {"Saturn", "Mars"}

PANCHA_PLANETS = {
    "Mars":    ("Ruchaka", "Aries", "Scorpio", "Capricorn"),
    "Mercury": ("Bhadra",  "Gemini", "Virgo",  "Virgo"),
    "Jupiter": ("Hamsa",   "Sagittarius", "Pisces", "Cancer"),
    "Venus":   ("Malavya", "Taurus", "Libra",  "Pisces"),
    "Saturn":  ("Sasha",   "Capricorn", "Aquarius", "Libra"),
}


# ─────────────────────────────────────────────────────────────
# Helpers
# ─────────────────────────────────────────────────────────────

def _planet_sign(name: str, planets: List[Dict]) -> Optional[str]:
    for p in planets:
        if p["planet"] == name:
            return p["sign"]
    return None


def _planet_house(name: str, planets: List[Dict], asc_sign: str) -> Optional[int]:
    sign = _planet_sign(name, planets)
    if sign is None:
        return None
    asc_idx = SIGN_IDX.get(asc_sign, 0)
    sign_idx = SIGN_IDX.get(sign, 0)
    return ((sign_idx - asc_idx) % 12) + 1


def _are_conjunct(p1: str, p2: str, planets: List[Dict], orb_deg: float = 10.0) -> bool:
    pos1 = next((p["longitude"] for p in planets if p["planet"] == p1), None)
    pos2 = next((p["longitude"] for p in planets if p["planet"] == p2), None)
    if pos1 is None or pos2 is None:
        return False
    diff = abs(pos1 - pos2) % 360
    return min(diff, 360 - diff) <= orb_deg


def _are_aspecting(p1: str, p2: str, planets: List[Dict]) -> bool:
    """Check Vedic full aspects (7th aspect for all; special for Mars/Jupiter/Saturn)."""
    s1 = _planet_sign(p1, planets)
    s2 = _planet_sign(p2, planets)
    if s1 is None or s2 is None:
        return False
    diff = (SIGN_IDX[s2] - SIGN_IDX[s1]) % 12

    # 7th full aspect (all planets)
    if diff == 6:
        return True
    # Mars: 4th and 8th
    if p1 == "Mars" and diff in (3, 7):
        return True
    # Jupiter: 5th and 9th
    if p1 == "Jupiter" and diff in (4, 8):
        return True
    # Saturn: 3rd and 10th
    if p1 == "Saturn" and diff in (2, 9):
        return True
    return False


def _house_lord(house_num: int, asc_sign: str) -> str:
    sign_idx = (SIGN_IDX.get(asc_sign, 0) + house_num - 1) % 12
    return SIGN_LORDS[SIGNS[sign_idx]]


def _houses_of_planet(planet: str, planets: List[Dict], asc_sign: str) -> Optional[int]:
    return _planet_house(planet, planets, asc_sign)


# ─────────────────────────────────────────────────────────────
# Yoga Detection Functions
# ─────────────────────────────────────────────────────────────

def _check_gaja_kesari(planets: List[Dict], asc_sign: str) -> Optional[Dict]:
    """Gaja Kesari Yoga: Jupiter in kendra (1,4,7,10) from Moon."""
    jup_sign = _planet_sign("Jupiter", planets)
    moon_sign = _planet_sign("Moon", planets)
    if jup_sign is None or moon_sign is None:
        return None
    diff = (SIGN_IDX[jup_sign] - SIGN_IDX[moon_sign]) % 12
    if diff in (0, 3, 6, 9):
        strength = "Strong" if diff in (0, 6) else "Moderate"
        return {
            "name":         "Gaja Kesari Yoga",
            "sanskrit":     "गज केसरी योग",
            "type":         "Dhana (Wealth)",
            "strength":     strength,
            "planets":      ["Jupiter", "Moon"],
            "description":  (
                f"Jupiter in {jup_sign} is in {diff//3 + 1}th kendra from Moon in {moon_sign}. "
                "Elephant-Lion combination: great intelligence, wealth, fame, and leadership."
            ),
            "financial_impact": (
                "Excellent for financial growth. Banking, finance, and FMCG sectors benefit. "
                "Bull markets tend to form or sustain during this yoga."
            ),
            "nse_signal": "BULLISH",
            "score": 0.85,
        }
    return None


def _check_dhana_yogas(planets: List[Dict], asc_sign: str) -> List[Dict]:
    """Detect Dhana Yogas (wealth combinations)."""
    yogas = []
    lords_2_11 = [_house_lord(2, asc_sign), _house_lord(11, asc_sign)]
    lords_1_9  = [_house_lord(1, asc_sign), _house_lord(9, asc_sign)]

    # Dhana Yoga 1: 2nd and 11th lords conjunct/aspect each other
    l2, l11 = lords_2_11
    if l2 != l11:
        if _are_conjunct(l2, l11, planets) or _are_aspecting(l2, l11, planets):
            yogas.append({
                "name":         "Dhana Yoga (2nd-11th Lords)",
                "sanskrit":     "धन योग",
                "type":         "Dhana (Wealth)",
                "strength":     "Strong",
                "planets":      [l2, l11],
                "description":  (
                    f"2nd lord ({l2}) and 11th lord ({l11}) are conjunct or aspecting — "
                    "classic wealth yoga from Parashara."
                ),
                "financial_impact": (
                    "Indicates accumulated wealth, high income, and financial prosperity. "
                    "Strong indication of stock market gains."
                ),
                "nse_signal": "BULLISH",
                "score": 0.80,
            })

    # Dhana Yoga 2: 9th and 11th lords combined
    l9, l11 = _house_lord(9, asc_sign), _house_lord(11, asc_sign)
    if l9 != l11 and (_are_conjunct(l9, l11, planets) or _are_aspecting(l9, l11, planets)):
        yogas.append({
            "name":         "Lakshmi-Kubera Yoga",
            "sanskrit":     "लक्ष्मी कुबेर योग",
            "type":         "Dhana (Wealth)",
            "strength":     "Strong",
            "planets":      [l9, l11],
            "description":  f"9th lord ({l9}) and 11th lord ({l11}) combined — fortune + gains.",
            "financial_impact": "Fortune favors financial investments. Long-term wealth accumulation.",
            "nse_signal": "BULLISH",
            "score": 0.75,
        })

    # Dhana Yoga 3: Jupiter in 2nd or 11th house
    jup_house = _planet_house("Jupiter", planets, asc_sign)
    if jup_house in (2, 5, 9, 11):
        yogas.append({
            "name":         "Guru Dhana Yoga",
            "sanskrit":     "गुरु धन योग",
            "type":         "Dhana (Wealth)",
            "strength":     "Moderate" if jup_house in (5, 9) else "Strong",
            "planets":      ["Jupiter"],
            "description":  f"Jupiter in {jup_house}th house — wealth through wisdom and expansion.",
            "financial_impact": "Banking, finance, and education sector gains. Long-term wealth.",
            "nse_signal": "BULLISH",
            "score": 0.70,
        })

    # Venus in 2nd or 7th (trading/partnerships)
    ven_house = _planet_house("Venus", planets, asc_sign)
    if ven_house in (2, 7, 11):
        yogas.append({
            "name":         "Shukra Dhana Yoga",
            "sanskrit":     "शुक्र धन योग",
            "type":         "Dhana (Wealth)",
            "strength":     "Moderate",
            "planets":      ["Venus"],
            "description":  f"Venus in {ven_house}th house — luxury, pleasure, and earned income.",
            "financial_impact": "FMCG, luxury, entertainment sector gains. Consumer spending up.",
            "nse_signal": "BULLISH",
            "score": 0.65,
        })

    return yogas


def _check_raj_yogas(planets: List[Dict], asc_sign: str) -> List[Dict]:
    """Detect Raj Yogas (power and authority combinations)."""
    yogas = []
    kendra_lords = [_house_lord(h, asc_sign) for h in (1, 4, 7, 10)]
    trikona_lords = [_house_lord(h, asc_sign) for h in (1, 5, 9)]

    seen_pairs = set()
    for kl in set(kendra_lords):
        for tl in set(trikona_lords):
            if kl != tl and (kl, tl) not in seen_pairs and (tl, kl) not in seen_pairs:
                if _are_conjunct(kl, tl, planets) or _are_aspecting(kl, tl, planets):
                    yogas.append({
                        "name":         "Raj Yoga",
                        "sanskrit":     "राज योग",
                        "type":         "Power & Authority",
                        "strength":     "Strong",
                        "planets":      [kl, tl],
                        "description":  (
                            f"Kendra lord ({kl}) and Trikona lord ({tl}) are combined — "
                            "Parashara's classic Raj Yoga."
                        ),
                        "financial_impact": (
                            "Market leadership, index-level bull runs. Government/PSU stocks "
                            "outperform. Strong IPO market."
                        ),
                        "nse_signal": "STRONGLY BULLISH",
                        "score": 0.90,
                    })
                    seen_pairs.add((kl, tl))

    return yogas


def _check_pancha_mahapurusha(planets: List[Dict], asc_sign: str) -> List[Dict]:
    """Detect Pancha Mahapurusha Yogas."""
    yogas = []
    for planet, (yoga_name, own1, own2, exalt) in PANCHA_PLANETS.items():
        sign = _planet_sign(planet, planets)
        house = _planet_house(planet, planets, asc_sign)
        if sign in (own1, own2, exalt) and house in (1, 4, 7, 10):
            yogas.append({
                "name":         f"{yoga_name} Yoga",
                "sanskrit":     f"{yoga_name} योग",
                "type":         "Pancha Mahapurusha",
                "strength":     "Exalted" if sign == exalt else "Own Sign",
                "planets":      [planet],
                "description":  (
                    f"{planet} in {sign} ({house}th house kendra) — {yoga_name} Yoga forms. "
                    "One of 5 great personality yogas (Parashara)."
                ),
                "financial_impact": _pancha_financial(yoga_name),
                "nse_signal": "BULLISH",
                "score": 0.80 if sign == exalt else 0.70,
            })
    return yogas


def _pancha_financial(yoga_name: str) -> str:
    impacts = {
        "Ruchaka": "Mars energy: Defense, real estate, energy stocks rally. Market momentum.",
        "Bhadra":  "Mercury intellect: IT, trading, telecom sector outperformance.",
        "Hamsa":   "Jupiter wisdom: Banking, finance, education are key themes.",
        "Malavya": "Venus luxury: FMCG, entertainment, auto sector boom.",
        "Sasha":   "Saturn discipline: Oil, mining, infrastructure long-term gains.",
    }
    return impacts.get(yoga_name, "Strong financial period.")


def _check_viparita_raj_yoga(planets: List[Dict], asc_sign: str) -> List[Dict]:
    """
    Viparita Raj Yoga: 6th, 8th, 12th lords in each other's signs.
    Brings unexpected gains from enemies, debts, or hidden sources.
    """
    yogas = []
    dusthana_lords = {
        6: _house_lord(6, asc_sign),
        8: _house_lord(8, asc_sign),
        12: _house_lord(12, asc_sign),
    }
    dusthana_signs = {
        SIGNS[(SIGN_IDX[asc_sign] + 5) % 12],
        SIGNS[(SIGN_IDX[asc_sign] + 7) % 12],
        SIGNS[(SIGN_IDX[asc_sign] + 11) % 12],
    }

    for house_num, lord in dusthana_lords.items():
        lord_sign = _planet_sign(lord, planets)
        if lord_sign in dusthana_signs and lord_sign != SIGNS[(SIGN_IDX[asc_sign] + house_num - 1) % 12]:
            yogas.append({
                "name":         f"Viparita Raj Yoga ({house_num}th lord)",
                "sanskrit":     "विपरीत राज योग",
                "type":         "Unexpected Gains",
                "strength":     "Moderate",
                "planets":      [lord],
                "description":  (
                    f"{house_num}th lord {lord} in another dusthana ({lord_sign}). "
                    "Enemies destroy each other; unexpected rise from crisis."
                ),
                "financial_impact": (
                    "Unexpected market reversals become profitable. Short-sellers trapped. "
                    "Sector-specific sudden gains from crisis situations."
                ),
                "nse_signal": "VOLATILE — sudden gains",
                "score": 0.55,
            })
    return yogas


def _check_malefic_yogas(planets: List[Dict], asc_sign: str) -> List[Dict]:
    """Detect negative yogas that hurt financial outcomes."""
    yogas = []

    # Kemadruma Yoga: Moon has no planets in 2nd or 12th from it
    moon_sign = _planet_sign("Moon", planets)
    if moon_sign:
        moon_idx = SIGN_IDX[moon_sign]
        adjacent = {SIGNS[(moon_idx + 1) % 12], SIGNS[(moon_idx - 1) % 12]}
        other_planets = [p for p in planets if p["planet"] not in ("Moon", "Rahu", "Ketu")]
        adjacent_occupied = any(p["sign"] in adjacent for p in other_planets)
        if not adjacent_occupied:
            yogas.append({
                "name":         "Kemadruma Yoga",
                "sanskrit":     "केमद्रुम योग",
                "type":         "Malefic",
                "strength":     "Weak",
                "planets":      ["Moon"],
                "description":  "Moon has no planets in 2nd or 12th house from it.",
                "financial_impact": (
                    "Emotional/impulsive financial decisions. Avoid trading on gut feeling. "
                    "FMCG and consumer sector may underperform."
                ),
                "nse_signal": "BEARISH for Moon sectors",
                "score": -0.40,
            })

    # Graha Yuddha: Mars-Saturn conjunction
    if _are_conjunct("Mars", "Saturn", planets, orb_deg=8):
        yogas.append({
            "name":         "Mars-Saturn Conjunction (Graha Yuddha)",
            "sanskrit":     "ग्रह युद्ध",
            "type":         "Malefic",
            "strength":     "Strong (Negative)",
            "planets":      ["Mars", "Saturn"],
            "description":  "Mars and Saturn in close conjunction — planetary war.",
            "financial_impact": (
                "Market turbulence, industrial accidents, geopolitical tensions. "
                "Real estate and infrastructure sectors under pressure."
            ),
            "nse_signal": "BEARISH — reduce exposure",
            "score": -0.70,
        })

    # Rahu-Ketu on financial axis (2nd-8th or 5th-11th)
    rahu_house = _planet_house("Rahu", planets, asc_sign)
    if rahu_house in (2, 8, 5, 11):
        axis = f"{rahu_house}th-{(rahu_house + 5) % 12 + 1}th"
        yogas.append({
            "name":         f"Rahu-Ketu on Financial Axis ({axis})",
            "sanskrit":     "राहु-केतु धन अक्ष",
            "type":         "Mixed — Disruption",
            "strength":     "Strong",
            "planets":      ["Rahu", "Ketu"],
            "description":  f"Rahu-Ketu axis on {axis} houses — financial obsession and disruption.",
            "financial_impact": (
                "Extreme greed/fear cycles. Tech and foreign sector volatility. "
                "Cryptocurrency and speculative assets highly volatile."
            ),
            "nse_signal": "VOLATILE — use stop-loss",
            "score": -0.20,
        })

    # Shakat Yoga: Moon in 6th/8th/12th from Jupiter
    jup_sign = _planet_sign("Jupiter", planets)
    if moon_sign and jup_sign:
        jup_idx = SIGN_IDX[jup_sign]
        moon_from_jup = (SIGN_IDX[moon_sign] - jup_idx) % 12
        if moon_from_jup in (5, 7, 11):
            yogas.append({
                "name":         "Shakat Yoga",
                "sanskrit":     "शकट योग",
                "type":         "Malefic",
                "strength":     "Moderate (Negative)",
                "planets":      ["Moon", "Jupiter"],
                "description":  f"Moon in {moon_from_jup + 1}th from Jupiter — wheel of fortune turns.",
                "financial_impact": (
                    "Unstable income, reversals in financial fortune. "
                    "Banking sector may face sudden corrections."
                ),
                "nse_signal": "CAUTIOUS",
                "score": -0.35,
            })

    return yogas


def _check_special_yogas(planets: List[Dict], asc_sign: str) -> List[Dict]:
    """Additional special financial yogas."""
    yogas = []

    # Budha-Aditya Yoga: Sun + Mercury conjunct
    if _are_conjunct("Sun", "Mercury", planets, orb_deg=10):
        yogas.append({
            "name":         "Budha-Aditya Yoga",
            "sanskrit":     "बुध-आदित्य योग",
            "type":         "Intelligence & Commerce",
            "strength":     "Moderate",
            "planets":      ["Sun", "Mercury"],
            "description":  "Sun and Mercury conjunct — sharp intellect in authority.",
            "financial_impact": (
                "IT, government tech contracts, media sector gains. "
                "Good for data-driven trading strategies."
            ),
            "nse_signal": "BULLISH for IT/Govt sectors",
            "score": 0.55,
        })

    # Venus-Jupiter mutual aspect/conjunction
    if (_are_conjunct("Venus", "Jupiter", planets, orb_deg=10) or
            _are_aspecting("Venus", "Jupiter", planets) or
            _are_aspecting("Jupiter", "Venus", planets)):
        yogas.append({
            "name":         "Venus-Jupiter (Lakshmi-Guru Yoga)",
            "sanskrit":     "लक्ष्मी गुरु योग",
            "type":         "Supreme Wealth",
            "strength":     "Strong",
            "planets":      ["Venus", "Jupiter"],
            "description":  "Venus and Jupiter combined or aspecting — goddess of wealth with guru.",
            "financial_impact": (
                "Premium financial period. Luxury + banking sectors, real estate, entertainment. "
                "One of the best combinations for wealth creation."
            ),
            "nse_signal": "STRONGLY BULLISH",
            "score": 0.90,
        })

    # Moon-Jupiter combination (lesser Gaja Kesari)
    if _are_conjunct("Moon", "Jupiter", planets, orb_deg=10):
        yogas.append({
            "name":         "Chandra-Guru Yoga",
            "sanskrit":     "चंद्र गुरु योग",
            "type":         "Wealth & Popularity",
            "strength":     "Moderate",
            "planets":      ["Moon", "Jupiter"],
            "description":  "Moon and Jupiter conjunct — emotional intelligence meets expansion.",
            "financial_impact": "Consumer goods, real estate, banking all benefit together.",
            "nse_signal": "BULLISH",
            "score": 0.70,
        })

    return yogas


# ─────────────────────────────────────────────────────────────
# Master Yoga Detection Function
# ─────────────────────────────────────────────────────────────

def detect_all_yogas(planets: List[Dict], ascendant: Dict) -> Dict:
    """
    Detect all financial yogas in a chart.
    Returns positive, negative yogas, and an overall market signal.
    """
    asc_sign = ascendant["sign"]
    all_yogas: List[Dict] = []

    # Positive yogas
    gk = _check_gaja_kesari(planets, asc_sign)
    if gk:
        all_yogas.append(gk)

    all_yogas.extend(_check_dhana_yogas(planets, asc_sign))
    all_yogas.extend(_check_raj_yogas(planets, asc_sign))
    all_yogas.extend(_check_pancha_mahapurusha(planets, asc_sign))
    all_yogas.extend(_check_viparita_raj_yoga(planets, asc_sign))
    all_yogas.extend(_check_special_yogas(planets, asc_sign))

    # Negative yogas
    all_yogas.extend(_check_malefic_yogas(planets, asc_sign))

    # Categorize
    positive = [y for y in all_yogas if y["score"] >= 0]
    negative = [y for y in all_yogas if y["score"] < 0]

    total_score = sum(y["score"] for y in all_yogas)
    yoga_count = len(all_yogas)
    avg_score = total_score / yoga_count if yoga_count else 0

    if avg_score >= 0.6:
        overall_signal = "STRONGLY BULLISH"
        summary = "Multiple powerful wealth yogas active — excellent period for investments."
        color = "#00C851"
    elif avg_score >= 0.3:
        overall_signal = "BULLISH"
        summary = "Positive yogas dominate — favorable for equity investments."
        color = "#4CAF50"
    elif avg_score >= 0.0:
        overall_signal = "MILDLY BULLISH"
        summary = "Mixed yogas with slight positive bias — selective investment approach."
        color = "#8BC34A"
    elif avg_score >= -0.3:
        overall_signal = "CAUTIOUS"
        summary = "Malefic yogas offset gains — tight stop-losses recommended."
        color = "#FF9800"
    else:
        overall_signal = "BEARISH"
        summary = "Strong malefic yogas — capital preservation priority."
        color = "#FF3D00"

    return {
        "ascendant":          asc_sign,
        "total_yogas_found":  yoga_count,
        "positive_yogas":     positive,
        "negative_yogas":     negative,
        "all_yogas":          all_yogas,
        "overall_yoga_score": round(avg_score, 3),
        "overall_signal":     overall_signal,
        "signal_color":       color,
        "summary":            summary,
        "favorable_sectors":  _get_yoga_sectors(positive),
        "avoid_sectors":      _get_yoga_sectors(negative, "avoid"),
    }


def _get_yoga_sectors(yogas: List[Dict], mode: str = "buy") -> List[str]:
    sectors: List[str] = []
    for yoga in yogas:
        impact = yoga.get("financial_impact", "")
        # Extract sector mentions from impact text
        sector_keywords = [
            "Banking", "Finance", "IT", "Pharma", "FMCG", "Real Estate",
            "Defense", "Infrastructure", "Gold", "Energy", "Auto", "Telecom",
            "Mining", "Luxury", "Entertainment", "PSU", "Technology"
        ]
        for kw in sector_keywords:
            if kw in impact and kw not in sectors:
                sectors.append(kw)
    return sectors[:8]  # Limit to top 8
