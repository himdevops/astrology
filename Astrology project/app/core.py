from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from typing import Dict, List, Tuple

import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
from zoneinfo import ZoneInfo
from datetime import timedelta


PLANETS = {
    "Sun": swe.SUN,
    "Moon": swe.MOON,
    "Mercury": swe.MERCURY,
    "Venus": swe.VENUS,
    "Mars": swe.MARS,
    "Jupiter": swe.JUPITER,
    "Saturn": swe.SATURN,
    "Rahu": swe.TRUE_NODE,
}

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

AYANAMSA_MAP = {
    "lahiri": swe.SIDM_LAHIRI,
    "raman": swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
}


@dataclass
class ResolvedLocation:
    place: str
    latitude: float
    longitude: float
    timezone_name: str
    timezone_offset_minutes: int


def parse_datetime(date_str: str, time_str: str) -> datetime:
    for fmt in ("%Y-%m-%d %H:%M", "%Y-%m-%d %H:%M:%S"):
        try:
            return datetime.strptime(f"{date_str} {time_str}", fmt)
        except ValueError:
            continue
    raise ValueError("Invalid date/time format. Use date=YYYY-MM-DD and time=HH:MM")


def geocode_place(place: str) -> Tuple[float, float, str]:
    geolocator = Nominatim(user_agent="financial_astrology_engine")
    location = geolocator.geocode(place)
    if not location:
        raise ValueError(f"Could not find coordinates for place: {place}")
    return float(location.latitude), float(location.longitude), location.address


def resolve_timezone_name(latitude: float, longitude: float) -> str:
    tf = TimezoneFinder()
    timezone_name = tf.timezone_at(lat=latitude, lng=longitude)
    if not timezone_name:
        raise ValueError("Could not determine timezone from coordinates")
    return timezone_name


def compute_timezone_offset_minutes(naive_local_dt: datetime, timezone_name: str) -> int:
    localized = naive_local_dt.replace(tzinfo=ZoneInfo(timezone_name))
    offset = localized.utcoffset()
    if offset is None:
        raise ValueError(f"Could not compute UTC offset for timezone: {timezone_name}")
    return int(offset.total_seconds() / 60)


def resolve_location_and_time(
    *,
    place: str,
    date_str: str,
    time_str: str,
    latitude: float | None,
    longitude: float | None,
    timezone_offset_minutes: int | None,
) -> Tuple[ResolvedLocation, datetime]:
    local_dt = parse_datetime(date_str, time_str)

    if latitude is None or longitude is None:
        latitude, longitude, display_place = geocode_place(place)
    else:
        display_place = place

    timezone_name = resolve_timezone_name(latitude, longitude)

    if timezone_offset_minutes is None:
        timezone_offset_minutes = compute_timezone_offset_minutes(local_dt, timezone_name)

    resolved = ResolvedLocation(
        place=display_place,
        latitude=latitude,
        longitude=longitude,
        timezone_name=timezone_name,
        timezone_offset_minutes=timezone_offset_minutes,
    )
    return resolved, local_dt




def to_julian_day_utc(local_dt: datetime, timezone_offset_minutes: int) -> float:
    utc_datetime = local_dt - timedelta(minutes=timezone_offset_minutes)

    return swe.julday(
        utc_datetime.year,
        utc_datetime.month,
        utc_datetime.day,
        utc_datetime.hour + utc_datetime.minute / 60.0 + utc_datetime.second / 3600.0,
    )


def normalize_degree(value: float) -> float:
    return value % 360.0


def degree_to_sign(degree: float) -> Tuple[str, float]:
    degree = normalize_degree(degree)
    sign_index = int(degree // 30)
    degree_in_sign = degree % 30
    return SIGNS[sign_index], round(degree_in_sign, 4)


def format_planet_position(name: str, degree: float, speed: float) -> Dict[str, object]:
    sign, degree_in_sign = degree_to_sign(degree)
    return {
        "planet": name,
        "longitude": round(normalize_degree(degree), 6),
        "sign": sign,
        "degree_in_sign": degree_in_sign,
        "retrograde": speed < 0,
    }


def calculate_ascendant(jd_ut: float, latitude: float, longitude: float, ayanamsa: str) -> Dict[str, object]:
    ayanamsa_key = ayanamsa.lower()
    if ayanamsa_key not in AYANAMSA_MAP:
        raise ValueError(f"Unsupported ayanamsa: {ayanamsa}. Supported: {', '.join(AYANAMSA_MAP)}")

    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    houses, ascmc = swe.houses_ex(jd_ut, latitude, longitude, b'P', swe.FLG_SIDEREAL)
    ascendant = ascmc[0]
    sign, degree_in_sign = degree_to_sign(ascendant)
    return {
        "longitude": round(normalize_degree(ascendant), 6),
        "sign": sign,
        "degree_in_sign": degree_in_sign,
    }


def build_house_cusps(jd_ut: float, latitude: float, longitude: float, ayanamsa: str) -> List[Dict[str, object]]:
    ayanamsa_key = ayanamsa.lower()
    if ayanamsa_key not in AYANAMSA_MAP:
        raise ValueError(f"Unsupported ayanamsa: {ayanamsa}. Supported: {', '.join(AYANAMSA_MAP)}")

    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    houses, _ = swe.houses_ex(jd_ut, latitude, longitude, b'P', swe.FLG_SIDEREAL)

    output = []
    for i in range(12):
        cusp = houses[i]
        sign, degree_in_sign = degree_to_sign(cusp)
        output.append({
            "house": i + 1,
            "longitude": round(normalize_degree(cusp), 6),
            "sign": sign,
            "degree_in_sign": degree_in_sign,
        })
    return output


def calculate_planets(jd_ut: float, ayanamsa: str) -> List[Dict[str, object]]:
    ayanamsa_key = ayanamsa.lower()
    if ayanamsa_key not in AYANAMSA_MAP:
        raise ValueError(f"Unsupported ayanamsa: {ayanamsa}. Supported: {', '.join(AYANAMSA_MAP)}")

    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    planets = []
    rahu_degree = None
    for name, planet_id in PLANETS.items():
        result = swe.calc_ut(jd_ut, planet_id, flags)
        xx = result[0]
        degree = xx[0]
        speed = xx[3]
        planets.append(format_planet_position(name, degree, speed))
        if name == "Rahu":
            rahu_degree = degree

    if rahu_degree is not None:
        ketu_degree = normalize_degree(rahu_degree + 180)
        planets.append(format_planet_position("Ketu", ketu_degree, -1.0))

    return planets
