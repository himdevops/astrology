"""
bhrigu.py — Bhrigu Samhita Predictions Module.
================================================
Generates life predictions based on Bhrigu Samhita rules.
Given a birth chart (ascendant + planet positions), looks up
classical predictions for each planet's house placement.

Also supports transit predictions by checking current planet
positions against the birth ascendant.

COMPLETELY SEPARATE from existing core modules — only imports
from core/ for ephemeris calculations.
"""
from __future__ import annotations

import os
import json
from datetime import datetime, date
from typing import Dict, Any, List, Optional

from core.ephemeris import get_all_planets, calc_ascendant, set_ayanamsa
from core.utils import datetime_to_jd, local_to_utc
from core.constants import SIGNS

# ═══════════════════════════════════════════════════════════════
# LOAD PREDICTIONS DATA
# ═══════════════════════════════════════════════════════════════

_DATA_PATH = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data", "bhrigu_predictions.json")

_PREDICTIONS = {}

def _load_predictions():
    """Load Bhrigu predictions from JSON file."""
    global _PREDICTIONS
    if _PREDICTIONS:
        return
    try:
        with open(_DATA_PATH, 'r', encoding='utf-8') as f:
            _PREDICTIONS = json.load(f)
    except Exception as e:
        print(f"Warning: Could not load Bhrigu predictions: {e}")
        _PREDICTIONS = {}

_load_predictions()


# ═══════════════════════════════════════════════════════════════
# CONSTANTS
# ═══════════════════════════════════════════════════════════════

PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

HOUSE_NAMES = [
    "1st (Ascendant/Self)", "2nd (Wealth/Family)", "3rd (Siblings/Courage)",
    "4th (Mother/Property)", "5th (Children/Education)", "6th (Enemies/Health)",
    "7th (Spouse/Partnership)", "8th (Longevity/Secrets)", "9th (Fortune/Dharma)",
    "10th (Career/Karma)", "11th (Gains/Income)", "12th (Loss/Moksha)",
]

PLANET_NATURE = {
    "Sun": "benefic",    # Natural malefic but karaka
    "Moon": "benefic",
    "Mars": "malefic",
    "Mercury": "neutral",
    "Jupiter": "benefic",
    "Venus": "benefic",
    "Saturn": "malefic",
    "Rahu": "malefic",
    "Ketu": "malefic",
}

PLANET_SIGNIFICATIONS = {
    "Sun": "Soul, Father, Authority, Government, Health, Fame, Willpower",
    "Moon": "Mind, Mother, Emotions, Public, Comfort, Liquids, Travel",
    "Mars": "Energy, Siblings, Courage, Property, Blood, Surgery, Competition",
    "Mercury": "Intelligence, Speech, Education, Business, Communication, Skin",
    "Jupiter": "Wisdom, Children, Wealth, Guru, Dharma, Fortune, Expansion",
    "Venus": "Spouse, Marriage, Luxury, Arts, Vehicles, Beauty, Pleasure",
    "Saturn": "Karma, Longevity, Discipline, Service, Delays, Chronic Issues",
    "Rahu": "Obsession, Foreign, Illusion, Technology, Unconventional, Sudden",
    "Ketu": "Spirituality, Detachment, Past Life, Liberation, Occult, Loss",
}


# ═══════════════════════════════════════════════════════════════
# CORE FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def get_house_from_longitude(planet_lon: float, asc_lon: float) -> int:
    """
    Calculate which house (1-12) a planet occupies based on ascendant.
    Uses whole-sign house system (traditional Vedic).
    """
    asc_sign = int(asc_lon / 30) % 12
    planet_sign = int(planet_lon / 30) % 12
    house = ((planet_sign - asc_sign) % 12) + 1
    return house


def get_bhrigu_prediction(ascendant_sign: str, planet: str, house: int) -> Optional[str]:
    """
    Look up the Bhrigu Samhita prediction for a planet in a house
    for a given ascendant.
    """
    if not _PREDICTIONS:
        _load_predictions()

    asc_data = _PREDICTIONS.get(ascendant_sign, {})
    planet_data = asc_data.get(planet, {})
    prediction = planet_data.get(str(house))
    return prediction


def generate_bhrigu_reading(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
) -> Dict[str, Any]:
    """
    Generate complete Bhrigu Samhita reading for a birth chart.
    Returns predictions for all 9 planets based on their house positions.
    """
    set_ayanamsa(ayanamsa)
    utc_dt = local_to_utc(birth_dt, tz_offset)
    jd = datetime_to_jd(utc_dt)

    # Get planet positions
    planets = get_all_planets(jd, ayanamsa)
    ascendant = calc_ascendant(jd, lat, lon, ayanamsa)

    asc_lon = ascendant.longitude
    asc_sign_idx = int(asc_lon / 30) % 12
    asc_sign = SIGNS[asc_sign_idx]

    # Build planet house placements
    planet_placements = []
    for pp in planets:
        if pp.planet in PLANETS_9:
            house = get_house_from_longitude(pp.longitude, asc_lon)
            sign_idx = int(pp.longitude / 30) % 12
            sign = SIGNS[sign_idx]

            # Get Bhrigu prediction
            prediction = get_bhrigu_prediction(asc_sign, pp.planet, house)

            planet_placements.append({
                "planet": pp.planet,
                "longitude": round(pp.longitude, 2),
                "sign": sign,
                "house": house,
                "house_name": HOUSE_NAMES[house - 1],
                "nature": PLANET_NATURE.get(pp.planet, "neutral"),
                "signification": PLANET_SIGNIFICATIONS.get(pp.planet, ""),
                "prediction": prediction or f"(Prediction not available for {pp.planet} in House {house} for {asc_sign} Ascendant)",
                "has_prediction": prediction is not None,
            })

    # Sort by house number
    planet_placements.sort(key=lambda x: x["house"])

    # Overall summary
    benefics_in_kendra = sum(
        1 for p in planet_placements
        if p["nature"] == "benefic" and p["house"] in [1, 4, 7, 10]
    )
    malefics_in_dusthana = sum(
        1 for p in planet_placements
        if p["nature"] == "malefic" and p["house"] in [3, 6, 11]
    )

    # Key life areas summary
    life_areas = {}
    area_mapping = {
        1: "personality", 2: "wealth", 3: "courage",
        4: "happiness", 5: "children", 6: "health",
        7: "marriage", 8: "longevity", 9: "fortune",
        10: "career", 11: "gains", 12: "spirituality",
    }
    for p in planet_placements:
        area = area_mapping.get(p["house"], "general")
        if area not in life_areas:
            life_areas[area] = []
        life_areas[area].append(p["planet"])

    return {
        "birth_info": {
            "date": birth_dt.strftime("%d-%m-%Y"),
            "time": birth_dt.strftime("%H:%M"),
            "latitude": lat,
            "longitude": lon,
            "tz_offset": tz_offset,
            "ayanamsa": ayanamsa,
        },
        "ascendant": {
            "sign": asc_sign,
            "longitude": round(asc_lon, 2),
            "sign_index": asc_sign_idx,
        },
        "planet_predictions": planet_placements,
        "summary": {
            "benefics_in_kendra": benefics_in_kendra,
            "malefics_in_dusthana": malefics_in_dusthana,
            "chart_strength": (
                "Strong" if benefics_in_kendra >= 2 else
                "Moderate" if benefics_in_kendra >= 1 else
                "Challenging"
            ),
            "life_areas": life_areas,
        },
        "predictions_available": sum(1 for p in planet_placements if p["has_prediction"]),
        "predictions_total": len(planet_placements),
    }


def generate_bhrigu_transit(
    birth_dt: datetime,
    lat: float,
    lon: float,
    tz_offset: float = 5.5,
    ayanamsa: str = "lahiri",
    transit_date: Optional[date] = None,
) -> Dict[str, Any]:
    """
    Generate Bhrigu transit predictions.
    Uses birth ascendant + current planet positions to give transit reading.
    """
    set_ayanamsa(ayanamsa)

    # Get birth ascendant
    utc_birth = local_to_utc(birth_dt, tz_offset)
    jd_birth = datetime_to_jd(utc_birth)
    ascendant = calc_ascendant(jd_birth, lat, lon, ayanamsa)
    asc_lon = ascendant.longitude
    asc_sign_idx = int(asc_lon / 30) % 12
    asc_sign = SIGNS[asc_sign_idx]

    # Get transit positions
    if transit_date is None:
        transit_date = date.today()

    transit_dt = datetime(transit_date.year, transit_date.month, transit_date.day, 12, 0)
    utc_transit = local_to_utc(transit_dt, tz_offset)
    jd_transit = datetime_to_jd(utc_transit)

    transit_planets = get_all_planets(jd_transit, ayanamsa)

    transit_predictions = []
    for pp in transit_planets:
        if pp.planet in PLANETS_9:
            house = get_house_from_longitude(pp.longitude, asc_lon)
            sign_idx = int(pp.longitude / 30) % 12
            sign = SIGNS[sign_idx]

            prediction = get_bhrigu_prediction(asc_sign, pp.planet, house)

            transit_predictions.append({
                "planet": pp.planet,
                "longitude": round(pp.longitude, 2),
                "sign": sign,
                "transit_house": house,
                "house_name": HOUSE_NAMES[house - 1],
                "nature": PLANET_NATURE.get(pp.planet, "neutral"),
                "prediction": prediction or f"(Transit prediction not available for {pp.planet} in House {house} for {asc_sign} Ascendant)",
                "has_prediction": prediction is not None,
            })

    transit_predictions.sort(key=lambda x: x["transit_house"])

    return {
        "ascendant": asc_sign,
        "transit_date": transit_date.strftime("%d-%m-%Y"),
        "transit_predictions": transit_predictions,
    }
