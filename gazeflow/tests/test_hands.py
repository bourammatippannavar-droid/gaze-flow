from types import SimpleNamespace
from gazeflow.tracking.hand_gesture_detector import HandGestureDetector
from gazeflow.tracking.hand_tracker import HandSample

def landmarks(thumb_y=0.3, extended=()):
    points = [SimpleNamespace(x=0.5, y=0.5) for _ in range(21)]
    for tip, pip in ((8, 6), (12, 10), (16, 14), (20, 18)):
        points[tip].y = 0.2 if tip in extended else 0.55
        points[pip].y = 0.4 if tip in extended else 0.6
    points[2].x = 0.5; points[3].x = 0.5; points[4].x = 0.2 if extended else 0.49; points[4].y = thumb_y
    return points

def test_hand_pose_names():
    detector = HandGestureDetector()
    assert detector._classify(landmarks(extended=(8, 12, 16, 20))) == "open_palm"
    assert detector._classify(landmarks()) == "fist"

def test_pinch_emits_start_and_end():
    detector = HandGestureDetector()
    sample = HandSample(True, landmarks=landmarks())
    sample.landmarks[4].x = sample.landmarks[8].x
    sample.landmarks[4].y = sample.landmarks[8].y
    assert [event.name for event in detector.update(sample, 0.0)] == ["pinch_start"]
    sample.present = False
    assert [event.name for event in detector.update(sample, 0.3)] == ["pinch_end"]
