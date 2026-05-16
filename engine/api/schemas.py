"""
schemas.py — Shared Pydantic request/response models for API.
==============================================================
All API endpoints use these schemas.
Modules never import from here — this is API-layer only.
"""
from __future__ import annotations

from typing import Optional
from pydantic import BaseModel, Field


class DateInput(BaseModel):
    """Single date query. Date accepts DD-MM-YYYY or YYYY-MM-DD."""
    date: str = Field(..., example="13-05-2026", description="DD-MM-YYYY or YYYY-MM-DD")
    city: Optional[str] = Field(default=None, description="City name — auto-resolves tz_offset")
    tz_offset: float = Field(default=5.5, description="Hours from UTC (auto-set if city given)")
    ayanamsa: str = Field(default="lahiri")


class DateRangeInput(BaseModel):
    """Date range query. Dates accept DD-MM-YYYY or YYYY-MM-DD."""
    start_date: str = Field(..., example="01-05-2026")
    end_date: str = Field(..., example="31-05-2026")
    city: Optional[str] = Field(default=None, description="City name — auto-resolves tz_offset")
    tz_offset: float = Field(default=5.5)
    ayanamsa: str = Field(default="lahiri")


class PlanetDateRangeInput(BaseModel):
    """Planet-specific date range query."""
    planet: str = Field(..., example="Mercury")
    start_date: str = Field(..., example="01-01-2026")
    end_date: str = Field(..., example="31-12-2026")
    city: Optional[str] = Field(default=None, description="City name — auto-resolves tz_offset")
    tz_offset: float = Field(default=5.5)
    ayanamsa: str = Field(default="lahiri")


class PanchangInput(BaseModel):
    """Panchang query with location. Supply city OR lat/lon."""
    date: str = Field(..., example="13-05-2026")
    time: str = Field(default="06:00", example="06:00")
    city: Optional[str] = Field(default=None, description="City name — auto-resolves lat/lon/tz")
    latitude: float = Field(default=23.1765, description="Latitude (Ujjain default)")
    longitude: float = Field(default=75.7885, description="Longitude (Ujjain default)")
    tz_offset: float = Field(default=5.5)
    ayanamsa: str = Field(default="lahiri")


class AllEventsInput(PanchangInput):
    """Combined query for all events."""
    pass


class KundaliInput(BaseModel):
    """Birth chart (Kundali) input — date, time, place of birth."""
    date: str = Field(..., example="15-08-1947", description="Date of birth DD-MM-YYYY or YYYY-MM-DD")
    time: str = Field(..., example="00:15", description="Time of birth HH:MM (24h)")
    city: Optional[str] = Field(default=None, description="Birth city — auto-resolves lat/lon/tz")
    latitude: float = Field(default=23.1765, description="Birth place latitude")
    longitude: float = Field(default=75.7885, description="Birth place longitude")
    tz_offset: float = Field(default=5.5, description="Timezone offset")
    ayanamsa: str = Field(default="lahiri")


class SpecialLagnasInput(KundaliInput):
    """Special Lagnas input — extends Kundali with karaka system choice."""
    karaka_system: int = Field(default=7, ge=7, le=8, description="Chara Karaka system: 7 (standard) or 8 (Jaimini with Rahu)")


class DashaInput(BaseModel):
    """Dasha calculation input — same birth data as Kundali."""
    date: str = Field(..., example="23-09-1992", description="Date of birth DD-MM-YYYY")
    time: str = Field(..., example="23:10", description="Time of birth HH:MM (24h)")
    city: Optional[str] = Field(default=None, description="Birth city")
    latitude: float = Field(default=23.1765, description="Birth place latitude")
    longitude: float = Field(default=75.7885, description="Birth place longitude")
    tz_offset: float = Field(default=5.5, description="Timezone offset")
    ayanamsa: str = Field(default="lahiri")
    max_level: int = Field(default=5, ge=1, le=5, description="Dasha depth (1=Mahadasha only, 5=full)")
    systems: Optional[list] = Field(
        default=None,
        description="List of systems: vimshottari, yogini, ashtottari, chara, narayana. Default: all",
    )


class TransitNavtaraInput(KundaliInput):
    """Transit Navtara input — birth data + transit date/time."""
    transit_date: str = Field(..., example="13-05-2026", description="Transit date DD-MM-YYYY")
    transit_time: str = Field(default="12:00", example="12:00", description="Transit time HH:MM (24h)")


class HoraInput(KundaliInput):
    """Hora & Auspicious Time input — birth data + target date."""
    target_date: str = Field(..., example="13-05-2026", description="Date to calculate horas DD-MM-YYYY")
    target_time: Optional[str] = Field(default="12:00", example="14:30", description="Transit time HH:MM (24h), defaults to noon")


class AshtakavargaInput(BaseModel):
    """Ashtakavarga calculation input with optional transit prediction range."""
    date: str = Field(..., example="23-09-1992", description="Date of birth DD-MM-YYYY")
    time: str = Field(..., example="23:10", description="Time of birth HH:MM (24h)")
    city: Optional[str] = Field(default=None, description="Birth city")
    latitude: float = Field(default=23.1765, description="Birth place latitude")
    longitude: float = Field(default=75.7885, description="Birth place longitude")
    tz_offset: float = Field(default=5.5, description="Timezone offset")
    ayanamsa: str = Field(default="lahiri")
    predict_start: Optional[str] = Field(
        default=None, description="Transit prediction start date DD-MM-YYYY (default: 1st of current month)",
    )
    predict_end: Optional[str] = Field(
        default=None, description="Transit prediction end date DD-MM-YYYY (default: end of current month)",
    )
