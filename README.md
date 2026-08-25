# GazeFlow: Hands-Free Computer Control

GazeFlow is a Python desktop application for hands-free mouse and keyboard control through webcam-based hand tracking. It uses the MediaPipe Tasks API to follow the index fingertip, recognize hand poses, and translate them into safe computer actions.

## Features

- Real-time hand tracking with up to two hands
- Calibrated index-fingertip cursor movement
- Adjustable sensitivity and active camera region
- Fist left-click
- Open palm neutral state
- Thumb/index pinch drag with mouse-down and mouse-up lifecycle
- Configurable gesture-to-action mappings
- Scroll actions, virtual keyboard, and optional voice commands
- Guided gesture practice popup with hold timing and results
- Particle sphere visualizer controlled by hand position, pinch, and two-hand spread
- Local JSON profiles and CSV/JSONL interaction analytics
- Pause/resume and PyAutoGUI fail-safe emergency stop

## Setup

Windows PowerShell:

```powershell
cd .\gaze-flow
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m gazeflow
```

A webcam is required. The Hand Landmarker model downloads automatically to `models/hand_landmarker.task` on first run. `pygame-ce` provides the `pygame` API for the visualizer and gesture trainer on current Python versions.

## Using GazeFlow

1. Start the app. It opens paused for safety.
2. Click `START CALIBRATION`, place your index fingertip over each target, and click.
3. Click `RESUME` after calibration.
4. Move your index finger to control the cursor.
5. Make a fist to click, or pinch thumb and index finger to drag.
6. Open `PRACTICE GESTURES` for guided gesture training.

Press `Space` to pause or resume. Press `Esc` for emergency stop. Move the pointer to a screen corner to trigger PyAutoGUI's fail-safe.

## Project layout

- `gazeflow/tracking`: hand capture, landmark samples, calibration, cursor mapping, and gesture detection
- `gazeflow/input`: safe mouse, drag, scroll, keyboard, and voice controls
- `gazeflow/storage`: local profiles and interaction analytics
- `gazeflow/ui`: Tk dashboard, gesture trainer, particle visualizer, and calibration workflow
- `gazeflow/tests`: hardware-independent behavior tests

## Validation

```powershell
.\.venv\Scripts\python.exe -m pytest gazeflow\tests -q
.\.venv\Scripts\python.exe -m compileall -q gazeflow
```

## Safety

GazeFlow starts paused and requires calibration before cursor movement. Every PyAutoGUI action is protected by its fail-safe; an emergency stop pauses input and releases any active drag.
