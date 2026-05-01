"""
shodasvarga module — All 16 Shodasvarga divisional charts + Vimshottari Dasha.
Combined endpoint for the Shodasvarga tab.
"""
from __future__ import annotations

from datetime import datetime
from typing import List, Optional

from fastapi import APIRouter, HTTPException
from pydantic import Field

from app.models import BirthDataInput, resolve_chart
from app.divisional import (
    calculate_shodasvarga,
    detect_vargottama,
    dignity_summary,
    SHODASVARGA_LIST,
    SHODASVARGA_NAMES,
)
from app.dasha import calculate_vimshottari_dasha, get_current_dasha

router = APIRouter(tags=["v3.0 — Shodasvarga"])


# ── schemas ───────────────────────────────────────────────────

class ShodasvargaInput(BirthDataInput):
    charts: List[str] = Field(
        default=SHODASVARGA_LIST,
        description="Which divisional charts to compute (default: all 16)",
    )
    as_of_date: Optional[str] = Field(
        default=None,
        description="Date for current dasha lookup (defaults to today)",
    )


# ── endpoints ─────────────────────────────────────────────────

@router.post("/shodasvarga", summary="All 16 Shodasvarga + Vimshottari Dasha")
def shodasvarga(payload: ShodasvargaInput):
    """
    Compute all 16 Shodasvarga divisional charts (D1–D60) with
    planet positions, dignity, Vargottama status, and full
    Vimshottari Dasha tree.
    """
    try:
        data = resolve_chart(payload, need_ascendant=True)

        # ── Divisional charts ────────────────────────────────
        all_charts = calculate_shodasvarga(
            data.planets, data.ascendant, payload.charts
        )

        # ── Vargottama detection ─────────────────────────────
        vargottama = detect_vargottama(data.planets, all_charts)

        # ── Dignity summary across vargas ────────────────────
        dignity = dignity_summary(all_charts)

        # ── Vimshottari Dasha ────────────────────────────────
        moon = next((p for p in data.planets if p["planet"] == "Moon"), None)
        dasha_data = None
        current_dasha = None
        if moon:
            dasha_data = calculate_vimshottari_dasha(
                moon["longitude"], data.local_dt, 120
            )
            as_of = (
                datetime.strptime(payload.as_of_date, "%Y-%m-%d")
                if payload.as_of_date else datetime.utcnow()
            )
            current_dasha = get_current_dasha(dasha_data, as_of)

        # ── Chart meta for UI dropdown ───────────────────────
        chart_list = []
        for c in SHODASVARGA_LIST:
            if c.lower() in all_charts:
                chart_list.append({
                    "id":   c,
                    "name": SHODASVARGA_NAMES.get(c, c),
                    "full": all_charts[c.lower()].get("chart", c),
                    "desc": all_charts[c.lower()].get("description", ""),
                })

        return {
            "type":           "shodasvarga",
            "name":           payload.name,
            "birth_date":     payload.date,
            "birth_time":     payload.time,
            "birth_place":    data.resolved.place,
            "ayanamsa":       payload.ayanamsa,
            "ascendant_d1":   data.ascendant,
            "chart_list":     chart_list,
            "charts":         all_charts,
            "vargottama":     vargottama,
            "dignity_summary": dignity,
            "dasha_data":     dasha_data,
            "current_dasha":  current_dasha,
        }
    except Exception as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
