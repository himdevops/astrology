"""
ephemeris.py — Swiss Ephemeris wrapper.
========================================
Lowest-level planet calculation. Returns PlanetPosition objects.
All sidereal/tropical logic lives here.
"""
from __future__ import annotations

from typing import List, Tuple

import swisseph as swe

from core.constants import (
    AYANAMSA_MAP, PLANET_IDS, PLANETS_9,
)
from core.types import PlanetPosition
from core.signs import calc_sign
from core.nakshatra import calc_nakshatra
from core.utils import normalize_degree, deg_to_dms


# ─── Ayanamsa ───────────────────────────────────────────────

def set_ayanamsa(ayanamsa: str = "lahiri"):
    """Configure sidereal ayanamsa for subsequent calculations."""
    sid = AYANAMSA_MAP.get(ayanamsa.lower(), swe.SIDM_LAHIRI)
    if sid != -1:
        swe.set_sid_mode(sid)


def get_ayanamsa_value(jd: float, ayanamsa: str = "lahiri") -> float:
    """Get ayanamsa offset in degrees for a Julian Day."""
    set_ayanamsa(ayanamsa)
    return swe.get_ayanamsa(jd)


# ─── Raw calculation ────────────────────────────────────────

def calc_planet_raw(
    jd: float, planet_id: int, sidereal: bool = True
) -> Tuple[float, float, float]:
    """
    Raw Swiss Ephemeris call.
    Returns (longitude, latitude, speed_deg_per_day).
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if sidereal:
        flags |= swe.FLG_SIDEREAL

    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[0], result[1], result[3]


def calc_planet_equatorial(jd: float, planet_id: int) -> Tuple[float, float]:
    """Get equatorial RA and Declination. Used for parallels."""
    flags = swe.FLG_SWIEPH | swe.FLG_EQUATORIAL
    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[0], result[1]  # RA, Declination


# ─── High-level position ────────────────────────────────────

def get_planet_position(
    jd: float, planet: str, ayanamsa: str = "lahiri"
) -> PlanetPosition:
    """
    Full position for one planet: sign, degree, nakshatra, pada, speed, retro.
    This is the workhorse function — everything else builds on it.
    """
    set_ayanamsa(ayanamsa)
    sidereal = ayanamsa.lower() != "tropical"

    if planet == "Ketu":
        lon, lat, speed = calc_planet_raw(jd, PLANET_IDS["Rahu"], sidereal)
        lon = normalize_degree(lon + 180)
        speed = -speed
    else:
        lon, lat, speed = calc_planet_raw(jd, PLANET_IDS[planet], sidereal)

    lon = normalize_degree(lon)

    sign_info = calc_sign(lon)
    nak_info = calc_nakshatra(lon)

    return PlanetPosition(
        planet=planet,
        longitude=lon,
        latitude=lat,
        speed=speed,
        sign=sign_info.name,
        sign_lord=sign_info.lord,
        degree_in_sign=sign_info.degree_in_sign,
        nakshatra=nak_info.name,
        nakshatra_lord=nak_info.lord,
        nakshatra_pada=nak_info.pada,
        retrograde=speed < 0,
        degree_display=f"{deg_to_dms(sign_info.degree_in_sign)} {sign_info.name}",
    )


def get_all_planets(
    jd: float, ayanamsa: str = "lahiri"
) -> List[PlanetPosition]:
    """Get positions for all 9 Vedic planets."""
    return [get_planet_position(jd, p, ayanamsa) for p in PLANETS_9]


def calc_ascendant(
    jd: float, lat: float, lon: float, ayanamsa: str = "lahiri"
) -> PlanetPosition:
    """
    Calculate Lagna (Ascendant) — the rising sign at a given time and place.
    Uses Swiss Ephemeris house calculation (Placidus).
    Returns a PlanetPosition-like object for the Ascendant.
    """
    set_ayanamsa(ayanamsa)
    sidereal = ayanamsa.lower() != "tropical"

    # swe.houses returns (cusps_tuple, ascmc_tuple)
    # ascmc[0] = Ascendant, ascmc[1] = MC, etc.
    flags = swe.FLG_SIDEREAL if sidereal else 0
    cusps, ascmc = swe.houses_ex(jd, lat, lon, b'P', flags)
    asc_lon = normalize_degree(ascmc[0])

    sign_info = calc_sign(asc_lon)
    nak_info = calc_nakshatra(asc_lon)

    return PlanetPosition(
        planet="Ascendant",
        longitude=asc_lon,
        latitude=0.0,
        speed=0.0,
        sign=sign_info.name,
        sign_lord=sign_info.lord,
        degree_in_sign=sign_info.degree_in_sign,
        nakshatra=nak_info.name,
        nakshatra_lord=nak_info.lord,
        nakshatra_pada=nak_info.pada,
        retrograde=False,
        degree_display=f"{deg_to_dms(sign_info.degree_in_sign)} {sign_info.name}",
    )
