from __future__ import annotations

import json
from dataclasses import asdict
from pathlib import Path

from .models import RoundRecord


class JsonlLogger:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        if self.path.exists():
            self.path.unlink()

    def log(self, record: RoundRecord) -> None:
        with self.path.open("a", encoding="utf-8") as f:
            f.write(json.dumps(asdict(record), ensure_ascii=False))
            f.write("\n")
