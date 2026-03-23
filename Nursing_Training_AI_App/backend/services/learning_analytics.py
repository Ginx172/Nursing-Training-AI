"""
Learning Analytics Service — dashboard stats, heatmaps, progression,
question quality flagging, and weekly/monthly summaries.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Any, Dict, List, Optional

from core.self_learning import SelfLearning, DIMENSIONS
from core.continuous_learning import ContinuousLearning

_sl = SelfLearning()
_cl = ContinuousLearning()

PASS_SCORE = 60.0


def _load_outcomes() -> List[Dict[str, Any]]:
    return _cl._load_outcomes()


# ------------------------------------------------------------------ #
# Dashboard                                                            #
# ------------------------------------------------------------------ #

def get_dashboard_stats() -> Dict[str, Any]:
    """Return high-level platform statistics."""
    outcomes = _load_outcomes()
    if not outcomes:
        return {"total_evaluations": 0, "avg_score": 0.0, "pass_rate": 0.0,
                "active_specialties": 0, "active_bands": 0}
    scores = [o.get("overall_score", 0.0) for o in outcomes]
    specialties = {o.get("specialty") for o in outcomes if o.get("specialty")}
    bands = {o.get("band") for o in outcomes if o.get("band")}
    return {
        "total_evaluations": len(outcomes),
        "avg_score": round(sum(scores) / len(scores), 2),
        "pass_rate": round(sum(1 for s in scores if s >= PASS_SCORE) / len(scores) * 100, 2),
        "active_specialties": len(specialties),
        "active_bands": len(bands),
    }


# ------------------------------------------------------------------ #
# Per-specialty heatmap                                                #
# ------------------------------------------------------------------ #

def get_specialty_heatmap() -> List[Dict[str, Any]]:
    """Return avg dimension scores per specialty (for heatmap visualisation)."""
    outcomes = _load_outcomes()
    groups: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
    for o in outcomes:
        sp = o.get("specialty", "unknown")
        ds = o.get("detailed_scores", {})
        for dim in DIMENSIONS:
            if dim in ds:
                groups[sp][dim].append(float(ds[dim]))
    result = []
    for sp, dim_scores in groups.items():
        row: Dict[str, Any] = {"specialty": sp}
        for dim in DIMENSIONS:
            vals = dim_scores.get(dim, [])
            row[dim] = round(sum(vals) / len(vals), 2) if vals else 0.0
        result.append(row)
    return result


# ------------------------------------------------------------------ #
# Per-band progression                                                 #
# ------------------------------------------------------------------ #

def get_band_progression() -> List[Dict[str, Any]]:
    """Return avg score and pass rate per NHS band."""
    outcomes = _load_outcomes()
    groups: Dict[str, List[float]] = defaultdict(list)
    for o in outcomes:
        band = o.get("band", "unknown")
        groups[band].append(float(o.get("overall_score", 0.0)))
    result = []
    for band, scores in sorted(groups.items()):
        result.append({
            "band": band,
            "evaluations": len(scores),
            "avg_score": round(sum(scores) / len(scores), 2),
            "pass_rate": round(sum(1 for s in scores if s >= PASS_SCORE) / len(scores) * 100, 2),
        })
    return result


# ------------------------------------------------------------------ #
# Question quality flagging                                            #
# ------------------------------------------------------------------ #

def get_question_quality_flags() -> Dict[str, List[int]]:
    """Return question IDs flagged as too hard or too easy."""
    outcomes = _load_outcomes()
    return _cl.calibrate_question_difficulty(outcomes)


# ------------------------------------------------------------------ #
# Weekly / monthly summaries                                           #
# ------------------------------------------------------------------ #

def _summary_for_period(
    outcomes: List[Dict[str, Any]],
    start: datetime,
    end: datetime,
    label: str,
) -> Dict[str, Any]:
    period_outcomes = []
    for o in outcomes:
        ts_str = o.get("timestamp")
        if ts_str:
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if start <= ts < end:
                    period_outcomes.append(o)
            except Exception:
                pass
    scores = [o.get("overall_score", 0.0) for o in period_outcomes]
    return {
        "period": label,
        "start": start.isoformat(),
        "end": end.isoformat(),
        "evaluations": len(period_outcomes),
        "avg_score": round(sum(scores) / len(scores), 2) if scores else 0.0,
        "pass_rate": round(sum(1 for s in scores if s >= PASS_SCORE) / len(scores) * 100, 2) if scores else 0.0,
    }


def get_weekly_summary(weeks: int = 4) -> List[Dict[str, Any]]:
    outcomes = _load_outcomes()
    now = datetime.now(timezone.utc)
    summaries = []
    for i in range(weeks - 1, -1, -1):
        end = now - timedelta(weeks=i)
        start = end - timedelta(weeks=1)
        label = f"Week of {start.strftime('%Y-%m-%d')}"
        summaries.append(_summary_for_period(outcomes, start, end, label))
    return summaries


def get_monthly_summary(months: int = 6) -> List[Dict[str, Any]]:
    outcomes = _load_outcomes()
    now = datetime.now(timezone.utc)
    summaries = []
    for i in range(months - 1, -1, -1):
        end = now - timedelta(days=30 * i)
        start = end - timedelta(days=30)
        label = start.strftime("%B %Y")
        summaries.append(_summary_for_period(outcomes, start, end, label))
    return summaries


# ------------------------------------------------------------------ #
# Convenience re-exports used by the API router                        #
# ------------------------------------------------------------------ #

def get_failure_patterns() -> List[Dict[str, Any]]:
    return _sl.get_failure_patterns()


def get_trends() -> Dict[str, str]:
    return _sl.get_trends()


def get_specialty_band_stats() -> Dict[str, Any]:
    return _sl.get_specialty_band_stats()
