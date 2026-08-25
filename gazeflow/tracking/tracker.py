import time
from typing import Optional
import cv2
import numpy as np
import mediapipe as mp
from gazeflow.config import ROOT
from .models import GazeDirection, GazeSample
from .hands import HandGestureDetector

LEFT_EYE = [33, 160, 158, 133, 153, 144]
RIGHT_EYE = [362, 385, 387, 263, 373, 380]
LEFT_IRIS = [468, 469, 470, 471]
RIGHT_IRIS = [473, 474, 475, 476]

class GazeTracker:
    def __init__(self, camera_index=0):
        self.capture = cv2.VideoCapture(camera_index)
        self.capture.set(cv2.CAP_PROP_FRAME_WIDTH, 960)
        self.capture.set(cv2.CAP_PROP_FRAME_HEIGHT, 540)
        base_options = mp.tasks.BaseOptions(model_asset_path=str(ROOT / "assets" / "face_landmarker.task"))
        options = mp.tasks.vision.FaceLandmarkerOptions(base_options=base_options, num_faces=1, output_face_blendshapes=False, output_facial_transformation_matrixes=False)
        self.mesh = mp.tasks.vision.FaceLandmarker.create_from_options(options)
        hand_options = mp.tasks.vision.HandLandmarkerOptions(base_options=mp.tasks.BaseOptions(model_asset_path=str(ROOT / "assets" / "hand_landmarker.task")), num_hands=1)
        self.hands = mp.tasks.vision.HandLandmarker.create_from_options(hand_options)
        self.hand_gestures = HandGestureDetector()
        self.last_time = time.monotonic()
        self.fps = 0.0
        self.last_frame = None

    @staticmethod
    def _point(landmarks, index, width, height):
        p = landmarks[index]
        return np.array([p.x * width, p.y * height], dtype=float)

    @classmethod
    def _eye_open(cls, landmarks, indices, width, height):
        p = [cls._point(landmarks, i, width, height) for i in indices]
        return float(np.linalg.norm(p[1] - p[5]) + np.linalg.norm(p[2] - p[4])) / max(2 * np.linalg.norm(p[0] - p[3]), 1e-6)


    def read(self) -> Optional[tuple[np.ndarray, GazeSample, list]]:
        ok, frame = self.capture.read()
        if not ok:
            return None
        frame = cv2.flip(frame, 1)
        height, width = frame.shape[:2]
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        result = self.mesh.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        hand_result = self.hands.detect(mp.Image(image_format=mp.ImageFormat.SRGB, data=rgb))
        now = time.monotonic()
        elapsed = now - self.last_time
        self.fps = 1 / elapsed if elapsed else self.fps
        self.last_time = now
        hand_events = []
        if hand_result.hand_landmarks:
            hand_landmarks = hand_result.hand_landmarks[0]
            hand_events = self.hand_gestures.update(hand_landmarks)
            for point in hand_landmarks:
                cv2.circle(frame, (int(point.x * width), int(point.y * height)), 3, (239, 201, 105), -1)
        if not result.face_landmarks:
            self.last_frame = frame
            return frame, GazeSample(fps=self.fps), hand_events
        landmarks = result.face_landmarks[0]
        left_open = self._eye_open(landmarks, LEFT_EYE, width, height)
        right_open = self._eye_open(landmarks, RIGHT_EYE, width, height)
        left_center = np.mean([self._point(landmarks, i, width, height) for i in LEFT_IRIS], axis=0)
        right_center = np.mean([self._point(landmarks, i, width, height) for i in RIGHT_IRIS], axis=0)
        eye_left = self._point(landmarks, 33, width, height); eye_right = self._point(landmarks, 133, width, height)
        eye_top = self._point(landmarks, 159, width, height); eye_bottom = self._point(landmarks, 145, width, height)
        eye_width = max(abs(eye_right[0] - eye_left[0]), 1)
        eye_height = max(abs(eye_bottom[1] - eye_top[1]), 1)
        x = float(np.clip((np.mean([left_center[0], right_center[0]]) - eye_left[0]) / eye_width, 0, 1))
        y = float(np.clip((np.mean([left_center[1], right_center[1]]) - eye_top[1]) / eye_height, 0, 1))
        if x < 0.36: direction = GazeDirection.LEFT
        elif x > 0.64: direction = GazeDirection.RIGHT
        elif y < 0.32: direction = GazeDirection.UP
        elif y > 0.68: direction = GazeDirection.DOWN
        else: direction = GazeDirection.CENTER
        confidence = float(np.clip(1 - abs(x - 0.5) * 0.25 - abs(y - 0.5) * 0.25, 0.5, 1.0))
        sample = GazeSample(x, y, direction, left_open, right_open, confidence, fps=self.fps)
        events = hand_events
        for point in landmarks:
            cv2.circle(frame, (int(point.x * width), int(point.y * height)), 1, (72, 213, 151), -1)
        self.last_frame = frame
        return frame, sample, events

    def close(self):
        self.capture.release()
        self.mesh.close()
        self.hands.close()
