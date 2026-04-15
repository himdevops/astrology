from __future__ import annotations

from app.core import (
    build_house_cusps,
    calculate_ascendant,
    calculate_planets,
    resolve_location_and_time,
    to_julian_day_utc,
)
from app.schemas import BirthInput, TransitInput


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
    ascendant = calculate_ascendant(jd_ut, resolved.latitude, resolved.longitude)
    houses = build_house_cusps(jd_ut, resolved.latitude, resolved.longitude)

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
        "houses": houses,
    }


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
    }
