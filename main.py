import os
import sys
import tkinter as tk
from ui.main_window import MCALGeneratorApp


def main():
    root = tk.Tk()
    MCALGeneratorApp(root)

    # Always resolve path from this file (not working directory)
    script_dir = os.path.dirname(os.path.abspath(__file__))
    icon_path = os.path.join(script_dir, "asserts", "creamcollar-favicon.ico")

    # Debug proof – remove later
    # print("Icon path:", icon_path)

    # Windows-safe icon handling
    if os.path.exists(icon_path):
        try:
            root.iconbitmap(icon_path)
        except tk.TclError as e:
            print("Failed to load icon:", e)
    

    # Maximize window (Windows + Linux safe)
    try:
        root.state("zoomed")      # Windows
    except tk.TclError:
        root.attributes("-zoomed", True)  # Linux

    root.mainloop()


if __name__ == "__main__":
    main()
