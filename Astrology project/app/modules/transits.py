"""
transits module — Transit Alert System endpoint.
"""
from __future__ import annotations

from typing import Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import TransitDataInput, resolve_chart
from app.core import (
    resolve_location_and_time,
    to_julian_day_utc,
    calculate_planets,
    calculate_ascendant,
)
from app.transit_alerts import generate_transit_alerts

router = APIRouter(tags=["Alerts"])


# ── schemas ───────────────────────────────────────────────────

class TransitAlertInput(TransitDataInput):
    days_ahead: int = Field(default=90, ge=7, le=365)
    natal_date:  Optional[str] = Field(default=None, example="1990-01-15")
    natal_time:  Optional[str] = Field(default=None, example="10:30")
    natal_place: Optional[str] = Field(default=None, example="Mumbai, Maharashtra, India")


# ── endpoints ─────────────────────────────────────────────────

@router.post("/transit-alerts", summary="NSE/BSE Transit Alert System")
def transit_alerts(payload: TransitAlertInput):
    """
    Sign ingress, retrograde, eclipse, critical-degree, and conjunction
    alerts.  Optional natal chart overlay for personal transits.
    """
    try:
        data = resolve_chart(payload, need_ascendant=False)

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
            natal_ascendant = calculate_ascendant(
                njd, nr.latitude, nr.longitude, payload.ayanamsa,
            )

        alerts = generate_transit_alerts(
            data.planets, natal_planets, natal_ascendant,
            data.local_dt, payload.days_ahead, payload.ayanamsa,
        )
        return {
            "type": "transit_alerts",
            "date": payload.date,
            "place": data.resolved.place,
            "current_planets": data.planets,
            "alerts": alerts,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
