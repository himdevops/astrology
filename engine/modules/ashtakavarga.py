"""
ashtakavarga.py — Ashtakavarga module (orchestrator).
======================================================
Takes birth data → produces BAV, SAV, Kaksha, Pinda Shodhana,
and advanced Kaksha-based transit predictions (hourly/minute precision).
"""
from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, Any, Optional

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc
from core.constants import SIGNS
from core.ashtakavarga import (
    calc_full_ashtakavarga, ASHTAK_PLANETS, _get_sign_index,
    calc_sav, calc_all_bav,
)
from core.transit_predict import predict_date_range, summarize_month
from core.kaksha_transit import (
    compute_monthly_kaksha_grid,
    compute_daily_kaksha_grid,
    compute_minute_detail,
)


def _get_transit_fn(ayanamsa: str):
    """Return a callable that gets transit planet positions for a Julian Day."""
    def get_positions(jd: float) -> dict:
        positions = get_all_planets(jd, ayanamsa)
        result = {}
        for pp in positions:
            if pp.planet in ASHTAK_PLANETS:
                sign_idx = _get_sign_index(pp.longitude)
                result[pp.planet] = (pp.longitude, sign_idx)
        return result
    return get_positions


def _get_birth_signs(planet_lons: Dict[str, float], asc_lon: float) -> Dict[str, int]:
    """Get birth chart sign indices for all planets + Lagna."""
    signs = {}
    for planet in ASHTAK_PLANETS:
        if planet in planet_lons:
            signs[planet] = _get_sign_index(planet_lons[planet])
    signs["Lagna"] = _get_sign_index(asc_lon)
    return signs


def generate_ashtakavarga(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    predict_start: Optional[date] = None,
    predict_end: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Generate complete Ashtakavarga analysis with advanced Kaksha transit predictions.
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    # Birth chart positions
    planet_positions = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)

    planet_lons = {}
    for pp in planet_positions:
        planet_lons[pp.planet] = pp.longitude

    # Full Ashtakavarga
    ashtak = calc_full_ashtakavarga(planet_lons, ascendant.longitude)

    # Birth sign positions (needed for kaksha benefic checks)
    birth_signs = _get_birth_signs(planet_lons, ascendant.longitude)

    result = {
        "birth_info": {
            "date": birth_dt.strftime("%d-%m-%Y"),
            "time": birth_dt.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "tz_offset": tz_offset,
            "ayanamsa": ayanamsa,
        },
        "ashtakavarga": ashtak,
    }

    # Transit predictions if date range given
    if predict_start and predict_end:
        all_bav = ashtak["bav"]
        sav = ashtak["sav"]
        transit_fn = _get_transit_fn(ayanamsa)

        # Legacy daily predictions (kept for backward compatibility)
        daily = predict_date_range(
            predict_start, predict_end,
            all_bav, sav, transit_fn, tz_offset,
        )
        summary = summarize_month(daily)

        # Advanced Kaksha grid (Parashara Light-style)
        kaksha_grid = compute_monthly_kaksha_grid(
            predict_start, predict_end,
            all_bav, sav, birth_signs,
            transit_fn, tz_offset,
        )

        result["predictions"] = {
            "start": predict_start.strftime("%d-%m-%Y"),
            "end": predict_end.strftime("%d-%m-%Y"),
            "daily": daily,
            "summary": summary,
            "kaksha_grid": kaksha_grid,
        }

    return result


def generate_daily_detail(
    birth_dt: datetime,
    lat: float,
    lon: float,
    target_date: date,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Generate hourly kaksha detail for a specific day.
    Returns 24-hour breakdown with per-planet kaksha transitions.
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    planet_positions = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)

    planet_lons = {}
    for pp in planet_positions:
        planet_lons[pp.planet] = pp.longitude

    ashtak = calc_full_ashtakavarga(planet_lons, ascendant.longitude)
    birth_signs = _get_birth_signs(planet_lons, ascendant.longitude)
    transit_fn = _get_transit_fn(ayanamsa)

    return compute_daily_kaksha_grid(
        target_date,
        ashtak["bav"], ashtak["sav"], birth_signs,
        transit_fn, tz_offset,
    )


def generate_minute_detail(
    birth_dt: datetime,
    lat: float,
    lon: float,
    target_date: date,
    target_hour: int,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    interval_minutes: int = 10,
) -> Dict[str, Any]:
    """
    Generate minute-level kaksha detail for a specific hour.
    Returns sub-hour slices (default: every 10 min).
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    planet_positions = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)

    planet_lons = {}
    for pp in planet_positions:
        planet_lons[pp.planet] = pp.longitude

    ashtak = calc_full_ashtakavarga(planet_lons, ascendant.longitude)
    birth_signs = _get_birth_signs(planet_lons, ascendant.longitude)
    transit_fn = _get_transit_fn(ayanamsa)

    return compute_minute_detail(
        target_date, target_hour,
        ashtak["bav"], ashtak["sav"], birth_signs,
        transit_fn, tz_offset, interval_minutes,
    )
