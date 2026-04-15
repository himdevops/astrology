"""
schemas.py — Pydantic Schemas for Financial Astrology Engine
"""
from typing import List, Optional
from pydantic import BaseModel, Field


# ─────────────────────────────────────────────────────────────
# Input Schemas
# ─────────────────────────────────────────────────────────────

class BirthInput(BaseModel):
    name: str            = Field(...,              example="Himanshu")
    date: str            = Field(...,              example="1990-01-15")
    time: str            = Field(...,              example="10:30")
    place: str           = Field(...,              example="Mumbai, Maharashtra, India")
    latitude:            Optional[float] = Field(default=None, example=19.0760)
    longitude:           Optional[float] = Field(default=None, example=72.8777)
    timezone_offset_minutes: Optional[int] = Field(default=None, example=330)
    ayanamsa: str        = Field(default="lahiri", example="lahiri")


class TransitInput(BaseModel):
    date: str  = Field(...,              example="2026-04-15")
    time: str  = Field(default="09:15",  example="09:15")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:   Optional[float] = Field(default=None)
    longitude:  Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")


class DashaInput(BaseModel):
    """Input for Vimshottari Dasha calculation (requires birth chart)."""
    name: str  = Field(...,  example="Himanshu")
    date: str  = Field(...,  example="1990-01-15")
    time: str  = Field(...,  example="10:30")
    place: str = Field(...,  example="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    as_of_date: Optional[str] = Field(
        default=None,
        example="2026-04-15",
        description="Date to find current dasha (defaults to today)"
    )
    years_to_show: int = Field(default=120, ge=10, le=120)


class DivisionalInput(BaseModel):
    """Input for divisional chart calculation."""
    name: str  = Field(...,  example="Himanshu")
    date: str  = Field(...,  example="1990-01-15")
    time: str  = Field(...,  example="10:30")
    place: str = Field(...,  example="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    charts: List[str] = Field(
        default=["D2", "D9", "D10"],
        example=["D2", "D9", "D10"],
        description="Which divisional charts to compute: D2, D3, D9, D10"
    )


class AshtakavargaInput(BaseModel):
    """Input for Ashtakavarga + transit date prediction."""
    name: str  = Field(...,  example="Himanshu")
    date: str  = Field(...,  example="1990-01-15")
    time: str  = Field(...,  example="10:30")
    place: str = Field(...,  example="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    # Transit prediction settings
    transit_from_date: Optional[str] = Field(
        default=None,
        example="2026-04-15",
        description="Start date for transit predictions (default: today)"
    )
    days_ahead: int = Field(default=180, ge=30, le=365)


class YogaInput(BaseModel):
    """Input for yoga detection."""
    name: str  = Field(...,  example="Himanshu")
    date: str  = Field(...,  example="1990-01-15")
    time: str  = Field(...,  example="10:30")
    place: str = Field(...,  example="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")


class TransitAlertInput(BaseModel):
    """Input for transit alert generation."""
    date: str  = Field(...,  example="2026-04-15")
    time: str  = Field(default="09:15", example="09:15")
    place: str = Field(default="Mumbai, Maharashtra, India")
    latitude:  Optional[float] = Field(default=None)
    longitude: Optional[float] = Field(default=None)
    timezone_offset_minutes: Optional[int] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    days_ahead: int = Field(default=90, ge=7, le=365)
    # Optional natal chart for personal transit analysis
    natal_date:  Optional[str] = Field(default=None, example="1990-01-15")
    natal_time:  Optional[str] = Field(default=None, example="10:30")
    natal_place: Optional[str] = Field(default=None, example="Mumbai, Maharashtra, India")


class FullPredictionInput(BaseModel):
    """
    Full autonomous prediction — combines natal chart + current transits.
    If no natal chart provided, uses transits only.
    """
    # Current date/transit
    transit_date: str  = Field(...,  example="2026-04-15")
    transit_time: str  = Field(default="09:15")
    transit_place: str = Field(default="Mumbai, Maharashtra, India")
    transit_latitude:  Optional[float] = Field(default=None)
    transit_longitude: Optional[float] = Field(default=None)
    ayanamsa: str = Field(default="lahiri")
    days_ahead: int = Field(default=90, ge=7, le=365)

    # Optional: natal chart for personalized prediction
    natal_name:  Optional[str]  = Field(default=None)
    natal_date:  Optional[str]  = Field(default=None)
    natal_time:  Optional[str]  = Field(default=None)
    natal_place: Optional[str]  = Field(default=None)
    natal_latitude:  Optional[float] = Field(default=None)
    natal_longitude: Optional[float] = Field(default=None)
