"""
core — Low-level Vedic Astrology calculation library.
======================================================
This package is the FOUNDATION of the entire engine.
Every module, API route, and future feature imports from here.

Sub-modules:
  constants  — All static data (signs, nakshatras, tithis, etc.)
  types      — Dataclasses / typed containers
  ephemeris  — Swiss Ephemeris wrapper (planet longitude, speed, latitude)
  signs      — Rashi (sign) calculations
  nakshatra  — Nakshatra, pada, lord calculations
  panchang   — Tithi, Yoga, Karana, Vara
  geo        — Sunrise, sunset, moonrise, location helpers
  utils      — Degree normalization, JD conversion, date helpers
"""

# Re-export commonly used items for convenience
from core.constants import (
    PLANETS_9, SIGNS, SIGN_LORDS,
    NAKSHATRAS_27, NAKSHATRA_LORDS,
    TITHIS, TITHI_PAKSHA, YOGAS, KARANAS,
    VARAS, VARA_LORDS,
    AYANAMSA_MAP, PLANET_IDS,
)
from core.types import PlanetPosition, PanchangData, LocationInfo
from core.ephemeris import (
    get_planet_position, get_all_planets,
    set_ayanamsa, get_ayanamsa_value,
)
from core.nakshatra import calc_nakshatra, get_nakshatra_info
from core.signs import calc_sign, get_sign_info
from core.panchang import get_panchang, calc_tithi, calc_yoga, calc_karana
from core.geo import calc_sunrise_sunset, resolve_location
from core.utils import (
    normalize_degree, deg_to_dms, dms_to_deg,
    datetime_to_jd, jd_to_datetime, local_to_utc,
    date_range, parse_date,
)
from core.cities import search_city, resolve_city
