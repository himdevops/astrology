"""
gold_predictor.py — Vedic Gold Price Prediction Engine v2.0

Based on Sarvatobhadra Chakra (Khemraj Publishers) Ardha Prakaran:
- Shlokas 245-246: Papa vedha = commodity expensive, Shubha vedha = commodity cheap
- Shlokas 345-406: Per-nakshatra commodity mapping with direction & duration
- Shlokas 349-360: Desh-Kaal-Panya (Place-Time-Commodity) lords & bala
- Shlokas 161-167: Graha Bala for vedha strength weighting
- Shlokas 55-56:  Dynamic nature (Ksheena Chandra, Krura-yukta Budha)
- Shloka 220:     Ubhayato Vedha — double-sided malefic = extreme signal
- Shloka 337:     Retrograde benefic vedha = ati shubha

v2.0 Additions:
- SBC Vedha integration — actual vedha geometry on gold nakshatra cells
- All-planet nakshatra scoring — Jupiter/Sun/Mars/Saturn in gold nakshatras
- Vedha on gold rulers — malefic vedha on Sun/Jupiter's nakshatra position
- Dynamic planet nature classification (Ksheena Chandra / Krura-yukta Budha)
- Graha Bala (sign dignity × motion multiplier) for vedha weight
- Ubhayato vedha detection for extreme gold signals

Gold Rulers: Sun (primary), Jupiter (secondary), Venus (luxury)
Gold Nakshatras: Punarvasu (383), Pushya (384), Chitra (390), Dhanishtha (400)
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Set

import swisseph as swe

from app.core import PLANETS, SIGNS, AYANAMSA_MAP, normalize_degree, degree_to_sign
from app.nakshatra import NAKSHATRAS, NAKSHATRA_FINANCIAL, get_nakshatra
from app.sbc_analysis import (
    get_vedha_cells,
    classify_planet_nature,
    calc_graha_bala,
)
from app.himanshu_sarvatobhdra import OUTER_NAK_POSITIONS

# ─────────────────────────────────────────────────────────────
# Constants
# ─────────────────────────────────────────────────────────────

GOLD_PLANETS = ["Sun", "Jupiter"]        # Primary gold rulers
GOLD_SUPPORT = ["Venus", "Saturn"]       # Secondary (Venus=luxury, Saturn=iron/pressure)
ALL_PLANETS = ["Sun", "Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Rahu", "Ketu"]

PLANET_NATURE = {
    "Sun": "malefic", "Moon": "benefic", "Mars": "malefic",
    "Mercury": "neutral", "Jupiter": "benefic", "Venus": "benefic",
    "Saturn": "malefic", "Rahu": "malefic", "Ketu": "malefic",
}

PLANET_COLORS = {
    "Sun": "#FFA500", "Moon": "#C0C0C0", "Mars": "#FF4444",
    "Mercury": "#00CED1", "Jupiter": "#FFD700", "Venus": "#FF69B4",
    "Saturn": "#4169E1", "Rahu": "#8B008B", "Ketu": "#808080",
}

# ─────────────────────────────────────────────────────────────
# Rule 1: Planet-Commodity Effects (Shlokas 245-246)
# पापग्रह वेध से वस्तु महंगी, शुभग्रह वेध से सस्ती
# Malefic vedha on gold ruler = gold price RISES (expensive)
# Benefic vedha on gold ruler = gold price FALLS (cheap)
# ─────────────────────────────────────────────────────────────

PLANET_GOLD_EFFECT = {
    # How each planet's transit affects gold
    "Sun":     {"gold_role": "primary_ruler", "effect": "rise",
                "reason": "Sun rules gold (suvarna). Papa vedha on Sun = scarcity = price rise",
                "weight": 1.0, "shloka": "245-246"},
    "Jupiter": {"gold_role": "secondary_ruler", "effect": "rise_when_strong",
                "reason": "Jupiter rules banking/prosperity. Strong Jupiter = gold demand from prosperity",
                "weight": 0.8, "shloka": "245-246, 354"},
    "Venus":   {"gold_role": "luxury_demand", "effect": "rise",
                "reason": "Venus rules luxury goods. Strong Venus = jewelry demand = gold price up",
                "weight": 0.5, "shloka": "350"},
    "Saturn":  {"gold_role": "pressure", "effect": "rise_on_retro",
                "reason": "Saturn creates chronic market pressure. Retro Saturn = gold safe haven",
                "weight": 0.6, "shloka": "245"},
    "Mars":    {"gold_role": "conflict", "effect": "rise",
                "reason": "Mars = conflict/war. Strong Mars = geopolitical tension = gold rises",
                "weight": 0.4, "shloka": "245"},
    "Moon":    {"gold_role": "sentiment", "effect": "indirect",
                "reason": "Moon = public sentiment. Ksheena (waning) Moon = fear = gold demand",
                "weight": 0.3, "shloka": "246"},
    "Mercury": {"gold_role": "trade", "effect": "fall_when_strong",
                "reason": "Mercury = commerce/trade. Strong Mercury = equity markets up = gold down",
                "weight": 0.3, "shloka": "354"},
    "Rahu":    {"gold_role": "foreign", "effect": "volatile",
                "reason": "Rahu = foreign influences, sudden events. Rahu vedha = gold volatility",
                "weight": 0.5, "shloka": "245"},
    "Ketu":    {"gold_role": "spiritual", "effect": "fall",
                "reason": "Ketu = detachment, reversal. Ketu influence = gold correction",
                "weight": 0.3, "shloka": "245"},
}

# ─────────────────────────────────────────────────────────────
# Rule 2: Per-Nakshatra Gold Commodity Mapping (Shlokas 379-406)
# Which nakshatras specifically affect gold when vedha occurs
# ─────────────────────────────────────────────────────────────

NAKSHATRA_GOLD_RULES = {
    # Nakshatras that directly mention gold (suvarna/swarna/hema)
    "Punarvasu":  {"gold": True, "commodities": ["Gold", "Silver", "Cotton"],
                   "direction": "North", "duration_months": 2, "shloka": "383",
                   "detail": "स्वर्ण रूप्ये कपासिश्च — Gold, Silver, Cotton affected"},
    "Pushya":     {"gold": True, "commodities": ["Gold", "Ghee", "Silver", "Rice", "Mustard"],
                   "direction": "South", "duration_months": 8, "shloka": "384",
                   "detail": "पुष्ये स्वर्ण घृतं रूप्यं — Gold, Ghee, Silver, Rice, Rock salt, Mustard"},
    "Chitra":     {"gold": True, "commodities": ["Gold", "Gems", "Moong", "Coral", "Horses"],
                   "direction": "North", "duration_months": 2, "shloka": "390",
                   "detail": "चित्रायां स्वर्णरत्नानि — Gold, Gems, Moong, Urad, Coral"},
    "Dhanishtha": {"gold": True, "commodities": ["Gold", "Silver", "Metals", "Gems", "Pearls"],
                   "direction": "East", "duration_days": 7, "shloka": "400",
                   "detail": "स्वर्णरूप्यधातवः — Gold, Silver, all metals, gems, pearls, currency"},
    # Nakshatras that mention metals/dhatu (indirect gold effect)
    "Krittika":   {"gold": False, "commodities": ["Rice", "Gems", "Diamond", "Metals", "Sesame"],
                   "direction": "South", "duration_months": 8, "shloka": "379",
                   "detail": "व्रीहियवाश्च मणयो हीरका धातवस्तिलाः — Metals & gems"},
    "Rohini":     {"gold": False, "commodities": ["All grains", "All metals", "All liquids"],
                   "direction": "East", "duration_days": 7, "shloka": "380",
                   "detail": "सर्वधान्यानि सर्वे रसाश्च धातवः — All metals affected"},
    "Mrigashira": {"gold": False, "commodities": ["Horses", "Cattle", "Gems", "Lac"],
                   "direction": "North", "duration_months": 2, "shloka": "381"},
    "Ardra":      {"gold": False, "commodities": ["Oil", "Salt", "Chemicals", "Sandalwood"],
                   "direction": "West", "duration_months": 1, "shloka": "382"},
    "Ashlesha":   {"gold": False, "commodities": ["Manjishtha", "Sugarcane", "Wheat", "Pepper"],
                   "direction": "West", "duration_months": 9, "shloka": "385"},
    "Magha":      {"gold": False, "commodities": ["Sesame", "Oil", "Ghee", "Coral", "Gram", "Jaggery"],
                   "direction": "South", "duration_months": 8, "shloka": "386"},
    "Purva Phalguni": {"gold": False, "commodities": ["Wool", "Silver items", "Sesame"],
                   "direction": "South", "duration_months": 8, "shloka": "387"},
    "Uttara Phalguni": {"gold": False, "commodities": ["Urad", "Moong", "Rice", "Garlic"],
                   "direction": "North", "duration_months": 2, "shloka": "388"},
    "Hasta":      {"gold": False, "commodities": ["Sandalwood", "Camphor", "Devdaru"],
                   "direction": "North", "duration_months": 2, "shloka": "389"},
    "Swati":      {"gold": False, "commodities": ["Betel nut", "Pepper", "Mustard oil", "Asafoetida"],
                   "direction": "North", "duration_days": 7, "shloka": "391"},
    "Vishakha":   {"gold": False, "commodities": ["Barley", "Rice", "Wheat", "Moong", "Masoor"],
                   "direction": "South", "duration_months": 8, "shloka": "392"},
    "Anuradha":   {"gold": False, "commodities": ["Tuvar", "Lentils", "Rice", "Gram"],
                   "direction": "East", "duration_days": 7, "shloka": "393"},
    "Jyeshtha":   {"gold": False, "commodities": ["Guggul", "Jaggery", "Lac", "Camphor", "Mercury metal"],
                   "direction": "East", "duration_days": 7, "shloka": "394"},
    "Mula":       {"gold": False, "commodities": ["White goods", "Cotton", "Salt", "Grains"],
                   "direction": "West", "duration_months": 1, "shloka": "395"},
    "Purva Ashadha": {"gold": False, "commodities": ["Surma", "Ghee", "Turmeric", "Rice"],
                   "direction": "West", "duration_months": 1, "shloka": "396"},
    "Uttara Ashadha": {"gold": False, "commodities": ["Horses", "Cattle", "Iron", "Metals", "Ghee"],
                   "direction": "East", "duration_days": 7, "shloka": "397",
                   "detail": "लोहादिधातवः — Iron and metals affected"},
    "Abhijit":    {"gold": False, "commodities": ["Raisins", "Dates", "Betel nut", "Cardamom", "Moong"],
                   "direction": "East", "duration_days": 7, "shloka": "398"},
    "Shravana":   {"gold": False, "commodities": ["Walnut", "Chironji", "Pippali", "Betel garden"],
                   "direction": "East", "duration_days": 7, "shloka": "399"},
    "Shatabhisha": {"gold": False, "commodities": ["Oil", "Kodra", "Liquor", "Bark", "Roots"],
                   "direction": "West", "duration_months": 1, "shloka": "401"},
    "Purva Bhadrapada": {"gold": False, "commodities": ["Priyangu", "Nutmeg", "All grains", "All metals", "Medicines"],
                   "direction": "South", "duration_months": 8, "shloka": "402",
                   "detail": "सर्वधान्यानि धातवः — All grains and metals"},
    "Uttara Bhadrapada": {"gold": False, "commodities": ["Jaggery", "Sugar", "Sesame", "Rice", "Ghee", "Gems", "Pearls"],
                   "direction": "West", "duration_months": 1, "shloka": "403"},
    "Revati":     {"gold": False, "commodities": ["Coconut", "Betel nut", "Pearls", "Gems", "Grocery"],
                   "direction": "West", "duration_months": 1, "shloka": "404"},
    "Ashwini":    {"gold": False, "commodities": ["Rice", "Grass", "Mule", "Camel", "Ghee", "All grains", "Cloth"],
                   "direction": "North", "duration_months": 2, "shloka": "405"},
    "Bharani":    {"gold": False, "commodities": ["Husk grains", "Juwar", "Pepper", "All medicines"],
                   "direction": "South", "duration_months": 8, "shloka": "406"},
}

# ─────────────────────────────────────────────────────────────
# Rule 3: Kaal-Panya Lords (Shloka 349-354)
# Jupiter sankranti = year, Sun sankranti = month, Sunrise = day
# Dhatu lords: Saturn, Rahu, Mars
# Gold falls under Dhatu category
# ─────────────────────────────────────────────────────────────

KAAL_LORDS = {
    "year":  ["Rahu", "Ketu", "Saturn", "Jupiter"],  # Varsha swami (349/353)
    "month": ["Mars", "Sun", "Mercury", "Venus"],     # Masa swami (353)
    "day":   ["Moon"],                                  # Dina swami = always Moon (353)
}

PANYA_LORDS = {
    "dhatu":  ["Saturn", "Rahu", "Mars"],    # Gold, Silver, Iron, Metals (354)
    "mool":   ["Ketu", "Venus", "Sun"],      # Cotton, Grains, Oil (354)
    "jeev":   ["Mercury", "Moon", "Jupiter"], # Animals, Dairy (354)
}

# ─────────────────────────────────────────────────────────────
# Rule 4: Graha Bala for Vedha Strength (Shloka 358-360)
# Kshetra bala: own=4, friend=3, neutral=2, enemy=1
# Vakra bala: retrograde planet = stronger vedha
# Uccha bala: exalted = full, debilitated = half
# ─────────────────────────────────────────────────────────────

PLANET_DIGNITY = {
    # own_signs, exaltation_sign, debilitation_sign, friends, enemies
    "Sun":     {"own": [4], "exalt": 0, "debil": 6, "friends": [3,4,7,11], "enemies": [6,9,10]},
    "Moon":    {"own": [3], "exalt": 1, "debil": 7, "friends": [0,3], "enemies": []},
    "Mars":    {"own": [0,7], "exalt": 9, "debil": 3, "friends": [3,4,11], "enemies": [1,5]},
    "Mercury": {"own": [2,5], "exalt": 5, "debil": 11, "friends": [4,6,8], "enemies": [3]},
    "Jupiter": {"own": [8,11], "exalt": 3, "debil": 9, "friends": [0,3,4], "enemies": [1,5]},
    "Venus":   {"own": [1,6], "exalt": 11, "debil": 5, "friends": [2,5,9,10], "enemies": [0,3]},
    "Saturn":  {"own": [9,10], "exalt": 6, "debil": 0, "friends": [1,5,8], "enemies": [0,3,4]},
}

# ─────────────────────────────────────────────────────────────
# Rule 5: Sign-based Gold Effects
# Fire signs (Aries, Leo, Sag) = bullish gold (Sun strong)
# Earth signs (Taurus, Virgo, Cap) = stable gold
# Air signs (Gemini, Libra, Aqua) = bearish (trade/equity focus)
# Water signs (Cancer, Scorpio, Pisces) = fear/sentiment = gold up
# ─────────────────────────────────────────────────────────────

SIGN_GOLD_EFFECT = {
    "Aries":       {"element": "Fire",  "gold_effect": 0.3,  "reason": "Mars sign — conflict energy, gold up"},
    "Taurus":      {"element": "Earth", "gold_effect": 0.5,  "reason": "Venus sign — luxury demand, gold stable/up"},
    "Gemini":      {"element": "Air",   "gold_effect": -0.2, "reason": "Mercury sign — trade focus, gold neutral"},
    "Cancer":      {"element": "Water", "gold_effect": 0.4,  "reason": "Moon sign — emotional buying, gold up"},
    "Leo":         {"element": "Fire",  "gold_effect": 0.6,  "reason": "Sun's own sign — gold ruler strong, gold up"},
    "Virgo":       {"element": "Earth", "gold_effect": -0.1, "reason": "Mercury sign — analytical, gold neutral"},
    "Libra":       {"element": "Air",   "gold_effect": 0.2,  "reason": "Venus sign — jewelry demand"},
    "Scorpio":     {"element": "Water", "gold_effect": 0.5,  "reason": "Mars sign — crisis/fear = gold safe haven"},
    "Sagittarius": {"element": "Fire",  "gold_effect": 0.3,  "reason": "Jupiter sign — expansion/banking"},
    "Capricorn":   {"element": "Earth", "gold_effect": 0.1,  "reason": "Saturn sign — caution, slow gold"},
    "Aquarius":    {"element": "Air",   "gold_effect": -0.3, "reason": "Saturn sign — tech/innovation focus, gold down"},
    "Pisces":      {"element": "Water", "gold_effect": 0.4,  "reason": "Jupiter sign — spiritual demand, gold up"},
}

# ─────────────────────────────────────────────────────────────
# Rule 6: Retrograde Effects on Gold
# ─────────────────────────────────────────────────────────────

RETRO_GOLD_EFFECT = {
    "Jupiter": {"retro_effect": 0.5,  "reason": "Jupiter retro = banking stress = gold safe haven rise",
                "shloka": "337: शुभग्रह वक्रगति में दृष्टिफल अति शुभ"},
    "Venus":   {"retro_effect": 0.4,  "reason": "Venus retro = luxury re-evaluation = gold demand shift"},
    "Saturn":  {"retro_effect": 0.6,  "reason": "Saturn retro = chronic market fear = gold rises sharply"},
    "Mercury": {"retro_effect": 0.3,  "reason": "Mercury retro = trade disruption = mild gold support"},
    "Mars":    {"retro_effect": 0.4,  "reason": "Mars retro = military tension review = gold volatility"},
}


# ─────────────────────────────────────────────────────────────
# SBC Grid — Nakshatra positions for vedha geometry
# Build reverse map: nakshatra_name → (row, col)
# ─────────────────────────────────────────────────────────────

NAK_TO_GRID: Dict[str, Tuple[int, int]] = {
    name: (r, c) for (r, c), name in OUTER_NAK_POSITIONS.items()
}

# Gold nakshatras set (for fast lookup)
GOLD_NAKSHATRAS: Set[str] = {"Punarvasu", "Pushya", "Chitra", "Dhanishtha"}

# Metal/Dhatu nakshatras — mention metals broadly (indirect gold support)
METAL_NAKSHATRAS: Set[str] = {
    "Krittika", "Rohini", "Uttara Ashadha", "Purva Bhadrapada", "Dhanishtha",
}

# All-planet nakshatra weights for gold scoring
# How important is each planet sitting in a gold nakshatra?
PLANET_NAK_GOLD_WEIGHT: Dict[str, float] = {
    "Sun":     1.5,   # Primary gold ruler — highest weight
    "Jupiter": 1.2,   # Secondary ruler — banking/prosperity
    "Mars":    0.8,   # Dhatu lord — metals/conflict
    "Saturn":  0.7,   # Dhatu lord — pressure/fear
    "Moon":    0.6,   # Sentiment — daily trigger
    "Venus":   0.5,   # Luxury/jewelry demand
    "Rahu":    0.5,   # Foreign/volatile influence
    "Mercury": 0.3,   # Trade — indirect
    "Ketu":    0.3,   # Reversal — indirect
}


# ─────────────────────────────────────────────────────────────
# SBC Vedha Scoring for Gold
# ─────────────────────────────────────────────────────────────

def _score_all_planet_nakshatras(positions: Dict[str, Dict]) -> Dict:
    """
    Rule 9: Score ALL planets' nakshatra positions for gold effect.
    (Shlokas 379-406 — per-nakshatra commodity mapping)

    When ANY planet sits in a gold nakshatra, it generates a gold signal.
    Weight depends on planet importance for gold.
    Malefic in gold nakshatra = gold RISES (scarcity/tension).
    Benefic in gold nakshatra = gold RISES (prosperity demand).
    """
    total_score = 0.0
    hits = []

    for pname, pdata in positions.items():
        nak = pdata.get("nakshatra", "")
        if not nak:
            continue

        nak_rule = NAKSHATRA_GOLD_RULES.get(nak, {})
        weight = PLANET_NAK_GOLD_WEIGHT.get(pname, 0.3)
        bala = pdata.get("kshetra_bala", 0.5)

        if nak_rule.get("gold", False):
            # Direct gold nakshatra — strong signal
            effect = weight * bala
            total_score += effect
            hits.append({
                "planet": pname,
                "nakshatra": nak,
                "type": "gold_nakshatra",
                "score": round(effect, 2),
                "shloka": nak_rule.get("shloka", "379-406"),
                "detail": nak_rule.get("detail", ""),
                "commodities": nak_rule.get("commodities", []),
            })
        elif nak in METAL_NAKSHATRAS:
            # Metal/dhatu nakshatra — mild gold support
            effect = weight * bala * 0.4
            total_score += effect
            hits.append({
                "planet": pname,
                "nakshatra": nak,
                "type": "metal_nakshatra",
                "score": round(effect, 2),
                "shloka": nak_rule.get("shloka", ""),
                "detail": nak_rule.get("detail", f"{nak} mentions metals/dhatu"),
                "commodities": nak_rule.get("commodities", []),
            })

    return {
        "score": round(total_score, 2),
        "hits": hits,
        "count": len(hits),
    }


def _score_sbc_vedha(positions: Dict[str, Dict], transit_planets_list: List[Dict]) -> Dict:
    """
    Rule 10: SBC Vedha on gold nakshatras & gold rulers' nakshatras.
    (Shlokas 245-246 — Papa vedha = gold expensive, Shubha vedha = gold cheap)

    Checks two things:
    A) Do any planets vedha a GOLD NAKSHATRA cell in the SBC grid?
       Papa vedha → gold RISES | Shubha vedha → gold FALLS
    B) Do any planets vedha the nakshatra where SUN or JUPITER currently sit?
       Papa vedha on gold ruler → gold RISES sharply

    Uses actual SBC get_vedha_cells() geometry for accuracy.
    """
    total_score = 0.0
    vedha_hits = []

    # Build positions of gold nakshatras on SBC grid
    gold_nak_cells: Dict[Tuple[int, int], str] = {}
    for gnak in GOLD_NAKSHATRAS:
        pos = NAK_TO_GRID.get(gnak)
        if pos:
            gold_nak_cells[pos] = gnak

    # Build position of gold rulers' current nakshatras
    ruler_nak_cells: Dict[Tuple[int, int], Dict] = {}
    for ruler in ["Sun", "Jupiter"]:
        rdata = positions.get(ruler, {})
        rnak = rdata.get("nakshatra", "")
        rpos = NAK_TO_GRID.get(rnak)
        if rpos:
            ruler_nak_cells[rpos] = {"planet": ruler, "nakshatra": rnak}

    # Classify planet natures dynamically
    sun_lon = positions.get("Sun", {}).get("longitude", 0.0)
    moon_lon = positions.get("Moon", {}).get("longitude", 0.0)

    # For each transit planet, compute vedha cells and check hits
    for tp in transit_planets_list:
        pname = tp.get("planet", "")
        nak = tp.get("nakshatra", "")
        speed = tp.get("speed", 0.0)
        longitude = tp.get("longitude", 0.0)
        sign = tp.get("sign", "")

        # Get planet's position on SBC grid
        planet_pos = NAK_TO_GRID.get(nak)
        if not planet_pos:
            continue

        # Classify nature
        nature_info = classify_planet_nature(pname, transit_planets_list, moon_lon, sun_lon)
        p_nature = nature_info["nature"]
        is_malefic = (p_nature == "malefic")

        # Calculate graha bala for vedha strength
        gbala = calc_graha_bala(pname, longitude, speed, sign)
        bala_factor = gbala.get("graha_bala", 0.5)

        # Get vedha cells from this planet's position
        vedha = get_vedha_cells(
            row=planet_pos[0], col=planet_pos[1],
            grid_size=9, planet=pname, speed=speed,
        )
        all_vedha_cells = set(vedha.get("all", []))

        # ── Check A: Vedha on gold nakshatra cells ──
        for gcell, gnak_name in gold_nak_cells.items():
            if gcell in all_vedha_cells:
                if is_malefic:
                    # Papa vedha on gold nakshatra = gold RISES (Shloka 245)
                    effect = 0.6 * bala_factor
                    total_score += effect
                    vedha_hits.append({
                        "vedha_planet": pname,
                        "vedha_nature": "papa",
                        "target": gnak_name,
                        "target_type": "gold_nakshatra",
                        "score": round(effect, 2),
                        "direction": "bullish",
                        "shloka": "245",
                        "detail": f"Papa ({pname}) vedha on {gnak_name} → gold expensive",
                        "graha_bala": round(bala_factor, 2),
                        "vedha_mode": vedha.get("vedha_mode", ""),
                    })
                else:
                    # Shubha vedha on gold nakshatra = gold FALLS (Shloka 246)
                    effect = -0.4 * bala_factor
                    total_score += effect
                    vedha_hits.append({
                        "vedha_planet": pname,
                        "vedha_nature": "shubha",
                        "target": gnak_name,
                        "target_type": "gold_nakshatra",
                        "score": round(effect, 2),
                        "direction": "bearish",
                        "shloka": "246",
                        "detail": f"Shubha ({pname}) vedha on {gnak_name} → gold cheap",
                        "graha_bala": round(bala_factor, 2),
                        "vedha_mode": vedha.get("vedha_mode", ""),
                    })

        # ── Check B: Vedha on gold rulers' nakshatra positions ──
        for rcell, rinfo in ruler_nak_cells.items():
            if rcell in all_vedha_cells:
                # Don't vedha yourself
                if pname == rinfo["planet"]:
                    continue
                if is_malefic:
                    # Papa vedha on Sun/Jupiter's nakshatra = strong gold signal
                    effect = 0.8 * bala_factor
                    total_score += effect
                    vedha_hits.append({
                        "vedha_planet": pname,
                        "vedha_nature": "papa",
                        "target": f"{rinfo['planet']} in {rinfo['nakshatra']}",
                        "target_type": "gold_ruler",
                        "score": round(effect, 2),
                        "direction": "strongly bullish",
                        "shloka": "245-246",
                        "detail": f"Papa ({pname}) vedha on {rinfo['planet']}'s nakshatra {rinfo['nakshatra']} → gold rises sharply",
                        "graha_bala": round(bala_factor, 2),
                        "vedha_mode": vedha.get("vedha_mode", ""),
                    })
                else:
                    # Shubha vedha on gold ruler = mild stabilization
                    effect = -0.3 * bala_factor
                    total_score += effect
                    vedha_hits.append({
                        "vedha_planet": pname,
                        "vedha_nature": "shubha",
                        "target": f"{rinfo['planet']} in {rinfo['nakshatra']}",
                        "target_type": "gold_ruler",
                        "score": round(effect, 2),
                        "direction": "mildly bearish",
                        "shloka": "246",
                        "detail": f"Shubha ({pname}) vedha on {rinfo['planet']}'s nakshatra → gold stabilizes",
                        "graha_bala": round(bala_factor, 2),
                        "vedha_mode": vedha.get("vedha_mode", ""),
                    })

    # ── Ubhayato Vedha detection (Shloka 220) ──
    # If 2+ malefic planets vedha the SAME gold nakshatra from opposite sides
    ubhayato_hits = []
    papa_vedha_on_gold: Dict[str, List[str]] = {}  # gold_nak → list of papa planets
    for vh in vedha_hits:
        if vh["vedha_nature"] == "papa" and vh["target_type"] == "gold_nakshatra":
            tgt = vh["target"]
            papa_vedha_on_gold.setdefault(tgt, []).append(vh["vedha_planet"])

    for gnak, planets in papa_vedha_on_gold.items():
        if len(planets) >= 2:
            ubhayato_score = 1.5
            total_score += ubhayato_score
            ubhayato_hits.append({
                "target": gnak,
                "planets": planets,
                "score": ubhayato_score,
                "shloka": "220",
                "detail": f"Ubhayato Vedha: {', '.join(planets)} both vedha {gnak} → EXTREME gold rise signal",
            })

    return {
        "score": round(total_score, 2),
        "vedha_hits": vedha_hits,
        "ubhayato": ubhayato_hits,
        "papa_count": sum(1 for v in vedha_hits if v["vedha_nature"] == "papa"),
        "shubha_count": sum(1 for v in vedha_hits if v["vedha_nature"] == "shubha"),
    }


# ─────────────────────────────────────────────────────────────
# Core Calculation Functions
# ─────────────────────────────────────────────────────────────

def _get_sidereal_pos(jd_ut: float, planet_id: int, ayanamsa_key: str) -> Tuple[float, float]:
    """Get sidereal longitude and speed."""
    swe.set_sid_mode(AYANAMSA_MAP[ayanamsa_key])
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    xx = swe.calc_ut(jd_ut, planet_id, flags)[0]
    return normalize_degree(xx[0]), xx[3]


def _jd_to_dt(jd: float, tz_offset: int = 330) -> datetime:
    y, m, d, h = swe.revjul(jd)
    hours = int(h)
    minutes = int((h - hours) * 60)
    return datetime(y, m, d, hours, minutes) + timedelta(minutes=tz_offset)


def _dt_to_jd(dt: datetime, tz_offset: int = 330) -> float:
    utc = dt - timedelta(minutes=tz_offset)
    return swe.julday(utc.year, utc.month, utc.day,
                      utc.hour + utc.minute / 60.0 + utc.second / 3600.0)


def _get_sign_index(lon: float) -> int:
    return int(lon / 30) % 12


def _get_nak_index(lon: float) -> int:
    return int(lon / (360.0 / 27)) % 27


def _get_kshetra_bala(planet: str, sign_idx: int) -> float:
    """Shloka 358: Own=1.0, Friend=0.75, Neutral=0.5, Enemy=0.25"""
    info = PLANET_DIGNITY.get(planet)
    if not info:
        return 0.5
    if sign_idx in info.get("own", []):
        return 1.0
    if sign_idx == info.get("exalt"):
        return 1.0
    if sign_idx == info.get("debil"):
        return 0.25
    if sign_idx in info.get("friends", []):
        return 0.75
    if sign_idx in info.get("enemies", []):
        return 0.25
    return 0.5


def _compute_planet_positions(jd: float, ayanamsa_key: str) -> Dict[str, Dict]:
    """Get all planet positions at a given JD."""
    positions = {}
    for name in ALL_PLANETS:
        if name == "Ketu":
            pid = PLANETS["Rahu"]
            lon, spd = _get_sidereal_pos(jd, pid, ayanamsa_key)
            lon = normalize_degree(lon + 180)
            spd = -abs(spd)
        else:
            pid = PLANETS.get(name)
            if pid is None:
                continue
            lon, spd = _get_sidereal_pos(jd, pid, ayanamsa_key)

        sign_idx = _get_sign_index(lon)
        nak_idx = _get_nak_index(lon)
        sign_name = SIGNS[sign_idx]
        nak_name = NAKSHATRAS[nak_idx]["name"]
        nak_lord = NAKSHATRAS[nak_idx]["lord"]
        retro = spd < 0

        positions[name] = {
            "longitude": round(lon, 4),
            "sign": sign_name,
            "sign_index": sign_idx,
            "nakshatra": nak_name,
            "nakshatra_index": nak_idx,
            "nakshatra_lord": nak_lord,
            "speed": round(spd, 4),
            "retrograde": retro,
            "kshetra_bala": _get_kshetra_bala(name, sign_idx),
        }
    return positions


# ─────────────────────────────────────────────────────────────
# Gold Signal Scoring — Daily
# ─────────────────────────────────────────────────────────────

def _build_transit_list(positions: Dict[str, Dict]) -> List[Dict]:
    """Convert positions dict to transit_planets list format needed by SBC vedha."""
    result = []
    for pname, pdata in positions.items():
        result.append({
            "planet": pname,
            "nakshatra": pdata.get("nakshatra", ""),
            "longitude": pdata.get("longitude", 0.0),
            "speed": pdata.get("speed", 0.0),
            "sign": pdata.get("sign", ""),
            "retrograde": pdata.get("retrograde", False),
        })
    return result


def _score_day(positions: Dict[str, Dict], date: datetime) -> Dict:
    """
    Score a single day for gold price prediction.
    Returns score (-10 to +10), reasons list, and breakdown.
    Positive = gold price likely to RISE
    Negative = gold price likely to FALL

    Rules 1-8: Original (sign, retro, malefic/benefic strength, ksheena, day lord)
    Rule 9:  All-planet nakshatra gold scoring (Shlokas 379-406)
    Rule 10: SBC Vedha on gold nakshatras & gold rulers (Shlokas 245-246)
    """
    score = 0.0
    reasons = []
    breakdown = {}
    active_rules = []

    # ── Rule 1: Sun's position (gold's primary ruler) ──
    sun = positions.get("Sun", {})
    sun_sign = sun.get("sign", "")
    sun_bala = sun.get("kshetra_bala", 0.5)
    sign_effect = SIGN_GOLD_EFFECT.get(sun_sign, {}).get("gold_effect", 0)
    sun_score = sign_effect * sun_bala * 1.5  # Sun is primary
    score += sun_score
    breakdown["sun_sign"] = {
        "score": round(sun_score, 2),
        "sign": sun_sign,
        "bala": sun_bala,
        "reason": f"Sun in {sun_sign} (bala={sun_bala:.2f})",
    }
    if abs(sun_score) > 0.2:
        reasons.append(f"Sun in {sun_sign} ({'+' if sun_score > 0 else ''}{sun_score:.2f})")
        active_rules.append({"rule": "Sun Sign Position", "shloka": "245-246",
                             "effect": "bullish" if sun_score > 0 else "bearish",
                             "score": round(sun_score, 2)})

    # ── Rule 2: Jupiter's position (secondary ruler) ──
    jup = positions.get("Jupiter", {})
    jup_sign = jup.get("sign", "")
    jup_bala = jup.get("kshetra_bala", 0.5)
    jup_sign_effect = SIGN_GOLD_EFFECT.get(jup_sign, {}).get("gold_effect", 0)
    jup_score = jup_sign_effect * jup_bala * 1.0
    score += jup_score
    breakdown["jupiter_sign"] = {
        "score": round(jup_score, 2),
        "sign": jup_sign,
        "bala": jup_bala,
    }
    if abs(jup_score) > 0.15:
        reasons.append(f"Jupiter in {jup_sign} ({'+' if jup_score > 0 else ''}{jup_score:.2f})")
        active_rules.append({"rule": "Jupiter Sign Position", "shloka": "349, 354",
                             "effect": "bullish" if jup_score > 0 else "bearish",
                             "score": round(jup_score, 2)})

    # ── Rule 3: Moon Nakshatra (daily signal) ──
    moon = positions.get("Moon", {})
    moon_nak = moon.get("nakshatra", "")
    nak_fin = NAKSHATRA_FINANCIAL.get(moon_nak, {})
    nak_score_raw = nak_fin.get("score", 0)
    # Invert for gold: bearish market = bullish gold (safe haven)
    # But also: very bullish market nakshatras like Pushya are ALSO bullish gold
    nak_gold_rule = NAKSHATRA_GOLD_RULES.get(moon_nak, {})
    if nak_gold_rule.get("gold", False):
        # Direct gold nakshatra — strong bullish signal
        moon_gold_score = 1.2
        reasons.append(f"Moon in {moon_nak} — GOLD NAKSHATRA ({nak_gold_rule.get('shloka', '')})")
        active_rules.append({"rule": f"Gold Nakshatra: {moon_nak}", "shloka": nak_gold_rule.get("shloka", ""),
                             "effect": "strongly bullish",
                             "detail": nak_gold_rule.get("detail", ""),
                             "score": 1.2})
    elif nak_score_raw < -0.3:
        # Bearish market nakshatra = gold safe haven
        moon_gold_score = abs(nak_score_raw) * 0.8
        reasons.append(f"Moon in {moon_nak} (bearish market → gold hedge, +{moon_gold_score:.2f})")
        active_rules.append({"rule": f"Safe Haven: {moon_nak}", "shloka": "245-246",
                             "effect": "bullish (hedge)",
                             "score": round(moon_gold_score, 2)})
    elif nak_score_raw > 0.6:
        # Strong bull market nakshatra = gold also benefits from prosperity
        moon_gold_score = nak_score_raw * 0.4
        reasons.append(f"Moon in {moon_nak} (prosperity → gold demand, +{moon_gold_score:.2f})")
        active_rules.append({"rule": f"Prosperity Demand: {moon_nak}", "shloka": "246",
                             "effect": "mildly bullish",
                             "score": round(moon_gold_score, 2)})
    else:
        moon_gold_score = nak_score_raw * 0.2  # mild effect
    score += moon_gold_score
    breakdown["moon_nakshatra"] = {
        "score": round(moon_gold_score, 2),
        "nakshatra": moon_nak,
        "market_score": nak_score_raw,
        "is_gold_nak": nak_gold_rule.get("gold", False),
    }

    # ── Rule 4: Retrograde effects ──
    retro_score = 0.0
    retro_planets = []
    for pname in ["Jupiter", "Venus", "Saturn", "Mercury", "Mars"]:
        p = positions.get(pname, {})
        if p.get("retrograde", False):
            r_info = RETRO_GOLD_EFFECT.get(pname, {})
            r_effect = r_info.get("retro_effect", 0.2)
            retro_score += r_effect
            retro_planets.append(pname)
            reasons.append(f"{pname} Retrograde (+{r_effect:.2f} gold)")
            active_rules.append({"rule": f"{pname} Retrograde", "shloka": r_info.get("shloka", "337, 359"),
                                 "effect": "bullish",
                                 "detail": r_info.get("reason", ""),
                                 "score": round(r_effect, 2)})
    score += retro_score
    breakdown["retrograde"] = {
        "score": round(retro_score, 2),
        "planets": retro_planets,
    }

    # ── Rule 5: Malefic planet strength (papa = gold expensive) ──
    malefic_strength = 0.0
    for pname in ["Mars", "Saturn", "Rahu", "Ketu"]:
        p = positions.get(pname, {})
        bala = p.get("kshetra_bala", 0.5)
        if bala >= 0.75:
            malefic_strength += 0.3
    if malefic_strength > 0:
        reasons.append(f"Strong malefics = scarcity pressure (+{malefic_strength:.2f})")
        active_rules.append({"rule": "Strong Malefics (Papa Graha)", "shloka": "245",
                             "effect": "bullish",
                             "detail": "पापग्रह बल = वस्तु महंगी",
                             "score": round(malefic_strength, 2)})
    score += malefic_strength
    breakdown["malefic_strength"] = {"score": round(malefic_strength, 2)}

    # ── Rule 6: Benefic planet strength (shubha = gold cheap/stable) ──
    benefic_strength = 0.0
    for pname in ["Jupiter", "Venus"]:
        p = positions.get(pname, {})
        bala = p.get("kshetra_bala", 0.5)
        if bala >= 0.75 and not p.get("retrograde", False):
            benefic_strength -= 0.2  # Strong benefic direct = markets good = less gold fear
    if benefic_strength < 0:
        reasons.append(f"Strong benefics direct = market confidence ({benefic_strength:.2f})")
        active_rules.append({"rule": "Strong Benefics (Shubha Graha)", "shloka": "246",
                             "effect": "mildly bearish",
                             "detail": "शुभग्रह बल = वस्तु सस्ती",
                             "score": round(benefic_strength, 2)})
    score += benefic_strength
    breakdown["benefic_strength"] = {"score": round(benefic_strength, 2)}

    # ── Rule 7: Moon waning (Ksheena Chandra) = fear ──
    moon_speed = moon.get("speed", 13)
    # Moon illumination proxy: when Moon is near Sun = new moon = ksheena
    sun_lon = sun.get("longitude", 0)
    moon_lon = moon.get("longitude", 0)
    sun_moon_diff = abs(moon_lon - sun_lon)
    if sun_moon_diff > 180:
        sun_moon_diff = 360 - sun_moon_diff
    if sun_moon_diff < 36:  # Near new moon — ksheena
        ksheena_score = 0.4
        score += ksheena_score
        reasons.append(f"Ksheena Chandra (waning near new moon) → fear → gold demand (+{ksheena_score})")
        active_rules.append({"rule": "Ksheena Chandra", "shloka": "Moon malefic when waning",
                             "effect": "bullish", "score": ksheena_score})
        breakdown["ksheena_moon"] = {"score": ksheena_score, "sun_moon_gap": round(sun_moon_diff, 1)}

    # ── Rule 8: Day lord effect ──
    weekday = date.weekday()  # 0=Mon
    day_lords = ["Moon", "Mars", "Mercury", "Jupiter", "Venus", "Saturn", "Sun"]
    day_lord = day_lords[weekday]
    day_effect = PLANET_GOLD_EFFECT.get(day_lord, {})
    day_score = 0.0
    if day_lord in ["Sun", "Mars", "Saturn"]:
        day_score = 0.15  # Malefic day lords = slight gold positive
    elif day_lord in ["Venus"]:
        day_score = 0.1   # Venus = jewelry/gold buying day
    elif day_lord in ["Mercury"]:
        day_score = -0.1  # Mercury = trade day
    score += day_score
    breakdown["day_lord"] = {"lord": day_lord, "score": round(day_score, 2)}

    # ── Rule 9: All-planet nakshatra gold scoring (Shlokas 379-406) ──
    nak_result = _score_all_planet_nakshatras(positions)
    nak_all_score = nak_result["score"]
    score += nak_all_score
    breakdown["all_planet_nakshatras"] = nak_result
    if nak_result["hits"]:
        for nh in nak_result["hits"]:
            reasons.append(f"{nh['planet']} in {nh['nakshatra']} ({nh['type']}, +{nh['score']})")
            active_rules.append({
                "rule": f"{nh['planet']} in {nh['type'].replace('_', ' ').title()}: {nh['nakshatra']}",
                "shloka": nh.get("shloka", "379-406"),
                "effect": "bullish",
                "detail": nh.get("detail", ""),
                "score": nh["score"],
            })

    # ── Rule 10: SBC Vedha on gold nakshatras & gold rulers (Shlokas 245-246) ──
    transit_list = _build_transit_list(positions)
    vedha_result = _score_sbc_vedha(positions, transit_list)
    vedha_score = vedha_result["score"]
    score += vedha_score
    breakdown["sbc_vedha"] = vedha_result
    if vedha_result["vedha_hits"]:
        for vh in vedha_result["vedha_hits"]:
            reasons.append(f"{vh['vedha_nature'].upper()} vedha: {vh['vedha_planet']} → {vh['target']} ({vh['direction']}, {'+' if vh['score'] > 0 else ''}{vh['score']})")
            active_rules.append({
                "rule": f"SBC Vedha: {vh['vedha_planet']} ({vh['vedha_nature']}) → {vh['target']}",
                "shloka": vh.get("shloka", "245-246"),
                "effect": vh["direction"],
                "detail": vh.get("detail", ""),
                "score": vh["score"],
            })
    if vedha_result["ubhayato"]:
        for ub in vedha_result["ubhayato"]:
            reasons.append(f"UBHAYATO VEDHA on {ub['target']} by {', '.join(ub['planets'])} (+{ub['score']})")
            active_rules.append({
                "rule": f"Ubhayato Vedha: {ub['target']}",
                "shloka": "220",
                "effect": "EXTREME bullish",
                "detail": ub["detail"],
                "score": ub["score"],
            })

    # ── Clamp score ──
    score = max(-10, min(10, score))

    # ── Determine signal ──
    if score >= 2.0:
        signal = "STRONG BULLISH"
        signal_color = "#00e874"
    elif score >= 1.0:
        signal = "BULLISH"
        signal_color = "#66bb6a"
    elif score >= 0.3:
        signal = "MILDLY BULLISH"
        signal_color = "#a5d6a7"
    elif score <= -1.5:
        signal = "BEARISH"
        signal_color = "#ff5252"
    elif score <= -0.5:
        signal = "MILDLY BEARISH"
        signal_color = "#ef9a9a"
    else:
        signal = "NEUTRAL"
        signal_color = "#bdbdbd"

    # ── Build per-planet nakshatra snapshot ──
    planet_nakshatras = {}
    for pn in ALL_PLANETS:
        pd = positions.get(pn, {})
        pnak = pd.get("nakshatra", "")
        planet_nakshatras[pn] = {
            "nakshatra": pnak,
            "sign": pd.get("sign", ""),
            "is_gold_nak": pnak in GOLD_NAKSHATRAS,
            "is_metal_nak": pnak in METAL_NAKSHATRAS,
        }

    return {
        "date": date.strftime("%Y-%m-%d"),
        "weekday": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"][weekday],
        "score": round(score, 2),
        "signal": signal,
        "signal_color": signal_color,
        "day_lord": day_lord,
        "moon_nakshatra": moon_nak,
        "moon_sign": moon.get("sign", ""),
        "sun_sign": sun.get("sign", ""),
        "jupiter_sign": jup.get("sign", ""),
        "reasons": reasons,
        "active_rules": active_rules,
        "breakdown": breakdown,
        "retro_planets": [p for p in ALL_PLANETS if positions.get(p, {}).get("retrograde", False)],
        "planet_nakshatras": planet_nakshatras,
        "vedha_summary": {
            "papa_count": vedha_result.get("papa_count", 0),
            "shubha_count": vedha_result.get("shubha_count", 0),
            "vedha_score": vedha_score,
            "ubhayato": len(vedha_result.get("ubhayato", [])),
        },
    }


# ─────────────────────────────────────────────────────────────
# Transit Event Detection for Gold
# ─────────────────────────────────────────────────────────────

def _detect_gold_events(
    jd_start: float, jd_end: float,
    ayanamsa_key: str, tz_offset: int,
) -> List[Dict]:
    """Detect planet transit events that specifically affect gold."""
    events = []
    step = 1.0  # 1 day step for event scanning

    jd = jd_start
    prev_positions = _compute_planet_positions(jd, ayanamsa_key)

    while jd < jd_end:
        jd_next = min(jd + step, jd_end)
        cur_positions = _compute_planet_positions(jd_next, ayanamsa_key)
        dt = _jd_to_dt(jd_next, tz_offset)

        for pname in ALL_PLANETS:
            prev = prev_positions.get(pname, {})
            cur = cur_positions.get(pname, {})

            # ── Sign Change ──
            if prev.get("sign_index") is not None and cur.get("sign_index") is not None:
                if prev["sign_index"] != cur["sign_index"]:
                    new_sign = cur["sign"]
                    gold_eff = SIGN_GOLD_EFFECT.get(new_sign, {}).get("gold_effect", 0)
                    pe = PLANET_GOLD_EFFECT.get(pname, {})
                    importance = "high" if pname in GOLD_PLANETS else "medium"

                    impact = ""
                    if pname == "Sun":
                        impact = f"Sun (gold ruler) enters {new_sign} — {'BULLISH' if gold_eff > 0.3 else 'BEARISH' if gold_eff < -0.1 else 'NEUTRAL'} for gold"
                    elif pname == "Jupiter":
                        impact = f"Jupiter sankranti into {new_sign} — NEW YEAR for commodity cycle (Shloka 349)"
                        importance = "critical"
                    elif pname == "Saturn":
                        impact = f"Saturn enters {new_sign} — long-term gold trend shift"
                        importance = "high"
                    elif pname == "Venus":
                        impact = f"Venus enters {new_sign} — luxury/jewelry demand shift"
                    else:
                        impact = f"{pname} enters {new_sign}"

                    events.append({
                        "date": dt.strftime("%Y-%m-%d"),
                        "planet": pname,
                        "event_type": "sign_change",
                        "from_sign": prev["sign"],
                        "to_sign": new_sign,
                        "gold_effect": round(gold_eff, 2),
                        "impact": impact,
                        "importance": importance,
                        "shloka": pe.get("shloka", "245-246"),
                        "color": PLANET_COLORS.get(pname, "#888"),
                    })

            # ── Nakshatra Change — ALL planets, gold & metal nakshatras ──
            if prev.get("nakshatra_index") is not None and cur.get("nakshatra_index") is not None:
                if prev["nakshatra_index"] != cur["nakshatra_index"]:
                    new_nak = cur["nakshatra"]
                    gold_rule = NAKSHATRA_GOLD_RULES.get(new_nak, {})
                    is_gold = gold_rule.get("gold", False)
                    is_metal = new_nak in METAL_NAKSHATRAS

                    if is_gold:
                        # ANY planet entering a gold nakshatra is significant
                        weight = PLANET_NAK_GOLD_WEIGHT.get(pname, 0.3)
                        importance = "critical" if pname in GOLD_PLANETS else "high"
                        events.append({
                            "date": dt.strftime("%Y-%m-%d"),
                            "planet": pname,
                            "event_type": "gold_nakshatra",
                            "nakshatra": new_nak,
                            "gold_effect": round(weight, 2),
                            "impact": f"{pname} enters GOLD nakshatra {new_nak} — {gold_rule.get('detail', 'Gold affected')}",
                            "importance": importance,
                            "shloka": gold_rule.get("shloka", "379-406"),
                            "commodities": gold_rule.get("commodities", []),
                            "duration": gold_rule.get("duration_months", gold_rule.get("duration_days", "?")),
                            "color": PLANET_COLORS.get(pname, "#888"),
                        })
                    elif is_metal and pname in ["Saturn", "Mars", "Rahu", "Sun", "Jupiter"]:
                        # Dhatu lords + gold rulers entering metal nakshatras
                        events.append({
                            "date": dt.strftime("%Y-%m-%d"),
                            "planet": pname,
                            "event_type": "metal_nakshatra",
                            "nakshatra": new_nak,
                            "gold_effect": 0.4,
                            "impact": f"{pname} enters metal/dhatu nakshatra {new_nak} — indirect gold support",
                            "importance": "medium",
                            "shloka": gold_rule.get("shloka", ""),
                            "commodities": gold_rule.get("commodities", []),
                            "color": PLANET_COLORS.get(pname, "#888"),
                        })

            # ── Retrograde Start/End ──
            if pname not in ["Sun", "Moon", "Rahu", "Ketu"]:
                prev_retro = prev.get("retrograde", False)
                cur_retro = cur.get("retrograde", False)
                if prev_retro != cur_retro:
                    retro_info = RETRO_GOLD_EFFECT.get(pname, {})
                    if cur_retro:
                        events.append({
                            "date": dt.strftime("%Y-%m-%d"),
                            "planet": pname,
                            "event_type": "retro_start",
                            "gold_effect": retro_info.get("retro_effect", 0.2),
                            "impact": f"{pname} goes RETROGRADE — {retro_info.get('reason', 'gold volatility')}",
                            "importance": "high" if pname in ["Jupiter", "Saturn"] else "medium",
                            "shloka": retro_info.get("shloka", "337, 359"),
                            "color": PLANET_COLORS.get(pname, "#888"),
                        })
                    else:
                        events.append({
                            "date": dt.strftime("%Y-%m-%d"),
                            "planet": pname,
                            "event_type": "retro_end",
                            "gold_effect": -retro_info.get("retro_effect", 0.2) * 0.5,
                            "impact": f"{pname} goes DIRECT — retro gold effect diminishes",
                            "importance": "medium",
                            "shloka": "359",
                            "color": PLANET_COLORS.get(pname, "#888"),
                        })

        # ── Vedha Events: detect when a planet starts/stops vedha-ing a gold nakshatra ──
        # Check if nakshatra changed for any planet (vedha geometry changes)
        for pname in ALL_PLANETS:
            prev_nak = prev_positions.get(pname, {}).get("nakshatra", "")
            cur_nak = cur_positions.get(pname, {}).get("nakshatra", "")
            if prev_nak != cur_nak and cur_nak:
                # Planet moved to new nakshatra — check if its vedha NOW hits a gold nakshatra
                cur_pos = NAK_TO_GRID.get(cur_nak)
                if cur_pos:
                    cur_speed = cur_positions.get(pname, {}).get("speed", 0.0)
                    vedha = get_vedha_cells(
                        row=cur_pos[0], col=cur_pos[1],
                        grid_size=9, planet=pname, speed=cur_speed,
                    )
                    vedha_all = set(vedha.get("all", []))

                    for gnak in GOLD_NAKSHATRAS:
                        gpos = NAK_TO_GRID.get(gnak)
                        if gpos and gpos in vedha_all:
                            nature = PLANET_NATURE.get(pname, "neutral")
                            if nature == "malefic":
                                events.append({
                                    "date": dt.strftime("%Y-%m-%d"),
                                    "planet": pname,
                                    "event_type": "vedha_gold_nak",
                                    "nakshatra": gnak,
                                    "from_nak": cur_nak,
                                    "gold_effect": 0.6,
                                    "impact": f"Papa {pname} in {cur_nak} now VEDHA-ing gold nakshatra {gnak} → gold expensive (Shloka 245)",
                                    "importance": "high",
                                    "shloka": "245",
                                    "vedha_mode": vedha.get("vedha_mode", ""),
                                    "color": PLANET_COLORS.get(pname, "#888"),
                                })
                            elif nature == "benefic":
                                events.append({
                                    "date": dt.strftime("%Y-%m-%d"),
                                    "planet": pname,
                                    "event_type": "vedha_gold_nak",
                                    "nakshatra": gnak,
                                    "from_nak": cur_nak,
                                    "gold_effect": -0.4,
                                    "impact": f"Shubha {pname} in {cur_nak} now VEDHA-ing gold nakshatra {gnak} → gold cheap (Shloka 246)",
                                    "importance": "medium",
                                    "shloka": "246",
                                    "vedha_mode": vedha.get("vedha_mode", ""),
                                    "color": PLANET_COLORS.get(pname, "#888"),
                                })

        prev_positions = cur_positions
        jd = jd_next

    return events


# ─────────────────────────────────────────────────────────────
# Main Entry Point
# ─────────────────────────────────────────────────────────────

def predict_gold(
    start_date: datetime,
    end_date: datetime,
    ayanamsa: str = "lahiri",
    tz_offset_minutes: int = 330,
) -> Dict:
    """
    Predict gold price direction over a date range.

    Returns:
    - daily_signals: list of daily gold score/signal/reasons
    - events: major transit events affecting gold
    - summary: overall period summary
    - rules_used: all rules applied with shloka references
    """
    ayanamsa_key = ayanamsa.lower()
    if ayanamsa_key not in AYANAMSA_MAP:
        raise ValueError(f"Unsupported ayanamsa: {ayanamsa}")

    jd_start = _dt_to_jd(start_date, tz_offset_minutes)
    jd_end = _dt_to_jd(end_date, tz_offset_minutes)

    # ── Daily signals ──
    daily_signals = []
    current = start_date
    while current < end_date:
        jd = _dt_to_jd(current, tz_offset_minutes)
        positions = _compute_planet_positions(jd, ayanamsa_key)
        day_result = _score_day(positions, current)
        daily_signals.append(day_result)
        current += timedelta(days=1)

    # ── Transit events ──
    events = _detect_gold_events(jd_start, jd_end, ayanamsa_key, tz_offset_minutes)
    events.sort(key=lambda e: e["date"])

    # ── Summary ──
    scores = [d["score"] for d in daily_signals]
    avg_score = sum(scores) / len(scores) if scores else 0
    bullish_days = sum(1 for s in scores if s >= 0.3)
    bearish_days = sum(1 for s in scores if s <= -0.5)
    neutral_days = len(scores) - bullish_days - bearish_days
    strong_days = [d for d in daily_signals if abs(d["score"]) >= 2.0]

    # Current planet positions at start
    start_positions = _compute_planet_positions(jd_start, ayanamsa_key)
    planet_snapshot = []
    for pname in ALL_PLANETS:
        p = start_positions.get(pname, {})
        planet_snapshot.append({
            "planet": pname,
            "sign": p.get("sign", ""),
            "nakshatra": p.get("nakshatra", ""),
            "retrograde": p.get("retrograde", False),
            "kshetra_bala": p.get("kshetra_bala", 0),
            "gold_role": PLANET_GOLD_EFFECT.get(pname, {}).get("gold_role", ""),
            "color": PLANET_COLORS.get(pname, "#888"),
        })

    if avg_score >= 1.0:
        overall = "STRONGLY BULLISH"
    elif avg_score >= 0.3:
        overall = "BULLISH"
    elif avg_score <= -1.0:
        overall = "BEARISH"
    elif avg_score <= -0.3:
        overall = "MILDLY BEARISH"
    else:
        overall = "NEUTRAL"

    # Add nakshatra and gold-nak flags to planet snapshot
    for ps in planet_snapshot:
        pnak = ps.get("nakshatra", "")
        ps["is_gold_nak"] = pnak in GOLD_NAKSHATRAS
        ps["is_metal_nak"] = pnak in METAL_NAKSHATRAS
        ps["nakshatra_shloka"] = NAKSHATRA_GOLD_RULES.get(pnak, {}).get("shloka", "")
        ps["nakshatra_commodities"] = NAKSHATRA_GOLD_RULES.get(pnak, {}).get("commodities", [])

    # Vedha summary for the period start
    start_transit_list = _build_transit_list(start_positions)
    start_vedha = _score_sbc_vedha(start_positions, start_transit_list)

    # Rules reference
    rules_used = [
        {"id": 1, "name": "Papa-Shubha Vedha", "shloka": "245-246",
         "description": "पापग्रह वेध से वस्तु महंगी, शुभग्रह वेध से सस्ती — Malefic vedha = gold expensive, Benefic vedha = gold cheap"},
        {"id": 2, "name": "Nakshatra Commodity Map", "shloka": "379-406",
         "description": "Each nakshatra rules specific commodities. Gold nakshatras: Punarvasu (383), Pushya (384), Chitra (390), Dhanishtha (400)"},
        {"id": 3, "name": "Jupiter Sankranti = Year", "shloka": "349",
         "description": "बृहस्पति की संक्रान्ति से वर्ष — Jupiter sign change marks new commodity year cycle"},
        {"id": 4, "name": "Dhatu Lords", "shloka": "354",
         "description": "धातु का स्वामी शनि, राहु, मंगल — Gold (dhatu) ruled by Saturn, Rahu, Mars"},
        {"id": 5, "name": "Graha Bala (Kshetra)", "shloka": "358-360",
         "description": "स्वक्षेत्रस्थे बलं पूर्ण — Own=4/4, friend=3/4, neutral=2/4, enemy=1/4. Motion: Retro=2×, Exalted=3×, Debilitated=0.5×"},
        {"id": 6, "name": "Vakra Bala", "shloka": "359, 337",
         "description": "शुभग्रह वक्रगति में दृष्टिफल अति शुभ — Retrograde benefic = very auspicious (gold rises)"},
        {"id": 7, "name": "Moon Nakshatra Daily", "shloka": "Various",
         "description": "Daily Moon transit through nakshatras gives immediate sentiment signal"},
        {"id": 8, "name": "Ksheena Chandra", "shloka": "55",
         "description": "Waning Moon (Sun-Moon < 36°) = malefic nature = fear = gold demand rises"},
        {"id": 9, "name": "All-Planet Nakshatra Gold Scoring", "shloka": "379-406",
         "description": "When ANY planet sits in a gold nakshatra (Punarvasu/Pushya/Chitra/Dhanishtha), gold signal generated. Weight by planet importance: Sun=1.5, Jupiter=1.2, Mars=0.8, etc."},
        {"id": 10, "name": "SBC Vedha on Gold Nakshatras", "shloka": "245-246",
         "description": "Using actual SBC vedha geometry: Papa planet vedha on gold nakshatra cell = gold RISES. Shubha vedha = gold FALLS. Also checks vedha on Sun/Jupiter's current nakshatra."},
        {"id": 11, "name": "Ubhayato Vedha", "shloka": "220",
         "description": "जब दो पापग्रह दोनों ओर से वेध करें = When 2+ malefic planets vedha same gold nakshatra → EXTREME gold rise signal"},
        {"id": 12, "name": "Dynamic Planet Nature", "shloka": "55-56",
         "description": "Ksheena Chandra (waning Moon → malefic) and Krura-yukta Budha (Mercury with malefic → malefic) change vedha nature dynamically"},
    ]

    return {
        "start_date": start_date.strftime("%Y-%m-%d"),
        "end_date": end_date.strftime("%Y-%m-%d"),
        "ayanamsa": ayanamsa,
        "total_days": len(daily_signals),
        "average_score": round(avg_score, 2),
        "overall_signal": overall,
        "bullish_days": bullish_days,
        "bearish_days": bearish_days,
        "neutral_days": neutral_days,
        "strong_signal_days": len(strong_days),
        "daily_signals": daily_signals,
        "events": events,
        "planet_positions": planet_snapshot,
        "rules_used": rules_used,
        "vedha_snapshot": {
            "at_start_date": start_vedha,
            "description": "SBC vedha state at period start — which planets vedha gold nakshatras",
        },
    }
