import json
import os
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class AuditLogger:
    def __init__(self, base_dir: Optional[str] = None) -> None:
        self.base_dir = Path(base_dir or os.getenv("AUDIT_DIR", "logs/audit"))
        self.base_dir.mkdir(parents=True, exist_ok=True)

    def _current_file(self) -> Path:
        date_str = datetime.utcnow().strftime("%Y-%m-%d")
        return self.base_dir / f"audit_{date_str}.jsonl"

    def log(self, actor: str, action: str, resource: str, details: Dict[str, Any]) -> None:
        record = {
            "ts": datetime.utcnow().isoformat() + "Z",
            "actor": actor,
            "action": action,
            "resource": resource,
            "details": details,
        }
        out = self._current_file()
        with open(out, "a", encoding="utf-8") as f:
            f.write(json.dumps(record, ensure_ascii=False) + "\n")


audit = AuditLogger()


