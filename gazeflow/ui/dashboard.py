import tkinter as tk
import threading
from tkinter import ttk, messagebox
from PIL import Image, ImageTk
import cv2
from gazeflow.config import Settings
from gazeflow.storage.analytics import Analytics
from gazeflow.storage.profiles import ProfileStore
from gazeflow.tracking.calibration import Calibration
from gazeflow.tracking.hand_tracker import HandTracker
from gazeflow.tracking.hand_gesture_detector import HandGestureDetector
from gazeflow.input.controller import ActionController
from .calibration import CalibrationWindow
from .keyboard import VirtualKeyboard
from .particle_visualizer import HandState, ParticleVisualizer
from .gesture_trainer import GestureTrainer

class Dashboard:
    def __init__(self, root):
        self.root = root; self.root.title("GazeFlow | Hands-Free Control"); self.root.geometry("1120x760"); self.root.configure(bg="#10151b")
        self.settings = ProfileStore().load(); self.store = ProfileStore(); self.analytics = Analytics(); self.calibration = Calibration(); self.tracker = HandTracker(self.settings.camera_index); self.gesture_detector = HandGestureDetector(); self.controller = ActionController(self.settings, self.calibration); self.hand_state = HandState(); self.visualizer = ParticleVisualizer(self.hand_state); self.current_sample = None; self.last_event = "ready"
        self._build(); self.root.bind("<space>", lambda _: self.toggle_pause()); self.root.bind("<Escape>", lambda _: self.stop()); self.update()
    def _build(self):
        style = ttk.Style(); style.theme_use("clam"); style.configure("TNotebook", background="#10151b", borderwidth=0); style.configure("TNotebook.Tab", background="#243542", foreground="#e9f1f4", padding=10); style.configure("TLabel", background="#10151b", foreground="#e9f1f4")
        header = tk.Frame(self.root, bg="#10151b"); header.pack(fill="x", padx=24, pady=18)
        tk.Label(header, text="GazeFlow", font=("Segoe UI", 24, "bold"), fg="#48d597", bg="#10151b").pack(side="left"); tk.Label(header, text="  HANDS-FREE COMPUTER CONTROL", font=("Segoe UI", 10), fg="#9aabb4", bg="#10151b").pack(side="left", pady=10)
        self.pause_button = tk.Button(header, text="RESUME", command=self.toggle_pause, bg="#48d597", fg="#10151b", relief="flat", padx=18, pady=8); self.pause_button.pack(side="right")
        tk.Button(header, text="PRACTICE GESTURES", command=self.open_trainer, bg="#2d829b", fg="white", relief="flat", padx=14, pady=8).pack(side="right", padx=8)
        tk.Button(header, text="EMERGENCY STOP", command=self.stop, bg="#ed6a5a", fg="white", relief="flat", padx=14, pady=8).pack(side="right", padx=8)
        main = tk.Frame(self.root, bg="#10151b"); main.pack(fill="both", expand=True, padx=24)
        self.video = tk.Label(main, bg="#17212b", width=760, height=430); self.video.pack(side="left", fill="both", expand=True)
        side = tk.Frame(main, bg="#17212b", width=290); side.pack(side="right", fill="y", padx=(18,0)); side.pack_propagate(False)
        self.status = tk.Label(side, text="PAUSED", font=("Segoe UI", 18, "bold"), fg="#ed6a5a", bg="#17212b"); self.status.pack(anchor="w", padx=20, pady=(22,12))
        self.readouts = {}
        for label in ("Cursor source", "Gesture", "Confidence", "FPS", "Calibration"):
            row = tk.Frame(side, bg="#17212b"); row.pack(fill="x", padx=20, pady=7); tk.Label(row, text=label, fg="#9aabb4", bg="#17212b").pack(side="left"); value = tk.Label(row, text="--", fg="#f4f7f9", bg="#17212b", font=("Segoe UI", 10, "bold")); value.pack(side="right"); self.readouts[label] = value
        tk.Button(side, text="START CALIBRATION", command=self.calibrate, bg="#2d829b", fg="white", relief="flat", padx=10, pady=8).pack(fill="x", padx=20, pady=22)
        tabs = ttk.Notebook(self.root); tabs.pack(fill="x", padx=24, pady=(18,22)); settings_tab = tk.Frame(tabs, bg="#17212b"); keyboard_tab = tk.Frame(tabs, bg="#17212b"); analytics_tab = tk.Frame(tabs, bg="#17212b"); tabs.add(settings_tab, text="Settings & gestures"); tabs.add(keyboard_tab, text="Virtual keyboard"); tabs.add(analytics_tab, text="Analytics")
        self._settings_tab(settings_tab); VirtualKeyboard(keyboard_tab, self.controller.type_text).pack(pady=12); self.analytics_label = tk.Label(analytics_tab, text="No interactions yet", fg="#e9f1f4", bg="#17212b", font=("Segoe UI", 11)); self.analytics_label.pack(anchor="w", padx=20, pady=15)
    def _settings_tab(self, parent):
        viewport = tk.Frame(parent, bg="#17212b", height=185)
        viewport.pack(fill="x", expand=True)
        viewport.pack_propagate(False)
        canvas = tk.Canvas(viewport, bg="#17212b", highlightthickness=0)
        scrollbar = ttk.Scrollbar(viewport, orient="vertical", command=canvas.yview)
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        inner = tk.Frame(canvas, bg="#17212b")
        window = canvas.create_window((0, 0), window=inner, anchor="nw")
        inner.bind("<Configure>", lambda _: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda event: canvas.itemconfigure(window, width=event.width))
        canvas.bind("<Enter>", lambda _: canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-event.delta / 120), "units")))
        canvas.bind("<Leave>", lambda _: canvas.unbind_all("<MouseWheel>"))
        tk.Label(inner, text="Gesture mappings", fg="#48d597", bg="#17212b", font=("Segoe UI", 11, "bold")).grid(row=0, column=0, columnspan=2, sticky="w", padx=18, pady=10)
        choices = ["none", "left_click", "right_click", "double_click", "scroll_up", "scroll_down", "pause", "fist", "open_palm", "pinch_start", "pinch_end", "drag_start", "drag_end"]
        for row, gesture in enumerate(self.settings.gesture_actions, 1):
            tk.Label(inner, text=gesture, fg="#e9f1f4", bg="#17212b").grid(row=row, column=0, sticky="w", padx=18, pady=3); var = tk.StringVar(value=self.settings.gesture_actions[gesture]); ttk.Combobox(inner, textvariable=var, values=choices, state="readonly", width=16).grid(row=row, column=1, padx=8, pady=3); var.trace_add("write", lambda *_args, g=gesture, v=var: self.settings.gesture_actions.__setitem__(g, v.get()))
        base = len(self.settings.gesture_actions) + 1
        tk.Label(inner, text="Sensitivity", fg="#e9f1f4", bg="#17212b").grid(row=base, column=0, sticky="w", padx=18, pady=(12, 3))
        sensitivity = tk.DoubleVar(value=self.settings.sensitivity)
        ttk.Scale(inner, from_=0.5, to=2.0, variable=sensitivity, command=lambda value: setattr(self.settings, "sensitivity", float(value))).grid(row=base, column=1, sticky="ew", padx=8, pady=(12, 3))
        tk.Label(inner, text="Active area", fg="#e9f1f4", bg="#17212b").grid(row=base + 1, column=0, sticky="w", padx=18, pady=3)
        margin = tk.DoubleVar(value=self.settings.active_margin)
        ttk.Scale(inner, from_=0.05, to=0.35, variable=margin, command=lambda value: setattr(self.settings, "active_margin", float(value))).grid(row=base + 1, column=1, sticky="ew", padx=8, pady=3)
        inner.columnconfigure(1, weight=1)
    def update(self):
        result = self.tracker.read()
        if result:
            frame, sample = result; self.current_sample = sample; self.hand_state.set_hands(sample.hands if sample.present and sample.hands else ([sample.landmarks] if sample.present and sample.landmarks else [])); self._show_frame(frame); self.readouts["Cursor source"].config(text="INDEX FINGER" if sample.present else "NO HAND"); self.readouts["Confidence"].config(text=f"{sample.confidence:.0%}"); self.readouts["FPS"].config(text=f"{sample.fps:.0f}"); self.readouts["Calibration"].config(text="READY" if self.calibration.ready else "NEEDED")
            events = self.gesture_detector.update(sample)
            if sample.present:
                self.controller.move(sample.index_x, sample.index_y)
            if not self.calibration.ready and not self.controller.paused:
                self.status.config(text="CALIBRATE FIRST", fg="#f3c969")
            elif not sample.present and not self.controller.paused:
                self.status.config(text="SHOW HAND", fg="#f3c969")
            for event in events: self.last_event = event.name; self.analytics.record(event.name); self.controller.action(self.settings.gesture_actions.get(event.name, "none"))
            if self.controller.paused and self.status.cget("text") == "ACTIVE": self.status.config(text="PAUSED", fg="#ed6a5a"); self.pause_button.config(text="RESUME")
            self.readouts["Gesture"].config(text=self.last_event.replace("_", " ").upper()); self.analytics_label.config(text="  ".join(f"{k}: {v}" for k,v in self.analytics.summary().items()) or "No interactions yet")
        self.root.after(15, self.update)
    def _show_frame(self, frame):
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB); image = Image.fromarray(rgb); image.thumbnail((760, 430)); self.photo = ImageTk.PhotoImage(image); self.video.config(image=self.photo)
    def toggle_pause(self):
        self.controller.toggle_pause(); paused = self.controller.paused; self.status.config(text="PAUSED" if paused else "ACTIVE", fg="#ed6a5a" if paused else "#48d597"); self.pause_button.config(text="RESUME" if paused else "PAUSE")
    def stop(self): self.controller.emergency_stop(); self.status.config(text="EMERGENCY STOP", fg="#ed6a5a"); self.pause_button.config(text="RESUME")
    def calibrate(self): CalibrationWindow(self.root, self.calibration, lambda: self.current_sample)
    def open_trainer(self):
        self.visualizer.stop()
        trainer = GestureTrainer(self.hand_state, on_complete=lambda results: self.analytics.record("training_complete", results))
        threading.Thread(target=trainer.run, daemon=True).start()
    def close(self): self.visualizer.stop(); self.store.save(self.settings); self.tracker.close(); self.root.destroy()
