"""
dasha.py — Dasha module (orchestrator).
========================================
Takes birth data → produces all 5 dasha systems.
"""
from __future__ import annotations

from datetime import datetime
from typing import Dict, Any

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc
from core.constants import SIGNS
from core.dasha import (
    calc_vimshottari, calc_yogini, calc_ashtottari,
    calc_chara, calc_narayana, find_current_dasha,
)


def generate_dashas(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    max_level: int = 5,
    systems: list = None,
) -> Dict[str, Any]:
    """
    Generate all requested dasha systems for a birth chart.

    Parameters:
        birth_dt:   Local datetime of birth
        lat:        Birth place latitude
        lon:        Birth place longitude
        tz_offset:  Timezone offset from UTC
        ayanamsa:   Ayanamsa system
        max_level:  Depth of sub-periods (1–5)
        systems:    List of systems to calculate (default: all)

    Returns:
        Dict with birth_info, each dasha system's periods, and current dashas.
    """
    if systems is None:
        systems = ["vimshottari", "yogini", "ashtottari", "chara", "narayana"]

    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    # Get planetary positions
    planet_positions = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)

    # Moon longitude (needed for nakshatra-based dashas)
    moon_lon = None
    planet_lons = {}
    for pp in planet_positions:
        planet_lons[pp.planet] = pp.longitude
        if pp.planet == "Moon":
            moon_lon = pp.longitude

    asc_sign_idx = SIGNS.index(ascendant.sign)

    result = {
        "birth_info": {
            "date": birth_dt.strftime("%d-%m-%Y"),
            "time": birth_dt.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "tz_offset": tz_offset,
            "ayanamsa": ayanamsa,
            "moon_longitude": round(moon_lon, 4) if moon_lon else None,
            "ascendant_sign": ascendant.sign,
        },
        "dashas": {},
    }

    now = datetime.now()

    # Nakshatra-based systems
    if "vimshottari" in systems and moon_lon is not None:
        vim = calc_vimshottari(moon_lon, birth_dt, max_level)
        vim["current_path"] = find_current_dasha(vim["periods"], now)
        result["dashas"]["vimshottari"] = vim

    if "yogini" in systems and moon_lon is not None:
        yog = calc_yogini(moon_lon, birth_dt, max_level)
        yog["current_path"] = find_current_dasha(yog["periods"], now)
        result["dashas"]["yogini"] = yog

    if "ashtottari" in systems and moon_lon is not None:
        ash = calc_ashtottari(moon_lon, birth_dt, max_level)
        ash["current_path"] = find_current_dasha(ash["periods"], now)
        result["dashas"]["ashtottari"] = ash

    # Sign-based systems
    if "chara" in systems:
        cha = calc_chara(asc_sign_idx, planet_lons, birth_dt)
        cha["current_path"] = find_current_dasha(cha["periods"], now)
        result["dashas"]["chara"] = cha

    if "narayana" in systems:
        nar = calc_narayana(asc_sign_idx, planet_lons, birth_dt)
        nar["current_path"] = find_current_dasha(nar["periods"], now)
        result["dashas"]["narayana"] = nar

    return result
