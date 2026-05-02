"""
panchang module — Panchang & Muhurta endpoints.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field

from app.panchang import calculate_panchang, calculate_panchang_calendar
from app.muhurta_advanced import (
    calculate_advanced_muhurta, get_activity_list, MUHURTA_ACTIVITIES,
    find_muhurta_dates,
)

router = APIRouter(tags=["v3.0 — Panchang"])


# ── schemas ───────────────────────────────────────────────────

class PanchangInput(BaseModel):
    date: str  = Field(...,  example="2026-04-28")
    time: str  = Field(default="09:15", example="09:15")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None, example=19.076)
    longitude: Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: int = Field(default=330)
    ayanamsa: str = Field(default="lahiri")


class PanchangCalendarInput(BaseModel):
    start_date: str = Field(..., example="2026-04-01")
    days: int = Field(default=30, ge=7, le=365)
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None, example=19.076)
    longitude: Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: int = Field(default=330)
    ayanamsa: str = Field(default="lahiri")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/panchang", summary="Daily Panchang with Muhurta")
def panchang(payload: PanchangInput):
    """
    Tithi, Nakshatra, Yoga, Karana, Vara + Muhurta windows
    (Rahu Kalam, Gulika, Abhijit, Choghadiya).
    """
    try:
        lat = payload.latitude or 19.076
        lon = payload.longitude or 72.8777
        return calculate_panchang(
            payload.date, payload.time, lat, lon,
            payload.timezone_offset_minutes, payload.ayanamsa,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/panchang-calendar", summary="Multi-day Panchang Trading Calendar")
def panchang_calendar(payload: PanchangCalendarInput):
    """Best/worst trading days based on Panchang financial scores."""
    try:
        lat = payload.latitude or 19.076
        lon = payload.longitude or 72.8777
        return calculate_panchang_calendar(
            payload.start_date, payload.days, lat, lon,
            payload.timezone_offset_minutes, payload.ayanamsa,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


# ── Advanced Muhurta schemas ─────────────────────────────────

class AdvancedMuhurtaInput(BaseModel):
    date: str = Field(..., example="2026-05-02")
    time: str = Field(default="09:15", example="09:15")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude: Optional[float] = Field(default=None, example=19.076)
    longitude: Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: int = Field(default=330)
    ayanamsa: str = Field(default="lahiri")
    activity: str = Field(default="vyapara", example="vivaha")
    birth_nakshatra: Optional[str] = Field(default=None, example="Rohini")
    birth_moon_sign: Optional[str] = Field(default=None, example="Taurus")


# ── Advanced Muhurta endpoints ───────────────────────────────

@router.post("/muhurta/advanced", summary="Advanced Muhurta Analysis (Muhurta Martanda)")
def advanced_muhurta(payload: AdvancedMuhurtaInput):
    """
    Comprehensive electional astrology analysis based on Muhurta Martanda.
    Checks: Panchanga Shuddhi, Tara Bala, Chandra Bala, Doshas (Dagdha,
    Mrityu, Panchaka, Rikta), Nakshatra/Tithi/Vara fitness for activity,
    Lagna Shuddhi, Hora, and 25+ activity-specific rules.
    """
    try:
        lat = payload.latitude or 19.076
        lon = payload.longitude or 72.8777
        return calculate_advanced_muhurta(
            date_str=payload.date,
            time_str=payload.time,
            latitude=lat,
            longitude_geo=lon,
            timezone_offset_minutes=payload.timezone_offset_minutes,
            ayanamsa_key=payload.ayanamsa,
            activity=payload.activity,
            birth_nakshatra=payload.birth_nakshatra,
            birth_moon_sign=payload.birth_moon_sign,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.get("/muhurta/activities", summary="List all Muhurta activities")
def muhurta_activities():
    """Return list of all 25+ activity types available for muhurta analysis."""
    return {"activities": get_activity_list()}


# ── Automated Muhurta Finder schemas ────────────────────────

class MuhurtaFinderInput(BaseModel):
    activity: str = Field(..., example="vivaha")
    start_date: str = Field(..., example="2026-05-01")
    months_ahead: int = Field(default=6, ge=1, le=12)
    person_name: str = Field(default="", example="Priya")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude: Optional[float] = Field(default=None, example=19.076)
    longitude: Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: int = Field(default=330)
    ayanamsa: str = Field(default="lahiri")
    birth_nakshatra: Optional[str] = Field(default=None, example="Rohini")
    birth_moon_sign: Optional[str] = Field(default=None, example="Taurus")
    min_score: float = Field(default=0.0, ge=0, le=100)
    time: str = Field(default="09:15", example="09:15")


# ── Automated Muhurta Finder endpoint ───────────────────────

@router.post("/muhurta/find-dates", summary="Find Auspicious Muhurta Dates")
def find_muhurta_dates_endpoint(payload: MuhurtaFinderInput):
    """
    Scan a date range (1-12 months) and return ranked list of
    auspicious dates for any of the 26 muhurta activities.
    Personalized with birth nakshatra and moon sign for Tara/Chandra Bala.
    """
    try:
        lat = payload.latitude or 19.076
        lon = payload.longitude or 72.8777
        return find_muhurta_dates(
            activity=payload.activity,
            start_date=payload.start_date,
            months_ahead=payload.months_ahead,
            person_name=payload.person_name,
            latitude=lat,
            longitude_geo=lon,
            timezone_offset_minutes=payload.timezone_offset_minutes,
            ayanamsa_key=payload.ayanamsa,
            birth_nakshatra=payload.birth_nakshatra,
            birth_moon_sign=payload.birth_moon_sign,
            min_score=payload.min_score,
            time_str=payload.time,
        )
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
