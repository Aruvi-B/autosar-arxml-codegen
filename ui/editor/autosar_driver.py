import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import json
from datetime import datetime


from .peripheral_config.dio_config import DioConfiguratorApp
from .peripheral_config.adc_config import AdcConfiguratorApp
from .peripheral_config.gpt_config import GptConfiguratorApp
from .peripheral_config.spi_config import SpiConfiguratorApp
from .peripheral_config.wdg_config import WdgConfiguratorApp
from .peripheral_config.can_config import CanConfiguratorApp

class AutosarDriverPanel:
    def __init__(self, parent, status_logger=None):
        self.frame = ttk.Frame(parent)
        self.status_logger = status_logger
        self.output_path_var = tk.StringVar()
        self.module_var = tk.StringVar()
        self.filename_var = tk.StringVar(value="Dio_Config.arxml")
        self.add_timestamp_var = tk.BooleanVar(value=True)
        
        self.current_module_vars = {}
        self.current_module = None
        self.dio_config_frame = None
        self.adc_config_frame = None

        self.output_path_var.set(os.path.abspath("output"))
        
        self.setup_ui()

    def setup_ui(self):
        ttk.Label(self.frame, text="AUTOSAR ARXML Generator", font=("Arial", 12, "bold")).pack(pady=5)

        control_frame = ttk.Frame(self.frame)
        control_frame.pack(fill="x", pady=10)

        ttk.Label(control_frame, text="Module:").pack(side="left", padx=5)
        self.combo = ttk.Combobox(
            control_frame,
            textvariable=self.module_var,
            state="readonly",
            values=["ADC", "DIO", "GPT", "WDG", "CAN", "SPI"],
            width=15
        )
        self.combo.set("Select Module")
        self.combo.pack(side="left", padx=5)
        self.combo.bind("<<ComboboxSelected>>", self.on_module_select)

        main_frame = ttk.Frame(self.frame)
        main_frame.pack(fill="both", expand=True, padx=10, pady=10)

        left_frame = ttk.LabelFrame(main_frame, text="Configuration", padding=5)
        left_frame.pack(side="left", fill="both", expand=True, padx=(0, 5))

        self.dynamic_frame = ttk.Frame(left_frame)
        self.dynamic_frame.pack(fill="both", expand=True)

        output_frame = ttk.LabelFrame(left_frame, text="Output Settings", padding=10)
        output_frame.pack(fill="x", pady=(10, 0), padx=5)
        output_frame.columnconfigure(1, weight=1)

        self.status_var = tk.StringVar(value="Ready - Select a module to begin")
        status_frame = ttk.Frame(self.frame)
        status_frame.pack(fill="x", side="bottom", pady=(5, 0))
        ttk.Label(status_frame, textvariable=self.status_var, relief="sunken", anchor="w").pack(fill="x")

    def on_module_select(self, event):
        self.current_module = self.module_var.get()
        self.build_dynamic_ui()

    def build_dynamic_ui(self):
        for widget in self.dynamic_frame.winfo_children():
            widget.destroy()
        
        self.current_module_vars = {}
        self.dio_config_frame = None
        self.adc_config_frame = None
        self.gpt_frame = None
        self.spi_frame = None
        self.wdg_frame = None
        self.can_frame = None
        module = self.current_module

        if not module:
            return

        if module == "DIO":
            self.show_dio_options()
        elif module == "ADC":
            self.show_adc_options()
        elif module == "GPT":
            self.show_gpt_options()
        elif module == "WDG":
            self.show_wdg_options()
        elif module == "CAN":
            self.show_can_options()
        elif module == "SPI":
            self.show_spi_options()
        
    def create_scrollable_frame(self, parent):
        main_frame = ttk.Frame(parent)
        main_frame.pack(fill="both", expand=True)
        
        canvas = tk.Canvas(main_frame)
        scrollbar = ttk.Scrollbar(main_frame, orient="vertical", command=canvas.yview)
        scroll_frame = ttk.Frame(canvas)

        def configure_scroll(event):
            canvas.configure(scrollregion=canvas.bbox("all"))
        
        def on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")

        scroll_frame.bind("<Configure>", configure_scroll)
        canvas.bind("<MouseWheel>", on_mousewheel)

        canvas_frame = canvas.create_window((0, 0), window=scroll_frame, anchor="nw")
        
        def configure_canvas(event):
            canvas.itemconfig(canvas_frame, width=event.width)
        
        canvas.bind("<Configure>", configure_canvas)
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        return canvas, scrollbar, scroll_frame

    def show_dio_options(self):
        self.dio_config_frame = DioConfiguratorApp(self.dynamic_frame)
        self.dio_config_frame.pack(fill="both", expand=True)

    def show_adc_options(self):
        self.adc_config_frame = AdcConfiguratorApp(self.dynamic_frame)
        self.adc_config_frame.pack(fill="both", expand=True)

    def show_gpt_options(self):
        self.gpt_frame = GptConfiguratorApp(self.dynamic_frame)
        self.gpt_frame.pack(fill="both", expand=True)

    def show_can_options(self):
        self.can_frame = CanConfiguratorApp(self.dynamic_frame)
        self.can_frame.pack(fill="both", expand=True)

    def show_wdg_options(self):
        self.wdg_frame = WdgConfiguratorApp(self.dynamic_frame)
        self.wdg_frame.pack(fill="both", expand=True)

    def show_spi_options(self):
        self.spi_frame = SpiConfiguratorApp(self.dynamic_frame)
        self.spi_frame.pack(fill="both", expand=True)

    def collect_user_inputs(self):
        user_inputs = {}
        
        for container_name, params in self.current_module_vars.items():
            user_inputs[container_name] = {}
            for param_name, var in params.items():
                try:
                    if isinstance(var, tk.BooleanVar):
                        value = var.get()
                        user_inputs[container_name][param_name] = value
                    elif isinstance(var, tk.IntVar):
                        value = var.get()
                        user_inputs[container_name][param_name] = value
                    else:  # StringVar
                        value = var.get().strip()
                        user_inputs[container_name][param_name] = value
                except tk.TclError:
                    user_inputs[container_name][param_name] = ""
        
        return user_inputs

    def select_output_folder(self):
        folder = filedialog.askdirectory(title="Select output folder")
        if folder:
            self.output_path_var.set(folder)

    def generate_and_save(self):
        if not self.current_module:
            messagebox.showwarning("No Module", "Please select a module first.")
            return

        if self.current_module == "DIO":
            self.generate_dio_arxml()
        elif self.current_module == "ADC":
            self.generate_adc_arxml()
        elif self.current_module == "GPT":
            self.generate_gpt_arxml()
        elif self.current_module == "SPI":
            self.generate_spi_arxml()
        elif self.current_module == "WDG":
            self.generate_wdg_arxml()
        elif self.current_module == "CAN":
            self.generate_can_arxml()
        # else:
        #     self.generate_create_pannalam()

    def generate_dio_arxml(self):
        if not self.dio_config_frame:
            messagebox.showwarning("DIO Not Initialized", "DIO module UI is not initialized.")
            return
        try:
            self.dio_config_frame.on_generate()
            self.status_var.set(f"Success - ARXML generated for DIO")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML for DIO:\n{e}")

    def generate_adc_arxml(self):
        if not self.adc_config_frame:
            messagebox.showwarning("ADC Not Initialized", "ADC module UI is not initialized.")
            return

        # The ADCConfiguratorApp handles its own output folder and filename
        # so we just need to trigger its on_generate method.
        try:
            self.adc_config_frame.on_generate()
            self.status_var.set(f"Success - ARXML generated for ADC")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML for ADC:\n{e}")
    def generate_gpt_arxml(self):
        if not self.gpt_frame:
            messagebox.showwarning("GPT Not Initialized", "GPT module UI is not initialized.")
            return

        try:
            self.gpt_frame.on_generate()
            self.status_var.set(f"Success - ARXML generated for GPT")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML for GPT:\n{e}")
    def generate_spi_arxml(self):
        if not self.spi_frame:
            messagebox.showwarning("SPI Not Initialized", "SPI module UI is not initialized.")
            return
        try:
            self.spi_frame.on_generate()
            self.status_var.set(f"Success - ARXML generated for SPI")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML for SPI:\n{e}")
    def generate_wdg_arxml(self):
        if not self.wdg_frame:
            messagebox.showwarning("WDG Not Initialized", "WDG module UI is not initialized.")
            return
        try:
            self.wdg_frame.on_generate()
            self.status_var.set(f"Success - ARXML generated for WDG")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML for WDG:\n{e}")
    def generate_can_arxml(self):
        if not self.can_frame:
            messagebox.showwarning("CAN Not Initialized", "CAN module UI is not initialized.")
            return
        try:
            self.can_frame.on_generate()
            self.status_var.set(f"Success - ARXML generated for CAN")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to generate ARXML for CAN:\n{e}")