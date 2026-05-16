"""
geo.py — Geographic / astronomical event calculations.
=======================================================
Sunrise, sunset, moonrise, moonset, location resolution.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Optional, Tuple

import swisseph as swe

from core.constants import DEFAULT_LOCATIONS
from core.types import LocationInfo
from core.utils import jd_to_datetime, utc_to_local


def _extract_event_jd(res) -> Optional[float]:
    """Extract Julian Day from swe.rise_trans result (handles all formats)."""
    if res is None:
        return None
    # res can be: (flag, jd), (flag, (jd,)), (flag, [jd]), tuple of tuples, etc.
    if isinstance(res, (list, tuple)) and len(res) >= 2:
        val = res[1]
        if isinstance(val, (list, tuple)):
            return float(val[0]) if len(val) > 0 else None
        return float(val)
    return None


def _try_rise_trans(jd: float, body: int, rsmi: int, geopos: tuple) -> Optional[float]:
    """
    Try multiple swe.rise_trans call signatures.
    Different pyswisseph versions have different signatures.
    Returns JD of event or None.
    """
    # Signature 1: rise_trans(tjd_ut, ipl, starname, epheflag, rsmi, geopos, atpress, attemp)
    try:
        res = swe.rise_trans(jd, body, "", swe.FLG_SWIEPH, rsmi, geopos, 0.0, 0.0)
        event_jd = _extract_event_jd(res)
        if event_jd and event_jd > jd - 1:
            return event_jd
    except (TypeError, Exception):
        pass

    # Signature 2: rise_trans(tjd_ut, ipl, geopos, atpress, attemp, rsmi)
    try:
        res = swe.rise_trans(jd, body, geopos, 0.0, 0.0, rsmi)
        event_jd = _extract_event_jd(res)
        if event_jd and event_jd > jd - 1:
            return event_jd
    except (TypeError, Exception):
        pass

    # Signature 3: rise_trans(tjd_ut, ipl, lon, lat, alt, atpress, attemp, rsmi)
    try:
        res = swe.rise_trans(jd, body, geopos[0], geopos[1], geopos[2], 0.0, 0.0, rsmi)
        event_jd = _extract_event_jd(res)
        if event_jd and event_jd > jd - 1:
            return event_jd
    except (TypeError, Exception):
        pass

    # Signature 4: rise_trans(tjd_ut, ipl, rsmi, geopos, atpress, attemp)
    try:
        res = swe.rise_trans(jd, body, rsmi, geopos, 0.0, 0.0)
        event_jd = _extract_event_jd(res)
        if event_jd and event_jd > jd - 1:
            return event_jd
    except (TypeError, Exception):
        pass

    return None


def _math_sunrise_sunset(jd: float, lat: float, lon: float) -> Tuple[Optional[float], Optional[float]]:
    """
    Mathematical sunrise/sunset calculation (fallback).
    Uses standard solar position equations.
    Returns (sunrise_jd, sunset_jd) in UTC.
    """
    # Get day of year from JD
    dt = jd_to_datetime(jd)
    day_of_year = dt.timetuple().tm_yday

    # Solar declination (approximate)
    declination = 23.45 * math.sin(math.radians(360 / 365 * (day_of_year - 81)))
    decl_rad = math.radians(declination)
    lat_rad = math.radians(lat)

    # Hour angle for sunrise/sunset (-0.833° for atmospheric refraction)
    cos_ha = (math.sin(math.radians(-0.833)) - math.sin(lat_rad) * math.sin(decl_rad)) / \
             (math.cos(lat_rad) * math.cos(decl_rad))

    if cos_ha > 1 or cos_ha < -1:
        return None, None  # No sunrise/sunset (polar)

    ha = math.degrees(math.acos(cos_ha))

    # Solar noon in UTC (approximate equation of time)
    b = math.radians(360 / 365 * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)  # minutes
    solar_noon_utc = 12.0 - (lon / 15.0) - (eot / 60.0)  # hours UTC

    sunrise_utc = solar_noon_utc - ha / 15.0
    sunset_utc = solar_noon_utc + ha / 15.0

    # Convert to JD
    base_jd = jd - (jd % 1) + 0.5  # midnight JD
    if base_jd > jd:
        base_jd -= 1.0

    sunrise_jd = base_jd + sunrise_utc / 24.0
    sunset_jd = base_jd + sunset_utc / 24.0

    return sunrise_jd, sunset_jd


def calc_sunrise_sunset(
    jd: float, lat: float, lon: float, tz_offset: float = 5.5
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Calculate sunrise, sunset, moonrise, moonset for JD + location.
    Returns HH:MM strings in LOCAL time (adjusted by tz_offset).
    Tries Swiss Ephemeris first, falls back to mathematical calculation.
    """
    geopos = (lon, lat, 0.0)
    results = {}

    for label, body, rsmi in [
        ("sunrise",  swe.SUN,  1),
        ("sunset",   swe.SUN,  2),
        ("moonrise", swe.MOON, 1),
        ("moonset",  swe.MOON, 2),
    ]:
        event_jd = _try_rise_trans(jd, body, rsmi, geopos)
        if event_jd:
            dt_utc = jd_to_datetime(event_jd)
            dt_local = utc_to_local(dt_utc, tz_offset)
            results[label] = dt_local.strftime("%H:%M")

    # Fallback: if swe.rise_trans didn't work for sun, use math
    if not results.get("sunrise") or not results.get("sunset"):
        sr_jd, ss_jd = _math_sunrise_sunset(jd, lat, lon)
        if sr_jd and "sunrise" not in results:
            dt_local = utc_to_local(jd_to_datetime(sr_jd), tz_offset)
            results["sunrise"] = dt_local.strftime("%H:%M")
        if ss_jd and "sunset" not in results:
            dt_local = utc_to_local(jd_to_datetime(ss_jd), tz_offset)
            results["sunset"] = dt_local.strftime("%H:%M")

    return (
        results.get("sunrise"),
        results.get("sunset"),
        results.get("moonrise"),
        results.get("moonset"),
    )


def resolve_location(
    name: Optional[str] = None,
    lat: Optional[float] = None,
    lon: Optional[float] = None,
    tz_offset: Optional[float] = None,
) -> LocationInfo:
    """
    Resolve a location from name or coordinates.
    Falls back to Mumbai if nothing provided.
    """
    if lat is not None and lon is not None:
        return LocationInfo(
            name=name or "Custom",
            latitude=lat,
            longitude=lon,
            tz_offset=tz_offset or 5.5,
        )

    if name and name.lower() in DEFAULT_LOCATIONS:
        loc = DEFAULT_LOCATIONS[name.lower()]
        return LocationInfo(
            name=loc["name"],
            latitude=loc["lat"],
            longitude=loc["lon"],
            tz_offset=loc["tz"],
        )

    # Default: Mumbai
    return LocationInfo(name="Mumbai", latitude=19.0760, longitude=72.8777, tz_offset=5.5)
