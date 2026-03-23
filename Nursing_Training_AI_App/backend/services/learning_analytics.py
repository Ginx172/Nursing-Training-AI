"""
Learning analytics: dashboard stats, specialty heatmap, band progression,
question quality flags, weekly/monthly summaries.
"""

from __future__ import annotations

from collections import defaultdict
from datetime import datetime, timedelta
from typing import Any, Dict, List, Optional

from core.self_learning import DIMENSIONS, self_learning


class LearningAnalyticsService:
    """Aggregates and surfaces learning metrics for dashboards and reports."""

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_dashboard_stats(self) -> Dict[str, Any]:
        """Return high-level KPIs for the dashboard."""
        outcomes = self_learning._load_outcomes()
        if not outcomes:
            return {"total_evaluations": 0, "avg_overall_score": None,
                    "trend": "no_data", "top_specialty": None}

        total = len(outcomes)
        avg_score = sum(float(o.get("overall_score", 0)) for o in outcomes) / total

        # Trend: compare last 20 vs previous 20
        recent = outcomes[-20:] if len(outcomes) >= 20 else outcomes
        previous = outcomes[-40:-20] if len(outcomes) >= 40 else []
        if previous:
            recent_avg = sum(float(o.get("overall_score", 0)) for o in recent) / len(recent)
            prev_avg = sum(float(o.get("overall_score", 0)) for o in previous) / len(previous)
            diff = recent_avg - prev_avg
            trend = "improving" if diff > 2 else ("declining" if diff < -2 else "stable")
        else:
            trend = "stable"

        # Top specialty by avg score
        spec_scores: Dict[str, List[float]] = defaultdict(list)
        for o in outcomes:
            spec_scores[o.get("specialty", "general")].append(
                float(o.get("overall_score", 0))
            )
        top_specialty = max(
            spec_scores.items(), key=lambda kv: sum(kv[1]) / len(kv[1])
        )[0] if spec_scores else None

        return {
            "total_evaluations": total,
            "avg_overall_score": round(avg_score, 1),
            "trend": trend,
            "top_specialty": top_specialty,
        }

    # ------------------------------------------------------------------
    # Specialty heatmap
    # ------------------------------------------------------------------

    def get_specialty_heatmap(self) -> List[Dict[str, Any]]:
        """Return avg scores per specialty × dimension for a heatmap."""
        outcomes = self_learning._load_outcomes()
        buckets: Dict[str, Dict[str, List[float]]] = defaultdict(
            lambda: {d: [] for d in DIMENSIONS}
        )
        for o in outcomes:
            spec = o.get("specialty", "general")
            scores = o.get("detailed_scores", {})
            overall = float(o.get("overall_score", 75.0))
            for dim in DIMENSIONS:
                buckets[spec][dim].append(float(scores.get(dim, overall)))

        rows = []
        for spec, dim_data in buckets.items():
            row: Dict[str, Any] = {"specialty": spec}
            for dim, vals in dim_data.items():
                row[dim] = round(sum(vals) / len(vals), 1) if vals else None
            rows.append(row)
        return rows

    # ------------------------------------------------------------------
    # Band progression
    # ------------------------------------------------------------------

    def get_band_progression(self) -> List[Dict[str, Any]]:
        """Return avg overall score per band, ordered band_2 → band_9."""
        outcomes = self_learning._load_outcomes()
        band_scores: Dict[str, List[float]] = defaultdict(list)
        for o in outcomes:
            band_scores[o.get("band", "band_5")].append(
                float(o.get("overall_score", 0))
            )

        band_order = [
            "band_2", "band_3", "band_4", "band_5", "band_6",
            "band_7", "band_8a", "band_8b", "band_8c", "band_8d", "band_9",
        ]
        rows = []
        for band in band_order:
            vals = band_scores.get(band, [])
            rows.append({
                "band": band,
                "avg_score": round(sum(vals) / len(vals), 1) if vals else None,
                "n": len(vals),
            })
        return rows

    # ------------------------------------------------------------------
    # Question quality flags
    # ------------------------------------------------------------------

    def get_question_quality_flags(
        self,
        too_hard_threshold: float = 40.0,
        too_easy_threshold: float = 95.0,
    ) -> List[Dict[str, Any]]:
        """Return questions flagged as too hard or too easy."""
        from core.continuous_learning import ContinuousLearning
        cl = ContinuousLearning()
        outcomes = self_learning._load_outcomes()
        return cl._flag_question_difficulty(outcomes)

    # ------------------------------------------------------------------
    # Weekly / monthly summaries
    # ------------------------------------------------------------------

    def get_weekly_summary(self) -> Dict[str, Any]:
        return self._time_window_summary(days=7, label="weekly")

    def get_monthly_summary(self) -> Dict[str, Any]:
        return self._time_window_summary(days=30, label="monthly")

    def _time_window_summary(self, days: int, label: str) -> Dict[str, Any]:
        outcomes = self_learning._load_outcomes()
        cutoff = datetime.utcnow() - timedelta(days=days)
        recent = []
        for o in outcomes:
            ts_str = o.get("ts", "")
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts >= cutoff:
                    recent.append(o)
            except Exception:
                pass  # outcomes without ts are excluded

        if not recent:
            return {"period": label, "total_evaluations": 0, "avg_score": None,
                    "top_specialty": None, "weakest_dimension": None}

        avg_score = sum(float(o.get("overall_score", 0)) for o in recent) / len(recent)

        spec_scores: Dict[str, List[float]] = defaultdict(list)
        dim_scores: Dict[str, List[float]] = defaultdict(list)
        for o in recent:
            spec_scores[o.get("specialty", "general")].append(
                float(o.get("overall_score", 0))
            )
            for dim in DIMENSIONS:
                score = o.get("detailed_scores", {}).get(dim)
                if score is not None:
                    dim_scores[dim].append(float(score))

        top_specialty = max(
            spec_scores.items(), key=lambda kv: sum(kv[1]) / len(kv[1])
        )[0] if spec_scores else None

        weakest_dim = min(
            ((d, sum(v) / len(v)) for d, v in dim_scores.items() if v),
            key=lambda x: x[1],
            default=(None, None),
        )[0]

        return {
            "period": label,
            "total_evaluations": len(recent),
            "avg_score": round(avg_score, 1),
            "top_specialty": top_specialty,
            "weakest_dimension": weakest_dim,
        }


learning_analytics = LearningAnalyticsService()
