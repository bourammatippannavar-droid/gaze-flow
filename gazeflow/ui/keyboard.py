import tkinter as tk

class VirtualKeyboard(tk.Frame):
    def __init__(self, parent, type_text):
        super().__init__(parent, bg="#17212b"); self.type_text = type_text
        rows = ["QWERTYUIOP", "ASDFGHJKL", "ZXCVBNM"]
        for row in rows:
            line = tk.Frame(self, bg="#17212b"); line.pack(pady=2)
            for key in row: tk.Button(line, text=key, width=4, command=lambda k=key: type_text(k.lower()), bg="#243542", fg="#e9f1f4", relief="flat").pack(side="left", padx=2)
        tk.Button(self, text="SPACE", width=18, command=lambda: type_text(" "), bg="#48d597", relief="flat").pack(pady=4)
