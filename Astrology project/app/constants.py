"""
constants.py — Shared Constants for Financial Astrology Engine v3.0
Single source of truth for all astrological data used across modules.
"""
from __future__ import annotations

# ─────────────────────────────────────────────────────────────
# 12 Rashis (Signs)
# ─────────────────────────────────────────────────────────────
SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_IDX = {s: i for i, s in enumerate(SIGNS)}

# Sign lords (Parashara)
SIGN_LORDS = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# ─────────────────────────────────────────────────────────────
# Planetary Dignity
# ─────────────────────────────────────────────────────────────
EXALTATION = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Gemini", "Ketu": "Sagittarius",
}
EXALTATION_DEGREE = {
    "Sun": 10, "Moon": 3, "Mars": 28, "Mercury": 15,
    "Jupiter": 5, "Venus": 27, "Saturn": 20, "Rahu": 20, "Ketu": 20,
}
DEBILITATION = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Sagittarius", "Ketu": "Gemini",
}
OWN_SIGNS = {
    "Sun": ["Leo"], "Moon": ["Cancer"], "Mars": ["Aries", "Scorpio"],
    "Mercury": ["Gemini", "Virgo"], "Jupiter": ["Sagittarius", "Pisces"],
    "Venus": ["Taurus", "Libra"], "Saturn": ["Capricorn", "Aquarius"],
    "Rahu": [], "Ketu": [],
}
MOOLATRIKONA = {
    "Sun": ("Leo", 0, 20), "Moon": ("Taurus", 4, 20),
    "Mars": ("Aries", 0, 12), "Mercury": ("Virgo", 16, 20),
    "Jupiter": ("Sagittarius", 0, 10), "Venus": ("Libra", 0, 15),
    "Saturn": ("Aquarius", 0, 20),
}

# ─────────────────────────────────────────────────────────────
# Natural Friendship Table (Parashara — Naisargika Maitri)
# ─────────────────────────────────────────────────────────────
NATURAL_FRIENDS = {
    "Sun":     {"friends": ["Moon", "Mars", "Jupiter"], "enemies": ["Venus", "Saturn"], "neutral": ["Mercury"]},
    "Moon":    {"friends": ["Sun", "Mercury"], "enemies": [], "neutral": ["Mars", "Jupiter", "Venus", "Saturn"]},
    "Mars":    {"friends": ["Sun", "Moon", "Jupiter"], "enemies": ["Mercury"], "neutral": ["Venus", "Saturn"]},
    "Mercury": {"friends": ["Sun", "Venus"], "enemies": ["Moon"], "neutral": ["Mars", "Jupiter", "Saturn"]},
    "Jupiter": {"friends": ["Sun", "Moon", "Mars"], "enemies": ["Mercury", "Venus"], "neutral": ["Saturn"]},
    "Venus":   {"friends": ["Mercury", "Saturn"], "enemies": ["Sun", "Moon"], "neutral": ["Mars", "Jupiter"]},
    "Saturn":  {"friends": ["Mercury", "Venus"], "enemies": ["Sun", "Moon", "Mars"], "neutral": ["Jupiter"]},
}

# ─────────────────────────────────────────────────────────────
# Directional Strength (Dig Bala) — Strongest house for each planet
# ─────────────────────────────────────────────────────────────
DIG_BALA_HOUSE = {
    "Sun": 10, "Mars": 10, "Jupiter": 1, "Mercury": 1,
    "Moon": 4, "Venus": 4, "Saturn": 7,
}

# ─────────────────────────────────────────────────────────────
# Classification
# ─────────────────────────────────────────────────────────────
NATURAL_BENEFICS = {"Jupiter", "Venus", "Mercury", "Moon"}
NATURAL_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

# Planetary karakas (financial)
FINANCIAL_KARAKAS = {
    "Jupiter": "Banking, Finance, Gold, Education",
    "Venus":   "FMCG, Luxury, Auto, Entertainment, Real Estate",
    "Saturn":  "Oil & Gas, Mining, Infrastructure, Utilities",
    "Mars":    "Defense, Steel, Energy, Real Estate",
    "Mercury": "IT, Telecom, Media, Trading, Logistics",
    "Moon":    "FMCG, Consumer Goods, Silver, Hospitality",
    "Sun":     "PSU, Power, Government, Gold",
    "Rahu":    "Tech, Chemicals, Aviation, Crypto",
    "Ketu":    "Pharma, Chemicals, Spiritual sectors",
}

# ─────────────────────────────────────────────────────────────
# Nakshatras
# ─────────────────────────────────────────────────────────────
NAKSHATRA_SPAN_DEG = 360.0 / 27  # 13.3333°
PADA_SPAN_DEG = NAKSHATRA_SPAN_DEG / 4  # 3.3333°

NAKSHATRA_LORD_ORDER = [
    "Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"
]
DASHA_YEARS = {
    "Ketu": 7, "Venus": 20, "Sun": 6, "Moon": 10, "Mars": 7,
    "Rahu": 18, "Jupiter": 16, "Saturn": 19, "Mercury": 17,
}
TOTAL_DASHA_YEARS = 120

# ─────────────────────────────────────────────────────────────
# Tithi / Panchang Constants
# ─────────────────────────────────────────────────────────────
TITHIS = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima/Amavasya",
]
YOGA_NAMES = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]
KARANA_NAMES = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija",
    "Vanija", "Vishti", "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]
VARA_NAMES = [
    "Sunday", "Monday", "Tuesday", "Wednesday",
    "Thursday", "Friday", "Saturday",
]
VARA_LORDS = {
    "Sunday": "Sun", "Monday": "Moon", "Tuesday": "Mars",
    "Wednesday": "Mercury", "Thursday": "Jupiter",
    "Friday": "Venus", "Saturday": "Saturn",
}

# ─────────────────────────────────────────────────────────────
# NSE/BSE Sector Mapping
# ─────────────────────────────────────────────────────────────
NSE_SECTORS = {
    "Banking":         "NIFTY BANK",
    "IT":              "NIFTY IT",
    "Pharma":          "NIFTY PHARMA",
    "FMCG":            "NIFTY FMCG",
    "Auto":            "NIFTY AUTO",
    "Real Estate":     "NIFTY REALTY",
    "Energy":          "NIFTY ENERGY",
    "Metal":           "NIFTY METAL",
    "Infrastructure":  "NIFTY INFRA",
    "PSU Bank":        "NIFTY PSU BANK",
    "Media":           "NIFTY MEDIA",
    "Private Bank":    "NIFTY PVT BANK",
    "MidCap":          "NIFTY MIDCAP 50",
    "SmallCap":        "NIFTY SMALLCAP 50",
}
