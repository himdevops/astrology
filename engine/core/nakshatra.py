"""
nakshatra.py — Nakshatra calculations.
=======================================
Pure math — takes a longitude, returns nakshatra, pada, lord.
"""
from __future__ import annotations

from core.constants import (
    NAKSHATRAS_27, NAKSHATRA_LORDS, NAKSHATRA_SPAN, PADA_SPAN,
    NAKSHATRA_DEITY, NAKSHATRA_TO_RASHI,
)
from core.types import NakshatraInfo


def calc_nakshatra(longitude: float) -> NakshatraInfo:
    """Calculate nakshatra from a sidereal longitude."""
    index = int(longitude / NAKSHATRA_SPAN) % 27
    name = NAKSHATRAS_27[index]
    lord = NAKSHATRA_LORDS[index]
    start = index * NAKSHATRA_SPAN
    degree_in_nak = longitude - start
    pada = min(int(degree_in_nak / PADA_SPAN) + 1, 4)

    return NakshatraInfo(
        index=index,
        name=name,
        lord=lord,
        pada=pada,
        degree_in_nakshatra=degree_in_nak,
        start_degree=start,
        end_degree=start + NAKSHATRA_SPAN,
        deity=NAKSHATRA_DEITY.get(name, ""),
    )


def get_nakshatra_info(name: str) -> dict:
    """Get full info for a nakshatra by name."""
    if name not in NAKSHATRA_TO_RASHI:
        return {"error": f"Unknown nakshatra: {name}"}
    idx = NAKSHATRAS_27.index(name)
    return {
        "nakshatra": name,
        "index": idx,
        "lord": NAKSHATRA_LORDS[idx],
        "rashi": NAKSHATRA_TO_RASHI[name],
        "deity": NAKSHATRA_DEITY.get(name, ""),
        "span_start": round(idx * NAKSHATRA_SPAN, 4),
        "span_end": round((idx + 1) * NAKSHATRA_SPAN, 4),
    }


def nakshatra_distance(from_nak: str, to_nak: str) -> int:
    """Count of nakshatras from one to another (1-27)."""
    f = NAKSHATRAS_27.index(from_nak)
    t = NAKSHATRAS_27.index(to_nak)
    return ((t - f) % 27) + 1
