"""
signs.py — Rashi (zodiac sign) calculations.
=============================================
Pure math — takes a longitude, returns sign info.
"""
from __future__ import annotations

from core.constants import SIGNS, SIGN_LORDS, SIGN_ELEMENTS, SIGN_MODALITY
from core.types import SignInfo


def calc_sign(longitude: float) -> SignInfo:
    """Calculate which sign a longitude falls in."""
    index = int(longitude / 30) % 12
    name = SIGNS[index]
    return SignInfo(
        index=index,
        name=name,
        lord=SIGN_LORDS[name],
        degree_in_sign=longitude - (index * 30),
        element=SIGN_ELEMENTS.get(name, ""),
        modality=SIGN_MODALITY.get(name, ""),
    )


def get_sign_info(sign_name: str) -> dict:
    """Get full info for a sign by name."""
    if sign_name not in SIGN_LORDS:
        return {"error": f"Unknown sign: {sign_name}"}
    return {
        "sign": sign_name,
        "lord": SIGN_LORDS[sign_name],
        "element": SIGN_ELEMENTS.get(sign_name, ""),
        "modality": SIGN_MODALITY.get(sign_name, ""),
        "index": SIGNS.index(sign_name),
    }


def sign_distance(from_sign: str, to_sign: str) -> int:
    """Number of signs from one to another (1-12)."""
    f = SIGNS.index(from_sign)
    t = SIGNS.index(to_sign)
    return ((t - f) % 12) + 1
