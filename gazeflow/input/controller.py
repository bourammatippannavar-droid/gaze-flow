import time
import pyautogui
from gazeflow.config import Settings
from gazeflow.tracking.calibration import Calibration
from gazeflow.tracking.cursor_mapping import map_fingertip

class ActionController:
    def __init__(self, settings: Settings, calibration: Calibration):
        self.settings = settings
        self.calibration = calibration
        self.paused = True
        self.emergency = False
        self.last_move = 0.0
        self.dwell_started = None
        self.dragging = False
        pyautogui.PAUSE = 0.03
        pyautogui.FAILSAFE = True
    def toggle_pause(self):
        if not self.emergency: self.paused = not self.paused
    def emergency_stop(self):
        if self.dragging:
            try: pyautogui.mouseUp()
            except pyautogui.FailSafeException: pass
            self.dragging = False
        self.paused = True; self.emergency = True
    def resume_after_stop(self):
        self.emergency = False; self.paused = True
    def move(self, x: float, y: float):
        if self.paused or self.emergency or not self.settings.gaze_mouse_enabled or not self.calibration.ready: return
        if time.monotonic() - self.last_move < 0.04: return
        x, y = map_fingertip(x, y, self.settings.active_margin, self.settings.sensitivity)
        sx, sy = pyautogui.size(); mx, my = self.calibration.map(x, y)
        try: pyautogui.moveTo(int(mx * sx), int(my * sy), duration=0.02)
        except pyautogui.FailSafeException: self.emergency_stop()
        self.last_move = time.monotonic()
    def action(self, name: str):
        if name == "pause":
            self.paused = True
            return
        if name == "drag_start":
            if not self.paused and not self.emergency and not self.dragging:
                try: pyautogui.mouseDown(); self.dragging = True
                except pyautogui.FailSafeException: self.emergency_stop()
            return
        if name == "drag_end":
            if self.dragging:
                try: pyautogui.mouseUp()
                except pyautogui.FailSafeException: self.emergency_stop()
                self.dragging = False
            return
        if name == "fist": name = "left_click"
        if self.paused or self.emergency: return
        try:
            if name == "left_click": pyautogui.click()
            elif name == "right_click": pyautogui.rightClick()
            elif name == "double_click": pyautogui.doubleClick(interval=0.1)
            elif name == "scroll_up" and self.settings.scroll_enabled: pyautogui.scroll(4)
            elif name == "scroll_down" and self.settings.scroll_enabled: pyautogui.scroll(-4)
        except pyautogui.FailSafeException: self.emergency_stop()
    def dwell_click(self, x: float, y: float):
        if self.paused or self.emergency or not self.settings.hand_click_enabled: return
        now = time.monotonic()
        if self.dwell_started is None: self.dwell_started = (now, x, y)
        started, start_x, start_y = self.dwell_started
        if abs(x - start_x) + abs(y - start_y) > 0.08: self.dwell_started = (now, x, y)
        elif now - started >= self.settings.dwell_seconds:
            try: pyautogui.click(); self.dwell_started = None
            except pyautogui.FailSafeException: self.emergency_stop()
    def reset_dwell(self):
        self.dwell_started = None
    def type_text(self, text: str):
        if not self.paused and not self.emergency:
            try: pyautogui.write(text)
            except pyautogui.FailSafeException: self.emergency_stop()
