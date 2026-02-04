# adc_config.py

import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# -------------------- Data Models --------------------
@dataclass
class AdcGeneralModel:
    AdcDeInitApi: bool = False
    AdcDevErrorDetect: bool = False
    AdcEnableLimitCheck: bool = False
    AdcEnableQueuing: bool = False
    AdcEnableStartStopGroupApi: bool = False
    AdcGrpNotifCapability: bool = False
    AdcHwTriggerApi: bool = False
    AdcLowPowerStatesSupport: bool = False
    AdcPowerStateAsynchTransitionMode: bool = False
    AdcReadGroupApi: bool = False
    AdcVersionInfoApi: bool = False
    AdcPriorityImplementation: str = "ADC_PRIORITY_NONE"  # Dropdown: ADC_PRIORITY_HW, ADC_PRIORITY_HW_SW, ADC_PRIORITY_NONE
    AdcResultAlignment: str = "ADC_ALIGN_RIGHT"  # Dropdown: ADC_ALIGN_LEFT, ADC_ALIGN_RIGHT

@dataclass
class AdcConfigSetModel:
    AdcHwUnit: int = 0

@dataclass
class AdcPowerStateConfigModel:
    AdcPowerState: int = 0
    AdcPowerStateReadyCbkRef: str = ""

@dataclass
class AdcChannelModel:
    AdcChannelConvTime: int = 0
    AdcChannelHighLimit: int = 4095
    AdcChannelId: int = 0
    AdcChannelLimitCheck: bool = False
    AdcChannelLowLimit: int = 0
    AdcChannelRangeSelect: str = "ADC_RANGE_ALWAYS"  # Dropdown with 7 options
    AdcChannelRefVoltsrcHigh: bool = False
    AdcChannelRefVoltsrcLow: bool = False
    AdcChannelResolution: int = 10
    AdcChannelSampTime: int = 0

@dataclass
class AdcGroupModel:
    AdcGroupAccessMode: str = "ADC_ACCESS_MODE_SINGLE"  # Dropdown: ADC_ACCESS_MODE_SINGLE, ADC_ACCESS_MODE_STREAMING
    AdcGroupConversionMode: str = "ADC_CONV_MODE_ONESHOT"  # Dropdown: ADC_CONV_MODE_CONTINUOUS, ADC_CONV_MODE_ONESHOT
    AdcGroupId: int = 0
    AdcGroupPriority: int = 0
    AdcGroupReplacement: str = "ADC_GROUP_REPL_ABORT_RESTART"  # Dropdown: ADC_GROUP_REPL_ABORT_RESTART, ADC_GROUP_REPL_SUSPEND_RESUME
    AdcGroupTriggSrc: str = "ADC_TRIGG_SRC_SW"  # Dropdown: ADC_TRIGG_SRC_HW, ADC_TRIGG_SRC_SW
    AdcHwTrigSignal: str = "ADC_HW_TRIG_BOTH_EDGES"  # Dropdown: 3 trigger signal options
    AdcHwTrigTimer: int = 0
    AdcNotification: bool = False
    AdcStreamingBufferMode: str = "ADC_STREAM_BUFFER_CIRCULAR"  # Dropdown: ADC_STREAM_BUFFER_CIRCULAR, ADC_STREAM_BUFFER_LINEAR
    AdcStreamingNumSamples: int = 1
    AdcGroupDefinition: int = 0

@dataclass
class AdcPublishedInformationModel:
    AdcChannelValueSigned: bool = False
    AdcGroupFirstChannelFixed: bool = False
    AdcMaxChannelResolution: int = 0

@dataclass
class AdcHwUnitModel:
    AdcClockSource: bool = False  # Fixed: Should be boolean, not int
    AdcHwUnitId: int = 0
    AdcPrescale: int = 0

@dataclass
class AdcAppModel:
    output_filepath: str = os.path.abspath(os.path.join("output/ADC", "adc_config.arxml"))
    AdcConfigSet: AdcConfigSetModel = field(default_factory=AdcConfigSetModel)  # Fixed: Should be model, not bool
    AdcGeneral: AdcGeneralModel = field(default_factory=AdcGeneralModel)
    AdcPowerStateConfig: AdcPowerStateConfigModel = field(default_factory=AdcPowerStateConfigModel)
    AdcChannel: AdcChannelModel = field(default_factory=AdcChannelModel)
    AdcGroup: AdcGroupModel = field(default_factory=AdcGroupModel)
    AdcHwUnit: AdcHwUnitModel = field(default_factory=AdcHwUnitModel)
    AdcPublishedInformation: AdcPublishedInformationModel = field(default_factory=AdcPublishedInformationModel)

# -------------------- ARXML Exporter --------------------
class AdcArxmlExporter:
    @staticmethod
    def export(model: AdcAppModel, filepath: str):
        AUTOSAR = ET.Element("AUTOSAR")
        ar_packages = ET.SubElement(AUTOSAR, "AR-PACKAGES")
        ar_package = ET.SubElement(ar_packages, "AR-PACKAGE")
        ET.SubElement(ar_package, "SHORT-NAME").text = "AdcPackage"
        elements = ET.SubElement(ar_package, "ELEMENTS")

        # Module configuration values
        module_vals = ET.SubElement(elements, "ECUC-MODULE-CONFIGURATION-VALUES")
        ET.SubElement(module_vals, "SHORT-NAME").text = "AdcConfig"
        def_ref = ET.SubElement(module_vals, "DEFINITION-REF", {"DEST": "ECUC-MODULE-DEF"})
        def_ref.text = "/AUTOSAR/EcucDefs/Adc"

        containers = ET.SubElement(module_vals, "CONTAINERS")

        def container_from_obj(short_name: str, obj):
            cont = ET.SubElement(containers, "ECUC-CONTAINER-VALUE")
            ET.SubElement(cont, "SHORT-NAME").text = short_name
            ET.SubElement(cont, "DEFINITION-REF", {"DEST": "ECUC-PARAM-CONF-CONTAINER-DEF"}).text = f"/AUTOSAR/EcucDefs/Adc/{short_name}"
            pvals = ET.SubElement(cont, "PARAMETER-VALUES")
            
            # Define which fields are enumerations
            enum_fields = {
                'AdcPriorityImplementation', 'AdcResultAlignment',
                'AdcChannelRangeSelect', 'AdcGroupAccessMode', 
                'AdcGroupConversionMode', 'AdcGroupReplacement',
                'AdcGroupTriggSrc', 'AdcHwTrigSignal', 'AdcStreamingBufferMode'
            }
            
            for key, val in obj.__dict__.items():
                if isinstance(val, bool):
                    p = ET.SubElement(pvals, "ECUC-BOOLEAN-PARAM-VALUE")
                elif isinstance(val, int):
                    p = ET.SubElement(pvals, "ECUC-NUMERICAL-PARAM-VALUE")
                elif key in enum_fields:
                    p = ET.SubElement(pvals, "ECUC-ENUMERATION-PARAM-VALUE")  # ✅ FIXED
                else:
                    p = ET.SubElement(pvals, "ECUC-TEXTUAL-PARAM-VALUE")
                ET.SubElement(p, "SHORT-NAME").text = key
                ET.SubElement(p, "VALUE").text = str(val)
        # Add all containers
        container_from_obj("AdcConfigSet", model.AdcConfigSet)
        container_from_obj("AdcGeneral", model.AdcGeneral)
        container_from_obj("AdcPowerStateConfig", model.AdcPowerStateConfig)
        container_from_obj("AdcChannel", model.AdcChannel)
        container_from_obj("AdcGroup", model.AdcGroup)
        container_from_obj("AdcHwUnit", model.AdcHwUnit)
        container_from_obj("AdcPublishedInformation", model.AdcPublishedInformation)

        AdcArxmlExporter._indent(AUTOSAR)
        tree = ET.ElementTree(AUTOSAR)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                AdcArxmlExporter._indent(e, level + 1)
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
class AdcConfiguratorApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = AdcAppModel()
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

        # Build sections in correct order
        self._build_section("AdcConfigSet", self.model.AdcConfigSet)
        self._build_section("AdcGeneral", self.model.AdcGeneral)
        self._build_section("AdcChannel", self.model.AdcChannel)
        self._build_section("AdcGroup", self.model.AdcGroup)
        self._build_section("AdcPublishedInformation", self.model.AdcPublishedInformation)
        self._build_section("AdcPowerStateConfig", self.model.AdcPowerStateConfig)
        self._build_section("AdcHwUnit", self.model.AdcHwUnit)

        # Bottom generate button
        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill="x", pady=(0,10))
        ttk.Button(btn_frm, text="Generate ADC ARXML", command=self.on_generate).pack(side="left", padx=8, pady=6)

    def _build_section(self, name, obj):
        sec = CollapsibleFrame(self.content, text=f"{name}")
        sec.pack(fill="x", pady=4)

        # Fields that should be dropdowns and their options
        dropdowns = {
            "AdcPriorityImplementation": ["ADC_PRIORITY_HW", "ADC_PRIORITY_HW_SW", "ADC_PRIORITY_NONE"],
            "AdcResultAlignment": ["ADC_ALIGN_LEFT", "ADC_ALIGN_RIGHT"],
            "AdcChannelRangeSelect": [
                "ADC_RANGE_ALWAYS", "ADC_RANGE_BETWEEN", "ADC_RANGE_NOT_BETWEEN", 
                "ADC_RANGE_NOT_OVER_HIGH", "ADC_RANGE_NOT_UNDER_LOW", 
                "ADC_RANGE_OVER_HIGH", "ADC_RANGE_UNDER_LOW"
            ],
            "AdcGroupAccessMode": ["ADC_ACCESS_MODE_SINGLE", "ADC_ACCESS_MODE_STREAMING"],
            "AdcGroupConversionMode": ["ADC_CONV_MODE_CONTINUOUS", "ADC_CONV_MODE_ONESHOT"],
            "AdcGroupReplacement": ["ADC_GROUP_REPL_ABORT_RESTART", "ADC_GROUP_REPL_SUSPEND_RESUME"],
            "AdcGroupTriggSrc": ["ADC_TRIGG_SRC_HW", "ADC_TRIGG_SRC_SW"],
            "AdcHwTrigSignal": [
                "ADC_HW_TRIG_BOTH_EDGES", "ADC_HW_TRIG_FALLING_EDGE", "ADC_HW_TRIG_RISING_EDGE"
            ],
            "AdcStreamingBufferMode": ["ADC_STREAM_BUFFER_CIRCULAR", "ADC_STREAM_BUFFER_LINEAR"]
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

        sections = [
            "AdcConfigSet",
            "AdcGeneral",
            "AdcPowerStateConfig",
            "AdcChannel",
            "AdcGroup",
            "AdcHwUnit",
            "AdcPublishedInformation",
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
            AdcArxmlExporter.export(self.model, self.model.output_filepath)
            messagebox.showinfo("Saved", f"ADC ARXML generated at:\n{self.model.output_filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ADC ARXML:\n{e}")

# -------------------- Standalone App Runner --------------------
def create_standalone_app():
    """Create a standalone window for ADC configurator"""
    root = tk.Tk()
    root.title("AUTOSAR ADC Configurator")
    root.geometry("1100x720")
    
    app = AdcConfiguratorApp(root)
    app.pack(fill="both", expand=True)
    
    return root

if __name__ == "__main__":
    root = create_standalone_app()
    root.mainloop()