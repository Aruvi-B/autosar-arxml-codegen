import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import webbrowser
# Import ARXML parser + UI panels
from .editor_panel import EditorPanel
from .status_panel import StatusPanel

class MCALGeneratorApp:
    def __init__(self, root):
        self.root = root

        self.root.title("AUTOSAR - MCAL Generator")

        # Add pop for close the window
        self.root.protocol("WM_DELETE_WINDOW", self.root_quit)

        # === FULL SCREEN SAFE ===
        try:
            screen_w = root.winfo_screenwidth()
            screen_h = root.winfo_screenheight()
            self.root.geometry(f"{screen_w}x{screen_h}")
        except tk.TclError:
            self.root.state("zoomed")  

        # === MAIN LAYOUT ===
        self.main_frame = ttk.Frame(root)
        self.main_frame.pack(fill="both", expand=True)

        # Horizontal split → Tree + Right side
        self.h_paned = ttk.PanedWindow(self.main_frame, orient="horizontal")
        self.h_paned.pack(fill="both", expand=True)

        # # LEFT TREE PANEL
        # self.tree_panel = TreePanel(self.h_paned)
        # self.h_paned.add(self.tree_panel.frame, weight=1)

        # RIGHT vertical split → Editor + Logs
        self.v_paned = ttk.PanedWindow(self.h_paned, orient="vertical")
        self.h_paned.add(self.v_paned, weight=3)

        # Create Logs first
        self.status_panel = StatusPanel(self.v_paned)

        # Create EditorPanel with log reference
        self.editor_panel = EditorPanel(self.v_paned, self.status_panel)
        
        self.v_paned.add(self.editor_panel.frame, weight=3)
        self.v_paned.add(self.status_panel.frame, weight=1)

        # Now create menu bar safely
        self.create_menubar()
    
    def open_link(self, url):
        webbrowser.open_new(url)
    # -----------------------------
    # MENU BAR
    # -----------------------------
    def create_menubar(self):
        menubar = tk.Menu(self.root)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        
        # Documents submenu
        docs_menu = tk.Menu(file_menu, tearoff=0)
        docs_menu.add_command(
            label="ADC Driver Spec",
            command=lambda: self.open_link("https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_ADCDriver.pdf")
        )
        docs_menu.add_command(
            label="DIO Driver Spec",
            command=lambda: self.open_link("https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_DIODriver.pdf")  # Replace with actual link
        )
        docs_menu.add_command(
            label="GPT Driver Spec",
            command=lambda: self.open_link("https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_GPTDriver.pdf")  
        )
        docs_menu.add_command(
            label="WDG Driver Spec",
            command=lambda: self.open_link("https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_WatchdogDriver.pdf")  
        )
        docs_menu.add_command(
            label="CAN Driver Spec",
            command=lambda: self.open_link("https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_CANDriver.pdf")  
        )
        docs_menu.add_command(
            label="SPI Driver Spec",
            command=lambda: self.open_link("https://www.autosar.org/fileadmin/standards/R24-11/CP/AUTOSAR_CP_SWS_SPIHandlerDriver.pdf")  
        )


        file_menu.add_cascade(label="AUTOSAR Docs SWS R24-11", menu=docs_menu)
        file_menu.add_command(label='User Manual', command=lambda: self.open_link("https://github.com/Creamcollar/arxml-autosar-codegen/blob/main/User%20Manual/User%20Manual.pdf"))
        file_menu.add_separator()
        file_menu.add_command(label="Quit", command=self.root.quit)
        menubar.add_cascade(label="File", menu=file_menu)

        # Edit menu
        # edit_menu = tk.Menu(menubar, tearoff=0)
        # edit_menu.add_command(label="Undo")
        # edit_menu.add_command(label="Redo")
        # menubar.add_cascade(label="Edit", menu=edit_menu)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.open_popup)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # -----------------------------
    # POPUP ABOUT WINDOW
    # -----------------------------
    def open_popup(self):
        message = (
            "Welcome to CreamCollar! \n\n"
            "Developers:\n"
            " - Aruvi B\n"
            " - Auroshaa A\n\n"
            "License:\n"
            "This project is licensed under the GNU GPL v3 license.\n\n"
            "Thank you for using our application!"
        )
        messagebox.showinfo("About CreamCollar", message)


    # -----------------------------
    # UPLOAD ARXML FILE
    # -----------------------------
    def upload_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("ARXML files", "*.arxml")])
        if not file_path:
            return

        self.status_panel.log(f"Loading ARXML: {file_path}")
        
        # Load into EditorPanel (Raw XML + Structured View)
        self.editor_panel.load_arxml_file(file_path)

            # Extract file name only
        import os
        file_name = os.path.basename(file_path)

        # Log both path and file name
        self.status_panel.log(f"Loading ARXML: {file_path}")
        self.status_panel.log(f"File selected: {file_name}")

        # Load into EditorPanel (Raw XML + Structured View)
        self.editor_panel.load_arxml_file(file_path)

        # Populate Tree Panel
        # try:
        #     parsed_data = parse_arxml(file_path)
        #     self.tree_panel.populate_from_arxml(parsed_data)
        #     self.status_panel.log("Tree View populated\n---------------------------------------")
        # except Exception as e:
        #     self.status_panel.log(f"Tree parse failed: {e}")
        #     messagebox.showerror("Parse Error", str(e))

    # -----------------------------
    # Placeholder Save
    # -----------------------------
    

    def save_back_to_file(self):
        """Legacy compatibility: just call download_arxml"""
        self.download_arxml()
    def root_quit(self):
        if messagebox.askokcancel("Quit", "Do you want to exit?"):
            # adding pop up say exit the application
            self.status_panel.log("Exiting application...") 
            
            self.root.quit()
