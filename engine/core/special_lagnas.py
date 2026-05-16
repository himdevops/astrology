"""
special_lagnas.py — Special Lagnas & Sensitive Points.
======================================================
Calculates all major special lagnas and sensitive points from BPHS
and Western astrology. Each function takes planet positions and
birth data → returns a longitude (0-360).

Special Lagnas (BPHS/Jaimini):
  - Hora Lagna (HL)
  - Ghati Lagna (GL)
  - Bhava Lagna (BL)
  - Sree Lagna (SL)
  - Pranapada Lagna (PP)
  - Varnada Lagna (VL)
  - Indu Lagna (IL)
  - Karakamsha Lagna (KL) — Atmakaraka's Navamsha sign
  - Swamsha — Atmakaraka's Navamsha position
  - Arudha Lagna (AL / Pada Lagna)

Sensitive Points:
  - Part of Fortune (Vedic)
  - Part of Fortune (Western)
  - Yoga Point (Sun + Moon mid-point)
  - Yogi Point & Avayogi Point
  - Bhrigu Bindu (Rahu-Moon mid-point)

Chara Karakas (Jaimini):
  - 8 Chara Karakas based on degree in sign
"""
from __future__ import annotations

from typing import Dict, List, Any, Optional

from core.constants import (
    SIGNS, SIGN_LORDS, PLANETS_9, PLANETS_7,
    NAKSHATRA_LORDS, NAKSHATRAS_27,
)
from core.utils import normalize_degree


# ═══════════════════════════════════════════════════════════════
# Chara Karakas (Jaimini system)
# ═══════════════════════════════════════════════════════════════

KARAKA_NAMES = [
    "Atmakaraka",        # AK — soul significator (highest degree)
    "Amatyakaraka",      # AmK — minister
    "Bhratrikaraka",     # BK — siblings
    "Matrikaraka",       # MK — mother
    "Putrakaraka",       # PK — children
    "Gnatikaraka",       # GK — relatives/enemies
    "Darakaraka",        # DK — spouse (lowest degree)
]

KARAKA_ABBREV = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK"]

# 8-karaka system names (Jaimini variant — optional)
KARAKA_NAMES_8 = [
    "Atmakaraka", "Amatyakaraka", "Bhratrikaraka", "Matrikaraka",
    "Putrakaraka", "Gnatikaraka", "Darakaraka", "Pitrikaraka",
]
KARAKA_ABBREV_8 = ["AK", "AmK", "BK", "MK", "PK", "GK", "DK", "PiK"]


def calc_chara_karakas(
    planet_positions: list, system: int = 7
) -> List[Dict[str, Any]]:
    """
    Calculate Jaimini Chara Karakas.

    system=7 (default, matches Parashara Light):
      Only Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn.
      Rahu and Ketu are excluded. 7 karakas assigned.

    system=8 (Jaimini variant):
      Sun through Saturn + Rahu (with reversed degree: 30 - deg).
      Ketu excluded. 8 karakas assigned, Rahu typically gets Pitrikaraka.

    Sorted by degree-in-sign descending: highest = Atmakaraka.
    Returns list of dicts: [{planet, degree_in_sign, karaka, abbrev}, ...]
    """
    karaka_data = []

    for pp in planet_positions:
        name = pp.planet if hasattr(pp, 'planet') else pp.get('planet', '')
        if name in ("Ascendant", "Ketu"):
            continue

        # In 7-karaka system, skip Rahu too
        if system == 7 and name == "Rahu":
            continue

        lon = pp.longitude if hasattr(pp, 'longitude') else pp.get('longitude', 0)
        deg_in_sign = lon % 30

        # In 8-karaka system, Rahu uses reverse degree per Jaimini
        if system == 8 and name == "Rahu":
            deg_in_sign = 30.0 - deg_in_sign

        karaka_data.append({
            "planet": name,
            "longitude": lon,
            "degree_in_sign": round(deg_in_sign, 4),
        })

    # Sort by degree_in_sign descending — highest degree = Atmakaraka
    karaka_data.sort(key=lambda x: x["degree_in_sign"], reverse=True)

    # Assign karaka names
    names = KARAKA_NAMES if system == 7 else KARAKA_NAMES_8
    abbrevs = KARAKA_ABBREV if system == 7 else KARAKA_ABBREV_8

    for i, kd in enumerate(karaka_data):
        if i < len(names):
            kd["karaka"] = names[i]
            kd["abbrev"] = abbrevs[i]
        else:
            kd["karaka"] = ""
            kd["abbrev"] = ""

    return karaka_data


def get_atmakaraka(planet_positions: list) -> Dict[str, Any]:
    """Get the Atmakaraka planet (highest degree in sign)."""
    karakas = calc_chara_karakas(planet_positions)
    return karakas[0] if karakas else {}


# ═══════════════════════════════════════════════════════════════
# Special Lagnas — BPHS
# ═══════════════════════════════════════════════════════════════

def calc_hora_lagna(jd: float, birth_jd: float, asc_lon: float,
                    sunrise_jd: float) -> float:
    """
    Hora Lagna (HL) — Wealth significator.

    Formula (BPHS Ch. 33):
    Time elapsed since sunrise in ghatis (24 min units).
    HL = Sun's longitude at birth + (time_since_sunrise_hours × 15°)
    Each hora = 2.5 ghatis = 1 hour.
    HL advances one sign per hora from Sun's position.

    Simplified: HL = Ascendant longitude + birth_time_offset
    Actually per BPHS: HL moves at ~1 sign per hour from sunrise.
    """
    # Time from sunrise in hours
    hours_from_sunrise = (birth_jd - sunrise_jd) * 24.0

    # HL advances 1 sign (30°) per 2.5 ghatis = 1 hour
    # Starting from Aries (0°) at sunrise
    hl = normalize_degree(hours_from_sunrise * 30.0)

    # Add the Sun's longitude offset for the birth date
    # Actually, standard formula: HL = (birth_time_from_midnight_in_ghatis × 30/2.5)
    # Most common: HL = Sunrise_Asc + elapsed_hours × 30
    # We use the widely-accepted formula from Sanjay Rath / BPHS:
    # HL = (elapsed hours from sunrise) × 30° (mod 360)
    # This gives the longitude from 0° Aries.

    return normalize_degree(hl)


def calc_ghati_lagna(jd: float, birth_jd: float, asc_lon: float,
                     sunrise_jd: float) -> float:
    """
    Ghati Lagna (GL) — Power and authority significator.

    Formula (BPHS Ch. 33):
    GL advances one sign per 5 ghatis (= 2 hours) from sunrise.
    GL = ghatis_elapsed × 30/5 = ghatis × 6

    1 ghati = 24 minutes, so:
    GL = (elapsed_minutes / 24) × 6 = elapsed_hours × 15°
    """
    hours_from_sunrise = (birth_jd - sunrise_jd) * 24.0
    ghatis = hours_from_sunrise * 2.5  # 1 hour = 2.5 ghatis
    gl = normalize_degree(ghatis * 6.0)
    return gl


def calc_bhava_lagna(jd: float, birth_jd: float, asc_lon: float,
                     sunrise_jd: float) -> float:
    """
    Bhava Lagna (BL) — House significator.

    BL advances one sign per 5 ghatis from sunrise.
    BL = (elapsed time from sunrise in hours) × 30° + Sun longitude
    This is sometimes equated with Lagna itself in some texts.

    Standard: BL = Lagna (same as Ascendant for equal house).
    Some traditions: BL = Sun_lon + hours_from_sunrise × 30/2
    """
    hours_from_sunrise = (birth_jd - sunrise_jd) * 24.0
    bl = normalize_degree(hours_from_sunrise * 15.0)
    return bl


def calc_sree_lagna(asc_lon: float, moon_lon: float) -> float:
    """
    Sree Lagna (SL) — Lakshmi (wealth & prosperity) significator.

    Formula (BPHS):
    If Lagna is in odd sign: SL = Lagna + (Moon_nakshatra_pada - 1) × 3°20'
    If Lagna is in even sign: SL is counted in reverse

    Simplified commonly used formula:
    SL = Lagna_lon + Moon_lon (mod 360) — known as the "add" method.

    Most accurate BPHS (Sanjay Rath):
    Determine the birth nakshatra (Moon's nakshatra).
    Count the nakshatra lord's position to get SL.

    Standard implementation: SL based on Moon-Nakshatra pada.
    """
    # Standard formula used by most software:
    # SL = Count from Moon nakshatra lord's position
    # Simplified: SL = Asc_longitude + Moon_longitude
    sl = normalize_degree(asc_lon + moon_lon)
    return sl


def calc_pranapada_lagna(sun_lon: float, birth_time_ghatis: float) -> float:
    """
    Pranapada Lagna (PP) — Vitality significator.

    Formula (BPHS Ch. 33):
    Multiply birth time ghatis (from sunrise) by 4.
    If Sun in movable sign: add result to Sun.
    If Sun in fixed sign: add result to Sun + 240°.
    If Sun in dual/mutable sign: add result to Sun + 120°.
    """
    sign_idx = int(sun_lon / 30) % 12
    modality_offset = [0, 240, 120][sign_idx % 3]  # Cardinal=0, Fixed=240, Mutable=120

    pp = normalize_degree(sun_lon + modality_offset + (birth_time_ghatis * 4))
    return pp


def calc_varnada_lagna(asc_lon: float, hora_lon: float) -> float:
    """
    Varnada Lagna (VL) — Caste/Varna significator (Jaimini).

    Formula:
    1. Count signs from Aries to Lagna sign (forward for odd, reverse for even)
    2. Count signs from Aries to Hora Lagna (forward for odd, reverse for even)
    3. Add/subtract depending on odd/even of Lagna sign
    4. Result counted from Aries or Pisces
    """
    asc_sign = int(asc_lon / 30) % 12
    hl_sign = int(hora_lon / 30) % 12

    asc_odd = (asc_sign % 2 == 0)  # Aries=0 is odd
    hl_odd = (hl_sign % 2 == 0)

    # Count from Aries (forward) for odd signs, from Pisces (backward) for even
    if asc_odd:
        asc_count = asc_sign + 1  # 1-based from Aries
    else:
        asc_count = 12 - asc_sign  # Count back from Pisces

    if hl_odd:
        hl_count = hl_sign + 1
    else:
        hl_count = 12 - hl_sign

    # If both odd or both even: add. Otherwise: subtract.
    if asc_odd == hl_odd:
        total = asc_count + hl_count
    else:
        total = abs(asc_count - hl_count)

    # Result sign: from Aries if Lagna odd, from Pisces if Lagna even
    if asc_odd:
        vl_sign = (total - 1) % 12
    else:
        vl_sign = (12 - total % 12) % 12

    return float(vl_sign * 30)


def calc_indu_lagna(moon_lon: float, ninth_lord_lon: float,
                    moon_sign_idx: int, ninth_lord_planet: str) -> float:
    """
    Indu Lagna (IL) — Financial prosperity indicator.

    Formula:
    1. Find 9th lord from Moon sign
    2. Find 9th lord from Lagna sign
    3. Assign Indu values: Sun=30, Moon=16, Mars=6, Mercury=8,
       Jupiter=10, Venus=12, Saturn=1
    4. Add both Indu values
    5. Divide by 12, take remainder
    6. Count that many signs from Moon
    """
    # This is calculated in the module layer where we have full chart context
    # Placeholder — the actual formula needs 9th house lord identification
    return moon_lon


# Indu values per BPHS
INDU_VALUES = {
    "Sun": 30, "Moon": 16, "Mars": 6, "Mercury": 8,
    "Jupiter": 10, "Venus": 12, "Saturn": 1,
    "Rahu": 0, "Ketu": 0,
}


def calc_indu_lagna_full(moon_lon: float, ninth_from_lagna_lord: str,
                         ninth_from_moon_lord: str) -> float:
    """
    Indu Lagna — full calculation with both 9th lords.

    Steps:
    1. Get Indu value for 9th lord from Lagna
    2. Get Indu value for 9th lord from Moon
    3. Sum = val1 + val2
    4. Remainder = sum % 12
    5. If remainder = 0, count 12 signs from Moon, else count remainder signs
    6. IL = Moon sign + remainder signs
    """
    val_lagna = INDU_VALUES.get(ninth_from_lagna_lord, 0)
    val_moon = INDU_VALUES.get(ninth_from_moon_lord, 0)

    total = val_lagna + val_moon
    remainder = total % 12
    if remainder == 0:
        remainder = 12

    moon_sign = int(moon_lon / 30) % 12
    il_sign = (moon_sign + remainder - 1) % 12

    return float(il_sign * 30)


# ═══════════════════════════════════════════════════════════════
# Karakamsha & Swamsha
# ═══════════════════════════════════════════════════════════════

def calc_karakamsha(atmakaraka_lon: float) -> float:
    """
    Karakamsha — Navamsha sign of the Atmakaraka.
    This is the sign where AK falls in D9.
    Returns the longitude at the start of that sign.
    """
    from core.divisional import d9_sign
    d9_idx = d9_sign(atmakaraka_lon)
    return float(d9_idx * 30)


def calc_swamsha(atmakaraka_lon: float) -> float:
    """
    Swamsha — Same as Karakamsha (Navamsha of AK).
    Used as the Lagna of the Karakamsha chart (D9 with AK as Asc).
    """
    return calc_karakamsha(atmakaraka_lon)


# ═══════════════════════════════════════════════════════════════
# Arudha Lagna (Pada Lagna)
# ═══════════════════════════════════════════════════════════════

def calc_arudha_lagna(asc_lon: float, first_lord_lon: float) -> float:
    """
    Arudha Lagna (AL) — Material/worldly perception.

    Formula:
    1. Find the lord of the Ascendant sign
    2. Count signs from Asc to that lord's sign
    3. Count the same number from the lord's sign
    4. That's the Arudha Lagna sign

    Exception: If result = Asc sign itself or 7th from it,
    move to 10th house from the Asc or lord respectively.
    """
    asc_sign = int(asc_lon / 30) % 12
    lord_sign = int(first_lord_lon / 30) % 12

    # Count from Asc to Lord (inclusive)
    count = (lord_sign - asc_sign) % 12

    # Project same count from Lord
    al_sign = (lord_sign + count) % 12

    # Exception: if AL = Asc or 7th from Asc, take 10th instead
    if al_sign == asc_sign:
        al_sign = (asc_sign + 9) % 12  # 10th from Asc
    elif al_sign == (asc_sign + 6) % 12:
        al_sign = (lord_sign + 9) % 12  # 10th from Lord

    return float(al_sign * 30)


# ═══════════════════════════════════════════════════════════════
# Sensitive Points — Vedic & Western
# ═══════════════════════════════════════════════════════════════

def calc_fortune_vedic(asc_lon: float, sun_lon: float, moon_lon: float,
                       is_day_birth: bool = True) -> float:
    """
    Part of Fortune — Vedic (Sahama / Punya Saham).

    Day birth:  Fortuna = Asc + Moon - Sun
    Night birth: Fortuna = Asc + Sun - Moon
    """
    if is_day_birth:
        return normalize_degree(asc_lon + moon_lon - sun_lon)
    else:
        return normalize_degree(asc_lon + sun_lon - moon_lon)


def calc_fortune_western(asc_lon: float, sun_lon: float, moon_lon: float,
                         is_day_birth: bool = True) -> float:
    """
    Part of Fortune — Western (same formula, some traditions always use day formula).

    Standard: Asc + Moon - Sun (always, regardless of day/night).
    Some Western: same day/night reversal as Vedic.
    """
    # Most Western software uses: Asc + Moon - Sun always
    return normalize_degree(asc_lon + moon_lon - sun_lon)


def calc_yoga_point(sun_lon: float, moon_lon: float) -> float:
    """
    Yoga Point — Sun + Moon midpoint.
    Used in various predictive techniques.
    """
    return normalize_degree((sun_lon + moon_lon) / 2.0)


def calc_yogi_point(sun_lon: float, moon_lon: float) -> float:
    """
    Yogi Point — (Sun + Moon + 93°20') mod 360.

    The nakshatra at this point is the Yogi nakshatra.
    The lord of that nakshatra is the Yogi planet (most auspicious).
    """
    return normalize_degree(sun_lon + moon_lon + 93.3333)


def calc_avayogi_point(yogi_lon: float) -> float:
    """
    Avayogi Point — 186°40' from Yogi Point.
    The 7th nakshatra from Yogi nakshatra.
    """
    return normalize_degree(yogi_lon + 186.6667)


def calc_bhrigu_bindu(rahu_lon: float, moon_lon: float) -> float:
    """
    Bhrigu Bindu (BB) — Mid-point of Rahu and Moon.

    Also called Destiny Point. Very significant for transit predictions.
    When any planet transits over BB, significant events occur.
    """
    # Mid-point calculation (shorter arc)
    diff = normalize_degree(moon_lon - rahu_lon)
    if diff > 180:
        return normalize_degree(rahu_lon + (360 - diff) / 2 + diff)
    return normalize_degree(rahu_lon + diff / 2)


def calc_gulika(sunrise_jd: float, sunset_jd: float, birth_jd: float,
                weekday: int) -> float:
    """
    Gulika (Mandi) — Son of Saturn, malefic sensitive point.

    Day duration is divided into 8 parts (one for each planet + one empty).
    Gulika is the start of Saturn's portion.

    Weekday rulers of 8 parts (starting from sunrise):
    Sunday:    Sun, Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu
    Monday:    Moon, Mars, Mercury, Jupiter, Venus, Saturn, Rahu, Sun
    etc. — Saturn's part varies by weekday.

    Saturn's segment number (0-based from sunrise):
    Sun=6, Mon=5, Tue=4, Wed=3, Thu=2, Fri=1, Sat=0
    """
    # Saturn's segment position for each weekday (0=Sunday)
    saturn_segment = [6, 5, 4, 3, 2, 1, 0]

    day_duration = sunset_jd - sunrise_jd
    segment_length = day_duration / 8.0

    seg = saturn_segment[weekday % 7]
    gulika_jd = sunrise_jd + seg * segment_length

    # The Ascendant at gulika_jd is the Gulika longitude
    # We'll compute this in the module layer with swe.houses
    # For now return the JD so the module can compute the Asc
    return gulika_jd


# ═══════════════════════════════════════════════════════════════
# Upagraha positions (sub-planets)
# ═══════════════════════════════════════════════════════════════

# Weekday-based segment assignments for upagrahas
# Each row = [Sun, Moon, Mars, Merc, Jup, Venus, Saturn, Rahu] segment (0-based)
# For day births, divide day duration into 8 parts
UPAGRAHA_SEGMENTS = {
    # planet_owner: segment_index for each weekday (Sun=0 through Sat=6)
    "Gulika":   [6, 5, 4, 3, 2, 1, 0],  # Saturn's segment
    "Mandi":    [6, 5, 4, 3, 2, 1, 0],  # Same as Gulika (some texts differ)
    "Yamaghantaka": [4, 3, 2, 1, 0, 6, 5],  # Jupiter's segment
    "Ardhaprahara": [3, 2, 1, 0, 6, 5, 4],  # Mercury's segment
}


# ═══════════════════════════════════════════════════════════════
# Master calculation — called from module layer
# ═══════════════════════════════════════════════════════════════

def calc_all_special_points(
    planet_positions: list,
    asc_lon: float,
    birth_jd: float,
    sunrise_jd: float,
    sunset_jd: float,
    weekday: int,
    lat: float = 0.0,
    lon: float = 0.0,
    karaka_system: int = 7,
) -> Dict[str, Any]:
    """
    Calculate all special lagnas and sensitive points.

    Parameters:
        planet_positions: List of PlanetPosition objects
        asc_lon: Ascendant longitude
        birth_jd: Julian Day of birth
        sunrise_jd: Julian Day of sunrise on birth date
        sunset_jd: Julian Day of sunset on birth date
        weekday: Day of week (0=Sunday, 6=Saturday)
        lat, lon: Birth place coordinates (for Gulika Asc calc)
        karaka_system: 7 (standard) or 8 (Jaimini with Rahu)

    Returns dict with all special points.
    """
    # Extract key planet longitudes
    planets = {}
    for pp in planet_positions:
        name = pp.planet if hasattr(pp, 'planet') else pp.get('planet', '')
        lng = pp.longitude if hasattr(pp, 'longitude') else pp.get('longitude', 0)
        planets[name] = lng

    sun_lon = planets.get("Sun", 0)
    moon_lon = planets.get("Moon", 0)
    rahu_lon = planets.get("Rahu", 0)

    # Day/Night birth
    is_day = sunrise_jd < birth_jd < sunset_jd

    # Birth time in ghatis from sunrise
    hours_from_sunrise = (birth_jd - sunrise_jd) * 24.0
    ghatis_from_sunrise = hours_from_sunrise * 2.5

    # ── Chara Karakas ──
    karakas = calc_chara_karakas(planet_positions, system=karaka_system)
    atmakaraka = karakas[0] if karakas else {}
    ak_lon = atmakaraka.get("longitude", 0)

    # ── Special Lagnas ──
    hora_lagna = calc_hora_lagna(birth_jd, birth_jd, asc_lon, sunrise_jd)
    ghati_lagna = calc_ghati_lagna(birth_jd, birth_jd, asc_lon, sunrise_jd)
    bhava_lagna = calc_bhava_lagna(birth_jd, birth_jd, asc_lon, sunrise_jd)
    sree_lagna = calc_sree_lagna(asc_lon, moon_lon)
    pranapada = calc_pranapada_lagna(sun_lon, ghatis_from_sunrise)
    varnada = calc_varnada_lagna(asc_lon, hora_lagna)
    karakamsha = calc_karakamsha(ak_lon)
    swamsha = calc_swamsha(ak_lon)

    # Arudha Lagna — need lord of Asc sign
    asc_sign = SIGNS[int(asc_lon / 30) % 12]
    asc_lord = SIGN_LORDS[asc_sign]
    asc_lord_lon = planets.get(asc_lord, 0)
    arudha = calc_arudha_lagna(asc_lon, asc_lord_lon)

    # Indu Lagna — need 9th lords from Lagna and Moon
    asc_sign_idx = int(asc_lon / 30) % 12
    moon_sign_idx = int(moon_lon / 30) % 12
    ninth_from_asc_sign = SIGNS[(asc_sign_idx + 8) % 12]
    ninth_from_moon_sign = SIGNS[(moon_sign_idx + 8) % 12]
    ninth_from_asc_lord = SIGN_LORDS[ninth_from_asc_sign]
    ninth_from_moon_lord = SIGN_LORDS[ninth_from_moon_sign]
    indu = calc_indu_lagna_full(moon_lon, ninth_from_asc_lord, ninth_from_moon_lord)

    # ── Sensitive Points ──
    fortune_vedic = calc_fortune_vedic(asc_lon, sun_lon, moon_lon, is_day)
    fortune_western = calc_fortune_western(asc_lon, sun_lon, moon_lon, is_day)
    yoga_point = calc_yoga_point(sun_lon, moon_lon)
    yogi_point = calc_yogi_point(sun_lon, moon_lon)
    avayogi_point = calc_avayogi_point(yogi_point)
    bhrigu_bindu = calc_bhrigu_bindu(rahu_lon, moon_lon)

    # Yogi/Avayogi nakshatra and planet
    yogi_nak_idx = int(yogi_point / (360.0 / 27)) % 27
    yogi_nakshatra = NAKSHATRAS_27[yogi_nak_idx]
    yogi_planet = NAKSHATRA_LORDS[yogi_nak_idx]

    avayogi_nak_idx = int(avayogi_point / (360.0 / 27)) % 27
    avayogi_nakshatra = NAKSHATRAS_27[avayogi_nak_idx]
    avayogi_planet = NAKSHATRA_LORDS[avayogi_nak_idx]

    # Duplicate yogi planet (Yogi Graha's replacement = avayogi's nak lord)
    # The planet that becomes the "duplicate yogi" is the lord of the
    # avayogi nakshatra — sometimes beneficial
    duplicate_yogi = NAKSHATRA_LORDS[avayogi_nak_idx]

    # ── Gulika/Mandi ──
    gulika_jd = calc_gulika(sunrise_jd, sunset_jd, birth_jd, weekday)

    return {
        "chara_karakas": karakas,
        "atmakaraka": atmakaraka,

        "special_lagnas": {
            "hora_lagna": hora_lagna,
            "ghati_lagna": ghati_lagna,
            "bhava_lagna": bhava_lagna,
            "sree_lagna": sree_lagna,
            "pranapada_lagna": pranapada,
            "varnada_lagna": varnada,
            "indu_lagna": indu,
            "karakamsha": karakamsha,
            "swamsha": swamsha,
            "arudha_lagna": arudha,
        },

        "sensitive_points": {
            "fortune_vedic": fortune_vedic,
            "fortune_western": fortune_western,
            "yoga_point": yoga_point,
            "yogi_point": yogi_point,
            "avayogi_point": avayogi_point,
            "bhrigu_bindu": bhrigu_bindu,
        },

        "yogi_avayogi": {
            "yogi_point": yogi_point,
            "yogi_nakshatra": yogi_nakshatra,
            "yogi_planet": yogi_planet,
            "avayogi_point": avayogi_point,
            "avayogi_nakshatra": avayogi_nakshatra,
            "avayogi_planet": avayogi_planet,
            "duplicate_yogi": duplicate_yogi,
        },

        "gulika_jd": gulika_jd,
        "is_day_birth": is_day,
        "ghatis_from_sunrise": round(ghatis_from_sunrise, 4),
    }
