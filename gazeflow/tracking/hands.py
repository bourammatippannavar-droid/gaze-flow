import time
from typing import Optional
from .models import GestureEvent

class HandGestureDetector:
    """Classifies stable hand poses from MediaPipe hand landmarks."""
    def __init__(self, cooldown=0.45):
        self.cooldown = cooldown
        self.last_name = ""
        self.last_emit = 0.0

    @staticmethod
    def _extended(landmarks):
        # Landmark coordinates are normalized to the camera image.
        fingers = {
            "index": landmarks[8].y < landmarks[6].y,
            "middle": landmarks[12].y < landmarks[10].y,
            "ring": landmarks[16].y < landmarks[14].y,
            "pinky": landmarks[20].y < landmarks[18].y,
        }
        thumb_base_span = max(abs(landmarks[3].x - landmarks[2].x) * 1.15, 0.04)
        thumb = abs(landmarks[4].x - landmarks[2].x) > thumb_base_span
        return thumb, fingers

    def classify(self, landmarks) -> Optional[str]:
        thumb, fingers = self._extended(landmarks)
        count = sum(fingers.values())
        if count == 4 and thumb: return "hand_open_palm"
        if count == 0 and not thumb: return "hand_fist"
        if count == 2 and fingers["index"] and fingers["middle"] and not fingers["ring"] and not fingers["pinky"]: return "hand_victory"
        if count == 0 and thumb: return "hand_thumb_up" if landmarks[4].y < landmarks[3].y else "hand_thumb_down"
        return None

    def update(self, landmarks, now=None) -> list[GestureEvent]:
        now = time.monotonic() if now is None else now
        name = self.classify(landmarks)
        if not name:
            self.last_name = ""
            return []
        if name != self.last_name or now - self.last_emit >= self.cooldown:
            self.last_name = name
            self.last_emit = now
            return [GestureEvent(name)]
        return []
