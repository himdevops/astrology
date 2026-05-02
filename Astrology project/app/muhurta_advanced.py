"""
muhurta_advanced.py — Advanced Muhurta (Electional Astrology) Engine
Based on "Muhurta Martanda" by Narayana Daivajna (Krishnadas Sanskrit Series)

Implements comprehensive muhurta analysis covering all chapters:
  Ch 1-2: Panchanga Shuddhi (5-element purity)
  Ch 3:   Nakshatra classification & activity mapping
  Ch 4:   Tithi-Vara-Nakshatra Doshas (Dagdha, Mrityu, etc.)
  Ch 5:   Tara Bala (9 Taras from birth nakshatra)
  Ch 6:   Chandra Bala (Moon strength from natal Moon)
  Ch 7:   Graha Bala for Muhurta
  Ch 8:   Lagna Shuddhi (Ascendant fitness)
  Ch 9:   Hora (Planetary hours)
  Ch 10+: Activity-specific Muhurta rules (25+ activities)

All calculations use sidereal positions via Swiss Ephemeris.
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from app.constants import SIGNS, NAKSHATRA_SPAN_DEG


# ═══════════════════════════════════════════════════════════════
# MASTER DATA TABLES — from Muhurta Martanda
# ═══════════════════════════════════════════════════════════════

NAKSHATRA_NAMES_27 = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira",
    "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha",
    "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati",
    "Vishakha", "Anuradha", "Jyeshtha", "Mula", "Purva Ashadha",
    "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati",
]

NAKSHATRA_LORDS_27 = [
    "Ketu", "Venus", "Sun", "Moon", "Mars",
    "Rahu", "Jupiter", "Saturn", "Mercury", "Ketu",
    "Venus", "Sun", "Moon", "Mars", "Rahu",
    "Jupiter", "Saturn", "Mercury", "Ketu", "Venus",
    "Sun", "Moon", "Mars", "Rahu", "Jupiter",
    "Saturn", "Mercury",
]

# ── 9 Tara (Star) Names ──
TARA_NAMES = [
    "Janma",     # 1 — Birth star (inauspicious)
    "Sampat",    # 2 — Wealth (auspicious)
    "Vipat",     # 3 — Danger (inauspicious)
    "Kshema",    # 4 — Prosperity (auspicious)
    "Pratyari",  # 5 — Obstacle (inauspicious)
    "Sadhaka",   # 6 — Achievement (auspicious)
    "Vadha",     # 7 — Death (inauspicious)
    "Mitra",     # 8 — Friend (auspicious)
    "Atimitra",  # 9 — Great Friend (very auspicious)
]

TARA_NATURE = {
    "Janma":    {"nature": "Inauspicious", "score": -0.7, "advice": "Avoid all new beginnings"},
    "Sampat":   {"nature": "Auspicious",   "score": 0.8,  "advice": "Excellent for wealth & gains"},
    "Vipat":    {"nature": "Inauspicious", "score": -0.6, "advice": "Danger — avoid risky actions"},
    "Kshema":   {"nature": "Auspicious",   "score": 0.7,  "advice": "Safety & prosperity — proceed"},
    "Pratyari": {"nature": "Inauspicious", "score": -0.5, "advice": "Obstacles likely — postpone"},
    "Sadhaka":  {"nature": "Auspicious",   "score": 0.6,  "advice": "Achievement energy — good for goals"},
    "Vadha":    {"nature": "Inauspicious", "score": -0.8, "advice": "Destructive — strictly avoid"},
    "Mitra":    {"nature": "Auspicious",   "score": 0.7,  "advice": "Friendly — good for partnerships"},
    "Atimitra": {"nature": "Very Auspicious", "score": 0.9, "advice": "Best tara — highly favorable"},
}

# ── Nakshatra Classification (Muhurta Martanda Ch 3) ──
# Each nakshatra classified by nature for activity selection
NAKSHATRA_CLASSIFICATION = {
    # Fixed (Dhruva/Sthira) — good for permanent things
    "Rohini":             "Dhruva",
    "Uttara Phalguni":    "Dhruva",
    "Uttara Ashadha":     "Dhruva",
    "Uttara Bhadrapada":  "Dhruva",
    # Movable (Chara) — good for travel, vehicles
    "Punarvasu":          "Chara",
    "Swati":              "Chara",
    "Shravana":           "Chara",
    "Dhanishtha":         "Chara",
    "Shatabhisha":        "Chara",
    # Sharp/Dreadful (Tikshna/Daruna) — good for tantra, surgery, breaking
    "Mula":               "Tikshna",
    "Jyeshtha":           "Tikshna",
    "Ardra":              "Tikshna",
    "Ashlesha":           "Tikshna",
    # Soft/Gentle (Mridu) — good for arts, romance, festivities
    "Mrigashira":         "Mridu",
    "Chitra":             "Mridu",
    "Anuradha":           "Mridu",
    "Revati":             "Mridu",
    # Mixed (Mishra/Sadharana) — good for routine activities
    "Vishakha":           "Mishra",
    "Krittika":           "Mishra",
    # Light/Swift (Kshipra/Laghu) — good for quick tasks, learning
    "Ashwini":            "Kshipra",
    "Pushya":             "Kshipra",
    "Hasta":              "Kshipra",
    # Fierce/Cruel (Ugra/Krura) — good for demolition, war
    "Bharani":            "Ugra",
    "Magha":              "Ugra",
    "Purva Phalguni":     "Ugra",
    "Purva Ashadha":      "Ugra",
    "Purva Bhadrapada":   "Ugra",
}

NAKSHATRA_CLASS_HINDI = {
    "Dhruva": "ध्रुव (स्थिर)",
    "Chara": "चर",
    "Tikshna": "तीक्ष्ण (दारुण)",
    "Mridu": "मृदु",
    "Mishra": "मिश्र (साधारण)",
    "Kshipra": "क्षिप्र (लघु)",
    "Ugra": "उग्र (क्रूर)",
}

# ── 27 Yogas ──
YOGA_NAMES_27 = [
    "Vishkumbha", "Priti", "Ayushman", "Saubhagya", "Shobhana",
    "Atiganda", "Sukarma", "Dhriti", "Shula", "Ganda",
    "Vriddhi", "Dhruva", "Vyaghata", "Harshana", "Vajra",
    "Siddhi", "Vyatipata", "Variyan", "Parigha", "Shiva",
    "Siddha", "Sadhya", "Shubha", "Shukla", "Brahma",
    "Indra", "Vaidhriti",
]

YOGA_QUALITY = {
    "Vishkumbha": "Inauspicious", "Priti": "Auspicious", "Ayushman": "Auspicious",
    "Saubhagya": "Very Auspicious", "Shobhana": "Auspicious",
    "Atiganda": "Inauspicious", "Sukarma": "Auspicious", "Dhriti": "Auspicious",
    "Shula": "Inauspicious", "Ganda": "Very Inauspicious",
    "Vriddhi": "Very Auspicious", "Dhruva": "Auspicious",
    "Vyaghata": "Inauspicious", "Harshana": "Auspicious", "Vajra": "Inauspicious",
    "Siddhi": "Very Auspicious", "Vyatipata": "Very Inauspicious",
    "Variyan": "Auspicious", "Parigha": "Inauspicious", "Shiva": "Auspicious",
    "Siddha": "Very Auspicious", "Sadhya": "Auspicious", "Shubha": "Very Auspicious",
    "Shukla": "Auspicious", "Brahma": "Auspicious", "Indra": "Auspicious",
    "Vaidhriti": "Very Inauspicious",
}

# ── 11 Karanas ──
KARANA_NAMES_11 = [
    "Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti",
    "Shakuni", "Chatushpada", "Naga", "Kimstughna",
]

KARANA_QUALITY = {
    "Bava": "Auspicious", "Balava": "Auspicious", "Kaulava": "Auspicious",
    "Taitila": "Auspicious", "Garija": "Auspicious", "Vanija": "Auspicious",
    "Vishti": "Very Inauspicious",  # Bhadra karana
    "Shakuni": "Inauspicious", "Chatushpada": "Inauspicious",
    "Naga": "Inauspicious", "Kimstughna": "Neutral",
}

# ── 15 Tithis ──
TITHI_NAMES_15 = [
    "Pratipada", "Dwitiya", "Tritiya", "Chaturthi", "Panchami",
    "Shashthi", "Saptami", "Ashtami", "Navami", "Dashami",
    "Ekadashi", "Dwadashi", "Trayodashi", "Chaturdashi", "Purnima",
]

# Tithi nature groups per Muhurta Martanda
TITHI_NATURE = {
    "Nanda":  [1, 6, 11],     # Pratipada, Shashthi, Ekadashi
    "Bhadra": [2, 7, 12],     # Dwitiya, Saptami, Dwadashi
    "Jaya":   [3, 8, 13],     # Tritiya, Ashtami, Trayodashi
    "Rikta":  [4, 9, 14],     # Chaturthi, Navami, Chaturdashi
    "Purna":  [5, 10, 15],    # Panchami, Dashami, Purnima/Amavasya
}

# ── Dagdha (Burnt) Tithi-Vara combinations (Muhurta Martanda) ──
# These tithi-weekday combos are inauspicious
DAGDHA_TITHI = {
    # (tithi_in_paksha 1-15, weekday 0=Mon..6=Sun)
    # Sunday + Dwadashi
    (12, 6): "Dagdha",
    # Monday + Ekadashi
    (11, 0): "Dagdha",
    # Tuesday + Panchami
    (5, 1): "Dagdha",
    # Wednesday + Tritiya
    (3, 2): "Dagdha",
    # Thursday + Shashthi
    (6, 3): "Dagdha",
    # Friday + Ashtami
    (8, 4): "Dagdha",
    # Saturday + Navami
    (9, 5): "Dagdha",
}

# ── Mrityu Yoga (Death combination) — Nakshatra + Weekday ──
# Per Muhurta Martanda: certain nak-vara combos cause mrityu yoga
MRITYU_YOGA = {
    # (nakshatra_idx 0-26, weekday 0=Mon..6=Sun)
    (6, 6):  True,   # Punarvasu + Sunday
    (2, 0):  True,   # Krittika + Monday
    (11, 1): True,   # Uttara Phalguni + Tuesday
    (17, 2): True,   # Jyeshtha + Wednesday
    (20, 3): True,   # Uttara Ashadha + Thursday
    (24, 4): True,   # Purva Bhadrapada + Friday
    (26, 5): True,   # Revati + Saturday
}

# ── Panchaka — 5 inauspicious nakshatras (last 5: Dhanishtha to Revati half) ──
PANCHAKA_NAKSHATRAS = [22, 23, 24, 25, 26]  # Dhanishtha, Shatabhisha, P.Bhadra, U.Bhadra, Revati

# ── Vishti (Bhadra) Karana timing ──
# Vishti falls every 7th karana — inauspicious for all work

# ── Chandra Bala — Moon's transit houses from natal Moon ──
CHANDRA_BALA = {
    1:  {"name": "Janma",    "score": -0.4, "nature": "Weak",     "advice": "Avoid — Moon in birth sign"},
    2:  {"name": "Dhana",    "score": -0.2, "nature": "Moderate",  "advice": "Financial loss possible"},
    3:  {"name": "Sahaja",   "score": 0.7,  "nature": "Good",     "advice": "Courage & gains — proceed"},
    4:  {"name": "Sukha",    "score": -0.3, "nature": "Weak",     "advice": "Domestic issues — postpone"},
    5:  {"name": "Putra",    "score": -0.1, "nature": "Neutral",  "advice": "Mixed — caution advised"},
    6:  {"name": "Shatru",   "score": 0.8,  "nature": "Excellent","advice": "Victory over enemies — excellent"},
    7:  {"name": "Kalatra",  "score": 0.6,  "nature": "Good",     "advice": "Partnership gains — proceed"},
    8:  {"name": "Mrityu",   "score": -0.7, "nature": "Very Weak","advice": "Danger & obstacles — strictly avoid"},
    9:  {"name": "Dharma",   "score": 0.5,  "nature": "Good",     "advice": "Auspicious — dharmic actions"},
    10: {"name": "Karma",    "score": 0.7,  "nature": "Good",     "advice": "Professional success — proceed"},
    11: {"name": "Labha",    "score": 0.9,  "nature": "Excellent","advice": "Maximum gains — highly favorable"},
    12: {"name": "Vyaya",    "score": -0.5, "nature": "Weak",     "advice": "Expenditure & loss — avoid"},
}

# ── Hora (Planetary Hours) lords ──
# Starting from Sunday sunrise, each hour ruled by planets in Chaldean order
HORA_ORDER = ["Sun", "Venus", "Mercury", "Moon", "Saturn", "Jupiter", "Mars"]
HORA_DAY_START = {
    6: 0,  # Sunday → Sun
    0: 3,  # Monday → Moon
    1: 6,  # Tuesday → Mars
    2: 2,  # Wednesday → Mercury
    3: 5,  # Thursday → Jupiter
    4: 1,  # Friday → Venus
    5: 4,  # Saturday → Saturn
}

HORA_QUALITY = {
    "Sun":     {"nature": "Authority",  "score": 0.5, "good_for": "Government, authority, father's work, gold"},
    "Moon":    {"nature": "Mind",       "score": 0.4, "good_for": "Public, women, liquids, travel, silver"},
    "Mars":    {"nature": "Energy",     "score": 0.3, "good_for": "Surgery, fire, land, military, competition"},
    "Mercury": {"nature": "Commerce",   "score": 0.7, "good_for": "Trade, learning, writing, communication"},
    "Jupiter": {"nature": "Wisdom",     "score": 0.9, "good_for": "Marriage, education, wealth, auspicious acts"},
    "Venus":   {"nature": "Luxury",     "score": 0.6, "good_for": "Art, romance, vehicles, entertainment"},
    "Saturn":  {"nature": "Discipline", "score": -0.3, "good_for": "Iron, oil, labor, agriculture, delays"},
}

# ═══════════════════════════════════════════════════════════════
# ACTIVITY-SPECIFIC MUHURTA RULES (Muhurta Martanda Ch 10-35+)
# ═══════════════════════════════════════════════════════════════

MUHURTA_ACTIVITIES = {
    "vivaha": {
        "name": "Vivaha (Marriage)",
        "name_hi": "विवाह",
        "good_nakshatras": ["Rohini", "Mrigashira", "Magha", "Uttara Phalguni", "Hasta",
                            "Swati", "Anuradha", "Mula", "Uttara Ashadha", "Shravana",
                            "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],  # Mon, Wed, Thu, Fri
        "avoid_varas": [1, 5, 6],    # Tue, Sat, Sun
        "good_lagnas": ["Taurus", "Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "avoid_months": ["Chaitra"],
        "good_nak_class": ["Dhruva", "Mridu", "Kshipra"],
        "notes": "Muhurta Martanda Ch.10: Lagna not 6,8,12 from bride/groom Moon. Avoid Vishti karana. Shukla Paksha preferred. Jupiter/Venus not combust."
    },
    "griha_pravesh": {
        "name": "Griha Pravesh (House Entry)",
        "name_hi": "गृह प्रवेश",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha",
                            "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 15],
        "good_varas": [0, 2, 3, 4],  # Mon, Wed, Thu, Fri
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Leo", "Virgo", "Libra", "Sagittarius", "Aquarius", "Pisces"],
        "good_nak_class": ["Dhruva", "Kshipra", "Chara"],
        "notes": "Muhurta Martanda: Jupiter & Venus not combust. Shukla Paksha preferred. 4th & 8th houses unafflicted. Avoid Rikta tithis, Vishti karana. Uttarayan preferred."
    },
    "yatra": {
        "name": "Yatra (Travel/Journey)",
        "name_hi": "यात्रा",
        "good_nakshatras": ["Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                            "Chitra", "Swati", "Anuradha", "Shravana",
                            "Dhanishtha", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Chara", "Kshipra", "Mridu"],
        "notes": "Muhurta Martanda: Chara (movable) nakshatras best for travel. Swati (self-moving) excellent. Direction of travel matters per weekday. Avoid Vishti karana. Moon waxing & strong."
    },
    "vyapara": {
        "name": "Vyapara (Business/Trade)",
        "name_hi": "व्यापार",
        "good_nakshatras": ["Ashwini", "Rohini", "Punarvasu", "Pushya", "Uttara Phalguni",
                            "Hasta", "Chitra", "Swati", "Anuradha", "Uttara Ashadha",
                            "Shravana", "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 6, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Dhruva", "Kshipra", "Chara", "Mridu"],
        "notes": "Muhurta Martanda: Dhruva nakshatras for permanent/stable business. Mercury strong & unafflicted. Pushya on Thursday = best for new business. Avoid 8th lord in lagna."
    },
    "vidya_arambha": {
        "name": "Vidya Arambha (Education Start)",
        "name_hi": "विद्या आरम्भ",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Shravana", "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 6, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Kshipra", "Mridu", "Dhruva"],
        "notes": "Muhurta Martanda: Dhruva nakshatras for long-term learning stability. Jupiter & Mercury strong. Wednesday & Thursday best. Hasta = skill mastery. Saraswati Puja on Vasant Panchami ideal."
    },
    "upanayana": {
        "name": "Upanayana (Sacred Thread)",
        "name_hi": "उपनयन",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Shravana", "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Dhruva", "Kshipra", "Mridu"],
        "notes": "Muhurta Martanda: Uttarayan & Shukla Paksha preferred. Avoid Rikta tithis & Vishti karana. Jupiter strong. Guru Pushya Yoga excellent."
    },
    "bhumi_puja": {
        "name": "Bhumi Puja (Foundation Stone)",
        "name_hi": "भूमि पूजन",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Pushya", "Uttara Phalguni",
                            "Hasta", "Chitra", "Swati", "Anuradha", "Uttara Ashadha",
                            "Shravana", "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 6, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Taurus", "Cancer", "Leo", "Virgo", "Libra", "Aquarius"],
        "good_nak_class": ["Dhruva", "Kshipra", "Chara"],
        "notes": "Muhurta Martanda: Dhruva nakshatras for permanent structures. Mars not in 7th/8th. 4th house strong. Avoid Rikta tithis. Jupiter unafflicted."
    },
    "krishi": {
        "name": "Krishi (Agriculture/Sowing)",
        "name_hi": "कृषि",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Uttara Ashadha", "Shravana", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 7, 10, 11, 12],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra", "Aquarius", "Pisces"],
        "good_nak_class": ["Dhruva", "Mridu", "Chara"],
        "notes": "Muhurta Martanda: Rohini (lord of vegetation) = best. Moon waxing & in watery/earthy signs. Venus strong for harvest. Mridu nakshatras for sowing. Saturn hora for ploughing."
    },
    "aushadha": {
        "name": "Aushadha (Medical Treatment)",
        "name_hi": "औषध सेवन",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Shravana", "Dhanishtha", "Revati"],
        "good_tithis": [1, 2, 3, 5, 6, 7, 10, 11, 12],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Gemini", "Cancer", "Virgo", "Libra", "Sagittarius"],
        "good_nak_class": ["Kshipra", "Mridu", "Dhruva"],
        "notes": "Muhurta Martanda: Ashwini = divine physicians (Ashwini Kumaras), best for starting treatment. Dhruva nakshatras for long-term treatment stability. Moon waxing preferred."
    },
    "shastra_kriya": {
        "name": "Shastra Kriya (Surgery)",
        "name_hi": "शस्त्र क्रिया",
        "good_nakshatras": ["Ashwini", "Ardra", "Ashlesha", "Jyeshtha", "Mula", "Hasta"],
        "good_tithis": [4, 9, 14],
        "good_varas": [1, 5],
        "avoid_varas": [0, 4],
        "good_lagnas": ["Aries", "Scorpio", "Capricorn"],
        "good_nak_class": ["Tikshna", "Kshipra"],
        "notes": "Muhurta Martanda: Tikshna nakshatras for surgical cutting. Ashwini (divine physicians Ashwini Kumaras) & Hasta excellent for medical procedures. Mars strong. Moon in 3,6,10,11."
    },
    "vastra_dharana": {
        "name": "Vastra Dharana (New Clothes)",
        "name_hi": "वस्त्र धारण",
        "good_nakshatras": ["Rohini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                            "Chitra", "Swati", "Shravana", "Dhanishtha", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Mridu", "Kshipra", "Dhruva"],
        "notes": "Muhurta Martanda: Venus strong — lord of beauty & decoration. Friday excellent. Mridu nakshatras for soft/beautiful clothes. Chitra = Vishwakarma's star for craftsmanship."
    },
    "ratna_dharana": {
        "name": "Ratna Dharana (Gem Wearing)",
        "name_hi": "रत्न धारण",
        "good_nakshatras": ["Ashwini", "Rohini", "Pushya", "Uttara Phalguni", "Hasta",
                            "Chitra", "Swati", "Anuradha", "Shravana",
                            "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 7, 10, 11, 12],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Dhruva", "Kshipra", "Mridu"],
        "notes": "Muhurta Martanda: Planet whose gem is worn must be strong & well-placed. Pushya on Thursday = best for gem/jewelry. Chitra (Vishwakarma's star) for crafted gems."
    },
    "vaahan": {
        "name": "Vaahan (Vehicle Purchase)",
        "name_hi": "वाहन खरीद",
        "good_nakshatras": ["Ashwini", "Rohini", "Punarvasu", "Pushya", "Hasta",
                            "Swati", "Anuradha", "Shravana", "Dhanishtha", "Revati"],
        "good_tithis": [2, 3, 5, 6, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Chara", "Kshipra"],
        "notes": "Muhurta Martanda: Chara (movable) nakshatras ideal for vehicles/transport. Venus strong (vehicle = luxury). Ashwini (horses/speed) = best. Mars-afflicted lagna = accident risk."
    },
    "naamkaran": {
        "name": "Naamkaran (Naming Ceremony)",
        "name_hi": "नामकरण",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Shravana", "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 6, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Gemini", "Cancer", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Kshipra", "Mridu", "Dhruva"],
        "notes": "Muhurta Martanda: Jupiter & Moon strong. Name's first letter from birth nakshatra pada syllable. 11th or 12th day after birth traditional. Shukla Paksha preferred."
    },
    "anna_prashana": {
        "name": "Anna Prashana (First Feeding)",
        "name_hi": "अन्न प्राशन",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Swati", "Shravana", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra", "Sagittarius"],
        "good_nak_class": ["Kshipra", "Mridu"],
        "notes": "Muhurta Martanda: Moon waxing & in benefic sign. Jupiter strong. Even tithis (2,6,10) and Panchami preferred. 6th month after birth traditional. Avoid Rikta tithis."
    },
    "mundan": {
        "name": "Mundan (First Haircut)",
        "name_hi": "मुण्डन",
        "good_nakshatras": ["Ashwini", "Mrigashira", "Punarvasu", "Pushya", "Hasta",
                            "Swati", "Shravana", "Dhanishtha", "Revati"],
        "good_tithis": [2, 3, 5, 6, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Taurus", "Gemini", "Cancer", "Virgo", "Libra"],
        "good_nak_class": ["Kshipra", "Mridu"],
        "notes": "Muhurta Martanda: Avoid child's birth nakshatra + 10th & 19th nakshatra from it. Moon waxing. Kshipra nakshatras for quick healing. Odd year of child's age preferred."
    },
    "vivad_nyaya": {
        "name": "Vivad/Nyaya (Court/Legal)",
        "name_hi": "विवाद/न्याय",
        "good_nakshatras": ["Pushya", "Hasta", "Anuradha", "Uttara Phalguni",
                            "Uttara Ashadha", "Uttara Bhadrapada",
                            "Ardra", "Ashlesha", "Jyeshtha", "Mula",
                            "Bharani", "Magha", "Purva Phalguni",
                            "Purva Ashadha", "Purva Bhadrapada"],
        "good_tithis": [2, 3, 5, 7, 10, 11],
        "good_varas": [1, 3, 6],  # Tue, Thu, Sun (Sun = authority/govt)
        "avoid_varas": [5],
        "good_lagnas": ["Aries", "Leo", "Scorpio", "Sagittarius"],
        "good_nak_class": ["Dhruva", "Ugra", "Tikshna"],
        "notes": "Muhurta Martanda: Tikshna (Ardra, Ashlesha, Jyeshtha, Mula) & Ugra nakshatras for aggressive legal action. Mars & Jupiter strong for victory. Sun strong for government cases. 6th lord weak."
    },
    "daan": {
        "name": "Daan (Charity/Donation)",
        "name_hi": "दान",
        "good_nakshatras": ["Ashwini", "Rohini", "Punarvasu", "Pushya", "Hasta",
                            "Uttara Phalguni", "Swati", "Anuradha", "Shravana",
                            "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 3, 5, 7, 10, 11, 13, 15],
        "good_varas": [0, 2, 3, 4, 6],
        "avoid_varas": [5],
        "good_lagnas": ["Cancer", "Virgo", "Libra", "Sagittarius", "Pisces"],
        "good_nak_class": ["Kshipra", "Dhruva", "Mridu"],
        "notes": "Muhurta Martanda: Purnima, Amavasya, Sankranti, Ekadashi excellent for charity. Punarvasu (return of goodness) ideal. Jupiter strong. Sunday for Sun-related daan."
    },
    "puja_havan": {
        "name": "Puja & Havan (Worship)",
        "name_hi": "पूजा-हवन",
        "good_nakshatras": ["Ashwini", "Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Anuradha",
                            "Uttara Ashadha", "Shravana", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 6, 7, 10, 11, 12, 13, 15],
        "good_varas": [0, 2, 3, 4, 6],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra", "Sagittarius", "Pisces"],
        "good_nak_class": ["Kshipra", "Dhruva", "Mridu"],
        "notes": "Muhurta Martanda: Jupiter hora best. All Dhruva nakshatras excellent. Avoid Rikta tithis & Vishti karana. Shukla Paksha preferred for sattvic rituals."
    },
    "devalaya": {
        "name": "Devalaya (Temple Construction)",
        "name_hi": "देवालय निर्माण",
        "good_nakshatras": ["Rohini", "Pushya", "Uttara Phalguni", "Hasta", "Chitra",
                            "Anuradha", "Uttara Ashadha", "Shravana",
                            "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13, 15],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Leo", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Dhruva", "Kshipra"],
        "notes": "Muhurta Martanda: Dhruva (fixed) nakshatras essential for permanent temple structures. Jupiter strong & unafflicted. Pushya = nourishing, excellent for sacred buildings. Purnima ideal."
    },
    "loan_debt": {
        "name": "Runa (Loan/Borrowing)",
        "name_hi": "ऋण लेना",
        "good_nakshatras": ["Ashwini", "Punarvasu", "Pushya", "Hasta", "Swati",
                            "Anuradha", "Shravana", "Dhanishtha", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11],
        "good_varas": [0, 2, 3],
        "avoid_varas": [1, 4, 5],
        "good_lagnas": ["Taurus", "Gemini", "Cancer", "Virgo", "Libra"],
        "good_nak_class": ["Chara", "Kshipra"],
        "notes": "Muhurta Martanda: Chara nakshatras — loan should flow freely. Mercury & Jupiter strong. 2nd/11th house unafflicted by Saturn. Avoid Friday (Venus = spending). Shukla Paksha preferred."
    },
    "santan_prapti": {
        "name": "Santan (Conception)",
        "name_hi": "सन्तान प्राप्ति",
        "good_nakshatras": ["Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Anuradha",
                            "Shravana", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [1, 2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5, 6],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra", "Sagittarius", "Pisces"],
        "good_nak_class": ["Mridu", "Dhruva", "Kshipra"],
        "notes": "Muhurta Martanda: Mridu nakshatras ideal for conception. Punarvasu = 'return of goodness', fertility star. Jupiter & Venus strong, 5th house unafflicted. Moon waxing in even signs preferred."
    },
    "pratishtha": {
        "name": "Pratishtha (Idol Installation)",
        "name_hi": "प्रतिष्ठा",
        "good_nakshatras": ["Rohini", "Mrigashira", "Pushya", "Uttara Phalguni", "Hasta",
                            "Anuradha", "Uttara Ashadha", "Shravana",
                            "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13, 15],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Leo", "Virgo", "Libra", "Sagittarius"],
        "good_nak_class": ["Dhruva", "Kshipra"],
        "notes": "Muhurta Martanda: Dhruva (fixed) nakshatras mandatory — idol must be permanent. Jupiter strong & unafflicted. Purnima excellent. Shukla Paksha required."
    },
    "gold_purchase": {
        "name": "Swarna Kray (Gold Purchase)",
        "name_hi": "स्वर्ण खरीद",
        "good_nakshatras": ["Ashwini", "Rohini", "Pushya", "Uttara Phalguni", "Hasta",
                            "Chitra", "Swati", "Anuradha", "Shravana",
                            "Dhanishtha", "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],  # Mon, Wed, Thu, Fri
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Leo", "Virgo", "Libra", "Sagittarius"],
        "good_nak_class": ["Dhruva", "Kshipra", "Mridu"],
        "notes": "Muhurta Martanda: Pushya nakshatra = supreme for gold purchase (Pushya-Swarna Yoga). Thursday best. Sun & Jupiter strong. Dhanteras (Dhanishtha + Trayodashi) traditional gold-buying day."
    },
    "property_purchase": {
        "name": "Bhu Kray (Property Purchase)",
        "name_hi": "भू-सम्पत्ति खरीद",
        "good_nakshatras": ["Rohini", "Pushya", "Uttara Phalguni", "Hasta", "Chitra",
                            "Anuradha", "Uttara Ashadha", "Shravana",
                            "Uttara Bhadrapada", "Revati"],
        "good_tithis": [2, 3, 5, 7, 10, 11, 12, 13],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Leo", "Virgo", "Libra", "Sagittarius", "Aquarius"],
        "good_nak_class": ["Dhruva", "Kshipra"],
        "notes": "Muhurta Martanda: Dhruva (fixed) nakshatras essential for permanent property. 4th house & Mars unafflicted. Pushya = nourishing for land. Avoid Rikta tithis."
    },
    "rasoi_arambha": {
        "name": "Rasoi Arambha (Kitchen/Food Start)",
        "name_hi": "रसोई आरम्भ",
        "good_nakshatras": ["Rohini", "Mrigashira", "Punarvasu", "Pushya",
                            "Uttara Phalguni", "Hasta", "Chitra", "Swati",
                            "Anuradha", "Shravana", "Revati"],
        "good_tithis": [2, 3, 5, 6, 7, 10, 11, 12],
        "good_varas": [0, 2, 3, 4],
        "avoid_varas": [1, 5],
        "good_lagnas": ["Taurus", "Cancer", "Virgo", "Libra"],
        "good_nak_class": ["Mridu", "Kshipra", "Dhruva"],
        "notes": "Muhurta Martanda: Moon & Venus strong for nourishment. Avoid fiery signs (Aries, Leo, Sagittarius) in lagna — fire risk. Mridu nakshatras for gentle cooking. Rohini = vegetation/food."
    },
}

# ═══════════════════════════════════════════════════════════════
# CORE CALCULATION FUNCTIONS
# ═══════════════════════════════════════════════════════════════

def _get_nak_index(longitude: float) -> int:
    """Get nakshatra index (0-26) from sidereal longitude."""
    idx = int(longitude / NAKSHATRA_SPAN_DEG)
    return min(idx, 26)


def _get_sign_name(longitude: float) -> str:
    """Get sign name from sidereal longitude."""
    idx = int(longitude / 30) % 12
    return SIGNS[idx]


def calculate_tara_bala(
    birth_nak_index: int,
    transit_nak_index: int,
) -> Dict:
    """
    Calculate Tara Bala — the relationship between birth nakshatra
    and transit/muhurta Moon nakshatra.

    There are 9 Taras, cycling in groups of 3 (each group = 9 nakshatras).
    Tara # = ((transit_nak - birth_nak) % 27) // 1, then (result % 9) + 1
    """
    diff = (transit_nak_index - birth_nak_index) % 27
    tara_num = (diff % 9) + 1
    tara_group = (diff // 9) + 1  # 1st, 2nd, or 3rd cycle

    tara_name = TARA_NAMES[tara_num - 1]
    tara_info = TARA_NATURE[tara_name]

    # Even-numbered taras in 2nd/3rd cycle are less harmful
    modified_score = tara_info["score"]
    if tara_group > 1 and tara_info["score"] < 0:
        modified_score = tara_info["score"] * 0.6  # Reduced maleficence

    return {
        "tara_number": tara_num,
        "tara_name": tara_name,
        "tara_name_hi": _tara_hindi(tara_name),
        "tara_group": tara_group,
        "nature": tara_info["nature"],
        "score": round(modified_score, 2),
        "advice": tara_info["advice"],
        "birth_nakshatra": NAKSHATRA_NAMES_27[birth_nak_index],
        "transit_nakshatra": NAKSHATRA_NAMES_27[transit_nak_index],
    }


def _tara_hindi(name: str) -> str:
    hindi = {
        "Janma": "जन्म", "Sampat": "सम्पत्", "Vipat": "विपत्",
        "Kshema": "क्षेम", "Pratyari": "प्रत्यरि", "Sadhaka": "साधक",
        "Vadha": "वध", "Mitra": "मित्र", "Atimitra": "अतिमित्र",
    }
    return hindi.get(name, name)


def calculate_chandra_bala(
    birth_moon_sign_idx: int,
    transit_moon_sign_idx: int,
) -> Dict:
    """
    Calculate Chandra Bala — Moon's strength based on transit
    position from natal Moon sign.

    Houses 3, 6, 7, 9, 10, 11 from natal Moon = strong (auspicious)
    Houses 1, 2, 4, 5, 8, 12 = weak (inauspicious)
    """
    house = ((transit_moon_sign_idx - birth_moon_sign_idx) % 12) + 1
    bala = CHANDRA_BALA[house]

    return {
        "house_from_moon": house,
        "house_name": bala["name"],
        "house_name_hi": _chandra_hindi(bala["name"]),
        "nature": bala["nature"],
        "score": bala["score"],
        "advice": bala["advice"],
        "birth_moon_sign": SIGNS[birth_moon_sign_idx],
        "transit_moon_sign": SIGNS[transit_moon_sign_idx],
        "is_strong": house in [3, 6, 7, 9, 10, 11],
    }


def _chandra_hindi(name: str) -> str:
    hindi = {
        "Janma": "जन्म", "Dhana": "धन", "Sahaja": "सहज",
        "Sukha": "सुख", "Putra": "पुत्र", "Shatru": "शत्रु",
        "Kalatra": "कलत्र", "Mrityu": "मृत्यु", "Dharma": "धर्म",
        "Karma": "कर्म", "Labha": "लाभ", "Vyaya": "व्यय",
    }
    return hindi.get(name, name)


def check_panchanga_shuddhi(
    tithi_in_paksha: int,
    nakshatra_idx: int,
    yoga_name: str,
    karana_name: str,
    weekday: int,  # 0=Mon..6=Sun
) -> Dict:
    """
    Panchanga Shuddhi — check purity of all 5 Panchanga elements.
    Per Muhurta Martanda: all 5 must be auspicious for a fully pure muhurta.
    """
    checks = []
    total_score = 0
    max_possible = 5

    # 1. Tithi check
    tithi_nature = None
    for nature, nums in TITHI_NATURE.items():
        if tithi_in_paksha in nums:
            tithi_nature = nature
            break
    tithi_ok = tithi_nature in ("Nanda", "Bhadra", "Jaya", "Purna")
    tithi_bad = tithi_nature == "Rikta"
    t_score = 1.0 if tithi_ok and not tithi_bad else (0.3 if not tithi_bad else -0.5)
    checks.append({
        "element": "Tithi",
        "element_hi": "तिथि",
        "value": TITHI_NAMES_15[tithi_in_paksha - 1] if 1 <= tithi_in_paksha <= 15 else f"T{tithi_in_paksha}",
        "nature": tithi_nature or "Unknown",
        "is_pure": tithi_ok,
        "score": t_score,
        "note": "Rikta tithis (4,9,14) are inauspicious" if tithi_bad else ("Auspicious tithi" if tithi_ok else "Neutral"),
    })
    total_score += t_score

    # 2. Nakshatra check
    nak_name = NAKSHATRA_NAMES_27[nakshatra_idx] if 0 <= nakshatra_idx < 27 else "Unknown"
    nak_class = NAKSHATRA_CLASSIFICATION.get(nak_name, "Unknown")
    nak_good = nak_class in ("Dhruva", "Kshipra", "Mridu", "Chara")
    nak_bad = nak_class in ("Tikshna", "Ugra")
    n_score = 1.0 if nak_good else (-0.3 if nak_bad else 0.5)
    checks.append({
        "element": "Nakshatra",
        "element_hi": "नक्षत्र",
        "value": nak_name,
        "nature": nak_class,
        "nature_hi": NAKSHATRA_CLASS_HINDI.get(nak_class, nak_class),
        "is_pure": nak_good,
        "score": n_score,
        "note": f"{nak_class} nakshatra — {'auspicious' if nak_good else 'caution needed' if nak_bad else 'mixed'}",
    })
    total_score += n_score

    # 3. Yoga check
    yq = YOGA_QUALITY.get(yoga_name, "Neutral")
    yoga_good = "Auspicious" in yq
    yoga_bad = "Inauspicious" in yq
    y_score = 1.0 if yoga_good else (-0.5 if yoga_bad else 0.3)
    checks.append({
        "element": "Yoga",
        "element_hi": "योग",
        "value": yoga_name,
        "nature": yq,
        "is_pure": yoga_good,
        "score": y_score,
        "note": f"{yq} yoga" + (" — avoid Vyatipata, Vaidhriti, Ganda" if yoga_bad else ""),
    })
    total_score += y_score

    # 4. Karana check
    kq = KARANA_QUALITY.get(karana_name, "Neutral")
    karana_good = kq == "Auspicious"
    karana_bad = "Inauspicious" in kq
    k_score = 1.0 if karana_good else (-0.8 if karana_name == "Vishti" else (-0.3 if karana_bad else 0.3))
    checks.append({
        "element": "Karana",
        "element_hi": "करण",
        "value": karana_name,
        "nature": kq,
        "is_pure": karana_good,
        "score": k_score,
        "note": "Vishti (Bhadra) karana — strictly avoid" if karana_name == "Vishti" else (
            "Auspicious karana" if karana_good else "Fixed karana — caution"
        ),
    })
    total_score += k_score

    # 5. Vara (weekday) check
    vara_names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    vara_hi = ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"]
    vara_good = weekday in [0, 2, 3, 4]  # Mon, Wed, Thu, Fri
    vara_bad = weekday in [1, 5]  # Tue, Sat
    v_score = 1.0 if weekday == 3 else (0.8 if vara_good else (-0.3 if vara_bad else 0.3))
    checks.append({
        "element": "Vara",
        "element_hi": "वार",
        "value": vara_names[weekday],
        "value_hi": vara_hi[weekday],
        "is_pure": vara_good,
        "score": v_score,
        "note": "Thursday (Guru) is best for auspicious works" if weekday == 3 else (
            "Good weekday" if vara_good else "Tuesday/Saturday — caution for auspicious acts"
        ),
    })
    total_score += v_score

    pure_count = sum(1 for c in checks if c["is_pure"])
    avg_score = total_score / max_possible

    if pure_count == 5:
        verdict = "Pancha Shuddhi — All 5 pure"
        verdict_hi = "पंचांग शुद्ध — सर्वोत्तम"
    elif pure_count >= 3:
        verdict = f"{pure_count}/5 Pure — Acceptable"
        verdict_hi = f"{pure_count}/5 शुद्ध — ग्राह्य"
    else:
        verdict = f"Only {pure_count}/5 Pure — Avoid"
        verdict_hi = f"केवल {pure_count}/5 शुद्ध — अशुभ"

    return {
        "checks": checks,
        "pure_count": pure_count,
        "total_elements": 5,
        "average_score": round(avg_score, 3),
        "is_fully_pure": pure_count == 5,
        "verdict": verdict,
        "verdict_hi": verdict_hi,
    }


def check_doshas(
    tithi_in_paksha: int,
    nakshatra_idx: int,
    weekday: int,
) -> List[Dict]:
    """
    Check for various Muhurta doshas per Muhurta Martanda.
    Returns list of active doshas.
    """
    doshas = []

    # 1. Dagdha Tithi (Burnt Tithi)
    if (tithi_in_paksha, weekday) in DAGDHA_TITHI:
        doshas.append({
            "dosha": "Dagdha Tithi",
            "dosha_hi": "दग्ध तिथि",
            "severity": "High",
            "description": f"Tithi {tithi_in_paksha} + {_vara_name(weekday)} = Burnt combination",
            "remedy": "Avoid new beginnings. If unavoidable, do Ganapati puja.",
        })

    # 2. Mrityu Yoga
    if (nakshatra_idx, weekday) in MRITYU_YOGA:
        doshas.append({
            "dosha": "Mrityu Yoga",
            "dosha_hi": "मृत्यु योग",
            "severity": "Very High",
            "description": f"{NAKSHATRA_NAMES_27[nakshatra_idx]} + {_vara_name(weekday)} = Death combination",
            "remedy": "Strictly avoid all important activities.",
        })

    # 3. Panchaka Dosha
    if nakshatra_idx in PANCHAKA_NAKSHATRAS:
        doshas.append({
            "dosha": "Panchaka",
            "dosha_hi": "पंचक",
            "severity": "Medium",
            "description": f"Moon in {NAKSHATRA_NAMES_27[nakshatra_idx]} — Panchaka zone (last 5 nakshatras)",
            "remedy": "Avoid construction, travel south, funerals. Panchaka shanti recommended.",
        })

    # 4. Rikta Tithi
    if tithi_in_paksha in [4, 9, 14]:
        doshas.append({
            "dosha": "Rikta Tithi",
            "dosha_hi": "रिक्त तिथि",
            "severity": "Medium",
            "description": f"Tithi {tithi_in_paksha} is Rikta (empty) — resources drain away",
            "remedy": "Not suitable for financial/business actions. Worship & charity OK.",
        })

    # 5. Ashtami Dosha (8th tithi)
    if tithi_in_paksha == 8:
        doshas.append({
            "dosha": "Ashtami",
            "dosha_hi": "अष्टमी दोष",
            "severity": "Low-Medium",
            "description": "Ashtami tithi — volatile energy, especially Krishna Ashtami",
            "remedy": "Avoid major initiations. Good for spiritual practices.",
        })

    # 6. Tuesday + Saturday (double malefic vara)
    if weekday == 1:  # Tuesday
        if tithi_in_paksha in [4, 9, 14]:  # Rikta + Tuesday = very bad
            doshas.append({
                "dosha": "Mangal-Rikta",
                "dosha_hi": "मंगल-रिक्त योग",
                "severity": "High",
                "description": "Mars day + Rikta tithi — double inauspicious",
                "remedy": "Postpone all new activities.",
            })

    return doshas


def _vara_name(weekday: int) -> str:
    names = ["Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday", "Sunday"]
    return names[weekday] if 0 <= weekday < 7 else f"Day{weekday}"


def calculate_hora(
    dt: datetime,
    sunrise_hour: float = 6.0,
) -> Dict:
    """
    Calculate planetary Hora (hour) for a given datetime.
    Each day has 24 horas starting from sunrise.
    """
    weekday = dt.weekday()  # 0=Mon..6=Sun
    # Hours since sunrise
    current_hour = dt.hour + dt.minute / 60.0
    hours_since_sunrise = current_hour - sunrise_hour
    if hours_since_sunrise < 0:
        hours_since_sunrise += 24

    hora_number = int(hours_since_sunrise) % 24

    # Get starting planet for this weekday
    start_idx = HORA_DAY_START.get(weekday, 0)
    planet_idx = (start_idx + hora_number) % 7
    hora_lord = HORA_ORDER[planet_idx]

    quality = HORA_QUALITY.get(hora_lord, {})

    return {
        "hora_number": hora_number + 1,
        "hora_lord": hora_lord,
        "nature": quality.get("nature", ""),
        "score": quality.get("score", 0),
        "good_for": quality.get("good_for", ""),
        "hora_start": _fmt_time(sunrise_hour + hora_number),
        "hora_end": _fmt_time(sunrise_hour + hora_number + 1),
    }


def _fmt_time(hours: float) -> str:
    h = int(hours) % 24
    m = int((hours - int(hours)) * 60)
    return f"{h:02d}:{m:02d}"


def check_lagna_shuddhi(
    lagna_sign: str,
    activity: str,
    moon_sign_in_lagna: bool = False,
) -> Dict:
    """
    Check Lagna (Ascendant) purity for a given activity.
    Per Muhurta Martanda: certain lagnas are good/bad for specific activities.
    """
    activity_data = MUHURTA_ACTIVITIES.get(activity)
    if not activity_data:
        return {"is_pure": True, "score": 0.5, "note": "Activity not found — generic check only"}

    good_lagnas = activity_data.get("good_lagnas", [])
    is_good = lagna_sign in good_lagnas

    # General rule: 6th, 8th, 12th from lagna lord are bad
    score = 0.8 if is_good else -0.3

    # Moon in lagna is generally good for muhurta
    if moon_sign_in_lagna:
        score += 0.2

    return {
        "lagna_sign": lagna_sign,
        "is_pure": is_good,
        "score": round(score, 2),
        "good_lagnas_for_activity": good_lagnas,
        "note": f"{lagna_sign} is {'suitable' if is_good else 'NOT ideal'} for {activity_data['name']}",
    }


# ═══════════════════════════════════════════════════════════════
# ACTIVITY-SPECIFIC MUHURTA ANALYSIS
# ═══════════════════════════════════════════════════════════════

def analyze_activity_muhurta(
    activity: str,
    tithi_in_paksha: int,
    nakshatra_idx: int,
    yoga_name: str,
    karana_name: str,
    weekday: int,
    birth_nak_idx: Optional[int] = None,
    birth_moon_sign_idx: Optional[int] = None,
    transit_moon_sign_idx: Optional[int] = None,
    lagna_sign: Optional[str] = None,
    paksha: str = "Shukla",
) -> Dict:
    """
    Comprehensive muhurta analysis for a specific activity.
    Checks all parameters per Muhurta Martanda rules.
    """
    activity_data = MUHURTA_ACTIVITIES.get(activity)
    if not activity_data:
        return {"error": f"Unknown activity: {activity}. Available: {list(MUHURTA_ACTIVITIES.keys())}"}

    results = {}
    score_components = []
    warnings = []
    positives = []

    # ── 1. Panchanga Shuddhi ──
    panchanga = check_panchanga_shuddhi(tithi_in_paksha, nakshatra_idx, yoga_name, karana_name, weekday)
    results["panchanga_shuddhi"] = panchanga
    score_components.append(("Panchanga Shuddhi", panchanga["average_score"], 0.20))

    # ── 2. Activity-specific Nakshatra check ──
    nak_name = NAKSHATRA_NAMES_27[nakshatra_idx] if 0 <= nakshatra_idx < 27 else ""
    nak_is_good = nak_name in activity_data.get("good_nakshatras", [])
    nak_class = NAKSHATRA_CLASSIFICATION.get(nak_name, "")
    nak_class_good = nak_class in activity_data.get("good_nak_class", [])
    nak_score = 1.0 if nak_is_good else (0.5 if nak_class_good else -0.3)
    results["nakshatra_fitness"] = {
        "nakshatra": nak_name,
        "classification": nak_class,
        "classification_hi": NAKSHATRA_CLASS_HINDI.get(nak_class, nak_class),
        "is_recommended": nak_is_good,
        "class_is_suitable": nak_class_good,
        "score": nak_score,
    }
    score_components.append(("Nakshatra Fitness", nak_score, 0.15))
    if nak_is_good:
        positives.append(f"{nak_name} is specifically recommended for {activity_data['name']}")
    elif not nak_class_good:
        warnings.append(f"{nak_name} ({nak_class}) is NOT ideal for {activity_data['name']}")

    # ── 3. Activity-specific Tithi check ──
    tithi_good = tithi_in_paksha in activity_data.get("good_tithis", [])
    tithi_score = 0.8 if tithi_good else -0.3
    tithi_name = TITHI_NAMES_15[tithi_in_paksha - 1] if 1 <= tithi_in_paksha <= 15 else f"T{tithi_in_paksha}"
    results["tithi_fitness"] = {
        "tithi": tithi_name,
        "paksha": paksha,
        "is_recommended": tithi_good,
        "score": tithi_score,
    }
    score_components.append(("Tithi Fitness", tithi_score, 0.10))
    if tithi_good:
        positives.append(f"{paksha} {tithi_name} is suitable for {activity_data['name']}")

    # ── 4. Activity-specific Vara check ──
    vara_good = weekday in activity_data.get("good_varas", [])
    vara_avoid = weekday in activity_data.get("avoid_varas", [])
    vara_score = 0.8 if vara_good else (-0.5 if vara_avoid else 0.2)
    results["vara_fitness"] = {
        "vara": _vara_name(weekday),
        "is_recommended": vara_good,
        "is_avoided": vara_avoid,
        "score": vara_score,
    }
    score_components.append(("Vara Fitness", vara_score, 0.10))
    if vara_avoid:
        warnings.append(f"{_vara_name(weekday)} is traditionally avoided for {activity_data['name']}")

    # ── 5. Doshas ──
    doshas = check_doshas(tithi_in_paksha, nakshatra_idx, weekday)
    results["doshas"] = doshas
    dosha_penalty = sum(-0.15 for d in doshas if d["severity"] == "High") + \
                    sum(-0.25 for d in doshas if d["severity"] == "Very High") + \
                    sum(-0.08 for d in doshas if d["severity"] in ("Medium", "Low-Medium"))
    score_components.append(("Dosha Check", max(-1.0, dosha_penalty), 0.15))
    for d in doshas:
        warnings.append(f"{d['dosha']} ({d['dosha_hi']}) — {d['description']}")

    # ── 6. Tara Bala (if birth nakshatra provided) ──
    if birth_nak_idx is not None:
        tara = calculate_tara_bala(birth_nak_idx, nakshatra_idx)
        results["tara_bala"] = tara
        score_components.append(("Tara Bala", tara["score"], 0.12))
        if tara["score"] < 0:
            warnings.append(f"Tara Bala: {tara['tara_name']} ({tara['tara_name_hi']}) — {tara['advice']}")
        else:
            positives.append(f"Tara Bala: {tara['tara_name']} ({tara['tara_name_hi']}) — {tara['advice']}")

    # ── 7. Chandra Bala (if birth Moon sign provided) ──
    if birth_moon_sign_idx is not None and transit_moon_sign_idx is not None:
        chandra = calculate_chandra_bala(birth_moon_sign_idx, transit_moon_sign_idx)
        results["chandra_bala"] = chandra
        score_components.append(("Chandra Bala", chandra["score"], 0.10))
        if not chandra["is_strong"]:
            warnings.append(f"Chandra Bala: Moon in {chandra['house_name']} ({chandra['house_name_hi']}) — {chandra['advice']}")
        else:
            positives.append(f"Chandra Bala: Moon in {chandra['house_name']} ({chandra['house_name_hi']}) — {chandra['advice']}")

    # ── 8. Lagna Shuddhi ──
    if lagna_sign:
        lagna = check_lagna_shuddhi(lagna_sign, activity)
        results["lagna_shuddhi"] = lagna
        score_components.append(("Lagna Shuddhi", lagna["score"], 0.08))

    # ═══ FINAL WEIGHTED SCORE ═══
    total_weight = sum(w for _, _, w in score_components)
    if total_weight > 0:
        final_score = sum(s * w for _, s, w in score_components) / total_weight
    else:
        final_score = 0

    final_score = max(-1.0, min(1.0, final_score))

    # Verdict
    if final_score >= 0.6:
        verdict = "HIGHLY AUSPICIOUS"
        verdict_hi = "अत्यन्त शुभ"
        verdict_type = "excellent"
        color = "#00C851"
    elif final_score >= 0.3:
        verdict = "AUSPICIOUS"
        verdict_hi = "शुभ"
        verdict_type = "good"
        color = "#4CAF50"
    elif final_score >= 0.0:
        verdict = "MIXED — Proceed with Caution"
        verdict_hi = "मिश्र — सावधानी"
        verdict_type = "mixed"
        color = "#FFC107"
    elif final_score >= -0.3:
        verdict = "INAUSPICIOUS — Avoid if Possible"
        verdict_hi = "अशुभ — यथासम्भव टालें"
        verdict_type = "bad"
        color = "#FF9800"
    else:
        verdict = "HIGHLY INAUSPICIOUS — Do Not Proceed"
        verdict_hi = "अत्यन्त अशुभ — कार्य न करें"
        verdict_type = "very_bad"
        color = "#FF3D00"

    results["final_analysis"] = {
        "activity": activity_data["name"],
        "activity_hi": activity_data["name_hi"],
        "final_score": round(final_score, 3),
        "verdict": verdict,
        "verdict_hi": verdict_hi,
        "verdict_type": verdict_type,
        "color": color,
        "score_breakdown": [
            {"component": name, "score": round(s, 3), "weight": f"{w*100:.0f}%"}
            for name, s, w in score_components
        ],
        "warnings": warnings,
        "positives": positives,
        "activity_notes": activity_data.get("notes", ""),
    }

    return results


# ═══════════════════════════════════════════════════════════════
# MASTER MUHURTA ANALYSIS — Full comprehensive check
# ═══════════════════════════════════════════════════════════════

def calculate_advanced_muhurta(
    date_str: str,
    time_str: str = "09:15",
    latitude: float = 19.076,
    longitude_geo: float = 72.8777,
    timezone_offset_minutes: int = 330,
    ayanamsa_key: str = "lahiri",
    activity: str = "vyapara",
    birth_nakshatra: Optional[str] = None,
    birth_moon_sign: Optional[str] = None,
) -> Dict:
    """
    Master Advanced Muhurta analysis combining all checks from Muhurta Martanda.
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

    # Get Sun and Moon
    sun_result = swe.calc_ut(jd, swe.SUN, flags)
    moon_result = swe.calc_ut(jd, swe.MOON, flags)
    sun_long = sun_result[0][0] % 360
    moon_long = moon_result[0][0] % 360

    # Calculate Panchanga elements
    diff = (moon_long - sun_long) % 360
    tithi_num = int(diff / 12.0)
    tithi_in_paksha = (tithi_num % 15) + 1
    paksha = "Shukla" if tithi_num < 15 else "Krishna"

    nakshatra_idx = _get_nak_index(moon_long)
    yoga_total = (sun_long + moon_long) % 360
    yoga_idx = min(int(yoga_total / NAKSHATRA_SPAN_DEG), 26)
    yoga_name = YOGA_NAMES_27[yoga_idx]

    karana_num = int(diff / 6.0)
    if karana_num == 0:
        karana_name = "Kimstughna"
    elif karana_num >= 57:
        karana_name = ["Shakuni", "Chatushpada", "Naga"][min(karana_num - 57, 2)]
    else:
        karana_name = ["Bava", "Balava", "Kaulava", "Taitila", "Garija", "Vanija", "Vishti"][(karana_num - 1) % 7]

    weekday = dt.weekday()

    # Resolve birth nakshatra
    birth_nak_idx = None
    if birth_nakshatra:
        for i, n in enumerate(NAKSHATRA_NAMES_27):
            if n.lower() == birth_nakshatra.lower():
                birth_nak_idx = i
                break

    # Resolve birth Moon sign
    birth_moon_sign_idx = None
    if birth_moon_sign:
        for i, s in enumerate(SIGNS):
            if s.lower() == birth_moon_sign.lower():
                birth_moon_sign_idx = i
                break

    transit_moon_sign_idx = int(moon_long / 30) % 12

    # Get lagna (ascendant)
    try:
        cusps, ascmc = swe.houses(jd, latitude, longitude_geo, b'P')
        asc_long = cusps[0] if cusps else 0
        lagna_sign = _get_sign_name(asc_long)
    except Exception:
        lagna_sign = None

    # Run activity muhurta analysis
    analysis = analyze_activity_muhurta(
        activity=activity,
        tithi_in_paksha=tithi_in_paksha,
        nakshatra_idx=nakshatra_idx,
        yoga_name=yoga_name,
        karana_name=karana_name,
        weekday=weekday,
        birth_nak_idx=birth_nak_idx,
        birth_moon_sign_idx=birth_moon_sign_idx,
        transit_moon_sign_idx=transit_moon_sign_idx,
        lagna_sign=lagna_sign,
        paksha=paksha,
    )

    # Calculate Hora
    hora = calculate_hora(dt)

    # Build response
    return {
        "type": "advanced_muhurta",
        "date": date_str,
        "time": time_str,
        "weekday": _vara_name(weekday),
        "weekday_hi": ["सोमवार", "मंगलवार", "बुधवार", "गुरुवार", "शुक्रवार", "शनिवार", "रविवार"][weekday],
        "panchanga_summary": {
            "tithi": f"{paksha} {TITHI_NAMES_15[tithi_in_paksha-1] if 1<=tithi_in_paksha<=15 else ''}",
            "nakshatra": NAKSHATRA_NAMES_27[nakshatra_idx],
            "nakshatra_lord": NAKSHATRA_LORDS_27[nakshatra_idx],
            "yoga": yoga_name,
            "karana": karana_name,
        },
        "moon_longitude": round(moon_long, 4),
        "sun_longitude": round(sun_long, 4),
        "lagna_sign": lagna_sign,
        "hora": hora,
        "analysis": analysis,
        "activity_list": {k: v["name"] for k, v in MUHURTA_ACTIVITIES.items()},
    }


def get_activity_list() -> List[Dict]:
    """Return list of all available muhurta activities."""
    return [
        {"key": k, "name": v["name"], "name_hi": v["name_hi"]}
        for k, v in MUHURTA_ACTIVITIES.items()
    ]


# ═══════════════════════════════════════════════════════════════
# AUTOMATED MUHURTA FINDER — Scan date range for best muhurtas
# ═══════════════════════════════════════════════════════════════

def find_muhurta_dates(
    activity: str,
    start_date: str,
    months_ahead: int = 6,
    person_name: str = "",
    latitude: float = 19.076,
    longitude_geo: float = 72.8777,
    timezone_offset_minutes: int = 330,
    ayanamsa_key: str = "lahiri",
    birth_nakshatra: Optional[str] = None,
    birth_moon_sign: Optional[str] = None,
    min_score: float = 0.0,
    time_str: str = "09:15",
) -> Dict:
    """
    Scan a date range (up to 12 months) and find all auspicious muhurta dates
    for a given activity. Returns ranked list of dates sorted by score.

    Parameters
    ----------
    activity : str
        Activity key from MUHURTA_ACTIVITIES (e.g. 'vivaha', 'namkaran')
    start_date : str
        Start date in YYYY-MM-DD format
    months_ahead : int
        Number of months to scan (1-12, default 6)
    person_name : str
        Name of person for whom muhurta is being found
    latitude, longitude_geo : float
        Location coordinates
    timezone_offset_minutes : int
        Timezone offset from UTC in minutes (default 330 for IST)
    ayanamsa_key : str
        Ayanamsa system (lahiri/krishnamurti/raman)
    birth_nakshatra : str, optional
        Birth nakshatra for Tara Bala calculation
    birth_moon_sign : str, optional
        Birth Moon sign for Chandra Bala calculation
    min_score : float
        Minimum score threshold (0.0 = include all, default)
    time_str : str
        Default analysis time (default "09:15")

    Returns
    -------
    dict with keys: person_name, activity, activity_name, search_range,
    total_days_scanned, dates_found, best_dates (top 20), all_dates (full list)
    """
    if activity not in MUHURTA_ACTIVITIES:
        raise ValueError(f"Unknown activity '{activity}'. Valid: {list(MUHURTA_ACTIVITIES.keys())}")

    months_ahead = max(1, min(12, months_ahead))

    start_dt = datetime.strptime(start_date, "%Y-%m-%d")
    end_dt = start_dt + timedelta(days=months_ahead * 30)

    # Set ayanamsa once
    ayanamsa_map = {
        "lahiri": swe.SIDM_LAHIRI,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "raman": swe.SIDM_RAMAN,
    }
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key.lower(), swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    # Resolve birth nakshatra index
    birth_nak_idx = None
    if birth_nakshatra:
        for i, n in enumerate(NAKSHATRA_NAMES_27):
            if n.lower() == birth_nakshatra.lower():
                birth_nak_idx = i
                break

    # Resolve birth Moon sign index
    birth_moon_sign_idx = None
    if birth_moon_sign:
        for i, s in enumerate(SIGNS):
            if s.lower() == birth_moon_sign.lower():
                birth_moon_sign_idx = i
                break

    all_dates = []
    current = start_dt
    total_days = 0

    while current <= end_dt:
        total_days += 1
        date_str = current.strftime("%Y-%m-%d")

        try:
            # Compute JD for this day
            dt = datetime.strptime(f"{date_str} {time_str}", "%Y-%m-%d %H:%M")
            utc_dt = dt - timedelta(minutes=timezone_offset_minutes)
            jd = swe.julday(
                utc_dt.year, utc_dt.month, utc_dt.day,
                utc_dt.hour + utc_dt.minute / 60.0
            )

            # Get Sun and Moon
            sun_result = swe.calc_ut(jd, swe.SUN, flags)
            moon_result = swe.calc_ut(jd, swe.MOON, flags)
            sun_long = sun_result[0][0] % 360
            moon_long = moon_result[0][0] % 360

            # Panchanga elements
            diff = (moon_long - sun_long) % 360
            tithi_num = int(diff / 12.0)
            tithi_in_paksha = (tithi_num % 15) + 1
            paksha = "Shukla" if tithi_num < 15 else "Krishna"

            nakshatra_idx = _get_nak_index(moon_long)
            yoga_total = (sun_long + moon_long) % 360
            yoga_idx = min(int(yoga_total / NAKSHATRA_SPAN_DEG), 26)
            yoga_name = YOGA_NAMES_27[yoga_idx]

            karana_num = int(diff / 6.0)
            if karana_num == 0:
                karana_name = "Kimstughna"
            elif karana_num >= 57:
                karana_name = ["Shakuni", "Chatushpada", "Naga"][min(karana_num - 57, 2)]
            else:
                karana_name = ["Bava", "Balava", "Kaulava", "Taitila",
                               "Garija", "Vanija", "Vishti"][(karana_num - 1) % 7]

            weekday = dt.weekday()
            transit_moon_sign_idx = int(moon_long / 30) % 12

            # Lagna (ascendant)
            try:
                cusps, ascmc = swe.houses(jd, latitude, longitude_geo, b'P')
                asc_long = cusps[0] if cusps else 0
                lagna_sign = _get_sign_name(asc_long)
            except Exception:
                lagna_sign = None

            # Run activity analysis
            analysis = analyze_activity_muhurta(
                activity=activity,
                tithi_in_paksha=tithi_in_paksha,
                nakshatra_idx=nakshatra_idx,
                yoga_name=yoga_name,
                karana_name=karana_name,
                weekday=weekday,
                birth_nak_idx=birth_nak_idx,
                birth_moon_sign_idx=birth_moon_sign_idx,
                transit_moon_sign_idx=transit_moon_sign_idx,
                lagna_sign=lagna_sign,
                paksha=paksha,
            )

            fa = analysis.get("final_analysis", {})
            raw_score = fa.get("final_score", 0)  # -1 to +1 scale
            # Convert to 0-100 scale: -1→0, 0→50, +1→100
            score_100 = round((raw_score + 1) * 50, 2)

            if score_100 >= min_score:
                # Hora for this day
                hora = calculate_hora(dt)

                all_dates.append({
                    "date": date_str,
                    "weekday": _vara_name(weekday),
                    "weekday_hi": ["सोमवार", "मंगलवार", "बुधवार",
                                   "गुरुवार", "शुक्रवार", "शनिवार",
                                   "रविवार"][weekday],
                    "tithi": f"{paksha} {TITHI_NAMES_15[tithi_in_paksha-1] if 1<=tithi_in_paksha<=15 else ''}",
                    "nakshatra": NAKSHATRA_NAMES_27[nakshatra_idx],
                    "nakshatra_lord": NAKSHATRA_LORDS_27[nakshatra_idx],
                    "yoga": yoga_name,
                    "karana": karana_name,
                    "lagna_sign": lagna_sign,
                    "hora_lord": hora.get("hora_lord", ""),
                    "moon_sign": SIGNS[transit_moon_sign_idx],
                    "score": score_100,
                    "verdict": fa.get("verdict", ""),
                    "verdict_color": fa.get("color", ""),
                    "panchanga_shuddhi": analysis.get("panchanga_shuddhi", {}),
                    "tara_bala": analysis.get("tara_bala"),
                    "chandra_bala": analysis.get("chandra_bala"),
                    "doshas": analysis.get("doshas", []),
                    "positives": fa.get("positives", []),
                    "warnings": fa.get("warnings", []),
                    "score_breakdown": fa.get("score_breakdown", []),
                })
        except Exception:
            # Skip dates that fail (e.g., ephemeris out of range)
            pass

        current += timedelta(days=1)

    # Sort by score descending
    all_dates.sort(key=lambda x: x["score"], reverse=True)

    # Categorize dates
    excellent = [d for d in all_dates if d["score"] >= 75]
    good = [d for d in all_dates if 50 <= d["score"] < 75]
    average = [d for d in all_dates if 25 <= d["score"] < 50]
    poor = [d for d in all_dates if d["score"] < 25]

    activity_info = MUHURTA_ACTIVITIES[activity]

    return {
        "type": "muhurta_finder",
        "person_name": person_name,
        "activity": activity,
        "activity_name": activity_info["name"],
        "activity_name_hi": activity_info["name_hi"],
        "search_range": {
            "start_date": start_date,
            "end_date": end_dt.strftime("%Y-%m-%d"),
            "months": months_ahead,
        },
        "birth_details": {
            "nakshatra": birth_nakshatra,
            "moon_sign": birth_moon_sign,
        },
        "location": {
            "latitude": latitude,
            "longitude": longitude_geo,
            "timezone_offset_minutes": timezone_offset_minutes,
        },
        "total_days_scanned": total_days,
        "summary": {
            "excellent": len(excellent),
            "good": len(good),
            "average": len(average),
            "poor": len(poor),
            "total_found": len(all_dates),
        },
        "best_dates": all_dates[:20],
        "excellent_dates": excellent[:10],
        "good_dates": good[:10],
        "all_dates": all_dates,
    }
