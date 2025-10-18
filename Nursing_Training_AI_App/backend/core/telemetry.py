import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class TelemetryLogger:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = Path(base_dir or os.getenv("TELEMETRY_DIR", "logs/analytics"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _current_file(self) -> Path:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self.base_dir / f"{date_str}.jsonl"

    def log_event(self, event_type: str, payload: Dict[str, Any]) -> None:
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "event": event_type,
            "payload": payload,
        }
        line = json.dumps(record, ensure_ascii=False)
        out = self._current_file()
        out.parent.mkdir(parents=True, exist_ok=True)
        with open(out, "a", encoding="utf-8") as f:
            f.write(line + "\n")


telemetry = TelemetryLogger()


