"""
dasha.py — Dasha (Planetary Period) calculation systems.
=========================================================
Supports:
  1. Vimshottari Dasha  (120 years, nakshatra-based)
  2. Yogini Dasha       (36 years, nakshatra-based)
  3. Ashtottari Dasha   (108 years, nakshatra-based)
  4. Chara Dasha        (Jaimini sign-based)
  5. Narayana Dasha     (Jaimini sign-based)

Each nakshatra-based system supports 5 levels:
  Mahadasha → Antardasha → Pratyantardasha → Sookshma → Prana

Sign-based systems (Chara, Narayana) have Dasha → Antardasha (2 levels).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import List, Dict, Any

from core.constants import (
    NAKSHATRA_SPAN, SIGNS, SIGN_LORDS,
    NAKSHATRA_LORDS, NAKSHATRAS_27,
)


# ═══════════════════════════════════════════════════════════════
# 1. VIMSHOTTARI DASHA (120 years)
# ═══════════════════════════════════════════════════════════════

VIMSHOTTARI_SEQUENCE = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
]

VIMSHOTTARI_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}

VIMSHOTTARI_TOTAL = 120.0


def _calc_nakshatra_balance(moon_lon: float) -> tuple:
    """
    Calculate nakshatra index and remaining fraction.
    Returns (nakshatra_index, fraction_remaining).
    fraction_remaining = how much of the nakshatra is left (0.0–1.0).
    """
    nak_idx = int(moon_lon / NAKSHATRA_SPAN) % 27
    deg_in_nak = moon_lon - (nak_idx * NAKSHATRA_SPAN)
    fraction_elapsed = deg_in_nak / NAKSHATRA_SPAN
    fraction_remaining = 1.0 - fraction_elapsed
    return nak_idx, fraction_remaining


def _build_period_tree(
    start_dt: datetime,
    lord: str,
    total_days: float,
    sequence: list,
    years_map: dict,
    total_years: float,
    level: int,
    max_level: int,
    level_names: list,
) -> Dict[str, Any]:
    """
    Recursively build a dasha period node with sub-periods.
    """
    end_dt = start_dt + timedelta(days=total_days)
    node = {
        "lord": lord,
        "level": level_names[level] if level < len(level_names) else f"Level-{level+1}",
        "start": start_dt.strftime("%d-%m-%Y"),
        "end": end_dt.strftime("%d-%m-%Y"),
        "start_dt": start_dt,
        "end_dt": end_dt,
        "duration_days": round(total_days, 2),
        "duration_years": round(total_days / 365.25, 4),
    }

    if level < max_level - 1:
        # Build sub-periods
        sub_periods = []
        lord_idx = sequence.index(lord)
        cursor = start_dt

        for i in range(len(sequence)):
            sub_lord = sequence[(lord_idx + i) % len(sequence)]
            sub_fraction = years_map[sub_lord] / total_years
            sub_days = total_days * sub_fraction

            sub_node = _build_period_tree(
                cursor, sub_lord, sub_days,
                sequence, years_map, total_years,
                level + 1, max_level, level_names,
            )
            sub_periods.append(sub_node)
            cursor = cursor + timedelta(days=sub_days)

        node["sub_periods"] = sub_periods

    return node


def calc_vimshottari(
    moon_lon: float,
    birth_dt: datetime,
    max_level: int = 5,
) -> Dict[str, Any]:
    """
    Calculate Vimshottari Dasha from Moon's sidereal longitude at birth.

    Parameters:
        moon_lon:  Sidereal longitude of Moon (0–360)
        birth_dt:  Datetime of birth (local)
        max_level: Depth of sub-periods (1–5)

    Returns:
        Dict with system info, current dasha, and full period tree.
    """
    nak_idx, balance_fraction = _calc_nakshatra_balance(moon_lon)
    nak_lord = NAKSHATRA_LORDS[nak_idx]
    nakshatra_name = NAKSHATRAS_27[nak_idx]

    # First Mahadasha lord = nakshatra lord, with remaining balance
    lord_idx = VIMSHOTTARI_SEQUENCE.index(nak_lord)

    level_names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma", "Prana"]
    periods = []
    cursor = birth_dt

    for i in range(9):
        lord = VIMSHOTTARI_SEQUENCE[(lord_idx + i) % 9]
        full_days = VIMSHOTTARI_YEARS[lord] * 365.25

        if i == 0:
            # First dasha: only the remaining balance
            dasha_days = full_days * balance_fraction
        else:
            dasha_days = full_days

        period = _build_period_tree(
            cursor, lord, dasha_days,
            VIMSHOTTARI_SEQUENCE, VIMSHOTTARI_YEARS,
            VIMSHOTTARI_TOTAL, 0, max_level, level_names,
        )
        periods.append(period)
        cursor = cursor + timedelta(days=dasha_days)

    # Clean up internal datetime objects
    _strip_dt_objects(periods)

    return {
        "system": "Vimshottari",
        "total_years": 120,
        "birth_nakshatra": nakshatra_name,
        "birth_nakshatra_lord": nak_lord,
        "balance": round(balance_fraction * VIMSHOTTARI_YEARS[nak_lord], 4),
        "balance_unit": "years",
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════
# 2. YOGINI DASHA (36 years)
# ═══════════════════════════════════════════════════════════════

YOGINI_SEQUENCE = [
    "Mangala", "Pingala", "Dhanya", "Bhramari",
    "Bhadrika", "Ulka", "Siddha", "Sankata",
]

YOGINI_YEARS = {
    "Mangala": 1, "Pingala": 2, "Dhanya": 3, "Bhramari": 4,
    "Bhadrika": 5, "Ulka": 6, "Siddha": 7, "Sankata": 8,
}

YOGINI_PLANET = {
    "Mangala": "Moon", "Pingala": "Sun", "Dhanya": "Jupiter",
    "Bhramari": "Mars", "Bhadrika": "Mercury", "Ulka": "Saturn",
    "Siddha": "Venus", "Sankata": "Rahu",
}

YOGINI_TOTAL = 36.0


def calc_yogini(
    moon_lon: float,
    birth_dt: datetime,
    max_level: int = 5,
) -> Dict[str, Any]:
    """Calculate Yogini Dasha from Moon's longitude."""
    nak_idx, balance_fraction = _calc_nakshatra_balance(moon_lon)
    nakshatra_name = NAKSHATRAS_27[nak_idx]

    # Yogini lord = (nakshatra_index + 3) % 8
    yogini_idx = (nak_idx + 3) % 8
    first_lord = YOGINI_SEQUENCE[yogini_idx]

    level_names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma", "Prana"]
    periods = []
    cursor = birth_dt

    for i in range(8):
        lord = YOGINI_SEQUENCE[(yogini_idx + i) % 8]
        full_days = YOGINI_YEARS[lord] * 365.25

        if i == 0:
            dasha_days = full_days * balance_fraction
        else:
            dasha_days = full_days

        period = _build_period_tree(
            cursor, lord, dasha_days,
            YOGINI_SEQUENCE, YOGINI_YEARS,
            YOGINI_TOTAL, 0, max_level, level_names,
        )
        # Add ruling planet info
        period["ruling_planet"] = YOGINI_PLANET[lord]
        periods.append(period)
        cursor = cursor + timedelta(days=dasha_days)

    _strip_dt_objects(periods)

    return {
        "system": "Yogini",
        "total_years": 36,
        "birth_nakshatra": nakshatra_name,
        "first_yogini": first_lord,
        "first_ruling_planet": YOGINI_PLANET[first_lord],
        "balance": round(balance_fraction * YOGINI_YEARS[first_lord], 4),
        "balance_unit": "years",
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════
# 3. ASHTOTTARI DASHA (108 years)
# ═══════════════════════════════════════════════════════════════

ASHTOTTARI_SEQUENCE = [
    "Sun", "Moon", "Mars", "Mercury",
    "Saturn", "Jupiter", "Rahu", "Venus",
]

ASHTOTTARI_YEARS = {
    "Sun": 6, "Moon": 15, "Mars": 8, "Mercury": 17,
    "Saturn": 10, "Jupiter": 19, "Rahu": 12, "Venus": 21,
}

ASHTOTTARI_TOTAL = 108.0

# Ashtottari uses a different nakshatra-to-lord mapping
# Starting from Ardra (nak 5), skipping every 3rd nakshatra
ASHTOTTARI_NAK_LORDS = {
    5: "Sun",      # Ardra
    8: "Moon",     # Ashlesha
    11: "Mars",    # Uttara Phalguni
    14: "Mercury", # Swati
    17: "Saturn",  # Jyeshtha
    20: "Jupiter", # Uttara Ashadha
    23: "Rahu",    # Shatabhisha
    26: "Venus",   # Revati
}


def _ashtottari_lord(nak_idx: int) -> tuple:
    """Find Ashtottari lord for a nakshatra and the start nak index."""
    # Map: groups of nakshatras to lords
    # Ardra(5),Punarvasu(6),Pushya(7) → Sun
    # Ashlesha(8),Magha(9),PPhalguni(10) → Moon
    # UPhalguni(11),Hasta(12),Chitra(13) → Mars
    # Swati(14),Vishakha(15),Anuradha(16) → Mercury
    # Jyeshtha(17),Mula(18),PAshadha(19) → Saturn
    # UAshadha(20),Shravana(21),Dhanishtha(22) → Jupiter
    # Shatabhisha(23),PBhadra(24),UBhadra(25) → Rahu
    # Revati(26),Ashwini(0),Bharani(1) → Venus
    # Krittika(2),Rohini(3),Mrigashira(4) → Sun (cycle repeats)

    # Normalize to Ashtottari cycle starting from Ardra (5)
    offset = (nak_idx - 5) % 27
    group = offset // 3
    lord = ASHTOTTARI_SEQUENCE[group % 8]
    start_nak = (5 + group * 3) % 27
    return lord, start_nak


def calc_ashtottari(
    moon_lon: float,
    birth_dt: datetime,
    max_level: int = 5,
) -> Dict[str, Any]:
    """Calculate Ashtottari Dasha from Moon's longitude."""
    nak_idx, _ = _calc_nakshatra_balance(moon_lon)
    nakshatra_name = NAKSHATRAS_27[nak_idx]

    lord, start_nak = _ashtottari_lord(nak_idx)

    # Balance: fraction remaining in the 3-nakshatra group
    group_start_lon = start_nak * NAKSHATRA_SPAN
    group_span = 3 * NAKSHATRA_SPAN
    deg_in_group = moon_lon - group_start_lon
    if deg_in_group < 0:
        deg_in_group += 360
    balance_fraction = 1.0 - (deg_in_group / group_span)
    if balance_fraction < 0:
        balance_fraction = 0.0
    if balance_fraction > 1:
        balance_fraction = 1.0

    lord_idx = ASHTOTTARI_SEQUENCE.index(lord)

    level_names = ["Mahadasha", "Antardasha", "Pratyantardasha", "Sookshma", "Prana"]
    periods = []
    cursor = birth_dt

    for i in range(8):
        p_lord = ASHTOTTARI_SEQUENCE[(lord_idx + i) % 8]
        full_days = ASHTOTTARI_YEARS[p_lord] * 365.25

        if i == 0:
            dasha_days = full_days * balance_fraction
        else:
            dasha_days = full_days

        period = _build_period_tree(
            cursor, p_lord, dasha_days,
            ASHTOTTARI_SEQUENCE, ASHTOTTARI_YEARS,
            ASHTOTTARI_TOTAL, 0, max_level, level_names,
        )
        periods.append(period)
        cursor = cursor + timedelta(days=dasha_days)

    _strip_dt_objects(periods)

    return {
        "system": "Ashtottari",
        "total_years": 108,
        "birth_nakshatra": nakshatra_name,
        "birth_nakshatra_lord": lord,
        "balance": round(balance_fraction * ASHTOTTARI_YEARS[lord], 4),
        "balance_unit": "years",
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════
# 4. CHARA DASHA (Jaimini — sign-based)
# ═══════════════════════════════════════════════════════════════

def _chara_dasha_years(sign_idx: int, planet_lons: dict) -> int:
    """
    Chara Dasha years for a sign = distance of its lord from the sign.
    Odd signs count forward, even signs count backward.
    """
    sign_name = SIGNS[sign_idx]
    lord = SIGN_LORDS[sign_name]
    lord_lon = planet_lons.get(lord, 0.0)
    lord_sign_idx = int(lord_lon / 30) % 12

    is_odd = (sign_idx % 2 == 0)  # Aries=0=odd
    if is_odd:
        distance = (lord_sign_idx - sign_idx) % 12
    else:
        distance = (sign_idx - lord_sign_idx) % 12

    # If lord is in own sign, years = 12
    if distance == 0:
        distance = 12

    return distance


def _chara_sign_sequence(asc_sign_idx: int) -> List[int]:
    """
    Chara Dasha sign sequence based on ascendant.
    Odd ascendant: Aries forward (0,1,2,...,11)
    Even ascendant: reverse from ascendant sign
    """
    is_odd = (asc_sign_idx % 2 == 0)
    if is_odd:
        return [(asc_sign_idx + i) % 12 for i in range(12)]
    else:
        return [(asc_sign_idx - i) % 12 for i in range(12)]


def calc_chara(
    asc_sign_idx: int,
    planet_lons: dict,
    birth_dt: datetime,
) -> Dict[str, Any]:
    """
    Calculate Chara Dasha (Jaimini sign-based).

    Parameters:
        asc_sign_idx: Ascendant sign index (0–11)
        planet_lons:  Dict of planet_name → sidereal longitude
        birth_dt:     Birth datetime
    """
    sequence = _chara_sign_sequence(asc_sign_idx)

    periods = []
    cursor = birth_dt

    for sign_idx in sequence:
        years = _chara_dasha_years(sign_idx, planet_lons)
        days = years * 365.25
        sign_name = SIGNS[sign_idx]
        lord = SIGN_LORDS[sign_name]

        end_dt = cursor + timedelta(days=days)

        # Antardasha: 12 sub-signs, each gets proportional share
        sub_periods = []
        is_odd = (sign_idx % 2 == 0)
        sub_cursor = cursor
        for j in range(12):
            if is_odd:
                sub_sign_idx = (sign_idx + j) % 12
            else:
                sub_sign_idx = (sign_idx - j) % 12

            sub_days = days / 12.0
            sub_end = sub_cursor + timedelta(days=sub_days)
            sub_periods.append({
                "lord": SIGNS[sub_sign_idx],
                "sign_lord": SIGN_LORDS[SIGNS[sub_sign_idx]],
                "level": "Antardasha",
                "start": sub_cursor.strftime("%d-%m-%Y"),
                "end": sub_end.strftime("%d-%m-%Y"),
                "duration_days": round(sub_days, 2),
                "duration_years": round(sub_days / 365.25, 4),
            })
            sub_cursor = sub_end

        periods.append({
            "lord": sign_name,
            "sign_lord": lord,
            "level": "Mahadasha",
            "start": cursor.strftime("%d-%m-%Y"),
            "end": end_dt.strftime("%d-%m-%Y"),
            "duration_days": round(days, 2),
            "duration_years": years,
            "sub_periods": sub_periods,
        })
        cursor = end_dt

    return {
        "system": "Chara",
        "total_years": "Variable",
        "note": "Jaimini sign-based dasha system",
        "ascendant_sign": SIGNS[asc_sign_idx],
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════
# 5. NARAYANA DASHA (Jaimini — sign-based)
# ═══════════════════════════════════════════════════════════════

def _narayana_years(sign_idx: int, planet_lons: dict) -> int:
    """
    Narayana Dasha years for a sign.
    Based on the lord's distance from the sign, similar to Chara
    but uses different counting rules per Parashara.
    Odd signs: count forward from the sign to its lord's position.
    Even signs: count backward.
    If lord is in own sign, years = 12.
    """
    sign_name = SIGNS[sign_idx]
    lord = SIGN_LORDS[sign_name]
    lord_lon = planet_lons.get(lord, 0.0)
    lord_sign_idx = int(lord_lon / 30) % 12

    is_odd = (sign_idx % 2 == 0)
    if is_odd:
        distance = (lord_sign_idx - sign_idx) % 12
    else:
        distance = (sign_idx - lord_sign_idx) % 12

    if distance == 0:
        distance = 12

    return distance


def _narayana_sign_sequence(asc_sign_idx: int, house_num: int = 1) -> List[int]:
    """
    Narayana Dasha sign sequence starting from a specific house.
    Follows kendras first, then panaphara, then apoklima pattern
    based on odd/even nature of the starting sign.
    For simplicity, uses the standard Jaimini sequence.
    """
    start_idx = (asc_sign_idx + house_num - 1) % 12
    is_odd = (start_idx % 2 == 0)
    if is_odd:
        return [(start_idx + i) % 12 for i in range(12)]
    else:
        return [(start_idx - i) % 12 for i in range(12)]


def calc_narayana(
    asc_sign_idx: int,
    planet_lons: dict,
    birth_dt: datetime,
) -> Dict[str, Any]:
    """
    Calculate Narayana Dasha (Jaimini sign-based, from Lagna).

    Parameters:
        asc_sign_idx: Ascendant sign index (0–11)
        planet_lons:  Dict of planet_name → sidereal longitude
        birth_dt:     Birth datetime
    """
    sequence = _narayana_sign_sequence(asc_sign_idx)

    periods = []
    cursor = birth_dt

    for sign_idx in sequence:
        years = _narayana_years(sign_idx, planet_lons)
        days = years * 365.25
        sign_name = SIGNS[sign_idx]
        lord = SIGN_LORDS[sign_name]

        end_dt = cursor + timedelta(days=days)

        # Antardasha: 12 sub-signs
        sub_periods = []
        is_odd = (sign_idx % 2 == 0)
        sub_cursor = cursor
        for j in range(12):
            if is_odd:
                sub_sign_idx = (sign_idx + j) % 12
            else:
                sub_sign_idx = (sign_idx - j) % 12

            sub_days = days / 12.0
            sub_end = sub_cursor + timedelta(days=sub_days)
            sub_periods.append({
                "lord": SIGNS[sub_sign_idx],
                "sign_lord": SIGN_LORDS[SIGNS[sub_sign_idx]],
                "level": "Antardasha",
                "start": sub_cursor.strftime("%d-%m-%Y"),
                "end": sub_end.strftime("%d-%m-%Y"),
                "duration_days": round(sub_days, 2),
                "duration_years": round(sub_days / 365.25, 4),
            })
            sub_cursor = sub_end

        periods.append({
            "lord": sign_name,
            "sign_lord": lord,
            "level": "Mahadasha",
            "start": cursor.strftime("%d-%m-%Y"),
            "end": end_dt.strftime("%d-%m-%Y"),
            "duration_days": round(days, 2),
            "duration_years": years,
            "sub_periods": sub_periods,
        })
        cursor = end_dt

    return {
        "system": "Narayana",
        "total_years": "Variable",
        "note": "Jaimini sign-based dasha from Lagna",
        "ascendant_sign": SIGNS[asc_sign_idx],
        "periods": periods,
    }


# ═══════════════════════════════════════════════════════════════
# Utility
# ═══════════════════════════════════════════════════════════════

def _strip_dt_objects(periods: list):
    """Remove internal datetime objects from period tree (for JSON serialization)."""
    for p in periods:
        p.pop("start_dt", None)
        p.pop("end_dt", None)
        if "sub_periods" in p:
            _strip_dt_objects(p["sub_periods"])


def find_current_dasha(periods: list, target_dt: datetime) -> list:
    """
    Find the active dasha path at a given datetime.
    Returns list of lord names from Mahadasha down to deepest matching level.
    """
    path = []
    for p in periods:
        start = datetime.strptime(p["start"], "%d-%m-%Y")
        end = datetime.strptime(p["end"], "%d-%m-%Y")
        if start <= target_dt < end:
            path.append(p["lord"])
            if "sub_periods" in p:
                sub_path = find_current_dasha(p["sub_periods"], target_dt)
                path.extend(sub_path)
            break
    return path
