"""
core.py — Swiss Ephemeris wrapper for Vedic Astrology Engine
=============================================================
Fresh implementation. Provides:
  - Planet longitude, sign, nakshatra, pada, speed, retrograde
  - Panchang: Tithi, Nakshatra, Yoga, Karana, Vara
  - Sunrise / Sunset / Moonrise / Moonset
  - Ayanamsa support (Lahiri default)
  - Julian Day conversion
"""
from __future__ import annotations

import math
from datetime import datetime, date, timedelta
from dataclasses import dataclass, field
from typing import Any, Dict, List, Optional, Tuple

import swisseph as swe

# ─── Ayanamsa ────────────────────────────────────────────────
AYANAMSA_MAP = {
    "lahiri":      swe.SIDM_LAHIRI,
    "raman":       swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar":  swe.SIDM_YUKTESHWAR,
    "tropical":    -1,
}

# ─── Planet IDs ──────────────────────────────────────────────
PLANET_IDS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mars":    swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus":   swe.VENUS,
    "Saturn":  swe.SATURN,
    "Rahu":    swe.TRUE_NODE,     # True Node (matches Parashara Light)
    "Ketu":    -1,                # Computed as Rahu + 180
}

PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

# ─── Signs ───────────────────────────────────────────────────
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]

SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ─── Nakshatras (27) ─────────────────────────────────────────
NAKSHATRAS_27 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAKSHATRA_LORDS = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun", "Moon",
    "Mars", "Rahu", "Jupiter", "Saturn", "Mercury",
    "Ketu", "Venus", "Sun",
    "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury",
]

# ─── Tithi ───────────────────────────────────────────────────
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

TITHI_PAKSHA = ["Shukla"] * 15 + ["Krishna"] * 15

# ─── Yoga (27) ───────────────────────────────────────────────
YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

# ─── Karana (11 types, 60 per month) ─────────────────────────
KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Nagava", "Kimstughna",
]

# ─── Vara (weekday) ─────────────────────────────────────────
VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# ─── Data classes ────────────────────────────────────────────

@dataclass
class PlanetPosition:
    planet: str
    longitude: float
    latitude: float
    speed: float           # deg/day
    sign: str
    sign_lord: str
    degree_in_sign: float
    nakshatra: str
    nakshatra_lord: str
    nakshatra_pada: int
    retrograde: bool
    degree_display: str    # e.g. "15°23'04\" Aries"

    def to_dict(self) -> dict:
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
class PanchangData:
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

    def to_dict(self) -> dict:
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


# ─── Utility ────────────────────────────────────────────────

def normalize_degree(deg: float) -> float:
    """Normalize to 0-360."""
    return deg % 360


def deg_to_dms(deg: float) -> str:
    """Convert decimal degrees to D°M'S\" string."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime (assumed UTC) to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def local_to_utc(dt: datetime, tz_offset_hours: float) -> datetime:
    """Convert local datetime to UTC given timezone offset in hours."""
    return dt - timedelta(hours=tz_offset_hours)


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to datetime (UTC)."""
    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    return datetime(y, m, d, hour, minute, second)


# ─── Ayanamsa setup ─────────────────────────────────────────

def set_ayanamsa(ayanamsa: str = "lahiri"):
    """Set the sidereal ayanamsa for all subsequent calculations."""
    sid = AYANAMSA_MAP.get(ayanamsa.lower(), swe.SIDM_LAHIRI)
    if sid != -1:
        swe.set_sid_mode(sid)


def get_ayanamsa_value(jd: float, ayanamsa: str = "lahiri") -> float:
    """Get ayanamsa value in degrees for given Julian Day."""
    set_ayanamsa(ayanamsa)
    return swe.get_ayanamsa(jd)


# ─── Planet calculations ────────────────────────────────────

def calc_planet_longitude(jd: float, planet_id: int, sidereal: bool = True) -> Tuple[float, float, float]:
    """
    Calculate planet longitude, latitude, speed.
    Returns (longitude, latitude, speed_deg_per_day).
    """
    flags = swe.FLG_SWIEPH | swe.FLG_SPEED
    if sidereal:
        flags |= swe.FLG_SIDEREAL

    result, _ = swe.calc_ut(jd, planet_id, flags)
    return result[0], result[1], result[3]  # lon, lat, speed


def get_planet_position(jd: float, planet: str, ayanamsa: str = "lahiri") -> PlanetPosition:
    """Get full position data for a single planet."""
    set_ayanamsa(ayanamsa)
    sidereal = ayanamsa.lower() != "tropical"

    if planet == "Ketu":
        # Ketu = Rahu + 180
        lon, lat, speed = calc_planet_longitude(jd, PLANET_IDS["Rahu"], sidereal)
        lon = normalize_degree(lon + 180)
        speed = -speed  # Ketu moves opposite
    else:
        planet_id = PLANET_IDS[planet]
        lon, lat, speed = calc_planet_longitude(jd, planet_id, sidereal)

    lon = normalize_degree(lon)

    # Sign
    sign_index = int(lon / 30)
    sign = SIGNS[sign_index]
    sign_lord = SIGN_LORDS[sign]
    degree_in_sign = lon - (sign_index * 30)

    # Nakshatra
    nak_index = int(lon / (360 / 27))
    nak_name = NAKSHATRAS_27[nak_index]
    nak_lord = NAKSHATRA_LORDS[nak_index]
    nak_start = nak_index * (360 / 27)
    pada = int((lon - nak_start) / (360 / 108)) + 1
    pada = min(pada, 4)

    # Retrograde
    retrograde = speed < 0

    # Display
    degree_display = f"{deg_to_dms(degree_in_sign)} {sign}"

    return PlanetPosition(
        planet=planet,
        longitude=lon,
        latitude=lat,
        speed=speed,
        sign=sign,
        sign_lord=sign_lord,
        degree_in_sign=degree_in_sign,
        nakshatra=nak_name,
        nakshatra_lord=nak_lord,
        nakshatra_pada=pada,
        retrograde=retrograde,
        degree_display=degree_display,
    )


def get_all_planets(jd: float, ayanamsa: str = "lahiri") -> List[PlanetPosition]:
    """Get positions for all 9 planets."""
    return [get_planet_position(jd, p, ayanamsa) for p in PLANETS_9]


# ─── Panchang calculations ──────────────────────────────────

def calc_tithi(sun_lon: float, moon_lon: float) -> Tuple[int, str, str]:
    """Calculate tithi from Sun and Moon longitudes."""
    diff = normalize_degree(moon_lon - sun_lon)
    index = int(diff / 12) % 30
    return index, TITHIS[index], TITHI_PAKSHA[index]


def calc_yoga(sun_lon: float, moon_lon: float) -> str:
    """Calculate Yoga from Sun + Moon longitudes."""
    total = normalize_degree(sun_lon + moon_lon)
    index = int(total / (360 / 27)) % 27
    return YOGAS[index]


def calc_karana(sun_lon: float, moon_lon: float) -> str:
    """Calculate Karana from Sun-Moon difference."""
    diff = normalize_degree(moon_lon - sun_lon)
    karana_index = int(diff / 6) % 60

    # Fixed karanas: Kimstughna(0), Shakuni(57), Chatushpada(58), Nagava(59)
    if karana_index == 0:
        return "Kimstughna"
    elif karana_index == 57:
        return "Shakuni"
    elif karana_index == 58:
        return "Chatushpada"
    elif karana_index == 59:
        return "Nagava"
    else:
        # Repeating cycle of 7: Bava, Balava, Kaulava, Taitila, Garaja, Vanija, Vishti
        return KARANAS[(karana_index - 1) % 7]


def calc_sunrise_sunset(
    jd: float, lat: float, lon: float
) -> Tuple[Optional[str], Optional[str], Optional[str], Optional[str]]:
    """
    Calculate sunrise, sunset, moonrise, moonset for given JD and location.
    Returns time strings in HH:MM format (local apparent time).
    """
    results = {}

    for label, body, event_type in [
        ("sunrise",  swe.SUN,  1),   # rise
        ("sunset",   swe.SUN,  2),   # set
        ("moonrise", swe.MOON, 1),
        ("moonset",  swe.MOON, 2),
    ]:
        try:
            # Use swe.rise_trans for rise/set calculations
            # flags: BIT_DISC_CENTER for center of disc
            res = swe.rise_trans(
                jd, body, lon, lat, 0.0, 0.0,  # geoalt, atpress
                event_type,
            )
            if res and len(res) >= 2:
                rise_jd = res[1][0] if isinstance(res[1], (list, tuple)) else res[1]
                dt_utc = jd_to_datetime(rise_jd)
                results[label] = dt_utc.strftime("%H:%M")
            else:
                results[label] = None
        except Exception:
            results[label] = None

    return results.get("sunrise"), results.get("sunset"), results.get("moonrise"), results.get("moonset")


def get_panchang(
    dt: datetime,
    lat: float = 23.1765,   # Ujjain default
    lon: float = 75.7885,
    tz_offset: float = 5.5,  # IST
    ayanamsa: str = "lahiri",
) -> PanchangData:
    """
    Compute full Panchang for a given date/time/location.
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    sun = get_planet_position(jd, "Sun", ayanamsa)
    moon = get_planet_position(jd, "Moon", ayanamsa)

    tithi_idx, tithi, paksha = calc_tithi(sun.longitude, moon.longitude)
    yoga = calc_yoga(sun.longitude, moon.longitude)
    karana = calc_karana(sun.longitude, moon.longitude)

    # Weekday
    weekday_idx = dt.weekday()  # Monday=0 in Python
    # Convert to Sunday=0 system
    vara_idx = (weekday_idx + 1) % 7
    weekday = VARAS[vara_idx]
    weekday_lord = VARA_LORDS[vara_idx]

    # Sunrise/sunset — use start-of-day JD
    sunrise_dt = dt.replace(hour=0, minute=0, second=0)
    sunrise_utc = local_to_utc(sunrise_dt, tz_offset)
    sunrise_jd = datetime_to_jd(sunrise_utc)

    sunrise, sunset, moonrise, moonset = calc_sunrise_sunset(sunrise_jd, lat, lon)

    return PanchangData(
        date=dt.strftime("%Y-%m-%d"),
        weekday=weekday,
        weekday_lord=weekday_lord,
        tithi_index=tithi_idx,
        tithi=tithi,
        paksha=paksha,
        nakshatra=moon.nakshatra,
        nakshatra_lord=moon.nakshatra_lord,
        yoga=yoga,
        karana=karana,
        sunrise=sunrise or "N/A",
        sunset=sunset or "N/A",
        moonrise=moonrise or "N/A",
        moonset=moonset or "N/A",
        sun_longitude=sun.longitude,
        moon_longitude=moon.longitude,
    )


# ─── Date range helper ──────────────────────────────────────

def date_range(start: date, end: date) -> List[date]:
    """Generate list of dates from start to end (inclusive)."""
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]
