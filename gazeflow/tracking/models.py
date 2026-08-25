from dataclasses import dataclass
from enum import Enum
from typing import Optional, Tuple

class GazeDirection(str, Enum):
    CENTER = "center"
    LEFT = "left"
    RIGHT = "right"
    UP = "up"
    DOWN = "down"
    UNKNOWN = "unknown"

@dataclass
class GazeSample:
    x: float = 0.5
    y: float = 0.5
    direction: GazeDirection = GazeDirection.UNKNOWN
    left_open: float = 1.0
    right_open: float = 1.0
    confidence: float = 0.0
    face_box: Optional[Tuple[int, int, int, int]] = None
    fps: float = 0.0

@dataclass
class GestureEvent:
    name: str
    confidence: float = 1.0
