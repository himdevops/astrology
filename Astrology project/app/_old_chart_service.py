"""
chart_service.py — Unified Chart Calculation Service
Orchestrates all astrological calculations including birth charts,
transits, dashas, divisional charts, ashtakavarga, yogas, and predictions.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from app.core import (
    build_house_cusps,
    calculate_ascendant,
    calculate_planets,
    resolve_location_and_time,
    to_julian_day_utc,
)
from app.schemas import (
    AshtakavargaInput,
    BirthInput,
    DashaInput,
    DivisionalInput,
    FullPredictionInput,
    SarvatobhadraInput,
    StrengthCalendarInput,
    TransitAlertInput,
    TransitInput,
    YogaInput,
    ShadbalaInput,
    BhavaChalitInput,
    KPAnalysisInput,
    PanchangInput,
    PanchangCalendarInput,
    BacktestInput,
)
from app.nakshatra import get_all_planet_nakshatras, get_moon_nakshatra_signal
from app.dasha import calculate_vimshottari_dasha, get_current_dasha
from app.divisional import calculate_all_divisional
from app.sarvatobhadra import calculate_sarvatobhadra as cast_sarvatobhadra
from app.ashtakavarga import calc_sarvashtakavarga, calc_transit_dates_with_ashtakavarga
from app.ashtakavarga_strength import (
    calc_daily_strength,
    calc_monthly_strength,
    calc_yearly_strength,
)
from app.yoga_detector import detect_all_yogas
from app.transit_alerts import generate_transit_alerts
from app.prediction_engine import generate_market_prediction
from app.shadbala import calculate_shadbala, calculate_bhava_chalit
from app.kp_system import calculate_kp_analysis
from app.panchang import calculate_panchang, calculate_panchang_calendar
from app.market_data import get_current_prices, get_historical_data, get_sector_performance
from app.backtesting import backtest_moon_nakshatra, backtest_planetary_transits, backtest_composite


# ─────────────────────────────────────────────────────────────
# Birth Chart
# ─────────────────────────────────────────────────────────────

def calculate_birth_chart(payload: BirthInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    houses = build_house_cusps(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    planet_nakshatras = get_all_planet_nakshatras(planets)

    return {
        "type": "birth_chart",
        "name": payload.name,
        "input": {
            "date": payload.date,
            "time": payload.time,
            "place": resolved.place,
            "latitude": resolved.latitude,
            "longitude": resolved.longitude,
            "timezone_name": resolved.timezone_name,
            "timezone_offset_minutes": resolved.timezone_offset_minutes,
            "ayanamsa": payload.ayanamsa,
        },
        "ascendant": ascendant,
        "planets": planets,
        "planet_nakshatras": planet_nakshatras,
        "houses": houses,
    }


# ─────────────────────────────────────────────────────────────
# Transits
# ─────────────────────────────────────────────────────────────

def calculate_transits(payload: TransitInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    planet_nakshatras = get_all_planet_nakshatras(planets)

    moon = next((p for p in planets if p["planet"] == "Moon"), None)
    moon_signal = get_moon_nakshatra_signal(moon["longitude"]) if moon else {}

    return {
        "type": "transits",
        "input": {
            "date": payload.date,
            "time": payload.time,
            "place": resolved.place,
            "latitude": resolved.latitude,
            "longitude": resolved.longitude,
            "timezone_name": resolved.timezone_name,
            "timezone_offset_minutes": resolved.timezone_offset_minutes,
            "ayanamsa": payload.ayanamsa,
        },
        "planets": planets,
        "planet_nakshatras": planet_nakshatras,
        "moon_nakshatra_signal": moon_signal,
    }


# ─────────────────────────────────────────────────────────────
# Dasha
# ─────────────────────────────────────────────────────────────

def calculate_dasha(payload: DashaInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)

    moon = next((p for p in planets if p["planet"] == "Moon"), None)
    if not moon:
        raise ValueError("Moon position not found in chart")

    dasha_data = calculate_vimshottari_dasha(moon["longitude"], local_dt, payload.years_to_show)
    as_of = datetime.strptime(payload.as_of_date, "%Y-%m-%d") if payload.as_of_date else datetime.utcnow()
    current = get_current_dasha(dasha_data, as_of)

    return {
        "type":          "vimshottari_dasha",
        "name":          payload.name,
        "birth_date":    payload.date,
        "birth_time":    payload.time,
        "birth_place":   resolved.place,
        "ayanamsa":      payload.ayanamsa,
        "dasha_data":    dasha_data,
        "current_dasha": current,
    }


# ─────────────────────────────────────────────────────────────
# Divisional Charts
# ─────────────────────────────────────────────────────────────

def calculate_divisional(payload: DivisionalInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    divisional_charts = calculate_all_divisional(planets, ascendant, payload.charts)

    return {
        "type":       "divisional_charts",
        "name":       payload.name,
        "birth_date": payload.date,
        "ayanamsa":   payload.ayanamsa,
        "ascendant":  ascendant,
        "charts":     divisional_charts,
    }


def calculate_sarvatobhadra(payload: SarvatobhadraInput) -> dict:
    return cast_sarvatobhadra(payload)


# ─────────────────────────────────────────────────────────────
# Ashtakavarga + Transit Dates
# ─────────────────────────────────────────────────────────────

def calculate_ashtakavarga(payload: AshtakavargaInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    sav_data = calc_sarvashtakavarga(planets, ascendant["longitude"])

    from_date = (
        datetime.strptime(payload.transit_from_date, "%Y-%m-%d")
        if payload.transit_from_date else datetime.utcnow()
    )
    transit_predictions = calc_transit_dates_with_ashtakavarga(
        planets, ascendant["longitude"], payload.ayanamsa, from_date, payload.days_ahead
    )

    return {
        "type":                 "ashtakavarga",
        "name":                 payload.name,
        "birth_date":           payload.date,
        "ayanamsa":             payload.ayanamsa,
        "natal_planets":        planets,
        "ascendant":            ascendant,
        "sarvashtakavarga":     sav_data,
        "transit_predictions":  transit_predictions,
    }


# ─────────────────────────────────────────────────────────────
# Yoga Detection
# ─────────────────────────────────────────────────────────────

def calculate_yogas(payload: YogaInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    yogas = detect_all_yogas(planets, ascendant)

    return {
        "type":       "yoga_detection",
        "name":       payload.name,
        "birth_date": payload.date,
        "ayanamsa":   payload.ayanamsa,
        "ascendant":  ascendant,
        "planets":    planets,
        "yogas":      yogas,
    }


# ─────────────────────────────────────────────────────────────
# Transit Alerts
# ─────────────────────────────────────────────────────────────

def calculate_transit_alerts(payload: TransitAlertInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    current_planets = calculate_planets(jd_ut, payload.ayanamsa)

    natal_planets = None
    natal_ascendant = None
    if payload.natal_date and payload.natal_time and payload.natal_place:
        nr, ndt = resolve_location_and_time(
            place=payload.natal_place,
            date_str=payload.natal_date,
            time_str=payload.natal_time,
            latitude=None,
            longitude=None,
            timezone_offset_minutes=None,
        )
        njd = to_julian_day_utc(ndt, nr.timezone_offset_minutes)
        natal_planets = calculate_planets(njd, payload.ayanamsa)
        natal_ascendant = calculate_ascendant(njd, nr.latitude, nr.longitude, payload.ayanamsa)

    alerts = generate_transit_alerts(
        current_planets, natal_planets, natal_ascendant,
        local_dt, payload.days_ahead, payload.ayanamsa,
    )

    return {
        "type":            "transit_alerts",
        "date":            payload.date,
        "place":           resolved.place,
        "current_planets": current_planets,
        "alerts":          alerts,
    }


# ─────────────────────────────────────────────────────────────
# Full Autonomous Prediction
# ─────────────────────────────────────────────────────────────

def calculate_full_prediction(payload: FullPredictionInput) -> dict:
    """
    The main autonomous prediction endpoint.
    Combines all signals for NSE/BSE market prediction.
    """
    transit_resolved, transit_dt = resolve_location_and_time(
        place=payload.transit_place,
        date_str=payload.transit_date,
        time_str=payload.transit_time,
        latitude=payload.transit_latitude,
        longitude=payload.transit_longitude,
        timezone_offset_minutes=None,
    )
    transit_jd = to_julian_day_utc(transit_dt, transit_resolved.timezone_offset_minutes)
    current_planets = calculate_planets(transit_jd, payload.ayanamsa)

    transit_alert_data = generate_transit_alerts(
        current_planets, None, None, transit_dt, payload.days_ahead, payload.ayanamsa
    )

    current_dasha_data = None
    yoga_data = None
    natal_chart_data = None

    if all([payload.natal_date, payload.natal_time, payload.natal_place]):
        nr, ndt = resolve_location_and_time(
            place=payload.natal_place,
            date_str=payload.natal_date,
            time_str=payload.natal_time,
            latitude=payload.natal_latitude,
            longitude=payload.natal_longitude,
            timezone_offset_minutes=None,
        )
        njd = to_julian_day_utc(ndt, nr.timezone_offset_minutes)
        natal_planets = calculate_planets(njd, payload.ayanamsa)
        natal_ascendant = calculate_ascendant(njd, nr.latitude, nr.longitude, payload.ayanamsa)

        moon = next((p for p in natal_planets if p["planet"] == "Moon"), None)
        if moon:
            dasha_full = calculate_vimshottari_dasha(moon["longitude"], ndt)
            current_dasha_data = get_current_dasha(dasha_full, transit_dt)

        yoga_data = detect_all_yogas(natal_planets, natal_ascendant)
        natal_chart_data = {
            "date": payload.natal_date,
            "place": nr.place,
            "ascendant": natal_ascendant,
            "planets": natal_planets,
        }

    prediction = generate_market_prediction(
        current_planets=current_planets,
        current_date=transit_dt,
        current_dasha=current_dasha_data,
        yoga_data=yoga_data,
        transit_data=transit_alert_data,
        natal_chart=natal_chart_data,
    )

    return {
        "type":            "full_market_prediction",
        "prediction_date": payload.transit_date,
        "market":          "NSE/BSE India",
        "current_planets": current_planets,
        "natal_chart":     natal_chart_data,
        "transit_alerts":  transit_alert_data,
        "prediction":      prediction,
    }


# ─────────────────────────────────────────────────────────────
# Ashtakavarga Strength Calendar
# ─────────────────────────────────────────────────────────────

def calculate_strength_calendar(payload: StrengthCalendarInput) -> dict:
    """
    Calculate Ashtakavarga strength calendar (daily/monthly/yearly).
    Shows which planets are strong and best/worst days for activities.
    """
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)

    calendar_type = payload.calendar_type.lower()

    if calendar_type == "daily":
        from_date = datetime.strptime(payload.from_date, "%Y-%m-%d") if payload.from_date else datetime.utcnow()
        calendar_data = calc_daily_strength(
            from_date, payload.days_ahead, planets, ascendant["longitude"], payload.ayanamsa
        )
    elif calendar_type == "monthly":
        year = payload.year if payload.year else datetime.utcnow().year
        month = payload.month if payload.month else datetime.utcnow().month
        calendar_data = calc_monthly_strength(year, month, planets, ascendant["longitude"], payload.ayanamsa)
    elif calendar_type == "yearly":
        year = payload.year if payload.year else datetime.utcnow().year
        calendar_data = calc_yearly_strength(year, planets, ascendant["longitude"], payload.ayanamsa)
    else:
        calendar_data = calc_daily_strength(
            datetime.utcnow(), 30, planets, ascendant["longitude"], payload.ayanamsa
        )

    return {
        "type":              "ashtakavarga_strength_calendar",
        "name":              payload.name,
        "birth_date":        payload.date,
        "birth_place":       resolved.place,
        "ayanamsa":          payload.ayanamsa,
        "ascendant":         ascendant,
        "calendar_type":     calendar_type,
        "calendar_data":     calendar_data,
    }


# ─────────────────────────────────────────────────────────────
# Shadbala (Six-fold Planetary Strength)
# ─────────────────────────────────────────────────────────────

def calculate_shadbala_endpoint(payload: ShadbalaInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)

    shadbala = calculate_shadbala(planets, ascendant, local_dt, resolved.latitude)

    return {
        "type": "shadbala",
        "name": payload.name,
        "birth_date": payload.date,
        "ayanamsa": payload.ayanamsa,
        "ascendant": ascendant,
        "shadbala": shadbala,
    }


# ─────────────────────────────────────────────────────────────
# Bhava Chalit Chart
# ─────────────────────────────────────────────────────────────

def calculate_bhava_chalit_endpoint(payload: BhavaChalitInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    houses = build_house_cusps(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)

    chalit = calculate_bhava_chalit(planets, houses, ascendant)

    return {
        "type": "bhava_chalit",
        "name": payload.name,
        "birth_date": payload.date,
        "ayanamsa": payload.ayanamsa,
        "ascendant": ascendant,
        "bhava_chalit": chalit,
    }


# ─────────────────────────────────────────────────────────────
# KP System Analysis
# ─────────────────────────────────────────────────────────────

def calculate_kp_endpoint(payload: KPAnalysisInput) -> dict:
    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=payload.latitude,
        longitude=payload.longitude,
        timezone_offset_minutes=payload.timezone_offset_minutes,
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)
    houses = build_house_cusps(jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa)

    # Transit planets for ruling planets
    transit_planets = None
    transit_dt = None
    if payload.transit_date:
        t_resolved, t_dt = resolve_location_and_time(
            place=payload.place,
            date_str=payload.transit_date,
            time_str=payload.transit_time or "09:15",
            latitude=payload.latitude,
            longitude=payload.longitude,
            timezone_offset_minutes=payload.timezone_offset_minutes,
        )
        t_jd = to_julian_day_utc(t_dt, t_resolved.timezone_offset_minutes)
        transit_planets = calculate_planets(t_jd, payload.ayanamsa)
        transit_dt = t_dt

    kp_data = calculate_kp_analysis(
        planets, houses, ascendant, transit_planets, transit_dt
    )

    return {
        "type": "kp_analysis",
        "name": payload.name,
        "birth_date": payload.date,
        "ayanamsa": payload.ayanamsa,
        "ascendant": ascendant,
        "kp_analysis": kp_data,
    }


# ─────────────────────────────────────────────────────────────
# Panchang
# ─────────────────────────────────────────────────────────────

def calculate_panchang_endpoint(payload: PanchangInput) -> dict:
    lat = payload.latitude or 19.076
    lon = payload.longitude or 72.8777
    return calculate_panchang(
        payload.date, payload.time, lat, lon,
        payload.timezone_offset_minutes, payload.ayanamsa
    )


def calculate_panchang_calendar_endpoint(payload: PanchangCalendarInput) -> dict:
    lat = payload.latitude or 19.076
    lon = payload.longitude or 72.8777
    return calculate_panchang_calendar(
        payload.start_date, payload.days, lat, lon,
        payload.timezone_offset_minutes, payload.ayanamsa
    )


# ─────────────────────────────────────────────────────────────
# Market Data
# ─────────────────────────────────────────────────────────────

def get_market_prices_endpoint(indices: list) -> dict:
    return get_current_prices(indices)


def get_sector_perf_endpoint(period: str = "1mo") -> dict:
    return get_sector_performance(period)


# ─────────────────────────────────────────────────────────────
# Backtesting
# ─────────────────────────────────────────────────────────────

def run_backtest_endpoint(payload: BacktestInput) -> dict:
    market = get_historical_data(
        payload.ticker, payload.start_date, payload.end_date
    )
    if "error" in market:
        return market

    data = market.get("data", [])
    if len(data) < 30:
        return {"error": "Insufficient market data for backtesting (need 30+ days)"}

    if payload.signal_type == "moon_nakshatra":
        return backtest_moon_nakshatra(data, payload.ayanamsa)
    elif payload.signal_type == "planetary_transits":
        return backtest_planetary_transits(data, payload.ayanamsa)
    else:
        return backtest_composite(data, payload.ayanamsa)
