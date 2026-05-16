"""Ashtakavarga API routes — BAV, SAV, Kaksha, Pinda, and advanced transit predictions."""
from __future__ import annotations

from datetime import datetime, date, timedelta

from fastapi import APIRouter, HTTPException

from api.schemas import AshtakavargaInput
from core.utils import parse_date
from core.cities import resolve_city
from modules.ashtakavarga import (
    generate_ashtakavarga,
    generate_daily_detail,
    generate_minute_detail,
)

router = APIRouter(prefix="/api/v1/ashtakavarga", tags=["Ashtakavarga"])


@router.post("", summary="Calculate Ashtakavarga with advanced Kaksha transit predictions")
def ashtakavarga_calc(payload: AshtakavargaInput):
    """
    Calculate complete Ashtakavarga system:
    - BAV (Bhinnashtakavarga) for 7 planets
    - SAV (Sarvashtakavarga)
    - Kaksha-based details
    - Pinda Shodhana (Trikona + Ekadhipatya + Graha/Rashi/Yoga Pinda)
    - Advanced Kaksha transit grid with multi-layer scoring
    """
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        # Parse prediction date range
        pred_start = None
        pred_end = None
        if payload.predict_start:
            pred_start = parse_date(payload.predict_start)
        if payload.predict_end:
            pred_end = parse_date(payload.predict_end)

        # Default: current month if no range given
        if pred_start is None:
            today = date.today()
            pred_start = today.replace(day=1)
        if pred_end is None:
            if pred_start.month == 12:
                pred_end = date(pred_start.year + 1, 1, 1) - timedelta(days=1)
            else:
                pred_end = date(pred_start.year, pred_start.month + 1, 1) - timedelta(days=1)

        # Cap range to 366 days max
        if (pred_end - pred_start).days > 366:
            pred_end = pred_start + timedelta(days=366)

        result = generate_ashtakavarga(
            dt, lat, lon, tz, payload.ayanamsa,
            pred_start, pred_end,
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/daily", summary="Get hourly Kaksha detail for a specific day")
def ashtakavarga_daily(payload: AshtakavargaInput):
    """
    Get 24-hour kaksha breakdown for a specific day.
    Uses predict_start as the target day.
    Returns per-planet kaksha transitions, hourly scores, best/worst hours.
    """
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        target = date.today()
        if payload.predict_start:
            target = parse_date(payload.predict_start)

        result = generate_daily_detail(
            dt, lat, lon, target, tz, payload.ayanamsa,
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))


@router.post("/minute", summary="Get minute-level Kaksha detail for a specific hour")
def ashtakavarga_minute(payload: AshtakavargaInput):
    """
    Get minute-level kaksha breakdown for a specific hour.
    predict_start = target day, predict_end = hour (format: "HH" like "14").
    """
    try:
        d = parse_date(payload.date)
        parts = payload.time.split(":")
        dt = datetime(d.year, d.month, d.day, int(parts[0]), int(parts[1]))

        lat, lon, tz = payload.latitude, payload.longitude, payload.tz_offset
        if payload.city:
            loc = resolve_city(payload.city)
            if loc:
                lat, lon, tz = loc.latitude, loc.longitude, loc.tz_offset

        target = date.today()
        if payload.predict_start:
            target = parse_date(payload.predict_start)

        target_hour = datetime.now().hour
        if payload.predict_end:
            try:
                target_hour = int(payload.predict_end.split("-")[0])
            except (ValueError, IndexError):
                pass

        result = generate_minute_detail(
            dt, lat, lon, target, target_hour,
            tz, payload.ayanamsa, interval_minutes=10,
        )
        return result
    except Exception as e:
        raise HTTPException(400, str(e))
