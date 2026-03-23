"""
Self-learning module: colectează rezultate, antrenează un model simplu, ajustează ponderi
per specialitate × band pe 5 dimensiuni.
"""

from typing import Dict, Any, List, Tuple
from pathlib import Path
import json
from datetime import datetime

DIMENSIONS = [
    "knowledge_depth",
    "clinical_reasoning",
    "safety_awareness",
    "communication",
    "leadership",
]

_DEFAULT_WEIGHT = 1.0


class SelfLearning:
    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.weights_file = self.storage_path / "weights.json"
        if not self.weights_file.exists():
            self._save_weights({})

    # ------------------------------------------------------------------
    # Internal helpers
    # ------------------------------------------------------------------

    def _save_weights(self, weights: Dict[str, Any]) -> None:
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(weights, f, indent=2)

    def _load_weights(self) -> Dict[str, Any]:
        with open(self.weights_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def _key(self, specialty: str, band: str) -> str:
        return f"{specialty}::{band}"

    def _default_dim_weights(self) -> Dict[str, float]:
        return {d: _DEFAULT_WEIGHT for d in DIMENSIONS}

    # ------------------------------------------------------------------
    # Public – backward-compatible API
    # ------------------------------------------------------------------

    def get_weights(self) -> Dict[str, float]:
        """Return flat global weights (backward-compatible)."""
        weights = self._load_weights()
        flat: Dict[str, float] = {}
        for dim in DIMENSIONS:
            values = [
                slot.get(dim, _DEFAULT_WEIGHT)
                for slot in weights.values()
                if isinstance(slot, dict)
            ]
            flat[f"{dim}_weight"] = (sum(values) / len(values)) if values else _DEFAULT_WEIGHT
        if not flat:
            flat = {f"{d}_weight": _DEFAULT_WEIGHT for d in DIMENSIONS}
        return flat

    def record_outcome(self, outcome: Dict[str, Any]) -> None:
        """Record a single evaluation outcome to outcomes.jsonl."""
        log_file = self.storage_path / "outcomes.jsonl"
        entry = {
            "ts": datetime.utcnow().isoformat(),
            **outcome,
        }
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(entry) + "\n")

    def retrain(self) -> Dict[str, float]:
        """Re-compute per-specialty×band weights from outcomes and return global flat weights."""
        log_file = self.storage_path / "outcomes.jsonl"
        if not log_file.exists():
            return self.get_weights()

        # Aggregate per (specialty, band) × dimension
        buckets: Dict[str, Dict[str, List[float]]] = {}
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                except Exception:
                    continue
                key = self._key(
                    obj.get("specialty", "general"),
                    obj.get("band", "band_5"),
                )
                if key not in buckets:
                    buckets[key] = {d: [] for d in DIMENSIONS}
                scores = obj.get("detailed_scores", {})
                overall = float(obj.get("overall_score", 75.0))
                for dim in DIMENSIONS:
                    score = scores.get(dim, overall)
                    buckets[key][dim].append(float(score))

        # Compute new weights per slot
        weights = self._load_weights()
        for key, dim_scores in buckets.items():
            slot = weights.get(key, self._default_dim_weights())
            for dim in DIMENSIONS:
                vals = dim_scores[dim]
                if not vals:
                    continue
                avg = sum(vals) / len(vals)
                # Adjust weight slightly toward areas needing improvement
                factor = 1.0 + (75.0 - avg) / 500.0
                slot[dim] = max(0.5, min(1.5, slot.get(dim, _DEFAULT_WEIGHT) * factor))
            weights[key] = slot
        self._save_weights(weights)
        return self.get_weights()

    # ------------------------------------------------------------------
    # Advanced analytics helpers
    # ------------------------------------------------------------------

    def _load_outcomes(self) -> List[Dict[str, Any]]:
        log_file = self.storage_path / "outcomes.jsonl"
        if not log_file.exists():
            return []
        outcomes = []
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    outcomes.append(json.loads(line))
                except Exception:
                    continue
        return outcomes

    def get_failure_patterns(self, threshold: float = 20.0) -> List[Dict[str, Any]]:
        """Return (specialty, band, dimension) combos with >threshold % failure rate."""
        outcomes = self._load_outcomes()
        if not outcomes:
            return []

        # Bucket scores per (specialty, band, dim)
        buckets: Dict[Tuple[str, str, str], List[float]] = {}
        for obj in outcomes:
            spec = obj.get("specialty", "general")
            band = obj.get("band", "band_5")
            scores = obj.get("detailed_scores", {})
            overall = float(obj.get("overall_score", 75.0))
            for dim in DIMENSIONS:
                score = float(scores.get(dim, overall))
                k = (spec, band, dim)
                buckets.setdefault(k, []).append(score)

        patterns = []
        for (spec, band, dim), vals in buckets.items():
            fail_rate = sum(1 for v in vals if v < 60) / len(vals) * 100
            if fail_rate > threshold:
                patterns.append({
                    "specialty": spec,
                    "band": band,
                    "dimension": dim,
                    "failure_rate_pct": round(fail_rate, 1),
                    "avg_score": round(sum(vals) / len(vals), 1),
                    "n": len(vals),
                })
        return sorted(patterns, key=lambda x: -x["failure_rate_pct"])

    def get_trends(self) -> List[Dict[str, Any]]:
        """Return improving/stable/declining trend per specialty+band."""
        outcomes = self._load_outcomes()
        if not outcomes:
            return []

        buckets: Dict[Tuple[str, str], List[float]] = {}
        for obj in outcomes:
            key = (obj.get("specialty", "general"), obj.get("band", "band_5"))
            buckets.setdefault(key, []).append(float(obj.get("overall_score", 75.0)))

        trends = []
        for (spec, band), scores in buckets.items():
            if len(scores) < 3:
                trend = "stable"
            else:
                mid = len(scores) // 2
                first_half_avg = sum(scores[:mid]) / mid
                second_half_avg = sum(scores[mid:]) / (len(scores) - mid)
                diff = second_half_avg - first_half_avg
                if diff > 3:
                    trend = "improving"
                elif diff < -3:
                    trend = "declining"
                else:
                    trend = "stable"
            trends.append({
                "specialty": spec,
                "band": band,
                "trend": trend,
                "avg_score": round(sum(scores) / len(scores), 1),
                "n": len(scores),
            })
        return trends

    def get_specialty_band_stats(self) -> List[Dict[str, Any]]:
        """Full aggregation per specialty × band."""
        outcomes = self._load_outcomes()
        if not outcomes:
            return []

        buckets: Dict[Tuple[str, str], Dict[str, List[float]]] = {}
        for obj in outcomes:
            key = (obj.get("specialty", "general"), obj.get("band", "band_5"))
            if key not in buckets:
                buckets[key] = {"overall": [], **{d: [] for d in DIMENSIONS}}
            buckets[key]["overall"].append(float(obj.get("overall_score", 75.0)))
            for dim in DIMENSIONS:
                score = obj.get("detailed_scores", {}).get(dim)
                if score is not None:
                    buckets[key][dim].append(float(score))

        stats = []
        for (spec, band), data in buckets.items():
            row: Dict[str, Any] = {"specialty": spec, "band": band}
            for field, vals in data.items():
                if vals:
                    row[f"avg_{field}"] = round(sum(vals) / len(vals), 1)
                    row[f"n_{field}"] = len(vals)
            stats.append(row)
        return stats


self_learning = SelfLearning()


