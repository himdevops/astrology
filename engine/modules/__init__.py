"""
modules — Independent astrological event calculation modules.
==============================================================
Each module depends ONLY on core/ — never on other modules.
This makes every module independently importable and testable.

Available modules:
  positions      — Daily planetary positions
  retrograde     — Retrograde detection & period finding
  transit        — Sign / nakshatra change detection
  combustion     — Proximity to Sun (combust status)
  aspects        — Vedic mutual aspects (Drishti)
  lunar_aspects  — Moon's aspects to all planets
  parallels      — Declination-based parallel/contra-parallel
  ecliptic       — Ecliptic plane crossings
  graha_yuddha   — Planetary war (within 1°)
"""
