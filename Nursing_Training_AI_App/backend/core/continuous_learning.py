"""
Continuous learning cycle: loads outcomes.jsonl, flags weak areas and question difficulty,
updates weight slices, saves dated JSON reports.
"""

from __future__ import annotations

import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

from core.self_learning import DIMENSIONS, SelfLearning

_WEAK_AREA_THRESHOLD = 60.0   # avg dim score below this → weak area
_TOO_HARD_THRESHOLD = 40.0    # avg overall score below this → question too hard
_TOO_EASY_THRESHOLD = 95.0    # avg overall score above this → question too easy


class ContinuousLearning:
    """Orchestrates the full ML cycle for continuous improvement."""

    def __init__(
        self,
        storage_dir: str = "models/self_learning",
        reports_dir: str = "models/reports",
    ) -> None:
        self.sl = SelfLearning(storage_dir=storage_dir)
        self.reports_path = Path(reports_dir)
        self.reports_path.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # Core cycle
    # ------------------------------------------------------------------

    def run_cycle(self) -> Dict[str, Any]:
        """Execute a full learning cycle and return a summary report."""
        outcomes = self.sl._load_outcomes()

        weak_areas = self._flag_weak_areas(outcomes)
        question_flags = self._flag_question_difficulty(outcomes)
        new_weights = self.sl.retrain()

        report: Dict[str, Any] = {
            "timestamp": datetime.utcnow().isoformat(),
            "outcomes_processed": len(outcomes),
            "weak_areas": weak_areas,
            "question_flags": question_flags,
            "updated_weights": new_weights,
            "failure_patterns": self.sl.get_failure_patterns(),
            "trends": self.sl.get_trends(),
        }

        self._save_report(report)
        return report

    # ------------------------------------------------------------------
    # Flagging helpers
    # ------------------------------------------------------------------

    def _flag_weak_areas(self, outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Identify specialty×band×dimension combinations averaging below threshold."""
        buckets: Dict[str, Dict[str, List[float]]] = {}
        for obj in outcomes:
            key = f"{obj.get('specialty', 'general')}::{obj.get('band', 'band_5')}"
            if key not in buckets:
                buckets[key] = {d: [] for d in DIMENSIONS}
            scores = obj.get("detailed_scores", {})
            overall = float(obj.get("overall_score", 75.0))
            for dim in DIMENSIONS:
                buckets[key][dim].append(float(scores.get(dim, overall)))

        flags = []
        for key, dim_scores in buckets.items():
            specialty, band = key.split("::", 1)
            for dim, vals in dim_scores.items():
                if not vals:
                    continue
                avg = sum(vals) / len(vals)
                if avg < _WEAK_AREA_THRESHOLD:
                    flags.append({
                        "specialty": specialty,
                        "band": band,
                        "dimension": dim,
                        "avg_score": round(avg, 1),
                        "n": len(vals),
                        "flag": "weak_area",
                    })
        return flags

    def _flag_question_difficulty(self, outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Flag questions as too-hard (<40 avg) or too-easy (>95 avg)."""
        q_scores: Dict[Any, List[float]] = {}
        for obj in outcomes:
            qid = obj.get("question_id")
            if qid is None:
                continue
            q_scores.setdefault(qid, []).append(float(obj.get("overall_score", 75.0)))

        flags = []
        for qid, scores in q_scores.items():
            avg = sum(scores) / len(scores)
            if avg < _TOO_HARD_THRESHOLD:
                flags.append({"question_id": qid, "avg_score": round(avg, 1), "flag": "too_hard"})
            elif avg > _TOO_EASY_THRESHOLD:
                flags.append({"question_id": qid, "avg_score": round(avg, 1), "flag": "too_easy"})
        return flags

    # ------------------------------------------------------------------
    # Persistence
    # ------------------------------------------------------------------

    def _save_report(self, report: Dict[str, Any]) -> Path:
        date_str = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        report_file = self.reports_path / f"cycle_report_{date_str}.json"
        with open(report_file, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)
        return report_file

    def get_latest_report(self) -> Dict[str, Any] | None:
        """Return the most recent saved report, or None if none exist."""
        reports = sorted(self.reports_path.glob("cycle_report_*.json"), reverse=True)
        if not reports:
            return None
        with open(reports[0], "r", encoding="utf-8") as f:
            return json.load(f)


continuous_learning = ContinuousLearning()
