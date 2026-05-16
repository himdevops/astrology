"""
hora.py — Hora (Planetary Hour) & Chaughadiya Calculations.
=============================================================
Traditional Vedic hora system:
  - Day divided into 12 unequal horas (sunrise to sunset)
  - Night divided into 12 unequal horas (sunset to next sunrise)
  - Each hora ruled by a planet in Chaldean order

Chaughadiya (चौघड़िया):
  - Day divided into 8 parts (sunrise to sunset)
  - Night divided into 8 parts (sunset to next sunrise)
  - Each period has a muhurta name with auspicious/inauspicious quality
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, Any, List, Optional, Tuple

import swisseph as swe

from core.geo import _try_rise_trans, _math_sunrise_sunset
from core.utils import datetime_to_jd, jd_to_datetime, local_to_utc, utc_to_local


# ═══════════════════════════════════════════════════════════════
# 1. HORA CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Chaldean order (hora sequence): Sun → Venus → Mercury → Moon → Saturn → Jupiter → Mars
HORA_SEQUENCE = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

# Day lord → weekday index (Python: Monday=0)
# Sunday=6, Monday=0, Tuesday=1, Wednesday=2, Thursday=3, Friday=4, Saturday=5
WEEKDAY_LORDS = {
    6: "Sun",       # Sunday
    0: "Moon",      # Monday
    1: "Mars",      # Tuesday
    2: "Mercury",   # Wednesday
    3: "Jupiter",   # Thursday
    4: "Venus",     # Friday
    5: "Saturn",    # Saturday
}

WEEKDAY_NAMES = {
    6: "Sunday", 0: "Monday", 1: "Tuesday", 2: "Wednesday",
    3: "Thursday", 4: "Friday", 5: "Saturday",
}
WEEKDAY_NAMES_HI = {
    6: "रविवार", 0: "सोमवार", 1: "मंगलवार", 2: "बुधवार",
    3: "गुरुवार", 4: "शुक्रवार", 5: "शनिवार",
}

HORA_PLANET_HI = {
    "Sun": "सूर्य", "Moon": "चंद्र", "Mars": "मंगल",
    "Mercury": "बुध", "Jupiter": "गुरु", "Venus": "शुक्र", "Saturn": "शनि",
}

# ═══════════════════════════════════════════════════════════════
# 2. CHAUGHADIYA CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Chaughadiya names and qualities
CHAUGHADIYA_NAMES = [
    "Udveg",    # Ruled by Sun — Inauspicious
    "Char",     # Ruled by Venus — Good (for travel)
    "Labh",     # Ruled by Mercury — Very Good (gain)
    "Amrit",    # Ruled by Moon — Excellent
    "Kaal",     # Ruled by Saturn — Very Bad
    "Shubh",    # Ruled by Jupiter — Very Good
    "Rog",      # Ruled by Mars — Bad (disease)
]

CHAUGHADIYA_NAMES_HI = [
    "उद्वेग", "चर", "लाभ", "अमृत", "काल", "शुभ", "रोग",
]

CHAUGHADIYA_LORDS = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]

CHAUGHADIYA_QUALITY = {
    "Udveg": "bad",
    "Char": "good",
    "Labh": "very_good",
    "Amrit": "excellent",
    "Kaal": "very_bad",
    "Shubh": "very_good",
    "Rog": "bad",
}

# Day Chaughadiya sequence by weekday (0=Monday ... 6=Sunday)
# Starting Chaughadiya for day: Sunday=Udveg(0), Mon=Amrit(3), Tue=Rog(6), Wed=Labh(2),
# Thu=Shubh(5), Fri=Char(1), Sat=Kaal(4)
DAY_CHAUGH_START = {
    6: 0,  # Sunday → Udveg
    0: 3,  # Monday → Amrit
    1: 6,  # Tuesday → Rog
    2: 2,  # Wednesday → Labh
    3: 5,  # Thursday → Shubh
    4: 1,  # Friday → Char
    5: 4,  # Saturday → Kaal
}

# Night Chaughadiya starting index
NIGHT_CHAUGH_START = {
    6: 6,  # Sunday night → Rog
    0: 2,  # Monday night → Labh
    1: 5,  # Tuesday night → Shubh
    2: 1,  # Wednesday night → Char
    3: 4,  # Thursday night → Kaal
    4: 0,  # Friday night → Udveg
    5: 3,  # Saturday night → Amrit
}


# ═══════════════════════════════════════════════════════════════
# 3. SUNRISE / SUNSET AS JD VALUES
# ═══════════════════════════════════════════════════════════════

def get_sunrise_sunset_jd(
    jd: float, lat: float, lon: float
) -> Tuple[Optional[float], Optional[float]]:
    """
    Get sunrise and sunset as Julian Day values (UTC).
    Tries Swiss Ephemeris first, falls back to math.
    """
    geopos = (lon, lat, 0.0)

    sunrise_jd = _try_rise_trans(jd, swe.SUN, 1, geopos)
    sunset_jd = _try_rise_trans(jd, swe.SUN, 2, geopos)

    # Fallback
    if not sunrise_jd or not sunset_jd:
        sr, ss = _math_sunrise_sunset(jd, lat, lon)
        if not sunrise_jd:
            sunrise_jd = sr
        if not sunset_jd:
            sunset_jd = ss

    return sunrise_jd, sunset_jd


# ═══════════════════════════════════════════════════════════════
# 4. HORA CALCULATIONS
# ═══════════════════════════════════════════════════════════════

def calc_hora_table(
    dt: datetime,
    lat: float,
    lon: float,
    tz: float,
) -> Dict[str, Any]:
    """
    Calculate 24 hora slots for a given date and location.

    Uses sunrise-based unequal hours:
      - Day hora duration = (sunset - sunrise) / 12
      - Night hora duration = (next_sunrise - sunset) / 12

    Returns:
        - horas: list of 24 hora dicts with start/end times, lord, is_day
        - sunrise/sunset times
        - day_lord (weekday lord)
    """
    # Use midnight local time so swe.rise_trans finds TODAY's sunrise
    # (If JD is after sunrise, rise_trans returns next day's sunrise → negative duration)
    midnight_local = datetime(dt.year, dt.month, dt.day, 0, 0)
    utc_midnight = local_to_utc(midnight_local, tz)
    jd = datetime_to_jd(utc_midnight)

    # Get sunrise/sunset for the given date
    sunrise_jd, sunset_jd = get_sunrise_sunset_jd(jd, lat, lon)
    if not sunrise_jd or not sunset_jd:
        return {"error": "Could not compute sunrise/sunset for this location"}

    # Safety: ensure sunset is after sunrise (same day)
    if sunset_jd <= sunrise_jd:
        # sunrise is for next day — go back further
        jd_earlier = jd - 0.5  # go back 12 hours
        sunrise_jd, sunset_jd = get_sunrise_sunset_jd(jd_earlier, lat, lon)
        if not sunrise_jd or not sunset_jd or sunset_jd <= sunrise_jd:
            return {"error": "Could not compute valid sunrise/sunset for this location"}

    # Get next day's sunrise for night hora calculation
    next_sunrise_jd, _ = get_sunrise_sunset_jd(sunset_jd + 0.01, lat, lon)
    if not next_sunrise_jd or next_sunrise_jd <= sunset_jd:
        # Estimate: ~24h after sunrise
        next_sunrise_jd = sunrise_jd + 1.0

    # Hora durations
    day_duration = sunset_jd - sunrise_jd         # in JD (fraction of day)
    night_duration = next_sunrise_jd - sunset_jd
    day_hora_dur = day_duration / 12.0
    night_hora_dur = night_duration / 12.0

    # Determine weekday from local date
    local_sunrise = utc_to_local(jd_to_datetime(sunrise_jd), tz)
    weekday = local_sunrise.weekday()  # Python: 0=Mon
    day_lord = WEEKDAY_LORDS[weekday]

    # Starting hora lord = day lord
    # Find index in HORA_SEQUENCE
    start_idx = HORA_SEQUENCE.index(day_lord)

    horas = []
    for i in range(24):
        if i < 12:
            # Day hora
            start_jd = sunrise_jd + i * day_hora_dur
            end_jd = sunrise_jd + (i + 1) * day_hora_dur
            is_day = True
        else:
            # Night hora
            ni = i - 12
            start_jd = sunset_jd + ni * night_hora_dur
            end_jd = sunset_jd + (ni + 1) * night_hora_dur
            is_day = False

        lord_idx = (start_idx + i) % 7
        lord = HORA_SEQUENCE[lord_idx]

        start_local = utc_to_local(jd_to_datetime(start_jd), tz)
        end_local = utc_to_local(jd_to_datetime(end_jd), tz)

        horas.append({
            "hora_num": i + 1,
            "is_day": is_day,
            "lord": lord,
            "lord_hi": HORA_PLANET_HI.get(lord, lord),
            "start": start_local.strftime("%H:%M"),
            "end": end_local.strftime("%H:%M"),
            "start_jd": start_jd,
            "end_jd": end_jd,
            "duration_min": round((end_jd - start_jd) * 24 * 60, 1),
        })

    sunrise_local = utc_to_local(jd_to_datetime(sunrise_jd), tz)
    sunset_local = utc_to_local(jd_to_datetime(sunset_jd), tz)

    return {
        "date": local_sunrise.strftime("%d-%m-%Y"),
        "weekday": WEEKDAY_NAMES[weekday],
        "weekday_hi": WEEKDAY_NAMES_HI[weekday],
        "day_lord": day_lord,
        "day_lord_hi": HORA_PLANET_HI.get(day_lord, day_lord),
        "sunrise": sunrise_local.strftime("%H:%M"),
        "sunset": sunset_local.strftime("%H:%M"),
        "day_hora_min": round(day_hora_dur * 24 * 60, 1),
        "night_hora_min": round(night_hora_dur * 24 * 60, 1),
        "horas": horas,
    }


# ═══════════════════════════════════════════════════════════════
# 5. CHAUGHADIYA CALCULATIONS
# ═══════════════════════════════════════════════════════════════

def calc_chaughadiya(
    dt: datetime,
    lat: float,
    lon: float,
    tz: float,
) -> Dict[str, Any]:
    """
    Calculate Chaughadiya (8 day + 8 night periods) for a given date.

    Returns:
        - day_periods: 8 periods from sunrise to sunset
        - night_periods: 8 periods from sunset to next sunrise
        - each with name, quality, lord, start/end times
    """
    # Use midnight local time so swe.rise_trans finds TODAY's sunrise
    midnight_local = datetime(dt.year, dt.month, dt.day, 0, 0)
    utc_midnight = local_to_utc(midnight_local, tz)
    jd = datetime_to_jd(utc_midnight)

    sunrise_jd, sunset_jd = get_sunrise_sunset_jd(jd, lat, lon)
    if not sunrise_jd or not sunset_jd:
        return {"error": "Could not compute sunrise/sunset"}

    # Safety: ensure sunset is after sunrise
    if sunset_jd <= sunrise_jd:
        jd_earlier = jd - 0.5
        sunrise_jd, sunset_jd = get_sunrise_sunset_jd(jd_earlier, lat, lon)
        if not sunrise_jd or not sunset_jd or sunset_jd <= sunrise_jd:
            return {"error": "Could not compute valid sunrise/sunset"}

    next_sunrise_jd, _ = get_sunrise_sunset_jd(sunset_jd + 0.01, lat, lon)
    if not next_sunrise_jd or next_sunrise_jd <= sunset_jd:
        next_sunrise_jd = sunrise_jd + 1.0

    day_duration = sunset_jd - sunrise_jd
    night_duration = next_sunrise_jd - sunset_jd
    day_period = day_duration / 8.0
    night_period = night_duration / 8.0

    local_sunrise = utc_to_local(jd_to_datetime(sunrise_jd), tz)
    weekday = local_sunrise.weekday()

    day_start_idx = DAY_CHAUGH_START[weekday]
    night_start_idx = NIGHT_CHAUGH_START[weekday]

    day_periods = []
    for i in range(8):
        idx = (day_start_idx + i) % 7
        name = CHAUGHADIYA_NAMES[idx]
        start_jd = sunrise_jd + i * day_period
        end_jd = sunrise_jd + (i + 1) * day_period
        start_local = utc_to_local(jd_to_datetime(start_jd), tz)
        end_local = utc_to_local(jd_to_datetime(end_jd), tz)

        day_periods.append({
            "index": i + 1,
            "name": name,
            "name_hi": CHAUGHADIYA_NAMES_HI[idx],
            "lord": CHAUGHADIYA_LORDS[idx],
            "lord_hi": HORA_PLANET_HI.get(CHAUGHADIYA_LORDS[idx], ""),
            "quality": CHAUGHADIYA_QUALITY[name],
            "start": start_local.strftime("%H:%M"),
            "end": end_local.strftime("%H:%M"),
            "duration_min": round((end_jd - start_jd) * 24 * 60, 1),
        })

    night_periods = []
    for i in range(8):
        idx = (night_start_idx + i) % 7
        name = CHAUGHADIYA_NAMES[idx]
        start_jd = sunset_jd + i * night_period
        end_jd = sunset_jd + (i + 1) * night_period
        start_local = utc_to_local(jd_to_datetime(start_jd), tz)
        end_local = utc_to_local(jd_to_datetime(end_jd), tz)

        night_periods.append({
            "index": i + 1,
            "name": name,
            "name_hi": CHAUGHADIYA_NAMES_HI[idx],
            "lord": CHAUGHADIYA_LORDS[idx],
            "lord_hi": HORA_PLANET_HI.get(CHAUGHADIYA_LORDS[idx], ""),
            "quality": CHAUGHADIYA_QUALITY[name],
            "start": start_local.strftime("%H:%M"),
            "end": end_local.strftime("%H:%M"),
            "duration_min": round((end_jd - start_jd) * 24 * 60, 1),
        })

    return {
        "day_periods": day_periods,
        "night_periods": night_periods,
    }
