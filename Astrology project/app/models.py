"""
models.py — Shared base Pydantic models and helpers for all modules.
Every module inherits from these so adding a new feature requires ZERO
boilerplate for the common birth-data / transit-data pattern.
"""
from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# Reusable base schemas
# ─────────────────────────────────────────────────────────────

class BirthDataInput(BaseModel):
    """Base schema for any endpoint that needs birth chart data."""
    name: str            = Field(default="Chart",   example="Himanshu")
    date: str            = Field(...,               example="1990-01-15")
    time: str            = Field(...,               example="10:30")
    place: str           = Field(default="Mumbai, Maharashtra, India",
                                 example="Mumbai, Maharashtra, India")
    latitude:            Optional[float] = Field(default=None, example=19.0760)
    longitude:           Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: Optional[int] = Field(default=None, example=330)
    ayanamsa: str        = Field(default="lahiri",  example="lahiri")


class TransitDataInput(BaseModel):
    """Base schema for transit-only endpoints (no birth name required)."""
    date: str  = Field(...,              example="2026-04-15")
    time: str  = Field(default="09:15",  example="09:15")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:   Optional[float] = Field(default=None)
    longitude:  Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")


# ─────────────────────────────────────────────────────────────
# Resolved chart data — returned by the helper below
# ─────────────────────────────────────────────────────────────

@dataclass
class ChartData:
    """Convenience container for the resolved output of a birth/transit input."""
    resolved: object        # ResolvedLocation from core
    local_dt: datetime
    jd_ut: float
    planets: list
    ascendant: dict | None = None
    houses: list | None = None


# ─────────────────────────────────────────────────────────────
# Helper — resolve payload → planets / ascendant / houses
# ─────────────────────────────────────────────────────────────

def resolve_chart(
    payload,
    *,
    need_ascendant: bool = True,
    need_houses: bool = False,
) -> ChartData:
    """
    Turn any payload that has date/time/place/ayanamsa into ready-to-use
    chart data.  Eliminates the 8-line boilerplate every endpoint repeats.

    Usage in a module:
        data = resolve_chart(payload, need_houses=True)
        # data.planets, data.ascendant, data.houses, data.jd_ut ...
    """
    from app.core import (
        resolve_location_and_time,
        to_julian_day_utc,
        calculate_planets,
        calculate_ascendant,
        build_house_cusps,
    )

    resolved, local_dt = resolve_location_and_time(
        place=payload.place,
        date_str=payload.date,
        time_str=payload.time,
        latitude=getattr(payload, "latitude", None),
        longitude=getattr(payload, "longitude", None),
        timezone_offset_minutes=getattr(payload, "timezone_offset_minutes", None),
    )
    jd_ut = to_julian_day_utc(local_dt, resolved.timezone_offset_minutes)
    planets = calculate_planets(jd_ut, payload.ayanamsa)

    ascendant = None
    houses = None
    if need_ascendant or need_houses:
        ascendant = calculate_ascendant(
            jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa
        )
    if need_houses:
        houses = build_house_cusps(
            jd_ut, resolved.latitude, resolved.longitude, payload.ayanamsa
        )

    return ChartData(
        resolved=resolved,
        local_dt=local_dt,
        jd_ut=jd_ut,
        planets=planets,
        ascendant=ascendant,
        houses=houses,
    )
