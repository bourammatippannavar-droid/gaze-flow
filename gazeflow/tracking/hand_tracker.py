import time
import urllib.request
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional

import cv2
import mediapipe as mp

from gazeflow.config import ROOT

MODEL_URL = "https://storage.googleapis.com/mediapipe-models/hand_landmarker/hand_landmarker/float16/1/hand_landmarker.task"
MODEL_PATH = ROOT / "models" / "hand_landmarker.task"

@dataclass
class HandSample:
    present: bool = False
    index_x: float = 0.5
    index_y: float = 0.5
    landmarks: list = field(default_factory=list)
    confidence: float = 0.0
    fps: float = 0.0
    hands: list = field(default_factory=list)

class HandTracker:
    def __init__(self, camera_index=0, model_path: Optional[Path] = None):
        self.capture = cv2.VideoCapture(camera_index)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        model_path = Path(model_path or MODEL_PATH)
        model_path.parent.mkdir(parents=True, exist_ok=True)
        if not model_path.exists():
            urllib.request.urlretrieve(MODEL_URL, model_path)
        options = mp.tasks.vision.HandLandmarkerOptions(
            base_options=mp.tasks.BaseOptions(model_asset_path=str(model_path)),
            num_hands=2,
            min_hand_detection_confidence=0.6,
            min_hand_presence_confidence=0.6,
            min_tracking_confidence=0.6,
        )
        self.landmarker = mp.tasks.vision.HandLandmarker.create_from_options(options)
        self.last_time = time.monotonic()
        self.fps = 0.0

    def read(self) -> Optional[tuple]:
        ok, frame = self.capture.read()
        if not ok:
            return None
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        image = mp.Image(image_format=mp.ImageFormat.SRGB, data=cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
        result = self.landmarker.detect(image)
        now = time.monotonic()
        elapsed = now - self.last_time
        self.fps = 1 / elapsed if elapsed else self.fps
        self.last_time = now
        if not result.hand_landmarks:
            return frame, HandSample(fps=self.fps)
        all_landmarks = [[(point.x, point.y, point.z) for point in hand] for hand in result.hand_landmarks]
        landmarks = result.hand_landmarks[0]
        index = landmarks[8]
        confidence = result.handedness[0][0].score if result.handedness else 0.0
        for point in landmarks:
            cv2.circle(frame, (int(point.x * width), int(point.y * height)), 3, (239, 201, 105), -1)
        return frame, HandSample(True, index.x, index.y, all_landmarks[0], confidence, self.fps, all_landmarks)

    def close(self):
        self.capture.release()
        self.landmarker.close()
