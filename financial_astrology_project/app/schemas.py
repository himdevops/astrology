from typing import Optional
from pydantic import BaseModel, Field


class BirthInput(BaseModel):
    name: str = Field(..., example="Test User")
    date: str = Field(..., example="1990-01-01")
    time: str = Field(..., example="12:00")
    place: str = Field(..., example="Ujjain, Madhya Pradesh, India")
    latitude: Optional[float] = Field(default=None, example=23.1765)
    longitude: Optional[float] = Field(default=None, example=75.7885)
    timezone_offset_minutes: Optional[int] = Field(default=None, example=330)
    ayanamsa: str = Field(default="lahiri", example="lahiri")


class TransitInput(BaseModel):
    date: str = Field(..., example="2026-04-15")
    time: str = Field(..., example="09:30")
    place: str = Field(default="Greenwich")
    latitude: Optional[float] = Field(default=None, example=51.4769)
    longitude: Optional[float] = Field(default=None, example=0.0)
    timezone_offset_minutes: Optional[int] = Field(default=None, example=0)
    ayanamsa: str = Field(default="lahiri", example="lahiri")
