#!/usr/bin/env python3
"""
CAN Configurator (Tkinter) - full single-window app that builds a simple
ECUC-like ARXML from the controls.

- Collapsible sections for each CAN container.
- Responsive layout: the content area (canvas) expands with the window.
- All fields you listed are implemented as checkboxes, entries or dropdowns.
- "Generate ARXML" writes a minimal ARXML to ./output/<folder>/<filename>.arxml

This is a pragmatic, runnable tool intended for editing the values and
exporting a basic ARXML representation. Adjust the ARXML exporter if you
need exact ECUC schema tags/defs for your toolchain.
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field

# -------------------- Data Models --------------------
@dataclass
class CanGeneralModel:
    CanDevErrorDetect: bool = True
    CanIndex: int = 0
    CanLPduReceiveCalloutFunction: str = ""
    CanMainFunctionBusoffPeriod: int = 100
    CanMainFunctionModePeriod: int = 100
    CanMainFunctionWakeupPeriod: int = 100
    CanMultiplexedTransmission: int = 0
    CanPublicIcomSupport: bool = False
    CanSetBaudrateApi: bool = False
    CanTimeoutDuration: int = 100
    CanVersionInfoApi: bool = True
    CanOsCounterRef: bool = False
    CanSupportTTCANRef: bool = False

@dataclass
class CanControllerModel:
    CanBusoffProcessing: str = "INTERRUPT"  # Dropdown (INTERRUPT, POLLING)
    CanControllerActivation: bool = True
    CanControllerBaseAddress: int = 0
    CanControllerId: int = 0
    CanRxProcessing: str = "INTERRUPT"  # (INTERRUPT, MIXED, POLLING)
    CanTxProcessing: str = "INTERRUPT"  # (INTERRUPT, MIXED, POLLING)
    CanWakeupFunctionalityAPI: bool = False
    CanWakeupProcessing: str = "INTERRUPT"  # (INTERRUPT, POLLING)
    CanWakeupSupport: bool = False
    CanControllerDefaultBaudrate: bool = False
    CanCpuClockRef: bool = False
    CanWakeupSourceRef: bool = False

@dataclass
class CanControllerBaudrateConfigModel:
    CanControllerBaudRate: int = 500000
    CanControllerBaudRateConfigID: int = 0
    CanControllerPropSeg: int = 1
    CanControllerSeg1: int = 1
    CanControllerSeg2: int = 1
    CanControllerSyncJumpWidth: int = 1

@dataclass
class CanControllerFdBaudrateConfigModel:
    CanControllerFdBaudRate: int = 2000000
    CanControllerPropSeg: int = 1
    CanControllerSeg1: int = 1
    CanControllerSeg2: int = 1
    CanControllerSyncJumpWidth: int = 1
    CanControllerTrcvDelayCompensationOffset: int = 0
    CanControllerTxBitRateSwitch: bool = False

@dataclass
class CanHardwareObjectModel:
    CanFdPaddingValue: int = 0
    CanHandleType: str = "BASIC"  # BASIC, FULL
    CanHardwareObjectUsesPolling: bool = False
    CanHwObjectCount: int = 1
    CanIdType: str = "STANDARD"  # EXTENDED, MIXED, STANDARD
    CanObjectId: int = 0
    CanObjectType: str = "RECEIVE"  # RECEIVE, TRANSMIT
    CanTriggerTransmitEnable: bool = False
    CanControllerRef: bool = True
    CanMainFunctionRWPeriodRef: bool = False

@dataclass
class CanHwFilterModel:
    CanHwFilterCode: int = 0
    CanHwFilterMask: int = 0

@dataclass
class CanIcomGeneralModel:
    CanIcomLevel: str = "CAN_ICOM_LEVEL_ONE"
    CanIcomVariant: str = "CAN_ICOM_VARIANT_HW"

@dataclass
class CanIcomRxMessageModel:
    CanIcomCounterValue: int = 0
    CanIcomMessageId: int = 0
    CanIcomMessageIdMask: int = 0
    CanIcomMissingMessageTimerValue: int = 0
    CanIcomPayloadLengthError: bool = False

@dataclass
class CanIcomRxMessageSignalConfigModel:
    CanIcomSignalMask: int = 0
    CanIcomSignalOperation: str = "AND"  # AND, XOR, EQUAL, GREATER, SMALLER
    CanIcomSignalValue: int = 0
    CanIcomSignalRef: bool = False

@dataclass
class AppModel:
    output_filepath: str = os.path.abspath(os.path.join("output/CAN", "can_config.arxml"))
    CanConfigSet: bool = True
    CanGeneral: CanGeneralModel = field(default_factory=CanGeneralModel)
    CanController: CanControllerModel = field(default_factory=CanControllerModel)
    CanControllerBaudrateConfig: CanControllerBaudrateConfigModel = field(default_factory=CanControllerBaudrateConfigModel)
    CanControllerFdBaudrateConfig: CanControllerFdBaudrateConfigModel = field(default_factory=CanControllerFdBaudrateConfigModel)
    CanHardwareObject: CanHardwareObjectModel = field(default_factory=CanHardwareObjectModel)
    CanHwFilter: CanHwFilterModel = field(default_factory=CanHwFilterModel)
    CanIcomGeneral: CanIcomGeneralModel = field(default_factory=CanIcomGeneralModel)
    CanIcomRxMessage: CanIcomRxMessageModel = field(default_factory=CanIcomRxMessageModel)
    CanIcomRxMessageSignalConfig: CanIcomRxMessageSignalConfigModel = field(default_factory=CanIcomRxMessageSignalConfigModel)

# -------------------- ARXML Exporter (simple) --------------------
class ArxmlExporter:
    @staticmethod
    def export(model: AppModel, filepath: str):
        AUTOSAR = ET.Element("AUTOSAR")
        ar_packages = ET.SubElement(AUTOSAR, "AR-PACKAGES")
        ar_package = ET.SubElement(ar_packages, "AR-PACKAGE")
        ET.SubElement(ar_package, "SHORT-NAME").text = "CanPackage"
        elements = ET.SubElement(ar_package, "ELEMENTS")

        def container_from_obj(short_name: str, obj):
            cont = ET.SubElement(elements, "ECUC-CONTAINER-VALUE")
            ET.SubElement(cont, "SHORT-NAME").text = short_name
            ET.SubElement(cont, "DEFINITION-REF", {"DEST": "ECUC-PARAM-CONF-CONTAINER-DEF"}).text = f"/AUTOSAR/EcucDefs/Can/{short_name}"
            pvals = ET.SubElement(cont, "PARAMETER-VALUES")
            for key, val in obj.__dict__.items():
                # choose element tag by python type: boolean => ECUC-BOOLEAN-PARAM-VALUE, int => ECUC-NUMERICAL-PARAM-VALUE, str => ECUC-TEXTUAL-PARAM-VALUE
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
        ET.SubElement(cs, "SHORT-NAME").text = "CanConfigSet"
        ET.SubElement(cs, "DEFINITION-REF", {"DEST":"ECUC-PARAM-CONF-CONTAINER-DEF"}).text = "/AUTOSAR/EcucDefs/Can/CanConfigSet"
        p = ET.SubElement(cs, "PARAMETER-VALUES")
        pv = ET.SubElement(p, "ECUC-BOOLEAN-PARAM-VALUE")
        ET.SubElement(pv, "SHORT-NAME").text = "CanConfigSetIncluded"
        ET.SubElement(pv, "VALUE").text = "true" if model.CanConfigSet else "false"

        # Add other containers
        container_from_obj("CanGeneral", model.CanGeneral)
        container_from_obj("CanController", model.CanController)
        container_from_obj("CanControllerBaudrateConfig", model.CanControllerBaudrateConfig)
        container_from_obj("CanControllerFdBaudrateConfig", model.CanControllerFdBaudrateConfig)
        container_from_obj("CanHardwareObject", model.CanHardwareObject)
        container_from_obj("CanHwFilter", model.CanHwFilter)
        container_from_obj("CanIcomGeneral", model.CanIcomGeneral)
        container_from_obj("CanIcomRxMessage", model.CanIcomRxMessage)
        container_from_obj("CanIcomRxMessageSignalConfig", model.CanIcomRxMessageSignalConfig)

        ArxmlExporter._indent(AUTOSAR)
        tree = ET.ElementTree(AUTOSAR)
        tree.write(filepath, encoding="utf-8", xml_declaration=True)

    @staticmethod
    def _indent(elem, level=0):
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            for e in elem:
                ArxmlExporter._indent(e, level + 1)
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
        self.toggle_btn = ttk.Checkbutton(header, text=text, variable=self.show, style="Toolbutton", command=self._toggle)
        self.toggle_btn.pack(side="left", anchor="w")
        self.content = ttk.Frame(self)
        self.content.pack(fill="x", expand=True, padx=6, pady=4)

    def _toggle(self):
        if self.show.get():
            self.content.pack(fill="x", expand=True, padx=6, pady=4)
        else:
            self.content.forget()

# -------------------- Main App --------------------
class CanConfiguratorApp(tk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        self.model = AppModel()
        self.var_output_filepath = tk.StringVar(value=self.model.output_filepath)
        self._build_ui()

    def _build_ui(self):
        # top frame for filename/outfolder and module label
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x", side="top")

        ttk.Label(top, text="Output File Path").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.var_output_filepath, width=60).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top, text="Browse...", command=self._browse_output_file).grid(row=0, column=2, sticky="w")
        top.columnconfigure(1, weight=1)

        # main frame with canvas for scrollable content
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

        # ensure canvas resizes with window
        def _on_config(e):
            canvas.configure(scrollregion=canvas.bbox("all"))
            # make inner width track canvas width for responsive contents
            canvas.itemconfig(self.content_id, width=canvas.winfo_width())

        self.content_id = canvas.create_window((0,0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(self.content_id, width=e.width))

        # Build sections
        self._build_section_CanConfigSet(self.content)
        self._build_section("CanGeneral", self.model.CanGeneral)
        self._build_section("CanController", self.model.CanController)
        self._build_section("CanControllerBaudrateConfig", self.model.CanControllerBaudrateConfig)
        self._build_section("CanControllerFdBaudrateConfig", self.model.CanControllerFdBaudrateConfig)
        self._build_section("CanHardwareObject", self.model.CanHardwareObject)
        self._build_section("CanHwFilter", self.model.CanHwFilter)
        self._build_section("CanIcomGeneral", self.model.CanIcomGeneral)
        self._build_section("CanIcomRxMessage", self.model.CanIcomRxMessage)
        self._build_section("CanIcomRxMessageSignalConfig", self.model.CanIcomRxMessageSignalConfig)

        # bottom generate button
        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill="x", pady=(0,10))
        ttk.Button(btn_frm, text="🚀 Generate CAN ARXML", command=self.on_generate).pack(side="left", padx=8, pady=6)

    def _build_section_CanConfigSet(self, parent):
        sec = CollapsibleFrame(parent, text="📦 CanConfigSet")
        sec.pack(fill="x", pady=4)
        self.var_CanConfigSet = tk.BooleanVar(value=self.model.CanConfigSet)
        ttk.Checkbutton(sec.content, text="Include CanConfigSet", variable=self.var_CanConfigSet).pack(anchor="w")

    def _build_section(self, name, obj):
        sec = CollapsibleFrame(self.content, text=f"📦 {name}")
        sec.pack(fill="x", pady=4)

        # fields that should be dropdowns and their options
        dropdowns = {
            "CanBusoffProcessing": ["INTERRUPT", "POLLING"],
            "CanRxProcessing": ["INTERRUPT", "MIXED", "POLLING"],
            "CanTxProcessing": ["INTERRUPT", "MIXED", "POLLING"],
            "CanWakeupProcessing": ["INTERRUPT", "POLLING"],
            "CanHandleType": ["BASIC", "FULL"],
            "CanIdType": ["EXTENDED", "MIXED", "STANDARD"],
            "CanObjectType": ["RECEIVE", "TRANSMIT"],
            "CanIcomLevel": ["CAN_ICOM_LEVEL_ONE", "CAN_ICOM_LEVEL_TWO", "CAN_ICOM_LEVEL_THREE"],
            "CanIcomVariant": ["CAN_ICOM_VARIANT_HW", "CAN_ICOM_VARIANT_NONE", "CAN_ICOM_VARIANT_SW"],
            "CanIcomSignalOperation": ["AND", "XOR", "EQUAL", "GREATER", "SMALLER"]
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
            filetypes=[("ARXML files", "*.arxml"), ("All files", "*.*ero")]
        )
        if filepath:
            self.var_output_filepath.set(filepath)

    def on_generate(self):
        # update model from widgets
        self.model.output_filepath = self.var_output_filepath.get()
        if not self.model.output_filepath:
            messagebox.showerror("Error", "Output file path cannot be empty.")
            return

        self.model.CanConfigSet = bool(self.var_CanConfigSet.get())

        sections = [
            "CanGeneral",
            "CanController",
            "CanControllerBaudrateConfig",
            "CanControllerFdBaudrateConfig",
            "CanHardwareObject",
            "CanHwFilter",
            "CanIcomGeneral",
            "CanIcomRxMessage",
            "CanIcomRxMessageSignalConfig",
        ]
        for sec in sections:
            obj = getattr(self.model, sec)
            for key in obj.__dict__.keys():
                var_name = f"var_{sec}_{key}"
                if not hasattr(self, var_name):
                    continue
                var = getattr(self, var_name)
                try:
                    # all tk.Variable support .get()
                    v = var.get()
                except Exception:
                    v = None
                # cast types based on original model attribute type
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
            ArxmlExporter.export(self.model, self.model.output_filepath)
            messagebox.showinfo("Saved", f"ARXML generated at:\n{self.model.output_filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML:\n{e}")

