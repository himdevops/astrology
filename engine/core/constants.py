"""
constants.py — All static astrological data.
=============================================
Single source of truth for signs, nakshatras, tithis, yogas,
karanas, planet IDs, ayanamsa codes, and lordship mappings.
Import from here — never hardcode these values in modules.
"""
from __future__ import annotations

import swisseph as swe


# ─── Ayanamsa Codes ─────────────────────────────────────────

AYANAMSA_MAP = {
    "lahiri":       swe.SIDM_LAHIRI,
    "raman":        swe.SIDM_RAMAN,
    "krishnamurti": swe.SIDM_KRISHNAMURTI,
    "yukteshwar":   swe.SIDM_YUKTESHWAR,
    "tropical":     -1,
}


# ─── Swiss Ephemeris Planet IDs ──────────────────────────────

PLANET_IDS = {
    "Sun":     swe.SUN,
    "Moon":    swe.MOON,
    "Mars":    swe.MARS,
    "Mercury": swe.MERCURY,
    "Jupiter": swe.JUPITER,
    "Venus":   swe.VENUS,
    "Saturn":  swe.SATURN,
    "Rahu":    swe.TRUE_NODE,     # True Node (matches Parashara Light)
    "Ketu":    -1,               # Computed as Rahu + 180
}

PLANETS_9 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]
PLANETS_7 = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Malefic / Benefic
MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}

# Planets that can actually go retrograde (not Sun/Moon, Rahu/Ketu always retro)
RETRO_CAPABLE = ["Mercury", "Venus", "Mars", "Jupiter", "Saturn"]

# Tara Grahas (participate in Graha Yuddha)
TARA_GRAHAS = ["Mars", "Mercury", "Jupiter", "Venus", "Saturn"]

# Average daily speeds (deg/day)
PLANET_AVG_SPEED = {
    "Sun": 0.9856, "Moon": 13.1764, "Mars": 0.5240,
    "Mercury": 1.3833, "Jupiter": 0.0831, "Venus": 1.2000,
    "Saturn": 0.0335, "Rahu": -0.0530, "Ketu": -0.0530,
}


# ─── 12 Signs (Rashis) ──────────────────────────────────────

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

SIGN_ELEMENTS = {
    "Aries": "Fire", "Taurus": "Earth", "Gemini": "Air", "Cancer": "Water",
    "Leo": "Fire", "Virgo": "Earth", "Libra": "Air", "Scorpio": "Water",
    "Sagittarius": "Fire", "Capricorn": "Earth", "Aquarius": "Air", "Pisces": "Water",
}

SIGN_MODALITY = {
    "Aries": "Cardinal", "Taurus": "Fixed", "Gemini": "Mutable",
    "Cancer": "Cardinal", "Leo": "Fixed", "Virgo": "Mutable",
    "Libra": "Cardinal", "Scorpio": "Fixed", "Sagittarius": "Mutable",
    "Capricorn": "Cardinal", "Aquarius": "Fixed", "Pisces": "Mutable",
}


# ─── 27 Nakshatras ──────────────────────────────────────────

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

NAKSHATRA_SPAN = 360.0 / 27.0   # 13°20' = 13.3333°
PADA_SPAN = NAKSHATRA_SPAN / 4  # 3°20'  = 3.3333°

# Nakshatra deity mapping
NAKSHATRA_DEITY = {
    "Ashwini": "Ashwini Kumaras", "Bharani": "Yama", "Krittika": "Agni",
    "Rohini": "Brahma", "Mrigashira": "Soma", "Ardra": "Rudra",
    "Punarvasu": "Aditi", "Pushya": "Brihaspati", "Ashlesha": "Sarpa",
    "Magha": "Pitris", "Purva Phalguni": "Bhaga", "Uttara Phalguni": "Aryaman",
    "Hasta": "Savitar", "Chitra": "Tvashtar", "Swati": "Vayu",
    "Vishakha": "Indra-Agni", "Anuradha": "Mitra", "Jyeshtha": "Indra",
    "Mula": "Nirrti", "Purva Ashadha": "Apas", "Uttara Ashadha": "Vishve Devas",
    "Shravana": "Vishnu", "Dhanishtha": "Vasus", "Shatabhisha": "Varuna",
    "Purva Bhadrapada": "Aja Ekapada", "Uttara Bhadrapada": "Ahir Budhnya",
    "Revati": "Pushan",
}

# Nakshatra to Rashi mapping (starting rashi for each nakshatra)
NAKSHATRA_TO_RASHI = {
    "Ashwini": "Aries", "Bharani": "Aries", "Krittika": "Aries",
    "Rohini": "Taurus", "Mrigashira": "Taurus",
    "Ardra": "Gemini", "Punarvasu": "Gemini",
    "Pushya": "Cancer", "Ashlesha": "Cancer",
    "Magha": "Leo", "Purva Phalguni": "Leo",
    "Uttara Phalguni": "Virgo", "Hasta": "Virgo",
    "Chitra": "Libra", "Swati": "Libra",
    "Vishakha": "Scorpio", "Anuradha": "Scorpio",
    "Jyeshtha": "Scorpio", "Mula": "Sagittarius",
    "Purva Ashadha": "Sagittarius", "Uttara Ashadha": "Capricorn",
    "Shravana": "Capricorn", "Dhanishtha": "Aquarius",
    "Shatabhisha": "Aquarius", "Purva Bhadrapada": "Pisces",
    "Uttara Bhadrapada": "Pisces", "Revati": "Pisces",
}


# ─── Tithis (30) ────────────────────────────────────────────

TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Amavasya",
]

TITHI_PAKSHA = ["Shukla"] * 15 + ["Krishna"] * 15


# ─── Yogas (27) ─────────────────────────────────────────────

YOGAS = [
    "Vishkambha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shoola", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyana", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]


# ─── Karanas (11 types) ─────────────────────────────────────

KARANAS = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garaja",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Nagava", "Kimstughna",
]


# ─── Vara (weekday) ─────────────────────────────────────────

VARAS = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"]
VARA_LORDS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn"]


# ─── Combustion Orbs ─────────────────────────────────────────

COMBUSTION_ORB = {
    "Moon": 12.0, "Mars": 17.0, "Mercury": 14.0,
    "Jupiter": 11.0, "Venus": 10.0, "Saturn": 15.0,
}
COMBUSTION_ORB_RETRO = {"Mercury": 12.0, "Venus": 8.0}


# ─── Vedic Aspect Angles ────────────────────────────────────

VEDIC_ASPECTS = {
    "Sun":     [180],
    "Moon":    [180],
    "Mars":    [90, 180, 210],
    "Mercury": [180],
    "Jupiter": [120, 180, 240],
    "Venus":   [180],
    "Saturn":  [60, 180, 270],
    "Rahu":    [120, 180, 240],
    "Ketu":    [120, 180, 240],
}

ASPECT_NAMES = {
    60: "3rd aspect", 90: "4th aspect", 120: "5th aspect",
    180: "7th aspect", 210: "8th aspect", 240: "9th aspect",
    270: "10th aspect",
}

ASPECT_ORB = 12.0


# ─── Default Location ───────────────────────────────────────

DEFAULT_LOCATIONS = {
    "ujjain":    {"lat": 23.1765, "lon": 75.7885, "tz": 5.5, "name": "Ujjain"},
    "mumbai":    {"lat": 19.0760, "lon": 72.8777, "tz": 5.5, "name": "Mumbai"},
    "delhi":     {"lat": 28.6139, "lon": 77.2090, "tz": 5.5, "name": "Delhi"},
    "chennai":   {"lat": 13.0827, "lon": 80.2707, "tz": 5.5, "name": "Chennai"},
    "kolkata":   {"lat": 22.5726, "lon": 88.3639, "tz": 5.5, "name": "Kolkata"},
    "bengaluru": {"lat": 12.9716, "lon": 77.5946, "tz": 5.5, "name": "Bengaluru"},
    "jaipur":    {"lat": 26.9124, "lon": 75.7873, "tz": 5.5, "name": "Jaipur"},
    "varanasi":  {"lat": 25.3176, "lon": 82.9739, "tz": 5.5, "name": "Varanasi"},
}
