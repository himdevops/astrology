"""
dasha.py — Vimshottari Dasha Engine
Calculates full Mahadasha / Antardasha / Pratyantar Dasha with
financial astrology significance for NSE/BSE markets.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

from app.nakshatra import (
    DASHA_YEARS,
    NAKSHATRA_LORD_ORDER,
    NAKSHATRA_SPAN_DEG,
    NAKSHATRAS,
    TOTAL_DASHA_YEARS,
    get_nakshatra,
)

# ─────────────────────────────────────────────────────────────
# Financial significance of each Dasha lord for NSE/BSE
# ─────────────────────────────────────────────────────────────
DASHA_FINANCIAL: Dict[str, Dict] = {
    "Sun": {
        "nature": "Authority & Power",
        "market_effect": (
            "Government policy-driven market. PSU stocks, infrastructure, energy rally. "
            "Speculation in gold. Ego-driven bubbles possible."
        ),
        "sectors": ["PSU Banks", "Infra", "Gold", "Power", "Govt Bonds"],
        "score": 0.40,
        "color": "#FFA500",
    },
    "Moon": {
        "nature": "Emotions & Liquidity",
        "market_effect": (
            "FII/retail liquidity-driven market. FMCG, real estate, consumer goods rally. "
            "Silver commodity positive. Emotional crowd buying."
        ),
        "sectors": ["FMCG", "Real Estate", "Hospitality", "Silver", "Consumer Durables"],
        "score": 0.55,
        "color": "#C0C0C0",
    },
    "Mars": {
        "nature": "Energy & Action",
        "market_effect": (
            "Aggressive market moves. Defense, real estate, steel, energy outperform. "
            "Good for short-term momentum trades. Conflict = volatility."
        ),
        "sectors": ["Defense", "Real Estate", "Steel", "Energy", "Mining"],
        "score": 0.35,
        "color": "#FF4444",
    },
    "Rahu": {
        "nature": "Illusion & Technology",
        "market_effect": (
            "Tech bubbles, foreign investment surge, unexpected rallies followed by crashes. "
            "IT, foreign stocks, unconventional sectors. High reward/risk."
        ),
        "sectors": ["IT/Tech", "Foreign Funds", "Chemicals", "Aviation", "Crypto"],
        "score": -0.15,
        "color": "#8B008B",
    },
    "Jupiter": {
        "nature": "Expansion & Abundance",
        "market_effect": (
            "Best dasha for wealth creation. Banking, finance, education, pharma flourish. "
            "Long-term bull market. Avoid overexpansion — bubbles form at peak."
        ),
        "sectors": ["Banking", "Finance", "Education", "Pharma", "Gold", "Religious stocks"],
        "score": 0.90,
        "color": "#FFD700",
    },
    "Saturn": {
        "nature": "Discipline & Structure",
        "market_effect": (
            "Slow grind markets. Blue-chip value stocks outperform; speculative assets crash. "
            "Oil, gas, mining, utilities thrive. Long holding periods required."
        ),
        "sectors": ["Oil & Gas", "Mining", "Utilities", "Infrastructure", "Leather"],
        "score": 0.25,
        "color": "#4169E1",
    },
    "Mercury": {
        "nature": "Commerce & Intelligence",
        "market_effect": (
            "Trading and commerce-driven markets. IT, telecom, media, banking rally. "
            "Volatile quick moves. Good for active traders."
        ),
        "sectors": ["IT", "Telecom", "Media", "Banking", "Logistics", "Publishing"],
        "score": 0.65,
        "color": "#00CED1",
    },
    "Ketu": {
        "nature": "Detachment & Spirituality",
        "market_effect": (
            "Sudden unexpected events; detachment from material. Pharma, chemicals, "
            "mystical sectors. Market dislocations and sudden crashes/gains."
        ),
        "sectors": ["Pharma", "Chemicals", "Spiritual/Yoga", "Exit positions"],
        "score": -0.30,
        "color": "#808080",
    },
    "Venus": {
        "nature": "Luxury & Pleasure",
        "market_effect": (
            "Best period for luxury, FMCG, entertainment, auto. Consumer spending surge. "
            "Real estate, gems, textiles boom. Overall wealth-generating period."
        ),
        "sectors": ["Luxury Goods", "Entertainment", "Auto", "Gems", "Textiles", "Hotels"],
        "score": 0.85,
        "color": "#FF69B4",
    },
}


def _days(years: float) -> float:
    """Convert years to days using tropical year."""
    return years * 365.25


def calculate_vimshottari_dasha(
    moon_longitude: float,
    birth_date: datetime,
    years_to_show: int = 120,
) -> Dict:
    """
    Full Vimshottari Dasha calculation from Moon's nakshatra position.

    Args:
        moon_longitude: Sidereal longitude of Moon (0–360°)
        birth_date: Date and time of birth
        years_to_show: How many years of dasha to show (default: full 120 years)

    Returns:
        Complete dasha tree with Mahadasha > Antardasha > Pratyantar Dasha
    """
    nakshatra_info = get_nakshatra(moon_longitude)
    birth_lord = nakshatra_info["lord"]

    # Fraction elapsed within the birth nakshatra → elapsed portion of birth dasha
    fraction_elapsed = nakshatra_info["degree_in_nakshatra"] / NAKSHATRA_SPAN_DEG
    birth_lord_total = DASHA_YEARS[birth_lord]

    elapsed_years_in_maha = fraction_elapsed * birth_lord_total
    balance_years = birth_lord_total - elapsed_years_in_maha

    birth_lord_idx = NAKSHATRA_LORD_ORDER.index(birth_lord)
    dashas: List[Dict] = []
    current_date = birth_date
    cutoff = birth_date + timedelta(days=_days(years_to_show))

    for i in range(9):
        lord_idx = (birth_lord_idx + i) % 9
        lord = NAKSHATRA_LORD_ORDER[lord_idx]

        if i == 0:
            # Partial first dasha
            maha_years = balance_years
            elapsed_in = elapsed_years_in_maha
        else:
            maha_years = DASHA_YEARS[lord]
            elapsed_in = 0.0

        end_date = current_date + timedelta(days=_days(maha_years))
        fin = DASHA_FINANCIAL.get(lord, {})

        antardashas = _calc_antardashas(
            lord, DASHA_YEARS[lord], elapsed_in, current_date
        )

        dashas.append({
            "mahadasha_lord":  lord,
            "start_date":      current_date.strftime("%Y-%m-%d"),
            "end_date":        end_date.strftime("%Y-%m-%d"),
            "duration_years":  round(maha_years, 4),
            "financial":       {
                "nature":        fin.get("nature", ""),
                "market_effect": fin.get("market_effect", ""),
                "sectors":       fin.get("sectors", []),
                "score":         fin.get("score", 0.0),
                "color":         fin.get("color", "#888888"),
            },
            "antardashas": antardashas,
        })
        current_date = end_date
        if current_date > cutoff:
            break

    return {
        "birth_nakshatra":       nakshatra_info["nakshatra"],
        "birth_nakshatra_lord":  birth_lord,
        "moon_longitude":        round(moon_longitude, 4),
        "balance_at_birth":      {
            "lord":  birth_lord,
            "years": round(balance_years, 4),
            "days":  round(_days(balance_years), 1),
        },
        "dashas": dashas,
    }


def _calc_antardashas(
    maha_lord: str,
    maha_total_years: int,
    elapsed_in_maha: float,
    maha_start: datetime,
) -> List[Dict]:
    """
    Calculate all 9 antardashas within a mahadasha.
    Handles partial first mahadasha correctly.
    """
    lord_idx = NAKSHATRA_LORD_ORDER.index(maha_lord)
    results: List[Dict] = []
    cumulative_years = 0.0

    for i in range(9):
        sub_idx = (lord_idx + i) % 9
        sub_lord = NAKSHATRA_LORD_ORDER[sub_idx]
        sub_years = (maha_total_years * DASHA_YEARS[sub_lord]) / TOTAL_DASHA_YEARS

        antar_abs_start = cumulative_years
        antar_abs_end = cumulative_years + sub_years

        if antar_abs_end <= elapsed_in_maha:
            # Fully elapsed before birth
            cumulative_years += sub_years
            continue

        if antar_abs_start < elapsed_in_maha:
            # Partially elapsed at birth
            remaining = antar_abs_end - elapsed_in_maha
            start_d = maha_start
            end_d = maha_start + timedelta(days=_days(remaining))
        else:
            offset = antar_abs_start - elapsed_in_maha
            start_d = maha_start + timedelta(days=_days(offset))
            end_d = start_d + timedelta(days=_days(sub_years))

        pratyantar = _calc_pratyantar(maha_lord, sub_lord, sub_years, start_d)

        results.append({
            "antardasha_lord":  sub_lord,
            "start_date":       start_d.strftime("%Y-%m-%d"),
            "end_date":         end_d.strftime("%Y-%m-%d"),
            "duration_days":    round(_days(sub_years), 1),
            "combined_score":   _combined_score(maha_lord, sub_lord),
            "market_effect":    DASHA_FINANCIAL.get(sub_lord, {}).get("market_effect", ""),
            "sectors":          DASHA_FINANCIAL.get(sub_lord, {}).get("sectors", []),
            "pratyantardashas": pratyantar,
        })
        cumulative_years += sub_years

    return results


def _calc_pratyantar(
    maha_lord: str,
    antar_lord: str,
    antar_total_years: float,
    antar_start: datetime,
) -> List[Dict]:
    """Calculate Pratyantar Dasha (sub-sub periods)."""
    antar_idx = NAKSHATRA_LORD_ORDER.index(antar_lord)
    results: List[Dict] = []
    current = antar_start

    for i in range(9):
        sub_idx = (antar_idx + i) % 9
        sub_lord = NAKSHATRA_LORD_ORDER[sub_idx]
        # Pratyantar = (antar_total_years × sub_lord_years) / 120
        prat_years = (antar_total_years * DASHA_YEARS[sub_lord]) / TOTAL_DASHA_YEARS
        end_d = current + timedelta(days=_days(prat_years))
        results.append({
            "pratyantar_lord": sub_lord,
            "start_date":      current.strftime("%Y-%m-%d"),
            "end_date":        end_d.strftime("%Y-%m-%d"),
            "duration_days":   round(_days(prat_years), 1),
            "score":           _combined_score(maha_lord, sub_lord),
        })
        current = end_d

    return results


def _combined_score(maha_lord: str, sub_lord: str) -> float:
    """Weighted combined financial score for maha + antardasha."""
    m = DASHA_FINANCIAL.get(maha_lord, {}).get("score", 0.0)
    s = DASHA_FINANCIAL.get(sub_lord,  {}).get("score", 0.0)
    return round(m * 0.60 + s * 0.40, 3)


def get_current_dasha(dasha_data: Dict, as_of: Optional[datetime] = None) -> Dict:
    """
    Find the active Mahadasha + Antardasha + Pratyantar Dasha for a given date.
    Defaults to today if as_of is None.
    """
    if as_of is None:
        as_of = datetime.utcnow()
    date_str = as_of.strftime("%Y-%m-%d")

    for maha in dasha_data.get("dashas", []):
        if not (maha["start_date"] <= date_str <= maha["end_date"]):
            continue

        active_antar = active_prat = None
        for antar in maha.get("antardashas", []):
            if antar["start_date"] <= date_str <= antar["end_date"]:
                active_antar = antar
                for prat in antar.get("pratyantardashas", []):
                    if prat["start_date"] <= date_str <= prat["end_date"]:
                        active_prat = prat
                        break
                break

        fin = DASHA_FINANCIAL.get(maha["mahadasha_lord"], {})
        return {
            "as_of_date":          date_str,
            "mahadasha":           maha["mahadasha_lord"],
            "mahadasha_start":     maha["start_date"],
            "mahadasha_end":       maha["end_date"],
            "mahadasha_score":     fin.get("score", 0.0),
            "mahadasha_sectors":   fin.get("sectors", []),
            "antardasha":          active_antar["antardasha_lord"] if active_antar else None,
            "antardasha_start":    active_antar["start_date"] if active_antar else None,
            "antardasha_end":      active_antar["end_date"] if active_antar else None,
            "pratyantar":          active_prat["pratyantar_lord"] if active_prat else None,
            "pratyantar_start":    active_prat["start_date"] if active_prat else None,
            "pratyantar_end":      active_prat["end_date"] if active_prat else None,
            "combined_score":      active_antar["combined_score"] if active_antar else fin.get("score", 0.0),
            "market_outlook":      fin.get("market_effect", ""),
            "favorable_sectors":   fin.get("sectors", []),
        }
    return {"error": "Date not found in dasha range"}
