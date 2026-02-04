import tkinter as tk
from tkinter import ttk

class StatusPanel:
    def __init__(self, parent):
        # Frame should expand fully inside the parent
        self.frame = ttk.Frame(parent)
        self.frame.pack(fill="x", expand=True, side="bottom")
        self.yaxis = 230  # default height
        #  Text log now fills entire width + auto expands
        self.text = tk.Text(
            self.frame,
            height=9,             # a bit more height
            bg="black",
            fg="yellow",
            wrap="none"           # no auto-wrap (scrollable)
        )
        self.text.insert("end", "Status log ready...\n")
        self.text.config(state="disabled")  # read-only mode

        #  Scrollbars
        y_scroll = ttk.Scrollbar(self.frame, orient="vertical", command=self.text.yview)
        x_scroll = ttk.Scrollbar(self.frame, orient="horizontal", command=self.text.xview)

        self.text.configure(
            yscrollcommand=y_scroll.set,
            xscrollcommand=x_scroll.set
        )

        #  Grid layout → allows expansion in both directions
        self.text.grid(row=0, column=0, sticky="nsew")
        y_scroll.grid(row=0, column=1, sticky="ns")
        x_scroll.grid(row=1, column=0, sticky="ew")

        # Tell grid to expand fully
        self.frame.grid_rowconfigure(0, weight=1)
        self.frame.grid_columnconfigure(0, weight=1)

    def log(self, message: str):
        """Append a new log line to the status log."""
        self.text.config(state="normal")  # enable edit temporarily
        self.text.insert("end", f"{message}\n")
        self.text.see("end")  # auto-scroll to latest log
        self.text.config(state="disabled")
