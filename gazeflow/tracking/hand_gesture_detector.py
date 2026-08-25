import math
import time
from .models import GestureEvent

WRIST = 0
THUMB_TIP = 4
INDEX_MCP, INDEX_PIP, INDEX_TIP = 5, 6, 8
MIDDLE_MCP, MIDDLE_PIP, MIDDLE_TIP = 9, 10, 12
RING_MCP, RING_PIP, RING_TIP = 13, 14, 16
PINKY_MCP, PINKY_PIP, PINKY_TIP = 17, 18, 20
FINGER_TIPS_PIPS_MCPS = [(INDEX_TIP, INDEX_PIP, INDEX_MCP), (MIDDLE_TIP, MIDDLE_PIP, MIDDLE_MCP), (RING_TIP, RING_PIP, RING_MCP), (PINKY_TIP, PINKY_PIP, PINKY_MCP)]

def _dist(a, b):
    return math.hypot(a.x - b.x, a.y - b.y)

class HandGestureDetector:
    def __init__(self, pinch_threshold=0.055, curl_ratio=0.85, cooldown_seconds=0.25):
        self.pinch_threshold = pinch_threshold
        self.curl_ratio = curl_ratio
        self.cooldown_seconds = cooldown_seconds
        self._current_pose = "none"
        self._cooldown_until = 0.0

    def _classify(self, landmarks):
        if _dist(landmarks[THUMB_TIP], landmarks[INDEX_TIP]) < self.pinch_threshold:
            return "pinch"
        curled = 0
        for tip_i, pip_i, mcp_i in FINGER_TIPS_PIPS_MCPS:
            tip_to_mcp = _dist(landmarks[tip_i], landmarks[mcp_i])
            pip_to_mcp = _dist(landmarks[pip_i], landmarks[mcp_i])
            if pip_to_mcp > 1e-6 and tip_to_mcp / pip_to_mcp < self.curl_ratio:
                curled += 1
        if curled >= 3:
            return "fist"
        if curled == 0:
            return "open_palm"
        return "none"

    def update(self, sample, now=None):
        now = time.monotonic() if now is None else now
        if not sample.present or not sample.landmarks:
            event = [GestureEvent("pinch_end")] if self._current_pose == "pinch" else []
            self._current_pose = "none"
            return event
        pose = self._classify(sample.landmarks)
        event_name = None
        if pose != self._current_pose and pose != "none" and now >= self._cooldown_until:
            event_name = "pinch_start" if pose == "pinch" else "pinch_end" if self._current_pose == "pinch" else pose
            self._cooldown_until = now + self.cooldown_seconds
        if pose != "pinch" and self._current_pose == "pinch" and event_name is None:
            event_name = "pinch_end"
        self._current_pose = pose
        return [GestureEvent(event_name)] if event_name else []
