"""
sbc_analysis.py — Advanced Sarvatobhadra Chakra Analysis Engine v3.5
Implements:
  • Vedha (obstruction aspects: row/column/diagonal)
  • Latta (planetary kicks on specific nakshatras)
  • Six Personal Bindus (Janma, Karma, Sanghatika, Uday, Adhan, Vinash)
  • Navatara system (9 tara categories from Janma nakshatra)
  • Transit SBC analysis with Shubha/Papa vedha quality
  • Planet-speed-based Vedha type (Dakshina/Vama/Prishtha)
  • Vedha line data for visual rendering in the UI
  • NSE/BSE market signal derived from SBC state
  • Ksheena Chandra — waning Moon becomes malefic (Shloka 55)
  • Krura-yukta Budha — Mercury conjunct malefic becomes malefic (Shloka 56)
  • Graha Bala — planet strength by sign + motion multipliers (Shlokas 161-167)
  • Dagdha/Jwalita/Dhumita — temporal vedha states (Shlokas 103-106)
  • Ubhayato Vedha — double-sided malefic vedha detection (Shloka 220)
  • 8 Upagraha sub-planets from Sun's nakshatra (Shlokas 250-260)
  • Commodity/Market vedha effects (Shlokas 245-246)
"""
from __future__ import annotations

import math
from typing import Dict, List, Optional, Tuple, Set

# ─────────────────────────────────────────────────────────────
# Planet average speeds (degrees/day) for Vedha type classification
# ─────────────────────────────────────────────────────────────
PLANET_AVG_SPEED: Dict[str, float] = {
    "Sun":     1.000,
    "Moon":    13.176,
    "Mars":    0.524,
    "Mercury": 1.383,
    "Jupiter": 0.083,
    "Venus":   1.200,
    "Saturn":  0.034,
    "Rahu":    0.053,
    "Ketu":    0.053,
}

# ─────────────────────────────────────────────────────────────
# Vedha Rules — per Khemraj Publishers book + Parashara's Light 9.0
# ─────────────────────────────────────────────────────────────
#
# Traditional Sarvatobhadra Chakra vedha rules from the Khemraj
# Publishers text (points 6–8):
#
# POINT 6 — ALL planets vedha in 3 directions (H + V + Diagonals)
#   "जिस नक्षत्र पर ग्रह रखा हो उस नक्षत्र स्थान से तीन ओर को वेध होता है"
#   Every planet vedhas in all 3 directions from its cell.
#
# POINT 7 — Sun/Moon/Rahu/Ketu always vedha in ALL 3 directions
#   "राहु तथा केतु सदा ही वक्री ओर सूर्य तथा चन्द्र सदा ही शीघ्रगामी
#    होने से इन ४ ग्रहो का वेध सदा तीनों ही ओर को एक सा होता है"
#   These 4 planets always hit full lines in every direction.
#
# POINT 8 — Front vedha hits NEAREST cell only; Left/Right hit full line
#   "दाहिनी ओर के वेध से तथा बाई ओर के वेध से तो जो अक्षरादि वेध
#    की सीध मे (लाइन मे) अवेगे उन सभी को वेध हो जाता है, परतु
#    सामने के वेध से केवल सामने के एक नक्षत्र को ही वेध होता है"
#   Right (दाहिनी) and Left (बाई) vedha → full line
#   Front (सामने) vedha → ONLY the nearest adjacent cell
#
# Speed classification (Parashara's Light 9.0):
#   दाहिनी / Right → Retrograde (Vakri)        → full half-lines
#   बाई / Left     → 25%+ faster (Sheeghra)    → full half-lines
#   सामने / Front  → Medium/normal (Madhya)    → nearest cell only
#   Sthana         → < 10% average (stationary) → full lines all dirs
#
# Sun/Moon always शीघ्रगामी → all 3 dirs active (full lines)
# Rahu/Ketu always वक्री     → all 3 dirs active (full lines)
# Mars/Mercury/Jupiter/Venus/Saturn → 1 of 3 dirs based on speed
# ─────────────────────────────────────────────────────────────

ALWAYS_FULL_VEDHA_PLANETS = {"Sun", "Moon", "Rahu", "Ketu"}
LEFT_VEDHA_THRESHOLD      = 1.25   # 25% faster than average
STATIONARY_THRESHOLD      = 0.10   # < 10% of average speed


def classify_vedha_type(planet: str, speed: float) -> Dict:
    """
    Classify Vedha direction per Khemraj book + Parashara's Light 9.0.

    ALL planets vedha in 3 directions (H + V + D1 + D2).
    The direction MODE determines reach:
      - Sun/Moon/Rahu/Ketu → always full lines, all directions
      - Others → speed decides:
          Sthana (stationary) → full lines, all directions, max strength
          Right (retrograde)  → full half-lines (right/down half)
          Left  (fast 25%+)   → full half-lines (left/up half)
          Front (medium)      → nearest adjacent cell only in each direction
    """
    avg = PLANET_AVG_SPEED.get(planet, 1.0)
    abs_speed = abs(speed)
    is_always_full = planet in ALWAYS_FULL_VEDHA_PLANETS

    # Sun/Moon/Rahu/Ketu: always full vedha in all directions
    if is_always_full:
        return {
            "type":         "3-Way Vedha",
            "description":  f"{planet} — always full 3-way vedha in all directions",
            "vedha_side":   "both",
            "vedha_mode":   "three_way",     # full lines, all dirs
            "strength":     "strong",
            "line_style":   "solid",
            "color_mod":    1.0,
            "is_three_way": True,
        }

    # Variable planets: classify by speed
    # Priority: Stationary > Retrograde > Fast > Normal (Front)
    if abs_speed < avg * STATIONARY_THRESHOLD:
        return {
            "type":         "Sthana Vedha",
            "description":  "Near-stationary — concentrated, maximum intensity vedha in all directions",
            "vedha_side":   "both",
            "vedha_mode":   "sthana",        # full lines, all dirs, max strength
            "strength":     "maximum",
            "line_style":   "double",
            "color_mod":    1.2,
            "is_three_way": True,
        }
    if speed < 0:
        return {
            "type":         "Right Vedha",
            "description":  "Retrograde (वक्री) — दाहिनी vedha; dviguna (2×) intensified",
            "vedha_side":   "right",
            "vedha_mode":   "right",         # dakshina direction
            "strength":     "intensified",
            "line_style":   "dashed",
            "color_mod":    1.5,             # retrograde = dviguna per Shloka 166
            "is_three_way": False,
        }
    if abs_speed > avg * LEFT_VEDHA_THRESHOLD:
        return {
            "type":         "Left Vedha",
            "description":  "Fast (शीघ्रगामी) — बाई vedha; svabhavaja natural strength",
            "vedha_side":   "left",
            "vedha_mode":   "left",          # vama direction
            "strength":     "normal",
            "line_style":   "solid",
            "color_mod":    1.0,
            "is_three_way": False,
        }
    # Front/Straight vedha — normal direct speed (madhya-gami)
    return {
        "type":         "Front Vedha",
        "description":  "Medium speed (मध्यगामी) — सामने vedha; only opposite nakshatra",
        "vedha_side":   "front",
        "vedha_mode":   "front",         # sammukha — only 1 nak opposite
        "strength":     "limited",
        "line_style":   "dotted",
        "color_mod":    0.8,
        "is_three_way": False,
    }


# Strength multipliers — affect scoring weight of vedha hits
# Per Shloka 166: Vakri (retrograde) = dviguna (2x), Shighra = svabhavaja (1x)
# Per Shloka 57: Krura+vakri = maha-krura, Saumya+vakri = maha-shubha
VEDHA_STRENGTH_MULTIPLIER: Dict[str, float] = {
    "Sthana Vedha":   2.0,   # Near-stationary = maximum concentrated power
    "3-Way Vedha":    1.3,   # Sun/Moon/Rahu/Ketu — always strong (sada vedha)
    "Right Vedha":    1.5,   # Retrograde (वक्री) — dviguna, intensified vedha
    "Left Vedha":     1.0,   # Fast (शीघ्र) — svabhavaja, natural strength
    "Front Vedha":    0.8,   # Medium (मध्यगामी) — only sammukha, limited reach
    "Standard Vedha": 1.0,   # Legacy fallback
}


# ═════════════════════════════════════════════════════════════
# ADVANCED SBC FEATURES — Khemraj Publishers book
# ═════════════════════════════════════════════════════════════


# ─────────────────────────────────────────────────────────────
# Ksheena Chandra (Shloka 55) — Waning Moon becomes malefic
# "कृष्ण पक्ष एकादशी से शुक्ल पक्ष पंचमी तक क्षीण चन्द्र
#  पापग्रह माना जाता है"
# Moon becomes malefic from Krishna Paksha 11 to Shukla Paksha 5
# ─────────────────────────────────────────────────────────────

def is_ksheena_chandra(moon_longitude: float, sun_longitude: float) -> Dict:
    """
    Check if Moon is Ksheena (waning/weak) per Shloka 55.
    Moon is malefic from Krishna Paksha Ekadashi (K11) to Shukla Paksha
    Panchami (S5).

    Tithi = (Moon - Sun) / 12, where each tithi = 12°.
    Shukla Paksha tithis 1-15 = tithi 1-15 (0°-180°)
    Krishna Paksha tithis 1-15 = tithi 16-30 (180°-360°)

    K11 = tithi 26 (300°), S5 = tithi 5 (60°)
    So malefic range: 300° to 60° (wrapping through 360°)
    """
    diff = (moon_longitude - sun_longitude) % 360.0
    tithi_num = int(diff / 12.0) + 1   # 1-30

    # Krishna Paksha 11 = tithi 26, to Shukla Paksha 5 = tithi 5
    # Malefic range: tithi 26-30 (K11 to Amavasya) + tithi 1-5 (S1 to S5)
    is_ksheena = tithi_num >= 26 or tithi_num <= 5

    # Determine paksha and tithi name
    if tithi_num <= 15:
        paksha = "Shukla"
        paksha_tithi = tithi_num
    else:
        paksha = "Krishna"
        paksha_tithi = tithi_num - 15

    return {
        "is_ksheena":   is_ksheena,
        "tithi_num":    tithi_num,
        "paksha":       paksha,
        "paksha_tithi": paksha_tithi,
        "moon_nature":  "malefic" if is_ksheena else "benefic",
        "description":  (f"Ksheena Chandra — {paksha} Paksha {paksha_tithi}, "
                        f"Moon is {'MALEFIC (क्षीण)' if is_ksheena else 'benefic (पूर्ण)'}"),
    }


# ─────────────────────────────────────────────────────────────
# Krura-yukta Budha (Shloka 56) — Mercury conjunct malefic
# "यदि बुध पाप ग्रह के साथ एक नवांश मे हो तो बुध भी
#  पापग्रह माना जाता है"
# Mercury becomes malefic when in same navamsha as a malefic
# ─────────────────────────────────────────────────────────────

def _get_navamsha_index(longitude: float) -> int:
    """
    Navamsha = 3°20' = 3.3333°. Each sign has 9 navamshas.
    Total 108 navamshas across the zodiac (12 signs × 9).
    Returns 0-107 navamsha index.
    """
    return int(longitude / (360.0 / 108.0)) % 108


def _krura_desc(is_krura: bool, conjunct: List[str], nav: int) -> str:
    if is_krura:
        return "Krura-yukta Budha — Mercury IS malefic (conjunct " + ", ".join(conjunct) + " in navamsha " + str(nav) + ")"
    return "Krura-yukta Budha — Mercury is benefic (no malefic conjunction in navamsha)"


def is_krura_yukta_budha(
    mercury_longitude: float,
    transit_planets: List[Dict],
) -> Dict:
    """
    Check if Mercury is Krura-yukta (conjunct malefic) per Shloka 56.
    Mercury becomes malefic when in the same navamsha as any malefic planet.

    Uses navamsha division (3°20' each, 108 total).
    """
    _CORE_MALEFICS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    merc_nav = _get_navamsha_index(mercury_longitude)

    conjunct_malefics = []
    for tp in transit_planets:
        if tp["planet"] in _CORE_MALEFICS:
            p_nav = _get_navamsha_index(tp["longitude"])
            if p_nav == merc_nav:
                conjunct_malefics.append(tp["planet"])

    is_krura = len(conjunct_malefics) > 0
    return {
        "is_krura_yukta":    is_krura,
        "mercury_navamsha":  merc_nav,
        "conjunct_malefics": conjunct_malefics,
        "mercury_nature":    "malefic" if is_krura else "benefic",
        "description":       _krura_desc(is_krura, conjunct_malefics, merc_nav),
    }


def classify_planet_nature(
    planet: str,
    transit_planets: List[Dict],
    moon_longitude: float = 0.0,
    sun_longitude: float = 0.0,
) -> Dict:
    """
    Dynamically classify a planet's nature (benefic/malefic) considering:
    - Ksheena Chandra (Shloka 55): waning Moon → malefic
    - Krura-yukta Budha (Shloka 56): Mercury + malefic navamsha → malefic
    - All other planets: static classification

    Returns dict with nature, reason, and detail info.
    """
    if planet == "Moon":
        kc = is_ksheena_chandra(moon_longitude, sun_longitude)
        return {
            "planet":  "Moon",
            "nature":  kc["moon_nature"],
            "reason":  "ksheena_chandra" if kc["is_ksheena"] else "normal",
            "detail":  kc,
        }

    if planet == "Mercury":
        merc_long = 0.0
        for tp in transit_planets:
            if tp["planet"] == "Mercury":
                merc_long = tp["longitude"]
                break
        kb = is_krura_yukta_budha(merc_long, transit_planets)
        return {
            "planet":  "Mercury",
            "nature":  kb["mercury_nature"],
            "reason":  "krura_yukta_budha" if kb["is_krura_yukta"] else "normal",
            "detail":  kb,
        }

    # Static classification for other planets
    _STATIC_BENEFIC = {"Jupiter", "Venus"}
    _STATIC_MALEFIC = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}
    if planet in _STATIC_BENEFIC:
        return {"planet": planet, "nature": "benefic", "reason": "inherent", "detail": {}}
    elif planet in _STATIC_MALEFIC:
        return {"planet": planet, "nature": "malefic", "reason": "inherent", "detail": {}}
    return {"planet": planet, "nature": "neutral", "reason": "unknown", "detail": {}}


# ─────────────────────────────────────────────────────────────
# Graha Bala for Vedha Strength (Shlokas 161-167)
# "ग्रह की बल — स्वराशि = 4/4, मित्र = 3/4, सम = 2/4, शत्रु = 1/4"
# Motion multipliers: retrograde=2×, exalted=3×, fast=1×, debilitated=0.5×
# ─────────────────────────────────────────────────────────────

# Sign lordships
SIGN_LORD: Dict[str, str] = {
    "Aries": "Mars", "Taurus": "Venus", "Gemini": "Mercury",
    "Cancer": "Moon", "Leo": "Sun", "Virgo": "Mercury",
    "Libra": "Venus", "Scorpio": "Mars", "Sagittarius": "Jupiter",
    "Capricorn": "Saturn", "Aquarius": "Saturn", "Pisces": "Jupiter",
}

# Natural friendships (Naisargika Maitri) per BPHS
NATURAL_FRIENDS: Dict[str, Set[str]] = {
    "Sun":     {"Moon", "Mars", "Jupiter"},
    "Moon":    {"Sun", "Mercury"},
    "Mars":    {"Sun", "Moon", "Jupiter"},
    "Mercury": {"Sun", "Venus"},
    "Jupiter": {"Sun", "Moon", "Mars"},
    "Venus":   {"Mercury", "Saturn"},
    "Saturn":  {"Mercury", "Venus"},
    "Rahu":    {"Mercury", "Venus", "Saturn"},
    "Ketu":    {"Mars", "Jupiter"},
}

NATURAL_ENEMIES: Dict[str, Set[str]] = {
    "Sun":     {"Venus", "Saturn"},
    "Moon":    set(),                    # Moon has no natural enemies
    "Mars":    {"Mercury"},
    "Mercury": {"Moon"},
    "Jupiter": {"Mercury", "Venus"},
    "Venus":   {"Sun", "Moon"},
    "Saturn":  {"Sun", "Moon", "Mars"},
    "Rahu":    {"Sun", "Moon", "Mars"},
    "Ketu":    {"Venus", "Mercury"},
}

# Exaltation / Debilitation signs
EXALTATION_SIGN: Dict[str, str] = {
    "Sun": "Aries", "Moon": "Taurus", "Mars": "Capricorn",
    "Mercury": "Virgo", "Jupiter": "Cancer", "Venus": "Pisces",
    "Saturn": "Libra", "Rahu": "Taurus", "Ketu": "Scorpio",
}
DEBILITATION_SIGN: Dict[str, str] = {
    "Sun": "Libra", "Moon": "Scorpio", "Mars": "Cancer",
    "Mercury": "Pisces", "Jupiter": "Capricorn", "Venus": "Virgo",
    "Saturn": "Aries", "Rahu": "Scorpio", "Ketu": "Taurus",
}

SIGNS_LIST = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]


def _get_sign_from_longitude(longitude: float) -> str:
    """Get zodiac sign from longitude (0-360)."""
    idx = int(longitude / 30.0) % 12
    return SIGNS_LIST[idx]


def _planet_sign_relation(planet: str, sign: str) -> str:
    """
    Determine relationship between planet and sign lord.
    Returns: 'own', 'friend', 'neutral', 'enemy'
    """
    lord = SIGN_LORD.get(sign, "")
    if lord == planet:
        return "own"
    friends = NATURAL_FRIENDS.get(planet, set())
    enemies = NATURAL_ENEMIES.get(planet, set())
    if lord in friends:
        return "friend"
    elif lord in enemies:
        return "enemy"
    return "neutral"


def calc_graha_bala(
    planet: str,
    longitude: float,
    speed: float,
    sign: str = "",
) -> Dict:
    """
    Calculate Graha Bala (planet strength) for vedha per Shlokas 161-167.

    Sign placement strength:
      Own sign   = 4/4 (1.0)
      Friend     = 3/4 (0.75)
      Neutral    = 2/4 (0.50)
      Enemy      = 1/4 (0.25)

    Motion multipliers:
      Exalted      = 3.0×
      Retrograde   = 2.0× (concentrated energy)
      Normal       = 1.0×
      Debilitated  = 0.5×

    Final graha_bala = sign_strength × motion_multiplier
    """
    if not sign:
        sign = _get_sign_from_longitude(longitude)

    # Sign placement strength
    relation = _planet_sign_relation(planet, sign)
    sign_strength_map = {"own": 1.0, "friend": 0.75, "neutral": 0.50, "enemy": 0.25}
    sign_strength = sign_strength_map.get(relation, 0.50)

    # Exaltation / Debilitation
    exalt_sign = EXALTATION_SIGN.get(planet, "")
    debil_sign = DEBILITATION_SIGN.get(planet, "")

    if sign == exalt_sign:
        motion_mult = 3.0
        motion_desc = "exalted (उच्च)"
    elif sign == debil_sign:
        motion_mult = 0.5
        motion_desc = "debilitated (नीच)"
    elif speed < 0:
        motion_mult = 2.0
        motion_desc = "retrograde (वक्री)"
    else:
        motion_mult = 1.0
        motion_desc = "direct (मार्गी)"

    graha_bala = sign_strength * motion_mult

    return {
        "planet":          planet,
        "sign":            sign,
        "sign_relation":   relation,
        "sign_strength":   sign_strength,
        "motion":          motion_desc,
        "motion_multiplier": motion_mult,
        "graha_bala":      round(graha_bala, 4),
        "graha_bala_label": (f"{planet} in {sign} ({relation}, {sign_strength:.0%}) × "
                             f"{motion_desc} ({motion_mult}×) = {graha_bala:.2f}"),
    }


# ─────────────────────────────────────────────────────────────
# Dagdha / Jwalita / Dhumita — Temporal Vedha States
# (Shlokas 103-106)
# "जो वेध हो चुका हो वह दग्ध (burnt), जो अभी हो रहा है वह
#  ज्वलित (burning), जो होने वाला है वह धूमित (smoking)"
# ─────────────────────────────────────────────────────────────

def classify_temporal_vedha(
    planet_nak_index: int,
    target_nak_index: int,
    speed: float,
    planet: str = "",
) -> Dict:
    """
    Classify vedha temporal state per Shlokas 103-106.

    The temporal state depends on whether the planet is approaching,
    currently at, or has passed the exact vedha point.

    Dagdha  (दग्ध)  = Past vedha — planet has already crossed → effect already occurred
    Jwalita (ज्वलित) = Current vedha — planet is at exact position → present effect (strongest)
    Dhumita (धूमित) = Future vedha — planet is approaching → coming effect (warning)

    For SBC: since vedha is based on nakshatra position on the grid,
    the temporal state is determined by the planet's speed direction
    relative to the target nakshatra index.
    """
    if planet_nak_index == target_nak_index:
        return {
            "state":       "jwalita",
            "state_hindi": "ज्वलित",
            "description": "Current vedha — burning (ज्वलित). Planet is AT exact vedha point. Maximum effect NOW.",
            "strength_mod": 1.5,   # Maximum effect
            "timing":      "present",
            "financial":   "Immediate market impact expected today/this session",
        }

    # Determine direction of motion
    if speed >= 0:
        # Direct motion: planet moves forward through nakshatras
        # If target is ahead → approaching (dhumita)
        # If target is behind → already passed (dagdha)
        forward_dist = (target_nak_index - planet_nak_index) % 27
        backward_dist = (planet_nak_index - target_nak_index) % 27

        if forward_dist <= 3:  # approaching — within 3 nakshatras ahead
            return {
                "state":       "dhumita",
                "state_hindi": "धूमित",
                "description": f"Future vedha — smoking (धूमित). Planet approaches vedha in ~{forward_dist} nakshatra(s). Effect building.",
                "strength_mod": 0.7 + (0.1 * (3 - forward_dist)),  # closer = stronger
                "timing":      "future",
                "financial":   f"Market impact building — expected in ~{forward_dist} day(s)",
            }
        elif backward_dist <= 3:  # just passed
            return {
                "state":       "dagdha",
                "state_hindi": "दग्ध",
                "description": f"Past vedha — burnt (दग्ध). Planet passed vedha {backward_dist} nakshatra(s) ago. Residual effect.",
                "strength_mod": 0.5 - (0.1 * backward_dist),  # further = weaker
                "timing":      "past",
                "financial":   f"Market impact fading — occurred ~{backward_dist} day(s) ago",
            }
    else:
        # Retrograde: planet moves backward
        backward_dist = (planet_nak_index - target_nak_index) % 27
        forward_dist = (target_nak_index - planet_nak_index) % 27

        if backward_dist <= 3:  # retrograde approaching
            return {
                "state":       "dhumita",
                "state_hindi": "धूमित",
                "description": f"Future vedha — smoking (धूमित). Retrograde planet approaches vedha in ~{backward_dist} nakshatra(s).",
                "strength_mod": 0.7 + (0.1 * (3 - backward_dist)),
                "timing":      "future",
                "financial":   f"Retrograde impact building — expected in ~{backward_dist} day(s)",
            }
        elif forward_dist <= 3:  # retrograde passed
            return {
                "state":       "dagdha",
                "state_hindi": "दग्ध",
                "description": f"Past vedha — burnt (दग्ध). Retrograde planet passed vedha {forward_dist} nakshatra(s) ago.",
                "strength_mod": 0.5 - (0.1 * forward_dist),
                "timing":      "past",
                "financial":   f"Retrograde impact fading — occurred ~{forward_dist} day(s) ago",
            }

    # Beyond range — no temporal state
    return {
        "state":       "none",
        "state_hindi": "—",
        "description": "No active temporal vedha state — planet is far from vedha point.",
        "strength_mod": 0.0,
        "timing":      "inactive",
        "financial":   "No immediate market impact from this vedha",
    }


# ─────────────────────────────────────────────────────────────
# 8 Upagraha Sub-Planets (Shlokas 250-260)
# Calculated from Sun's nakshatra position
# ─────────────────────────────────────────────────────────────

UPAGRAHA_OFFSETS: Dict[str, Dict] = {
    "Vidyunmukha": {"offset":  4, "nature": "malefic",
                    "effect": "Lightning-like sudden destruction; flash crashes",
                    "financial": "Sudden sharp market drops, volatility spikes"},
    "Shula":       {"offset":  7, "nature": "malefic",
                    "effect": "Piercing pain, chronic affliction",
                    "financial": "Sustained downward pressure, sector-specific damage"},
    "Sannipata":   {"offset": 13, "nature": "malefic",
                    "effect": "Combined disease, multiple afflictions",
                    "financial": "Multiple sectors affected simultaneously"},
    "Ketu-Upa":    {"offset": 17, "nature": "malefic",
                    "effect": "Tail/shadow affliction, hidden problems",
                    "financial": "Hidden risks surface, unexpected corrections"},
    "Ulka":        {"offset": 20, "nature": "malefic",
                    "effect": "Meteor-like impact, destructive force",
                    "financial": "Major market event, circuit breaker risk"},
    "Kampa":       {"offset": 21, "nature": "malefic",
                    "effect": "Trembling/earthquake, instability",
                    "financial": "Market tremors, institutional selling"},
    "Vajra":       {"offset": 22, "nature": "malefic",
                    "effect": "Thunderbolt destruction, supreme force",
                    "financial": "Severe market correction, gap-down opening"},
    "Nirghata":    {"offset": 23, "nature": "malefic",
                    "effect": "Catastrophic sound/shock, total destruction",
                    "financial": "Black swan event risk, panic selling"},
}


def calc_upagrahas(sun_nakshatra: str) -> List[Dict]:
    """
    Calculate 8 Upagraha positions from Sun's nakshatra per Shlokas 250-260.

    Offsets from Sun's nakshatra (0-based):
    Vidyunmukha=5th(+4), Shula=8th(+7), Sannipata=14th(+13),
    Ketu-upa=18th(+17), Ulka=21st(+20), Kampa=22nd(+21),
    Vajra=23rd(+22), Nirghata=24th(+23).

    All upagrahas are malefic and add affliction points.
    """
    sun_idx = NAK_INDEX.get(sun_nakshatra, 0)
    result = []

    for name, info in UPAGRAHA_OFFSETS.items():
        upa_idx = (sun_idx + info["offset"]) % 27
        upa_nak = NAKSHATRAS_27[upa_idx]
        result.append({
            "name":        name,
            "nakshatra":   upa_nak,
            "nak_index":   upa_idx,
            "offset_from_sun": info["offset"] + 1,  # 1-based as in texts
            "nature":      info["nature"],
            "effect":      info["effect"],
            "financial":   info["financial"],
        })

    return result


# ─────────────────────────────────────────────────────────────
# Commodity / Market Vedha Effects (Shlokas 245-246 + 126-152)
# "पापग्रह वेध से वस्तु महंगी, शुभग्रह वेध से सस्ती"
# ─────────────────────────────────────────────────────────────

PLANET_COMMODITY_EFFECTS: Dict[str, Dict] = {
    "Sun":     {"commodities": ["Gold", "Wheat", "Government bonds"],
                "malefic_effect": "Prices rise — scarcity, authority disruption",
                "benefic_effect": "N/A (always malefic)",
                "nse_sectors": ["PSU Banks", "Government companies", "Power"]},
    "Moon":    {"commodities": ["Silver", "Rice", "Water", "Dairy"],
                "malefic_effect": "Prices rise when Ksheena — consumer stress",
                "benefic_effect": "Prices stable/fall — consumer abundance",
                "nse_sectors": ["FMCG", "Consumer goods", "Hotels"]},
    "Mars":    {"commodities": ["Copper", "Red lentils", "Iron", "Real estate"],
                "malefic_effect": "Property disputes, metal prices surge",
                "benefic_effect": "N/A (always malefic)",
                "nse_sectors": ["Real Estate", "Metal", "Defense"]},
    "Mercury": {"commodities": ["Green gram", "Emerald", "IT services"],
                "malefic_effect": "IT sector correction when Krura-yukta",
                "benefic_effect": "IT/Commerce thriving, communication stocks up",
                "nse_sectors": ["IT", "Telecom", "Media"]},
    "Jupiter": {"commodities": ["Gold", "Turmeric", "Banking instruments"],
                "malefic_effect": "N/A (always benefic)",
                "benefic_effect": "Banking sector gains, prosperity, expansion",
                "nse_sectors": ["Banking", "Finance", "NBFCs"]},
    "Venus":   {"commodities": ["Diamond", "Sugar", "Cotton", "Luxury goods"],
                "malefic_effect": "N/A (always benefic)",
                "benefic_effect": "Luxury/entertainment thriving, sugar prices stable",
                "nse_sectors": ["Auto", "Luxury", "Entertainment", "Sugar"]},
    "Saturn":  {"commodities": ["Iron", "Oil", "Coal", "Mustard"],
                "malefic_effect": "Chronic pressure on oil/infra, sustained bear",
                "benefic_effect": "N/A (always malefic)",
                "nse_sectors": ["Oil & Gas", "Infrastructure", "Mining"]},
    "Rahu":    {"commodities": ["Foreign goods", "Electronics", "Pharma"],
                "malefic_effect": "Tech crash risk, foreign market contagion",
                "benefic_effect": "N/A (always malefic)",
                "nse_sectors": ["Tech", "Pharma", "Foreign-linked"]},
    "Ketu":    {"commodities": ["Chemicals", "Pharma", "Spiritual goods"],
                "malefic_effect": "Pharma/chemical sector uncertainty, reversals",
                "benefic_effect": "N/A (always malefic)",
                "nse_sectors": ["Pharma", "Chemicals", "Fertilizers"]},
}

# Per-entity vedha effects (Shlokas 107-125)
ENTITY_VEDHA_EFFECTS: Dict[str, Dict] = {
    "nakshatra": {
        "effect": "Confusion, mental turmoil (भ्रांति)",
        "financial": "Market confusion, unclear trend, avoid trading",
        "severity_mod": 1.0,
    },
    "akshara": {
        "effect": "Financial loss, damage (हानि)",
        "financial": "Direct financial loss, stock-specific drop",
        "severity_mod": 1.2,
    },
    "svara": {
        "effect": "Disease, health issues (रोग)",
        "financial": "Sector weakness, gradual decline",
        "severity_mod": 0.8,
    },
    "tithi": {
        "effect": "Fear, anxiety (भय)",
        "financial": "Market fear, VIX spike, panic selling",
        "severity_mod": 1.1,
    },
    "rashi": {
        "effect": "Great obstacle, major impediment (महा विघ्न)",
        "financial": "Major market obstacle, regulatory action, circuit breaker",
        "severity_mod": 1.5,
    },
    "vara": {
        "effect": "Disruption of daily routine (दिन विघ्न)",
        "financial": "Day-specific volatility",
        "severity_mod": 0.7,
    },
}


# ─────────────────────────────────────────────────────────────
# Ubhayato Vedha — Double-sided malefic vedha (Shloka 220)
# "जब दो पापग्रह दोनों ओर से वेध करें तो अत्यंत विनाश"
# When TWO malefic planets vedha from both sides → extreme danger
# ─────────────────────────────────────────────────────────────

def detect_ubhayato_vedha(
    all_vedha_hits: List[Dict],
    transit_planets: List[Dict],
    planet_natures: Dict[str, str],
) -> List[Dict]:
    """
    Detect Ubhayato Vedha (double-sided malefic vedha) per Shloka 220.

    When TWO or more malefic planets vedha the same entity from opposite
    sides (directions), it indicates maximum danger/destruction.

    For financial astrology: This is the strongest bearish signal.
    """
    # Group vedha hits by target entity
    entity_vedhas: Dict[str, List[Dict]] = {}
    for vh in all_vedha_hits:
        entity = vh.get("to_entity", "")
        if not entity:
            continue
        if entity not in entity_vedhas:
            entity_vedhas[entity] = []
        entity_vedhas[entity].append(vh)

    ubhayato_list = []

    for entity, hits in entity_vedhas.items():
        # Filter to malefic-only hits
        malefic_hits = [h for h in hits
                        if planet_natures.get(h["planet"], "malefic") == "malefic"]

        if len(malefic_hits) < 2:
            continue

        # Check for opposite directions
        directions = {h.get("vedha_direction", "") for h in malefic_hits}
        opposite_pairs = [
            ("horizontal", "vertical"),
            ("diagonal_main", "diagonal_anti"),
        ]
        # Also check same-axis opposite sides
        has_opposite = False
        for d1, d2 in opposite_pairs:
            if d1 in directions and d2 in directions:
                has_opposite = True
                break

        # Even 2+ malefics from same direction is a strong signal
        if len(malefic_hits) >= 2:
            planets_involved = list({h["planet"] for h in malefic_hits})
            severity = "EXTREME" if has_opposite else "SEVERE"
            ubhayato_list.append({
                "entity":           entity,
                "malefic_count":    len(malefic_hits),
                "planets":          planets_involved,
                "directions":       sorted(directions),
                "is_true_ubhayato": has_opposite,
                "severity":         severity,
                "description":      (f"{'Ubhayato Vedha (उभयतो वेध)' if has_opposite else 'Multi-malefic Vedha'}: "
                                     f"{', '.join(planets_involved)} vedha '{entity}' — "
                                     f"{'OPPOSITE sides → MAXIMUM destruction' if has_opposite else 'same-side concentration → severe affliction'}"),
                "financial":        (f"EXTREME BEARISH — {entity} under multi-malefic vedha. "
                                     f"{'Double-sided attack = circuit breaker risk' if has_opposite else 'Concentrated malefic pressure = sustained decline'}"),
            })

    return sorted(ubhayato_list, key=lambda x: x["malefic_count"], reverse=True)


# ─────────────────────────────────────────────────────────────
# Per-Nakshatra Vedha Map (Shlokas 19-47)
# Authoritative vedha targets for each nakshatra from each direction.
# This maps which entities are vedha'd when a planet transits a
# specific nakshatra, from each of the 3 directions.
# Key: nakshatra → {"vama": [...], "dakshina": [...], "sammukha": [...]}
# ─────────────────────────────────────────────────────────────

# NOTE: This is a partial map based on the extractable text from the
# Khemraj Publishers book. The complete map requires all 28 nakshatra
# entries from Shlokas 19-47. Geometric line intersection is still
# used as fallback for nakshatras not in this map.

PER_NAKSHATRA_VEDHA_TARGETS: Dict[str, Dict[str, List[str]]] = {
    # Each nakshatra maps to its specific vedha targets per direction
    # vama (left/बाई), dakshina (right/दाहिनी), sammukha (front/सामने)
    # These are the entities (nakshatras, rashis, tithis, aksharas) that
    # are hit from each direction.
    # Populated from the book's shloka-by-shloka vedha enumeration.
    # Format: {"vama": [target_entities], "dakshina": [...], "sammukha": [...]}

    # Ashwini (Shloka 19-20)
    "Ashwini": {
        "vama":      ["Bharani", "Krittika", "Rohini", "Mrigashira"],
        "dakshina":  ["Revati", "Uttara Bhadrapada", "Purva Bhadrapada"],
        "sammukha":  ["Ashlesha"],
    },
    # Bharani (Shloka 21)
    "Bharani": {
        "vama":      ["Krittika", "Rohini", "Mrigashira", "Ardra"],
        "dakshina":  ["Ashwini", "Revati", "Uttara Bhadrapada"],
        "sammukha":  ["Pushya"],
    },
    # Krittika
    "Krittika": {
        "vama":      ["Rohini", "Mrigashira", "Ardra", "Punarvasu"],
        "dakshina":  ["Bharani", "Ashwini", "Revati"],
        "sammukha":  ["Punarvasu"],
    },
    # Rohini
    "Rohini": {
        "vama":      ["Mrigashira", "Ardra", "Punarvasu", "Pushya"],
        "dakshina":  ["Krittika", "Bharani", "Ashwini"],
        "sammukha":  ["Magha"],
    },
    # Mrigashira
    "Mrigashira": {
        "vama":      ["Ardra", "Punarvasu", "Pushya", "Ashlesha"],
        "dakshina":  ["Rohini", "Krittika", "Bharani"],
        "sammukha":  ["Purva Phalguni"],
    },
    # Ardra
    "Ardra": {
        "vama":      ["Punarvasu", "Pushya", "Ashlesha", "Magha"],
        "dakshina":  ["Mrigashira", "Rohini", "Krittika"],
        "sammukha":  ["Uttara Phalguni"],
    },
    # Punarvasu
    "Punarvasu": {
        "vama":      ["Pushya", "Ashlesha", "Magha", "Purva Phalguni"],
        "dakshina":  ["Ardra", "Mrigashira", "Rohini"],
        "sammukha":  ["Hasta"],
    },
    # Pushya
    "Pushya": {
        "vama":      ["Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni"],
        "dakshina":  ["Punarvasu", "Ardra", "Mrigashira"],
        "sammukha":  ["Chitra"],
    },
    # Ashlesha
    "Ashlesha": {
        "vama":      ["Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta"],
        "dakshina":  ["Pushya", "Punarvasu", "Ardra"],
        "sammukha":  ["Swati"],
    },
    # Magha
    "Magha": {
        "vama":      ["Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra"],
        "dakshina":  ["Ashlesha", "Pushya", "Punarvasu"],
        "sammukha":  ["Vishakha"],
    },
    # Purva Phalguni
    "Purva Phalguni": {
        "vama":      ["Uttara Phalguni", "Hasta", "Chitra", "Swati"],
        "dakshina":  ["Magha", "Ashlesha", "Pushya"],
        "sammukha":  ["Anuradha"],
    },
    # Uttara Phalguni
    "Uttara Phalguni": {
        "vama":      ["Hasta", "Chitra", "Swati", "Vishakha"],
        "dakshina":  ["Purva Phalguni", "Magha", "Ashlesha"],
        "sammukha":  ["Jyeshtha"],
    },
    # Hasta
    "Hasta": {
        "vama":      ["Chitra", "Swati", "Vishakha", "Anuradha"],
        "dakshina":  ["Uttara Phalguni", "Purva Phalguni", "Magha"],
        "sammukha":  ["Mula"],
    },
    # Chitra
    "Chitra": {
        "vama":      ["Swati", "Vishakha", "Anuradha", "Jyeshtha"],
        "dakshina":  ["Hasta", "Uttara Phalguni", "Purva Phalguni"],
        "sammukha":  ["Purva Ashadha"],
    },
    # Swati
    "Swati": {
        "vama":      ["Vishakha", "Anuradha", "Jyeshtha", "Mula"],
        "dakshina":  ["Chitra", "Hasta", "Uttara Phalguni"],
        "sammukha":  ["Uttara Ashadha"],
    },
    # Vishakha
    "Vishakha": {
        "vama":      ["Anuradha", "Jyeshtha", "Mula", "Purva Ashadha"],
        "dakshina":  ["Swati", "Chitra", "Hasta"],
        "sammukha":  ["Shravana"],
    },
    # Anuradha
    "Anuradha": {
        "vama":      ["Jyeshtha", "Mula", "Purva Ashadha", "Uttara Ashadha"],
        "dakshina":  ["Vishakha", "Swati", "Chitra"],
        "sammukha":  ["Dhanishtha"],
    },
    # Jyeshtha
    "Jyeshtha": {
        "vama":      ["Mula", "Purva Ashadha", "Uttara Ashadha", "Shravana"],
        "dakshina":  ["Anuradha", "Vishakha", "Swati"],
        "sammukha":  ["Shatabhisha"],
    },
    # Mula
    "Mula": {
        "vama":      ["Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishtha"],
        "dakshina":  ["Jyeshtha", "Anuradha", "Vishakha"],
        "sammukha":  ["Purva Bhadrapada"],
    },
    # Purva Ashadha
    "Purva Ashadha": {
        "vama":      ["Uttara Ashadha", "Shravana", "Dhanishtha", "Shatabhisha"],
        "dakshina":  ["Mula", "Jyeshtha", "Anuradha"],
        "sammukha":  ["Uttara Bhadrapada"],
    },
    # Uttara Ashadha
    "Uttara Ashadha": {
        "vama":      ["Shravana", "Dhanishtha", "Shatabhisha", "Purva Bhadrapada"],
        "dakshina":  ["Purva Ashadha", "Mula", "Jyeshtha"],
        "sammukha":  ["Revati"],
    },
    # Shravana
    "Shravana": {
        "vama":      ["Dhanishtha", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada"],
        "dakshina":  ["Uttara Ashadha", "Purva Ashadha", "Mula"],
        "sammukha":  ["Ashwini"],
    },
    # Dhanishtha
    "Dhanishtha": {
        "vama":      ["Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"],
        "dakshina":  ["Shravana", "Uttara Ashadha", "Purva Ashadha"],
        "sammukha":  ["Bharani"],
    },
    # Shatabhisha
    "Shatabhisha": {
        "vama":      ["Purva Bhadrapada", "Uttara Bhadrapada", "Revati", "Ashwini"],
        "dakshina":  ["Dhanishtha", "Shravana", "Uttara Ashadha"],
        "sammukha":  ["Krittika"],
    },
    # Purva Bhadrapada
    "Purva Bhadrapada": {
        "vama":      ["Uttara Bhadrapada", "Revati", "Ashwini", "Bharani"],
        "dakshina":  ["Shatabhisha", "Dhanishtha", "Shravana"],
        "sammukha":  ["Rohini"],
    },
    # Uttara Bhadrapada
    "Uttara Bhadrapada": {
        "vama":      ["Revati", "Ashwini", "Bharani", "Krittika"],
        "dakshina":  ["Purva Bhadrapada", "Shatabhisha", "Dhanishtha"],
        "sammukha":  ["Mrigashira"],
    },
    # Revati
    "Revati": {
        "vama":      ["Ashwini", "Bharani", "Krittika", "Rohini"],
        "dakshina":  ["Uttara Bhadrapada", "Purva Bhadrapada", "Shatabhisha"],
        "sammukha":  ["Ardra"],
    },
}


def get_per_nakshatra_vedha_targets(
    planet_nakshatra: str,
    vedha_mode: str,
) -> Optional[List[str]]:
    """
    Get authoritative vedha targets for a planet in a specific nakshatra,
    using the per-nakshatra vedha map from Shlokas 19-47.

    vedha_mode: "three_way"/"sthana" → all 3 directions
                "left" → vama targets only
                "right" → dakshina targets only
                "front" → sammukha targets only

    Returns None if nakshatra is not in the map (fallback to geometric).
    """
    targets = PER_NAKSHATRA_VEDHA_TARGETS.get(planet_nakshatra)
    if not targets:
        return None

    if vedha_mode in ("three_way", "sthana"):
        # All 3 directions
        all_targets = list(set(
            targets.get("vama", []) +
            targets.get("dakshina", []) +
            targets.get("sammukha", [])
        ))
        return all_targets
    elif vedha_mode == "left":
        return targets.get("vama", [])
    elif vedha_mode == "right":
        return targets.get("dakshina", [])
    elif vedha_mode == "front":
        return targets.get("sammukha", [])

    return None


# ─────────────────────────────────────────────────────────────
# Nakshatra sequence (0-indexed, Ashwini=0 … Revati=26)
# ─────────────────────────────────────────────────────────────
NAKSHATRAS_27: List[str] = [
    "Ashwini","Bharani","Krittika","Rohini","Mrigashira","Ardra",
    "Punarvasu","Pushya","Ashlesha","Magha","Purva Phalguni",
    "Uttara Phalguni","Hasta","Chitra","Swati","Vishakha",
    "Anuradha","Jyeshtha","Mula","Purva Ashadha","Uttara Ashadha",
    "Shravana","Dhanishtha","Shatabhisha","Purva Bhadrapada",
    "Uttara Bhadrapada","Revati",
]
NAK_INDEX: Dict[str, int] = {n: i for i, n in enumerate(NAKSHATRAS_27)}

# Abhijit is the special 28th; treat as equivalent to Uttara Ashadha for counting
_ABHIJIT_EQUIV = "Uttara Ashadha"


def _nak_idx(name: str) -> int:
    if name == "Abhijit":
        name = _ABHIJIT_EQUIV
    return NAK_INDEX.get(name, 0)


def nak_at_offset(from_nak: str, offset: int, direction: str = "forward") -> str:
    """
    Return the nakshatra at `offset` positions from `from_nak`.
    direction: 'forward' (increasing index) or 'backward' (decreasing).
    Offset is 0-based (offset=0 returns from_nak itself).
    """
    idx = _nak_idx(from_nak)
    if direction == "forward":
        return NAKSHATRAS_27[(idx + offset) % 27]
    else:
        return NAKSHATRAS_27[(idx - offset) % 27]


# ─────────────────────────────────────────────────────────────
# Navatara — 9 Tara categories from Janma Nakshatra
# ─────────────────────────────────────────────────────────────
NAVATARA_DEF: List[Tuple[str, str, str]] = [
    ("Janma",      "neutral",      "Birth star — sensitive, pivotal"),
    ("Sampat",     "auspicious",   "Prosperity — favorable transits"),
    ("Vipat",      "inauspicious", "Obstacle/danger — beware"),
    ("Kshema",     "auspicious",   "Welfare — good transits"),
    ("Pratyari",   "inauspicious", "Enemy star — unfavorable"),
    ("Sadhaka",    "auspicious",   "Achievement — success"),
    ("Naidhana",   "inauspicious", "Death/destruction — avoid"),
    ("Mitra",      "auspicious",   "Friend star — beneficial"),
    ("Adhi Mitra", "auspicious",   "Best friend — most favorable"),
]


def calc_navatara(janma_nak: str) -> Dict[str, Dict]:
    """
    For each of the 27 nakshatras, return its Tara relationship
    to the Janma Nakshatra.
    """
    result: Dict[str, Dict] = {}
    j = _nak_idx(janma_nak)
    for i, nak in enumerate(NAKSHATRAS_27):
        dist = (i - j) % 27           # 0-based offset from janma
        tara_idx = dist % 9           # which of the 9 taras
        name, quality, desc = NAVATARA_DEF[tara_idx]
        result[nak] = {
            "tara":        name,
            "quality":     quality,
            "description": desc,
            "offset_from_janma": dist + 1,   # 1-based as in texts
        }
    return result


# ─────────────────────────────────────────────────────────────
# Six Personal Bindus (identifiers) from Janma Nakshatra
# ─────────────────────────────────────────────────────────────
SIX_BINDUS_DEF: Dict[str, int] = {
    "Janma":      0,   # 1st  (Moon's natal nakshatra)
    "Karma":      9,   # 10th
    "Sanghatika": 15,  # 16th
    "Uday":       17,  # 18th
    "Adhan":      18,  # 19th
    "Vinash":     22,  # 23rd
}


def calc_six_bindus(janma_nak: str) -> Dict[str, Dict]:
    """Return the six personal bindus (sensitive nakshatras) from Janma."""
    result: Dict[str, Dict] = {}
    for bindu_name, offset in SIX_BINDUS_DEF.items():
        nak = nak_at_offset(janma_nak, offset, "forward")
        result[bindu_name] = {
            "nakshatra":   nak,
            "offset":      offset + 1,
            "description": _BINDU_DESC[bindu_name],
        }
    return result


_BINDU_DESC: Dict[str, str] = {
    "Janma":      "Moon's birth nakshatra — most sensitive personal point",
    "Karma":      "10th from Janma — career and action axis",
    "Sanghatika": "16th from Janma — collective/community karma",
    "Uday":       "18th from Janma — rising/manifestation point",
    "Adhan":      "19th from Janma — conception nakshatra",
    "Vinash":     "23rd from Janma — danger/destruction point",
}


# ─────────────────────────────────────────────────────────────
# Vedha Line Data for UI Rendering
# Returns the start/end grid coordinates for every vedha line
# ─────────────────────────────────────────────────────────────

def get_vedha_lines(
    planet_name: str,
    row: int,
    col: int,
    speed: float,
    grid_size: int = 9,
) -> Dict:
    """
    Return vedha line segments for a planet at (row, col).
    Per Khemraj Publishers traditional SBC rules:

    Sun/Moon/Rahu/Ketu (3-Way) = ALL 3 directions:
      D1 (main diagonal) + D2 (anti diagonal) + Sammukha (H or V straight line)
      "सूर्य तथा चन्द्र सदा ही शीघ्रगामी होने से इन ४ ग्रहो का वेध
       सदा तीनों ही ओर को एक सा होता है"

    Mars/Mercury/Jupiter/Venus/Saturn (variable) = DIAGONALS ONLY:
      D1 + D2 (no H/V straight lines). Speed determines reach:
      Sthana (stationary) → full diagonals, max strength
      Right  (retrograde) → half-diagonals right/down
      Left   (fast 25%+)  → half-diagonals left/up
      Front  (normal)     → nearest diagonal neighbor only
    """
    vedha_info   = classify_vedha_type(planet_name, speed)
    vedha_mode   = vedha_info["vedha_mode"]   # "three_way","sthana","left","right","front"
    vedha_side   = vedha_info["vedha_side"]   # "both","left","right","front"
    last         = grid_size - 1
    is_always_full = planet_name in ALWAYS_FULL_VEDHA_PLANETS

    lines: List[Dict] = []

    if vedha_mode == "front":
        # ── FRONT VEDHA — nearest diagonal neighbor only ──────
        # Only for variable planets (Mars/Mercury/Jupiter/Venus/Saturn)

        # Diagonal ↘: top-left and bottom-right neighbors
        if row > 0 and col > 0:
            lines.append({"type": "diagonal_main", "from": [row - 1, col - 1], "to": [row, col]})
        if row < last and col < last:
            lines.append({"type": "diagonal_main", "from": [row, col], "to": [row + 1, col + 1]})
        # Diagonal ↗: top-right and bottom-left neighbors
        if row > 0 and col < last:
            lines.append({"type": "diagonal_anti", "from": [row - 1, col + 1], "to": [row, col]})
        if row < last and col > 0:
            lines.append({"type": "diagonal_anti", "from": [row, col], "to": [row + 1, col - 1]})

    else:
        # ── FULL / HALF DIAGONALS ────────────────────────────

        # ── Diagonal ↘ (main) ───────────────────────────────
        step_tl = min(row, col)
        d1_r0, d1_c0 = row - step_tl, col - step_tl
        step_br = min(last - row, last - col)
        d1_r1, d1_c1 = row + step_br, col + step_br

        if vedha_side == "left":
            d1_line = {"type": "diagonal_main", "from": [d1_r0, d1_c0], "to": [row, col]}
        elif vedha_side == "right":
            d1_line = {"type": "diagonal_main", "from": [row, col], "to": [d1_r1, d1_c1]}
        else:
            d1_line = {"type": "diagonal_main", "from": [d1_r0, d1_c0], "to": [d1_r1, d1_c1]}
        lines.append(d1_line)

        # ── Diagonal ↗ (anti) ───────────────────────────────
        step_tr = min(row, last - col)
        d2_r0, d2_c0 = row - step_tr, col + step_tr
        step_bl = min(last - row, col)
        d2_r1, d2_c1 = row + step_bl, col - step_bl

        if vedha_side == "left":
            d2_line = {"type": "diagonal_anti", "from": [d2_r0, d2_c0], "to": [row, col]}
        elif vedha_side == "right":
            d2_line = {"type": "diagonal_anti", "from": [row, col], "to": [d2_r1, d2_c1]}
        else:
            d2_line = {"type": "diagonal_anti", "from": [d2_r0, d2_c0], "to": [d2_r1, d2_c1]}
        lines.append(d2_line)

        # ── Sammukha / Straight line — ONLY for Sun/Moon/Rahu/Ketu ──
        # These 4 planets always vedha in ALL 3 directions including
        # the straight line (horizontal or vertical through their cell)
        if is_always_full:
            # Horizontal full line
            lines.append({"type": "horizontal", "from": [row, 0], "to": [row, last]})
            # Vertical full line
            lines.append({"type": "vertical", "from": [0, col], "to": [last, col]})

    strength_mult = VEDHA_STRENGTH_MULTIPLIER.get(vedha_info["type"], 1.0)

    # Direction list
    active_dirs = ["diagonal1", "diagonal2"]
    if is_always_full and vedha_mode != "front":
        active_dirs.extend(["horizontal", "vertical"])

    return {
        "planet":              planet_name,
        "position":            [row, col],
        "speed":               round(speed, 4),
        "vedha_type":          vedha_info["type"],
        "vedha_mode":          vedha_mode,
        "vedha_side":          vedha_side,
        "is_three_way":        True,
        "strength":            vedha_info["strength"],
        "strength_multiplier": strength_mult,
        "line_style":          vedha_info["line_style"],
        "description":         vedha_info["description"],
        "active_directions":   active_dirs,
        "lines":               lines,
    }


# ─────────────────────────────────────────────────────────────
# Latta — Planetary Kicks
# Rules: the transiting planet "kicks" a nakshatra at a fixed
# offset. If the kicked nakshatra is a personal bindu or Janma,
# the native feels the latta effect.
# ─────────────────────────────────────────────────────────────
LATTA_RULES: Dict[str, Tuple[str, int]] = {
    # Traditional Vedic counting is INCLUSIVE (planet's own star = 1st)
    # So "nth nakshatra from planet" = offset of (n-1) in 0-based index
    "Sun":     ("forward",   11),   # 12th forward (inclusive) = +11
    "Mars":    ("forward",    2),   # 3rd forward  (inclusive) = +2
    "Jupiter": ("forward",    5),   # 6th forward  (inclusive) = +5
    "Saturn":  ("forward",    7),   # 8th forward  (inclusive) = +7
    "Venus":   ("backward",   4),   # 5th backward (inclusive) = -4
    "Mercury": ("backward",   6),   # 7th backward (inclusive) = -6
    "Rahu":    ("backward",   8),   # 9th backward (inclusive) = -8
    "Ketu":    ("backward",   8),   # 9th backward (inclusive) = -8
    "Moon":    ("backward",  21),   # 22nd backward (inclusive) = -21
}

LATTA_EFFECTS: Dict[str, str] = {
    "Sun":     "Financial loss in every venture; setbacks from authority",
    "Moon":    "Excessive financial loss; emotional disturbances",
    "Mars":    "Wounds, injuries, property disputes, impulsive losses",
    "Mercury": "Loss of position, status, and reputation",
    "Jupiter": "Loss of wisdom, prestige, and good fortune",
    "Venus":   "Quarrels, discord, relationship disruptions",
    "Saturn":  "Disease, sorrow, chronic delays, legal issues",
    "Rahu":    "Grief, unhappiness, deception, unexpected shocks",
    "Ketu":    "Confusion, accidents, hidden problems, isolation",
}

LATTA_FINANCIAL: Dict[str, str] = {
    "Sun":     "PSU/Govt stocks impacted; avoid large trades",
    "Moon":    "Consumer/FMCG stocks down; market emotionally weak",
    "Mars":    "Defense/Real estate sector under pressure",
    "Mercury": "IT/Telecom sector underperformance expected",
    "Jupiter": "Banking/Finance sector risk; avoid long positions",
    "Venus":   "FMCG/Luxury sector volatile",
    "Saturn":  "Infrastructure/Oil under sustained pressure",
    "Rahu":    "Tech/Foreign stocks crash risk",
    "Ketu":    "Pharma/Chemicals sector uncertain",
}


def calc_latta_for_planet(
    planet_name: str,
    transiting_nak: str,
    retrograde: bool = False,
) -> Dict:
    """
    Calculate which nakshatra this planet is currently kicking (Latta).
    Retrograde planets reverse their Latta direction.
    """
    if planet_name not in LATTA_RULES:
        return {}
    direction, offset = LATTA_RULES[planet_name]
    # Retrograde reverses direction
    if retrograde:
        direction = "backward" if direction == "forward" else "forward"

    kicked_nak = nak_at_offset(transiting_nak, offset, direction)
    return {
        "planet":       planet_name,
        "transiting":   transiting_nak,
        "latta_offset": offset,
        "direction":    direction,
        "kicked_nakshatra": kicked_nak,
        "effect":       LATTA_EFFECTS.get(planet_name, ""),
        "nse_impact":   LATTA_FINANCIAL.get(planet_name, ""),
        "retrograde":   retrograde,
    }


# ─────────────────────────────────────────────────────────────
# Vedha — Grid Aspects
# Each cell (row, col) vedhas (aspects):
#   • Its entire row (horizontal)
#   • Its entire column (vertical)
#   • Both diagonals through it
# ─────────────────────────────────────────────────────────────
BENEFIC_PLANETS = {"Jupiter", "Venus", "Mercury", "Moon"}
MALEFIC_PLANETS = {"Sun", "Mars", "Saturn", "Rahu", "Ketu"}

VEDHA_EFFECTS: Dict[str, str] = {
    "Sun":     "Grief, sorrow, setbacks from authority",
    "Moon":    "Mixed results — both good and bad",
    "Mars":    "Loss of wealth, property damage, disputes",
    "Mercury": "Sharpening of intellect, mental activity",
    "Jupiter": "Many gains, good happenings, prosperity",
    "Venus":   "Fear from enemies, relationship issues",
    "Saturn":  "Pain, chronic ailments, prolonged obstacles",
    "Rahu":    "Obstructions, sudden shocks, deception",
    "Ketu":    "Confusion, accidents, spiritual disruption",
}

VEDHA_MULTIPLE_EFFECTS: Dict[int, str] = {
    1: "Conflict and misunderstanding",
    2: "Loss of wealth and financial setbacks",
    3: "Defeat or significant failure",
    4: "Severe consequences — maximum caution",
}

VEDHA_FINANCIAL: Dict[str, Dict] = {
    "Jupiter": {"signal": "BULLISH", "score":  0.7, "impact": "Banking/Finance gains"},
    "Venus":   {"signal": "BULLISH", "score":  0.6, "impact": "FMCG/Luxury sector gains"},
    "Mercury": {"signal": "BULLISH", "score":  0.5, "impact": "IT/Commerce sector active"},
    "Moon":    {"signal": "NEUTRAL", "score":  0.3, "impact": "Consumer sentiment mixed"},
    "Sun":     {"signal": "CAUTION", "score": -0.2, "impact": "PSU sector under pressure"},
    "Mars":    {"signal": "BEARISH", "score": -0.5, "impact": "Market energy disrupted"},
    "Saturn":  {"signal": "BEARISH", "score": -0.4, "impact": "Structural market slowdown"},
    "Rahu":    {"signal": "BEARISH", "score": -0.6, "impact": "Tech/Foreign stocks volatile"},
    "Ketu":    {"signal": "BEARISH", "score": -0.5, "impact": "Pharma/Chemicals uncertain"},
}


def get_vedha_cells(
    row: int,
    col: int,
    grid_size: int = 9,
    planet: str = "",
    speed: float = 1.0,
) -> Dict[str, List[Tuple[int,int]]]:
    """
    Return cells under vedha from position (row, col).
    Per Khemraj Publishers SBC rules:

    Sun/Moon/Rahu/Ketu (3-Way) = D1 + D2 + H + V (all 3 directions + straight)
    Variable planets = D1 + D2 only (diagonals, no H/V)

    The vedha MODE determines which cells are hit:
      3-Way   → full diagonals + full H/V (Sun/Moon/Rahu/Ketu only)
      Sthana  → full diagonals (variable planets, stationary)
      Left    → half-diagonals top-left (fast planets)
      Right   → half-diagonals bottom-right (retrograde)
      Front   → nearest diagonal neighbor only (normal speed)
    """
    vedha_info = classify_vedha_type(planet, speed)
    vedha_mode = vedha_info["vedha_mode"]
    vedha_side = vedha_info["vedha_side"]
    is_always_full = planet in ALWAYS_FULL_VEDHA_PLANETS

    # H/V only for Sun/Moon/Rahu/Ketu (3-way planets)
    horizontal = []
    vertical   = []

    if vedha_mode == "front":
        # ── FRONT VEDHA — nearest diagonal neighbor only ─────
        diag1 = []
        diag2 = []
        if row > 0 and col > 0:
            diag1.append((row - 1, col - 1))
        if row < grid_size - 1 and col < grid_size - 1:
            diag1.append((row + 1, col + 1))
        if row > 0 and col < grid_size - 1:
            diag2.append((row - 1, col + 1))
        if row < grid_size - 1 and col > 0:
            diag2.append((row + 1, col - 1))
    else:
        # ── DIAGONALS (all non-front modes) ──────────────────

        # Diagonal 1: ↘ main diagonal
        diag1 = []
        if vedha_side in ("left", "both"):
            r, c = row - 1, col - 1
            while r >= 0 and c >= 0:
                diag1.append((r, c)); r -= 1; c -= 1
        if vedha_side in ("right", "both"):
            r, c = row + 1, col + 1
            while r < grid_size and c < grid_size:
                diag1.append((r, c)); r += 1; c += 1

        # Diagonal 2: ↗ anti diagonal
        diag2 = []
        if vedha_side in ("left", "both"):
            r, c = row - 1, col + 1
            while r >= 0 and c < grid_size:
                diag2.append((r, c)); r -= 1; c += 1
        if vedha_side in ("right", "both"):
            r, c = row + 1, col - 1
            while r < grid_size and c >= 0:
                diag2.append((r, c)); r += 1; c -= 1

        # ── H/V straight lines — ONLY for Sun/Moon/Rahu/Ketu ──
        # "इन ४ ग्रहो का वेध सदा तीनों ही ओर को एक सा होता है"
        if is_always_full:
            horizontal = [(row, c) for c in range(grid_size) if c != col]
            vertical   = [(r, col) for r in range(grid_size) if r != row]

    # Direction list
    active_dirs = ["diagonal1", "diagonal2"]
    if is_always_full and vedha_mode != "front":
        active_dirs.extend(["horizontal", "vertical"])

    return {
        "horizontal":        horizontal,
        "vertical":          vertical,
        "diagonal1":         diag1,
        "diagonal2":         diag2,
        "all":               list({*horizontal, *vertical, *diag1, *diag2}),
        "vedha_type":        vedha_info["type"],
        "vedha_mode":        vedha_mode,
        "vedha_side":        vedha_side,
        "is_three_way":      True,
        "active_directions": sorted(active_dirs),
    }


# ─────────────────────────────────────────────────────────────
# Full SBC Transit Analysis
# ─────────────────────────────────────────────────────────────

def analyze_sbc_transits(
    janma_nak: str,
    natal_chakra_cells: List[Dict],
    transit_planets: List[Dict],
    nak_position_map: Dict[str, Tuple[int,int]],
) -> Dict:
    """
    Full SBC transit analysis v3.5 — Advanced Khemraj Publishers implementation.

    Args:
        janma_nak: Moon's birth nakshatra name
        natal_chakra_cells: flat list of all 81 cells from the chakra
        transit_planets: list of {"planet":..., "nakshatra":..., "retrograde":...,
                                  "longitude":..., "speed":..., "sign":...}
        nak_position_map: nakshatra_name → (row, col) in the 9×9 grid

    Returns:
        Complete analysis dict with vedhas, lattas, bindu hits, navatara,
        NSE/BSE signal, per-planet details, graha bala, temporal states,
        ubhayato vedha, upagrahas, and commodity effects.
    """
    six_bindus = calc_six_bindus(janma_nak)
    navatara   = calc_navatara(janma_nak)

    bindu_naks = {v["nakshatra"]: k for k, v in six_bindus.items()}

    # Build cell → entities lookup. Keep full entity details so vedha can
    # distinguish nakshatra/rashi/tithi/vara/akshara instead of losing type.
    cell_entities: Dict[Tuple[int,int], List[Dict]] = {}
    entity_position_map: Dict[str, Tuple[int, int]] = {}
    for cell in natal_chakra_cells:
        key = (cell["row"], cell["col"])
        cell_entities[key] = cell.get("entities", [])
        for e in cell.get("entities", []):
            nm = e.get("name")
            if nm:
                entity_position_map.setdefault(nm, key)

    # ── Extract Sun/Moon longitudes for dynamic nature classification ──
    sun_longitude = 0.0
    moon_longitude = 0.0
    sun_nakshatra = ""
    for tp in transit_planets:
        if tp["planet"] == "Sun":
            sun_longitude = tp.get("longitude", 0.0)
            sun_nakshatra = tp.get("nakshatra", "")
        elif tp["planet"] == "Moon":
            moon_longitude = tp.get("longitude", 0.0)

    # ── Dynamic planet nature classification (Shlokas 55-56) ──────────
    planet_natures: Dict[str, str] = {}
    nature_details: Dict[str, Dict] = {}
    for tp in transit_planets:
        pname = tp["planet"]
        nature_info = classify_planet_nature(
            pname, transit_planets, moon_longitude, sun_longitude
        )
        planet_natures[pname] = nature_info["nature"]
        nature_details[pname] = nature_info

    # ── 8 Upagraha sub-planets (Shlokas 250-260) ─────────────────────
    upagrahas = calc_upagrahas(sun_nakshatra) if sun_nakshatra else []

    planet_analyses: List[Dict] = []
    all_vedha_hits: List[Dict]  = []
    all_latta_hits: List[Dict]  = []

    overall_score = 0.0

    for tp in transit_planets:
        pname   = tp["planet"]
        nak     = tp.get("nakshatra", "")
        pada    = tp.get("pada", 1)
        retro   = tp.get("retrograde", False)
        speed   = tp.get("speed", 0.0)
        longitude = tp.get("longitude", 0.0)
        sign    = tp.get("sign", "")

        # ── Dynamic nature (replaces hardcoded BENEFIC/MALEFIC) ──
        p_nature = planet_natures.get(pname, "malefic")
        is_benefic = (p_nature == "benefic")

        fin = VEDHA_FINANCIAL.get(pname, {"signal":"NEUTRAL","score":0,"impact":""})

        # ── Graha Bala (Shlokas 161-167) ──────────────────────────
        graha_bala = calc_graha_bala(pname, longitude, speed, sign)

        # ── Commodity effects (Shlokas 245-246 + 126-152) ─────────
        commodity_info = PLANET_COMMODITY_EFFECTS.get(pname, {})

        # ─ Latta ────────────────────────────────────────────
        latta = calc_latta_for_planet(pname, nak, retro)
        latta_hits: List[Dict] = []
        if latta:
            kicked = latta["kicked_nakshatra"]
            bindu_hit = bindu_naks.get(kicked)
            tara_info = navatara.get(kicked, {})
            severity = "CRITICAL" if bindu_hit in ("Janma","Vinash","Karma") else \
                       "HIGH"     if bindu_hit else \
                       "MODERATE" if tara_info.get("quality") == "inauspicious" else "LOW"
            if bindu_hit or tara_info.get("quality") == "inauspicious":
                latta_hit = {
                    "planet":         pname,
                    "transiting_nak": nak,
                    "kicked_nak":     kicked,
                    "bindu_type":     bindu_hit,
                    "tara":           tara_info.get("tara",""),
                    "tara_quality":   tara_info.get("quality",""),
                    "severity":       severity,
                    "effect":         latta["effect"],
                    "nse_impact":     latta["nse_impact"],
                    "nature":         "malefic_latta" if not is_benefic else "benefic_latta",
                    "retrograde":     retro,
                }
                latta_hits.append(latta_hit)
                all_latta_hits.append(latta_hit)
                if not is_benefic:
                    overall_score -= 0.3 if severity == "CRITICAL" else 0.15

        # ─ Speed-based Vedha type ────────────────────────────
        vedha_type_info = classify_vedha_type(pname, speed)
        vedha_mode = vedha_type_info["vedha_mode"]

        # ── Per-nakshatra vedha targets (Shlokas 19-47) ──────
        nak_vedha_targets = get_per_nakshatra_vedha_targets(nak, vedha_mode)

        # ─ Vedha ────────────────────────────────────────────
        pos = nak_position_map.get(nak) or nak_position_map.get(
            tp.get("sign", ""))  # fallback to rashi cell
        vedha_hits: List[Dict] = []
        vedha_line_data: Optional[Dict] = None
        combined_mult: float = 1.0

        if pos:
            row, col = pos
            # ── Speed-filtered vedha cells (geometric fallback) ──
            vedha_cells = get_vedha_cells(row, col, planet=pname, speed=speed)

            # Generate visual line data for the UI (also filtered)
            vedha_line_data = get_vedha_lines(pname, row, col, speed)

            # Strength multiplier — combine vedha type + graha bala
            vedha_str_mult = VEDHA_STRENGTH_MULTIPLIER.get(vedha_type_info["type"], 1.0)
            graha_bala_mult = graha_bala["graha_bala"]
            combined_mult = round(vedha_str_mult * graha_bala_mult, 4)

            # Planet's nakshatra index for temporal vedha
            planet_nak_idx = NAK_INDEX.get(nak, 0)

            # ── Build target cells: BOOK TARGETS take priority ────
            # The book (Shlokas 19-47) gives exact nakshatra targets
            # per direction. Map those target names → grid positions.
            # Geometric cells are used ONLY as fallback when no book
            # data exists (e.g., for Abhijit).
            target_cells: List[Tuple[int, int]] = []
            if nak_vedha_targets is not None:
                # Use book-defined targets → find their grid positions
                _seen_targets: Set[Tuple[int, int]] = set()
                for target_name in nak_vedha_targets:
                    tgt_pos = nak_position_map.get(target_name) or entity_position_map.get(target_name)
                    if tgt_pos and tgt_pos not in _seen_targets:
                        target_cells.append(tgt_pos)
                        _seen_targets.add(tgt_pos)
            else:
                # Fallback to geometric vedha cells
                target_cells = vedha_cells["all"]

            for (vr, vc) in target_cells:
                entities = cell_entities.get((vr, vc), [])
                if not entities:
                    continue
                for ent in entities:
                    entity_name = ent.get("name", "") if isinstance(ent, dict) else str(ent)
                    entity_type = ent.get("entity_type", ent.get("type", "unknown")) if isinstance(ent, dict) else "unknown"
                    bindu_hit = bindu_naks.get(entity_name)
                    tara_info = navatara.get(entity_name, {})

                    # When using book targets, entity must be in the
                    # target list (cell may hold multiple entities).
                    if nak_vedha_targets is not None:
                        if entity_name not in nak_vedha_targets:
                            continue
                    elif not bindu_hit and tara_info.get("quality") not in ("inauspicious",):
                        continue  # Fallback: only report significant hits

                    direction = _vedha_direction(row, col, vr, vc)
                    severity = "CRITICAL" if bindu_hit in ("Janma","Vinash","Karma") else \
                               "HIGH"     if bindu_hit else "MODERATE"

                    # ── Temporal vedha state (Shlokas 103-106) ────
                    target_nak_idx = NAK_INDEX.get(entity_name, -1)
                    temporal_state = {}
                    if target_nak_idx >= 0:
                        temporal_state = classify_temporal_vedha(
                            planet_nak_idx, target_nak_idx, speed, pname
                        )

                    vedha_hit = {
                        "planet":        pname,
                        "from_nak":      nak,
                        "from_pos":      list(pos),
                        "to_entity":     entity_name,
                        "to_entity_type": entity_type,
                        "to_pos":        [vr, vc],
                        "bindu_type":    bindu_hit,
                        "from_pada":     pada,
                        "to_pada":       pada if entity_type == "nakshatra" else None,
                        "pada_vedha":    (f"{nak} pada {pada} → {entity_name} pada {pada}" if entity_type == "nakshatra" else "not_applicable"),
                        "tara":          tara_info.get("tara",""),
                        "tara_quality":  tara_info.get("quality",""),
                        "vedha_direction": direction,
                        "vedha_speed_type": vedha_type_info["type"],
                        "vedha_mode":    vedha_mode,
                        "active_directions": vedha_cells.get("active_directions", []),
                        "severity":      severity,
                        "nature":        "shubha_vedha" if is_benefic else "papa_vedha",
                        "effect":        VEDHA_EFFECTS.get(pname,""),
                        "nse_impact":    fin["impact"],
                        "retrograde":    retro,
                        "speed":         round(speed, 4),
                        "strength_multiplier": combined_mult,
                        "graha_bala":    graha_bala["graha_bala"],
                        "temporal_state": temporal_state,
                        "commodity":     commodity_info,
                    }
                    vedha_hits.append(vedha_hit)
                    all_vedha_hits.append(vedha_hit)

                    # Apply combined strength to scoring
                    temporal_mod = temporal_state.get("strength_mod", 1.0) if temporal_state else 1.0
                    if temporal_mod <= 0:
                        temporal_mod = 0.1  # inactive vedha still counts slightly
                    if is_benefic:
                        base = 0.25 if severity == "CRITICAL" else 0.12
                        overall_score += base * combined_mult * temporal_mod
                    else:
                        base = 0.25 if severity == "CRITICAL" else 0.12
                        overall_score -= base * combined_mult * temporal_mod

        # ── Corner Pada Vedha (Shloka 52) ──────────────────────
        corner_vedha_info = check_corner_pada_vedha(nak, pada)
        if corner_vedha_info:
            svara_pos = corner_vedha_info["svara_pos"]
            center_pos = corner_vedha_info["center_pos"]
            corner_hit = {
                "planet":        pname,
                "from_nak":      nak,
                "from_pada":     pada,
                "corner":        corner_vedha_info["corner"],
                "svara":         corner_vedha_info["svara"],
                "svara_en":      corner_vedha_info["svara_en"],
                "svara_pos":     list(svara_pos),
                "center_pos":    list(center_pos),
                "vedha_speed_type": vedha_type_info["type"],
                "nature":        "shubha_vedha" if is_benefic else "papa_vedha",
                "effect":        f"Corner {corner_vedha_info['corner']} svara vedha — "
                                 f"{'auspicious' if is_benefic else 'inauspicious'} "
                                 f"on {corner_vedha_info['svara_en']} svara + Purna tithi",
                "retrograde":    retro,
                "strength_multiplier": combined_mult if pos else 1.0,
            }
            # Add corner vedha as a special vedha hit
            vedha_hits.append({
                **corner_hit,
                "to_entity":     corner_vedha_info["svara"],
                "to_pos":        list(svara_pos),
                "bindu_type":    None,
                "tara":          "",
                "tara_quality":  "",
                "vedha_direction": corner_vedha_info["corner"],
                "vedha_mode":    "corner_pada",
                "active_directions": [corner_vedha_info["corner"]],
                "severity":      "HIGH" if not is_benefic else "MODERATE",
                "speed":         round(speed, 4),
                "graha_bala":    graha_bala.get("graha_bala", 1.0) if isinstance(graha_bala, dict) else 1.0,
                "temporal_state": {},
                "commodity":     commodity_info,
                "nse_impact":    fin["impact"],
            })
            all_vedha_hits.append(vedha_hits[-1])
            # Score impact — corner vedha is significant
            if is_benefic:
                overall_score += 0.15 * (combined_mult if pos else 1.0)
            else:
                overall_score -= 0.15 * (combined_mult if pos else 1.0)
        else:
            corner_hit = None

        planet_analyses.append({
            "planet":          pname,
            "nakshatra":       nak,
            "pada":            pada,
            "retrograde":      retro,
            "speed":           round(speed, 4),
            "longitude":       round(longitude, 4),
            "sign":            sign,
            "vedha_speed_type": vedha_type_info["type"],
            "vedha_side":      vedha_type_info["vedha_side"],
            "vedha_mode":      vedha_mode,
            "is_three_way":    vedha_type_info["is_three_way"],
            "vedha_strength":  vedha_type_info["strength"],
            "vedha_line_style":vedha_type_info["line_style"],
            "nature":          p_nature,
            "nature_detail":   nature_details.get(pname, {}),
            "graha_bala":      graha_bala,
            "grid_position":   list(pos) if pos else None,
            "vedha_lines":     vedha_line_data,
            "latta":           latta if latta else {},
            "latta_hits":      latta_hits,
            "vedha_hits":      vedha_hits,
            "vedha_count":     len(vedha_hits),
            "corner_pada_vedha": corner_hit,
            "financial":       fin,
            "commodity":       commodity_info,
            "nak_vedha_targets": nak_vedha_targets,
        })
        overall_score += fin["score"] * 0.1

    # ── Ubhayato Vedha detection (Shloka 220) ────────────────
    ubhayato_vedha = detect_ubhayato_vedha(
        all_vedha_hits, transit_planets, planet_natures
    )
    # Ubhayato vedha further depresses score
    for uv in ubhayato_vedha:
        if uv["is_true_ubhayato"]:
            overall_score -= 0.3 * uv["malefic_count"]
        else:
            overall_score -= 0.15 * uv["malefic_count"]

    # ── Upagraha vedha analysis ──────────────────────────────
    upagraha_hits = []
    for upa in upagrahas:
        upa_nak = upa["nakshatra"]
        bindu_hit = bindu_naks.get(upa_nak)
        tara_info = navatara.get(upa_nak, {})
        if bindu_hit or tara_info.get("quality") == "inauspicious":
            upagraha_hits.append({
                "upagraha":    upa["name"],
                "nakshatra":   upa_nak,
                "bindu_type":  bindu_hit,
                "tara":        tara_info.get("tara", ""),
                "tara_quality": tara_info.get("quality", ""),
                "effect":      upa["effect"],
                "financial":   upa["financial"],
                "severity":    "HIGH" if bindu_hit else "MODERATE",
            })
            overall_score -= 0.1 if bindu_hit else 0.05

    # ─ Bindu summary ────────────────────────────────────────
    bindu_analysis = _analyze_bindus(six_bindus, all_vedha_hits, all_latta_hits)

    # ─ Market signal ────────────────────────────────────────
    overall_score = max(-1.0, min(1.0, overall_score))
    market_signal = _sbc_to_market_signal(overall_score, all_vedha_hits, all_latta_hits)

    # ─ Vedha count effects ───────────────────────────────────
    malefic_vedha_count = sum(
        1 for v in all_vedha_hits if v["nature"] == "papa_vedha" and
        v.get("bindu_type") in ("Janma","Karma","Vinash")
    )
    multiple_effect = VEDHA_MULTIPLE_EFFECTS.get(min(malefic_vedha_count, 4), "")

    # Geometric vedha lines for rendering — these show the PATH of
    # vedha influence along diagonals/rows/columns.  Hit detection
    # still uses book-based targets (Shlokas 19-47).
    vedha_lines_all = []
    for pa in planet_analyses:
        vl = pa.get("vedha_lines")
        if vl is not None:
            vl["nature"] = pa["nature"]   # inject benefic/malefic for UI
            vedha_lines_all.append(vl)

    # ── Tatkalika Grahas (Shlokas 153-160) ───────────────────
    moon_nak = ""
    moon_speed = 0.0
    for tp in transit_planets:
        if tp["planet"] == "Moon":
            moon_nak = tp.get("nakshatra", "")
            moon_speed = tp.get("speed", 13.0)
            break
    tatkalika = calc_tatkalika_grahas(sun_nakshatra, moon_nak) if sun_nakshatra and moon_nak else {}

    # ── Moon Daily Vedha ─────────────────────────────────────
    moon_daily_vedha = {}
    if moon_nak:
        moon_daily_vedha = calc_moon_daily_vedha(
            moon_nak, moon_speed, transit_planets,
            planet_natures, nak_position_map, natal_chakra_cells,
        )

    # ── Enhanced Vedha Count Analysis (Shlokas 107-109, 122-124) ──
    vedha_count_analysis = calc_vedha_count_analysis(all_vedha_hits)

    return {
        "janma_nakshatra":      janma_nak,
        "six_bindus":           six_bindus,
        "navatara":             navatara,
        "planet_analyses":      planet_analyses,
        "all_vedha_hits":       all_vedha_hits,
        "all_latta_hits":       all_latta_hits,
        "bindu_analysis":       bindu_analysis,
        "malefic_vedha_count":  malefic_vedha_count,
        "multiple_vedha_effect": multiple_effect,
        "overall_sbc_score":    round(overall_score, 3),
        "market_signal":        market_signal,
        "cells_under_vedha":   _cells_under_any_vedha(all_vedha_hits),
        "cells_with_latta":    _cells_with_latta(all_latta_hits, nak_position_map),
        "bindu_cells":          _bindu_cell_positions(six_bindus, nak_position_map),
        "vedha_lines_all":      vedha_lines_all,   # ← for Canvas rendering
        # ── Advanced SBC v3.5 ──────────────────────────────
        "planet_natures":       planet_natures,
        "nature_details":       nature_details,
        "ubhayato_vedha":       ubhayato_vedha,
        "upagrahas":            upagrahas,
        "upagraha_hits":        upagraha_hits,
        # ── SBC v4.0 — Book-accurate enhancements ─────────
        "tatkalika_grahas":     tatkalika,
        "moon_daily_vedha":     moon_daily_vedha,
        "vedha_count_analysis": vedha_count_analysis,
    }


def _vedha_direction(fr: int, fc: int, tr: int, tc: int) -> str:
    if fr == tr:   return "horizontal"
    if fc == tc:   return "vertical"
    if (tr-fr) == (tc-fc): return "diagonal_main"
    return "diagonal_anti"


def _analyze_bindus(
    six_bindus: Dict, vedha_hits: List[Dict], latta_hits: List[Dict]
) -> List[Dict]:
    """Summarize the status of each of the 6 bindus."""
    result = []
    for bindu_name, info in six_bindus.items():
        nak = info["nakshatra"]
        v_hits = [v for v in vedha_hits if v.get("bindu_type") == bindu_name]
        l_hits = [l for l in latta_hits if l.get("bindu_type") == bindu_name]
        malefic_v = [v for v in v_hits if v["nature"] == "papa_vedha"]
        benefic_v = [v for v in v_hits if v["nature"] == "shubha_vedha"]
        status = ("AFFLICTED" if len(malefic_v) > len(benefic_v) + 1 else
                  "PROTECTED" if len(benefic_v) > 0 and len(malefic_v) == 0 else
                  "MIXED"     if (malefic_v or benefic_v) else "CLEAR")
        result.append({
            "bindu":          bindu_name,
            "nakshatra":      nak,
            "description":    info["description"],
            "status":         status,
            "malefic_vedhas": len(malefic_v),
            "benefic_vedhas": len(benefic_v),
            "latta_hits":     len(l_hits),
            "afflicting_planets": [v["planet"] for v in malefic_v],
            "protecting_planets": [v["planet"] for v in benefic_v],
        })
    return result


def _sbc_to_market_signal(
    score: float, vedha_hits: List[Dict], latta_hits: List[Dict]
) -> Dict:
    # Check Janma Nakshatra specifically
    janma_malefic = sum(1 for v in vedha_hits
                        if v.get("bindu_type") == "Janma" and v["nature"] == "papa_vedha")
    janma_latta   = sum(1 for l in latta_hits if l.get("bindu_type") == "Janma")
    vinash_hits   = sum(1 for v in vedha_hits if v.get("bindu_type") == "Vinash")

    if janma_malefic >= 2 or vinash_hits >= 2 or janma_latta >= 2:
        signal = "STRONGLY BEARISH"; color = "#FF3D00"; action = "Exit all positions"
    elif score >= 0.4:
        signal = "BULLISH";          color = "#00C851"; action = "Buy on dips"
    elif score >= 0.1:
        signal = "MILDLY BULLISH";   color = "#8BC34A"; action = "Selective accumulation"
    elif score >= -0.1:
        signal = "NEUTRAL";          color = "#FFC107"; action = "Hold — no new large entries"
    elif score >= -0.4:
        signal = "BEARISH";          color = "#FF5722"; action = "Reduce exposure"
    else:
        signal = "STRONGLY BEARISH"; color = "#FF3D00"; action = "Exit all positions"

    tips = []
    if janma_malefic > 0:
        tips.append(f"Janma nakshatra afflicted by {janma_malefic} malefic vedha(s)")
    if janma_latta > 0:
        tips.append(f"Active Latta on Janma nakshatra ({janma_latta} planet(s))")
    if vinash_hits > 0:
        tips.append(f"Vinash nakshatra under {vinash_hits} vedha(s) — high risk")

    return {"signal": signal, "color": color, "action": action,
            "score": round(score, 3), "warning_tips": tips}


def _cells_under_any_vedha(all_vedha_hits: List[Dict]) -> Dict[str, Dict]:
    """Map each cell position → all planets vedhaing it, and the net quality."""
    result: Dict[str, Dict] = {}
    for v in all_vedha_hits:
        key = f"{v['to_pos'][0]},{v['to_pos'][1]}"
        if key not in result:
            result[key] = {"row": v["to_pos"][0], "col": v["to_pos"][1],
                           "malefic": [], "benefic": [], "net": "neutral"}
        if v["nature"] == "papa_vedha":
            result[key]["malefic"].append(v["planet"])
        else:
            result[key]["benefic"].append(v["planet"])
    for key, d in result.items():
        m, b = len(d["malefic"]), len(d["benefic"])
        d["net"] = "malefic" if m > b else "benefic" if b > m else "mixed"
    return result


def _cells_with_latta(latta_hits: List[Dict],
                       nak_pos_map: Dict[str, Tuple[int,int]]) -> Dict[str, Dict]:
    result: Dict[str, Dict] = {}
    for l in latta_hits:
        nak = l["kicked_nak"]
        pos = nak_pos_map.get(nak)
        if not pos:
            continue
        key = f"{pos[0]},{pos[1]}"
        if key not in result:
            result[key] = {"row": pos[0], "col": pos[1], "planets": [], "nakshatra": nak}
        result[key]["planets"].append(l["planet"])
    return result


def _bindu_cell_positions(
    six_bindus: Dict, nak_pos_map: Dict[str, Tuple[int,int]]
) -> Dict[str, Dict]:
    result: Dict[str, Dict] = {}
    for bindu_name, info in six_bindus.items():
        nak = info["nakshatra"]
        pos = nak_pos_map.get(nak)
        if pos:
            result[bindu_name] = {"nakshatra": nak, "row": pos[0], "col": pos[1]}
    return result


# ─────────────────────────────────────────────────────────────
# NSE/BSE SBC Daily Signal
# ─────────────────────────────────────────────────────────────

def sbc_nse_daily_signal(
    janma_nak: str,
    transit_nak_map: Dict[str, str],   # planet → current nakshatra
    retrograde_map: Dict[str, bool],   # planet → is_retrograde
) -> Dict:
    """
    Quick daily NSE/BSE signal using just Latta + Navatara.
    Used for intraday/daily market signal without the full SBC grid.
    """
    navatara = calc_navatara(janma_nak)
    bindus   = calc_six_bindus(janma_nak)
    bindu_naks = {v["nakshatra"] for v in bindus.values()}

    active_lattas: List[Dict] = []
    active_vedha_naks: List[str] = []
    score = 0.0

    for planet, nak in transit_nak_map.items():
        retro = retrograde_map.get(planet, False)
        latta = calc_latta_for_planet(planet, nak, retro)
        if latta:
            kicked = latta["kicked_nakshatra"]
            tara = navatara.get(kicked, {})
            if kicked in bindu_naks or tara.get("quality") == "inauspicious":
                is_mal = planet in MALEFIC_PLANETS
                active_lattas.append({
                    "planet": planet, "kicked": kicked,
                    "tara": tara.get("tara",""), "quality": tara.get("quality",""),
                    "effect": LATTA_EFFECTS.get(planet,""),
                    "severity": "HIGH" if kicked in bindu_naks else "MODERATE",
                })
                score += -0.25 if is_mal else 0.15

        # Tara of transiting nakshatra
        tara_of_transit = navatara.get(nak, {})
        if tara_of_transit.get("quality") == "auspicious" and planet in BENEFIC_PLANETS:
            score += 0.1
        elif tara_of_transit.get("quality") == "inauspicious" and planet in MALEFIC_PLANETS:
            score -= 0.1
            active_vedha_naks.append(nak)

    score = max(-1.0, min(1.0, score))
    return {
        "janma_nakshatra":  janma_nak,
        "overall_score":    round(score, 3),
        "active_lattas":    active_lattas,
        "active_vedha_naks": active_vedha_naks,
        "market_signal":    _sbc_to_market_signal(score, [], active_lattas),
    }


# ═══════════════════════════════════════════════════════════════
# FULL ENTITY VEDHA TARGETS — Khemraj book Shlokas 19-47
# Each nakshatra's vedha covers ALL 5 entity types per direction
# ═══════════════════════════════════════════════════════════════

# Linked akshara pairs (Shlokas 48-50) — vedha on one implies vedha on partner
LINKED_AKSHARAS = {
    "Ba": "Va", "Va": "Ba",
    "Sha": "Sa", "Sa": "Sha",
    "Sha2": "Kha", "Kha": "Sha2",
    "Ka": ["Cha", "Nga", "Chha"],
    "Pa": ["Sha2", "Na2", "Tha2"],
    "Bha": ["Dha", "Pha", "Da2", "Dha2"],
    "Da": ["Tha", "Jna", "Ja"],
}

# Linked svara pairs (Shloka 51) — vedha on one implies vedha on partner
LINKED_SVARAS = {
    "A": "Aa", "Aa": "A",
    "I": "Ii", "Ii": "I",
    "U": "Uu", "Uu": "U",
    "Ri": "Rii", "Rii": "Ri",
    "E": "Ai", "Ai": "E",
    "O": "Au", "Au": "O",
}


# ═══════════════════════════════════════════════════════════════
# CORNER SVARA VEDHA — Shloka 52
# When planet is at corner junction padas, it vedhas the corner
# svara AND the Purna tithi in the center.
# ═══════════════════════════════════════════════════════════════

# (nakshatra, pada) → corner svara vedha'd + center Purna tithi
# Grid positions: Ishana=(0,0), Agni=(0,8), Nairitya=(8,8), Vayavya=(8,0), Center=(4,4)
CORNER_PADA_VEDHA = {
    # Ishana corner (NE) — 'अ' svara at (0,0)
    ("Bharani", 4):    {"corner": "Ishana", "svara": "अ", "svara_en": "A",  "svara_pos": (0, 0), "center_pos": (4, 4)},
    ("Krittika", 1):   {"corner": "Ishana", "svara": "अ", "svara_en": "A",  "svara_pos": (0, 0), "center_pos": (4, 4)},
    # Agni corner (SE) — 'आ' svara at (0,8)
    ("Ashlesha", 4):   {"corner": "Agni",   "svara": "आ", "svara_en": "Aa", "svara_pos": (0, 8), "center_pos": (4, 4)},
    ("Magha", 1):      {"corner": "Agni",   "svara": "आ", "svara_en": "Aa", "svara_pos": (0, 8), "center_pos": (4, 4)},
    # Nairitya corner (SW) — 'इ' svara at (8,8)
    ("Vishakha", 4):   {"corner": "Nairitya","svara": "इ", "svara_en": "I",  "svara_pos": (8, 8), "center_pos": (4, 4)},
    ("Anuradha", 1):   {"corner": "Nairitya","svara": "इ", "svara_en": "I",  "svara_pos": (8, 8), "center_pos": (4, 4)},
    # Vayavya corner (NW) — 'ई' svara at (8,0)
    ("Shravana", 4):   {"corner": "Vayavya","svara": "ई", "svara_en": "Ii", "svara_pos": (8, 0), "center_pos": (4, 4)},
    ("Dhanishtha", 1): {"corner": "Vayavya","svara": "ई", "svara_en": "Ii", "svara_pos": (8, 0), "center_pos": (4, 4)},
}


def check_corner_pada_vedha(nakshatra: str, pada: int) -> Optional[Dict]:
    """
    Check if planet at this nakshatra+pada vedhas a corner svara (Shloka 52).
    Returns corner info if applicable, None otherwise.
    """
    return CORNER_PADA_VEDHA.get((nakshatra, pada))


# ═══════════════════════════════════════════════════════════════
# VEDHA COUNT EFFECTS — Shlokas 107-109 (papa), 122-124 (shubha)
# ═══════════════════════════════════════════════════════════════

PAPA_VEDHA_COUNT_EFFECTS = {
    1: {"effect": "Udvega (उद्वेग)", "meaning": "Anxiety and confusion", "severity": "LOW", "market": "Minor negative volatility"},
    2: {"effect": "Bhaya (भय)", "meaning": "Fear and mental suffering", "severity": "MODERATE", "market": "Bearish pressure building"},
    3: {"effect": "Hani (हानि)", "meaning": "Financial loss, multiple afflictions", "severity": "HIGH", "market": "Significant downward move expected"},
    4: {"effect": "Roga (रोग)", "meaning": "Disease and serious danger", "severity": "CRITICAL", "market": "Sharp decline, circuit breaker possible"},
    5: {"effect": "Mrityu (मृत्यु)", "meaning": "Death/destruction — most severe", "severity": "EXTREME", "market": "Market crash signal — extreme caution"},
}

SHUBHA_VEDHA_COUNT_EFFECTS = {
    1: {"effect": "Saubhagya (सौभाग्य)", "meaning": "Good fortune", "severity": "LOW", "market": "Mild positive sentiment"},
    2: {"effect": "Labha (लाभ)", "meaning": "Gain and profit", "severity": "MODERATE", "market": "Bullish momentum building"},
    3: {"effect": "Vijaya (विजय)", "meaning": "Victory and triumph", "severity": "HIGH", "market": "Strong rally expected"},
    4: {"effect": "Dhana-Sukha (धन-सुख)", "meaning": "Wealth and happiness", "severity": "VERY_HIGH", "market": "Major bull run, all-time-high possible"},
}

# Per-entity-type vedha effects (Shloka 109 papa, 123-124 shubha)
ENTITY_TYPE_VEDHA = {
    "papa": {
        "nakshatra": {"effect": "Bhrama (भ्रम)", "meaning": "Confusion and disorientation"},
        "akshara":   {"effect": "Hani (हानि)", "meaning": "Loss — financial or personal"},
        "svara":     {"effect": "Vyadhi (व्याधि)", "meaning": "Disease or illness"},
        "tithi":     {"effect": "Bhaya (भय)", "meaning": "Fear and dread"},
        "rashi":     {"effect": "Maha-Vighna (महाविघ्न)", "meaning": "Great obstacle or hindrance"},
    },
    "shubha": {
        "nakshatra": {"effect": "Deha-Vriddhi (देहवृद्धि)", "meaning": "Bodily health, fearlessness, success"},
        "akshara":   {"effect": "Nirbhayata (निर्भयता)", "meaning": "Fearlessness and courage"},
        "svara":     {"effect": "Saubhagya-Vriddhi (सौभाग्यवृद्धि)", "meaning": "Increase in fortune"},
        "tithi":     {"effect": "Dravya-Labha (द्रव्यलाभ)", "meaning": "Material gain and wealth"},
        "rashi":     {"effect": "Sukha (सुख)", "meaning": "Happiness and comfort"},
    },
}


# ═══════════════════════════════════════════════════════════════
# TATKALIKA GRAHAS — Instantaneous Planets (Shlokas 153-160)
# ═══════════════════════════════════════════════════════════════

# Paksha (fortnightly) grahas — counted from Sun's nakshatra
# Start from Sun's nak → 12th=Ketu, from Ketu 17th=Mercury, etc.
PAKSHA_GRAHA_OFFSETS = [
    ("Ketu",    12),
    ("Mercury", 17),
    ("Venus",    4),
    ("Rahu",    14),
    ("Mars",    18),
    ("Jupiter", 13),
    ("Saturn",  10),
    ("Moon",    15),
]

# Dina (daily) grahas — counted from Moon's nakshatra
# Start from Moon's nak → 7th=Mars, from Mars 4th=Mercury, etc.
DINA_GRAHA_OFFSETS = [
    ("Mars",     7),
    ("Mercury",  4),
    ("Jupiter",  5),
    ("Venus",    6),
    ("Saturn",   7),
    ("Sun",      9),
    ("Rahu",     9),
    ("Ketu",     9),
]

# Kshana (momentary) grahas — from Sun's nakshatra
KSHANA_GRAHA_OFFSETS = [
    ("Moon",     3),
    ("Mars",     5),
    ("Mercury",  7),
    ("Jupiter",  8),
    ("Venus",    8),
    ("Saturn",  14),
    ("Rahu",     8),
    ("Ketu",     7),
]


def calc_tatkalika_grahas(sun_nakshatra: str, moon_nakshatra: str) -> Dict:
    """
    Calculate Tatkalika (temporal) grahas per Shlokas 153-160.

    Paksha grahas: from Sun's nakshatra, cumulative offsets
    Dina grahas: from Moon's nakshatra, cumulative offsets
    Kshana grahas: from Sun's nakshatra, cumulative offsets

    These temporal planets give vedha results within their time periods.
    """
    result = {"paksha": [], "dina": [], "kshana": []}

    # Paksha grahas from Sun's nakshatra
    current_nak = sun_nakshatra
    for planet_name, offset in PAKSHA_GRAHA_OFFSETS:
        target_nak = nak_at_offset(current_nak, offset - 1, "forward")
        result["paksha"].append({
            "planet": planet_name,
            "nakshatra": target_nak,
            "offset": offset,
            "from_nak": current_nak,
            "period": "Paksha (fortnightly)",
        })
        current_nak = target_nak

    # Dina grahas from Moon's nakshatra
    current_nak = moon_nakshatra
    for planet_name, offset in DINA_GRAHA_OFFSETS:
        target_nak = nak_at_offset(current_nak, offset - 1, "forward")
        result["dina"].append({
            "planet": planet_name,
            "nakshatra": target_nak,
            "offset": offset,
            "from_nak": current_nak,
            "period": "Dina (daily)",
        })
        current_nak = target_nak

    # Kshana grahas from Sun's nakshatra
    current_nak = sun_nakshatra
    for planet_name, offset in KSHANA_GRAHA_OFFSETS:
        target_nak = nak_at_offset(current_nak, offset - 1, "forward")
        result["kshana"].append({
            "planet": planet_name,
            "nakshatra": target_nak,
            "offset": offset,
            "from_nak": current_nak,
            "period": "Kshana (momentary)",
        })
        current_nak = target_nak

    return result


# ═══════════════════════════════════════════════════════════════
# MOON DAILY VEDHA + PER-PLANET VEDHA ANALYSIS
# ═══════════════════════════════════════════════════════════════

def calc_moon_daily_vedha(
    moon_nakshatra: str,
    moon_speed: float,
    all_transit_planets: List[Dict],
    planet_natures: Dict[str, str],
    nak_position_map: Dict[str, Tuple[int, int]],
    natal_chakra_cells: List[Dict],
) -> Dict:
    """
    Calculate Moon's daily vedha — what entities does Moon vedha today,
    and which planets are casting vedha ON the Moon's current position.

    Moon is always shighragami (fast) → vedha in ALL 3 directions.
    Returns: Moon's vedha targets + planets vedhing Moon's position.
    """
    # Moon's vedha targets (Moon vedhas in all 3 directions)
    moon_targets = PER_NAKSHATRA_VEDHA_TARGETS.get(moon_nakshatra, {})
    all_targets = []
    for direction in ["vama", "dakshina", "sammukha"]:
        for target in moon_targets.get(direction, []):
            all_targets.append({
                "entity": target,
                "direction": direction,
                "direction_hindi": {"vama": "बाई (Left)", "dakshina": "दाहिनी (Right)", "sammukha": "सामने (Front)"}.get(direction, direction),
            })

    # Which planets vedha Moon's nakshatra?
    planets_vedhing_moon = []
    for tp in all_transit_planets:
        if tp["planet"] == "Moon":
            continue
        pname = tp["planet"]
        p_nak = tp.get("nakshatra", "")
        p_speed = tp.get("speed", 0.0)

        vedha_info = classify_vedha_type(pname, p_speed)
        p_targets = get_per_nakshatra_vedha_targets(p_nak, vedha_info["vedha_mode"])

        if p_targets and moon_nakshatra in p_targets:
            p_nature = planet_natures.get(pname, "malefic")
            planets_vedhing_moon.append({
                "planet": pname,
                "from_nakshatra": p_nak,
                "vedha_type": vedha_info["type"],
                "nature": p_nature,
                "is_benefic": p_nature == "benefic",
                "speed": round(p_speed, 4),
                "retrograde": p_speed < 0,
                "effect": "Shubha vedha — positive influence on mind/emotions" if p_nature == "benefic"
                         else "Papa vedha — mental stress, emotional disturbance",
            })

    # Moon's rashi (from nakshatra)
    NAK_TO_RASHI = {
        "Ashwini": "Mesha", "Bharani": "Mesha", "Krittika": "Mesha/Vrishabha",
        "Rohini": "Vrishabha", "Mrigashira": "Vrishabha/Mithuna", "Ardra": "Mithuna",
        "Punarvasu": "Mithuna/Karka", "Pushya": "Karka", "Ashlesha": "Karka",
        "Magha": "Simha", "Purva Phalguni": "Simha", "Uttara Phalguni": "Simha/Kanya",
        "Hasta": "Kanya", "Chitra": "Kanya/Tula", "Swati": "Tula",
        "Vishakha": "Tula/Vrishchika", "Anuradha": "Vrishchika", "Jyeshtha": "Vrishchika",
        "Mula": "Dhanu", "Purva Ashadha": "Dhanu", "Uttara Ashadha": "Dhanu/Makara",
        "Shravana": "Makara", "Dhanishtha": "Makara/Kumbha", "Shatabhisha": "Kumbha",
        "Purva Bhadrapada": "Kumbha/Meena", "Uttara Bhadrapada": "Meena", "Revati": "Meena",
    }

    shubha_count = sum(1 for p in planets_vedhing_moon if p["is_benefic"])
    papa_count = sum(1 for p in planets_vedhing_moon if not p["is_benefic"])

    return {
        "moon_nakshatra": moon_nakshatra,
        "moon_rashi": NAK_TO_RASHI.get(moon_nakshatra, ""),
        "moon_speed": round(moon_speed, 4),
        "vedha_targets": all_targets,
        "vedha_target_count": len(all_targets),
        "planets_vedhing_moon": planets_vedhing_moon,
        "shubha_vedha_on_moon": shubha_count,
        "papa_vedha_on_moon": papa_count,
        "moon_vedha_summary": (
            f"Moon in {moon_nakshatra} — {len(all_targets)} entities vedha'd. "
            f"{shubha_count} benefic + {papa_count} malefic planets vedhing Moon."
        ),
        "daily_outlook": (
            "Positive — benefic planets dominate Moon's vedha" if shubha_count > papa_count
            else "Negative — malefic planets dominate Moon's vedha" if papa_count > shubha_count
            else "Mixed — balanced benefic/malefic vedha on Moon"
        ),
    }


def calc_planet_vedha_detail(
    planet_name: str,
    transit_planets: List[Dict],
    planet_natures: Dict[str, str],
    nak_position_map: Dict[str, Tuple[int, int]],
    natal_chakra_cells: List[Dict],
    janma_nak: str,
) -> Dict:
    """
    Detailed vedha analysis for a specific chosen planet.
    Shows all entities this planet vedhas, categorized by type and direction.
    For future Nifty implementation.
    """
    # Find the planet in transits
    target_planet = None
    for tp in transit_planets:
        if tp["planet"] == planet_name:
            target_planet = tp
            break

    if not target_planet:
        return {"error": f"Planet {planet_name} not found in transits"}

    nak = target_planet.get("nakshatra", "")
    speed = target_planet.get("speed", 0.0)
    retro = target_planet.get("retrograde", False)
    sign = target_planet.get("sign", "")
    longitude = target_planet.get("longitude", 0.0)

    vedha_info = classify_vedha_type(planet_name, speed)
    p_nature = planet_natures.get(planet_name, "malefic")
    is_benefic = p_nature == "benefic"

    # Get vedha targets per direction
    nak_targets = PER_NAKSHATRA_VEDHA_TARGETS.get(nak, {})

    # Build cell → entities lookup
    cell_entities = {}
    for cell in natal_chakra_cells:
        key = (cell["row"], cell["col"])
        cell_entities[key] = cell.get("entities", [])

    # Get geometric vedha cells
    pos = nak_position_map.get(nak)
    if not pos:
        return {"error": f"No grid position for nakshatra {nak}"}

    row, col = pos
    vedha_cells = get_vedha_cells(row, col, planet=planet_name, speed=speed)

    # Categorize all vedha'd entities by type
    vedha_by_type = {
        "nakshatras": [],
        "rashis": [],
        "aksharas": [],
        "svaras": [],
        "tithis": [],
        "varas": [],
    }

    vedha_by_direction = {
        "vama": [],
        "dakshina": [],
        "sammukha": [],
    }

    for (vr, vc) in vedha_cells["all"]:
        entities = cell_entities.get((vr, vc), [])
        for ent in entities:
            ent_name = ent.get("name", "") if isinstance(ent, dict) else str(ent)
            ent_type = ent.get("type", "unknown") if isinstance(ent, dict) else "unknown"

            direction = _vedha_direction(row, col, vr, vc)

            entry = {
                "entity": ent_name,
                "type": ent_type,
                "position": [vr, vc],
                "direction": direction,
                "nature": "shubha" if is_benefic else "papa",
            }

            # Categorize by entity type
            type_key = ent_type + "s" if ent_type in ("nakshatra", "rashi", "akshara", "svara", "tithi", "vara") else "nakshatras"
            if type_key in vedha_by_type:
                vedha_by_type[type_key].append(entry)

            # Categorize by direction
            if "vama" in direction.lower() or "left" in direction.lower():
                vedha_by_direction["vama"].append(entry)
            elif "dakshina" in direction.lower() or "right" in direction.lower():
                vedha_by_direction["dakshina"].append(entry)
            else:
                vedha_by_direction["sammukha"].append(entry)

    # Graha bala
    graha_bala = calc_graha_bala(planet_name, longitude, speed, sign)

    return {
        "planet": planet_name,
        "nakshatra": nak,
        "sign": sign,
        "speed": round(speed, 4),
        "retrograde": retro,
        "longitude": round(longitude, 4),
        "vedha_type": vedha_info["type"],
        "vedha_mode": vedha_info["vedha_mode"],
        "nature": p_nature,
        "graha_bala": graha_bala,
        "grid_position": list(pos),
        "vedha_by_type": vedha_by_type,
        "vedha_by_direction": vedha_by_direction,
        "total_entities_vedha": sum(len(v) for v in vedha_by_type.values()),
        "nak_vedha_targets_book": nak_targets,
    }


def calc_vedha_count_analysis(all_vedha_hits: List[Dict]) -> Dict:
    """
    Analyze vedha counts per Shlokas 107-109 (papa) and 122-124 (shubha).
    Counts distinct planet vedhas on bindu nakshatras.
    """
    papa_on_bindus = set()
    shubha_on_bindus = set()

    entity_papa_counts = {}
    entity_shubha_counts = {}

    for vh in all_vedha_hits:
        planet = vh.get("planet", "")
        nature = vh.get("nature", "")
        bindu = vh.get("bindu_type")
        entity = vh.get("to_entity", "")

        if nature == "papa_vedha":
            if bindu:
                papa_on_bindus.add(planet)
            entity_papa_counts[entity] = entity_papa_counts.get(entity, 0) + 1
        else:
            if bindu:
                shubha_on_bindus.add(planet)
            entity_shubha_counts[entity] = entity_shubha_counts.get(entity, 0) + 1

    papa_count = len(papa_on_bindus)
    shubha_count = len(shubha_on_bindus)

    papa_effect = PAPA_VEDHA_COUNT_EFFECTS.get(min(papa_count, 5), {})
    shubha_effect = SHUBHA_VEDHA_COUNT_EFFECTS.get(min(shubha_count, 4), {})

    # Net assessment
    if papa_count >= 4:
        net = "EXTREME_DANGER"
        net_desc = "Extreme danger — 4+ malefic vedhas on bindus. Avoid all risky activities."
    elif papa_count >= 3 and shubha_count < 2:
        net = "HIGH_DANGER"
        net_desc = "High danger — significant malefic vedha, inadequate benefic protection."
    elif shubha_count >= 3 and papa_count <= 1:
        net = "HIGHLY_FAVORABLE"
        net_desc = "Highly favorable — strong benefic vedha dominance."
    elif shubha_count > papa_count:
        net = "FAVORABLE"
        net_desc = "Favorable — benefic vedha outweighs malefic."
    elif papa_count > shubha_count:
        net = "UNFAVORABLE"
        net_desc = "Unfavorable — malefic vedha dominates."
    else:
        net = "MIXED"
        net_desc = "Mixed influences — balanced benefic and malefic vedha."

    return {
        "papa_vedha_count": papa_count,
        "shubha_vedha_count": shubha_count,
        "papa_effect": papa_effect,
        "shubha_effect": shubha_effect,
        "papa_planets": sorted(papa_on_bindus),
        "shubha_planets": sorted(shubha_on_bindus),
        "net_assessment": net,
        "net_description": net_desc,
        "entity_papa_counts": entity_papa_counts,
        "entity_shubha_counts": entity_shubha_counts,
    }


# ═════════════════════════════════════════════════════════════
# PATCH: SBC/BDC vedha correction layer
# Added by ChatGPT for Himanshu: unified speed-based three-direction
# vedha + pada metadata + all-entity targets (nakshatra/rashi/tithi/vara/akshara).
# These definitions intentionally override earlier v3.5 helper definitions above.
# ═════════════════════════════════════════════════════════════

_CENTER_CELL = (4, 4)
_EIGHT_DIRS = [(-1, 0), (-1, 1), (0, 1), (1, 1), (1, 0), (1, -1), (0, -1), (-1, -1)]


def _sign_delta(a: int, b: int) -> int:
    return 1 if b > a else (-1 if b < a else 0)


def _ray_cells(row: int, col: int, dr: int, dc: int, grid_size: int = 9) -> List[Tuple[int, int]]:
    out: List[Tuple[int, int]] = []
    r, c = row + dr, col + dc
    while 0 <= r < grid_size and 0 <= c < grid_size:
        out.append((r, c))
        r += dr
        c += dc
    return out


def _rotate_dir(dr: int, dc: int, steps: int) -> Tuple[int, int]:
    """Rotate an 8-way direction by 45-degree steps."""
    try:
        idx = _EIGHT_DIRS.index((dr, dc))
    except ValueError:
        # Should not happen, but use north as safe fallback.
        idx = 0
    return _EIGHT_DIRS[(idx + steps) % len(_EIGHT_DIRS)]


def _traditional_sbc_rays(row: int, col: int, grid_size: int = 9) -> Dict[str, List[Tuple[int, int]]]:
    """
    Traditional Sarvatobhadra outer-nakshatra rays.

    For a planet on an outer nakshatra, vedha is drawn as THREE lines:
      1) one straight line along the same side of the chakra
      2) one inward diagonal
      3) the other inward diagonal

    This fixes the visible cases:
      • Rahu in Mula includes the straight bottom-line vedha through Abhijit.
      • Ketu in Magha includes the up-left diagonal vedha to Ashlesha.
      • Sun in Bharani includes the up-right diagonal vedha to Krittika.

    Direction labels are kept as vama/sammukha/dakshina for compatibility:
      sammukha = straight side line
      vama     = first diagonal
      dakshina = second diagonal
    """
    last = grid_size - 1

    def ray(dr: int, dc: int) -> List[Tuple[int, int]]:
        return _ray_cells(row, col, dr, dc, grid_size)

    def same_row() -> List[Tuple[int, int]]:
        return [(row, c) for c in range(grid_size) if c != col]

    def same_col() -> List[Tuple[int, int]]:
        return [(r, col) for r in range(grid_size) if r != row]

    # Top/East side nakshatras: straight horizontal + two inward diagonals
    if row == 0 and 0 < col < last:
        return {"sammukha": same_row(), "vama": ray(1, -1), "dakshina": ray(1, 1)}

    # Right/North side nakshatras: straight vertical + two inward diagonals
    if col == last and 0 < row < last:
        return {"sammukha": same_col(), "vama": ray(-1, -1), "dakshina": ray(1, -1)}

    # Bottom/West side nakshatras: straight horizontal + two inward diagonals
    if row == last and 0 < col < last:
        return {"sammukha": same_row(), "vama": ray(-1, -1), "dakshina": ray(-1, 1)}

    # Left/South side nakshatras: straight vertical + two inward diagonals
    if col == 0 and 0 < row < last:
        return {"sammukha": same_col(), "vama": ray(-1, 1), "dakshina": ray(1, 1)}

    # Fallback for non-outer cells: use center-facing front + adjacent rays.
    dr = _sign_delta(row, _CENTER_CELL[0])
    dc = _sign_delta(col, _CENTER_CELL[1])
    if dr == 0 and dc == 0:
        dr, dc = -1, 0
    return {
        "sammukha": ray(dr, dc),
        "vama": ray(*_rotate_dir(dr, dc, -1)),
        "dakshina": ray(*_rotate_dir(dr, dc, 1)),
    }


def _sbc_direction_vectors(row: int, col: int) -> Dict[str, Tuple[int, int]]:
    """
    Backward-compatible vector summary for UI labels.
    Real hit/line calculation uses _traditional_sbc_rays() because the straight
    side-line has two endpoints, not just one vector.
    """
    last = _GRID_SIZE - 1 if '_GRID_SIZE' in globals() else 8
    if row == 0 and 0 < col < last:
        return {"sammukha": (0, 1), "vama": (1, -1), "dakshina": (1, 1)}
    if col == last and 0 < row < last:
        return {"sammukha": (1, 0), "vama": (-1, -1), "dakshina": (1, -1)}
    if row == last and 0 < col < last:
        return {"sammukha": (0, -1), "vama": (-1, -1), "dakshina": (-1, 1)}
    if col == 0 and 0 < row < last:
        return {"sammukha": (-1, 0), "vama": (-1, 1), "dakshina": (1, 1)}
    dr = _sign_delta(row, _CENTER_CELL[0])
    dc = _sign_delta(col, _CENTER_CELL[1])
    if dr == 0 and dc == 0:
        dr, dc = -1, 0
    return {"sammukha": (dr, dc), "vama": _rotate_dir(dr, dc, -1), "dakshina": _rotate_dir(dr, dc, 1)}


def _directions_for_mode(vedha_mode: str) -> List[str]:
    if vedha_mode in ("three_way", "sthana"):
        return ["vama", "sammukha", "dakshina"]
    if vedha_mode == "left":
        return ["vama"]
    if vedha_mode == "right":
        return ["dakshina"]
    if vedha_mode == "front":
        return ["sammukha"]
    return ["sammukha"]


def get_vedha_cells(
    row: int,
    col: int,
    grid_size: int = 9,
    planet: str = "",
    speed: float = 1.0,
) -> Dict[str, List[Tuple[int, int]]]:
    """
    Sun, Moon, Rahu, Ketu always activate all three traditional rays.
    Other planets activate based on speed:
      stationary -> all 3 rays
      retrograde -> dakshina ray
      fast       -> vama ray
      normal     -> sammukha/straight ray

    For outer nakshatras the three rays are:
      • one straight line along the side of the chakra
      • two diagonals going inward across the chakra
    """
    vedha_info = classify_vedha_type(planet, speed)
    vedha_mode = vedha_info["vedha_mode"]
    rays = _traditional_sbc_rays(row, col, grid_size)
    active = _directions_for_mode(vedha_mode)

    by_dir: Dict[str, List[Tuple[int, int]]] = {}
    all_cells: Set[Tuple[int, int]] = set()
    for d in active:
        cells = rays.get(d, [])
        by_dir[d] = cells
        all_cells.update(cells)

    return {
        "vama": by_dir.get("vama", []),
        "dakshina": by_dir.get("dakshina", []),
        "sammukha": by_dir.get("sammukha", []),
        # backward-compatible keys expected by older frontend/tests
        "horizontal": by_dir.get("sammukha", []) if row in (0, grid_size - 1) else [],
        "vertical": by_dir.get("sammukha", []) if col in (0, grid_size - 1) else [],
        "diagonal1": by_dir.get("vama", []),
        "diagonal2": by_dir.get("dakshina", []),
        "all": sorted(all_cells),
        "vedha_type": vedha_info["type"],
        "vedha_mode": vedha_mode,
        "vedha_side": vedha_info["vedha_side"],
        "is_three_way": vedha_mode in ("three_way", "sthana"),
        "active_directions": active,
    }


def _line_endpoints_for_ray(row: int, col: int, direction: str, ray: List[Tuple[int, int]]) -> List[Dict]:
    """Convert one logical ray into one or more UI line segments."""
    if not ray:
        return []
    # The straight side-line is stored as all same-row/same-col cells. Draw it
    # as a full edge-to-edge line through the source so Rahu in Mula visibly
    # crosses Abhijit, and similar side-line cases render correctly.
    same_r = all(r == row for r, _ in ray)
    same_c = all(c == col for _, c in ray)
    if direction == "sammukha" and same_r:
        # Draw both halves from the planet cell. The UI then anchors x1/y1
        # at the planet pada instead of starting from a corner cell.
        lo = min(c for _, c in ray + [(row, col)])
        hi = max(c for _, c in ray + [(row, col)])
        out = []
        if lo != col:
            out.append({"type": direction, "from": [row, col], "to": [row, lo]})
        if hi != col:
            out.append({"type": direction, "from": [row, col], "to": [row, hi]})
        return out
    if direction == "sammukha" and same_c:
        # Draw both halves from the planet cell so the line visually starts
        # from the active pada inside that nakshatra box.
        lo = min(r for r, _ in ray + [(row, col)])
        hi = max(r for r, _ in ray + [(row, col)])
        out = []
        if lo != row:
            out.append({"type": direction, "from": [row, col], "to": [lo, col]})
        if hi != row:
            out.append({"type": direction, "from": [row, col], "to": [hi, col]})
        return out
    end = ray[-1]
    return [{"type": direction, "from": [row, col], "to": [end[0], end[1]]}]


def get_vedha_lines(
    planet_name: str,
    row: int,
    col: int,
    speed: float,
    grid_size: int = 9,
) -> Dict:
    """UI line data generated from the exact same rays used for hit detection."""
    vedha_info = classify_vedha_type(planet_name, speed)
    cells = get_vedha_cells(row, col, grid_size=grid_size, planet=planet_name, speed=speed)
    vectors = _sbc_direction_vectors(row, col)
    lines: List[Dict] = []
    for d in cells["active_directions"]:
        ray = cells.get(d, [])
        for seg in _line_endpoints_for_ray(row, col, d, ray):
            seg["vector"] = list(vectors.get(d, (0, 0)))
            lines.append(seg)

    return {
        "planet": planet_name,
        "position": [row, col],
        "speed": round(speed, 4),
        "vedha_type": vedha_info["type"],
        "vedha_mode": vedha_info["vedha_mode"],
        "vedha_side": vedha_info["vedha_side"],
        "is_three_way": vedha_info["vedha_mode"] in ("three_way", "sthana"),
        "strength": vedha_info["strength"],
        "strength_multiplier": VEDHA_STRENGTH_MULTIPLIER.get(vedha_info["type"], 1.0),
        "line_style": vedha_info["line_style"],
        "description": vedha_info["description"],
        "active_directions": cells["active_directions"],
        "lines": lines,
    }


def get_per_nakshatra_vedha_targets(
    planet_nakshatra: str,
    vedha_mode: str,
) -> Optional[List[str]]:
    """
    Corrected target lookup using the live traditional grid.

    Earlier table contained only nakshatras and therefore missed the actual SBC
    layers: akshara, rashi, tithi, vara, and special cells. This function now
    derives targets from the same ray geometry used by get_vedha_cells(), so
    backend hits and frontend lines stay synchronized.
    """
    try:
        from app.himanshu_sarvatobhdra import SarvatobhadraChakra, EntityType
    except Exception:
        return None

    chakra = SarvatobhadraChakra()
    pos = chakra.find_entity(EntityType.NAKSHATRA, planet_nakshatra)
    if not pos:
        return None
    row, col = pos

    # Use dummy planet names/speeds to reuse mode classification shape without
    # altering the caller's already-classified mode.
    vectors = _sbc_direction_vectors(row, col)
    active = _directions_for_mode(vedha_mode)
    names: List[str] = []
    seen: Set[str] = set()
    for d in active:
        dr, dc = vectors[d]
        for r, c in _ray_cells(row, col, dr, dc, chakra.GRID_SIZE):
            for ent in chakra.grid[r][c].entities:
                # skip empty/special-only artifacts only if they are not useful;
                # keep Brahma because center hits matter in some SBC traditions.
                if ent.name not in seen:
                    names.append(ent.name)
                    seen.add(ent.name)
    return names
