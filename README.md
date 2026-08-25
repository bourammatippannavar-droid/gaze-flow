# GazeFlow

GazeFlow is a hands-free desktop control tool using OpenCV and MediaPipe Tasks. It uses the index fingertip for calibrated cursor movement and hand gestures for actions: fist clicks, open palm is neutral, and thumb/index pinch starts and ends a drag. Gesture mappings, a virtual keyboard, local profiles, analytics, pause, and emergency stop are included.

## Setup

Windows PowerShell:

```powershell
cd .\gaze-flow
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m gazeflow
```

A webcam is required for tracking. The application starts paused; press `Space` to pause/resume and `Esc` for an emergency stop. Use the Calibration tab before enabling mouse control. Voice commands are optional and disabled by default.

## Project layout

- `gazeflow/tracking`: camera capture, hand landmarks, cursor coordinates, and gesture recognition
- `gazeflow/input`: safe mouse, scroll, click, keyboard, and voice controls
- `gazeflow/storage`: profiles, settings, and interaction analytics
- `gazeflow/ui`: Tk dashboard and calibration workflow
- `tests`: hardware-independent behavior tests

## Safety

PyAutoGUI failsafe is enabled. Gaze actions are disabled until calibration is complete and the dashboard is unpaused. Emergency stop immediately pauses actions and releases the camera.

The Hand Landmarker model is downloaded automatically to `models/hand_landmarker.task` on first run.
