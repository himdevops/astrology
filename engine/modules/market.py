"""
Moon Market Analysis Module
============================
Applies Vedic astrology rules to Moon transit data for NSE/BSE
market direction prediction (Bullish / Bearish / Neutral).
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Any, Optional, Tuple

from core.ephemeris import get_all_planets, calc_ascendant, PlanetPosition
from core.utils import local_to_utc, datetime_to_jd

# ═══════════════════════════════════════════════════════════════
# CONSTANTS — Market Astrology Rules
# ═══════════════════════════════════════════════════════════════

RASHI_NAMES = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
RASHI_HI = [
    "मेष", "वृष", "मिथुन", "कर्क", "सिंह", "कन्या",
    "तुला", "वृश्चिक", "धनु", "मकर", "कुम्भ", "मीन",
]

NAKS_27 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha",
    "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta",
    "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Mula", "Purva Ashadha", "Uttara Ashadha",
    "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

# ── Rule 1: Tithi ──
# Krishna Paksha Ekadashi (K11) to Shukla Paksha Panchami (S5) = Bullish
# Shukla Paksha Shashthi (S6) to Krishna Paksha Dashami (K10) = Bearish

# ── Rule 2: Moon Rashi ──
RASHI_SIGNAL = {
    "Aries": "bullish", "Taurus": "bullish", "Gemini": "bearish",
    "Cancer": "bearish", "Leo": "bullish", "Virgo": "bearish",
    "Libra": "bearish", "Scorpio": "bullish", "Sagittarius": "bearish",
    "Capricorn": "bullish", "Aquarius": "bearish", "Pisces": "bearish",
}

# ── Rule 2a: Rashi Lord Signal ──
# Malefic lords (Sun, Saturn, Mars, Rahu, Ketu) = Bullish
# Benefic lords (Venus, Mercury, Moon, Jupiter) = Bearish
RASHI_LORD = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}
RASHI_LORD_SIGNAL = {
    "Sun": "bullish", "Moon": "bearish", "Mars": "bullish",
    "Mercury": "bearish", "Jupiter": "bearish", "Venus": "bearish",
    "Saturn": "bullish", "Rahu": "bullish", "Ketu": "bullish",
}

# ── Rule 2b: Rashi Degree Ranges (same for all rashis) ──
# Alternating 2-pada (6°40') and 1-pada (3°20') ranges
# Pattern from image: all green for bullish rashi, varies otherwise
DEGREE_RANGES = [
    {"start": 0.0, "end": 6.6667, "signal": "bullish", "label": "0°-6°40'"},
    {"start": 6.6667, "end": 10.0, "signal": "bearish", "label": "6°40'-10°"},
    {"start": 10.0, "end": 16.6667, "signal": "bullish", "label": "10°-16°40'"},
    {"start": 16.6667, "end": 20.0, "signal": "bearish", "label": "16°40'-20°"},
    {"start": 20.0, "end": 26.6667, "signal": "bullish", "label": "20°-26°40'"},
    {"start": 26.6667, "end": 30.0, "signal": "bearish", "label": "26°40'-30°"},
]

# ── Rule 3: Nakshatra Classification ──
# Extracted from screenshots (green = bullish, red = bearish, white = NA)
NAKSHATRA_SIGNAL = {
    "Ashwini": "bullish", "Bharani": "bullish", "Krittika": "bullish",
    "Rohini": "bearish", "Mrigashira": "bullish", "Ardra": "bullish",
    "Punarvasu": "bearish", "Pushya": "bearish", "Ashlesha": "bullish",
    "Magha": "bullish", "Purva Phalguni": "bearish", "Uttara Phalguni": "bullish",
    "Hasta": "bearish", "Chitra": "bullish", "Swati": "bullish",
    "Vishakha": "bearish", "Anuradha": "bullish", "Jyeshtha": "bullish",
    "Mula": "bearish", "Purva Ashadha": "bearish", "Uttara Ashadha": "bullish",
    "Shravana": "bullish", "Dhanishtha": "bearish", "Shatabhisha": "bullish",
    "Purva Bhadrapada": "bearish", "Uttara Bhadrapada": "bullish", "Revati": "bearish",
    "Abhijeet": "bearish",
}

# ── Rule 4: Moon Conjunction (Yuti) ──
# Moon + planet conjunction signal
CONJUNCTION_SIGNAL = {
    "Sun": "bullish", "Venus": "bearish", "Mercury": "bullish",
    "Jupiter": "bearish", "Mars": "bullish", "Saturn": "bullish",
    "Rahu": "bullish", "Ketu": "bearish",
    "Uranus": "bullish", "Pluto": "bullish", "Neptune": "bearish",
}

# ── Rule 5: Shadashtak (6/8 relationship) ──
# Pairs where rashi1-rashi2 are in 6/8 from each other
# Green pairs = bullish, Red pairs = bearish
SHADASHTAK_PAIRS_BULLISH = {
    (1, 8), (8, 1),   # Aries-Scorpio
    (2, 7), (7, 2),   # Taurus-Libra
    (1, 6), (6, 1),   # Aries-Virgo
    (11, 4), (4, 11), # Aquarius-Cancer
}
# All other 6/8 pairs are bearish

# ── Rule 6: Dwidamsha (2/12 relationship) ──
# Forward consecutive pairs = bullish, backward = bearish
DWIDAMSHA_BULLISH = {
    (12, 1), (2, 3), (4, 5), (6, 7), (8, 9), (10, 11),
}
DWIDAMSHA_BEARISH = {
    (10, 9), (12, 11), (2, 1), (4, 3), (6, 5), (8, 7),
}

# ── Rule 7: Western Aspects ──
ASPECT_SIGNAL = {
    0: "neutral",     # Conjunction
    60: "bullish",    # Sextile
    90: "bearish",    # Square
    120: "bullish",   # Trine
    180: "bearish",   # Opposition
}

# ── Rule 8: Hora Planet ──
HORA_SIGNAL = {
    "Sun": "bullish", "Venus": "bullish", "Mercury": "neutral",
    "Moon": "neutral", "Saturn": "bearish", "Jupiter": "bullish",
    "Mars": "bullish",
}

# ── Conjunction threshold (degrees) ──
CONJUNCTION_ORB = 10.0  # degrees
ASPECT_ORB = 8.0  # orb for western aspects


# ═══════════════════════════════════════════════════════════════
# CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_tithi_info(sun_lon: float, moon_lon: float) -> Dict:
    """Calculate tithi number, paksha, and market signal."""
    diff = (moon_lon - sun_lon) % 360
    tithi_idx = int(diff / 12) % 30  # 0-29
    tithi_num = tithi_idx + 1  # 1-30

    if tithi_num <= 15:
        paksha = "Shukla"
        paksha_tithi = tithi_num
    else:
        paksha = "Krishna"
        paksha_tithi = tithi_num - 15

    tithi_names_s = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    ]
    tithi_names_k = [
        "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
        "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
        "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
    ]

    if paksha == "Shukla":
        tithi_name = f"Shukla {tithi_names_s[paksha_tithi - 1]}"
    else:
        tithi_name = f"Krishna {tithi_names_k[paksha_tithi - 1]}"

    # Rule 1: K11 to S5 = Bullish, S6 to K10 = Bearish
    # K11 = tithi_num 26, S5 = tithi_num 5
    # Bullish range: 26,27,28,29,30,1,2,3,4,5
    # Bearish range: 6,7,8,9,10,11,12,13,14,15,16,17,18,19,20,21,22,23,24,25
    if tithi_num >= 26 or tithi_num <= 5:
        signal = "bullish"
    elif tithi_num >= 6 and tithi_num <= 25:
        signal = "bearish"
    else:
        signal = "neutral"

    return {
        "tithi_num": tithi_num,
        "tithi_name": tithi_name,
        "paksha": paksha,
        "paksha_tithi": paksha_tithi,
        "signal": signal,
    }


def get_rashi_info(moon_lon: float) -> Dict:
    """Moon rashi and degree analysis."""
    rashi_idx = int(moon_lon / 30) % 12
    deg_in_rashi = moon_lon % 30
    rashi_name = RASHI_NAMES[rashi_idx]
    rashi_hi = RASHI_HI[rashi_idx]

    # Rashi signal
    rashi_signal = RASHI_SIGNAL.get(rashi_name, "neutral")

    # Degree range signal
    deg_signal = "neutral"
    deg_label = ""
    for dr in DEGREE_RANGES:
        if dr["start"] <= deg_in_rashi < dr["end"]:
            deg_signal = dr["signal"]
            deg_label = dr["label"]
            break

    # Rashi Lord signal
    rashi_lord = RASHI_LORD.get(rashi_name, "")
    rashi_lord_signal = RASHI_LORD_SIGNAL.get(rashi_lord, "neutral")

    return {
        "rashi_name": rashi_name,
        "rashi_hi": rashi_hi,
        "rashi_index": rashi_idx + 1,
        "degree_in_rashi": round(deg_in_rashi, 2),
        "rashi_signal": rashi_signal,
        "degree_signal": deg_signal,
        "degree_label": deg_label,
        "rashi_lord": rashi_lord,
        "rashi_lord_signal": rashi_lord_signal,
    }


def get_nakshatra_info(moon: PlanetPosition) -> Dict:
    """Moon nakshatra and pada. Also checks for Abhijeet (28th nakshatra)."""
    nak_name = moon.nakshatra
    pada = moon.nakshatra_pada

    # Abhijeet nakshatra: 6°40' to 10°53'20" Capricorn (abs longitude 276.6667° to 280.8889°)
    is_abhijeet = False
    if 276.6667 <= moon.longitude < 280.8889:
        is_abhijeet = True

    signal = NAKSHATRA_SIGNAL.get(nak_name, "neutral")

    result = {
        "nakshatra": nak_name,
        "pada": pada,
        "nakshatra_lord": moon.nakshatra_lord,
        "signal": signal,
    }

    if is_abhijeet:
        result["abhijeet"] = True
        result["abhijeet_signal"] = NAKSHATRA_SIGNAL.get("Abhijeet", "bearish")

    return result


NAVAMSHA_SIGNAL = {
    "Aries": "bullish", "Taurus": "bullish", "Gemini": "bearish",
    "Cancer": "bearish", "Leo": "bullish", "Virgo": "bearish",
    "Libra": "bearish", "Scorpio": "bullish", "Sagittarius": "bearish",
    "Capricorn": "bullish", "Aquarius": "bearish", "Pisces": "bearish",
}


def get_navamsha_rashi(longitude: float) -> Dict:
    """Calculate Navamsha (D9) rashi for a given longitude."""
    # Each navamsha = 3°20' = 3.3333°
    navamsha_idx = int(longitude / 3.3333) % 12
    nav_rashi = RASHI_NAMES[navamsha_idx]
    return {
        "rashi_name": nav_rashi,
        "rashi_hi": RASHI_HI[navamsha_idx],
        "rashi_index": navamsha_idx + 1,
        "signal": NAVAMSHA_SIGNAL.get(nav_rashi, "bearish"),
    }


def get_conjunctions(moon: PlanetPosition, planets: List[PlanetPosition]) -> List[Dict]:
    """Find planets conjunct with Moon (within orb)."""
    results = []
    for p in planets:
        if p.planet == "Moon":
            continue
        diff = abs(((moon.longitude - p.longitude) % 360 + 180) % 360 - 180)
        if diff <= CONJUNCTION_ORB:
            signal = CONJUNCTION_SIGNAL.get(p.planet, "neutral")
            results.append({
                "planet": p.planet,
                "distance": round(diff, 2),
                "signal": signal,
            })
    return results


NAVAMSHA_YUTI_SIGNAL = {
    "Sun": "bullish", "Venus": "bullish", "Mercury": "bullish",
    "Jupiter": "bullish", "Mars": "bullish", "Rahu": "bullish",
    "Ketu": "bearish", "Saturn": "bearish",
    "Uranus": "bullish", "Pluto": "bullish", "Neptune": "bearish",
}


def get_navamsha_conjunctions(moon_lon: float, planets: List[PlanetPosition]) -> List[Dict]:
    """Find planets conjunct with Moon in Navamsha chart."""
    moon_nav = int(moon_lon / 3.3333) % 12
    results = []
    for p in planets:
        if p.planet == "Moon":
            continue
        p_nav = int(p.longitude / 3.3333) % 12
        if p_nav == moon_nav:
            signal = NAVAMSHA_YUTI_SIGNAL.get(p.planet, "neutral")
            results.append({
                "planet": p.planet,
                "navamsha_rashi": RASHI_NAMES[p_nav],
                "signal": signal,
            })
    return results


def get_shadashtak(moon_rashi_idx: int, planets: List[PlanetPosition]) -> List[Dict]:
    """Check 6/8 relationship of Moon with other planets."""
    results = []
    for p in planets:
        if p.planet == "Moon":
            continue
        p_rashi = int(p.longitude / 30) % 12 + 1
        m_rashi = moon_rashi_idx + 1
        diff = ((p_rashi - m_rashi) % 12)
        if diff == 5 or diff == 7:  # 6th or 8th from each other
            pair = (m_rashi, p_rashi)
            if pair in SHADASHTAK_PAIRS_BULLISH:
                signal = "bullish"
            else:
                signal = "bearish"
            results.append({
                "planet": p.planet,
                "moon_rashi": RASHI_NAMES[moon_rashi_idx],
                "planet_rashi": RASHI_NAMES[int(p.longitude / 30) % 12],
                "pair": f"{RASHI_NAMES[m_rashi-1]} - {RASHI_NAMES[p_rashi-1]} ({m_rashi}-{p_rashi})",
                "relationship": "6th" if diff == 5 else "8th",
                "signal": signal,
            })
    return results


def get_dwidamsha(moon_rashi_idx: int, planets: List[PlanetPosition]) -> List[Dict]:
    """Check 2/12 relationship of Moon with other planets."""
    results = []
    for p in planets:
        if p.planet == "Moon":
            continue
        p_rashi = int(p.longitude / 30) % 12 + 1
        m_rashi = moon_rashi_idx + 1
        diff = ((p_rashi - m_rashi) % 12)
        if diff == 1 or diff == 11:  # 2nd or 12th from each other
            pair = (m_rashi, p_rashi)
            if pair in DWIDAMSHA_BULLISH:
                signal = "bullish"
            elif pair in DWIDAMSHA_BEARISH:
                signal = "bearish"
            else:
                signal = "neutral"
            results.append({
                "planet": p.planet,
                "pair": f"{RASHI_NAMES[m_rashi-1]} - {RASHI_NAMES[p_rashi-1]} ({m_rashi}-{p_rashi})",
                "relationship": "2nd" if diff == 1 else "12th",
                "signal": signal,
            })
    return results


def get_western_aspects(moon: PlanetPosition, planets: List[PlanetPosition]) -> List[Dict]:
    """Calculate western aspects (0, 60, 90, 120, 180) between Moon and planets."""
    results = []
    aspect_angles = [0, 60, 90, 120, 180]
    for p in planets:
        if p.planet in ("Moon", "Rahu", "Ketu"):
            continue
        diff = abs(((moon.longitude - p.longitude) % 360 + 180) % 360 - 180)
        for angle in aspect_angles:
            if abs(diff - angle) <= ASPECT_ORB:
                signal = ASPECT_SIGNAL.get(angle, "neutral")
                results.append({
                    "planet": p.planet,
                    "aspect_angle": angle,
                    "actual_angle": round(diff, 2),
                    "signal": signal,
                    "aspect_name": {0: "Conjunction", 60: "Sextile", 90: "Square",
                                    120: "Trine", 180: "Opposition"}.get(angle, ""),
                })
                break
    return results


def get_hora_planet(dt: datetime) -> Dict:
    """Calculate the Hora (planetary hour) ruler."""
    # Day lords: Sun=0, Mon=1, Tue=2, Wed=3, Thu=4, Fri=5, Sat=6
    weekday = dt.weekday()  # Monday=0
    day_lord_order = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    # Hora sequence: each planet rules 1 hour, cycling through Chaldean order
    hora_sequence = ["Saturn", "Jupiter", "Mars", "Sun", "Venus", "Mercury", "Moon"]

    # Find hora start from the day lord
    day_lord = day_lord_order[weekday]
    start_idx = hora_sequence.index(day_lord)

    # Hours since sunrise (approximate: 6 AM)
    hour_since_sunrise = dt.hour - 6
    if hour_since_sunrise < 0:
        hour_since_sunrise += 24

    hora_idx = (start_idx + hour_since_sunrise) % 7
    hora_planet = hora_sequence[hora_idx]

    signal = HORA_SIGNAL.get(hora_planet, "neutral")

    return {
        "hora_planet": hora_planet,
        "hora_num": hour_since_sunrise + 1,
        "signal": signal,
    }


def get_sat_moon_dwidamsha(moon_lon: float, saturn_lon: float) -> Dict:
    """Special exception: Saturn-Moon Dwidamsha (2/12) = always Bullish."""
    moon_rashi = int(moon_lon / 30) % 12 + 1
    sat_rashi = int(saturn_lon / 30) % 12 + 1
    diff = ((sat_rashi - moon_rashi) % 12)
    if diff == 1 or diff == 11:
        return {
            "active": True,
            "pair": f"{RASHI_NAMES[moon_rashi-1]} - {RASHI_NAMES[sat_rashi-1]}",
            "signal": "bullish",
            "note": "Exception: Sat-Moon Dwidamsha is always Bullish",
        }
    return {"active": False, "signal": "neutral"}


# ═══════════════════════════════════════════════════════════════
# MAIN ANALYSIS FUNCTION
# ═══════════════════════════════════════════════════════════════

def generate_market_analysis(
    analysis_dt: datetime,
    tz: float = 5.5,
    ayanamsa: str = "lahiri",
    lat: float = 18.9750,   # Mumbai (NSE)
    lon: float = 72.8258,
) -> Dict[str, Any]:
    """
    Generate complete Moon-based market analysis for NSE/BSE.

    Args:
        analysis_dt: DateTime to analyze (typically 9:15 AM or 1:15 PM IST)
        tz: Timezone offset
        ayanamsa: Ayanamsa system
        lat, lon: Location (default: Mumbai / NSE)

    Returns:
        Dict with all rule signals and overall verdict
    """
    utc_dt = local_to_utc(analysis_dt, tz)
    jd = datetime_to_jd(utc_dt)
    planets = get_all_planets(jd, ayanamsa)

    # Find Moon and Sun
    moon = None
    sun = None
    saturn = None
    for p in planets:
        if p.planet == "Moon":
            moon = p
        elif p.planet == "Sun":
            sun = p
        elif p.planet == "Saturn":
            saturn = p

    if not moon or not sun:
        return {"error": "Could not calculate Moon/Sun positions"}

    moon_rashi_idx = int(moon.longitude / 30) % 12

    # ── Apply all rules ──
    tithi = get_tithi_info(sun.longitude, moon.longitude)
    rashi = get_rashi_info(moon.longitude)
    nakshatra = get_nakshatra_info(moon)
    navamsha = get_navamsha_rashi(moon.longitude)
    conjunctions = get_conjunctions(moon, planets)
    nav_conjunctions = get_navamsha_conjunctions(moon.longitude, planets)
    shadashtak = get_shadashtak(moon_rashi_idx, planets)
    dwidamsha = get_dwidamsha(moon_rashi_idx, planets)
    sat_moon_dwi = get_sat_moon_dwidamsha(moon.longitude, saturn.longitude) if saturn else {"active": False, "signal": "neutral"}
    western_aspects = get_western_aspects(moon, planets)
    hora = get_hora_planet(analysis_dt)

    # ── Collect all signals ──
    signals = []
    signals.append({"rule": "Tithi", "signal": tithi["signal"], "detail": tithi["tithi_name"]})
    signals.append({"rule": "Moon Rashi", "signal": rashi["rashi_signal"], "detail": f"{rashi['rashi_name']} ({rashi['rashi_hi']})"})
    signals.append({"rule": "Rashi Lord", "signal": rashi["rashi_lord_signal"], "detail": f"{rashi['rashi_lord']} ({rashi['rashi_name']})"})
    signals.append({"rule": "Rashi Degree", "signal": rashi["degree_signal"], "detail": f"{rashi['degree_label']} ({rashi['degree_in_rashi']:.1f}°)"})
    signals.append({"rule": "Nakshatra", "signal": nakshatra["signal"], "detail": f"{nakshatra['nakshatra']} P{nakshatra['pada']}"})
    if nakshatra.get("abhijeet"):
        signals.append({"rule": "Abhijeet Nakshatra", "signal": nakshatra["abhijeet_signal"], "detail": "Moon in Abhijeet (28th Nakshatra)"})
    signals.append({"rule": "Navamsha", "signal": navamsha["signal"], "detail": f"Moon in {navamsha['rashi_name']} ({navamsha['rashi_hi']})"})
    signals.append({"rule": "Hora", "signal": hora["signal"], "detail": hora["hora_planet"]})

    if conjunctions:
        for c in conjunctions:
            signals.append({"rule": f"Conjunction (Mo+{c['planet']})", "signal": c["signal"], "detail": f"{c['distance']}° apart"})
    else:
        signals.append({"rule": "Conjunction", "signal": "neutral", "detail": "No conjunction"})

    if nav_conjunctions:
        for nc in nav_conjunctions:
            signals.append({"rule": f"Navamsha Yuti (Mo+{nc['planet']})", "signal": nc["signal"], "detail": nc["navamsha_rashi"]})
    else:
        signals.append({"rule": "Navamsha Yuti", "signal": "neutral", "detail": "No yuti"})

    if shadashtak:
        for s in shadashtak:
            signals.append({"rule": f"Shadashtak ({s['relationship']})", "signal": s["signal"], "detail": s["pair"]})

    if dwidamsha:
        for d in dwidamsha:
            signals.append({"rule": f"Dwidamsha ({d['relationship']})", "signal": d["signal"], "detail": d["pair"]})

    if sat_moon_dwi.get("active"):
        signals.append({"rule": "Sat-Moon Dwidamsha (Exception)", "signal": "bullish", "detail": sat_moon_dwi["pair"]})

    for wa in western_aspects:
        signals.append({"rule": f"Western Aspect ({wa['aspect_name']})", "signal": wa["signal"], "detail": f"Mo-{wa['planet']} {wa['actual_angle']:.1f}°"})

    # ── Score calculation ──
    bullish_count = sum(1 for s in signals if s["signal"] == "bullish")
    bearish_count = sum(1 for s in signals if s["signal"] == "bearish")
    neutral_count = sum(1 for s in signals if s["signal"] == "neutral")
    total = len(signals)

    if bullish_count > bearish_count:
        overall = "bullish"
    elif bearish_count > bullish_count:
        overall = "bearish"
    else:
        overall = "neutral"

    strength = abs(bullish_count - bearish_count) / max(total, 1) * 100

    # ── Planet positions for display ──
    planet_data = []
    for p in planets:
        planet_data.append({
            "planet": p.planet,
            "longitude": round(p.longitude, 4),
            "sign": p.sign,
            "degree_in_sign": round(p.longitude % 30, 2),
            "nakshatra": p.nakshatra,
            "pada": p.nakshatra_pada,
            "retrograde": p.retrograde,
        })

    return {
        "analysis_time": analysis_dt.strftime("%d-%m-%Y %H:%M"),
        "moon": {
            "longitude": round(moon.longitude, 4),
            "sign": moon.sign,
            "degree_in_sign": round(moon.longitude % 30, 2),
            "nakshatra": moon.nakshatra,
            "pada": moon.nakshatra_pada,
            "nakshatra_lord": moon.nakshatra_lord,
        },
        "tithi": tithi,
        "rashi": rashi,
        "nakshatra_analysis": nakshatra,
        "navamsha": navamsha,
        "conjunctions": conjunctions,
        "navamsha_conjunctions": nav_conjunctions,
        "shadashtak": shadashtak,
        "dwidamsha": dwidamsha,
        "sat_moon_dwidamsha": sat_moon_dwi,
        "western_aspects": western_aspects,
        "hora": hora,
        "signals": signals,
        "score": {
            "bullish": bullish_count,
            "bearish": bearish_count,
            "neutral": neutral_count,
            "total": total,
            "overall": overall,
            "strength": round(strength, 1),
        },
        "planets": planet_data,
    }


# ═══════════════════════════════════════════════════════════════
# INTRADAY TREND CHANGE SCANNER (Ardha Prahara)
# ═══════════════════════════════════════════════════════════════

def generate_trend_scan(
    date_dt: datetime,
    tz: float = 5.5,
    ayanamsa: str = "lahiri",
    start_hour: int = 9, start_min: int = 15,
    end_hour: int = 17, end_min: int = 0,
    interval_min: int = 15,
) -> Dict[str, Any]:
    """
    Scan through the trading day at regular intervals and detect
    when the overall market signal changes (trend reversal points).

    Returns timeline of signals + list of trend change moments.
    """
    timeline = []
    trend_changes = []
    prev_overall = None
    prev_snapshot = None

    # Generate time slots
    current = datetime(date_dt.year, date_dt.month, date_dt.day, start_hour, start_min)
    end_time = datetime(date_dt.year, date_dt.month, date_dt.day, end_hour, end_min)

    while current <= end_time:
        result = generate_market_analysis(
            analysis_dt=current, tz=tz, ayanamsa=ayanamsa,
        )

        score = result.get("score", {})
        overall = score.get("overall", "neutral")
        strength = score.get("strength", 0)

        # Track what changed for each rule
        rule_signals = {}
        for s in result.get("signals", []):
            rule_signals[s["rule"]] = {"signal": s["signal"], "detail": s["detail"]}

        slot = {
            "time": current.strftime("%H:%M"),
            "overall": overall,
            "bullish": score.get("bullish", 0),
            "bearish": score.get("bearish", 0),
            "neutral": score.get("neutral", 0),
            "strength": strength,
            "moon_deg": result.get("moon", {}).get("longitude", 0),
            "moon_sign": result.get("moon", {}).get("sign", ""),
            "moon_nak": result.get("moon", {}).get("nakshatra", ""),
            "moon_deg_in_sign": result.get("moon", {}).get("degree_in_sign", 0),
            "hora": result.get("hora", {}).get("hora_planet", ""),
        }
        timeline.append(slot)

        # Detect trend change
        if prev_overall is not None and overall != prev_overall:
            # Find which rules changed
            changed_rules = []
            if prev_snapshot:
                for rule_name, cur_val in rule_signals.items():
                    prev_val = prev_snapshot.get(rule_name, {})
                    if prev_val.get("signal") != cur_val["signal"]:
                        changed_rules.append({
                            "rule": rule_name,
                            "from": prev_val.get("signal", "—"),
                            "to": cur_val["signal"],
                            "detail": cur_val["detail"],
                        })
                # Also check rules that disappeared
                for rule_name, prev_val in prev_snapshot.items():
                    if rule_name not in rule_signals:
                        changed_rules.append({
                            "rule": rule_name,
                            "from": prev_val.get("signal", "—"),
                            "to": "—",
                            "detail": "no longer active",
                        })

            trend_changes.append({
                "time": current.strftime("%H:%M"),
                "from": prev_overall,
                "to": overall,
                "strength": strength,
                "moon_deg": round(result.get("moon", {}).get("longitude", 0), 4),
                "moon_sign": result.get("moon", {}).get("sign", ""),
                "moon_nak": result.get("moon", {}).get("nakshatra", ""),
                "changed_rules": changed_rules,
            })

        prev_overall = overall
        prev_snapshot = rule_signals
        current += timedelta(minutes=interval_min)

    return {
        "date": date_dt.strftime("%d-%m-%Y"),
        "scan_start": f"{start_hour:02d}:{start_min:02d}",
        "scan_end": f"{end_hour:02d}:{end_min:02d}",
        "interval_minutes": interval_min,
        "total_slots": len(timeline),
        "trend_changes": trend_changes,
        "change_count": len(trend_changes),
        "timeline": timeline,
    }
