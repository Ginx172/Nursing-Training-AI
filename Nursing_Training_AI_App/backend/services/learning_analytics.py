"""
Learning Analytics Service — dashboard data, heatmaps, progression, question quality.
"""

from __future__ import annotations

import statistics
from datetime import datetime, timezone, timedelta
from typing import Any, Dict, List, Optional

from core.self_learning import SelfLearning, FAILURE_THRESHOLD


class LearningAnalyticsService:
    """Provides analytics data for the learning insights dashboard."""

    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.self_learning = SelfLearning(storage_dir=storage_dir)

    # ------------------------------------------------------------------
    # Dashboard
    # ------------------------------------------------------------------

    def get_dashboard(self) -> Dict[str, Any]:
        """Overall platform analytics dashboard."""
        outcomes = self.self_learning._load_outcomes()
        if not outcomes:
            return {
                "total_sessions": 0,
                "avg_score": None,
                "pass_rate": None,
                "active_specialties": [],
                "active_bands": [],
                "trend_direction": "no_data",
            }

        scores = [float(o.get("overall_score", 0)) for o in outcomes]
        specialties = list({o.get("specialty", "unknown") for o in outcomes})
        bands = list({o.get("band", "unknown") for o in outcomes})

        # Simple trend: compare first half vs second half
        mid = len(scores) // 2
        first_half_avg = statistics.mean(scores[:mid]) if mid > 0 else None
        second_half_avg = statistics.mean(scores[mid:]) if scores[mid:] else None
        if first_half_avg is None or second_half_avg is None:
            trend = "insufficient_data"
        elif second_half_avg - first_half_avg > 2:
            trend = "improving"
        elif first_half_avg - second_half_avg > 2:
            trend = "declining"
        else:
            trend = "stable"

        return {
            "total_sessions": len(outcomes),
            "avg_score": round(statistics.mean(scores), 2),
            "min_score": round(min(scores), 2),
            "max_score": round(max(scores), 2),
            "pass_rate": round(
                sum(1 for s in scores if s >= FAILURE_THRESHOLD) / len(scores) * 100, 2
            ),
            "active_specialties": sorted(specialties),
            "active_bands": sorted(bands),
            "trend_direction": trend,
        }

    # ------------------------------------------------------------------
    # Heatmap
    # ------------------------------------------------------------------

    def get_specialty_heatmap(self) -> Dict[str, Any]:
        """Per-specialty average scores — suitable for heatmap rendering."""
        stats = self.self_learning.get_specialty_band_stats()
        heatmap: Dict[str, Dict[str, Any]] = {}
        for key, data in stats.items():
            sp = data["specialty"]
            bd = data["band"]
            heatmap.setdefault(sp, {})[bd] = {
                "avg_score": data["avg_score"],
                "pass_rate": data["pass_rate"],
                "total_sessions": data["total_sessions"],
            }
        return heatmap

    # ------------------------------------------------------------------
    # Per-specialty analytics
    # ------------------------------------------------------------------

    def get_specialty_analytics(self, specialty: str) -> Dict[str, Any]:
        """Detailed analytics for a single specialty."""
        stats = self.self_learning.get_specialty_band_stats(specialty=specialty)
        trends = self.self_learning.get_trends(specialty=specialty)
        failure_patterns = [
            p for p in self.self_learning.get_failure_patterns()
            if p["specialty"] == specialty.lower()
        ]
        return {
            "specialty": specialty,
            "band_breakdown": stats,
            "trends": trends,
            "failure_patterns": failure_patterns,
        }

    # ------------------------------------------------------------------
    # Per-band analytics
    # ------------------------------------------------------------------

    def get_band_analytics(self, band: str) -> Dict[str, Any]:
        """Detailed analytics for a single band."""
        stats = self.self_learning.get_specialty_band_stats(band=band)
        trends = self.self_learning.get_trends(band=band)
        failure_patterns = [
            p for p in self.self_learning.get_failure_patterns()
            if p["band"] == band.lower()
        ]
        return {
            "band": band,
            "specialty_breakdown": stats,
            "trends": trends,
            "failure_patterns": failure_patterns,
        }

    # ------------------------------------------------------------------
    # Question quality
    # ------------------------------------------------------------------

    def get_question_quality(self) -> List[Dict[str, Any]]:
        """Flag questions where everyone scores < 40 (too hard) or > 95 (too easy)."""
        outcomes = self.self_learning._load_outcomes()
        q_scores: Dict[str, List[float]] = {}
        for o in outcomes:
            qid = str(o.get("question_id", ""))
            if not qid:
                continue
            q_scores.setdefault(qid, []).append(float(o.get("overall_score", 0)))

        flagged: List[Dict[str, Any]] = []
        for qid, scores in q_scores.items():
            avg = statistics.mean(scores)
            if avg < 40:
                flag = "too_hard"
            elif avg > 95:
                flag = "too_easy"
            else:
                continue
            flagged.append({
                "question_id": qid,
                "avg_score": round(avg, 2),
                "sample_size": len(scores),
                "flag": flag,
            })
        flagged.sort(key=lambda x: x["avg_score"])
        return flagged

    # ------------------------------------------------------------------
    # Summaries
    # ------------------------------------------------------------------

    def _summary_for_period(self, days: int) -> Dict[str, Any]:
        """Build a summary for the last `days` days."""
        outcomes = self.self_learning._load_outcomes()
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        recent: List[Dict[str, Any]] = []
        for o in outcomes:
            ts_str = o.get("timestamp", "")
            try:
                ts = datetime.fromisoformat(ts_str)
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                if ts >= cutoff:
                    recent.append(o)
            except Exception:
                continue

        period_label = f"last_{days}_days"
        if not recent:
            return {"period": period_label, "sessions": 0, "avg_score": None}

        scores = [float(o.get("overall_score", 0)) for o in recent]
        return {
            "period": period_label,
            "sessions": len(recent),
            "avg_score": round(statistics.mean(scores), 2),
            "pass_rate": round(
                sum(1 for s in scores if s >= FAILURE_THRESHOLD) / len(scores) * 100, 2
            ),
            "specialties_active": list({o.get("specialty", "") for o in recent}),
        }

    def get_weekly_summary(self) -> Dict[str, Any]:
        """Generate a weekly summary of learning activity."""
        return self._summary_for_period(days=7)

    def get_monthly_summary(self) -> Dict[str, Any]:
        """Generate a monthly summary of learning activity."""
        return self._summary_for_period(days=30)


learning_analytics_service = LearningAnalyticsService()
