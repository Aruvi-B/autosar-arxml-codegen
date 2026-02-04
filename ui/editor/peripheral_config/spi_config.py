#!/usr/bin/env python3
"""
SPI Configurator (Tkinter) - following standardized GUI structure
Converted from original SPI script to match CAN configurator pattern.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# -------------------- Data Models --------------------
@dataclass
class SpiDemEventParameterRefsModel:
    SPI_E_HARDWARE_ERROR: bool = True

@dataclass
class SpiGeneralModel:
    SpiCancelApi: bool = True
    SpiChannelBuffersAllowed: int = 1
    SpiDevErrorDetect: bool = True
    SpiHwStatusApi: bool = True
    SpiInterruptibleSeqAllowed: bool = False
    SpiLevelDelivered: int = 0
    SpiMainFunctionPeriod: int = 10
    SpiSupportConcurrentSyncTransmit: bool = False
    SpiUserCallbackHeaderFile: str = ""
    SpiVersionInfoApi: bool = True

@dataclass
class SpiSequenceModel:
    SpiInterruptibleSequence: bool = False
    SpiSeqEndNotification: bool = False
    SpiSequenceId: int = 0
    SpiJobAssignment: bool = True

@dataclass
class SpiChannelModel:
    SpiChannelId: int = 0
    SpiChannelType: bool = True
    SpiDataWidth: int = 8
    SpiDefaultData: int = 0
    SpiEbMaxLength: int = 1
    SpiIbNBuffers: int = 1
    SpiTransferStart: bool = True

@dataclass
class SpiChannelListModel:
    SpiChannelIndex: int = 0
    SpiChannelAssignment: bool = True

@dataclass
class SpiJobModel:
    SpiHwUnitSynchronous: str = "SYNCHRONOUS"  # Dropdown: SYNCHRONOUS, ASYNCHRONOUS
    SpiJobEndNotification: bool = True
    SpiJobId: int = 0
    SpiJobPriority: int = 0
    SpiDeviceAssignment: bool = True

@dataclass
class SpiExternalDeviceModel:
    SpiBaudrate: int = 1000000
    SpiCsBehavior: str = "CS_KEEP_ASSERTED" # Dropdown: CS_KEEP_ASSERTED, CS_TOGGLE
    SpiCsIdentifier: str = "CS0"
    SpiCsPolarity: str = "HIGH"  # Dropdown: HIGH, LOW
    SpiCsSelection: str = "CS_VIA_GPIO"  # Dropdown: CS_VIA_GPIO, CS_VIA_PERIPHERAL_ENGINE
    SpiDataShiftEdge: str = "LEADING"  # Dropdown: LEADING, TRAILING
    SpiEnableCs: bool = True
    SpiHwUnit: str = "CSIB0"  # Dropdown: CSIB0, CSIB1, CSIB2, CSIB3
    SpiShiftClockIdleLevel: str = "HIGH"  # Dropdown: HIGH, LOW
    SpiTimeClk2Cs: int = 10
    SpiTimeCs2Clk: int = 10
    SpiTimeCs2Cs: int = 10

@dataclass
class SpiDriverModel:
    SpiMaxChannel: int = 0
    SpiMaxJob: int = 0
    SpiMaxSequence: int = 0

@dataclass
class SpiPublishedInformationModel:
    SpiMaxHwUnit: int = 0

@dataclass
class SpiAppModel:
    output_filepath: str = os.path.abspath(os.path.join("output/SPI", "spi_config.arxml"))
    SpiConfigSet: bool = True
    SpiDemEventParameterRefs: SpiDemEventParameterRefsModel = field(default_factory=SpiDemEventParameterRefsModel)
    SpiGeneral: SpiGeneralModel = field(default_factory=SpiGeneralModel)
    SpiSequence: SpiSequenceModel = field(default_factory=SpiSequenceModel)
    SpiChannel: SpiChannelModel = field(default_factory=SpiChannelModel)
    SpiChannelList: SpiChannelListModel = field(default_factory=SpiChannelListModel)
    SpiJob: SpiJobModel = field(default_factory=SpiJobModel)
    SpiExternalDevice: SpiExternalDeviceModel = field(default_factory=SpiExternalDeviceModel)
    SpiDriver: SpiDriverModel = field(default_factory=SpiDriverModel)
    SpiPublishedInformation: SpiPublishedInformationModel = field(default_factory=SpiPublishedInformationModel)

# -------------------- ARXML Exporter --------------------
class SpiArxmlExporter:
    @staticmethod
    def export(model: SpiAppModel, filepath: str):
        AUTOSAR = ET.Element("AUTOSAR")
        ar_packages = ET.SubElement(AUTOSAR, "AR-PACKAGES")
        ar_package = ET.SubElement(ar_packages, "AR-PACKAGE")
        ET.SubElement(ar_package, "SHORT-NAME").text = "SpiPackage"
        elements = ET.SubElement(ar_package, "ELEMENTS")

        def container_from_obj(short_name: str, obj):
            cont = ET.SubElement(elements, "ECUC-CONTAINER-VALUE")
            ET.SubElement(cont, "SHORT-NAME").text = short_name
            ET.SubElement(cont, "DEFINITION-REF", {"DEST": "ECUC-PARAM-CONF-CONTAINER-DEF"}).text = f"/AUTOSAR/EcucDefs/Spi/{short_name}"
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
        ET.SubElement(cs, "SHORT-NAME").text = "SpiConfigSet"
        ET.SubElement(cs, "DEFINITION-REF", {"DEST":"ECUC-PARAM-CONF-CONTAINER-DEF"}).text = "/AUTOSAR/EcucDefs/Spi/SpiConfigSet"
        p = ET.SubElement(cs, "PARAMETER-VALUES")
        pv = ET.SubElement(p, "ECUC-BOOLEAN-PARAM-VALUE")
        ET.SubElement(pv, "SHORT-NAME").text = "SpiConfigSetIncluded"
        ET.SubElement(pv, "VALUE").text = "true" if model.SpiConfigSet else "false"

        # Add other containers
        container_from_obj("SpiDemEventParameterRefs", model.SpiDemEventParameterRefs)
        container_from_obj("SpiGeneral", model.SpiGeneral)
        container_from_obj("SpiSequence", model.SpiSequence)
        container_from_obj("SpiChannel", model.SpiChannel)
        container_from_obj("SpiChannelList", model.SpiChannelList)
        container_from_obj("SpiJob", model.SpiJob)
        container_from_obj("SpiExternalDevice", model.SpiExternalDevice)
        container_from_obj("SpiDriver", model.SpiDriver)
        container_from_obj("SpiPublishedInformation", model.SpiPublishedInformation)

        SpiArxmlExporter._indent(AUTOSAR)
        tree = ET.ElementTree(AUTOSAR)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                SpiArxmlExporter._indent(e, level + 1)
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
class SpiConfiguratorApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = SpiAppModel()
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
        self._build_section_SpiConfigSet(self.content)
        self._build_section("SpiDemEventParameterRefs", self.model.SpiDemEventParameterRefs)
        self._build_section("SpiGeneral", self.model.SpiGeneral)
        self._build_section("SpiSequence", self.model.SpiSequence)
        self._build_section("SpiChannel", self.model.SpiChannel)
        self._build_section("SpiChannelList", self.model.SpiChannelList)
        self._build_section("SpiJob", self.model.SpiJob)
        self._build_section("SpiExternalDevice", self.model.SpiExternalDevice)
        self._build_section("SpiDriver", self.model.SpiDriver)
        self._build_section("SpiPublishedInformation", self.model.SpiPublishedInformation)

        # Bottom generate button
        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill="x", pady=(0,10))
        ttk.Button(btn_frm, text="🚀 Generate SPI ARXML", command=self.on_generate).pack(side="left", padx=8, pady=6)

    def _build_section_SpiConfigSet(self, parent):
        sec = CollapsibleFrame(parent, text="📦 SpiConfigSet")
        sec.pack(fill="x", pady=4)
        self.var_SpiConfigSet = tk.BooleanVar(value=self.model.SpiConfigSet)
        ttk.Checkbutton(sec.content, text="Include SpiConfigSet", variable=self.var_SpiConfigSet).pack(anchor="w")

    def _build_section(self, name, obj):
        sec = CollapsibleFrame(self.content, text=f"📦 {name}")
        sec.pack(fill="x", pady=4)

        # Fields that should be dropdowns and their options
        dropdowns = {
            "SpiHwUnitSynchronous": ["SYNCHRONOUS", "ASYNCHRONOUS"],
            "SpiCsPolarity": ["HIGH", "LOW"],
            "SpiCsSelection": ["CS_VIA_GPIO", "CS_VIA_PERIPHERAL_ENGINE"],
            "SpiDataShiftEdge": ["LEADING", "TRAILING"],
            "SpiHwUnit": ["CSIB0", "CSIB1", "CSIB2", "CSIB3"],
            "SpiShiftClockIdleLevel": ["HIGH", "LOW"],
            "SpiCsBehavior": ["CS_KEEP_ASSERTED", "CS_TOGGLE"]
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

        self.model.SpiConfigSet = bool(self.var_SpiConfigSet.get())

        sections = [
            "SpiDemEventParameterRefs",
            "SpiGeneral",
            "SpiSequence",
            "SpiChannel",
            "SpiChannelList",
            "SpiJob",
            "SpiExternalDevice",
            "SpiDriver",
            "SpiPublishedInformation",
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
            SpiArxmlExporter.export(self.model, self.model.output_filepath)
            messagebox.showinfo("Saved", f"SPI ARXML generated at:\n{self.model.output_filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate SPI ARXML:\n{e}")

# -------------------- Standalone App Runner --------------------
def create_standalone_app():
    """Create a standalone window for SPI configurator"""
    root = tk.Tk()
    root.title("AUTOSAR SPI Configurator")
    root.geometry("1100x720")
    
    app = SpiConfiguratorApp(root)
    app.pack(fill="both", expand=True)
    
    return root

if __name__ == "__main__":
    root = create_standalone_app()
    root.mainloop()
