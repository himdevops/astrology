"""
ashtakavarga_advanced.py — Advanced Ashtakavarga Predictions (from Secrets of Ashtakavarga).
=============================================================================================
Implements prediction techniques from the book that are NOT in the existing codebase.
This is a SEPARATE module — does NOT modify any existing files.

Features:
  1. Gantavya Rasi (Advance Effects) — planets give next-sign effects before entering
  2. Rekha Strength % — transit effectiveness as (rekhas/8) × 100
  3. Daily SAV Score — sum BAV scores for all transiting planets on a given day
  4. Trikona Nakshatra Trouble — dangerous transit nakshatra from SAV + Saturn
  5. Bhava Destruction via Saturn — which bhava Saturn damages and when
  6. Planet-specific Life Predictions — father/mother/sibling/spouse/children from BAV
  7. Kaksha Fine Timing — exact degree ranges where planet gives results in a sign
"""
from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import Dict, Any, List, Optional

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc
from core.constants import SIGNS, NAKSHATRAS_27 as NAKSHATRAS
from core.ashtakavarga import (
    calc_full_ashtakavarga, ASHTAK_PLANETS, KAKSHA_LORDS,
    _get_sign_index, calc_kaksha,
)


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

# Gantavya Rasi: how far in advance a planet starts giving effects of NEXT sign
# (from Ch4, Sloka 7 of Secrets of Ashtakavarga)
GANTAVYA_DAYS = {
    "Saturn": 180,    # 6 months
    "Jupiter": 60,    # 2 months
    "Mars": 8,        # 8 days
    "Sun": 5,         # 5 days
    "Venus": 4,       # 4 days
    "Mercury": 3,     # 3 days
    "Moon": 1,        # 1 day (ghati-based, simplified to 1 day)
}

# Average transit duration per sign (approximate days)
TRANSIT_DURATION = {
    "Saturn": 912,    # ~2.5 years
    "Jupiter": 365,   # ~1 year
    "Mars": 45,       # ~45 days
    "Sun": 30,        # ~30 days
    "Venus": 28,      # ~28 days
    "Mercury": 25,    # ~25 days
    "Moon": 2.25,     # ~2.25 days
}

# Planet-specific life event BAV mappings (Ch6)
LIFE_PREDICTIONS = {
    "Sun": {
        "signifies": "Father, Authority, Government, Health",
        "thresholds": {
            "excellent": 6, "good": 5, "average": 4, "bad": 3, "very_bad": 2,
        },
        "results": {
            "excellent": "Father prosperous, gains from government, excellent health & authority",
            "good": "Good relations with father, moderate authority gains",
            "average": "Mixed results regarding father and career",
            "bad": "Father's health issues, problems with authority",
            "very_bad": "Serious trouble — father, legal issues, or health crisis",
        },
    },
    "Moon": {
        "signifies": "Mother, Mind, Emotions, Public",
        "thresholds": {
            "excellent": 6, "good": 5, "average": 4, "bad": 3, "very_bad": 2,
        },
        "results": {
            "excellent": "Mother happy, peaceful mind, public recognition",
            "good": "Good mental state, harmonious family",
            "average": "Fluctuating emotions, mixed public dealings",
            "bad": "Mother's health issues, mental disturbance",
            "very_bad": "Severe mental anguish, mother's suffering",
        },
    },
    "Mars": {
        "signifies": "Siblings, Courage, Property, Energy",
        "thresholds": {
            "excellent": 6, "good": 5, "average": 4, "bad": 3, "very_bad": 2,
        },
        "results": {
            "excellent": "Property gains, siblings prosper, high energy & courage",
            "good": "Good health, minor property gains",
            "average": "Mixed — some conflicts, some gains",
            "bad": "Sibling troubles, accidents, property disputes",
            "very_bad": "Serious injuries, legal property fights, sibling separation",
        },
    },
    "Mercury": {
        "signifies": "Education, Business, Communication, Intelligence",
        "thresholds": {
            "excellent": 6, "good": 5, "average": 4, "bad": 3, "very_bad": 2,
        },
        "results": {
            "excellent": "Academic success, business boom, sharp intellect",
            "good": "Good communication, learning opportunities",
            "average": "Normal business, routine education",
            "bad": "Business loss, communication breakdowns",
            "very_bad": "Failed exams, fraud, nervous disorders",
        },
    },
    "Jupiter": {
        "signifies": "Children, Wealth, Wisdom, Guru, Dharma",
        "thresholds": {
            "excellent": 6, "good": 5, "average": 4, "bad": 3, "very_bad": 2,
        },
        "results": {
            "excellent": "Children prosper, wealth increase, spiritual growth",
            "good": "Good fortune, wisdom gains, child-related happiness",
            "average": "Moderate gains, routine spiritual life",
            "bad": "Financial stress, children's issues",
            "very_bad": "Major financial loss, child health issues, guru problems",
        },
    },
    "Venus": {
        "signifies": "Spouse, Marriage, Luxury, Vehicles, Arts",
        "thresholds": {
            "excellent": 6, "good": 5, "average": 4, "bad": 3, "very_bad": 2,
        },
        "results": {
            "excellent": "Happy marriage, luxury gains, vehicle purchase, artistic success",
            "good": "Harmonious spouse relations, minor comforts",
            "average": "Normal married life, routine",
            "bad": "Marital discord, vehicle problems",
            "very_bad": "Separation risk, major luxury/vehicle loss",
        },
    },
    "Saturn": {
        "signifies": "Longevity, Karma, Service, Delays, Chronic Issues",
        "thresholds": {
            "excellent": 5, "good": 4, "average": 3, "bad": 2, "very_bad": 1,
        },
        "results": {
            "excellent": "Good longevity, karmic rewards, stable service",
            "good": "Steady progress, minor delays only",
            "average": "Normal karmic results, some delays",
            "bad": "Chronic issues surface, service problems, delays",
            "very_bad": "Severe karma, chronic disease, major delays & losses",
        },
    },
}

# SAV daily score interpretations (Ch4, Slokas 69-76)
SAV_DAILY_RESULTS = [
    (56, "Coronation-like day — supreme success in all matters"),
    (52, "Royal honors, major gains, celebrations"),
    (48, "Excellent day — wealth, happiness, all desires fulfilled"),
    (44, "Very good — financial gains, recognition, joy"),
    (40, "Good day — moderate gains, positive developments"),
    (36, "Above average — small gains, general well-being"),
    (32, "Average — mixed results, nothing exceptional"),
    (28, "Below average — minor obstacles, caution advised"),
    (24, "Difficult — losses possible, health issues"),
    (20, "Bad — serious obstacles, financial loss, quarrels"),
    (16, "Very bad — illness, major losses, danger"),
    (0,  "Terrible — extreme caution, possible calamity"),
]


# ═══════════════════════════════════════════════════════════════
# HELPER FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _get_transit_positions(jd: float, ayanamsa: str) -> Dict[str, float]:
    """Get current transit longitudes for all planets."""
    positions = get_all_planets(jd, ayanamsa)
    result = {}
    for pp in positions:
        if pp.planet in ASHTAK_PLANETS:
            result[pp.planet] = pp.longitude
    return result


def _get_nakshatra(lon: float) -> Dict[str, Any]:
    """Get nakshatra info from longitude."""
    nak_idx = int(lon / (360 / 27)) % 27
    nak_degree = lon % (360 / 27)
    return {
        "index": nak_idx,
        "name": NAKSHATRAS[nak_idx] if nak_idx < len(NAKSHATRAS) else f"Nak-{nak_idx+1}",
        "degree_in_nakshatra": round(nak_degree, 2),
    }


# ═══════════════════════════════════════════════════════════════
# 1. GANTAVYA RASI — Advance Effects
# ═══════════════════════════════════════════════════════════════

def calc_gantavya_rasi(
    transit_lons: Dict[str, float],
    all_bav: Dict[str, List[int]],
    sav: List[int],
) -> List[Dict[str, Any]]:
    """
    Calculate Gantavya Rasi effects for each planet.
    Shows if a planet is close enough to next sign to start giving advance effects.
    """
    results = []
    for planet in ASHTAK_PLANETS:
        if planet not in transit_lons:
            continue
        lon = transit_lons[planet]
        current_sign = _get_sign_index(lon)
        next_sign = (current_sign + 1) % 12
        deg_in_sign = lon % 30
        remaining_deg = 30 - deg_in_sign

        # Estimate how many days until sign change
        avg_speed = 30 / TRANSIT_DURATION[planet]  # degrees per day
        days_to_change = remaining_deg / avg_speed if avg_speed > 0 else 9999

        gantavya_days = GANTAVYA_DAYS[planet]
        is_in_gantavya = days_to_change <= gantavya_days

        # Current sign score
        current_bav = all_bav.get(planet, [0]*12)[current_sign]
        current_sav = sav[current_sign]

        # Next sign score (advance effect)
        next_bav = all_bav.get(planet, [0]*12)[next_sign]
        next_sav = sav[next_sign]

        entry = {
            "planet": planet,
            "current_sign": SIGNS[current_sign],
            "next_sign": SIGNS[next_sign],
            "degree_in_sign": round(deg_in_sign, 2),
            "days_to_sign_change": round(days_to_change, 1),
            "gantavya_window_days": gantavya_days,
            "is_in_gantavya_zone": is_in_gantavya,
            "current_sign_bav": current_bav,
            "current_sign_sav": current_sav,
            "next_sign_bav": next_bav,
            "next_sign_sav": next_sav,
        }

        if is_in_gantavya:
            # Blend: show both current and advance effects
            entry["effective_bav"] = round((current_bav + next_bav) / 2, 1)
            entry["advance_effect"] = (
                "positive" if next_bav >= 4 else
                "neutral" if next_bav >= 3 else
                "negative"
            )
            entry["note"] = (
                f"{planet} within {gantavya_days}-day Gantavya window — "
                f"already giving effects of {SIGNS[next_sign]} (BAV={next_bav})"
            )
        else:
            entry["effective_bav"] = current_bav
            entry["advance_effect"] = None
            entry["note"] = f"Not yet in Gantavya zone ({round(days_to_change,0)} days away)"

        results.append(entry)

    return results


# ═══════════════════════════════════════════════════════════════
# 2. REKHA STRENGTH % — Transit Effectiveness
# ═══════════════════════════════════════════════════════════════

def calc_rekha_strength(
    transit_lons: Dict[str, float],
    all_bav: Dict[str, List[int]],
    sav: List[int],
) -> List[Dict[str, Any]]:
    """
    Calculate effectiveness percentage for each transiting planet.
    Rekha Strength = (BAV score / 8) × 100
    SAV Strength = (SAV score / 56) × 100
    """
    results = []
    for planet in ASHTAK_PLANETS:
        if planet not in transit_lons:
            continue
        lon = transit_lons[planet]
        sign_idx = _get_sign_index(lon)

        bav_score = all_bav.get(planet, [0]*12)[sign_idx]
        sav_score = sav[sign_idx]

        bav_pct = round((bav_score / 8) * 100, 1)
        sav_pct = round((sav_score / 56) * 100, 1)

        # Kaksha fine timing
        kaksha_info = calc_kaksha(lon)

        # Overall transit quality
        if bav_pct >= 62.5 and sav_pct >= 50:  # 5/8 and 28/56
            quality = "excellent"
        elif bav_pct >= 50:  # 4/8
            quality = "good"
        elif bav_pct >= 37.5:  # 3/8
            quality = "neutral"
        else:
            quality = "weak"

        results.append({
            "planet": planet,
            "sign": SIGNS[sign_idx],
            "bav_score": bav_score,
            "bav_strength_pct": bav_pct,
            "sav_score": sav_score,
            "sav_strength_pct": sav_pct,
            "quality": quality,
            "kaksha": kaksha_info,
            "interpretation": (
                f"{planet} gives {bav_pct}% of its full transit result in {SIGNS[sign_idx]}. "
                f"Sign has {sav_pct}% overall ashtakavarga strength."
            ),
        })

    return results


# ═══════════════════════════════════════════════════════════════
# 3. DAILY SAV SCORE — Day Quality Rating
# ═══════════════════════════════════════════════════════════════

def calc_daily_sav_score(
    transit_lons: Dict[str, float],
    all_bav: Dict[str, List[int]],
    sav: List[int],
) -> Dict[str, Any]:
    """
    Calculate total SAV score for the day by summing each planet's
    BAV score in its current transit sign.
    Per Ch4 Sloka 69-76: total determines day quality (max 56).
    """
    total = 0
    breakdown = []
    for planet in ASHTAK_PLANETS:
        if planet not in transit_lons:
            continue
        sign_idx = _get_sign_index(transit_lons[planet])
        bav_score = all_bav.get(planet, [0]*12)[sign_idx]
        total += bav_score
        breakdown.append({
            "planet": planet,
            "sign": SIGNS[sign_idx],
            "bav_contribution": bav_score,
        })

    # Find matching interpretation
    interpretation = ""
    for threshold, desc in SAV_DAILY_RESULTS:
        if total >= threshold:
            interpretation = desc
            break

    # Rating
    if total >= 40:
        rating = "excellent"
    elif total >= 32:
        rating = "good"
    elif total >= 28:
        rating = "average"
    elif total >= 22:
        rating = "below_average"
    else:
        rating = "bad"

    return {
        "total_score": total,
        "max_possible": 56,
        "percentage": round((total / 56) * 100, 1),
        "rating": rating,
        "interpretation": interpretation,
        "breakdown": breakdown,
    }


# ═══════════════════════════════════════════════════════════════
# 4. TRIKONA NAKSHATRA TROUBLE
# ═══════════════════════════════════════════════════════════════

def calc_trikona_nakshatra_trouble(
    sav: List[int],
    planet_signs: Dict[str, int],
    transit_lons: Dict[str, float],
) -> Dict[str, Any]:
    """
    Trikona Nakshatra Trouble Prediction (Ch3, Sloka 23-24).
    Count rekhas (SAV) from Lagna sign to Saturn's sign.
    Multiply by 7, divide by 27. Remainder = nakshatra index
    where malefic transit causes maximum trouble.
    """
    lagna_sign = planet_signs.get("Lagna")
    saturn_sign = planet_signs.get("Saturn")

    if lagna_sign is None or saturn_sign is None:
        return {"error": "Lagna or Saturn sign not available"}

    # Count SAV from Lagna to Saturn (inclusive of both)
    total_sav = 0
    if saturn_sign >= lagna_sign:
        for i in range(lagna_sign, saturn_sign + 1):
            total_sav += sav[i]
    else:
        for i in range(lagna_sign, 12):
            total_sav += sav[i]
        for i in range(0, saturn_sign + 1):
            total_sav += sav[i]

    # Formula: (total × 7) ÷ 27 → remainder is nakshatra
    product = total_sav * 7
    trouble_nak_idx = product % 27

    trouble_nak = NAKSHATRAS[trouble_nak_idx] if trouble_nak_idx < len(NAKSHATRAS) else f"Nak-{trouble_nak_idx+1}"

    # Check if any malefic is currently in that nakshatra
    malefics = ["Saturn", "Mars", "Sun"]  # Rahu/Ketu excluded from ashtakavarga
    current_threats = []
    for m in malefics:
        if m in transit_lons:
            m_nak = int(transit_lons[m] / (360/27)) % 27
            if m_nak == trouble_nak_idx:
                current_threats.append(m)

    # Trikona nakshatras (same trouble applies to 1st, 10th, 19th from the result)
    trikona_naks = [
        trouble_nak_idx,
        (trouble_nak_idx + 9) % 27,   # 10th nakshatra
        (trouble_nak_idx + 18) % 27,  # 19th nakshatra
    ]

    trikona_names = []
    for idx in trikona_naks:
        name = NAKSHATRAS[idx] if idx < len(NAKSHATRAS) else f"Nak-{idx+1}"
        trikona_names.append({"index": idx, "name": name})

    return {
        "lagna_sign": SIGNS[lagna_sign],
        "saturn_sign": SIGNS[saturn_sign],
        "sav_sum_lagna_to_saturn": total_sav,
        "formula": f"({total_sav} × 7) ÷ 27 = {product // 27} remainder {trouble_nak_idx}",
        "trouble_nakshatra": trouble_nak,
        "trouble_nakshatra_index": trouble_nak_idx,
        "trikona_trouble_nakshatras": trikona_names,
        "current_malefic_threats": current_threats,
        "is_active_threat": len(current_threats) > 0,
        "warning": (
            f"⚠ {', '.join(current_threats)} currently transiting trouble nakshatra {trouble_nak}!"
            if current_threats else
            f"No malefic currently in trouble nakshatra ({trouble_nak})"
        ),
    }


# ═══════════════════════════════════════════════════════════════
# 5. BHAVA DESTRUCTION VIA SATURN TRANSIT
# ═══════════════════════════════════════════════════════════════

def calc_bhava_vulnerability(
    all_bav: Dict[str, List[int]],
    sav: List[int],
    planet_signs: Dict[str, int],
    pinda_data: Dict[str, Any],
    transit_lons: Dict[str, float],
) -> List[Dict[str, Any]]:
    """
    Bhava Destruction Timing (Ch7, Sloka 16).
    For each bhava (house from Lagna):
      - Find the SAV score for that sign
      - Find minimum SAV sign = most vulnerable
      - When Saturn transits the weakest sign of a bhava's ashtakavarga,
        that bhava suffers

    Also: Pinda × rekhas ÷ 27 = nakshatra where Saturn transit harms bhava
    """
    lagna_sign = planet_signs.get("Lagna", 0)
    saturn_lon = transit_lons.get("Saturn")
    saturn_sign = _get_sign_index(saturn_lon) if saturn_lon else None

    bhava_names = [
        "1st (Self/Body)", "2nd (Wealth/Speech)", "3rd (Siblings/Courage)",
        "4th (Mother/Property)", "5th (Children/Education)", "6th (Enemies/Health)",
        "7th (Spouse/Partnership)", "8th (Longevity/Hidden)", "9th (Fortune/Father)",
        "10th (Career/Karma)", "11th (Gains/Income)", "12th (Loss/Moksha)",
    ]

    results = []
    for bhava_num in range(12):
        bhava_sign = (lagna_sign + bhava_num) % 12
        bhava_sav = sav[bhava_sign]

        # Find the weakest sign in terms of SAV for vulnerability
        min_sav = min(sav)
        min_sav_signs = [i for i in range(12) if sav[i] == min_sav]

        # Is Saturn currently in this bhava?
        saturn_in_bhava = saturn_sign == bhava_sign if saturn_sign is not None else False

        # Vulnerability assessment
        if bhava_sav <= 22:
            vulnerability = "high"
        elif bhava_sav <= 25:
            vulnerability = "moderate"
        elif bhava_sav <= 28:
            vulnerability = "low"
        else:
            vulnerability = "protected"

        # Pinda-based trouble nakshatra (if pinda data available)
        trouble_nak = None
        pinda_planets = pinda_data.get("planets", {})
        # Use the planet that signifies this bhava
        bhava_significators = {
            0: "Sun", 1: "Jupiter", 2: "Mars", 3: "Moon",
            4: "Jupiter", 5: "Mars", 6: "Venus", 7: "Saturn",
            8: "Jupiter", 9: "Sun", 10: "Jupiter", 11: "Saturn",
        }
        sig_planet = bhava_significators.get(bhava_num, "Sun")
        if sig_planet in pinda_planets:
            sodhya = pinda_planets[sig_planet].get("sodhya_pinda", 0)
            if sodhya > 0 and bhava_sav > 0:
                nak_idx = (sodhya * bhava_sav) % 27
                nak_name = NAKSHATRAS[nak_idx] if nak_idx < len(NAKSHATRAS) else f"Nak-{nak_idx+1}"
                trouble_nak = {"index": nak_idx, "name": nak_name}

        results.append({
            "bhava": bhava_num + 1,
            "bhava_name": bhava_names[bhava_num],
            "sign": SIGNS[bhava_sign],
            "sav_score": bhava_sav,
            "vulnerability": vulnerability,
            "saturn_transiting": saturn_in_bhava,
            "trouble_nakshatra": trouble_nak,
            "status": (
                "⚠ ACTIVE — Saturn transiting this bhava!" if saturn_in_bhava and vulnerability in ["high", "moderate"]
                else "Saturn here but bhava protected" if saturn_in_bhava
                else f"Vulnerable (SAV={bhava_sav})" if vulnerability == "high"
                else "Normal"
            ),
        })

    return results


# ═══════════════════════════════════════════════════════════════
# 6. PLANET-SPECIFIC LIFE PREDICTIONS
# ═══════════════════════════════════════════════════════════════

def calc_life_predictions(
    transit_lons: Dict[str, float],
    all_bav: Dict[str, List[int]],
) -> List[Dict[str, Any]]:
    """
    Planet-specific life event predictions based on transit BAV score.
    Ch6: Each planet's BAV score in current transit sign predicts
    specific life areas.
    """
    results = []
    for planet in ASHTAK_PLANETS:
        if planet not in transit_lons or planet not in LIFE_PREDICTIONS:
            continue

        config = LIFE_PREDICTIONS[planet]
        sign_idx = _get_sign_index(transit_lons[planet])
        bav_score = all_bav.get(planet, [0]*12)[sign_idx]
        thresholds = config["thresholds"]

        # Determine rating
        if bav_score >= thresholds["excellent"]:
            rating = "excellent"
        elif bav_score >= thresholds["good"]:
            rating = "good"
        elif bav_score >= thresholds["average"]:
            rating = "average"
        elif bav_score >= thresholds["bad"]:
            rating = "bad"
        else:
            rating = "very_bad"

        results.append({
            "planet": planet,
            "signifies": config["signifies"],
            "transit_sign": SIGNS[sign_idx],
            "bav_score": bav_score,
            "rating": rating,
            "prediction": config["results"][rating],
            "strength_pct": round((bav_score / 8) * 100, 1),
        })

    return results


# ═══════════════════════════════════════════════════════════════
# 7. KAKSHA FINE TIMING
# ═══════════════════════════════════════════════════════════════

def calc_kaksha_fine_timing(
    transit_lons: Dict[str, float],
    all_bav: Dict[str, List[int]],
    planet_signs: Dict[str, int],
) -> List[Dict[str, Any]]:
    """
    Kaksha-level fine timing (Ch4, Sloka 4).
    When a planet transits a sign, it ONLY gives results in the specific
    3°45' kaksha where the contributing planets have given rekhas.
    Shows which degree ranges are active (benefic) vs inactive.

    Returns for each planet: the 8 kaksha zones with benefic/malefic status.
    """
    from core.ashtakavarga import BAV_RULES

    results = []
    for planet in ASHTAK_PLANETS:
        if planet not in transit_lons:
            continue

        lon = transit_lons[planet]
        sign_idx = _get_sign_index(lon)
        current_kaksha = calc_kaksha(lon)

        # Build kaksha benefic map for this planet in this sign
        rules = BAV_RULES.get(planet, {})
        kakshas = []
        for k_idx, k_lord in enumerate(KAKSHA_LORDS):
            start_deg = k_idx * 3.75
            end_deg = start_deg + 3.75

            # Check if this kaksha lord contributes a benefic point
            contrib_sign = planet_signs.get(k_lord)
            if contrib_sign is not None:
                benefic_houses = rules.get(k_lord, [])
                house_from_contrib = ((sign_idx - contrib_sign) % 12) + 1
                is_benefic = house_from_contrib in benefic_houses
            else:
                is_benefic = False

            is_current = (current_kaksha["kaksha"] == k_idx + 1)

            kakshas.append({
                "kaksha_num": k_idx + 1,
                "lord": k_lord,
                "start_deg": round(start_deg, 2),
                "end_deg": round(end_deg, 2),
                "is_benefic": is_benefic,
                "is_current": is_current,
                "status": (
                    "✓ ACTIVE — Planet here & benefic kaksha" if is_current and is_benefic
                    else "✗ Planet here but malefic kaksha" if is_current
                    else "Benefic zone" if is_benefic
                    else "Inactive zone"
                ),
            })

        # Count benefic vs malefic kakshas
        benefic_count = sum(1 for k in kakshas if k["is_benefic"])
        current_is_benefic = any(k["is_current"] and k["is_benefic"] for k in kakshas)

        results.append({
            "planet": planet,
            "sign": SIGNS[sign_idx],
            "longitude": round(lon, 2),
            "current_kaksha": current_kaksha,
            "current_kaksha_benefic": current_is_benefic,
            "benefic_kaksha_count": benefic_count,
            "malefic_kaksha_count": 8 - benefic_count,
            "kakshas": kakshas,
            "timing_note": (
                f"{planet} currently in {'BENEFIC' if current_is_benefic else 'MALEFIC'} "
                f"kaksha of {current_kaksha['kaksha_lord']} — "
                f"{'giving positive results' if current_is_benefic else 'results suppressed'}"
            ),
        })

    return results


# ═══════════════════════════════════════════════════════════════
# 8. MULTI-DAY FORECAST
# ═══════════════════════════════════════════════════════════════

def calc_multi_day_forecast(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz: float,
    ayanamsa: str,
    start_date: date,
    num_days: int = 7,
) -> List[Dict[str, Any]]:
    """
    Generate daily SAV scores for multiple days.
    Useful for finding best/worst days in a week.
    """
    set_ayanamsa(ayanamsa)
    utc_birth = local_to_utc(birth_dt, tz)
    jd_birth = datetime_to_jd(utc_birth)

    # Birth chart
    planet_positions = get_all_planets(jd_birth, ayanamsa)
    ascendant = calc_ascendant(jd_birth, lat, lon, ayanamsa)
    planet_lons = {pp.planet: pp.longitude for pp in planet_positions if pp.planet in ASHTAK_PLANETS}
    ashtak = calc_full_ashtakavarga(planet_lons, ascendant.longitude)
    all_bav = ashtak["bav"]
    sav = ashtak["sav"]

    forecast = []
    for day_offset in range(num_days):
        target_date = start_date + timedelta(days=day_offset)
        # Get transit positions at noon of target date
        noon_dt = datetime(target_date.year, target_date.month, target_date.day, 12, 0)
        noon_utc = local_to_utc(noon_dt, tz)
        jd_noon = datetime_to_jd(noon_utc)
        transit_lons = _get_transit_positions(jd_noon, ayanamsa)

        day_score = calc_daily_sav_score(transit_lons, all_bav, sav)

        forecast.append({
            "date": target_date.strftime("%d-%m-%Y"),
            "weekday": target_date.strftime("%A"),
            "score": day_score["total_score"],
            "percentage": day_score["percentage"],
            "rating": day_score["rating"],
            "interpretation": day_score["interpretation"],
        })

    return forecast


# ═══════════════════════════════════════════════════════════════
# MASTER FUNCTION — Generate All Advanced Predictions
# ═══════════════════════════════════════════════════════════════

def generate_advanced_ashtakavarga(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    transit_date: Optional[date] = None,
    forecast_days: int = 7,
) -> Dict[str, Any]:
    """
    Generate all advanced Ashtakavarga predictions.
    Uses birth chart for BAV/SAV, transit date for current predictions.
    """
    set_ayanamsa(ayanamsa)

    # Birth chart calculation
    utc_birth = local_to_utc(birth_dt, tz_offset)
    jd_birth = datetime_to_jd(utc_birth)

    planet_positions = get_all_planets(jd_birth, ayanamsa)
    ascendant = calc_ascendant(jd_birth, lat, lon, ayanamsa)

    planet_lons = {}
    for pp in planet_positions:
        if pp.planet in ASHTAK_PLANETS:
            planet_lons[pp.planet] = pp.longitude

    # Full ashtakavarga from birth chart
    ashtak = calc_full_ashtakavarga(planet_lons, ascendant.longitude)
    all_bav = ashtak["bav"]
    sav = ashtak["sav"]
    planet_signs = {}
    for p in ASHTAK_PLANETS:
        if p in planet_lons:
            planet_signs[p] = _get_sign_index(planet_lons[p])
    planet_signs["Lagna"] = _get_sign_index(ascendant.longitude)

    # Transit positions for target date
    if transit_date is None:
        transit_date = date.today()

    transit_dt = datetime(transit_date.year, transit_date.month, transit_date.day, 12, 0)
    transit_utc = local_to_utc(transit_dt, tz_offset)
    jd_transit = datetime_to_jd(transit_utc)
    transit_lons = _get_transit_positions(jd_transit, ayanamsa)

    # Pinda data from birth chart
    pinda_data = ashtak.get("pinda_shodhana", {})

    # Run all advanced calculations
    result = {
        "birth_info": {
            "date": birth_dt.strftime("%d-%m-%Y"),
            "time": birth_dt.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "tz_offset": tz_offset,
            "ayanamsa": ayanamsa,
        },
        "transit_date": transit_date.strftime("%d-%m-%Y"),
        "gantavya_rasi": calc_gantavya_rasi(transit_lons, all_bav, sav),
        "rekha_strength": calc_rekha_strength(transit_lons, all_bav, sav),
        "daily_sav_score": calc_daily_sav_score(transit_lons, all_bav, sav),
        "trikona_trouble": calc_trikona_nakshatra_trouble(sav, planet_signs, transit_lons),
        "bhava_vulnerability": calc_bhava_vulnerability(all_bav, sav, planet_signs, pinda_data, transit_lons),
        "life_predictions": calc_life_predictions(transit_lons, all_bav),
        "kaksha_fine_timing": calc_kaksha_fine_timing(transit_lons, all_bav, planet_signs),
        "weekly_forecast": calc_multi_day_forecast(
            birth_dt, lat, lon, tz_offset, ayanamsa,
            transit_date, forecast_days,
        ),
    }

    return result
