"""
utils.py — Pure utility functions (no astrology logic).
========================================================
Degree math, Julian Day conversion, date helpers.
Used by every other core module — zero dependencies on astrology code.
"""
from __future__ import annotations

from datetime import datetime, date, timedelta
from typing import List

import swisseph as swe


def normalize_degree(deg: float) -> float:
    """Normalize any angle to 0–360 range."""
    return deg % 360


def deg_to_dms(deg: float) -> str:
    """Convert decimal degrees → D°MM'SS\" string."""
    d = int(deg)
    m = int((deg - d) * 60)
    s = int(((deg - d) * 60 - m) * 60)
    return f"{d}°{m:02d}'{s:02d}\""


def dms_to_deg(d: int, m: int, s: int) -> float:
    """Convert D, M, S → decimal degrees."""
    return d + m / 60.0 + s / 3600.0


def angular_distance(lon1: float, lon2: float) -> float:
    """Shortest angular distance between two longitudes (0–180)."""
    diff = abs(normalize_degree(lon1) - normalize_degree(lon2))
    return min(diff, 360 - diff)


def angular_diff(from_lon: float, to_lon: float) -> float:
    """Signed angular difference from → to (0–360)."""
    return normalize_degree(to_lon - from_lon)


# ─── Julian Day ──────────────────────────────────────────────

def datetime_to_jd(dt: datetime) -> float:
    """Convert datetime (assumed UTC) to Julian Day."""
    return swe.julday(dt.year, dt.month, dt.day,
                      dt.hour + dt.minute / 60.0 + dt.second / 3600.0)


def jd_to_datetime(jd: float) -> datetime:
    """Convert Julian Day to datetime (UTC)."""
    y, m, d, h = swe.revjul(jd)
    hour = int(h)
    minute = int((h - hour) * 60)
    second = int(((h - hour) * 60 - minute) * 60)
    return datetime(y, m, d, hour, minute, second)


def local_to_utc(dt: datetime, tz_offset_hours: float) -> datetime:
    """Convert local datetime to UTC."""
    return dt - timedelta(hours=tz_offset_hours)


def utc_to_local(dt: datetime, tz_offset_hours: float) -> datetime:
    """Convert UTC datetime to local."""
    return dt + timedelta(hours=tz_offset_hours)


# ─── Date helpers ────────────────────────────────────────────

def parse_date(s: str) -> date:
    """Parse date string — accepts DD-MM-YYYY or YYYY-MM-DD."""
    s = s.strip()
    # DD-MM-YYYY (Indian format)
    if len(s) >= 10 and s[2] == "-" and s[5] == "-":
        return datetime.strptime(s, "%d-%m-%Y").date()
    # YYYY-MM-DD (ISO format)
    return datetime.strptime(s, "%Y-%m-%d").date()


def date_range(start: date, end: date) -> List[date]:
    """Generate inclusive list of dates from start to end."""
    days = (end - start).days
    return [start + timedelta(days=i) for i in range(days + 1)]


def date_to_datetime(d: date, hour: int = 6, minute: int = 0) -> datetime:
    """Convert date to datetime at specified time (default 6:00 AM)."""
    return datetime(d.year, d.month, d.day, hour, minute, 0)
