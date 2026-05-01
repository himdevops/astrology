"""
kp_system.py — Krishnamurti Paddhati (KP) System for Financial Astrology
Implements:
1. Sub-lord theory with cuspal sub-lords for all 12 houses
2. Significators (planet → house connections via star-lord, sub-lord)
3. Ruling Planets (RP) for event timing
4. KP-based market entry/exit signals
5. Cuspal Sub-Lord table for financial houses (2, 5, 7, 10, 11)

KP uses Placidus house system with Krishnamurti Ayanamsa (default).
Each nakshatra (13°20') is subdivided into 9 unequal sub-lords
proportional to Vimshottari Dasha years.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, List, Optional, Tuple

from app.constants import (
    SIGNS, SIGN_IDX, SIGN_LORDS,
    NAKSHATRA_LORD_ORDER, DASHA_YEARS, TOTAL_DASHA_YEARS,
    NAKSHATRA_SPAN_DEG, PADA_SPAN_DEG,
    FINANCIAL_KARAKAS,
)

# ─────────────────────────────────────────────────────────────
# KP Sub-lord Division Table
# Each nakshatra is divided proportionally by Dasha years
# ─────────────────────────────────────────────────────────────

def build_kp_sublord_table() -> List[Dict]:
    """
    Build the complete 249-entry KP sub-lord table.
    Each entry: nakshatra number, sign, star-lord, sub-lord, degree range.
    """
    table = []
    entry_id = 1

    for nak_idx in range(27):
        nak_start = nak_idx * NAKSHATRA_SPAN_DEG
        star_lord = NAKSHATRA_LORD_ORDER[nak_idx % 9]
        lord_start_idx = NAKSHATRA_LORD_ORDER.index(star_lord)

        sub_start = nak_start
        for sub_offset in range(9):
            sub_idx = (lord_start_idx + sub_offset) % 9
            sub_lord = NAKSHATRA_LORD_ORDER[sub_idx]
            sub_span = NAKSHATRA_SPAN_DEG * (DASHA_YEARS[sub_lord] / TOTAL_DASHA_YEARS)
            sub_end = sub_start + sub_span

            sign_idx = int(sub_start / 30) % 12
            table.append({
                "id": entry_id,
                "nakshatra": nak_idx + 1,
                "sign": SIGNS[sign_idx],
                "sign_lord": SIGN_LORDS[SIGNS[sign_idx]],
                "star_lord": star_lord,
                "sub_lord": sub_lord,
                "start_deg": round(sub_start, 6),
                "end_deg": round(sub_end, 6),
            })
            entry_id += 1
            sub_start = sub_end

    return table


# Pre-build the table
KP_SUBLORD_TABLE = build_kp_sublord_table()


def get_kp_pointer(longitude: float) -> Dict:
    """
    Get complete KP pointer for a given sidereal longitude.
    Returns: sign-lord, star-lord, sub-lord, sub-sub-lord.
    """
    longitude = longitude % 360.0

    # Find the sub-lord entry
    for entry in KP_SUBLORD_TABLE:
        if entry["start_deg"] <= longitude < entry["end_deg"]:
            # Calculate sub-sub-lord within the sub-lord range
            sub_start = entry["start_deg"]
            sub_span = entry["end_deg"] - entry["start_deg"]
            pos_in_sub = longitude - sub_start
            fraction = pos_in_sub / sub_span if sub_span > 0 else 0

            sub_lord_idx = NAKSHATRA_LORD_ORDER.index(entry["sub_lord"])
            sub_sub_lord = _find_sub_at_fraction(sub_lord_idx, fraction)

            return {
                "longitude": round(longitude, 6),
                "sign": entry["sign"],
                "sign_lord": entry["sign_lord"],
                "star_lord": entry["star_lord"],
                "sub_lord": entry["sub_lord"],
                "sub_sub_lord": sub_sub_lord,
                "kp_number": entry["id"],
            }

    # Fallback for 360.0
    entry = KP_SUBLORD_TABLE[-1]
    return {
        "longitude": round(longitude, 6),
        "sign": entry["sign"],
        "sign_lord": entry["sign_lord"],
        "star_lord": entry["star_lord"],
        "sub_lord": entry["sub_lord"],
        "sub_sub_lord": entry["sub_lord"],
        "kp_number": entry["id"],
    }


def _find_sub_at_fraction(lord_start_idx: int, fraction: float) -> str:
    """Find which sub-lord governs at a given fraction (0-1)."""
    cumulative = 0.0
    for i in range(9):
        idx = (lord_start_idx + i) % 9
        lord = NAKSHATRA_LORD_ORDER[idx]
        span = DASHA_YEARS[lord] / TOTAL_DASHA_YEARS
        cumulative += span
        if fraction <= cumulative:
            return lord
    return NAKSHATRA_LORD_ORDER[lord_start_idx]


# ─────────────────────────────────────────────────────────────
# Cuspal Sub-Lords for all 12 Houses
# ─────────────────────────────────────────────────────────────

def calculate_cuspal_sublords(houses: List[Dict]) -> List[Dict]:
    """
    Calculate KP cuspal sub-lords for all 12 house cusps.
    The sub-lord of a cusp determines whether that house's matters
    will fructify (supportive sub-lord) or not (non-supportive).
    """
    cuspal_data = []
    for house in houses:
        cusp_long = house["longitude"]
        kp_data = get_kp_pointer(cusp_long)

        house_num = house["house"]
        cuspal_data.append({
            "house": house_num,
            "cusp_longitude": round(cusp_long, 4),
            "sign": kp_data["sign"],
            "sign_lord": kp_data["sign_lord"],
            "star_lord": kp_data["star_lord"],
            "sub_lord": kp_data["sub_lord"],
            "sub_sub_lord": kp_data["sub_sub_lord"],
            "kp_number": kp_data["kp_number"],
            "financial_relevance": _house_financial_relevance(house_num),
        })

    return cuspal_data


def _house_financial_relevance(house: int) -> str:
    """Financial relevance of each house in KP for market prediction."""
    relevance = {
        1: "Self-wealth, overall financial personality",
        2: "CRITICAL: Accumulated wealth, bank balance, family money",
        3: "Short-term trading gains, communication-based income",
        4: "Property, fixed assets, real estate investments",
        5: "CRITICAL: Speculation, stock market, intelligent investments",
        6: "Debts, loans, competition — service sector income",
        7: "CRITICAL: Business partnerships, foreign trade, contracts",
        8: "Sudden gains/losses, insurance, inheritance, market shocks",
        9: "Fortune, long-distance trade, export business",
        10: "CRITICAL: Career, professional success, government income",
        11: "CRITICAL: Income, gains, profit realization, desires fulfilled",
        12: "Expenses, losses, foreign investments, import business",
    }
    return relevance.get(house, "")


# ─────────────────────────────────────────────────────────────
# Significator Analysis
# ─────────────────────────────────────────────────────────────

def calculate_significators(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
) -> Dict:
    """
    Calculate significators for each house using KP methodology.
    A planet signifies a house through 4 levels:
    1. Planets in the star of occupant of that house
    2. Occupant planet itself
    3. Planets in the star of lord of that house
    4. Lord of that house
    Sub-lord connection determines final fructification.
    """
    asc_sign = ascendant["sign"]
    asc_idx = SIGN_IDX.get(asc_sign, 0)

    # Map planets to houses
    planet_houses = {}
    for p in planets:
        if p["planet"] in ("Rahu", "Ketu"):
            continue
        p_sign_idx = SIGN_IDX.get(p["sign"], 0)
        house = ((p_sign_idx - asc_idx) % 12) + 1
        planet_houses[p["planet"]] = house

    # Get star-lord of each planet
    planet_star_lords = {}
    for p in planets:
        kp = get_kp_pointer(p["longitude"])
        planet_star_lords[p["planet"]] = kp["star_lord"]

    # Calculate significators for each house
    house_significators = {}
    for house_num in range(1, 13):
        sign_idx = (asc_idx + house_num - 1) % 12
        house_lord = SIGN_LORDS[SIGNS[sign_idx]]

        # Level 1 & 2: Occupants and planets in star of occupants
        occupants = [name for name, h in planet_houses.items() if h == house_num]
        star_of_occupants = []
        for occ in occupants:
            for pname, sl in planet_star_lords.items():
                if sl == occ and pname not in star_of_occupants:
                    star_of_occupants.append(pname)

        # Level 3 & 4: Lord and planets in star of lord
        star_of_lord = [
            pname for pname, sl in planet_star_lords.items()
            if sl == house_lord
        ]

        all_significators = list(dict.fromkeys(
            star_of_occupants + occupants + star_of_lord + [house_lord]
        ))

        house_significators[house_num] = {
            "house": house_num,
            "sign": SIGNS[sign_idx],
            "lord": house_lord,
            "occupants": occupants,
            "star_of_occupants": star_of_occupants,
            "star_of_lord": star_of_lord,
            "all_significators": all_significators,
            "significator_count": len(all_significators),
        }

    return house_significators


# ─────────────────────────────────────────────────────────────
# Ruling Planets (RP) for Event Timing
# ─────────────────────────────────────────────────────────────

def calculate_ruling_planets(
    transit_planets: List[Dict],
    transit_datetime: datetime,
    ascendant: Dict,
) -> Dict:
    """
    KP Ruling Planets at the moment of query/event.
    RP = Sign lord + Star lord + Sub lord of:
    1. Ascendant at query time
    2. Moon at query time
    3. Day lord

    Ruling planets indicate WHICH planets are active NOW and
    help pinpoint the exact timing of market events.
    """
    # Day lord
    weekday = transit_datetime.weekday()
    day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    day_lord = day_lords[weekday]

    # Moon's KP pointer
    moon = next((p for p in transit_planets if p["planet"] == "Moon"), None)
    moon_kp = get_kp_pointer(moon["longitude"]) if moon else {}

    # Ascendant KP pointer
    asc_kp = get_kp_pointer(ascendant["longitude"])

    # Collect all ruling planets
    rp_list = []
    if asc_kp:
        rp_list.extend([asc_kp["sign_lord"], asc_kp["star_lord"], asc_kp["sub_lord"]])
    if moon_kp:
        rp_list.extend([moon_kp["sign_lord"], moon_kp["star_lord"], moon_kp["sub_lord"]])
    rp_list.append(day_lord)

    # Count frequency — stronger RPs appear multiple times
    from collections import Counter
    rp_counts = Counter(rp_list)
    sorted_rps = sorted(rp_counts.items(), key=lambda x: -x[1])

    # Primary RPs (appear 2+ times)
    primary_rps = [rp for rp, count in sorted_rps if count >= 2]
    secondary_rps = [rp for rp, count in sorted_rps if count == 1]

    return {
        "query_datetime": transit_datetime.strftime("%Y-%m-%d %H:%M"),
        "day_lord": day_lord,
        "ascendant_kp": asc_kp,
        "moon_kp": moon_kp,
        "ruling_planets": {
            "all": [{"planet": rp, "strength": count} for rp, count in sorted_rps],
            "primary": primary_rps,
            "secondary": secondary_rps,
        },
        "financial_timing": _rp_financial_timing(primary_rps, secondary_rps),
    }


def _rp_financial_timing(primary: List[str], secondary: List[str]) -> Dict:
    """Market timing interpretation from Ruling Planets."""
    bullish_planets = {"Jupiter", "Venus", "Moon", "Mercury"}
    bearish_planets = {"Saturn", "Mars", "Rahu", "Ketu"}

    bull_count = sum(1 for p in primary if p in bullish_planets)
    bear_count = sum(1 for p in primary if p in bearish_planets)

    if bull_count > bear_count:
        signal = "BULLISH TIMING"
        action = "Good time for market entry / buying"
    elif bear_count > bull_count:
        signal = "BEARISH TIMING"
        action = "Avoid new entries / consider exit"
    else:
        signal = "NEUTRAL TIMING"
        action = "Wait for clearer ruling planet alignment"

    active_sectors = []
    for rp in primary:
        sectors = FINANCIAL_KARAKAS.get(rp, "")
        if sectors:
            active_sectors.append(f"{rp}: {sectors}")

    return {
        "signal": signal,
        "action": action,
        "bullish_rps": bull_count,
        "bearish_rps": bear_count,
        "active_sectors": active_sectors,
    }


# ─────────────────────────────────────────────────────────────
# KP Financial Analysis — Main Function
# ─────────────────────────────────────────────────────────────

def calculate_kp_analysis(
    planets: List[Dict],
    houses: List[Dict],
    ascendant: Dict,
    transit_planets: Optional[List[Dict]] = None,
    transit_datetime: Optional[datetime] = None,
) -> Dict:
    """
    Complete KP analysis for financial astrology.
    Combines cuspal sub-lords, significators, and ruling planets.
    """
    # 1. Cuspal sub-lords
    cuspal = calculate_cuspal_sublords(houses)

    # 2. Significators
    significators = calculate_significators(planets, houses, ascendant)

    # 3. Planet KP pointers
    planet_kp = []
    for p in planets:
        kp = get_kp_pointer(p["longitude"])
        planet_kp.append({
            "planet": p["planet"],
            **kp,
        })

    # 4. Financial house analysis (2, 5, 7, 10, 11)
    financial_analysis = _kp_financial_house_analysis(cuspal, significators)

    # 5. Ruling planets (if transit data provided)
    ruling_planets = None
    if transit_planets and transit_datetime:
        ruling_planets = calculate_ruling_planets(
            transit_planets, transit_datetime, ascendant
        )

    return {
        "type": "kp_analysis",
        "cuspal_sublords": cuspal,
        "significators": significators,
        "planet_kp_pointers": planet_kp,
        "financial_analysis": financial_analysis,
        "ruling_planets": ruling_planets,
    }


def _kp_financial_house_analysis(
    cuspal: List[Dict],
    significators: Dict,
) -> Dict:
    """
    Analyze financial houses (2, 5, 7, 10, 11) using KP sub-lord method.
    The sub-lord of financial cusp determines if wealth will materialize.
    """
    financial_houses = {
        2: "Wealth & Savings",
        5: "Stock Market & Speculation",
        7: "Business & Partnerships",
        10: "Career & Professional Income",
        11: "Gains & Profit Realization",
    }
    positive_houses = {1, 2, 3, 5, 6, 9, 10, 11}  # Houses whose signification = gain
    negative_houses = {4, 7, 8, 12}  # Houses whose signification = loss/expense

    analysis = {}
    total_score = 0
    for house_num, meaning in financial_houses.items():
        cusp = next((c for c in cuspal if c["house"] == house_num), None)
        if not cusp:
            continue

        sub_lord = cusp["sub_lord"]
        sigs = significators.get(house_num, {})

        # Check if sub-lord signifies positive or negative houses
        sub_lord_houses = []
        for h, sig_data in significators.items():
            if sub_lord in sig_data.get("all_significators", []):
                sub_lord_houses.append(h)

        positive_sigs = [h for h in sub_lord_houses if h in positive_houses]
        negative_sigs = [h for h in sub_lord_houses if h in negative_houses]

        if len(positive_sigs) > len(negative_sigs):
            verdict = "FAVORABLE"
            score = 0.6
        elif len(negative_sigs) > len(positive_sigs):
            verdict = "UNFAVORABLE"
            score = -0.4
        else:
            verdict = "MIXED"
            score = 0.0

        total_score += score
        analysis[house_num] = {
            "house": house_num,
            "meaning": meaning,
            "cusp_sub_lord": sub_lord,
            "sub_lord_signifies_houses": sub_lord_houses,
            "positive_houses": positive_sigs,
            "negative_houses": negative_sigs,
            "verdict": verdict,
            "score": score,
            "total_significators": sigs.get("all_significators", []),
        }

    avg_score = total_score / len(financial_houses) if financial_houses else 0
    if avg_score > 0.3:
        overall = "KP indicates STRONG financial potential"
    elif avg_score > 0:
        overall = "KP indicates MODERATE financial potential"
    elif avg_score > -0.3:
        overall = "KP indicates MIXED financial outlook"
    else:
        overall = "KP indicates WEAK financial period — caution advised"

    return {
        "houses": analysis,
        "avg_score": round(avg_score, 3),
        "overall_verdict": overall,
    }
