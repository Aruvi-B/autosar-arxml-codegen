#!/usr/bin/env python3
"""
WDG Configurator (Tkinter) - following standardized GUI structure
Converted from original WDG script to match CAN configurator pattern.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# -------------------- Data Models --------------------
@dataclass
class WdgDemEventParameterRefsModel:
    WDG_E_DISABLE_REJECTED: bool = True
    WDG_E_MODE_FAILED: bool = True

@dataclass
class WdgGeneralModel:
    WdgDevErrorDetect: bool = True
    WdgDisableAllowed: bool = True
    WdgIndex: int = 0
    WdgInitialTimeout: int = 100
    WdgMaxTimeout: int = 1000
    WdgRunArea: str = "RAM"  # Dropdown: RAM, ROM
    WdgTriggerLocation: str = ""
    WdgVersionInfoApi: bool = True

@dataclass
class WdgSettingsFastModel:
    WdgSettingsFast: bool = True

@dataclass
class WdgSettingsSlowModel:
    WdgSettingsSlow: bool = True

@dataclass
class WdgSettingsOffModel:
    WdgSettingsOff: bool = True

@dataclass
class WdgSettingsConfigModel:
    WdgDefaultMode: str = "WDGIF_FAST_MODE"  # Dropdown: WDGIF_FAST_MODE, WDGIF_OFF_MODE, WDGIF_SLOW_MODE
    WdgExternalConfiguration: bool = False
    WdgSettingsFast: bool = True
    WdgSettingsOff: bool = True
    WdgSettingsSlow: bool = True

@dataclass
class WdgExternalConfigurationModel:
    WdgExternalContainerRef: bool = True

@dataclass
class WdgPublishedInformationModel:
    WdgTriggerMode: str = "DG_BOTH"  # Dropdown: DG_BOTH, WDG_TOGGLE, WDG_WINDOW

@dataclass
class WdgAppModel:
    output_filepath: str = os.path.abspath(os.path.join("output", "wdg_config.arxml"))
    WdgConfigSet: bool = True
    WdgDemEventParameterRefs: WdgDemEventParameterRefsModel = field(default_factory=WdgDemEventParameterRefsModel)
    WdgGeneral: WdgGeneralModel = field(default_factory=WdgGeneralModel)
    WdgSettingsConfig: WdgSettingsConfigModel = field(default_factory=WdgSettingsConfigModel)
    WdgExternalConfiguration: WdgExternalConfigurationModel = field(default_factory=WdgExternalConfigurationModel)
    WdgPublishedInformation: WdgPublishedInformationModel = field(default_factory=WdgPublishedInformationModel)

# -------------------- ARXML Exporter --------------------
class WdgArxmlExporter:
    @staticmethod
    def export(model: WdgAppModel, filepath: str):
        AUTOSAR = ET.Element("AUTOSAR")
        ar_packages = ET.SubElement(AUTOSAR, "AR-PACKAGES")
        ar_package = ET.SubElement(ar_packages, "AR-PACKAGE")
        ET.SubElement(ar_package, "SHORT-NAME").text = "WdgPackage"
        elements = ET.SubElement(ar_package, "ELEMENTS")

        def container_from_obj(short_name: str, obj):
            cont = ET.SubElement(elements, "ECUC-CONTAINER-VALUE")
            ET.SubElement(cont, "SHORT-NAME").text = short_name
            ET.SubElement(cont, "DEFINITION-REF", {"DEST": "ECUC-PARAM-CONF-CONTAINER-DEF"}).text = f"/AUTOSAR/EcucDefs/Wdg/{short_name}"
            pvals = ET.SubElement(cont, "PARAMETER-VALUES")
            for key, val in obj.__dict__.items():
                if isinstance(val, bool):
                    p = ET.SubElement(pvals, "ECUC-BOOLEAN-PARAM-VALUE")
                elif isinstance(val, int):
                    p = ET.SubElement(pvals, "ECUC-NUMERICAL-PARAM-VALUE")
                else:
                    p = ET.SubElement(pvals, "ECUC-TEXTUAL-PARAM-VALUE")
                ET.SubElement(p, "SHORT-NAME").text = key
                ET.SubElement(p, "VALUE").text = str(val)

        # Config set (boolean container)
        cs = ET.SubElement(elements, "ECUC-CONTAINER-VALUE")
        ET.SubElement(cs, "SHORT-NAME").text = "WdgConfigSet"
        ET.SubElement(cs, "DEFINITION-REF", {"DEST":"ECUC-PARAM-CONF-CONTAINER-DEF"}).text = "/AUTOSAR/EcucDefs/Wdg/WdgConfigSet"
        p = ET.SubElement(cs, "PARAMETER-VALUES")
        pv = ET.SubElement(p, "ECUC-BOOLEAN-PARAM-VALUE")
        ET.SubElement(pv, "SHORT-NAME").text = "WdgConfigSetIncluded"
        ET.SubElement(pv, "VALUE").text = "true" if model.WdgConfigSet else "false"

        # Add other containers
        container_from_obj("WdgDemEventParameterRefs", model.WdgDemEventParameterRefs)
        container_from_obj("WdgGeneral", model.WdgGeneral)
        container_from_obj("WdgSettingsConfig", model.WdgSettingsConfig)
        container_from_obj("WdgExternalConfiguration", model.WdgExternalConfiguration)
        container_from_obj("WdgPublishedInformation", model.WdgPublishedInformation)

        WdgArxmlExporter._indent(AUTOSAR)
        tree = ET.ElementTree(AUTOSAR)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                WdgArxmlExporter._indent(e, level + 1)
            if not e.tail or not e.tail.strip():
                e.tail = i
        elif level and (not elem.tail or not elem.tail.strip()):
            elem.tail = i

# -------------------- GUI Widgets --------------------
class CollapsibleFrame(ttk.Frame):
    def __init__(self, master, text="", *args, **kwargs):
        super().__init__(master, *args, **kwargs)
        self.show = tk.BooleanVar(value=True)
        header = ttk.Frame(self)
        header.pack(fill="x", expand=False)
        self.toggle_btn = ttk.Checkbutton(header, text=text, variable=self.show, 
                                        style="Toolbutton", command=self._toggle)
        self.toggle_btn.pack(side="left", anchor="w")
        self.content = ttk.Frame(self)
        self.content.pack(fill="x", expand=True, padx=6, pady=4)

    def _toggle(self):
        if self.show.get():
            self.content.pack(fill="x", expand=True, padx=6, pady=4)
        else:
            self.content.forget()

# -------------------- Main App --------------------
class WdgConfiguratorApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = WdgAppModel()
        self.var_output_filepath = tk.StringVar(value=self.model.output_filepath)
        self._build_ui()

    def _build_ui(self):
        # Top frame for filename/outfolder
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x", side="top")

        ttk.Label(top, text="Output File Path").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.var_output_filepath, width=60).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top, text="Browse...", command=self._browse_output_file).grid(row=0, column=2, sticky="w")
        top.columnconfigure(1, weight=1)

        # Main frame with canvas for scrollable content
        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=8, pady=8)

        canvas = tk.Canvas(main)
        canvas.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        vsb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=vsb.set)
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        self.content = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=self.content, anchor="nw")

        # Ensure canvas resizes with window
        self.content_id = canvas.create_window((0,0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(self.content_id, width=e.width))

        # Build sections
        self._build_section_WdgConfigSet(self.content)
        self._build_section("WdgDemEventParameterRefs", self.model.WdgDemEventParameterRefs)
        self._build_section("WdgGeneral", self.model.WdgGeneral)
        self._build_section("WdgSettingsConfig", self.model.WdgSettingsConfig)
        self._build_section("WdgExternalConfiguration", self.model.WdgExternalConfiguration)
        self._build_section("WdgPublishedInformation", self.model.WdgPublishedInformation)

        # Bottom generate button
        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill="x", pady=(0,10))
        ttk.Button(btn_frm, text="🚀 Generate WDG ARXML", command=self.on_generate).pack(side="left", padx=8, pady=6)

    def _build_section_WdgConfigSet(self, parent):
        sec = CollapsibleFrame(parent, text="📦 WdgConfigSet")
        sec.pack(fill="x", pady=4)
        self.var_WdgConfigSet = tk.BooleanVar(value=self.model.WdgConfigSet)
        ttk.Checkbutton(sec.content, text="Include WdgConfigSet", variable=self.var_WdgConfigSet).pack(anchor="w")

    def _build_section(self, name, obj):
        sec = CollapsibleFrame(self.content, text=f"📦 {name}")
        sec.pack(fill="x", pady=4)

        # Fields that should be dropdowns and their options
        dropdowns = {
            "WdgRunArea": ["RAM", "ROM"],
            "WdgDefaultMode": ["WDGIF_FAST_MODE", "WDGIF_OFF_MODE", "WDGIF_SLOW_MODE"],
            "WdgTriggerMode": ["DG_BOTH", "WDG_TOGGLE", "WDG_WINDOW"]
        }

        for key, val in obj.__dict__.items():
            widget_row = ttk.Frame(sec.content)
            widget_row.pack(fill="x", pady=2, padx=4)
            ttk.Label(widget_row, text=key, width=36, anchor="w").pack(side="left")

            var_name = f"var_{name}_{key}"
            if key in dropdowns:
                var = tk.StringVar(value=str(val))
                cb = ttk.Combobox(widget_row, textvariable=var, values=dropdowns[key], state="readonly")
                cb.pack(side="left", fill="x", expand=True)
            elif isinstance(val, bool):
                var = tk.BooleanVar(value=val)
                cb = ttk.Checkbutton(widget_row, variable=var)
                cb.pack(side="left")
            elif isinstance(val, int):
                var = tk.IntVar(value=val)
                entry = ttk.Entry(widget_row, textvariable=var)
                entry.pack(side="left", fill="x", expand=True)
            else:
                var = tk.StringVar(value=str(val))
                entry = ttk.Entry(widget_row, textvariable=var)
                entry.pack(side="left", fill="x", expand=True)

            setattr(self, var_name, var)

    def _browse_output_file(self):
        filepath = filedialog.asksaveasfilename(
            title="Save ARXML file",
            defaultextension=".arxml",
            filetypes=[("ARXML files", "*.arxml"), ("All files", "*.*")])
        if filepath:
            self.var_output_filepath.set(filepath)

    def on_generate(self):
        # Update model from widgets
        self.model.output_filepath = self.var_output_filepath.get()
        if not self.model.output_filepath:
            messagebox.showerror("Error", "Output file path cannot be empty.")
            return

        self.model.WdgConfigSet = bool(self.var_WdgConfigSet.get())

        sections = [
            "WdgDemEventParameterRefs",
            "WdgGeneral",
            "WdgSettingsConfig",
            "WdgExternalConfiguration",
            "WdgPublishedInformation",
        ]
        
        for sec in sections:
            obj = getattr(self.model, sec)
            for key in obj.__dict__.keys():
                var_name = f"var_{sec}_{key}"
                if not hasattr(self, var_name):
                    continue
                var = getattr(self, var_name)
                try:
                    # All tk.Variable support .get()
                    v = var.get()
                except Exception:
                    v = None
                # Cast types based on original model attribute type
                orig = getattr(obj, key)
                if isinstance(orig, bool):
                    setattr(obj, key, bool(v))
                elif isinstance(orig, int):
                    try:
                        setattr(obj, key, int(v))
                    except Exception:
                        setattr(obj, key, 0)
                else:
                    setattr(obj, key, str(v))

        outdir = os.path.dirname(self.model.output_filepath)
        os.makedirs(outdir, exist_ok=True)
        
        try:
            WdgArxmlExporter.export(self.model, self.model.output_filepath)
            messagebox.showinfo("Saved", f"WDG ARXML generated at:\n{self.model.output_filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate WDG ARXML:\n{e}")

# -------------------- Standalone App Runner --------------------
def create_standalone_app():
    """Create a standalone window for WDG configurator"""
    root = tk.Tk()
    root.title("AUTOSAR WDG Configurator")
    root.geometry("1100x720")
    
    app = WdgConfiguratorApp(root)
    app.pack(fill="both", expand=True)
    
    return root

if __name__ == "__main__":
    root = create_standalone_app()
    root.mainloop()
