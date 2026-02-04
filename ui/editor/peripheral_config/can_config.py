#!/usr/bin/env python3
"""
CAN Configurator (Tkinter) - updated, complete single-file app.

Run: python3 can_configurator.py
"""
import os
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import xml.etree.ElementTree as ET
from dataclasses import dataclass, field, fields

# -------------------- Data Models --------------------
@dataclass
class CanGeneralModel:
    CanDevErrorDetect: bool = True
    CanEnableSecurityEventReporting: bool = False
    CanGlobalTimeSupport: bool = False
    CanIndex: int = 0
    CanLPduReceiveCalloutFunction: str = ""  # User-provided function name
    CanMainFunctionBusoffPeriod: int = 100
    CanMainFunctionModePeriod: int = 100
    CanMainFunctionWakeupPeriod: int = 100
    CanMultiplexedTransmission: int = 0
    CanSetBaudrateApi: bool = False
    CanTimeoutDuration: int = 100
    CanVersionInfoApi: bool = True


@dataclass
class CanControllerModel:
    CanBusoffProcessing: str = "INTERRUPT"  # Options: INTERRUPT, POLLING
    CanControllerActivation: bool = True
    CanControllerBaseAddress: int = 0
    CanControllerId: int = 0
    CanHwPnSupport: bool = False
    CanRxProcessing: str = "INTERRUPT"  # INTERRUPT, MIXED, POLLING
    CanTxProcessing: str = "INTERRUPT"  # INTERRUPT, MIXED, POLLING
    CanWakeupProcessing: str = "INTERRUPT"  # INTERRUPT, POLLING
    CanWakeupSupport: bool = False


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
    CanControllerSspOffset: bool = False
    CanControllerTxBitRateSwitch: bool = False


@dataclass
class CanPartialNetworkModel:
    CanPnEnabled: bool = False
    CanPnFrameCanId: int = 0
    CanPnFrameCanIdMask: int = 0
    CanPnFrameDlc: int = 8


@dataclass
class CanPnFrameDataMaskSpecModel:
    CanPnFrameDataMask: int = 0
    CanPnFrameDataMaskIndex: int = 0


@dataclass
class CanHardwareObjectModel:
    CanFdPaddingValue: int = 0
    CanHandleType: str = "BASIC"  # BASIC, FULL
    CanHardwareObjectUsesPolling: bool = False
    CanHwObjectCount: int = 1
    CanIdType: str = "STANDARD"  # EXTENDED, MIXED, STANDARD
    CanObjectId: int = 0
    CanObjectPayloadLength: str = "CAN_OBJECT_PL_8"  # see options below
    CanObjectType: str = "RECEIVE"  # RECEIVE, TRANSMIT
    CanTriggerTransmitEnable: bool = False


@dataclass
class CanHwFilterModel:
    CanHwFilterCode: int = 0
    CanHwFilterMask: int = 0


@dataclass
class CanMainFunctionRWPeriodsModel:
    CanMainFunctionPeriod: int = 0


@dataclass
class CanTTControllerModel:
    CanTTControllerApplWatchdogLimit: int = 0
    CanTTControllerCycleCountMax: int = 0
    CanTTControllerExpectedTxTrigger: int = 0
    CanTTControllerExternalClockSynchronisation: bool = False
    CanTTControllerGlobalTimeFiltering: bool = False
    CanTTControllerInitialRefOffset: int = 0
    CanTTControllerInterruptEnable: int = 0
    CanTTControllerLevel2: bool = False
    CanTTControllerNTUConfig: int = 0
    CanTTControllerOperationMode: str = "CAN_TT_TIME_TRIGGERED"
    # Options: CAN_TT_EVENT_SYNC_TIME_TRIGGERED, CAN_TT_EVENT_TRIGGERED, CAN_TT_TIME_TRIGGERED
    CanTTControllerSyncDeviation: int = 0
    CanTTControllerTimeMaster: bool = False
    CanTTControllerTimeMasterPriority: int = 0
    CanTTControllerTURRestore: bool = False
    CanTTControllerTxEnableWindowLength: int = 0
    CanTTControllerWatchTriggerGapTimeMark: int = 0
    CanTTControllerWatchTriggerTimeMark: int = 0
    CanTTIRQProcessing: str = "INTERRUPT"  # INTERRUPT, POLLING


@dataclass
class CanTTHardwareObjectTriggerModel:
    CanTTHardwareObjectBaseCycle: int = 0
    CanTTHardwareObjectCycleRepetition: int = 0
    CanTTHardwareObjectTimeMark: int = 0
    CanTTHardwareObjectTriggerId: int = 0
    CanTTHardwareObjectTriggerType: str = "CAN_TT_TX_TRIGGER_SINGLE"
    # Options: CAN_TT_RX_TRIGGER, CAN_TT_TX_REF_TRIGGER, CAN_TT_TX_REF_TRIGGER_GAP,
    # CAN_TT_TX_TRIGGER_EXCLUSIVE, CAN_TT_TX_TRIGGER_MERGED, CAN_TT_TX_TRIGGER_SINGLE


@dataclass
class CanXLGeneralModel:
    CanXLEthGlobalTimeSupport: bool = False


@dataclass
class CanXLControllerModel:
    CanXLCtrlEthDefaultPriority: int = 0
    CanXLEthDefaultQueue: int = 0
    CanXLEthPhysAddress: str = ""  # User input


@dataclass
class CanXLHardwareObjectModel:
    CanXLObjectId: int = 0
    CanXLHwFilter: bool = False


@dataclass
class CanXLBaudrateConfigModel:
    CanXLBaudRate: int = 1000000
    CanXLErrorSignaling: bool = False
    CanXLPropSeg: int = 1
    CanXLPwmL: int = 0
    CanXLPwmO: int = 0
    CanXLPwmS: int = 0
    CanXLSeg1: int = 1
    CanXLSeg2: int = 1
    CanXLSspOffset: int = 0
    CanXLSyncJumpWidth: int = 1
    CanXLTrcvPwmMode: bool = False


@dataclass
class CanXLEthEgressFifoModel:
    CanXLEthIngressFifoCanXLQueue: int = 0
    CanXLEthIngressFifoIdx: int = 0
    CanXLEthIngressFifoVcid: int = 0


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


# -------------------- AppModel (root) --------------------
@dataclass
class AppModel:
    output_filepath: str = os.path.abspath(os.path.join("output/CAN", "can_config.arxml"))
    CanConfigSet: bool = True
    # 18 CAN Sections
    CanGeneral: CanGeneralModel = field(default_factory=CanGeneralModel)
    CanController: CanControllerModel = field(default_factory=CanControllerModel)
    CanControllerBaudrateConfig: CanControllerBaudrateConfigModel = field(default_factory=CanControllerBaudrateConfigModel)
    CanControllerFdBaudrateConfig: CanControllerFdBaudrateConfigModel = field(default_factory=CanControllerFdBaudrateConfigModel)
    CanPartialNetwork: CanPartialNetworkModel = field(default_factory=CanPartialNetworkModel)
    CanPnFrameDataMaskSpec: CanPnFrameDataMaskSpecModel = field(default_factory=CanPnFrameDataMaskSpecModel)
    CanHardwareObject: CanHardwareObjectModel = field(default_factory=CanHardwareObjectModel)
    CanHwFilter: CanHwFilterModel = field(default_factory=CanHwFilterModel)
    CanMainFunctionRWPeriods: CanMainFunctionRWPeriodsModel = field(default_factory=CanMainFunctionRWPeriodsModel)
    CanTTController: CanTTControllerModel = field(default_factory=CanTTControllerModel)
    CanTTHardwareObjectTrigger: CanTTHardwareObjectTriggerModel = field(default_factory=CanTTHardwareObjectTriggerModel)
    CanXLGeneral: CanXLGeneralModel = field(default_factory=CanXLGeneralModel)
    CanXLController: CanXLControllerModel = field(default_factory=CanXLControllerModel)
    CanXLHardwareObject: CanXLHardwareObjectModel = field(default_factory=CanXLHardwareObjectModel)
    CanXLBaudrateConfig: CanXLBaudrateConfigModel = field(default_factory=CanXLBaudrateConfigModel)
    CanXLEthEgressFifo: CanXLEthEgressFifoModel = field(default_factory=CanXLEthEgressFifoModel)
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
                if isinstance(val, bool):
                    tag = "ECUC-BOOLEAN-PARAM-VALUE"
                elif isinstance(val, int):
                    tag = "ECUC-NUMERICAL-PARAM-VALUE"
                else:
                    tag = "ECUC-TEXTUAL-PARAM-VALUE"
                p = ET.SubElement(pvals, tag)
                ET.SubElement(p, "SHORT-NAME").text = key
                ET.SubElement(p, "VALUE").text = str(val)

        # Config set container
        cs = ET.SubElement(elements, "ECUC-CONTAINER-VALUE")
        ET.SubElement(cs, "SHORT-NAME").text = "CanConfigSet"
        ET.SubElement(cs, "DEFINITION-REF", {"DEST": "ECUC-PARAM-CONF-CONTAINER-DEF"}).text = "/AUTOSAR/EcucDefs/Can/CanConfigSet"
        p = ET.SubElement(cs, "PARAMETER-VALUES")
        pv = ET.SubElement(p, "ECUC-BOOLEAN-PARAM-VALUE")
        ET.SubElement(pv, "SHORT-NAME").text = "CanConfigSetIncluded"
        ET.SubElement(pv, "VALUE").text = "true" if model.CanConfigSet else "false"

        # Export every dataclass field in AppModel except output_filepath and CanConfigSet
        for f in fields(model):
            name = f.name
            if name in ("output_filepath", "CanConfigSet"):
                continue
            obj = getattr(model, name)
            # Only export dataclass-like containers (safety)
            if hasattr(obj, "__dict__"):
                container_from_obj(name, obj)

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
        self.all_sections = {}  # name->obj
        self._build_ui()

    def _build_ui(self):
        top = ttk.Frame(self, padding=8)
        top.pack(fill="x", side="top")

        ttk.Label(top, text="Output File Path").grid(row=0, column=0, sticky="w")
        ttk.Entry(top, textvariable=self.var_output_filepath, width=60).grid(row=0, column=1, sticky="ew", padx=8)
        ttk.Button(top, text="Browse...", command=self._browse_output_file).grid(row=0, column=2, sticky="w")
        top.columnconfigure(1, weight=1)

        main = ttk.Frame(self)
        main.pack(fill="both", expand=True, padx=8, pady=8)

        canvas = tk.Canvas(main)
        canvas.pack(side="left", fill="both", expand=True)

        vsb = ttk.Scrollbar(main, orient="vertical", command=canvas.yview)
        vsb.pack(side="right", fill="y")
        canvas.configure(yscrollcommand=vsb.set)
        # mouse wheel scroll handler (works on Windows/mac to a degree)
        canvas.bind_all("<MouseWheel>", lambda event: canvas.yview_scroll(int(-1*(event.delta/120)), "units"))

        # single content frame inside canvas (only one create_window)
        self.content = ttk.Frame(canvas)
        self.content_id = canvas.create_window((0, 0), window=self.content, anchor="nw")
        self.content.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.bind("<Configure>", lambda e: canvas.itemconfigure(self.content_id, width=e.width))

        # Build all sections dynamically
        self._build_all_sections()

        btn_frm = ttk.Frame(self)
        btn_frm.pack(fill="x", pady=(0, 10))
        ttk.Button(btn_frm, text="🚀 Generate ARXML", command=self.on_generate).pack(side="left", padx=8, pady=6)

    def _build_all_sections(self):
        # Build CanConfigSet checkbox
        self._build_section_CanConfigSet(self.content)

        # Map of the 18 sections - name to model object
        sections = {
            "CanGeneral": self.model.CanGeneral,
            "CanController": self.model.CanController,
            "CanControllerBaudrateConfig": self.model.CanControllerBaudrateConfig,
            "CanControllerFdBaudrateConfig": self.model.CanControllerFdBaudrateConfig,
            "CanPartialNetwork": self.model.CanPartialNetwork,
            "CanPnFrameDataMaskSpec": self.model.CanPnFrameDataMaskSpec,
            "CanHardwareObject": self.model.CanHardwareObject,
            "CanHwFilter": self.model.CanHwFilter,
            "CanMainFunctionRWPeriods": self.model.CanMainFunctionRWPeriods,
            "CanTTController": self.model.CanTTController,
            "CanTTHardwareObjectTrigger": self.model.CanTTHardwareObjectTrigger,
            "CanXLGeneral": self.model.CanXLGeneral,
            "CanXLController": self.model.CanXLController,
            "CanXLHardwareObject": self.model.CanXLHardwareObject,
            "CanXLBaudrateConfig": self.model.CanXLBaudrateConfig,
            "CanXLEthEgressFifo": self.model.CanXLEthEgressFifo,
            "CanIcomGeneral": self.model.CanIcomGeneral,
            "CanIcomRxMessage": self.model.CanIcomRxMessage,
            "CanIcomRxMessageSignalConfig": self.model.CanIcomRxMessageSignalConfig,
        }

        # store for later extraction
        self.all_sections = sections

        for name, obj in sections.items():
            self._build_section(name, obj)

    def _build_section_CanConfigSet(self, parent):
        sec = CollapsibleFrame(parent, text="📦 CanConfigSet")
        sec.pack(fill="x", pady=4)
        self.var_CanConfigSet = tk.BooleanVar(value=self.model.CanConfigSet)
        ttk.Checkbutton(sec.content, text="Include CanConfigSet", variable=self.var_CanConfigSet).pack(anchor="w")

    def _build_section(self, name, obj):
        sec = CollapsibleFrame(self.content, text=f"📦 {name}")
        sec.pack(fill="x", pady=4)

        # dropdown options for known keys
        dropdowns = {
            "CanBusoffProcessing": ["INTERRUPT", "POLLING"],
            "CanRxProcessing": ["INTERRUPT", "MIXED", "POLLING"],
            "CanTxProcessing": ["INTERRUPT", "MIXED", "POLLING"],
            "CanWakeupProcessing": ["INTERRUPT", "POLLING"],
            "CanHandleType": ["BASIC", "FULL"],
            "CanIdType": ["EXTENDED", "MIXED", "STANDARD"],
            "CanObjectType": ["RECEIVE", "TRANSMIT"],
            "CanObjectPayloadLength": [
                "CAN_OBJECT_PL_8", "CAN_OBJECT_PL_12", "CAN_OBJECT_PL_16",
                "CAN_OBJECT_PL_20", "CAN_OBJECT_PL_24", "CAN_OBJECT_PL_32",
                "CAN_OBJECT_PL_48", "CAN_OBJECT_PL_64"
            ],
            "CanIcomLevel": ["CAN_ICOM_LEVEL_ONE", "CAN_ICOM_LEVEL_TWO", "CAN_ICOM_LEVEL_THREE"],
            "CanIcomVariant": ["CAN_ICOM_VARIANT_HW", "CAN_ICOM_VARIANT_NONE", "CAN_ICOM_VARIANT_SW"],
            "CanIcomSignalOperation": ["AND", "XOR", "EQUAL", "GREATER", "SMALLER"],
            "CanTTControllerOperationMode": ["CAN_TT_EVENT_SYNC_TIME_TRIGGERED", "CAN_TT_EVENT_TRIGGERED", "CAN_TT_TIME_TRIGGERED"],
            "CanTTIRQProcessing": ["INTERRUPT", "POLLING"],
            "CanTTHardwareObjectTriggerType": [
                "CAN_TT_RX_TRIGGER", "CAN_TT_TX_REF_TRIGGER", "CAN_TT_TX_REF_TRIGGER_GAP",
                "CAN_TT_TX_TRIGGER_EXCLUSIVE", "CAN_TT_TX_TRIGGER_MERGED", "CAN_TT_TX_TRIGGER_SINGLE"
            ],
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
                var = tk.StringVar(value=str(val))
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
            filetypes=[("ARXML files", "*.arxml"), ("All files", "*.*")]
        )
        if filepath:
            self.var_output_filepath.set(filepath)

    def on_generate(self):
        # update model from widgets
        self.model.output_filepath = self.var_output_filepath.get().strip()
        if not self.model.output_filepath:
            messagebox.showerror("Error", "Output file path cannot be empty.")
            return

        self.model.CanConfigSet = bool(self.var_CanConfigSet.get())

        # update every section from UI
        for sec_name, obj in self.all_sections.items():
            for key in obj.__dict__.keys():
                var_name = f"var_{sec_name}_{key}"
                if not hasattr(self, var_name):
                    continue
                var = getattr(self, var_name)
                try:
                    v = var.get()
                except Exception:
                    v = None

                orig = getattr(obj, key)
                # cast appropriately
                if isinstance(orig, bool):
                    # var may be "0"/"1" or boolean
                    if isinstance(v, str):
                        lowered = v.lower()
                        val_bool = lowered in ("1", "true", "yes", "y", "on")
                    else:
                        val_bool = bool(v)
                    setattr(obj, key, val_bool)
                elif isinstance(orig, int):
                    try:
                        setattr(obj, key, int(str(v).strip()) if str(v).strip() != "" else 0)
                    except Exception:
                        setattr(obj, key, 0)
                else:
                    setattr(obj, key, str(v))

        # prepare output dir
        outdir = os.path.dirname(self.model.output_filepath)
        if outdir:
            os.makedirs(outdir, exist_ok=True)

        try:
            ArxmlExporter.export(self.model, self.model.output_filepath)
            messagebox.showinfo("Saved", f"ARXML generated at:\n{self.model.output_filepath}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML:\n{e}")


# -------------------- Run App --------------------
def main():
    root = tk.Tk()
    root.title("CAN Configurator")
    root.geometry("900x700")
    app = CanConfiguratorApp(root)
    app.pack(fill="both", expand=True)
    root.mainloop()


if __name__ == "__main__":
    main()
