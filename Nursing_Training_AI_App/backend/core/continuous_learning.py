"""
Continuous Learning Engine — ML cycle that analyses outcomes.jsonl,
calibrates question difficulty, and produces dated JSON reports.
"""

from __future__ import annotations

import json
from collections import defaultdict
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Dict, List, Optional

DIMENSIONS = ["knowledge_depth", "clinical_reasoning", "safety_awareness", "communication", "leadership"]

WEAK_THRESHOLD = 60.0       # avg dim score below this → weak area
TOO_HARD_THRESHOLD = 40.0   # avg score below → question too hard
TOO_EASY_THRESHOLD = 95.0   # avg score above → question too easy


class ContinuousLearning:
    """
    Loads outcomes.jsonl, groups by specialty+band, identifies weak areas,
    calibrates question difficulty, updates weight slices and saves a dated report.
    """

    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.outcomes_file = self.storage_path / "outcomes.jsonl"
        self.weights_file = self.storage_path / "weights.json"
        self.reports_dir = self.storage_path / "reports"
        self.reports_dir.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------ #
    # Internal helpers                                                     #
    # ------------------------------------------------------------------ #

    def _load_outcomes(self) -> List[Dict[str, Any]]:
        outcomes: List[Dict[str, Any]] = []
        if not self.outcomes_file.exists():
            return outcomes
        with open(self.outcomes_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    outcomes.append(json.loads(line))
                except Exception:
                    continue
        return outcomes

    def _load_weights(self) -> Dict[str, Any]:
        if not self.weights_file.exists():
            return {"global": {dim: 1.0 for dim in DIMENSIONS}}
        with open(self.weights_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _save_weights(self, weights: Dict[str, Any]) -> None:
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2)

    def _slice_key(self, specialty: Optional[str], band: Optional[str]) -> str:
        s = (specialty or "general").lower().replace(" ", "_")
        b = (band or "band_5").lower().replace(" ", "_")
        return f"{s}__{b}"

    # ------------------------------------------------------------------ #
    # Analysis                                                             #
    # ------------------------------------------------------------------ #

    def identify_weak_areas(self, outcomes: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Return per-(specialty, band, dimension) combos with avg score < WEAK_THRESHOLD."""
        groups: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        for o in outcomes:
            key = self._slice_key(o.get("specialty"), o.get("band"))
            ds = o.get("detailed_scores", {})
            for dim in DIMENSIONS:
                if dim in ds:
                    groups[key][dim].append(float(ds[dim]))

        weak: List[Dict[str, Any]] = []
        for key, dim_scores in groups.items():
            specialty, band = (key.split("__") + ["unknown"])[:2]
            for dim, scores in dim_scores.items():
                avg = sum(scores) / len(scores) if scores else 0.0
                if avg < WEAK_THRESHOLD:
                    weak.append({
                        "specialty": specialty,
                        "band": band,
                        "dimension": dim,
                        "avg_score": round(avg, 2),
                        "sample_count": len(scores),
                    })
        return weak

    def calibrate_question_difficulty(self, outcomes: List[Dict[str, Any]]) -> Dict[str, List[int]]:
        """Flag question_ids as too_hard or too_easy based on avg overall_score."""
        q_scores: Dict[int, List[float]] = defaultdict(list)
        for o in outcomes:
            qid = o.get("question_id")
            if qid is not None:
                q_scores[int(qid)].append(float(o.get("overall_score", 0.0)))

        too_hard: List[int] = []
        too_easy: List[int] = []
        for qid, scores in q_scores.items():
            avg = sum(scores) / len(scores)
            if avg < TOO_HARD_THRESHOLD:
                too_hard.append(qid)
            elif avg > TOO_EASY_THRESHOLD:
                too_easy.append(qid)
        return {"too_hard": sorted(too_hard), "too_easy": sorted(too_easy)}

    def _calc_weight_factor(self, scores: List[float]) -> float:
        """Calculate a weight factor from a list of scores. Returns value in [0.5, 1.5]."""
        if not scores:
            return 1.0
        avg = sum(scores) / len(scores)
        factor = 1.0 + (75.0 - avg) / 250.0
        return round(max(0.5, min(1.5, factor)), 4)

    def update_weights(self, outcomes: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Recompute per-slice + global weights from outcomes and persist them."""
        weights = self._load_weights()
        groups: Dict[str, Dict[str, List[float]]] = defaultdict(lambda: defaultdict(list))
        global_dim_scores: Dict[str, List[float]] = defaultdict(list)

        for o in outcomes:
            key = self._slice_key(o.get("specialty"), o.get("band"))
            ds = o.get("detailed_scores", {})
            overall = float(o.get("overall_score", 75.0))
            for dim in DIMENSIONS:
                score = float(ds.get(dim, overall))
                groups[key][dim].append(score)
                global_dim_scores[dim].append(score)

        for key, dim_scores in groups.items():
            slice_w: Dict[str, float] = {}
            for dim in DIMENSIONS:
                slice_w[dim] = self._calc_weight_factor(dim_scores.get(dim, []))
            weights[key] = slice_w

        global_w: Dict[str, float] = {}
        for dim in DIMENSIONS:
            global_w[dim] = self._calc_weight_factor(global_dim_scores.get(dim, []))
        weights["global"] = global_w

        self._save_weights(weights)
        return weights

    # ------------------------------------------------------------------ #
    # Main cycle                                                           #
    # ------------------------------------------------------------------ #

    def run_cycle(self) -> Dict[str, Any]:
        """Run a full learning cycle and save a dated JSON report."""
        outcomes = self._load_outcomes()
        weak_areas = self.identify_weak_areas(outcomes)
        difficulty = self.calibrate_question_difficulty(outcomes)
        updated_weights = self.update_weights(outcomes)

        report: Dict[str, Any] = {
            "generated_at": datetime.now(timezone.utc).isoformat(),
            "total_outcomes_processed": len(outcomes),
            "weak_areas": weak_areas,
            "question_difficulty_calibration": difficulty,
            "weight_slices_updated": len(updated_weights) - 1,  # exclude "global"
            "global_weights": updated_weights.get("global", {}),
        }

        date_str = datetime.now(timezone.utc).strftime("%Y%m%d_%H%M%S")
        report_path = self.reports_dir / f"report_{date_str}.json"
        with open(report_path, "w", encoding="utf-8") as f:
            json.dump(report, f, indent=2)

        report["report_path"] = str(report_path)
        return report

    def latest_report(self) -> Optional[Dict[str, Any]]:
        """Return the most recent report, or None if no reports exist."""
        reports = sorted(self.reports_dir.glob("report_*.json"))
        if not reports:
            return None
        with open(reports[-1], "r", encoding="utf-8") as f:
            return json.load(f)


# Module-level singleton
continuous_learning = ContinuousLearning()
