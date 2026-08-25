import csv
import json
from datetime import datetime, timezone
from pathlib import Path
from gazeflow.config import DATA_DIR

class Analytics:
    def __init__(self, path: Path = DATA_DIR / "interactions.csv", jsonl_path: Path = DATA_DIR / "interactions.jsonl"):
        self.path = path
        self.jsonl_path = jsonl_path
        self.path.parent.mkdir(parents=True, exist_ok=True)
        self.jsonl_path.parent.mkdir(parents=True, exist_ok=True)
        if not self.path.exists():
            with self.path.open("w", newline="", encoding="utf-8") as f:
                csv.writer(f).writerow(["timestamp", "event"])
    def record(self, event: str, payload: dict | None = None) -> None:
        with self.path.open("a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([datetime.now(timezone.utc).isoformat(), event])
        with self.jsonl_path.open("a", encoding="utf-8") as f:
            f.write(json.dumps({"timestamp": datetime.now(timezone.utc).isoformat(), "event": event, "data": payload or {}}) + "\n")
    def summary(self) -> dict[str, int]:
        counts: dict[str, int] = {}
        if self.path.exists():
            with self.path.open(newline="", encoding="utf-8") as f:
                for row in csv.DictReader(f):
                    counts[row["event"]] = counts.get(row["event"], 0) + 1
        return counts
