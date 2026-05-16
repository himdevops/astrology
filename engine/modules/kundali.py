"""
kundali.py — Birth Chart (Kundali) module.
==========================================
Takes date of birth, time, and place → produces:
  - All 16 Shodashvarga divisional charts
  - Full nakshatra details for each planet (name, pada, lord, sub-lord, deity)
  - Ascendant (Lagna) for each varga
  - House placements

This is the master module for horoscope generation.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any, List

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc, deg_to_dms
from core.nakshatra import calc_nakshatra
from core.signs import calc_sign
from core.constants import (
    SIGNS, SIGN_LORDS, NAKSHATRAS_27, NAKSHATRA_LORDS,
    NAKSHATRA_DEITY, NAKSHATRA_SPAN, PADA_SPAN,
)
from core.divisional import (
    calc_varga, calc_all_vargas, VARGA_ORDER, VARGA_NAMES,
    calc_varga_deity,
)


# ─── KP Sub-Lord Table ──────────────────────────────────────
# Vimshottari Dasha years for each planet (determines sub-division proportions)
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
DASHA_SEQUENCE = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
TOTAL_DASHA_YEARS = 120.0


def calc_sub_lord(longitude: float) -> str:
    """
    Calculate KP Sub-Lord for a given sidereal longitude.
    Each nakshatra (13°20') is divided among 9 planets
    in Vimshottari Dasha proportion, starting from the nakshatra lord.
    """
    nak_index = int(longitude / NAKSHATRA_SPAN) % 27
    nak_lord = NAKSHATRA_LORDS[nak_index]
    degree_in_nak = longitude - (nak_index * NAKSHATRA_SPAN)

    # Find starting position in dasha sequence
    start_idx = DASHA_SEQUENCE.index(nak_lord)

    # Sub-divide the nakshatra span proportionally
    accumulated = 0.0
    for i in range(9):
        planet = DASHA_SEQUENCE[(start_idx + i) % 9]
        sub_span = NAKSHATRA_SPAN * (DASHA_YEARS[planet] / TOTAL_DASHA_YEARS)
        accumulated += sub_span
        if degree_in_nak < accumulated:
            return planet

    return DASHA_SEQUENCE[(start_idx + 8) % 9]


# ─── Planet Detail Builder ──────────────────────────────────

def _build_planet_detail(planet_pos) -> Dict[str, Any]:
    """Build full nakshatra detail for a planet position."""
    nak = calc_nakshatra(planet_pos.longitude)
    sub_lord = calc_sub_lord(planet_pos.longitude)

    return {
        "planet": planet_pos.planet,
        "longitude": round(planet_pos.longitude, 4),
        "latitude": round(planet_pos.latitude, 4),
        "speed": round(planet_pos.speed, 6),
        "retrograde": planet_pos.retrograde,
        "sign": planet_pos.sign,
        "sign_lord": planet_pos.sign_lord,
        "degree_in_sign": round(planet_pos.degree_in_sign, 4),
        "degree_display": planet_pos.degree_display,
        "nakshatra": nak.name,
        "nakshatra_lord": nak.lord,
        "nakshatra_pada": nak.pada,
        "nakshatra_deity": nak.deity,
        "nakshatra_degree": round(nak.degree_in_nakshatra, 4),
        "sub_lord": sub_lord,
    }


# ─── House Assignment ───────────────────────────────────────

def _assign_houses(asc_sign_idx: int, planet_details: List[Dict]) -> List[Dict]:
    """
    Assign house numbers based on Ascendant sign.
    House 1 = Ascendant sign, House 2 = next sign, etc.
    """
    for p in planet_details:
        p_sign_idx = SIGNS.index(p["sign"])
        house = ((p_sign_idx - asc_sign_idx) % 12) + 1
        p["house"] = house
    return planet_details


# ─── Varga Chart Builder ────────────────────────────────────

def _build_varga_chart(
    planet_positions, asc_longitude: float, varga: str
) -> Dict[str, Any]:
    """
    Build a single divisional chart.
    Returns chart with planet placements, ascendant, and house map.
    """
    # Ascendant in this varga
    asc_varga = calc_varga(asc_longitude, varga)
    asc_sign_idx = asc_varga["sign_index"]

    # Deity for ascendant in this varga
    asc_deity_info = calc_varga_deity(asc_longitude, varga)

    # Planet placements in this varga
    planets = []
    for pp in planet_positions:
        varga_info = calc_varga(pp.longitude, varga)
        p_sign_idx = varga_info["sign_index"]
        house = ((p_sign_idx - asc_sign_idx) % 12) + 1

        # Deity for this planet in this varga
        deity_info = calc_varga_deity(pp.longitude, varga)

        planet_entry = {
            "planet": pp.planet,
            "sign": varga_info["sign"],
            "sign_lord": varga_info["sign_lord"],
            "house": house,
            "retrograde": pp.retrograde,
        }
        if deity_info:
            planet_entry["deity"] = deity_info["deity"]
            planet_entry["deity_part"] = deity_info["part"]

        planets.append(planet_entry)

    # Build house map (which planets in each house)
    house_map = {i: [] for i in range(1, 13)}
    for p in planets:
        house_map[p["house"]].append(p["planet"])

    # Sign for each house
    house_signs = {}
    for h in range(1, 13):
        sign_idx = (asc_sign_idx + h - 1) % 12
        house_signs[h] = {
            "sign": SIGNS[sign_idx],
            "sign_lord": SIGN_LORDS[SIGNS[sign_idx]],
        }

    result = {
        "varga": varga,
        "name": VARGA_NAMES[varga],
        "ascendant_sign": asc_varga["sign"],
        "ascendant_lord": asc_varga["sign_lord"],
        "ascendant_sign_index": asc_sign_idx,
        "planets": planets,
        "house_map": {str(k): v for k, v in house_map.items()},
        "house_signs": {str(k): v for k, v in house_signs.items()},
    }
    if asc_deity_info:
        result["ascendant_deity"] = asc_deity_info["deity"]
        result["ascendant_deity_part"] = asc_deity_info["part"]

    return result


# ═══════════════════════════════════════════════════════════════
# Main Entry Point
# ═══════════════════════════════════════════════════════════════

def generate_kundali(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Generate complete Kundali (birth chart) with all 16 Shodashvarga.

    Parameters:
        birth_dt:  Local datetime of birth
        lat:       Birth place latitude
        lon:       Birth place longitude
        tz_offset: Timezone offset from UTC
        ayanamsa:  Ayanamsa system (lahiri, raman, krishnamurti)

    Returns:
        Complete kundali data with:
        - birth_info: Input details
        - planets: Full planet details with nakshatra/sub-lord
        - ascendant: Lagna details
        - charts: All 16 divisional charts
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    # Get all planet positions
    planet_positions = get_all_planets(jd, ayanamsa)

    # Get Ascendant
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)

    # Build detailed planet info with nakshatra/sub-lord
    planet_details = [_build_planet_detail(pp) for pp in planet_positions]

    # Ascendant detail
    asc_nak = calc_nakshatra(ascendant.longitude)
    asc_sub_lord = calc_sub_lord(ascendant.longitude)
    asc_detail = {
        "planet": "Ascendant",
        "longitude": round(ascendant.longitude, 4),
        "sign": ascendant.sign,
        "sign_lord": ascendant.sign_lord,
        "degree_in_sign": round(ascendant.degree_in_sign, 4),
        "degree_display": ascendant.degree_display,
        "nakshatra": asc_nak.name,
        "nakshatra_lord": asc_nak.lord,
        "nakshatra_pada": asc_nak.pada,
        "nakshatra_deity": asc_nak.deity,
        "sub_lord": asc_sub_lord,
    }

    # Assign houses in D1
    asc_sign_idx = SIGNS.index(ascendant.sign)
    planet_details = _assign_houses(asc_sign_idx, planet_details)

    # Build all 16 divisional charts
    charts = {}
    for varga in VARGA_ORDER:
        charts[varga] = _build_varga_chart(planet_positions, ascendant.longitude, varga)

    return {
        "birth_info": {
            "date": birth_dt.strftime("%d-%m-%Y"),
            "time": birth_dt.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "tz_offset": tz_offset,
            "ayanamsa": ayanamsa,
        },
        "ascendant": asc_detail,
        "planets": planet_details,
        "charts": charts,
    }
