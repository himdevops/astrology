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

References: BPHS Ch.27, Surya Siddhanta, Parashara's Light methodology.
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


# ─────────────────────────────────────────────────────────────
# Divisional Chart Calculation (Varga)
# Needed for Saptavargaja Bala — check dignity in 7 vargas
# ─────────────────────────────────────────────────────────────

def _varga_sign(longitude: float, varga: int) -> str:
    """
    Calculate which sign a planet falls in for a given divisional chart.
    varga=1: Rasi, 2: Hora, 3: Drekkana, 4: Chaturthamsa,
    7: Saptamsa, 9: Navamsa, 10: Dashamsa
    """
    deg = longitude % 360.0
    sign_idx = int(deg // 30)
    deg_in_sign = deg % 30

    if varga == 1:
        # Rasi — same as rasi chart
        return SIGNS[sign_idx]

    elif varga == 2:
        # Hora — 0-15° = Sun's hora (Leo), 15-30° = Moon's hora (Cancer)
        # Odd signs: 0-15 Sun, 15-30 Moon; Even signs: reversed
        is_odd = sign_idx % 2 == 0  # Aries=0 is odd sign #1
        if is_odd:
            return "Leo" if deg_in_sign < 15 else "Cancer"
        else:
            return "Cancer" if deg_in_sign < 15 else "Leo"

    elif varga == 3:
        # Drekkana — each sign divided into 3 parts of 10°
        decanate = int(deg_in_sign // 10)
        # 1st: same sign, 2nd: 5th from sign, 3rd: 9th from sign
        offsets = [0, 4, 8]
        return SIGNS[(sign_idx + offsets[decanate]) % 12]

    elif varga == 4:
        # Chaturthamsa — each sign divided into 4 parts of 7.5°
        quarter = int(deg_in_sign // 7.5)
        quarter = min(quarter, 3)
        return SIGNS[(sign_idx + quarter * 3) % 12]

    elif varga == 7:
        # Saptamsa — each sign divided into 7 parts of 4.2857°
        part = int(deg_in_sign / (30.0 / 7))
        part = min(part, 6)
        # Odd signs: start from same sign; Even signs: start from 7th
        if sign_idx % 2 == 0:  # Odd rasi
            return SIGNS[(sign_idx + part) % 12]
        else:  # Even rasi
            return SIGNS[(sign_idx + 6 + part) % 12]

    elif varga == 9:
        # Navamsa — each sign divided into 9 parts of 3.333°
        part = int(deg_in_sign / (30.0 / 9))
        part = min(part, 8)
        # Fire signs start from Aries, Earth from Cap, Air from Libra, Water from Cancer
        fire_start = [0, 9, 6, 3]  # Aries=0, Cap=9, Libra=6, Cancer=3
        element = sign_idx % 4  # 0=Fire, 1=Earth, 2=Air, 3=Water
        start = fire_start[element]
        return SIGNS[(start + part) % 12]

    elif varga == 10:
        # Dashamsa — each sign divided into 10 parts of 3°
        part = int(deg_in_sign // 3)
        part = min(part, 9)
        # Odd signs: start from same sign; Even signs: start from 9th sign
        if sign_idx % 2 == 0:  # Odd rasi
            return SIGNS[(sign_idx + part) % 12]
        else:  # Even rasi
            return SIGNS[(sign_idx + 8 + part) % 12]

    return SIGNS[sign_idx]  # fallback to rasi


def _dignity_score(name: str, sign: str) -> float:
    """
    Return dignity virupas for a planet in a given sign.
    Per BPHS Saptavargaja:
      Exalted: 20, Moolatrikona: 15, Own: 12, Friendly: 7.5,
      Neutral: 3.75, Enemy: 1.875, Debilitated: 1.875
    Note: Some texts use different scales; these follow standard Parashara.
    """
    # Check exaltation
    if sign == EXALTATION.get(name):
        return 20.0
    # Check debilitation first before friends
    if sign == DEBILITATION.get(name):
        return 1.875
    # Moolatrikona
    mt = MOOLATRIKONA.get(name)
    if mt and sign == mt[0]:
        return 15.0
    # Own sign
    if sign in OWN_SIGNS.get(name, []):
        return 12.0
    # Friendship with sign lord
    lord = SIGN_LORDS.get(sign, "")
    friends_data = NATURAL_FRIENDS.get(name, {})
    if lord in friends_data.get("friends", []):
        return 7.5
    if lord in friends_data.get("neutral", []):
        return 3.75
    if lord in friends_data.get("enemies", []):
        return 1.875
    return 3.75  # default neutral


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
    # Extract Sun and Moon longitudes for Kala Bala
    sun_long = 0.0
    moon_long = 0.0
    for p in planets:
        if p["planet"] == "Sun":
            sun_long = p["longitude"]
        elif p["planet"] == "Moon":
            moon_long = p["longitude"]

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
        kala = _calc_kala_bala(name, birth_datetime, longitude, sun_long, moon_long)

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

    # b) Saptavargaja Bala (Dignity across 7 divisional charts)
    sapta = _saptavargaja_bala(name, longitude, sign)

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


def _saptavargaja_bala(name: str, longitude: float, rasi_sign: str) -> float:
    """
    Check planet's dignity across 7 divisional charts (Sapta Varga):
    Rasi, Hora, Drekkana, Chaturthamsa, Saptamsha, Navamsa, Dashamsa.
    Sum the dignity virupas across all 7 vargas.
    Per BPHS: each varga contributes its own dignity score.
    """
    vargas = [1, 2, 3, 4, 7, 9, 10]
    total = 0.0
    for v in vargas:
        if v == 1:
            varga_sign = rasi_sign
        else:
            varga_sign = _varga_sign(longitude, v)
        total += _dignity_score(name, varga_sign)
    return round(total, 2)


def _ojhayugma_bala(name: str, sign: str) -> float:
    """
    Odd/Even sign placement strength.
    Sun, Mars, Jupiter prefer odd signs: 15 virupas
    Moon, Venus, Saturn prefer even signs: 15 virupas
    Mercury: 15 virupas in either.
    Non-preferred: 0 virupas.
    """
    sign_idx = SIGN_IDX.get(sign, 0)
    is_odd = sign_idx % 2 == 0  # Aries=0 is odd sign #1 in Jyotish
    odd_preferred = {"Sun", "Mars", "Jupiter"}
    even_preferred = {"Moon", "Venus", "Saturn"}
    if name in odd_preferred and is_odd:
        return 15.0
    if name in even_preferred and not is_odd:
        return 15.0
    if name == "Mercury":
        return 15.0
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
# Arc-based: 60 virupas at best house, 0 at 7th from it (opposite)
# Linear interpolation based on arc distance (BPHS standard)
# ─────────────────────────────────────────────────────────────

def _calc_dig_bala(name: str, sign: str, asc_sign: str) -> Dict:
    """
    Max 60 virupas when planet is in its dig bala house, 0 at opposite.
    Uses arc-based formula: virupas = 60 * (180 - arc) / 180
    where arc = angular distance between planet's house midpoint and
    the dig bala house midpoint, measured in degrees (30° per house).
    """
    best_house = DIG_BALA_HOUSE.get(name, 1)
    asc_idx = SIGN_IDX.get(asc_sign, 0)
    sign_idx = SIGN_IDX.get(sign, 0)
    actual_house = ((sign_idx - asc_idx) % 12) + 1

    # Arc distance in houses (0-6 range)
    diff = abs(actual_house - best_house)
    if diff > 6:
        diff = 12 - diff

    # Arc in degrees (each house = 30°)
    arc_deg = diff * 30.0
    virupas = round(60.0 * (180.0 - arc_deg) / 180.0, 2)
    virupas = max(0.0, virupas)

    return {"virupas": virupas, "rupas": round(virupas / 60, 2),
            "best_house": best_house, "actual_house": actual_house}


# ─────────────────────────────────────────────────────────────
# 3. KALA BALA (Temporal Strength)
# Components: Nathonnatha, Paksha, Tribhaga, Abda, Masa, Vara, Hora
# ─────────────────────────────────────────────────────────────

# Hora lord sequence (Chaldean order)
_HORA_SEQUENCE = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]
# Weekday start hora lord: Sun=Sunday, Moon=Monday, Mars=Tuesday, etc.
_WEEKDAY_HORA_START = {
    6: "Sun",       # Sunday (weekday() = 6)
    0: "Moon",      # Monday
    1: "Mars",      # Tuesday
    2: "Mercury",   # Wednesday
    3: "Jupiter",   # Thursday
    4: "Venus",     # Friday
    5: "Saturn",    # Saturday
}


def _calc_kala_bala(
    name: str, dt: datetime, longitude: float,
    sun_longitude: float, moon_longitude: float,
) -> Dict:
    """Temporal strength based on time of birth — proper BPHS calculation."""

    # ── Nathonnatha Bala ─────────────────────────────────────
    # Day planets (Sun, Jupiter, Venus) get strength during day
    # Night planets (Moon, Mars, Saturn) get strength at night
    # Mercury is always strong (sandhya planet)
    # Proportional: max 60 at noon/midnight, 0 at sunrise/sunset
    hour = dt.hour + dt.minute / 60.0

    # Approximate sunrise ~6:00, sunset ~18:00 (can be improved with lat/long)
    sunrise = 6.0
    sunset = 18.0

    day_planets = {"Sun", "Jupiter", "Venus"}
    night_planets = {"Moon", "Mars", "Saturn"}

    if name == "Mercury":
        nathonnatha = 60.0  # Mercury always strong (sandhya graha)
    elif name in day_planets:
        if sunrise <= hour < sunset:
            # Day time: proportional, max at noon
            noon = (sunrise + sunset) / 2.0
            dist_from_noon = abs(hour - noon)
            half_day = (sunset - sunrise) / 2.0
            nathonnatha = round(60.0 * (1.0 - dist_from_noon / half_day), 2)
        else:
            nathonnatha = 0.0
    elif name in night_planets:
        if hour >= sunset or hour < sunrise:
            # Night time: proportional, max at midnight
            if hour >= sunset:
                midnight_dist = abs(hour - 24.0)
            else:
                midnight_dist = hour
            half_night = (24.0 - sunset + sunrise) / 2.0
            nathonnatha = round(60.0 * (1.0 - midnight_dist / half_night), 2)
        else:
            nathonnatha = 0.0
    else:
        nathonnatha = 30.0  # fallback

    nathonnatha = max(0.0, min(60.0, nathonnatha))

    # ── Paksha Bala ──────────────────────────────────────────
    # Based on Moon's phase (Moon - Sun angle)
    # Shukla Paksha (waxing): benefics gain strength
    # Krishna Paksha (waning): malefics gain strength
    # Formula: tithi_angle = (Moon_long - Sun_long) % 360
    # Paksha Bala = tithi_angle / 3 for benefics (max 60 at Purnima)
    # Paksha Bala = (360 - tithi_angle) / 3 for malefics
    tithi_angle = (moon_longitude - sun_longitude) % 360.0
    benefics_paksha = {"Moon", "Mercury", "Jupiter", "Venus"}

    if name in benefics_paksha:
        # Benefics: strongest at Purnima (180°), weakest at Amavasya (0°/360°)
        if tithi_angle <= 180:
            paksha = round(tithi_angle / 3.0, 2)
        else:
            paksha = round((360.0 - tithi_angle) / 3.0, 2)
    else:
        # Malefics (Sun, Mars, Saturn): strongest at Amavasya, weakest at Purnima
        if tithi_angle <= 180:
            paksha = round((180.0 - tithi_angle) / 3.0, 2)
        else:
            paksha = round((tithi_angle - 180.0) / 3.0, 2)

    paksha = max(0.0, min(60.0, paksha))

    # ── Tribhaga Bala ────────────────────────────────────────
    # Day divided into 3 parts (each ~4 hrs from sunrise to sunset)
    # Night divided into 3 parts (each ~4 hrs from sunset to sunrise)
    # 1st third of day: Mercury; 2nd: Sun; 3rd: Saturn
    # 1st third of night: Moon; 2nd: Venus; 3rd: Mars
    # Jupiter gets Tribhaga strength always (per some texts)
    day_length = sunset - sunrise  # hours
    night_length = 24.0 - day_length

    tribhaga = 0.0
    if sunrise <= hour < sunset:
        # Daytime: which third?
        elapsed = hour - sunrise
        third = int(elapsed / (day_length / 3.0))
        third = min(third, 2)
        day_lords = ["Mercury", "Sun", "Saturn"]
        if name == day_lords[third]:
            tribhaga = 15.0
    else:
        # Nighttime: which third?
        if hour >= sunset:
            elapsed = hour - sunset
        else:
            elapsed = (24.0 - sunset) + hour
        third = int(elapsed / (night_length / 3.0))
        third = min(third, 2)
        night_lords = ["Moon", "Venus", "Mars"]
        if name == night_lords[third]:
            tribhaga = 15.0

    if name == "Jupiter":
        tribhaga = 15.0  # Jupiter always gets Tribhaga

    # ── Vara Bala (day of week lord) ─────────────────────────
    weekday = dt.weekday()  # Monday=0
    vara_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    vara_lord = vara_lords[weekday]
    vara = 45.0 if name == vara_lord else 0.0

    # ── Hora Bala (planetary hour lord) ──────────────────────
    # 24 horas per day, starting from sunrise with weekday lord
    # Each hora = 1 hour, cycling through Chaldean order
    hora_start_lord = _WEEKDAY_HORA_START.get(weekday, "Sun")
    start_idx = _HORA_SEQUENCE.index(hora_start_lord) if hora_start_lord in _HORA_SEQUENCE else 0

    # Hours since sunrise
    if hour >= sunrise:
        hours_since_sunrise = hour - sunrise
    else:
        hours_since_sunrise = (24.0 - sunrise) + hour

    hora_number = int(hours_since_sunrise) % 24
    hora_lord_idx = (start_idx + hora_number) % 7
    hora_lord = _HORA_SEQUENCE[hora_lord_idx]
    hora = 60.0 if name == hora_lord else 0.0

    # ── Abda Bala (year lord) ────────────────────────────────
    # Simplified: year lord based on weekday of year start
    # Per BPHS, year lord = lord of weekday on which the year's
    # first day of Chaitra falls. Approximated here.
    year_start = datetime(dt.year, 1, 1)
    year_weekday = year_start.weekday()
    year_lord = vara_lords[year_weekday]
    abda = 15.0 if name == year_lord else 0.0

    # ── Masa Bala (month lord) ───────────────────────────────
    month_start = datetime(dt.year, dt.month, 1)
    month_weekday = month_start.weekday()
    month_lord = vara_lords[month_weekday]
    masa = 30.0 if name == month_lord else 0.0

    total = nathonnatha + paksha + tribhaga + vara + hora + abda + masa
    return {
        "virupas": round(total, 2), "rupas": round(total / 60, 2),
        "components": {
            "nathonnatha": round(nathonnatha, 2),
            "paksha": round(paksha, 2),
            "tribhaga": round(tribhaga, 2),
            "vara": round(vara, 2),
            "hora": round(hora, 2),
            "abda": round(abda, 2),
            "masa": round(masa, 2),
        },
    }


# ─────────────────────────────────────────────────────────────
# 4. CHESHTA BALA (Motional Strength)
# Based on planetary speed — 8 states per BPHS
# ─────────────────────────────────────────────────────────────

MEAN_DAILY_MOTION = {
    "Sun": 0.9856, "Moon": 13.1764, "Mars": 0.5240, "Mercury": 1.3833,
    "Jupiter": 0.0831, "Venus": 1.2000, "Saturn": 0.0335,
}

# BPHS defines 8 types of planetary motion (Cheshta):
# 1. Vakra (Retrograde) = 60 virupas
# 2. Anuvakra (Entering retrograde) = 30 virupas
# 3. Vikala (Stationary) = 15 virupas
# 4. Manda (Slow direct) = 15 virupas
# 5. Mandatara (Very slow) = 7.5 virupas
# 6. Sama (Mean motion) = 30 virupas
# 7. Chara (Fast) = 45 virupas
# 8. Atichara (Very fast) = 30 virupas


def _calc_cheshta_bala(name: str, speed: float, retrograde: bool) -> Dict:
    """
    Motional strength per BPHS 8-state system.
    Sun and Moon use simple speed ratio (they never retrograde).
    """
    mean = MEAN_DAILY_MOTION.get(name, 1.0)
    state = "Direct"

    if name in ("Sun", "Moon"):
        # Sun/Moon never retrograde — strength proportional to speed
        ratio = abs(speed) / mean if mean > 0 else 1.0
        if ratio >= 1.3:
            virupas = 30.0  # Atichara (too fast)
            state = "Atichara"
        elif ratio >= 1.1:
            virupas = 45.0  # Chara (fast)
            state = "Chara"
        elif ratio >= 0.9:
            virupas = 30.0  # Sama (mean motion)
            state = "Sama"
        elif ratio >= 0.5:
            virupas = 15.0  # Manda (slow)
            state = "Manda"
        else:
            virupas = 7.5   # Mandatara (very slow)
            state = "Mandatara"
    else:
        if retrograde:
            # True retrograde: check speed magnitude
            retro_ratio = abs(speed) / mean if mean > 0 else 0
            if retro_ratio >= 0.5:
                virupas = 60.0  # Vakra (full retrograde motion)
                state = "Vakra"
            else:
                virupas = 30.0  # Anuvakra (entering/leaving retrograde)
                state = "Anuvakra"
        elif abs(speed) < mean * 0.05:
            virupas = 15.0  # Vikala (stationary)
            state = "Vikala"
        else:
            ratio = abs(speed) / mean if mean > 0 else 1.0
            if ratio >= 1.3:
                virupas = 30.0  # Atichara
                state = "Atichara"
            elif ratio >= 1.1:
                virupas = 45.0  # Chara
                state = "Chara"
            elif ratio >= 0.9:
                virupas = 30.0  # Sama
                state = "Sama"
            elif ratio >= 0.5:
                virupas = 15.0  # Manda
                state = "Manda"
            else:
                virupas = 7.5   # Mandatara
                state = "Mandatara"

    return {"virupas": round(virupas, 2), "rupas": round(virupas / 60, 2),
            "speed": speed, "retrograde": retrograde, "motion_state": state}


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
# Per BPHS: aspect strength based on Graha Drishti values
# ─────────────────────────────────────────────────────────────

# Graha Drishti (planetary aspect) values in virupas
# Every planet has full (60) aspect on 7th house
# Partial aspects on 3rd, 4th, 8th, 10th houses
# Plus special aspects for Mars, Jupiter, Saturn
STANDARD_ASPECTS = {
    3: 15.0,   # 3rd house: quarter aspect
    4: 45.0,   # 4th house: three-quarter aspect
    5: 7.5,    # 5th house: one-eighth aspect
    8: 45.0,   # 8th house: three-quarter aspect
    9: 15.0,   # 9th house: quarter aspect
    10: 7.5,   # 10th house: one-eighth aspect
}

# Special full aspects (60 virupas)
SPECIAL_ASPECTS = {
    "Mars":    {4, 8},       # Mars: full aspect on 4th and 8th (in addition to 7th)
    "Jupiter": {5, 9},       # Jupiter: full aspect on 5th and 9th
    "Saturn":  {3, 10},      # Saturn: full aspect on 3rd and 10th
}


def _calc_drig_bala(name: str, planets: List[Dict], asc_sign: str) -> Dict:
    """
    Aspectual strength from benefic/malefic aspects.
    Benefic aspects add virupas, malefic aspects subtract.
    Uses Graha Drishti values per BPHS.
    """
    sign = None
    for p in planets:
        if p["planet"] == name:
            sign = p["sign"]
            break
    if sign is None:
        return {"virupas": 0, "rupas": 0}

    sign_idx = SIGN_IDX.get(sign, 0)
    total = 0.0
    benefics = {"Jupiter", "Venus"}
    # Moon is benefic when waxing (simplified: always benefic for aspects)
    # Mercury is benefic when alone or with benefics (simplified: benefic)
    conditional_benefics = {"Moon", "Mercury"}
    malefics = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

    for p in planets:
        pname = p["planet"]
        if pname == name or pname in ("Rahu", "Ketu"):
            # Skip self; Rahu/Ketu don't cast Graha Drishti in standard BPHS
            continue
        p_sign_idx = SIGN_IDX.get(p["sign"], 0)
        diff = (p_sign_idx - sign_idx) % 12

        if diff == 0:
            continue  # Same sign = conjunction, not aspect

        # Get aspect strength
        aspect_strength = 0.0

        if diff == 6:
            # 7th house: full aspect for all planets
            aspect_strength = 60.0
        elif diff in STANDARD_ASPECTS:
            aspect_strength = STANDARD_ASPECTS[diff]

        # Special aspects override to full (60)
        special = SPECIAL_ASPECTS.get(pname, set())
        if (diff + 1) in special:
            # diff is 0-indexed house distance, special aspects use 1-indexed
            # diff=3 means 4th house, diff=7 means 8th house, etc.
            pass
        # Correct: diff=3 means planet in 4th from target... actually:
        # diff = (p_sign_idx - sign_idx) % 12 means p is 'diff+1'th house from target
        # Actually no: if p is in sign_idx+6, diff=6 which is 7th house. So diff+1 = house number.
        house_from = diff + 1 if diff > 0 else 12
        if house_from in special:
            aspect_strength = 60.0

        if aspect_strength > 0:
            # Determine if aspecting planet is benefic or malefic
            if pname in benefics:
                total += aspect_strength / 4.0
            elif pname in conditional_benefics:
                total += aspect_strength / 4.0  # Treat as benefic
            elif pname in malefics:
                total -= aspect_strength / 4.0

    # Drig Bala can be negative (net malefic aspects)
    # Per BPHS, it's clamped to 0 minimum for total Shadbala
    virupas = max(-60.0, min(60.0, total))
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
