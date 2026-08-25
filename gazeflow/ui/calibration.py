import tkinter as tk
from gazeflow.tracking.calibration import Calibration

class CalibrationWindow:
    targets = [(0.1,0.1),(0.9,0.1),(0.5,0.5),(0.1,0.9),(0.9,0.9)]
    def __init__(self, parent, calibration: Calibration, sample_getter):
        self.calibration = calibration; self.sample_getter = sample_getter; self.index = 0
        self.window = tk.Toplevel(parent); self.window.title("GazeFlow Calibration"); self.window.geometry("700x500"); self.window.configure(bg="#10151b")
        self.canvas = tk.Canvas(self.window, bg="#10151b", highlightthickness=0); self.canvas.pack(fill="both", expand=True)
        self.window.bind("<Button-1>", self.capture); self.draw()
    def draw(self):
        self.canvas.delete("all"); w, h = self.window.winfo_width(), self.window.winfo_height(); x, y = self.targets[self.index]
        self.canvas.create_oval(w*x-16,h*y-16,w*x+16,h*y+16, fill="#48d597", outline="")
        self.canvas.create_text(w/2, 40, text=f"Look at the target, then click  ({self.index+1}/5)", fill="#f4f7f9", font=("Segoe UI", 16))
    def capture(self, _event=None):
        sample = self.sample_getter()
        if sample:
            x, y = self.targets[self.index]; self.calibration.add(sample.index_x, sample.index_y, x, y)
        self.index += 1
        if self.index >= len(self.targets): self.window.destroy()
        else: self.draw()
