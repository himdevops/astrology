"""
transit_alerts.py — NSE/BSE Transit Alert Engine
Real-time alerts for key planetary transits, retrogrades, eclipses,
and critical degree transits that affect Indian stock markets.
"""
from __future__ import annotations

from datetime import datetime, timedelta
from typing import Dict, List, Optional

import swisseph as swe

SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces",
]
SIGN_IDX = {s: i for i, s in enumerate(SIGNS)}

# ─────────────────────────────────────────────────────────────
# Market-Critical Planetary Events
# ─────────────────────────────────────────────────────────────

# Key degrees for market turning points (0° = sign start = gandanta/sandhi)
CRITICAL_DEGREES = {
    "exact_0":   {"label": "Gandanta (sign junction)", "impact": "HIGH UNCERTAINTY — market reversal risk"},
    "exact_15":  {"label": "Mid-sign (stable)",         "impact": "STABLE — trend continuation"},
    "exact_29":  {"label": "Anaretic degree (final)",    "impact": "CRITICAL — completion phase, major move imminent"},
}

# Planetary strength in signs (for market prediction)
PLANET_SIGN_EFFECTS: Dict[str, Dict] = {
    "Jupiter": {
        "Aries":       (+0.70, "Bull run — new cycle begins. IT, Pharma lead."),
        "Taurus":      (+0.90, "Strong bull — Rohini/Taurus energy. Banking, FMCG boom."),
        "Gemini":      (+0.50, "Mixed — IT, Media volatile. Mercury's sign dilutes Jup."),
        "Cancer":      (+0.95, "Exalted Jupiter — peak bull market. All sectors up."),
        "Leo":         (+0.60, "Government/PSU focus. Large-cap outperformance."),
        "Virgo":       (-0.20, "Debilitated Jupiter — market correction risk."),
        "Libra":       (+0.65, "Balance/partnership. Banking, Legal services."),
        "Scorpio":     (+0.45, "Deep transformation. Insurance, Oil & Gas focus."),
        "Sagittarius": (+0.80, "Own sign — expansion. Education, Finance, Gold."),
        "Capricorn":   (-0.30, "Debilitated — structural corrections. Infrastructure stress."),
        "Aquarius":    (+0.55, "Technology/innovation. IT, Startup ecosystem."),
        "Pisces":      (+0.85, "Own sign — spiritual wealth. Banking, Pharma, Exports."),
    },
    "Saturn": {
        "Aries":       (-0.40, "Debilitated Saturn — sudden structural shocks. Avoid."),
        "Taurus":      (-0.10, "Slow but steady FMCG/Real Estate. Patient investment."),
        "Gemini":      (-0.20, "Communication/IT sector pressure. Telecom consolidation."),
        "Cancer":      (-0.35, "Emotional market stress. Real estate stagnation."),
        "Leo":         (-0.50, "Government/PSU sector heavy. Bureaucratic delays."),
        "Virgo":       (+0.20, "Analytical discipline. Healthcare/Pharma long-term gains."),
        "Libra":       (+0.40, "Exalted Saturn — long-term stability. Infrastructure wins."),
        "Scorpio":     (-0.30, "Transformation through pain. Insurance, Mining volatile."),
        "Sagittarius": (-0.20, "Philosophical/legal battles. Avoid speculative sectors."),
        "Capricorn":   (+0.50, "Own sign — disciplined growth. Oil, Mining, Utilities."),
        "Aquarius":    (+0.45, "Own sign — tech infrastructure. Long-term IT/Power."),
        "Pisces":      (-0.15, "Diffused energy. Export/shipping sector mixed."),
    },
    "Mars": {
        "Aries":       (+0.70, "Own sign — aggressive bull. Defense, Energy, Steel surge."),
        "Taurus":      (+0.30, "Steady but stubborn. Real estate activity increases."),
        "Gemini":      (+0.20, "Trading volatility. Short-term momentum in IT."),
        "Cancer":      (-0.50, "Debilitated Mars — emotional market crashes. Caution."),
        "Leo":         (+0.55, "Leadership/speculative surge. Large-caps outperform."),
        "Virgo":       (+0.25, "Technical analysis dominates. Precision sector gains."),
        "Libra":       (-0.10, "Mixed — partnerships/legal sector focus."),
        "Scorpio":     (+0.65, "Own sign — intense rally then correction. High volatility."),
        "Sagittarius": (+0.40, "Optimistic momentum. Export/commodities rally."),
        "Capricorn":   (+0.80, "Exalted Mars — strongest bull signal for Defense/Infra."),
        "Aquarius":    (+0.20, "Technology/innovation sector brief rally."),
        "Pisces":      (-0.20, "Diffused Mars energy. Pharma/Exports mixed."),
    },
    "Venus": {
        "Aries":       (+0.50, "Aggressive luxury spending. Auto, Hotels, Fashion."),
        "Taurus":      (+0.80, "Own sign Venus — FMCG, Luxury, Real estate boom."),
        "Gemini":      (+0.55, "Media, Entertainment, Telecom bullish."),
        "Cancer":      (+0.60, "Consumer sentiment high. FMCG, Hospitality up."),
        "Leo":         (+0.45, "Entertainment/glamour. Media stocks rally."),
        "Virgo":       (-0.30, "Debilitated Venus — consumer spending falls. FMCG weak."),
        "Libra":       (+0.85, "Own sign Venus — all consumer sectors thrive."),
        "Scorpio":     (-0.10, "Transformation in luxury. Hidden value plays."),
        "Sagittarius": (+0.50, "Travel, Tourism, Education sector gains."),
        "Capricorn":   (+0.40, "Disciplined spending. Long-term luxury brand growth."),
        "Aquarius":    (+0.55, "Tech-luxury convergence. EV, High-tech consumer."),
        "Pisces":      (+0.90, "Exalted Venus — premium bull signal for consumer sectors."),
    },
    "Mercury": {
        "Gemini":      (+0.85, "Own sign — IT, Telecom, Media, Banking all rally."),
        "Virgo":       (+0.90, "Exalted Mercury — precision analytics. IT services peak."),
        "Aries":       (+0.40, "Fast decisions. Short-term momentum trades work."),
        "Taurus":      (+0.55, "Practical finance. Banking analytics, FinTech gains."),
        "Cancer":      (-0.10, "Emotional communication. Consumer sentiment surveys."),
        "Leo":         (+0.50, "Government communication. PSU IT contracts."),
        "Libra":       (+0.60, "Balanced analysis. Legal-tech, Financial advisory."),
        "Scorpio":     (+0.30, "Deep research pays. Pharma research, Data analytics."),
        "Sagittarius": (-0.25, "Debilitated-like — speculation over analysis risk."),
        "Capricorn":   (+0.45, "Structural analysis. Infrastructure contracts."),
        "Aquarius":    (+0.70, "Innovation + communication. Fintech, AI sector boom."),
        "Pisces":      (-0.30, "Debilitated Mercury — poor communication, confusion in IT."),
    },
}

# Retrograde market effects
RETROGRADE_EFFECTS: Dict[str, Dict] = {
    "Mercury": {
        "duration": "~21 days (3x/year)",
        "market_effect": (
            "HIGH CAUTION: Communication breakdowns, technology glitches, contract delays. "
            "IT sector volatile. Avoid signing contracts or IPO applications. "
            "Re-examine existing positions — don't open new large trades."
        ),
        "sectors_affected": ["IT", "Telecom", "Banking", "Media", "Logistics"],
        "nse_action": "REDUCE RISK — close speculative positions",
        "score": -0.40,
    },
    "Venus": {
        "duration": "~40 days (every 18 months)",
        "market_effect": (
            "Consumer confidence drops. FMCG, Luxury, Auto sector corrections. "
            "Real estate deals fall through. Avoid luxury stock purchases."
        ),
        "sectors_affected": ["FMCG", "Auto", "Real Estate", "Luxury", "Entertainment"],
        "nse_action": "SELL consumer sector on rallies",
        "score": -0.35,
    },
    "Mars": {
        "duration": "~72 days (every 2 years)",
        "market_effect": (
            "Energy dissipated. Defense, Steel, Energy sectors consolidate. "
            "Real estate deals slow. Geopolitical tensions may ease surprisingly."
        ),
        "sectors_affected": ["Defense", "Steel", "Real Estate", "Energy"],
        "nse_action": "HOLD — avoid new positions in affected sectors",
        "score": -0.30,
    },
    "Jupiter": {
        "duration": "~120 days (annual)",
        "market_effect": (
            "Expansion contracts temporarily. Banking/Finance consolidation. "
            "Review and reassess — don't expand. Good time for value investing."
        ),
        "sectors_affected": ["Banking", "Finance", "Education", "Pharma"],
        "nse_action": "VALUE ACCUMULATE — long-term buys only",
        "score": -0.15,
    },
    "Saturn": {
        "duration": "~140 days (annual)",
        "market_effect": (
            "Structural review of slow sectors. Oil, Mining, Utilities pause. "
            "Karma settlements. Old debts and past issues resurface in markets."
        ),
        "sectors_affected": ["Oil & Gas", "Mining", "Infrastructure", "Utilities"],
        "nse_action": "LONG-TERM HOLD — no new infra positions",
        "score": -0.20,
    },
}

# Key planetary combinations for NSE/BSE
CONJUNCTION_ALERTS: Dict[str, Dict] = {
    "Jupiter-Saturn": {
        "cycle": "~20 years",
        "market_effect": "Great Conjunction — generational market shift. New economic paradigm begins.",
        "score": 0.70 if False else -0.10,  # Depends on sign
    },
    "Jupiter-Venus": {
        "market_effect": "Premium bull signal. Banking + consumer sector dual rally.",
        "score": 0.85,
    },
    "Mars-Saturn": {
        "market_effect": "Industrial conflict. Defense/infrastructure friction. Market volatility.",
        "score": -0.65,
    },
    "Saturn-Rahu": {
        "market_effect": "Karmic debt + illusion. Market bubbles burst. Systemic risk.",
        "score": -0.80,
    },
    "Jupiter-Rahu": {
        "market_effect": "Guru Chandala — inflated optimism then crash. Tech bubble risk.",
        "score": -0.40,
    },
    "Venus-Mars": {
        "market_effect": "Consumer + energy intersection. Auto sector surge. Short-lived.",
        "score": 0.40,
    },
}


def generate_transit_alerts(
    current_planets: List[Dict],
    natal_planets: Optional[List[Dict]] = None,
    natal_ascendant: Optional[Dict] = None,
    from_date: Optional[datetime] = None,
    days_ahead: int = 90,
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Generate comprehensive NSE/BSE transit alerts for the given period.
    Covers: sign transits, retrogrades, conjunctions, critical degrees,
    and natal chart transits.
    """
    if from_date is None:
        from_date = datetime.utcnow()

    ayanamsa_map = {
        "lahiri": swe.SIDM_LAHIRI,
        "raman": swe.SIDM_RAMAN,
        "krishnamurti": swe.SIDM_KRISHNAMURTI,
        "fagan_bradley": swe.SIDM_FAGAN_BRADLEY,
    }
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key.lower(), swe.SIDM_LAHIRI))

    all_alerts: List[Dict] = []

    # 1. Current planetary positions + sign effects
    current_sign_alerts = _current_sign_analysis(current_planets)
    all_alerts.extend(current_sign_alerts)

    # 2. Retrograde status
    retrograde_alerts = _check_retrogrades(current_planets, from_date)
    all_alerts.extend(retrograde_alerts)

    # 3. Critical degree alerts
    critical_alerts = _check_critical_degrees(current_planets)
    all_alerts.extend(critical_alerts)

    # 4. Planetary conjunctions
    conjunction_alerts = _check_conjunctions(current_planets)
    all_alerts.extend(conjunction_alerts)

    # 5. Upcoming sign ingresses (Jupiter, Saturn, Mars — slow planets)
    upcoming_ingresses = _calc_upcoming_ingresses(from_date, days_ahead, ayanamsa_key)
    all_alerts.extend(upcoming_ingresses)

    # 6. Upcoming retrogrades
    upcoming_retrogrades = _calc_upcoming_retrogrades(from_date, days_ahead)
    all_alerts.extend(upcoming_retrogrades)

    # 7. Eclipse detection
    eclipse_alerts = _calc_eclipse_alerts(from_date, days_ahead)
    all_alerts.extend(eclipse_alerts)

    # 8. Natal transits (if natal chart provided)
    natal_transits = []
    if natal_planets and natal_ascendant:
        natal_transits = _calc_natal_transits(current_planets, natal_planets, natal_ascendant)

    # Sort and prioritize
    all_alerts.sort(key=lambda x: (-x.get("priority", 0), x.get("date", "")))
    high_priority = [a for a in all_alerts if a.get("priority", 0) >= 8]
    medium_priority = [a for a in all_alerts if 5 <= a.get("priority", 0) < 8]
    low_priority = [a for a in all_alerts if a.get("priority", 0) < 5]

    overall_score = _calc_overall_market_score(all_alerts)
    outlook = _score_to_outlook(overall_score)

    return {
        "generated_date":    from_date.strftime("%Y-%m-%d %H:%M"),
        "days_ahead":        days_ahead,
        "market_score":      round(overall_score, 3),
        "market_outlook":    outlook["label"],
        "outlook_color":     outlook["color"],
        "recommendation":    outlook["recommendation"],
        "high_priority_alerts":   high_priority,
        "medium_priority_alerts": medium_priority,
        "low_priority_alerts":    low_priority,
        "natal_transits":    natal_transits,
        "total_alerts":      len(all_alerts),
        "nse_sectors": {
            "buy":   _collect_sectors(all_alerts, "buy"),
            "hold":  _collect_sectors(all_alerts, "hold"),
            "avoid": _collect_sectors(all_alerts, "avoid"),
        },
    }


def _current_sign_analysis(planets: List[Dict]) -> List[Dict]:
    """Analyze current planetary sign positions for market impact."""
    alerts = []
    key_planets = ["Jupiter", "Saturn", "Mars", "Venus", "Mercury"]

    for p in planets:
        if p["planet"] not in key_planets:
            continue
        effects = PLANET_SIGN_EFFECTS.get(p["planet"], {})
        sign_effect = effects.get(p["sign"])
        if sign_effect is None:
            continue
        score, description = sign_effect

        if abs(score) >= 0.50:
            alerts.append({
                "type":        "SIGN_TRANSIT",
                "planet":      p["planet"],
                "sign":        p["sign"],
                "date":        "CURRENT",
                "description": f"{p['planet']} in {p['sign']}: {description}",
                "score":       score,
                "priority":    int(abs(score) * 10),
                "signal":      "BULLISH" if score > 0.3 else "BEARISH" if score < -0.3 else "NEUTRAL",
            })
    return alerts


def _check_retrogrades(planets: List[Dict], date: datetime) -> List[Dict]:
    """Check currently retrograde planets and their market impact."""
    alerts = []
    for p in planets:
        if p.get("retrograde") and p["planet"] in RETROGRADE_EFFECTS:
            effect = RETROGRADE_EFFECTS[p["planet"]]
            alerts.append({
                "type":             "RETROGRADE_ACTIVE",
                "planet":           p["planet"],
                "sign":             p["sign"],
                "date":             date.strftime("%Y-%m-%d"),
                "description":      f"⚠️ {p['planet']} RETROGRADE in {p['sign']}: {effect['market_effect']}",
                "sectors_affected": effect["sectors_affected"],
                "score":            effect["score"],
                "priority":         8,
                "signal":           "CAUTION",
                "action":           effect["nse_action"],
            })
    return alerts


def _check_critical_degrees(planets: List[Dict]) -> List[Dict]:
    """Check if any planets are at critical degrees."""
    alerts = []
    for p in planets:
        deg_in_sign = p["degree_in_sign"]
        if deg_in_sign <= 1.0 or deg_in_sign >= 29.0:
            label = "Gandanta/Sandhi (0°)" if deg_in_sign <= 1.0 else "Anaretic (29°)"
            alerts.append({
                "type":        "CRITICAL_DEGREE",
                "planet":      p["planet"],
                "sign":        p["sign"],
                "degree":      deg_in_sign,
                "date":        "CURRENT",
                "description": f"🎯 {p['planet']} at {label} in {p['sign']} — market turning point imminent.",
                "score":       -0.30,
                "priority":    7,
                "signal":      "WATCH CAREFULLY",
            })
    return alerts


def _check_conjunctions(planets: List[Dict]) -> List[Dict]:
    """Check current planetary conjunctions."""
    alerts = []
    n = len(planets)
    for i in range(n):
        for j in range(i + 1, n):
            p1, p2 = planets[i], planets[j]
            if p1["sign"] != p2["sign"]:
                continue
            long1, long2 = p1["longitude"], p2["longitude"]
            orb = abs(long1 - long2) % 360
            orb = min(orb, 360 - orb)
            if orb > 10:
                continue

            pair_key = f"{p1['planet']}-{p2['planet']}"
            pair_key2 = f"{p2['planet']}-{p1['planet']}"
            effect = CONJUNCTION_ALERTS.get(pair_key) or CONJUNCTION_ALERTS.get(pair_key2)

            if effect:
                score = effect.get("score", 0)
                alerts.append({
                    "type":        "CONJUNCTION",
                    "planet":      pair_key,
                    "sign":        p1["sign"],
                    "orb_degrees": round(orb, 2),
                    "date":        "CURRENT",
                    "description": (
                        f"🔮 {pair_key} conjunction in {p1['sign']} (orb {orb:.1f}°): "
                        f"{effect['market_effect']}"
                    ),
                    "score":       score,
                    "priority":    9 if abs(score) > 0.5 else 6,
                    "signal":      "STRONGLY BULLISH" if score > 0.5 else
                                   "BULLISH" if score > 0 else
                                   "BEARISH" if score < -0.5 else "CAUTIOUS",
                })
    return alerts


def _calc_upcoming_ingresses(
    from_date: datetime, days_ahead: int, ayanamsa_key: str
) -> List[Dict]:
    """Calculate upcoming sign changes for slow planets."""
    ayanamsa_map = {"lahiri": swe.SIDM_LAHIRI, "raman": swe.SIDM_RAMAN,
                    "krishnamurti": swe.SIDM_KRISHNAMURTI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key.lower(), swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    slow_planets = {"Jupiter": swe.JUPITER, "Saturn": swe.SATURN, "Mars": swe.MARS}
    alerts = []

    jd_start = swe.julday(from_date.year, from_date.month, from_date.day,
                           from_date.hour + from_date.minute / 60.0)
    jd_end = jd_start + days_ahead

    for pname, pid in slow_planets.items():
        r = swe.calc_ut(jd_start, pid, flags)
        prev_sign = int(r[0][0] / 30) % 12
        jd = jd_start

        while jd < jd_end:
            jd += 1.0
            r = swe.calc_ut(jd, pid, flags)
            curr_sign = int(r[0][0] / 30) % 12
            speed = r[0][3]

            if curr_sign != prev_sign:
                precise_jd = _bisect_ingress(pid, flags, jd - 1, jd, prev_sign)
                y, m, d, h = swe.revjul(precise_jd)
                try:
                    dt = datetime(int(y), int(m), int(d))
                    effect = PLANET_SIGN_EFFECTS.get(pname, {}).get(SIGNS[curr_sign])
                    score = effect[0] if effect else 0
                    desc = effect[1] if effect else ""
                    retro = speed < 0
                    alerts.append({
                        "type":        "UPCOMING_INGRESS",
                        "planet":      pname,
                        "entering_sign": SIGNS[curr_sign],
                        "from_sign":   SIGNS[prev_sign],
                        "date":        dt.strftime("%Y-%m-%d"),
                        "retrograde":  retro,
                        "description": (
                            f"📅 {pname} {'(R) ' if retro else ''}enters {SIGNS[curr_sign]} "
                            f"on {dt.strftime('%d %b %Y')}: {desc}"
                        ),
                        "score":       score,
                        "priority":    9 if pname in ("Jupiter", "Saturn") else 7,
                        "signal":      "BULLISH" if score > 0.3 else "BEARISH" if score < -0.3 else "NEUTRAL",
                    })
                except (ValueError, OverflowError):
                    pass
                prev_sign = curr_sign

    return alerts


def _bisect_ingress(pid, flags, jd_lo, jd_hi, prev_sign, n=20):
    for _ in range(n):
        mid = (jd_lo + jd_hi) / 2
        r = swe.calc_ut(mid, pid, flags)
        if int(r[0][0] / 30) % 12 == prev_sign:
            jd_lo = mid
        else:
            jd_hi = mid
    return (jd_lo + jd_hi) / 2


def _calc_upcoming_retrogrades(from_date: datetime, days_ahead: int) -> List[Dict]:
    """Detect upcoming retrograde stations."""
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED
    swe.set_sid_mode(swe.SIDM_LAHIRI)

    planet_ids = {"Mercury": swe.MERCURY, "Venus": swe.VENUS,
                  "Mars": swe.MARS, "Jupiter": swe.JUPITER, "Saturn": swe.SATURN}
    alerts = []
    jd_start = swe.julday(from_date.year, from_date.month, from_date.day, 12.0)
    jd_end = jd_start + days_ahead

    for pname, pid in planet_ids.items():
        r0 = swe.calc_ut(jd_start, pid, flags)
        prev_speed = r0[0][3]
        jd = jd_start

        while jd < jd_end:
            jd += 1.0
            r = swe.calc_ut(jd, pid, flags)
            speed = r[0][3]
            sign = SIGNS[int(r[0][0] / 30) % 12]

            # Retrograde station (direct → retrograde)
            if prev_speed >= 0 and speed < 0:
                y, m, d, _ = swe.revjul(jd)
                try:
                    dt = datetime(int(y), int(m), int(d))
                    eff = RETROGRADE_EFFECTS.get(pname, {})
                    alerts.append({
                        "type":             "UPCOMING_RETROGRADE",
                        "planet":           pname,
                        "sign":             sign,
                        "date":             dt.strftime("%Y-%m-%d"),
                        "description":      (
                            f"⏪ {pname} goes RETROGRADE in {sign} on {dt.strftime('%d %b %Y')}. "
                            f"{eff.get('market_effect','')}"
                        ),
                        "sectors_affected": eff.get("sectors_affected", []),
                        "score":            eff.get("score", -0.30),
                        "priority":         8,
                        "signal":           "CAUTION",
                        "action":           eff.get("nse_action", "Reduce risk"),
                    })
                except (ValueError, OverflowError):
                    pass

            # Direct station (retrograde → direct)
            elif prev_speed <= 0 and speed > 0:
                y, m, d, _ = swe.revjul(jd)
                try:
                    dt = datetime(int(y), int(m), int(d))
                    alerts.append({
                        "type":        "RETROGRADE_DIRECT",
                        "planet":      pname,
                        "sign":        sign,
                        "date":        dt.strftime("%Y-%m-%d"),
                        "description": (
                            f"▶️ {pname} goes DIRECT in {sign} on {dt.strftime('%d %b %Y')}. "
                            "Sector activity resumes — BUY on confirmation."
                        ),
                        "score":       0.35,
                        "priority":    7,
                        "signal":      "BUY on confirmation",
                    })
                except (ValueError, OverflowError):
                    pass

            prev_speed = speed

    return alerts


def _calc_eclipse_alerts(from_date: datetime, days_ahead: int) -> List[Dict]:
    """Detect solar and lunar eclipses."""
    alerts = []
    jd_start = swe.julday(from_date.year, from_date.month, from_date.day, 12.0)
    jd_end = jd_start + days_ahead

    # Scan for eclipses
    jd = jd_start
    while jd < jd_end:
        # Check for solar eclipse
        ecl = swe.sol_eclipse_when_glob(jd, swe.FLG_SWIEPH | swe.HELFLAG_LONG_SEARCH, 0)
        if ecl and ecl[0] >= 0:
            eclipse_jd = ecl[1][0]
            if jd_start <= eclipse_jd <= jd_end:
                y, m, d, _ = swe.revjul(eclipse_jd)
                try:
                    dt = datetime(int(y), int(m), int(d))
                    alerts.append({
                        "type":        "SOLAR_ECLIPSE",
                        "date":        dt.strftime("%Y-%m-%d"),
                        "description": (
                            f"☀️🌑 SOLAR ECLIPSE on {dt.strftime('%d %b %Y')}. "
                            "Major market event — trend reversal likely within 2 weeks. "
                            "Reduce equity exposure before eclipse date."
                        ),
                        "score":       -0.60,
                        "priority":    10,
                        "signal":      "HIGH CAUTION — major reversal risk",
                        "pre_action":  "Reduce equity 5 days before",
                        "post_action": "Buy quality on confirmation 7 days after",
                    })
                except (ValueError, OverflowError):
                    pass
            jd = eclipse_jd + 25  # Skip ahead
        else:
            jd += 25

    # Lunar eclipses
    jd = jd_start
    while jd < jd_end:
        ecl = swe.lun_eclipse_when(jd, swe.FLG_SWIEPH | swe.HELFLAG_LONG_SEARCH, 0)
        if ecl and ecl[0] >= 0:
            eclipse_jd = ecl[1][0]
            if jd_start <= eclipse_jd <= jd_end:
                y, m, d, _ = swe.revjul(eclipse_jd)
                try:
                    dt = datetime(int(y), int(m), int(d))
                    alerts.append({
                        "type":        "LUNAR_ECLIPSE",
                        "date":        dt.strftime("%Y-%m-%d"),
                        "description": (
                            f"🌕🌑 LUNAR ECLIPSE on {dt.strftime('%d %b %Y')}. "
                            "Emotional market response — consumer/FMCG volatile. "
                            "Short-term correction likely."
                        ),
                        "score":       -0.40,
                        "priority":    9,
                        "signal":      "CAUTION — short-term correction",
                    })
                except (ValueError, OverflowError):
                    pass
            jd = eclipse_jd + 25
        else:
            jd += 25

    return alerts


def _calc_natal_transits(
    current_planets: List[Dict],
    natal_planets: List[Dict],
    natal_ascendant: Dict,
) -> List[Dict]:
    """Analyze current transits over natal chart positions."""
    alerts = []
    natal_asc_sign = natal_ascendant["sign"]
    asc_idx = SIGN_IDX.get(natal_asc_sign, 0)

    for transit_p in current_planets:
        for natal_p in natal_planets:
            t_long = transit_p["longitude"]
            n_long = natal_p["longitude"]
            diff = abs(t_long - n_long) % 360
            diff = min(diff, 360 - diff)

            if diff <= 3.0:  # Conjunction orb 3°
                house_num = ((SIGN_IDX.get(natal_p["sign"], 0) - asc_idx) % 12) + 1
                h_effect = {2: "wealth", 5: "speculation/stocks", 8: "sudden events",
                             9: "fortune", 10: "career", 11: "income gains"}.get(house_num, "")
                alerts.append({
                    "type":         "NATAL_TRANSIT",
                    "transit_planet": transit_p["planet"],
                    "natal_planet": natal_p["planet"],
                    "house":        house_num,
                    "orb":          round(diff, 2),
                    "description":  (
                        f"Transit {transit_p['planet']} conjunct natal {natal_p['planet']} "
                        f"in {house_num}th house ({h_effect}). Orb: {diff:.1f}°"
                    ),
                    "score":        0.5 if transit_p["planet"] in {"Jupiter", "Venus"} else -0.3,
                    "priority":     7,
                    "signal":       "PERSONAL MARKET PEAK" if house_num in (2, 5, 11) else "WATCH",
                })

    return alerts


def _calc_overall_market_score(alerts: List[Dict]) -> float:
    """Weighted average of all alert scores."""
    if not alerts:
        return 0.0
    total_weight = sum(a.get("priority", 5) for a in alerts)
    weighted_sum = sum(a.get("score", 0) * a.get("priority", 5) for a in alerts)
    return weighted_sum / total_weight if total_weight > 0 else 0.0


def _score_to_outlook(score: float) -> Dict:
    if score >= 0.50:
        return {"label": "STRONGLY BULLISH", "color": "#00C851",
                "recommendation": "Maximum equity allocation; growth sectors lead."}
    if score >= 0.25:
        return {"label": "BULLISH", "color": "#4CAF50",
                "recommendation": "Overweight equities; focus on signaled sectors."}
    if score >= 0.0:
        return {"label": "MILDLY BULLISH", "color": "#8BC34A",
                "recommendation": "Selective buying; defensive + growth mix."}
    if score >= -0.25:
        return {"label": "CAUTIOUS", "color": "#FF9800",
                "recommendation": "Reduce high-beta; hold blue chips; increase Gold."}
    if score >= -0.50:
        return {"label": "BEARISH", "color": "#FF5722",
                "recommendation": "Defensive posture; Gold + bonds + cash."}
    return {"label": "STRONGLY BEARISH", "color": "#FF3D00",
            "recommendation": "Capital preservation; exit equities; Gold/bonds/FD."}


def _collect_sectors(alerts: List[Dict], mode: str) -> List[str]:
    sectors: List[str] = []
    for a in alerts:
        score = a.get("score", 0)
        if mode == "buy" and score > 0.3:
            sectors.extend(a.get("sectors_affected", []))
        elif mode == "avoid" and score < -0.3:
            sectors.extend(a.get("sectors_affected", []))
    return list(dict.fromkeys(sectors))[:6]  # Deduplicated, top 6
