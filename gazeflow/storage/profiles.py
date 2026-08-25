import json
from dataclasses import asdict
from pathlib import Path
from typing import Any, Dict
from gazeflow.config import DATA_DIR, Settings

class ProfileStore:
    def __init__(self, path: Path = DATA_DIR / "profiles.json"):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)
    def load(self, name: str = "default") -> Settings:
        if not self.path.exists():
            return Settings()
        data = json.loads(self.path.read_text(encoding="utf-8"))
        saved = data.get(name, {})
        if "blink_click_enabled" in saved:
            saved["hand_click_enabled"] = saved.pop("blink_click_enabled")
        settings = Settings(**saved)
        defaults = Settings().gesture_actions
        legacy = {"hand_fist": "fist", "hand_open_palm": "open_palm"}
        settings.gesture_actions = {legacy.get(key, key): value for key, value in settings.gesture_actions.items()}
        settings.gesture_actions = {key: settings.gesture_actions[key] for key in defaults if key in settings.gesture_actions}
        settings.gesture_actions = {**defaults, **settings.gesture_actions}
        settings.gesture_actions["open_palm"] = "none"
        return settings
    def save(self, settings: Settings, name: str = "default") -> None:
        data: Dict[str, Any] = {}
        if self.path.exists():
            data = json.loads(self.path.read_text(encoding="utf-8"))
        data[name] = asdict(settings)
        self.path.write_text(json.dumps(data, indent=2), encoding="utf-8")
