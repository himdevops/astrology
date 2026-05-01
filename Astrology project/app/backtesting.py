"""
backtesting.py — Astrological Signal Backtesting Engine
Tests Vedic astrology predictions against historical NSE/BSE data.

Features:
1. Signal-by-signal backtesting (Moon nakshatra, Dasha, Yoga, etc.)
2. Composite prediction backtesting
3. Accuracy metrics, hit ratio, correlation analysis
4. Sector rotation validation
5. Drawdown and risk analysis
"""
from __future__ import annotations

import math
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple

import swisseph as swe

from app.constants import SIGNS, NAKSHATRA_SPAN_DEG
from app.nakshatra import get_moon_nakshatra_signal, get_nakshatra
from app.prediction_engine import (
    PLANET_WEIGHTS, SIGN_SCORES, PLANET_SIGN_SCORES,
    _calc_planet_score, _score_to_prediction,
)


def backtest_moon_nakshatra(
    market_data: List[Dict],
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Backtest Moon Nakshatra signals against actual market returns.
    For each trading day, calculate Moon's nakshatra and compare
    the predicted signal with actual Nifty return.

    market_data: list of {date, open, high, low, close, volume}
    """
    ayanamsa_map = {"lahiri": swe.SIDM_LAHIRI, "krishnamurti": swe.SIDM_KRISHNAMURTI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key, swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    results = []
    correct = 0
    total = 0
    cumulative_return = 0.0

    for i, day in enumerate(market_data):
        if i == 0:
            continue  # Need previous day for return

        try:
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            jd = swe.julday(dt.year, dt.month, dt.day, 3.75)  # ~9:15 AM IST = 3:45 UTC
            moon = swe.calc_ut(jd, swe.MOON, flags)
            moon_long = moon[0][0] % 360

            signal = get_moon_nakshatra_signal(moon_long)
            nak_score = signal.get("financial_score", 0)
            predicted_direction = "UP" if nak_score > 0 else "DOWN" if nak_score < 0 else "FLAT"

            actual_return = (day["close"] - market_data[i - 1]["close"]) / market_data[i - 1]["close"] * 100
            actual_direction = "UP" if actual_return > 0.1 else "DOWN" if actual_return < -0.1 else "FLAT"

            is_correct = predicted_direction == actual_direction
            if predicted_direction != "FLAT":
                total += 1
                if is_correct:
                    correct += 1

            # Simulated P&L: if signal says UP, go long; DOWN go short
            if nak_score > 0:
                pnl = actual_return
            elif nak_score < 0:
                pnl = -actual_return
            else:
                pnl = 0
            cumulative_return += pnl

            results.append({
                "date": day["date"],
                "nakshatra": signal.get("moon_nakshatra", ""),
                "nak_score": nak_score,
                "predicted": predicted_direction,
                "actual_return_pct": round(actual_return, 4),
                "actual_direction": actual_direction,
                "correct": is_correct,
                "daily_pnl_pct": round(pnl, 4),
                "cumulative_pnl_pct": round(cumulative_return, 4),
            })
        except Exception:
            continue

    hit_ratio = (correct / total * 100) if total > 0 else 0

    # Nakshatra-wise accuracy
    nak_accuracy = _nakshatra_wise_accuracy(results)

    return {
        "type": "backtest_moon_nakshatra",
        "total_trading_days": len(results),
        "signals_generated": total,
        "correct_predictions": correct,
        "hit_ratio_pct": round(hit_ratio, 2),
        "cumulative_return_pct": round(cumulative_return, 2),
        "avg_daily_pnl": round(cumulative_return / len(results), 4) if results else 0,
        "nakshatra_accuracy": nak_accuracy,
        "daily_results": results[-30:],  # Last 30 days for brevity
        "assessment": _assess_backtest(hit_ratio, cumulative_return),
    }


def backtest_planetary_transits(
    market_data: List[Dict],
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Backtest composite planetary transit signals.
    Uses weighted planet-sign scores vs actual market returns.
    """
    ayanamsa_map = {"lahiri": swe.SIDM_LAHIRI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key, swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
    }

    results = []
    correct = 0
    total = 0
    cumulative = 0.0

    for i, day in enumerate(market_data):
        if i == 0:
            continue

        try:
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            jd = swe.julday(dt.year, dt.month, dt.day, 3.75)

            planets = []
            for name, pid in planet_ids.items():
                r = swe.calc_ut(jd, pid, flags)
                long = r[0][0] % 360
                speed = r[0][3]
                sign_idx = int(long / 30)
                planets.append({
                    "planet": name,
                    "longitude": long,
                    "sign": SIGNS[sign_idx],
                    "speed": speed,
                    "retrograde": speed < 0,
                })

            score, _ = _calc_planet_score(planets)
            predicted = "UP" if score > 0.55 else "DOWN" if score < 0.45 else "FLAT"

            actual_return = (day["close"] - market_data[i - 1]["close"]) / market_data[i - 1]["close"] * 100
            actual = "UP" if actual_return > 0.1 else "DOWN" if actual_return < -0.1 else "FLAT"

            if predicted != "FLAT":
                total += 1
                if predicted == actual:
                    correct += 1

            pnl = actual_return if score > 0.55 else (-actual_return if score < 0.45 else 0)
            cumulative += pnl

            results.append({
                "date": day["date"],
                "planet_score": round(score, 4),
                "predicted": predicted,
                "actual_return_pct": round(actual_return, 4),
                "actual": actual,
                "correct": predicted == actual,
                "daily_pnl_pct": round(pnl, 4),
                "cumulative_pnl_pct": round(cumulative, 4),
            })
        except Exception:
            continue

    hit_ratio = (correct / total * 100) if total > 0 else 0

    return {
        "type": "backtest_planetary_transits",
        "total_trading_days": len(results),
        "signals_generated": total,
        "correct_predictions": correct,
        "hit_ratio_pct": round(hit_ratio, 2),
        "cumulative_return_pct": round(cumulative, 2),
        "risk_metrics": _calc_risk_metrics(results),
        "daily_results": results[-30:],
        "assessment": _assess_backtest(hit_ratio, cumulative),
    }


def backtest_composite(
    market_data: List[Dict],
    ayanamsa_key: str = "lahiri",
) -> Dict:
    """
    Full composite backtest combining all signals:
    Moon nakshatra + Planetary transits + Panchang elements.
    """
    ayanamsa_map = {"lahiri": swe.SIDM_LAHIRI}
    swe.set_sid_mode(ayanamsa_map.get(ayanamsa_key, swe.SIDM_LAHIRI))
    flags = swe.FLG_SWIEPH | swe.FLG_SIDEREAL | swe.FLG_SPEED

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN,
    }

    results = []
    correct = 0
    total = 0
    cumulative = 0.0

    for i, day in enumerate(market_data):
        if i == 0:
            continue

        try:
            dt = datetime.strptime(day["date"], "%Y-%m-%d")
            jd = swe.julday(dt.year, dt.month, dt.day, 3.75)

            # Get all planet positions
            planets = []
            for name, pid in planet_ids.items():
                r = swe.calc_ut(jd, pid, flags)
                long = r[0][0] % 360
                speed = r[0][3]
                sign_idx = int(long / 30)
                planets.append({
                    "planet": name,
                    "longitude": long,
                    "sign": SIGNS[sign_idx],
                    "speed": speed,
                    "retrograde": speed < 0,
                })

            # Signal 1: Planetary transit score
            planet_score, _ = _calc_planet_score(planets)

            # Signal 2: Moon nakshatra
            moon = next((p for p in planets if p["planet"] == "Moon"), None)
            nak_score = 0.0
            if moon:
                nak_signal = get_moon_nakshatra_signal(moon["longitude"])
                nak_score = nak_signal.get("financial_score", 0)

            # Signal 3: Tithi (Sun-Moon angle)
            sun = next((p for p in planets if p["planet"] == "Sun"), None)
            tithi_score = 0.0
            if sun and moon:
                diff = (moon["longitude"] - sun["longitude"]) % 360
                tithi_num = int(diff / 12.0) % 15
                # Rikta tithis (4, 9, 14) are bad
                if tithi_num in (3, 8, 13):
                    tithi_score = -0.40
                elif tithi_num in (4, 9):  # Purna tithis
                    tithi_score = 0.50
                else:
                    tithi_score = 0.10

            # Signal 4: Retrograde penalty
            retro_count = sum(1 for p in planets if p.get("retrograde") and p["planet"] in ("Mercury", "Venus", "Mars"))
            retro_penalty = retro_count * -0.15

            # Composite score
            composite = (
                planet_score * 0.35 +
                nak_score * 0.25 +
                tithi_score * 0.20 +
                retro_penalty +
                0.10  # bias
            )
            composite = max(-1, min(1, composite))

            predicted = "UP" if composite > 0.15 else "DOWN" if composite < -0.15 else "FLAT"
            actual_return = (day["close"] - market_data[i - 1]["close"]) / market_data[i - 1]["close"] * 100
            actual = "UP" if actual_return > 0.1 else "DOWN" if actual_return < -0.1 else "FLAT"

            if predicted != "FLAT":
                total += 1
                if predicted == actual:
                    correct += 1

            pnl = actual_return if composite > 0.15 else (-actual_return if composite < -0.15 else 0)
            cumulative += pnl

            results.append({
                "date": day["date"],
                "composite_score": round(composite, 4),
                "planet_score": round(planet_score, 4),
                "nakshatra_score": round(nak_score, 3),
                "tithi_score": round(tithi_score, 3),
                "retro_penalty": round(retro_penalty, 3),
                "predicted": predicted,
                "actual_return_pct": round(actual_return, 4),
                "actual": actual,
                "correct": predicted == actual,
                "daily_pnl_pct": round(pnl, 4),
                "cumulative_pnl_pct": round(cumulative, 4),
            })
        except Exception:
            continue

    hit_ratio = (correct / total * 100) if total > 0 else 0

    return {
        "type": "backtest_composite",
        "total_trading_days": len(results),
        "signals_generated": total,
        "correct_predictions": correct,
        "hit_ratio_pct": round(hit_ratio, 2),
        "cumulative_return_pct": round(cumulative, 2),
        "risk_metrics": _calc_risk_metrics(results),
        "signal_distribution": {
            "bullish_signals": sum(1 for r in results if r["predicted"] == "UP"),
            "bearish_signals": sum(1 for r in results if r["predicted"] == "DOWN"),
            "neutral_signals": sum(1 for r in results if r["predicted"] == "FLAT"),
        },
        "daily_results": results[-30:],
        "monthly_summary": _monthly_summary(results),
        "assessment": _assess_backtest(hit_ratio, cumulative),
    }


# ─────────────────────────────────────────────────────────────
# Helper Functions
# ─────────────────────────────────────────────────────────────

def _nakshatra_wise_accuracy(results: List[Dict]) -> List[Dict]:
    """Calculate accuracy per nakshatra."""
    nak_stats: Dict[str, Dict] = {}
    for r in results:
        nak = r.get("nakshatra", "Unknown")
        if nak not in nak_stats:
            nak_stats[nak] = {"total": 0, "correct": 0, "pnl": 0.0}
        if r.get("predicted") != "FLAT":
            nak_stats[nak]["total"] += 1
            if r.get("correct"):
                nak_stats[nak]["correct"] += 1
        nak_stats[nak]["pnl"] += r.get("daily_pnl_pct", 0)

    accuracy = []
    for nak, stats in sorted(nak_stats.items()):
        hit = (stats["correct"] / stats["total"] * 100) if stats["total"] > 0 else 0
        accuracy.append({
            "nakshatra": nak,
            "signals": stats["total"],
            "correct": stats["correct"],
            "hit_ratio": round(hit, 1),
            "total_pnl": round(stats["pnl"], 2),
        })

    return sorted(accuracy, key=lambda x: -x["hit_ratio"])


def _calc_risk_metrics(results: List[Dict]) -> Dict:
    """Calculate risk metrics for the backtest."""
    if not results:
        return {}

    pnls = [r.get("daily_pnl_pct", 0) for r in results]
    cum = [r.get("cumulative_pnl_pct", 0) for r in results]

    # Max drawdown
    peak = 0.0
    max_dd = 0.0
    for c in cum:
        if c > peak:
            peak = c
        dd = peak - c
        if dd > max_dd:
            max_dd = dd

    # Sharpe ratio (simplified, annualized)
    avg = sum(pnls) / len(pnls) if pnls else 0
    std = math.sqrt(sum((p - avg) ** 2 for p in pnls) / len(pnls)) if len(pnls) > 1 else 1
    sharpe = (avg / std) * math.sqrt(252) if std > 0 else 0

    # Win/Loss ratio
    wins = [p for p in pnls if p > 0]
    losses = [p for p in pnls if p < 0]
    avg_win = sum(wins) / len(wins) if wins else 0
    avg_loss = abs(sum(losses) / len(losses)) if losses else 1

    return {
        "max_drawdown_pct": round(max_dd, 2),
        "sharpe_ratio": round(sharpe, 2),
        "avg_daily_pnl": round(avg, 4),
        "std_daily_pnl": round(std, 4),
        "win_loss_ratio": round(avg_win / avg_loss, 2) if avg_loss > 0 else 0,
        "total_wins": len(wins),
        "total_losses": len(losses),
        "best_day": round(max(pnls), 2) if pnls else 0,
        "worst_day": round(min(pnls), 2) if pnls else 0,
    }


def _monthly_summary(results: List[Dict]) -> List[Dict]:
    """Group backtest results by month."""
    months: Dict[str, List] = {}
    for r in results:
        month_key = r["date"][:7]  # YYYY-MM
        if month_key not in months:
            months[month_key] = []
        months[month_key].append(r)

    summary = []
    for month, days in sorted(months.items()):
        total_pnl = sum(d.get("daily_pnl_pct", 0) for d in days)
        total_signals = sum(1 for d in days if d.get("predicted") != "FLAT")
        correct = sum(1 for d in days if d.get("correct") and d.get("predicted") != "FLAT")
        hit = (correct / total_signals * 100) if total_signals > 0 else 0

        summary.append({
            "month": month,
            "trading_days": len(days),
            "signals": total_signals,
            "correct": correct,
            "hit_ratio": round(hit, 1),
            "monthly_return_pct": round(total_pnl, 2),
        })

    return summary


def _assess_backtest(hit_ratio: float, cumulative_return: float) -> Dict:
    """Overall assessment of backtest quality."""
    if hit_ratio >= 60 and cumulative_return > 0:
        grade = "A"
        verdict = "Strong predictive signal — viable for trading"
    elif hit_ratio >= 55 and cumulative_return > 0:
        grade = "B"
        verdict = "Moderate signal — use as one of multiple confirmations"
    elif hit_ratio >= 50:
        grade = "C"
        verdict = "Marginal signal — combine with other indicators"
    else:
        grade = "D"
        verdict = "Weak signal — needs improvement or different parameters"

    return {
        "grade": grade,
        "verdict": verdict,
        "hit_ratio_assessment": (
            "Excellent" if hit_ratio >= 60 else
            "Good" if hit_ratio >= 55 else
            "Fair" if hit_ratio >= 50 else "Poor"
        ),
        "return_assessment": (
            "Profitable" if cumulative_return > 10 else
            "Marginally Profitable" if cumulative_return > 0 else
            "Loss-making"
        ),
    }
