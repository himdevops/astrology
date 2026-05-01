"""
panchang.py — Panchang (Five Limbs) & Muhurta Module for Financial Astrology
Implements:
1. Tithi (Lunar Day) — Moon-Sun angular distance
2. Nakshatra (Lunar Mansion) — Moon's position
3. Yoga (Sun-Moon combination) — Sum of longitudes / 13.333°
4. Karana (Half-Tithi) — Half lunar day
5. Vara (Weekday) — Day lord

Plus Muhurta (Electional Astrology):
- Rahu Kalam, Gulika Kalam, Yamaganda
- Abhijit Muhurta (best time of day)
- Choghadiya (Gujarati trading community system)
- Best trading windows based on Panchang

All calculations use sidereal (Lahiri) positions from Swiss Ephemeris.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from app.constants import (
    SIGNS, SIGN_IDX, TITHIS, YOGA_NAMES, KARANA_NAMES,
    VARA_NAMES, VARA_LORDS, NAKSHATRA_SPAN_DEG,
)

# ─────────────────────────────────────────────────────────────
# Tithi Financial Mapping
# ─────────────────────────────────────────────────────────────
TITHI_FINANCIAL = {
    "Pratipada":  {"nature": "Nanda",  "score": 0.40, "signal": "New beginnings — cautious BUY"},
    "Dwitiya":    {"nature": "Bhadra", "score": 0.60, "signal": "Auspicious — BUY"},
    "Tritiya":    {"nature": "Jaya",   "score": 0.70, "signal": "Victory energy — STRONG BUY"},
    "Chaturthi":  {"nature": "Rikta",  "score": -0.30, "signal": "Empty/loss — AVOID trading"},
    "Panchami":   {"nature": "Purna",  "score": 0.80, "signal": "Full/complete — STRONG BUY"},
    "Shashthi":   {"nature": "Nanda",  "score": 0.40, "signal": "Moderate — HOLD"},
    "Saptami":    {"nature": "Bhadra", "score": 0.60, "signal": "Auspicious — BUY"},
    "Ashtami":    {"nature": "Jaya",   "score": -0.40, "signal": "Volatile — CAUTION (Ashtami effect)"},
    "Navami":     {"nature": "Rikta",  "score": -0.50, "signal": "Rikta tithi — AVOID"},
    "Dashami":    {"nature": "Purna",  "score": 0.70, "signal": "Completion — BUY"},
    "Ekadashi":   {"nature": "Nanda",  "score": 0.50, "signal": "Spiritual/moderate — HOLD/BUY"},
    "Dwadashi":   {"nature": "Bhadra", "score": 0.55, "signal": "Auspicious — BUY"},
    "Trayodashi":  {"nature": "Jaya",  "score": 0.65, "signal": "Victory — BUY"},
    "Chaturdashi": {"nature": "Rikta", "score": -0.60, "signal": "Pre-Purnima/Amavasya — HIGH CAUTION"},
    "Purnima/Amavasya": {"nature": "Purna", "score": -0.20, "signal": "Full/New Moon — VOLATILE, avoid large positions"},
}

# ─────────────────────────────────────────────────────────────
# Yoga Financial Mapping (selected important ones)
# ─────────────────────────────────────────────────────────────
YOGA_FINANCIAL = {
    "Vishkumbha": -0.50, "Priti": 0.70, "Ayushman": 0.60, "Saubhagya": 0.80,
    "Shobhana": 0.75, "Atiganda": -0.60, "Sukarma": 0.70, "Dhriti": 0.65,
    "Shula": -0.70, "Ganda": -0.80, "Vriddhi": 0.85, "Dhruva": 0.50,
    "Vyaghata": -0.55, "Harshana": 0.70, "Vajra": -0.40, "Siddhi": 0.90,
    "Vyatipata": -0.75, "Variyan": 0.40, "Parigha": -0.50, "Shiva": 0.60,
    "Siddha": 0.85, "Sadhya": 0.70, "Shubha": 0.80, "Shukla": 0.75,
    "Brahma": 0.60, "Indra": 0.65, "Vaidhriti": -0.70,
}

# ─────────────────────────────────────────────────────────────
# Nakshatra names for Panchang (Moon's nakshatra)
# ─────────────────────────────────────────────────────────────
NAKSHATRA_NAMES = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]


# ─────────────────────────────────────────────────────────────
# Core Panchang Calculation
# ─────────────────────────────────────────────────────────────

def calculate_panchang(
    date_str: str,
    time_str: str = "09:15",
    latitude: float = 19.076,
    longitude: float = 72.8777,
    timezone_offset_minutes: int = 330,
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Calculate complete Panchang for a given date/time/location.
    Default: Mumbai at NSE opening time (9:15 AM IST).
    """
    # Parse date/time
    dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
    utc_dt = dt - timedelta(minutes=timezone_offset_minutes)

    jd = swe.julday(
        utc_dt.year, utc_dt.month, utc_dt.day,
        utc_dt.hour + utc_dt.minute / 60.0
    )

    # Set ayanamsa
    ayanamsa_map = {
        "lahiri": swe.SIDM_LAHIRI,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "raman": swe.SIDM_RAMAN,
    }
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key.lower(), swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    # Get Sun and Moon positions
    sun_result = swe.calc_ut(jd, swe.SUN, flags)
    moon_result = swe.calc_ut(jd, swe.MOON, flags)
    sun_long = sun_result[0][0] % 360
    moon_long = moon_result[0][0] % 360

    # 1. TITHI
    tithi_data = _calc_tithi(sun_long, moon_long)

    # 2. NAKSHATRA (Moon's)
    nakshatra_data = _calc_nakshatra(moon_long)

    # 3. YOGA
    yoga_data = _calc_yoga(sun_long, moon_long)

    # 4. KARANA
    karana_data = _calc_karana(sun_long, moon_long)

    # 5. VARA
    vara_data = _calc_vara(dt)

    # 6. MUHURTA
    muhurta_data = calculate_muhurta(dt, latitude, longitude, timezone_offset_minutes)

    # Combined Financial Score
    financial = _panchang_financial_score(tithi_data, nakshatra_data, yoga_data, karana_data, vara_data)

    return {
        "type": "panchang",
        "date": date_str,
        "time": time_str,
        "location": {"latitude": latitude, "longitude": longitude},
        "ayanamsa": ayanamsa_key,
        "sun_longitude": round(sun_long, 4),
        "moon_longitude": round(moon_long, 4),
        "tithi": tithi_data,
        "nakshatra": nakshatra_data,
        "yoga": yoga_data,
        "karana": karana_data,
        "vara": vara_data,
        "muhurta": muhurta_data,
        "financial_analysis": financial,
    }


def _calc_tithi(sun_long: float, moon_long: float) -> Dict:
    """Calculate Tithi (lunar day) from Moon-Sun angular distance."""
    diff = (moon_long - sun_long) % 360
    tithi_num = int(diff / 12.0)  # Each tithi = 12°
    tithi_fraction = (diff % 12.0) / 12.0  # How much of tithi elapsed

    paksha = "Shukla" if tithi_num < 15 else "Krishna"
    tithi_in_paksha = (tithi_num % 15)
    tithi_name = TITHIS[tithi_in_paksha]

    # Full moon / New moon
    if tithi_num == 14:
        tithi_name = "Purnima"
    elif tithi_num == 29 or tithi_num >= 29:
        tithi_name = "Amavasya"

    fin = TITHI_FINANCIAL.get(tithi_name, TITHI_FINANCIAL.get("Purnima/Amavasya", {}))

    return {
        "tithi_number": tithi_num + 1,
        "tithi_name": tithi_name,
        "paksha": paksha,
        "tithi_fraction_elapsed": round(tithi_fraction, 4),
        "nature": fin.get("nature", ""),
        "financial_score": fin.get("score", 0),
        "nse_signal": fin.get("signal", "NEUTRAL"),
    }


def _calc_nakshatra(moon_long: float) -> Dict:
    """Calculate Moon's Nakshatra."""
    nak_idx = int(moon_long / NAKSHATRA_SPAN_DEG)
    nak_idx = min(nak_idx, 26)
    nak_name = NAKSHATRA_NAMES[nak_idx]
    degree_in_nak = moon_long - (nak_idx * NAKSHATRA_SPAN_DEG)
    pada = int(degree_in_nak / (NAKSHATRA_SPAN_DEG / 4)) + 1
    pada = min(pada, 4)

    return {
        "nakshatra_number": nak_idx + 1,
        "nakshatra_name": nak_name,
        "pada": pada,
        "degree_in_nakshatra": round(degree_in_nak, 4),
    }


def _calc_yoga(sun_long: float, moon_long: float) -> Dict:
    """Calculate Yoga (Sun + Moon longitudes / 13.333°)."""
    total = (sun_long + moon_long) % 360
    yoga_idx = int(total / NAKSHATRA_SPAN_DEG)
    yoga_idx = min(yoga_idx, 26)
    yoga_name = YOGA_NAMES[yoga_idx]
    score = YOGA_FINANCIAL.get(yoga_name, 0)

    return {
        "yoga_number": yoga_idx + 1,
        "yoga_name": yoga_name,
        "financial_score": score,
        "signal": (
            "BULLISH" if score > 0.5 else
            "MILDLY BULLISH" if score > 0 else
            "BEARISH" if score < -0.3 else "NEUTRAL"
        ),
    }


def _calc_karana(sun_long: float, moon_long: float) -> Dict:
    """Calculate Karana (half-tithi)."""
    diff = (moon_long - sun_long) % 360
    karana_num = int(diff / 6.0)  # Each karana = 6°

    # Fixed karanas: first half of Shukla Pratipada = Kimstughna
    # Movable karanas cycle: Bava, Balava, Kaulava, Taitila, Garija, Vanija, Vishti
    if karana_num == 0:
        karana_name = "Kimstughna"
    elif karana_num >= 57:
        fixed_idx = karana_num - 57
        fixed_karanas = ["Shakuni", "Chatushpada", "Naga"]
        karana_name = fixed_karanas[min(fixed_idx, 2)]
    else:
        movable_idx = (karana_num - 1) % 7
        movable_karanas = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti"]
        karana_name = movable_karanas[movable_idx]

    # Vishti (Bhadra) karana is inauspicious for trading
    is_vishti = karana_name == "Vishti"

    return {
        "karana_number": karana_num + 1,
        "karana_name": karana_name,
        "is_vishti_bhadra": is_vishti,
        "financial_note": (
            "AVOID — Vishti (Bhadra) Karana active. No new positions."
            if is_vishti else
            f"{karana_name} Karana — normal trading conditions"
        ),
        "score": -0.50 if is_vishti else 0.10,
    }


def _calc_vara(dt: datetime) -> Dict:
    """Calculate Vara (weekday) and its lord."""
    day_name = dt.strftime("%A")
    lord = VARA_LORDS.get(day_name, "")

    # Day-wise market tendencies (empirical + traditional)
    vara_scores = {
        "Monday": 0.30,     # Moon — sentiment driven
        "Tuesday": 0.20,    # Mars — volatile energy
        "Wednesday": 0.50,  # Mercury — trading/commerce
        "Thursday": 0.70,   # Jupiter — expansion, best for buying
        "Friday": 0.60,     # Venus — consumer sectors strong
        "Saturday": -0.20,  # Saturn — markets closed but pre-analysis
        "Sunday": -0.20,    # Sun — markets closed
    }

    return {
        "day": day_name,
        "lord": lord,
        "financial_score": vara_scores.get(day_name, 0),
        "note": f"{day_name} ruled by {lord}",
    }


# ─────────────────────────────────────────────────────────────
# Muhurta — Best Trading Windows
# ─────────────────────────────────────────────────────────────

def calculate_muhurta(
    dt: datetime,
    latitude: float = 19.076,
    longitude_geo: float = 72.8777,
    timezone_offset: int = 330,
) -> Dict:
    """
    Calculate Muhurta (auspicious time windows) for a given day.
    Includes Rahu Kalam, Gulika Kalam, Abhijit Muhurta, and Choghadiya.
    """
    # Approximate sunrise/sunset (simplified for Indian markets)
    sunrise_hour = 6.0  # ~6:00 AM
    sunset_hour = 18.5   # ~6:30 PM
    day_duration = sunset_hour - sunrise_hour
    night_duration = 24 - day_duration

    # Rahu Kalam (inauspicious — avoid trading)
    rahu_kalam = _calc_rahu_kalam(dt.weekday(), sunrise_hour, day_duration)

    # Gulika Kalam (inauspicious)
    gulika_kalam = _calc_gulika_kalam(dt.weekday(), sunrise_hour, day_duration)

    # Yamaganda (inauspicious)
    yamaganda = _calc_yamaganda(dt.weekday(), sunrise_hour, day_duration)

    # Abhijit Muhurta (most auspicious — best for major trades)
    midday = (sunrise_hour + sunset_hour) / 2
    abhijit_start = midday - 0.4  # ~24 min before midday
    abhijit_end = midday + 0.4    # ~24 min after midday

    # Choghadiya (Gujarati trading system — 8 periods per day/night)
    choghadiya = _calc_choghadiya(dt.weekday(), sunrise_hour, sunset_hour)

    return {
        "rahu_kalam": {
            "start": _format_time(rahu_kalam[0]),
            "end": _format_time(rahu_kalam[1]),
            "warning": "AVOID trading during Rahu Kalam",
        },
        "gulika_kalam": {
            "start": _format_time(gulika_kalam[0]),
            "end": _format_time(gulika_kalam[1]),
            "warning": "AVOID initiating new positions",
        },
        "yamaganda": {
            "start": _format_time(yamaganda[0]),
            "end": _format_time(yamaganda[1]),
            "warning": "Caution period",
        },
        "abhijit_muhurta": {
            "start": _format_time(abhijit_start),
            "end": _format_time(abhijit_end),
            "note": "BEST time for major trades and new investments",
        },
        "choghadiya": choghadiya,
        "nse_trading_windows": _nse_trading_windows(
            rahu_kalam, gulika_kalam, abhijit_start, abhijit_end
        ),
    }


# Rahu Kalam sequence: Sun=8, Mon=2, Tue=7, Wed=5, Thu=6, Fri=4, Sat=3
RAHU_KALAM_PERIOD = {6: 8, 0: 2, 1: 7, 2: 5, 3: 6, 4: 4, 5: 3}
# Gulika: Sun=7, Mon=6, Tue=5, Wed=4, Thu=3, Fri=2, Sat=1
GULIKA_PERIOD = {6: 7, 0: 6, 1: 5, 2: 4, 3: 3, 4: 2, 5: 1}
# Yamaganda: Sun=5, Mon=4, Tue=3, Wed=7, Thu=2, Fri=1, Sat=6
YAMA_PERIOD = {6: 5, 0: 4, 1: 3, 2: 7, 3: 2, 4: 1, 5: 6}


def _calc_rahu_kalam(weekday: int, sunrise: float, day_dur: float) -> Tuple[float, float]:
    period = RAHU_KALAM_PERIOD.get(weekday, 1)
    slot = day_dur / 8
    start = sunrise + (period - 1) * slot
    return (start, start + slot)


def _calc_gulika_kalam(weekday: int, sunrise: float, day_dur: float) -> Tuple[float, float]:
    period = GULIKA_PERIOD.get(weekday, 1)
    slot = day_dur / 8
    start = sunrise + (period - 1) * slot
    return (start, start + slot)


def _calc_yamaganda(weekday: int, sunrise: float, day_dur: float) -> Tuple[float, float]:
    period = YAMA_PERIOD.get(weekday, 1)
    slot = day_dur / 8
    start = sunrise + (period - 1) * slot
    return (start, start + slot)


# Choghadiya: day periods ruled by planets
CHOGHADIYA_ORDER_DAY = {
    6: ["Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg"],
    0: ["Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit"],
    1: ["Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog"],
    2: ["Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh"],
    3: ["Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal", "Shubh"],
    4: ["Chal", "Labh", "Amrit", "Kaal", "Shubh", "Rog", "Udveg", "Chal"],
    5: ["Kaal", "Shubh", "Rog", "Udveg", "Chal", "Labh", "Amrit", "Kaal"],
}

CHOGHADIYA_QUALITY = {
    "Amrit":  {"quality": "Best", "score": 0.90, "color": "#00C851", "trading": "STRONG BUY window"},
    "Shubh":  {"quality": "Good", "score": 0.70, "color": "#4CAF50", "trading": "BUY window"},
    "Labh":   {"quality": "Gain", "score": 0.80, "color": "#8BC34A", "trading": "PROFIT BOOKING window"},
    "Chal":   {"quality": "Neutral", "score": 0.30, "color": "#FFC107", "trading": "Quick trades only"},
    "Rog":    {"quality": "Bad", "score": -0.40, "color": "#FF9800", "trading": "AVOID new positions"},
    "Kaal":   {"quality": "Very Bad", "score": -0.60, "color": "#FF5722", "trading": "NO TRADING"},
    "Udveg":  {"quality": "Anxious", "score": -0.50, "color": "#FF3D00", "trading": "AVOID — high anxiety"},
}


def _calc_choghadiya(weekday: int, sunrise: float, sunset: float) -> List[Dict]:
    """Calculate day Choghadiya periods (8 slots from sunrise to sunset)."""
    order = CHOGHADIYA_ORDER_DAY.get(weekday, CHOGHADIYA_ORDER_DAY[0])
    slot_duration = (sunset - sunrise) / 8
    result = []

    for i, name in enumerate(order):
        start = sunrise + i * slot_duration
        end = start + slot_duration
        quality = CHOGHADIYA_QUALITY.get(name, {})
        result.append({
            "period": i + 1,
            "name": name,
            "start": _format_time(start),
            "end": _format_time(end),
            "quality": quality.get("quality", ""),
            "score": quality.get("score", 0),
            "color": quality.get("color", "#9E9E9E"),
            "trading_signal": quality.get("trading", ""),
        })

    return result


def _nse_trading_windows(
    rahu: Tuple, gulika: Tuple,
    abhijit_start: float, abhijit_end: float,
) -> Dict:
    """Map Muhurta to NSE trading hours (9:15 AM - 3:30 PM)."""
    nse_open = 9.25   # 9:15 AM
    nse_close = 15.5  # 3:30 PM

    # Check if Rahu Kalam falls during market hours
    rahu_during_market = (
        rahu[0] < nse_close and rahu[1] > nse_open
    )
    abhijit_during_market = (
        nse_open <= abhijit_start <= nse_close
    )

    return {
        "nse_hours": f"{_format_time(nse_open)} - {_format_time(nse_close)}",
        "rahu_kalam_during_market": rahu_during_market,
        "rahu_warning": (
            f"Rahu Kalam ({_format_time(rahu[0])}-{_format_time(rahu[1])}) overlaps market hours — CAUTION"
            if rahu_during_market else "Rahu Kalam outside market hours — safe"
        ),
        "best_entry_time": (
            f"Abhijit Muhurta: {_format_time(abhijit_start)}-{_format_time(abhijit_end)}"
            if abhijit_during_market else
            f"First hour after opening: {_format_time(nse_open)}-{_format_time(nse_open + 1)}"
        ),
        "avoid_windows": [],
    }


def _format_time(hours: float) -> str:
    """Convert decimal hours to HH:MM format."""
    h = int(hours)
    m = int((hours - h) * 60)
    return f"{h:02d}:{m:02d}"


# ─────────────────────────────────────────────────────────────
# Combined Financial Score
# ─────────────────────────────────────────────────────────────

def _panchang_financial_score(
    tithi: Dict, nakshatra: Dict, yoga: Dict,
    karana: Dict, vara: Dict,
) -> Dict:
    """
    Combine all 5 Panchang elements into a single financial score.
    Weights: Tithi=30%, Yoga=25%, Vara=20%, Karana=15%, Nakshatra=10%
    """
    tithi_score = tithi.get("financial_score", 0)
    yoga_score = yoga.get("financial_score", 0)
    vara_score = vara.get("financial_score", 0)
    karana_score = karana.get("score", 0)
    # Nakshatra score from existing module would be plugged in
    nak_score = 0.3  # default neutral-positive

    combined = (
        tithi_score * 0.30 +
        yoga_score * 0.25 +
        vara_score * 0.20 +
        karana_score * 0.15 +
        nak_score * 0.10
    )
    combined = max(-1.0, min(1.0, combined))

    if combined >= 0.5:
        signal = "STRONGLY AUSPICIOUS"
        action = "Excellent Panchang — initiate trades, buy aggressively"
        color = "#00C851"
    elif combined >= 0.2:
        signal = "AUSPICIOUS"
        action = "Good Panchang — favorable for buying and new positions"
        color = "#4CAF50"
    elif combined >= 0:
        signal = "NEUTRAL"
        action = "Mixed Panchang — routine trading, no major initiations"
        color = "#FFC107"
    elif combined >= -0.3:
        signal = "INAUSPICIOUS"
        action = "Weak Panchang — reduce risk, avoid new positions"
        color = "#FF9800"
    else:
        signal = "HIGHLY INAUSPICIOUS"
        action = "Very poor Panchang — capital preservation mode"
        color = "#FF3D00"

    return {
        "combined_score": round(combined, 3),
        "signal": signal,
        "action": action,
        "color": color,
        "breakdown": {
            "tithi_score": round(tithi_score, 3),
            "yoga_score": round(yoga_score, 3),
            "vara_score": round(vara_score, 3),
            "karana_score": round(karana_score, 3),
            "nakshatra_score": round(nak_score, 3),
        },
        "weights": "Tithi 30% | Yoga 25% | Vara 20% | Karana 15% | Nakshatra 10%",
    }


# ─────────────────────────────────────────────────────────────
# Multi-day Panchang Calendar
# ─────────────────────────────────────────────────────────────

def calculate_panchang_calendar(
    start_date: str,
    days: int = 30,
    latitude: float = 19.076,
    longitude: float = 72.8777,
    timezone_offset_minutes: int = 330,
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """Generate Panchang calendar for multiple days with trading signals."""
    calendar_data = []
    dt = datetime.strptime(start_date, "%Y-%m-%d")

    for day_offset in range(days):
        current = dt + timedelta(days=day_offset)
        # Skip weekends
        if current.weekday() in (5, 6):
            continue
        date_str = current.strftime("%Y-%m-%d")
        panchang = calculate_panchang(
            date_str, "09:15", latitude, longitude,
            timezone_offset_minutes, ayanamsa_key
        )
        calendar_data.append({
            "date": date_str,
            "day": current.strftime("%A"),
            "tithi": panchang["tithi"]["tithi_name"],
            "paksha": panchang["tithi"]["paksha"],
            "nakshatra": panchang["nakshatra"]["nakshatra_name"],
            "yoga": panchang["yoga"]["yoga_name"],
            "karana": panchang["karana"]["karana_name"],
            "combined_score": panchang["financial_analysis"]["combined_score"],
            "signal": panchang["financial_analysis"]["signal"],
            "color": panchang["financial_analysis"]["color"],
        })

    # Sort by score
    best_days = sorted(calendar_data, key=lambda x: -x["combined_score"])[:5]
    worst_days = sorted(calendar_data, key=lambda x: x["combined_score"])[:5]

    return {
        "type": "panchang_calendar",
        "start_date": start_date,
        "total_trading_days": len(calendar_data),
        "calendar": calendar_data,
        "best_trading_days": best_days,
        "worst_trading_days": worst_days,
        "avg_score": round(
            sum(d["combined_score"] for d in calendar_data) / len(calendar_data), 3
        ) if calendar_data else 0,
    }
