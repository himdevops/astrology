"""
panchang.py — Tithi, Yoga, Karana, Vara calculations + full Panchang.
======================================================================
Depends on ephemeris.py for planet positions, geo.py for sunrise.
"""
from __future__ import annotations

from datetime import datetime
from typing import Tuple

from core.constants import (
    TITHIS, TITHI_PAKSHA, YOGAS, KARANAS,
    VARAS, VARA_LORDS,
)
from core.types import PanchangData
from core.utils import normalize_degree, local_to_utc, datetime_to_jd
from core.ephemeris import get_planet_position, set_ayanamsa
from core.geo import calc_sunrise_sunset


def calc_tithi(sun_lon: float, moon_lon: float) -> Tuple[int, str, str]:
    """Tithi from Sun–Moon elongation. Returns (index, name, paksha)."""
    diff = normalize_degree(moon_lon - sun_lon)
    index = int(diff / 12) % 30
    return index, TITHIS[index], TITHI_PAKSHA[index]


def calc_yoga(sun_lon: float, moon_lon: float) -> str:
    """Yoga from Sun + Moon longitudes."""
    total = normalize_degree(sun_lon + moon_lon)
    index = int(total / (360 / 27)) % 27
    return YOGAS[index]


def calc_karana(sun_lon: float, moon_lon: float) -> str:
    """Karana from Sun–Moon difference."""
    diff = normalize_degree(moon_lon - sun_lon)
    ki = int(diff / 6) % 60
    if ki == 0:
        return "Kimstughna"
    elif ki == 57:
        return "Shakuni"
    elif ki == 58:
        return "Chatushpada"
    elif ki == 59:
        return "Nagava"
    return KARANAS[(ki - 1) % 7]


def calc_vara(dt: datetime) -> Tuple[str, str]:
    """Weekday name and lord from datetime. Returns (vara, lord)."""
    idx = (dt.weekday() + 1) % 7  # Python Mon=0 → Sunday=0
    return VARAS[idx], VARA_LORDS[idx]


def get_panchang(
    dt: datetime,
    lat: float = 23.1765,
    lon: float = 75.7885,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> PanchangData:
    """
    Compute full Panchang for a given local datetime + location.
    This is the main entry point for Panchang data.
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    sun = get_planet_position(jd, "Sun", ayanamsa)
    moon = get_planet_position(jd, "Moon", ayanamsa)

    tithi_idx, tithi, paksha = calc_tithi(sun.longitude, moon.longitude)
    yoga = calc_yoga(sun.longitude, moon.longitude)
    karana = calc_karana(sun.longitude, moon.longitude)
    vara, vara_lord = calc_vara(dt)

    # Sunrise/sunset at start of day
    sunrise_dt = dt.replace(hour=0, minute=0, second=0)
    sunrise_utc = local_to_utc(sunrise_dt, tz_offset)
    sunrise_jd = datetime_to_jd(sunrise_utc)
    sunrise, sunset, moonrise, moonset = calc_sunrise_sunset(sunrise_jd, lat, lon, tz_offset)

    return PanchangData(
        date=dt.strftime("%d-%m-%Y"),
        weekday=vara,
        weekday_lord=vara_lord,
        tithi_index=tithi_idx,
        tithi=tithi,
        paksha=paksha,
        nakshatra=moon.nakshatra,
        nakshatra_lord=moon.nakshatra_lord,
        yoga=yoga,
        karana=karana,
        sunrise=sunrise or "N/A",
        sunset=sunset or "N/A",
        moonrise=moonrise or "N/A",
        moonset=moonset or "N/A",
        sun_longitude=sun.longitude,
        moon_longitude=moon.longitude,
    )
