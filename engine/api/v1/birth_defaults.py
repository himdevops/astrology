"""Birth defaults API — serves centralised default birth data."""
from __future__ import annotations

from fastapi import APIRouter
from config.settings import settings

router = APIRouter(prefix="/api/v1/birth-defaults", tags=["Config"])


@router.get("", summary="Get default birth data")
def get_birth_defaults():
    """
    Returns the centralised default birth data.
    All UI modules should call this on page load to get consistent defaults.
    """
    return {
        "date": settings.DEFAULT_DOB,
        "time": settings.DEFAULT_TOB,
        "place": settings.DEFAULT_PLACE,
        "latitude": settings.DEFAULT_LAT,
        "longitude": settings.DEFAULT_LON,
        "tz_offset": settings.DEFAULT_TZ_OFFSET,
        "ayanamsa": settings.DEFAULT_AYANAMSA,
    }
