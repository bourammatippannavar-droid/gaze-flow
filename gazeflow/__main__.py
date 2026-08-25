import tkinter as tk
from gazeflow.ui.dashboard import Dashboard

def main():
    root = tk.Tk(); app = Dashboard(root); root.protocol("WM_DELETE_WINDOW", app.close); root.mainloop()

if __name__ == "__main__":
    main()
