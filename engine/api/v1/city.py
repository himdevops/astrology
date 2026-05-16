"""City search API routes."""
from __future__ import annotations

from fastapi import APIRouter, Query

from core.cities import search_city, resolve_city

router = APIRouter(prefix="/api/v1/city", tags=["City"])


@router.get("/search", summary="Search cities by name")
def city_search(q: str = Query(..., min_length=2, description="City name (partial match)")):
    """
    Returns matching cities with lat, lon, timezone offset.
    Used for autocomplete in the frontend.
    """
    results = search_city(q, limit=10)
    return {"results": results, "count": len(results)}


@router.get("/resolve", summary="Resolve city to coordinates")
def city_resolve(q: str = Query(..., min_length=2, description="City name")):
    """
    Resolve a city name to full LocationInfo (lat, lon, tz_offset).
    Returns best match or 404-style empty result.
    """
    loc = resolve_city(q)
    if loc:
        return {
            "found": True,
            "name": loc.name,
            "latitude": loc.latitude,
            "longitude": loc.longitude,
            "tz_offset": loc.tz_offset,
        }
    return {"found": False, "name": q, "message": "City not found in database"}
