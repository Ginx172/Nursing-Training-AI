"""
Self-learning module: colectează rezultate, antrenează un model simplu (stub), ajustează ponderi.
"""

from typing import Dict, Any, List
from pathlib import Path
import json


class SelfLearning:
    def __init__(self, storage_dir: str = "models/self_learning") -> None:
        self.storage_path = Path(storage_dir)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        self.weights_file = self.storage_path / "weights.json"
        if not self.weights_file.exists():
            self._save_weights({
                "knowledge_depth_weight": 1.0,
                "clinical_reasoning_weight": 1.0,
                "safety_awareness_weight": 1.0,
                "communication_weight": 1.0,
                "leadership_weight": 1.0
            })

    def _save_weights(self, weights: Dict[str, float]) -> None:
        with open(self.weights_file, "w", encoding="utf-8") as f:
            json.dump(weights, f)

    def get_weights(self) -> Dict[str, float]:
        with open(self.weights_file, "r", encoding="utf-8") as f:
            return json.load(f)

    def record_outcome(self, outcome: Dict[str, Any]) -> None:
        # outcome: {"band": str, "specialty": str, "overall_score": float, "user_feedback_score": float}
        log_file = self.storage_path / "outcomes.jsonl"
        with open(log_file, "a", encoding="utf-8") as f:
            f.write(json.dumps(outcome) + "\n")

    def retrain(self) -> Dict[str, float]:
        # Stub: ajustează ușor ponderile pe baza mediei scorurilor
        log_file = self.storage_path / "outcomes.jsonl"
        if not log_file.exists():
            return self.get_weights()
        total = 0.0
        n = 0
        with open(log_file, "r", encoding="utf-8") as f:
            for line in f:
                try:
                    obj = json.loads(line)
                    total += float(obj.get("overall_score", 0))
                    n += 1
                except Exception:
                    continue
        if n == 0:
            return self.get_weights()
        avg = total / n
        weights = self.get_weights()
        factor = 1.0 + (avg - 75.0) / 500.0  # mică ajustare în jurul baseline-ului
        for k in list(weights.keys()):
            weights[k] = max(0.5, min(1.5, weights[k] * factor))
        self._save_weights(weights)
        return weights


self_learning = SelfLearning()


