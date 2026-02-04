import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import os

from ui.editor.autosar_driver import AutosarDriverPanel
from ui.editor.raw_xml import RawXmlPanel
# from ui.editor.structure_view import StructureViewPanel
from ui.build_edit.dio_build import ARXMLtoDIOConfigGUI
from ui.build_edit.adc_build import ARXMLtoADCGenerator
from ui.build_edit.can_build import ARXMLtoCANGenerator
from ui.build_edit.gpt_build import ARXMLtoGPTConfigGUI
from ui.build_edit.spi_build import ARXMLtoSPIGenerator
from ui.build_edit.wdg_build import ARXMLtoWDGGenerator


class EditorPanel:
    def __init__(self, parent, status_logger=None):
        self.frame = ttk.Frame(parent)
        self.notebook = ttk.Notebook(self.frame)
        self.notebook.pack(fill="both", expand=True)

        self.status_logger = status_logger
        self.xml_tree = None
        self.xml_file_path = None

        self.build_panels = {}
        self.current_build_panel = None

        self.setup_tabs()

        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

    def on_tab_changed(self, event):
        selected_tab_text = self.notebook.tab(self.notebook.select(), "text")
        v_paned = self.frame.master
        status_panel_frame = self.status_logger.frame

        is_visible = True
        try:
            v_paned.pane(status_panel_frame)
            is_visible = True
        except tk.TclError:
            is_visible = False

        if selected_tab_text in [" Peripheral Config Editor ", " Raw XML ", " Edit & Build "]:
            if is_visible:
                v_paned.remove(status_panel_frame)
        else:
            if not is_visible:
                v_paned.add(status_panel_frame)

    def setup_tabs(self):
        self.autosar_driver_panel = AutosarDriverPanel(self.notebook, self.status_logger)
        self.notebook.add(self.autosar_driver_panel.frame, text=" Peripheral Config Editor ")

        self.raw_xml_panel = RawXmlPanel(self.notebook, self.status_logger, self.on_raw_xml_change)
        self.notebook.add(self.raw_xml_panel.frame, text=" Raw XML ")

        self.setup_build_tab()

    def setup_build_tab(self):
        self.build_tab = ttk.Frame(self.notebook)
        self.notebook.add(self.build_tab, text=" Edit & Build ")

        # Top frame for dropdown
        top_frame = ttk.Frame(self.build_tab)
        top_frame.pack(fill="x", pady=5, padx=5)

        ttk.Label(top_frame, text="Select Driver:").pack(side="left", padx=(0, 5))
        self.driver_selector = ttk.Combobox(top_frame, values=["ADC", "DIO", "GPT", "WDG", "CAN", "SPI"], state="readonly")
        self.driver_selector.pack(side="left")
        self.driver_selector.bind("<<ComboboxSelected>>", self.on_driver_selected)

        # Container for the selected build panel
        self.build_panel_container = ttk.Frame(self.build_tab)
        self.build_panel_container.pack(fill="both", expand=True)

        # Initialize panels
        self.build_panels["ADC"] = ARXMLtoADCGenerator(self.build_panel_container)
        self.build_panels["DIO"] = ARXMLtoDIOConfigGUI(self.build_panel_container)
        self.build_panels["CAN"] = ARXMLtoCANGenerator(self.build_panel_container)
        self.build_panels["GPT"] = ARXMLtoGPTConfigGUI(self.build_panel_container)
        self.build_panels["SPI"] = ARXMLtoSPIGenerator(self.build_panel_container)
        self.build_panels["WDG"] = ARXMLtoWDGGenerator(self.build_panel_container)

        self.driver_selector.set("Select Peripheral")
        # self.show_build_panel("GPT")

    def on_driver_selected(self, event):
        selected_driver = self.driver_selector.get()
        self.show_build_panel(selected_driver)

    def show_build_panel(self, driver_name):
        if self.current_build_panel:
            self.current_build_panel.pack_forget()
        
        self.current_build_panel = self.build_panels.get(driver_name)
        
        if self.current_build_panel:
            self.current_build_panel.pack(fill="both", expand=True)

    def on_raw_xml_change(self, xml_tree):
        self.xml_tree = xml_tree

    def on_structure_view_change(self, xml_tree):
        self.xml_tree = xml_tree
        ET.register_namespace('', "http://autosar.org/schema/r4.0")
        xml_str = ET.tostring(self.xml_tree.getroot(), encoding="unicode", xml_declaration=True)
        formatted_xml = self.raw_xml_panel.format_xml_string(xml_str)
        self.raw_xml_panel.set_content(formatted_xml)

    def load_arxml_file(self, file_path):
        self.xml_file_path = file_path
        
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                content = f.read()
            
            self.raw_xml_panel.set_content(content)
            
            if self.status_logger: 
                self.status_logger.log(f"Loaded ARXML: {os.path.basename(file_path)}")

        except Exception as e:
            messagebox.showerror("Error", f"Cannot load ARXML: {e}")
            if self.status_logger: 
                self.status_logger.log(f"Failed to load ARXML: {e}")
            return

        try:
            self.xml_tree = ET.parse(file_path)
            self.raw_xml_panel.xml_tree = self.xml_tree
            
            if self.status_logger: 
                self.status_logger.log(f"Parsed XML elements")
                self.status_logger.log("Structured view populated")

        except ET.ParseError as e:
            messagebox.showerror("XML Parse Error", f"Invalid XML format: {e}")
            if self.status_logger: 
                self.status_logger.log(f"XML Parse Error: {e}")
        except Exception as e:
            messagebox.showerror("Parse Error", f"Unexpected error: {e}")
            if self.status_logger: 
                self.status_logger.log(f"Parse Error: {e}")
