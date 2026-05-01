"""
ashtakavarga module — Ashtakavarga + Strength Calendar endpoints.
"""
from __future__ import annotations

from datetime import datetime
from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.ashtakavarga import calc_sarvashtakavarga, calc_transit_dates_with_ashtakavarga
from app.ashtakavarga_strength import (
    calc_daily_strength,
    calc_monthly_strength,
    calc_yearly_strength,
)

router = APIRouter(tags=["Ashtakavarga"])


# ── schemas ───────────────────────────────────────────────────

class AshtakavargaInput(BirthDataInput):
    transit_from_date: Optional[str] = Field(
        default=None, example="2026-04-15",
        description="Start date for transit predictions (default: today)",
    )
    days_ahead: int = Field(default=180, ge=30, le=365)


class StrengthCalendarInput(BirthDataInput):
    calendar_type: str = Field(
        default="daily", example="daily",
        description="'daily', 'monthly', or 'yearly'",
    )
    from_date: Optional[str] = Field(default=None, example="2026-04-15")
    days_ahead: int = Field(default=30, ge=7, le=365)
    year: Optional[int] = Field(default=None, example=2026)
    month: Optional[int] = Field(default=None, ge=1, le=12, example=4)


# ── endpoints ─────────────────────────────────────────────────

@router.post("/ashtakavarga", summary="Ashtakavarga + Transit Date Predictions")
def ashtakavarga(payload: AshtakavargaInput):
    """BAV/SAV scores and upcoming transit predictions with market impact."""
    try:
        data = resolve_chart(payload)
        sav_data = calc_sarvashtakavarga(data.planets, data.ascendant["longitude"])

        from_date = (
            datetime.strptime(payload.transit_from_date, "%Y-%m-%d")
            if payload.transit_from_date else datetime.utcnow()
        )
        transit_preds = calc_transit_dates_with_ashtakavarga(
            data.planets, data.ascendant["longitude"],
            payload.ayanamsa, from_date, payload.days_ahead,
        )
        return {
            "type": "ashtakavarga",
            "name": payload.name,
            "birth_date": payload.date,
            "ayanamsa": payload.ayanamsa,
            "natal_planets": data.planets,
            "ascendant": data.ascendant,
            "sarvashtakavarga": sav_data,
            "transit_predictions": transit_preds,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/strength-calendar", summary="Daily/Monthly/Yearly Strength Calendar")
def strength_calendar(payload: StrengthCalendarInput):
    """Ashtakavarga strength calendar showing best/worst days for trading."""
    try:
        data = resolve_chart(payload)
        cal_type = payload.calendar_type.lower()

        if cal_type == "daily":
            fd = (
                datetime.strptime(payload.from_date, "%Y-%m-%d")
                if payload.from_date else datetime.utcnow()
            )
            cal = calc_daily_strength(
                fd, payload.days_ahead, data.planets,
                data.ascendant["longitude"], payload.ayanamsa,
            )
        elif cal_type == "monthly":
            y = payload.year or datetime.utcnow().year
            m = payload.month or datetime.utcnow().month
            cal = calc_monthly_strength(
                y, m, data.planets, data.ascendant["longitude"], payload.ayanamsa,
            )
        elif cal_type == "yearly":
            y = payload.year or datetime.utcnow().year
            cal = calc_yearly_strength(
                y, data.planets, data.ascendant["longitude"], payload.ayanamsa,
            )
        else:
            cal = calc_daily_strength(
                datetime.utcnow(), 30, data.planets,
                data.ascendant["longitude"], payload.ayanamsa,
            )

        return {
            "type": "ashtakavarga_strength_calendar",
            "name": payload.name,
            "birth_date": payload.date,
            "birth_place": data.resolved.place,
            "ayanamsa": payload.ayanamsa,
            "ascendant": data.ascendant,
            "calendar_type": cal_type,
            "calendar_data": cal,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
