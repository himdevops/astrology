"""
settings.py — Centralized configuration.
==========================================
Override via environment variables for production deployment.
"""
from __future__ import annotations

import os


class Settings:
    # Server
    HOST: str = os.getenv("ASTRO_HOST", "0.0.0.0")
    PORT: int = int(os.getenv("ASTRO_PORT", "8000"))
    DEBUG: bool = os.getenv("ASTRO_DEBUG", "true").lower() == "true"

    # Defaults
    DEFAULT_AYANAMSA: str = os.getenv("ASTRO_AYANAMSA", "lahiri")
    DEFAULT_TZ_OFFSET: float = float(os.getenv("ASTRO_TZ_OFFSET", "5.5"))
    DEFAULT_LOCATION: str = os.getenv("ASTRO_LOCATION", "ujjain")

    # Default birth data (centralised — used by all modules)
    DEFAULT_DOB: str = os.getenv("ASTRO_DOB", "23-09-1992")
    DEFAULT_TOB: str = os.getenv("ASTRO_TOB", "23:10")
    DEFAULT_PLACE: str = os.getenv("ASTRO_PLACE", "Ujjain")
    DEFAULT_LAT: float = float(os.getenv("ASTRO_LAT", "23.1765"))
    DEFAULT_LON: float = float(os.getenv("ASTRO_LON", "75.7885"))

    # CORS
    CORS_ORIGINS: list = os.getenv("ASTRO_CORS_ORIGINS", "*").split(",")

    # Swiss Ephemeris data path (if custom ephemeris files)
    EPHE_PATH: str = os.getenv("ASTRO_EPHE_PATH", "")

    # API versioning
    API_VERSION: str = "v1"
    API_PREFIX: str = f"/api/{API_VERSION}"


settings = Settings()
