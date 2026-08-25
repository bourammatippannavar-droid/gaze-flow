from dataclasses import dataclass, field
from typing import List, Tuple
import numpy as np

@dataclass
class Calibration:
    points: List[Tuple[float, float, float, float]] = field(default_factory=list)
    ready: bool = False
    def add(self, gaze_x: float, gaze_y: float, screen_x: float, screen_y: float) -> None:
        self.points.append((gaze_x, gaze_y, screen_x, screen_y))
        self.ready = len(self.points) >= 5
    def map(self, gaze_x: float, gaze_y: float) -> Tuple[float, float]:
        if not self.points:
            return gaze_x, gaze_y
        source = np.array([[p[0], p[1], 1] for p in self.points])
        target_x = np.array([p[2] for p in self.points])
        target_y = np.array([p[3] for p in self.points])
        coeff_x, *_ = np.linalg.lstsq(source, target_x, rcond=None)
        coeff_y, *_ = np.linalg.lstsq(source, target_y, rcond=None)
        mapped = np.array([gaze_x, gaze_y, 1])
        return float(np.clip(mapped @ coeff_x, 0, 1)), float(np.clip(mapped @ coeff_y, 0, 1))
