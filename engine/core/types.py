"""
types.py — Typed dataclasses used across the entire engine.
============================================================
All modules return these types — ensures consistency everywhere.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional


@dataclass
class PlanetPosition:
    """Complete position data for a single planet."""
    planet: str
    longitude: float
    latitude: float
    speed: float              # deg/day
    sign: str
    sign_lord: str
    degree_in_sign: float
    nakshatra: str
    nakshatra_lord: str
    nakshatra_pada: int
    retrograde: bool
    degree_display: str       # e.g. "15°23'04\" Aries"

    def to_dict(self) -> Dict[str, Any]:
        return {
            "planet": self.planet,
            "longitude": round(self.longitude, 6),
            "latitude": round(self.latitude, 4),
            "speed": round(self.speed, 6),
            "sign": self.sign,
            "sign_lord": self.sign_lord,
            "degree_in_sign": round(self.degree_in_sign, 4),
            "nakshatra": self.nakshatra,
            "nakshatra_lord": self.nakshatra_lord,
            "nakshatra_pada": self.nakshatra_pada,
            "retrograde": self.retrograde,
            "degree_display": self.degree_display,
        }


@dataclass
class NakshatraInfo:
    """Nakshatra calculation result."""
    index: int
    name: str
    lord: str
    pada: int
    degree_in_nakshatra: float
    start_degree: float
    end_degree: float
    deity: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "nakshatra": self.name,
            "lord": self.lord,
            "pada": self.pada,
            "degree_in_nakshatra": round(self.degree_in_nakshatra, 4),
            "deity": self.deity,
        }


@dataclass
class SignInfo:
    """Rashi (sign) calculation result."""
    index: int
    name: str
    lord: str
    degree_in_sign: float
    element: str = ""
    modality: str = ""

    def to_dict(self) -> Dict[str, Any]:
        return {
            "index": self.index,
            "sign": self.name,
            "lord": self.lord,
            "degree_in_sign": round(self.degree_in_sign, 4),
            "element": self.element,
            "modality": self.modality,
        }


@dataclass
class LocationInfo:
    """Resolved geographic location."""
    name: str
    latitude: float
    longitude: float
    tz_offset: float         # hours from UTC

    def to_dict(self) -> Dict[str, Any]:
        return {
            "name": self.name,
            "latitude": self.latitude,
            "longitude": self.longitude,
            "tz_offset": self.tz_offset,
        }


@dataclass
class PanchangData:
    """Complete Panchang for a date/time/location."""
    date: str
    weekday: str
    weekday_lord: str
    tithi_index: int
    tithi: str
    paksha: str
    nakshatra: str
    nakshatra_lord: str
    yoga: str
    karana: str
    sunrise: str
    sunset: str
    moonrise: str
    moonset: str
    sun_longitude: float
    moon_longitude: float

    def to_dict(self) -> Dict[str, Any]:
        return {
            "date": self.date,
            "weekday": self.weekday,
            "weekday_lord": self.weekday_lord,
            "tithi": self.tithi,
            "paksha": self.paksha,
            "tithi_full": f"{self.paksha} {self.tithi}",
            "nakshatra": self.nakshatra,
            "nakshatra_lord": self.nakshatra_lord,
            "yoga": self.yoga,
            "karana": self.karana,
            "sunrise": self.sunrise,
            "sunset": self.sunset,
            "moonrise": self.moonrise,
            "moonset": self.moonset,
        }


@dataclass
class AspectInfo:
    """A single aspect between two planets."""
    aspecting_planet: str
    aspected_planet: str
    aspect_angle: int
    aspect_name: str
    actual_distance: float
    aspecting_sign: str
    aspected_sign: str

    def to_dict(self) -> Dict[str, Any]:
        return {
            "aspecting_planet": self.aspecting_planet,
            "aspected_planet": self.aspected_planet,
            "aspect_angle": self.aspect_angle,
            "aspect_name": self.aspect_name,
            "actual_distance": round(self.actual_distance, 2),
            "aspecting_sign": self.aspecting_sign,
            "aspected_sign": self.aspected_sign,
        }
