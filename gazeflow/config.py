from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict

ROOT = Path(__file__).resolve().parent.parent
DATA_DIR = ROOT / "data"

@dataclass
class Settings:
    sensitivity: float = 1.0
    active_margin: float = 0.15
    dwell_seconds: float = 1.2
    hand_click_enabled: bool = True
    gaze_mouse_enabled: bool = True
    scroll_enabled: bool = True
    voice_enabled: bool = False
    camera_index: int = 0
    gesture_actions: Dict[str, str] = field(default_factory=lambda: {
        "fist": "left_click", "open_palm": "none", "pinch_start": "drag_start",
        "pinch_end": "drag_end",
    })
