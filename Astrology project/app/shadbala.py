"""
shadbala.py — Six-fold Planetary Strength (Shadbala) for Financial Astrology
Implements all 6 components of Shadbala per Parashara and BPHS:
1. Sthana Bala (Positional Strength)
2. Dig Bala (Directional Strength)
3. Kala Bala (Temporal Strength)
4. Cheshta Bala (Motional Strength)
5. Naisargika Bala (Natural Strength)
6. Drig Bala (Aspectual Strength)

Each bala is measured in Rupas (1 Rupa = 60 Virupas).
Financial interpretation maps planetary strength to market sector confidence.
"""
from __future__ import annotations

import math
from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.constants import (
    SIGNS, SIGN_IDX, SIGN_LORDS,
    EXALTATION, EXALTATION_DEGREE, DEBILITATION, OWN_SIGNS, MOOLATRIKONA,
    NATURAL_FRIENDS, DIG_BALA_HOUSE, FINANCIAL_KARAKAS,
)


# ─────────────────────────────────────────────────────────────
# Required Minimum Shadbala (in Rupas) per Parashara
# ─────────────────────────────────────────────────────────────
REQUIRED_STRENGTH = {
    "Sun": 6.5, "Moon": 6.0, "Mars": 5.0, "Mercury": 7.0,
    "Jupiter": 6.5, "Venus": 5.5, "Saturn": 5.0,
}

SHADBALA_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


def calculate_shadbala(
    planets: List[Dict],
    ascendant: Dict,
    birth_datetime: datetime,
    latitude: float = 0.0,
) -> Dict:
    """
    Calculate complete Shadbala for all 7 planets.
    Returns individual bala components + total + financial interpretation.
    """
    results = {}
    asc_sign = ascendant["sign"]

    for planet_data in planets:
        name = planet_data["planet"]
        if name not in SHADBALA_PLANETS:
            continue

        longitude = planet_data["longitude"]
        sign = planet_data["sign"]
        speed = planet_data.get("speed", 0.0)
        retrograde = planet_data.get("retrograde", False)

        # 1. Sthana Bala (Positional)
        sthana = _calc_sthana_bala(name, longitude, sign, planets, asc_sign)

        # 2. Dig Bala (Directional)
        dig = _calc_dig_bala(name, sign, asc_sign)

        # 3. Kala Bala (Temporal)
        kala = _calc_kala_bala(name, birth_datetime, longitude)

        # 4. Cheshta Bala (Motional)
        cheshta = _calc_cheshta_bala(name, speed, retrograde)

        # 5. Naisargika Bala (Natural)
        naisargika = _calc_naisargika_bala(name)

        # 6. Drig Bala (Aspectual)
        drig = _calc_drig_bala(name, planets, asc_sign)

        total_virupas = (
            sthana["virupas"] + dig["virupas"] + kala["virupas"] +
            cheshta["virupas"] + naisargika["virupas"] + drig["virupas"]
        )
        total_rupas = round(total_virupas / 60, 2)
        required = REQUIRED_STRENGTH.get(name, 5.0)
        ratio = round(total_rupas / required, 2) if required > 0 else 0

        results[name] = {
            "planet": name,
            "sthana_bala": sthana,
            "dig_bala": dig,
            "kala_bala": kala,
            "cheshta_bala": cheshta,
            "naisargika_bala": naisargika,
            "drig_bala": drig,
            "total_virupas": round(total_virupas, 2),
            "total_rupas": total_rupas,
            "required_rupas": required,
            "strength_ratio": ratio,
            "is_strong": ratio >= 1.0,
            "strength_label": (
                "Very Strong" if ratio >= 1.5 else
                "Strong" if ratio >= 1.0 else
                "Moderate" if ratio >= 0.7 else
                "Weak" if ratio >= 0.5 else "Very Weak"
            ),
            "financial_impact": _financial_interpretation(name, ratio),
        }

    # Rank planets by strength
    ranked = sorted(results.values(), key=lambda x: -x["total_rupas"])
    strongest = ranked[0]["planet"] if ranked else ""
    weakest = ranked[-1]["planet"] if ranked else ""

    return {
        "type": "shadbala",
        "planets": results,
        "ranking": [{"planet": r["planet"], "rupas": r["total_rupas"],
                      "ratio": r["strength_ratio"]} for r in ranked],
        "strongest_planet": strongest,
        "weakest_planet": weakest,
        "strong_planets": [r["planet"] for r in ranked if r["is_strong"]],
        "weak_planets": [r["planet"] for r in ranked if not r["is_strong"]],
        "financial_summary": _financial_summary(results),
    }


# ─────────────────────────────────────────────────────────────
# 1. STHANA BALA (Positional Strength)
# Composed of: Uchcha Bala, Saptavargaja Bala, Ojhayugma Bala,
# Kendradi Bala, Drekkana Bala
# ─────────────────────────────────────────────────────────────

def _calc_sthana_bala(
    name: str, longitude: float, sign: str,
    planets: List[Dict], asc_sign: str,
) -> Dict:
    # a) Uchcha Bala (Exaltation strength)
    uchcha = _uchcha_bala(name, longitude)

    # b) Saptavargaja Bala (Dignity in 7 divisional charts - simplified)
    sapta = _saptavargaja_bala(name, sign)

    # c) Ojhayugma Bala (Odd/Even sign-planet match)
    ojha = _ojhayugma_bala(name, sign)

    # d) Kendradi Bala (Kendra/Panaphara/Apoklima)
    kendradi = _kendradi_bala(name, sign, asc_sign)

    # e) Drekkana Bala (Male/Female/Neutral decanate)
    drekkana = _drekkana_bala(name, longitude)

    total = uchcha + sapta + ojha + kendradi + drekkana
    return {
        "virupas": round(total, 2),
        "rupas": round(total / 60, 2),
        "components": {
            "uchcha_bala": round(uchcha, 2),
            "saptavargaja_bala": round(sapta, 2),
            "ojhayugma_bala": round(ojha, 2),
            "kendradi_bala": round(kendradi, 2),
            "drekkana_bala": round(drekkana, 2),
        },
    }


def _uchcha_bala(name: str, longitude: float) -> float:
    """Exaltation strength: max 60 virupas at exact exaltation, 0 at debilitation."""
    exalt_sign = EXALTATION.get(name)
    exalt_deg = EXALTATION_DEGREE.get(name, 0)
    if exalt_sign is None:
        return 30.0  # default for nodes

    exalt_long = SIGN_IDX.get(exalt_sign, 0) * 30 + exalt_deg
    diff = abs(longitude - exalt_long)
    if diff > 180:
        diff = 360 - diff
    return round(60.0 * (1.0 - diff / 180.0), 2)


def _saptavargaja_bala(name: str, sign: str) -> float:
    """Simplified: check dignity in rasi chart. Exalted=30, Own=22.5, Moola=15, Friend=7.5, Neutral=3.75, Enemy=1.875"""
    if sign == EXALTATION.get(name):
        return 30.0
    mt = MOOLATRIKONA.get(name)
    if mt and sign == mt[0]:
        return 22.5
    if sign in OWN_SIGNS.get(name, []):
        return 20.0
    lord = SIGN_LORDS.get(sign, "")
    friends_data = NATURAL_FRIENDS.get(name, {})
    if lord in friends_data.get("friends", []):
        return 15.0
    if lord in friends_data.get("neutral", []):
        return 7.5
    if lord in friends_data.get("enemies", []):
        return 3.75
    if sign == DEBILITATION.get(name):
        return 1.875
    return 7.5


def _ojhayugma_bala(name: str, sign: str) -> float:
    """Odd/Even sign placement strength."""
    sign_idx = SIGN_IDX.get(sign, 0)
    is_odd = sign_idx % 2 == 0  # Aries=0 is odd in Jyotish
    # Sun, Mars, Jupiter prefer odd; Moon, Venus, Saturn prefer even
    odd_preferred = {"Sun", "Mars", "Jupiter"}
    even_preferred = {"Moon", "Venus", "Saturn"}
    if name in odd_preferred and is_odd:
        return 15.0
    if name in even_preferred and not is_odd:
        return 15.0
    if name == "Mercury":
        return 15.0  # Mercury is comfortable everywhere
    return 0.0


def _kendradi_bala(name: str, sign: str, asc_sign: str) -> float:
    """Kendra=60, Panaphara=30, Apoklima=15."""
    asc_idx = SIGN_IDX.get(asc_sign, 0)
    sign_idx = SIGN_IDX.get(sign, 0)
    house = ((sign_idx - asc_idx) % 12) + 1
    if house in (1, 4, 7, 10):
        return 60.0
    if house in (2, 5, 8, 11):
        return 30.0
    return 15.0


def _drekkana_bala(name: str, longitude: float) -> float:
    """Male planets strong in 1st drekkana, neutral in 2nd, female in 3rd."""
    deg_in_sign = longitude % 30
    decanate = int(deg_in_sign / 10)  # 0, 1, 2
    male = {"Sun", "Mars", "Jupiter"}
    female = {"Moon", "Venus", "Saturn"}
    if name in male and decanate == 0:
        return 15.0
    if name in female and decanate == 2:
        return 15.0
    if name == "Mercury" and decanate == 1:
        return 15.0
    return 0.0


# ─────────────────────────────────────────────────────────────
# 2. DIG BALA (Directional Strength)
# ─────────────────────────────────────────────────────────────

def _calc_dig_bala(name: str, sign: str, asc_sign: str) -> Dict:
    """Max 60 virupas when planet is in its dig bala house, 0 at opposite."""
    best_house = DIG_BALA_HOUSE.get(name, 1)
    asc_idx = SIGN_IDX.get(asc_sign, 0)
    sign_idx = SIGN_IDX.get(sign, 0)
    actual_house = ((sign_idx - asc_idx) % 12) + 1

    # Distance from ideal house (circular)
    diff = abs(actual_house - best_house)
    if diff > 6:
        diff = 12 - diff
    virupas = round(60.0 * (1.0 - diff / 6.0), 2)
    return {"virupas": virupas, "rupas": round(virupas / 60, 2),
            "best_house": best_house, "actual_house": actual_house}


# ─────────────────────────────────────────────────────────────
# 3. KALA BALA (Temporal Strength)
# Simplified: Nathonnatha + Paksha + Tribhaga + Abda/Masa/Vara/Hora
# ─────────────────────────────────────────────────────────────

def _calc_kala_bala(name: str, dt: datetime, longitude: float) -> Dict:
    """Temporal strength based on time of birth."""
    # Nathonnatha Bala (day/night)
    hour = dt.hour + dt.minute / 60.0
    is_day = 6.0 <= hour < 18.0
    day_planets = {"Sun", "Jupiter", "Venus"}
    night_planets = {"Moon", "Mars", "Saturn"}
    if name in day_planets:
        nathonnatha = 60.0 if is_day else 0.0
    elif name in night_planets:
        nathonnatha = 0.0 if is_day else 60.0
    else:  # Mercury
        nathonnatha = 60.0  # Always strong

    # Paksha Bala (waxing/waning moon)
    paksha = 30.0  # simplified default

    # Tribhaga Bala (time of day)
    tribhaga = 15.0  # simplified

    # Vara Bala (day of week)
    weekday = dt.weekday()  # Monday=0
    vara_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    vara_lord = vara_lords[weekday]
    vara = 45.0 if name == vara_lord else 0.0

    # Hora Bala
    hora = 15.0 if name == vara_lord else 0.0

    total = nathonnatha + paksha + tribhaga + vara + hora
    return {
        "virupas": round(total, 2), "rupas": round(total / 60, 2),
        "components": {
            "nathonnatha": round(nathonnatha, 2),
            "paksha": round(paksha, 2),
            "tribhaga": round(tribhaga, 2),
            "vara": round(vara, 2),
            "hora": round(hora, 2),
        },
    }


# ─────────────────────────────────────────────────────────────
# 4. CHESHTA BALA (Motional Strength)
# Based on planetary speed — retrograde, stationary, direct
# ─────────────────────────────────────────────────────────────

MEAN_DAILY_MOTION = {
    "Sun": 0.9856, "Moon": 13.1764, "Mars": 0.5240, "Mercury": 1.3833,
    "Jupiter": 0.0831, "Venus": 1.2000, "Saturn": 0.0335,
}

def _calc_cheshta_bala(name: str, speed: float, retrograde: bool) -> Dict:
    """Motional strength: fast=strong, retro=moderate, stationary=weak."""
    mean = MEAN_DAILY_MOTION.get(name, 1.0)

    if name in ("Sun", "Moon"):
        # Sun/Moon never retrograde — speed ratio
        ratio = abs(speed) / mean if mean > 0 else 1.0
        virupas = min(60.0, ratio * 30.0)
    else:
        if retrograde:
            virupas = 30.0  # Retrograde = moderate strength
        elif abs(speed) < 0.01:
            virupas = 15.0  # Stationary = least strength
        else:
            ratio = abs(speed) / mean if mean > 0 else 1.0
            virupas = min(60.0, ratio * 40.0)

    return {"virupas": round(virupas, 2), "rupas": round(virupas / 60, 2),
            "speed": speed, "retrograde": retrograde}


# ─────────────────────────────────────────────────────────────
# 5. NAISARGIKA BALA (Natural Strength)
# Fixed values per Parashara — Sun strongest, Saturn weakest
# ─────────────────────────────────────────────────────────────

NAISARGIKA_VALUES = {
    "Sun": 60.0, "Moon": 51.43, "Mars": 17.14, "Mercury": 25.71,
    "Jupiter": 34.28, "Venus": 42.86, "Saturn": 8.57,
}

def _calc_naisargika_bala(name: str) -> Dict:
    virupas = NAISARGIKA_VALUES.get(name, 20.0)
    return {"virupas": virupas, "rupas": round(virupas / 60, 2)}


# ─────────────────────────────────────────────────────────────
# 6. DRIG BALA (Aspectual Strength)
# Benefic aspects add strength, malefic aspects reduce
# ─────────────────────────────────────────────────────────────

def _calc_drig_bala(name: str, planets: List[Dict], asc_sign: str) -> Dict:
    """Aspectual strength from benefic/malefic aspects."""
    sign = None
    for p in planets:
        if p["planet"] == name:
            sign = p["sign"]
            break
    if sign is None:
        return {"virupas": 0, "rupas": 0}

    sign_idx = SIGN_IDX.get(sign, 0)
    total = 0.0
    benefics = {"Jupiter", "Venus", "Mercury", "Moon"}
    malefics = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

    for p in planets:
        if p["planet"] == name:
            continue
        p_sign_idx = SIGN_IDX.get(p["sign"], 0)
        diff = (p_sign_idx - sign_idx) % 12

        # Full aspect at 7th house distance
        aspect_strength = 0.0
        if diff == 6:
            aspect_strength = 60.0
        elif diff in (3, 9):
            aspect_strength = 30.0
        elif diff in (4, 8):
            aspect_strength = 15.0
        # Special aspects
        if p["planet"] == "Mars" and diff in (3, 7):
            aspect_strength = max(aspect_strength, 45.0)
        if p["planet"] == "Jupiter" and diff in (4, 8):
            aspect_strength = max(aspect_strength, 45.0)
        if p["planet"] == "Saturn" and diff in (2, 9):
            aspect_strength = max(aspect_strength, 45.0)

        if aspect_strength > 0:
            if p["planet"] in benefics:
                total += aspect_strength / 4
            elif p["planet"] in malefics:
                total -= aspect_strength / 4

    virupas = max(0, min(60, total))
    return {"virupas": round(virupas, 2), "rupas": round(virupas / 60, 2)}


# ─────────────────────────────────────────────────────────────
# Financial Interpretation
# ─────────────────────────────────────────────────────────────

def _financial_interpretation(name: str, ratio: float) -> Dict:
    """Map Shadbala strength to NSE/BSE sector confidence."""
    sectors = FINANCIAL_KARAKAS.get(name, "")
    if ratio >= 1.5:
        return {
            "signal": "VERY STRONG",
            "sectors": sectors,
            "confidence": "HIGH",
            "action": f"STRONG BUY for {name}-ruled sectors: {sectors}",
            "score": 0.90,
        }
    if ratio >= 1.0:
        return {
            "signal": "STRONG",
            "sectors": sectors,
            "confidence": "MODERATE-HIGH",
            "action": f"BUY for {name}-ruled sectors: {sectors}",
            "score": 0.65,
        }
    if ratio >= 0.7:
        return {
            "signal": "MODERATE",
            "sectors": sectors,
            "confidence": "MODERATE",
            "action": f"HOLD for {name}-ruled sectors: {sectors}",
            "score": 0.30,
        }
    if ratio >= 0.5:
        return {
            "signal": "WEAK",
            "sectors": sectors,
            "confidence": "LOW",
            "action": f"REDUCE exposure to {name}-ruled sectors",
            "score": -0.20,
        }
    return {
        "signal": "VERY WEAK",
        "sectors": sectors,
        "confidence": "VERY LOW",
        "action": f"AVOID {name}-ruled sectors: {sectors}",
        "score": -0.50,
    }


def _financial_summary(results: Dict) -> Dict:
    """Generate overall financial summary from Shadbala."""
    strong_sectors = []
    weak_sectors = []
    total_score = 0.0
    count = 0

    for name, data in results.items():
        fi = data["financial_impact"]
        score = fi["score"]
        total_score += score
        count += 1
        if score > 0.3:
            strong_sectors.append(fi["sectors"])
        elif score < -0.1:
            weak_sectors.append(fi["sectors"])

    avg = total_score / count if count > 0 else 0
    if avg >= 0.5:
        outlook = "STRONGLY BULLISH — Multiple planets have high Shadbala"
    elif avg >= 0.2:
        outlook = "BULLISH — Planetary strength supports market growth"
    elif avg >= 0:
        outlook = "NEUTRAL — Mixed planetary strength signals"
    elif avg >= -0.3:
        outlook = "CAUTIOUS — Weak planetary strength in key areas"
    else:
        outlook = "BEARISH — Widespread planetary weakness"

    return {
        "avg_score": round(avg, 3),
        "outlook": outlook,
        "strong_sectors": strong_sectors,
        "weak_sectors": weak_sectors,
    }


# ─────────────────────────────────────────────────────────────
# Bhava Chalit Chart
# ─────────────────────────────────────────────────────────────

def calculate_bhava_chalit(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
) -> Dict:
    """
    Bhava Chalit Chart — shows actual house placement vs sign placement.
    Uses mid-point (Bhava Madhya) system where house cusp is the midpoint.
    Critical for financial astrology: a planet may be in Taurus by sign
    but in the 1st house by Bhava Chalit — different financial implications.
    """
    asc_long = ascendant["longitude"]

    # Calculate Bhava Madhya (midpoints) and Bhava Sandhi (boundaries)
    bhava_madhya = []
    bhava_sandhi = []
    for i in range(12):
        cusp = houses[i]["longitude"]
        next_cusp = houses[(i + 1) % 12]["longitude"]
        bhava_madhya.append(cusp)

        # Sandhi = midpoint between this cusp and next
        if next_cusp > cusp:
            sandhi = (cusp + next_cusp) / 2
        else:
            sandhi = ((cusp + next_cusp + 360) / 2) % 360
        bhava_sandhi.append(sandhi)

    # Place planets in Bhavas
    chalit_planets = []
    for p in planets:
        p_long = p["longitude"]
        rasi_sign = p["sign"]
        rasi_house = _get_house_from_sign(rasi_sign, ascendant["sign"])
        bhava_house = _find_bhava(p_long, bhava_sandhi)

        shifted = bhava_house != rasi_house
        chalit_planets.append({
            "planet": p["planet"],
            "longitude": p["longitude"],
            "rasi_sign": rasi_sign,
            "rasi_house": rasi_house,
            "bhava_house": bhava_house,
            "shifted": shifted,
            "shift_note": (
                f"{p['planet']} shifts from {rasi_house}th to {bhava_house}th house in Bhava Chalit"
                if shifted else f"{p['planet']} stays in {rasi_house}th house"
            ),
            "financial_note": _bhava_financial_note(p["planet"], bhava_house, shifted),
        })

    shifted_planets = [p for p in chalit_planets if p["shifted"]]

    return {
        "type": "bhava_chalit",
        "bhava_madhya": [{"house": i + 1, "longitude": round(bhava_madhya[i], 4),
                          } for i in range(12)],
        "bhava_sandhi": [{"boundary": i + 1, "longitude": round(bhava_sandhi[i], 4),
                          } for i in range(12)],
        "planets": chalit_planets,
        "shifted_planets": shifted_planets,
        "shift_count": len(shifted_planets),
        "financial_impact": (
            "Significant Bhava Chalit shifts — use Chalit houses for prediction"
            if len(shifted_planets) >= 3
            else "Minor shifts — Rasi chart placements mostly valid"
        ),
    }


def _get_house_from_sign(sign: str, asc_sign: str) -> int:
    asc_idx = SIGN_IDX.get(asc_sign, 0)
    sign_idx = SIGN_IDX.get(sign, 0)
    return ((sign_idx - asc_idx) % 12) + 1


def _find_bhava(longitude: float, sandhi_points: List[float]) -> int:
    """Find which Bhava a planet falls in based on Sandhi boundaries."""
    for i in range(12):
        start = sandhi_points[i - 1] if i > 0 else sandhi_points[11]
        end = sandhi_points[i]
        if start < end:
            if start <= longitude < end:
                return i + 1
        else:  # wraps around 360
            if longitude >= start or longitude < end:
                return i + 1
    return 1  # fallback


def _bhava_financial_note(planet: str, house: int, shifted: bool) -> str:
    """Financial significance of Bhava Chalit house placement."""
    wealth_houses = {2, 5, 9, 11}
    loss_houses = {6, 8, 12}
    power_houses = {1, 4, 7, 10}

    if house in wealth_houses:
        return f"{planet} in {house}th Bhava — directly impacts wealth/income"
    if house in power_houses:
        return f"{planet} in {house}th Bhava — Kendra placement strengthens career/authority"
    if house in loss_houses:
        return f"{planet} in {house}th Bhava — challenges in financial matters"
    return f"{planet} in {house}th Bhava"
