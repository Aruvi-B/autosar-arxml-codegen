import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from .drivers.can_code import CAN_H_TEMPLATE, CAN_C_TEMPLATE

class ARXMLtoCANGenerator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.config_data = self.get_default_config()
        
        self.arxml_file_path = None
        self.status_var = tk.StringVar()
        self.setup_ui()

    def get_default_config(self):
        return {
            'vendor_id': 1810,
            'module_id': 80,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            'can_config_set': True,
            'can_general': {},
            'controllers': [],
            'hw_objects': [],
            'hw_filters': [],
            'main_function_rw_periods': [],
            'can_icom_enabled': False,
            'icom_configs': [],
            'can_icom_general': {},
            'icom_rx_messages': [],
            'icom_signal_configs': [],  # Added for orphaned signal configs
            'icom_wakeup_causes': [],
            'can_partial_network': {},
            'can_pn_frame_data_mask_spec': [],
            'can_tt_controller': {},
            'can_tt_hardware_object_trigger': [],
            'can_xl_general': {},
            'can_xl_controller': {},
            'can_xl_hardware_object': [],
            'can_xl_baudrate_config': {},
            'can_xl_eth_egress_fifo': [],
        }

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title_label = ttk.Label(self, text="ARXML to CAN Driver Generator", 
                               font=('Arial', 16, 'bold'))
        title_label.grid(row=0, column=0, pady=(10, 10), sticky='w', padx=10)

        file_frame = ttk.LabelFrame(self, text="Select ARXML File", padding="10")
        file_frame.grid(row=1, column=0, sticky='ew', padx=10)
        file_frame.columnconfigure(1, weight=1)

        self.file_path_var = tk.StringVar(value="No file selected")
        file_path_label = ttk.Label(file_frame, textvariable=self.file_path_var, 
                                   background="white", relief="sunken", padding="5")
        file_path_label.grid(row=0, column=1, sticky='ew')

        browse_btn = ttk.Button(file_frame, text="Browse ARXML File", 
                               command=self.browse_arxml_file)
        browse_btn.grid(row=0, column=0, padx=(0,10))

        self.parse_btn = ttk.Button(file_frame, text="Parse ARXML", 
                                   command=self.parse_arxml, state='disabled')
        self.parse_btn.grid(row=0, column=2, padx=(10,0))

        main_paned_window = ttk.PanedWindow(self, orient=tk.HORIZONTAL)
        main_paned_window.grid(row=2, column=0, sticky='nsew', padx=10, pady=(10, 0))

        left_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(left_frame, weight=1)
        left_frame.rowconfigure(0, weight=1)
        left_frame.columnconfigure(0, weight=1)

        right_frame = ttk.Frame(main_paned_window)
        main_paned_window.add(right_frame, weight=1)
        right_frame.rowconfigure(0, weight=1)
        right_frame.columnconfigure(0, weight=1)

        config_frame = ttk.LabelFrame(left_frame, text="Extracted Configuration (Read-Only)", padding="10")
        config_frame.grid(row=0, column=0, sticky='nsew')
        config_frame.rowconfigure(0, weight=1)
        config_frame.columnconfigure(0, weight=1)
        
        self.config_text = scrolledtext.ScrolledText(config_frame, font=('Courier', 9), state='disabled', wrap='word')
        self.config_text.grid(row=0, column=0, sticky='nsew')

        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.grid(row=1, column=0, sticky='w', pady=(10, 0))

        self.generate_btn = ttk.Button(buttons_frame, text="Generate CAN_CFG.H", command=self.generate_can_cfg_h)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(buttons_frame, text="Save Driver Files", command=self.save_driver_files)
        self.save_btn.pack(side=tk.LEFT)

        code_frame = ttk.LabelFrame(right_frame, text="Generated Can_Cfg.h", padding="10")
        code_frame.grid(row=0, column=0, sticky='nsew')
        code_frame.rowconfigure(0, weight=1)
        code_frame.columnconfigure(0, weight=1)

        self.code_text = scrolledtext.ScrolledText(code_frame, wrap='none', font=('Courier', 9))
        self.code_text.grid(row=0, column=0, sticky='nsew')
        
        code_scrollbar_y = ttk.Scrollbar(code_frame, orient='vertical', command=self.code_text.yview)
        code_scrollbar_y.grid(row=0, column=1, sticky='ns')
        self.code_text['yscrollcommand'] = code_scrollbar_y.set
        
        code_scrollbar_x = ttk.Scrollbar(code_frame, orient='horizontal', command=self.code_text.xview)
        code_scrollbar_x.grid(row=1, column=0, sticky='ew')
        self.code_text['xscrollcommand'] = code_scrollbar_x.set

        status_frame = ttk.Frame(self)
        status_frame.grid(row=3, column=0, sticky='ew', padx=10, pady=(5, 10))
        
        ttk.Label(status_frame, text="Status:").pack(side='left')
        ttk.Label(status_frame, textvariable=self.status_var).pack(side='left', padx=(5, 0))

    def browse_arxml_file(self):
        file_path = filedialog.askopenfilename(
            title="Select ARXML File",
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.*")])
        
        if file_path:
            self.arxml_file_path = file_path
            self.file_path_var.set(os.path.basename(file_path))
            self.parse_btn.config(state='normal')
            self.status_var.set("File selected - Ready to parse")

    def parse_arxml(self):
        if not self.arxml_file_path:
            messagebox.showerror("Error", "No ARXML file selected")
            return

        try:
            self.status_var.set("Parsing ARXML...")
            self.config_data = self.get_default_config()
            tree = ET.parse(self.arxml_file_path)
            root = tree.getroot()
            
            success = self.extract_config_from_arxml(root)
            
            if success:
                self.display_configuration()
                self.status_var.set("ARXML parsed successfully")
                messagebox.showinfo("Success", "ARXML parsed successfully!")
                self.generate_can_cfg_h()
            else:
                self.status_var.set("Warning: Limited configuration found")
                messagebox.showwarning("Warning", "ARXML parsed but limited CAN configuration found. Please verify the file structure.")
            
        except ET.ParseError as e:
            self.status_var.set("Parse error")
            messagebox.showerror("Parse Error", f"Failed to parse ARXML file: {str(e)}")
        except Exception as e:
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_config_from_arxml(self, root):
        container_paths = [
            './/ECUC-CONTAINER-VALUE',
            './/{http://autosar.org/schema/r4.0}ECUC-CONTAINER-VALUE',
        ]
        
        containers = []
        for path in container_paths:
            found = root.findall(path)
            if found:
                containers.extend(found)
        
        config_found = False
        
        for container in containers:
            short_name_elem = container.find('SHORT-NAME')
            if short_name_elem is None:
                continue
                
            short_name = short_name_elem.text

            if 'CanConfigSet' in short_name:
                config_found = True
                self.config_data['can_config_set'] = True
            elif 'CanGeneral' in short_name and 'Icom' not in short_name:
                config_found = True
                self._extract_can_general(container)
            elif 'CanController' in short_name and 'Baudrate' not in short_name and 'Fd' not in short_name:
                config_found = True
                self._extract_controller_config(container, short_name)
            elif 'CanControllerBaudrateConfig' in short_name and 'Fd' not in short_name:
                config_found = True
                self._extract_controller_baudrate_config(container, short_name)
            elif 'CanControllerFdBaudrateConfig' in short_name:
                config_found = True
                self._extract_controller_fd_baudrate_config(container, short_name)
            elif 'CanHardwareObject' in short_name:
                config_found = True
                self._extract_hw_object_config(container, short_name)
            elif 'CanHwFilter' in short_name:
                config_found = True
                self._extract_hw_filter_config(container)
            elif 'CanMainFunctionRWPeriods' in short_name:
                config_found = True
                self._extract_main_function_rw_periods(container)
            elif 'CanIcomGeneral' in short_name:
                config_found = True
                self.config_data['can_icom_enabled'] = True
                self._extract_icom_general_config(container)
            elif 'CanIcomRxMessageSignalConfig' in short_name:
                config_found = True
                self.config_data['can_icom_enabled'] = True
                self._extract_icom_rx_message_signal_config(container, short_name)
            elif 'CanIcomRxMessage' in short_name and 'Signal' not in short_name:
                config_found = True
                self.config_data['can_icom_enabled'] = True
                self._extract_icom_rx_message_config(container, short_name)
            elif 'CanIcom' in short_name and 'General' not in short_name and 'RxMessage' not in short_name:
                config_found = True
                self.config_data['can_icom_enabled'] = True
            elif 'CanPartialNetwork' in short_name:
                config_found = True
                self._extract_can_partial_network(container)
            elif 'CanPnFrameDataMaskSpec' in short_name:
                config_found = True
                self._extract_can_pn_frame_data_mask_spec(container)
            elif 'CanTTController' in short_name:
                config_found = True
                self._extract_can_tt_controller(container)
            elif 'CanTTHardwareObjectTrigger' in short_name:
                config_found = True
                self._extract_can_tt_hardware_object_trigger(container)
            elif 'CanXLGeneral' in short_name:
                config_found = True
                self._extract_can_xl_general(container)
            elif 'CanXLController' in short_name:
                config_found = True
                self._extract_can_xl_controller(container)
            elif 'CanXLHardwareObject' in short_name:
                config_found = True
                self._extract_can_xl_hardware_object(container)
            elif 'CanXLBaudrateConfig' in short_name:
                config_found = True
                self._extract_can_xl_baudrate_config(container)
            elif 'CanXLEthEgressFifo' in short_name:
                config_found = True
                self._extract_can_xl_eth_egress_fifo(container)

        return config_found

    def _extract_can_general(self, container):
        self.config_data['can_general'] = self._extract_params(container)

    def _extract_controller_config(self, container, container_name):
        controller = self._extract_params(container)
        controller['id'] = controller.get('CanControllerId', len(self.config_data['controllers']))
        controller['baudrate_configs'] = []
        controller['fd_baudrate_configs'] = []
        self.config_data['controllers'].append(controller)

    def _extract_controller_baudrate_config(self, container, container_name):
        """Extract standalone CanControllerBaudrateConfig containers"""
        baudrate_config = self._extract_params(container)
        # Try to find the parent controller by looking for references or use a default approach
        controller_ref = self._find_controller_reference(container)
        if controller_ref is not None:
            if controller_ref < len(self.config_data['controllers']):
                self.config_data['controllers'][controller_ref]['baudrate_configs'].append(baudrate_config)
        else:
            # If no specific controller reference found, add to the last controller or create a default one
            if not self.config_data['controllers']:
                default_controller = {'id': 0, 'baudrate_configs': [], 'fd_baudrate_configs': []}
                self.config_data['controllers'].append(default_controller)
            self.config_data['controllers'][-1]['baudrate_configs'].append(baudrate_config)

    def _extract_controller_fd_baudrate_config(self, container, container_name):
        """Extract standalone CanControllerFdBaudrateConfig containers"""
        fd_baudrate_config = self._extract_params(container)
        # Try to find the parent controller by looking for references or use a default approach
        controller_ref = self._find_controller_reference(container)
        if controller_ref is not None:
            if controller_ref < len(self.config_data['controllers']):
                self.config_data['controllers'][controller_ref]['fd_baudrate_configs'].append(fd_baudrate_config)
        else:
            # If no specific controller reference found, add to the last controller or create a default one
            if not self.config_data['controllers']:
                default_controller = {'id': 0, 'baudrate_configs': [], 'fd_baudrate_configs': []}
                self.config_data['controllers'].append(default_controller)
            self.config_data['controllers'][-1]['fd_baudrate_configs'].append(fd_baudrate_config)

    def _find_controller_reference(self, container):
        """Try to find controller reference in the container or its parent"""
        # Look for reference elements that might point to a controller
        refs = container.findall('.//ECUC-REFERENCE-VALUE')
        for ref in refs:
            ref_def = ref.find('DEFINITION-REF')
            if ref_def is not None and 'Controller' in ref_def.text:
                value_ref = ref.find('VALUE-REF')
                if value_ref is not None:
                    # Extract controller ID from reference
                    ref_text = value_ref.text
                    # Try to extract number from reference string
                    import re
                    numbers = re.findall(r'\d+', ref_text)
                    if numbers:
                        return int(numbers[-1])  # Take the last number found
        return None

    def _extract_icom_rx_message_signal_config(self, container, container_name):
        """Extract CanIcomRxMessageSignalConfig containers"""
        signal_config = self._extract_params(container)
        signal_config['container_name'] = container_name
        
        # Initialize icom_signal_configs if it doesn't exist
        if 'icom_signal_configs' not in self.config_data:
            self.config_data['icom_signal_configs'] = []
        
        # Check if we have any ICOM RX messages to associate this signal config with
        if self.config_data['icom_rx_messages']:
            # Add to the last message's signal configs
            if 'signal_configs' not in self.config_data['icom_rx_messages'][-1]:
                self.config_data['icom_rx_messages'][-1]['signal_configs'] = []
            self.config_data['icom_rx_messages'][-1]['signal_configs'].append(signal_config)
        else:
            # Store separately if no parent message found yet
            self.config_data['icom_signal_configs'].append(signal_config)

    def _extract_hw_object_config(self, container, container_name):
        hw_object = self._extract_params(container)
        hw_object['id'] = hw_object.get('CanObjectId', len(self.config_data['hw_objects']))
        self.config_data['hw_objects'].append(hw_object)

    def _extract_hw_filter_config(self, container):
        self.config_data['hw_filters'].append(self._extract_params(container))

    def _extract_main_function_rw_periods(self, container):
        self.config_data['main_function_rw_periods'].append(self._extract_params(container))

    def _extract_icom_general_config(self, container):
        self.config_data['can_icom_general'] = self._extract_params(container)

    def _extract_icom_rx_message_config(self, container, container_name):
        rx_message = self._extract_params(container)
        rx_message['id'] = rx_message.get('CanIcomMessageId', len(self.config_data['icom_rx_messages']))
        rx_message['signal_configs'] = []
        rx_message['container_name'] = container_name
        
        # Look for nested signal configurations within this message
        for sub_container in container.findall('.//ECUC-CONTAINER-VALUE'):
            sub_name_elem = sub_container.find('SHORT-NAME')
            if sub_name_elem is not None and 'SignalConfig' in sub_name_elem.text:
                signal_config = self._extract_params(sub_container)
                signal_config['container_name'] = sub_name_elem.text
                rx_message['signal_configs'].append(signal_config)
        
        self.config_data['icom_rx_messages'].append(rx_message)
        
        # If we have orphaned signal configs, try to associate them
        if 'icom_signal_configs' in self.config_data and self.config_data['icom_signal_configs']:
            rx_message['signal_configs'].extend(self.config_data['icom_signal_configs'])
            # Clear the orphaned configs
            self.config_data['icom_signal_configs'] = []

    def _extract_can_partial_network(self, container):
        self.config_data['can_partial_network'] = self._extract_params(container)

    def _extract_can_pn_frame_data_mask_spec(self, container):
        self.config_data['can_pn_frame_data_mask_spec'].append(self._extract_params(container))

    def _extract_can_tt_controller(self, container):
        self.config_data['can_tt_controller'] = self._extract_params(container)

    def _extract_can_tt_hardware_object_trigger(self, container):
        self.config_data['can_tt_hardware_object_trigger'].append(self._extract_params(container))

    def _extract_can_xl_general(self, container):
        self.config_data['can_xl_general'] = self._extract_params(container)

    def _extract_can_xl_controller(self, container):
        self.config_data['can_xl_controller'] = self._extract_params(container)

    def _extract_can_xl_hardware_object(self, container):
        self.config_data['can_xl_hardware_object'].append(self._extract_params(container))

    def _extract_can_xl_baudrate_config(self, container):
        self.config_data['can_xl_baudrate_config'] = self._extract_params(container)

    def _extract_can_xl_eth_egress_fifo(self, container):
        self.config_data['can_xl_eth_egress_fifo'].append(self._extract_params(container))

    def _extract_params(self, container):
        params = {}
        
        # Extract boolean parameters
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if name_elem is not None and value_elem is not None:
                name = name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1']
                params[name] = value
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if name_elem is not None and value_elem is not None:
                name = name_elem.text
                try:
                    # Try integer first, then float
                    if '.' in value_elem.text:
                        params[name] = float(value_elem.text)
                    else:
                        params[name] = int(value_elem.text)
                except (ValueError, TypeError):
                    params[name] = 0
        
        # Extract textual parameters
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if name_elem is not None and value_elem is not None:
                name = name_elem.text
                params[name] = value_elem.text
        
        # Extract enumeration parameters
        for param in container.findall('.//ECUC-ENUMERATION-PARAM-VALUE'):
            name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if name_elem is not None and value_elem is not None:
                name = name_elem.text
                params[name] = value_elem.text
        
        return params

    def display_configuration(self):
        config_text = "═" * 80 + "\n"
        config_text += "EXTRACTED CONFIGURATION FROM ARXML\n"
        config_text += "═" * 80 + "\n\n"
        
        # Module Information
        config_text += "MODULE INFORMATION\n"
        # config_text += "─" * 40 + "\n"
        config_text += f"  Vendor ID: {self.config_data['vendor_id']}\n"
        config_text += f"  Module ID: {self.config_data['module_id']}\n"
        config_text += f"  Instance ID: {self.config_data['instance_id']}\n"
        config_text += f"  SW Version: {self.config_data['sw_major_version']}.{self.config_data['sw_minor_version']}.{self.config_data['sw_patch_version']}\n"
        config_text += f"  Config Set Enabled: {'Yes' if self.config_data['can_config_set'] else 'No'}\n\n"
        
        # CAN General Configuration
        if self.config_data['can_general']:
            config_text += "CAN GENERAL CONFIGURATION\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['can_general'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # CAN Controllers
        if self.config_data['controllers']:
            config_text += f"CAN CONTROLLERS ({len(self.config_data['controllers'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, controller in enumerate(self.config_data['controllers']):
                config_text += f"  Controller {i} (ID: {controller.get('id', 'N/A')})\n"
                for key, value in controller.items():
                    if key not in ['baudrate_configs', 'fd_baudrate_configs', 'id']:
                        formatted_value = self._format_value(value)
                        config_text += f"    {key}: {formatted_value}\n"
                
                # Baudrate Configurations
                if controller.get('baudrate_configs'):
                    config_text += f"    Baudrate Configs ({len(controller['baudrate_configs'])}):\n"
                    for j, br_config in enumerate(controller['baudrate_configs']):
                        config_text += f"      Config {j}:\n"
                        for br_key, br_value in br_config.items():
                            formatted_value = self._format_value(br_value)
                            config_text += f"        {br_key}: {formatted_value}\n"
                
                # FD Baudrate Configurations
                if controller.get('fd_baudrate_configs'):
                    config_text += f"    FD Baudrate Configs ({len(controller['fd_baudrate_configs'])}):\n"
                    for j, fd_config in enumerate(controller['fd_baudrate_configs']):
                        config_text += f"      FD Config {j}:\n"
                        for fd_key, fd_value in fd_config.items():
                            formatted_value = self._format_value(fd_value)
                            config_text += f"        {fd_key}: {formatted_value}\n"
                config_text += "\n"
        
        # Hardware Objects
        if self.config_data['hw_objects']:
            config_text += f"HARDWARE OBJECTS ({len(self.config_data['hw_objects'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, hw_obj in enumerate(self.config_data['hw_objects']):
                config_text += f"  HW Object {i} (ID: {hw_obj.get('id', 'N/A')})\n"
                for key, value in hw_obj.items():
                    if key != 'id':
                        formatted_value = self._format_value(value)
                        config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # Hardware Filters
        if self.config_data['hw_filters']:
            config_text += f"HARDWARE FILTERS ({len(self.config_data['hw_filters'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, hw_filter in enumerate(self.config_data['hw_filters']):
                config_text += f"  HW Filter {i}\n"
                for key, value in hw_filter.items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # Main Function RW Periods
        if self.config_data['main_function_rw_periods']:
            config_text += f"MAIN FUNCTION RW PERIODS ({len(self.config_data['main_function_rw_periods'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, period in enumerate(self.config_data['main_function_rw_periods']):
                config_text += f"  Period {i}\n"
                for key, value in period.items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # Partial Network Configuration
        if self.config_data['can_partial_network']:
            config_text += "CAN PARTIAL NETWORK\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['can_partial_network'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # PN Frame Data Mask Specifications
        if self.config_data['can_pn_frame_data_mask_spec']:
            config_text += f"PN FRAME DATA MASK SPEC ({len(self.config_data['can_pn_frame_data_mask_spec'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, mask_spec in enumerate(self.config_data['can_pn_frame_data_mask_spec']):
                config_text += f"  Mask Spec {i}\n"
                for key, value in mask_spec.items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # Time Triggered Controller
        if self.config_data['can_tt_controller']:
            config_text += "CAN TT CONTROLLER\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['can_tt_controller'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # TT Hardware Object Triggers
        if self.config_data['can_tt_hardware_object_trigger']:
            config_text += f"TT HARDWARE OBJECT TRIGGERS ({len(self.config_data['can_tt_hardware_object_trigger'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, trigger in enumerate(self.config_data['can_tt_hardware_object_trigger']):
                config_text += f"  Trigger {i}\n"
                for key, value in trigger.items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # CAN XL General
        if self.config_data['can_xl_general']:
            config_text += "CAN XL GENERAL\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['can_xl_general'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # CAN XL Controller
        if self.config_data['can_xl_controller']:
            config_text += "CAN XL CONTROLLER\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['can_xl_controller'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # CAN XL Hardware Objects
        if self.config_data['can_xl_hardware_object']:
            config_text += f"CAN XL HARDWARE OBJECTS ({len(self.config_data['can_xl_hardware_object'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, xl_obj in enumerate(self.config_data['can_xl_hardware_object']):
                config_text += f"  XL HW Object {i}\n"
                for key, value in xl_obj.items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # CAN XL Baudrate Config
        if self.config_data['can_xl_baudrate_config']:
            config_text += "CAN XL BAUDRATE CONFIG\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['can_xl_baudrate_config'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # CAN XL Ethernet Egress FIFO
        if self.config_data['can_xl_eth_egress_fifo']:
            config_text += f"CAN XL ETH EGRESS FIFO ({len(self.config_data['can_xl_eth_egress_fifo'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for i, fifo in enumerate(self.config_data['can_xl_eth_egress_fifo']):
                config_text += f"  FIFO {i}\n"
                for key, value in fifo.items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
                config_text += "\n"
        
        # ICOM Configuration (if enabled)
        if self.config_data['can_icom_enabled']:
            config_text += "CAN ICOM CONFIGURATION\n"
            # config_text += "─" * 40 + "\n"
            config_text += "  ICOM Enabled: Yes\n"
            
            if self.config_data['can_icom_general']:
                config_text += "  ICOM General Configuration:\n"
                for key, value in self.config_data['can_icom_general'].items():
                    formatted_value = self._format_value(value)
                    config_text += f"    {key}: {formatted_value}\n"
            
            if self.config_data['icom_rx_messages']:
                config_text += f"  ICOM RX Messages ({len(self.config_data['icom_rx_messages'])}):\n"
                for i, rx_msg in enumerate(self.config_data['icom_rx_messages']):
                    config_text += f"    Message {i} (ID: {rx_msg.get('id', 'N/A')}):\n"
                    config_text += f"      Container: {rx_msg.get('container_name', 'Unknown')}\n"
                    for key, value in rx_msg.items():
                        if key not in ['signal_configs', 'id', 'container_name']:
                            formatted_value = self._format_value(value)
                            config_text += f"      {key}: {formatted_value}\n"
                    
                    if rx_msg.get('signal_configs'):
                        config_text += f"      Signal Configs ({len(rx_msg['signal_configs'])}):\n"
                        for j, sig_config in enumerate(rx_msg['signal_configs']):
                            config_text += f"        Signal {j}:\n"
                            if 'container_name' in sig_config:
                                config_text += f"          Container: {sig_config['container_name']}\n"
                            for sig_key, sig_value in sig_config.items():
                                if sig_key != 'container_name':
                                    formatted_value = self._format_value(sig_value)
                                    config_text += f"          {sig_key}: {formatted_value}\n"
            
            # Show orphaned signal configs if any
            if self.config_data.get('icom_signal_configs'):
                config_text += f"  Orphaned ICOM Signal Configs ({len(self.config_data['icom_signal_configs'])}):\n"
                for i, sig_config in enumerate(self.config_data['icom_signal_configs']):
                    config_text += f"    Orphaned Signal {i}:\n"
                    for key, value in sig_config.items():
                        formatted_value = self._format_value(value)
                        config_text += f"      {key}: {formatted_value}\n"
            
                        config_text += "\n"
                    if rx_msg.get('signal_configs'):
                        config_text += f"      Signal Configs ({len(rx_msg['signal_configs'])}):\n"
                        for j, sig_config in enumerate(rx_msg['signal_configs']):
                            config_text += f"        Signal {j}:\n"
                            for sig_key, sig_value in sig_config.items():
                                formatted_value = self._format_value(sig_value)
                                config_text += f"          {sig_key}: {formatted_value}\n"
            config_text += "\n"
        
        config_text += "═" * 80 + "\n"
        config_text += "END OF CONFIGURATION\n"
        config_text += "═" * 80 + "\n"

        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')

    def _format_value(self, value):
        """Format configuration values for display"""
        if isinstance(value, bool):
            return "Yes" if value else "No"
        elif isinstance(value, (int, float)):
            return str(value)
        elif isinstance(value, str):
            return f'"{value}"'
        elif value is None:
            return "Not Set"
        else:
            return str(value)

    def generate_can_cfg_h(self):
        if not self.config_data.get('controllers'):
            messagebox.showwarning("Warning", "No CAN controllers configured.")
            return

        arxml_filename = os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'
        generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        content = f"""#ifndef CAN_CFG_H
#define CAN_CFG_H

/**
 * Developer: Aruvi B & Auroshaa A from CreamCollar
 * @file Can_Cfg.h
 * @brief CAN Configuration Header File
 * @details Generated CAN Configuration Header from ARXML
 * 
 * Generated from ARXML: {arxml_filename}
 * Generated on: {generation_date}
 */

#include "Std_Types.h"

/*==================================================================================================
*                              MODULE IDENTIFICATION
==================================================================================================*/
#define CAN_CFG_VENDOR_ID                    ({self.config_data['vendor_id']}U)
#define CAN_CFG_MODULE_ID                    ({self.config_data['module_id']}U)
#define CAN_CFG_INSTANCE_ID                  ({self.config_data['instance_id']}U)

/*==================================================================================================
*                              VERSION INFORMATION
==================================================================================================*/
#define CAN_CFG_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)
#define CAN_CFG_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)
#define CAN_CFG_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)

/*==================================================================================================
*                              CONFIGURATION SET
==================================================================================================*/
#define CAN_CONFIG_SET                       {'STD_ON' if self.config_data['can_config_set'] else 'STD_OFF'}

/*==================================================================================================
*                              CAN GENERAL CONFIGURATION
==================================================================================================*/
"""

        # Add CAN General Configuration
        can_general = self.config_data.get('can_general', {})
        content += f"#define CAN_DEV_ERROR_DETECT                 {'STD_ON' if can_general.get('CanDevErrorDetect', False) else 'STD_OFF'}\n"
        content += f"#define CAN_ENABLE_SECURITY_EVENT_REPORTING  {'STD_ON' if can_general.get('CanEnableSecurityEventReporting', False) else 'STD_OFF'}\n"
        content += f"#define CAN_GLOBAL_TIME_SUPPORT              {'STD_ON' if can_general.get('CanGlobalTimeSupport', False) else 'STD_OFF'}\n"
        content += f"#define CAN_INDEX                            ({can_general.get('CanIndex', 0)}U)\n"
        content += f"#define CAN_LPDU_RECEIVE_CALLOUT_FUNCTION    \"{can_general.get('CanLPduReceiveCalloutFunction', '')}\"\n"
        content += f"#define CAN_MAIN_FUNCTION_BUSOFF_PERIOD      ({can_general.get('CanMainFunctionBusoffPeriod', 100)}U)\n"
        content += f"#define CAN_MAIN_FUNCTION_MODE_PERIOD        ({can_general.get('CanMainFunctionModePeriod', 100)}U)\n"
        content += f"#define CAN_MAIN_FUNCTION_WAKEUP_PERIOD      ({can_general.get('CanMainFunctionWakeupPeriod', 100)}U)\n"
        content += f"#define CAN_MULTIPLEXED_TRANSMISSION         ({can_general.get('CanMultiplexedTransmission', 0)}U)\n"
        content += f"#define CAN_SET_BAUDRATE_API                 {'STD_ON' if can_general.get('CanSetBaudrateApi', False) else 'STD_OFF'}\n"
        content += f"#define CAN_TIMEOUT_DURATION                 ({can_general.get('CanTimeoutDuration', 100)}U)\n"
        content += f"#define CAN_VERSION_INFO_API                 {'STD_ON' if can_general.get('CanVersionInfoApi', True) else 'STD_OFF'}\n"

        content += f"""
/*==================================================================================================
*                              CAN CONTROLLER CONFIGURATION
==================================================================================================*/
#define CAN_CONTROLLER_COUNT                 ({len(self.config_data['controllers'])}U)
#define CAN_HW_OBJECT_COUNT                  ({len(self.config_data['hw_objects'])}U)

"""

        # Add Controller-specific configurations
        for i, controller in enumerate(self.config_data['controllers']):
            controller_id = controller.get('id', i)
            content += f"/* Controller {controller_id} Configuration */\n"
            
            for key, value in controller.items():
                if key not in ['baudrate_configs', 'fd_baudrate_configs', 'id']:
                    if isinstance(value, bool):
                        formatted_value = 'STD_ON' if value else 'STD_OFF'
                    elif isinstance(value, int):
                        formatted_value = f"({value}U)"
                    else:
                        formatted_value = str(value)
                    content += f"#define CAN_CONTROLLER_{controller_id}_{key.upper()}    {formatted_value}\n"
            
            # Add Baudrate configurations
            if controller.get('baudrate_configs'):
                content += f"\n/* Controller {controller_id} Baudrate Configurations */\n"
                for j, br_config in enumerate(controller['baudrate_configs']):
                    br_id = br_config.get('CanControllerBaudRateConfigID', j)
                    for key, value in br_config.items():
                        if isinstance(value, (int, float)):
                            formatted_value = f"({value}U)" if isinstance(value, int) else str(value)
                        else:
                            formatted_value = str(value)
                        content += f"#define CAN_CTRL_{controller_id}_BR_{br_id}_{key.upper()}    {formatted_value}\n"
            
            # Add FD Baudrate configurations
            if controller.get('fd_baudrate_configs'):
                content += f"\n/* Controller {controller_id} FD Baudrate Configurations */\n"
                for j, fd_config in enumerate(controller['fd_baudrate_configs']):
                    fd_id = fd_config.get('CanControllerFdBaudRateConfigID', j)
                    for key, value in fd_config.items():
                        if isinstance(value, bool):
                            formatted_value = 'STD_ON' if value else 'STD_OFF'
                        elif isinstance(value, (int, float)):
                            formatted_value = f"({value}U)" if isinstance(value, int) else str(value)
                        else:
                            formatted_value = str(value)
                        content += f"#define CAN_CTRL_{controller_id}_FD_BR_{fd_id}_{key.upper()}    {formatted_value}\n"
            content += "\n"

        # Add Hardware Object configurations
        if self.config_data['hw_objects']:
            content += """/*==================================================================================================
*                              CAN HARDWARE OBJECT CONFIGURATION
==================================================================================================*/
"""
            for i, hw_obj in enumerate(self.config_data['hw_objects']):
                obj_id = hw_obj.get('id', i)
                content += f"/* Hardware Object {obj_id} Configuration */\n"
                for key, value in hw_obj.items():
                    if key != 'id':
                        if isinstance(value, bool):
                            formatted_value = 'STD_ON' if value else 'STD_OFF'
                        elif isinstance(value, int):
                            formatted_value = f"({value}U)"
                        else:
                            formatted_value = str(value)
                        content += f"#define CAN_HW_OBJ_{obj_id}_{key.upper()}    {formatted_value}\n"
                content += "\n"

        # Add Hardware Filter configurations
        if self.config_data['hw_filters']:
            content += """/*==================================================================================================
*                              CAN HARDWARE FILTER CONFIGURATION
==================================================================================================*/
"""
            for i, hw_filter in enumerate(self.config_data['hw_filters']):
                content += f"/* Hardware Filter {i} Configuration */\n"
                for key, value in hw_filter.items():
                    if isinstance(value, (int, float)):
                        formatted_value = f"({value}U)" if isinstance(value, int) else str(value)
                    else:
                        formatted_value = str(value)
                    content += f"#define CAN_HW_FILTER_{i}_{key.upper()}    {formatted_value}\n"
                content += "\n"

        # Add Partial Network configurations
        if self.config_data['can_partial_network']:
            content += """/*==================================================================================================
*                              CAN PARTIAL NETWORK CONFIGURATION
==================================================================================================*/
"""
            for key, value in self.config_data['can_partial_network'].items():
                if isinstance(value, bool):
                    formatted_value = 'STD_ON' if value else 'STD_OFF'
                elif isinstance(value, int):
                    formatted_value = f"({value}U)"
                else:
                    formatted_value = str(value)
                content += f"#define CAN_PN_{key.upper()}    {formatted_value}\n"
            content += "\n"

        # Add Time Triggered configurations
        if self.config_data['can_tt_controller']:
            content += """/*==================================================================================================
*                              CAN TIME TRIGGERED CONFIGURATION
==================================================================================================*/
"""
            for key, value in self.config_data['can_tt_controller'].items():
                if isinstance(value, bool):
                    formatted_value = 'STD_ON' if value else 'STD_OFF'
                elif isinstance(value, int):
                    formatted_value = f"({value}U)"
                else:
                    formatted_value = str(value)
                content += f"#define CAN_TT_{key.upper()}    {formatted_value}\n"
            content += "\n"

        # Add CAN XL configurations
        if self.config_data['can_xl_general']:
            content += """/*==================================================================================================
*                              CAN XL CONFIGURATION
==================================================================================================*/
"""
            for key, value in self.config_data['can_xl_general'].items():
                if isinstance(value, bool):
                    formatted_value = 'STD_ON' if value else 'STD_OFF'
                elif isinstance(value, int):
                    formatted_value = f"({value}U)"
                else:
                    formatted_value = str(value)
                content += f"#define CAN_XL_{key.upper()}    {formatted_value}\n"
            content += "\n"

        # Add ICOM configurations
        if self.config_data['can_icom_enabled']:
            content += """/*==================================================================================================
*                              CAN ICOM CONFIGURATION
==================================================================================================*/
#define CAN_ICOM_SUPPORT                     STD_ON
"""
            if self.config_data['can_icom_general']:
                content += "/* ICOM General Configuration */\n"
                for key, value in self.config_data['can_icom_general'].items():
                    if isinstance(value, bool):
                        formatted_value = 'STD_ON' if value else 'STD_OFF'
                    elif isinstance(value, int):
                        formatted_value = f"({value}U)"
                    else:
                        formatted_value = f'"{value}"' if isinstance(value, str) else str(value)
                    content += f"#define CAN_ICOM_{key.upper()}    {formatted_value}\n"
                content += "\n"
            
            if self.config_data['icom_rx_messages']:
                content += f"#define CAN_ICOM_RX_MESSAGE_COUNT            ({len(self.config_data['icom_rx_messages'])}U)\n\n"
                for i, rx_msg in enumerate(self.config_data['icom_rx_messages']):
                    msg_id = rx_msg.get('id', i)
                    content += f"/* ICOM RX Message {msg_id} Configuration */\n"
                    for key, value in rx_msg.items():
                        if key not in ['signal_configs', 'id', 'container_name']:
                            if isinstance(value, bool):
                                formatted_value = 'STD_ON' if value else 'STD_OFF'
                            elif isinstance(value, int):
                                formatted_value = f"({value}U)"
                            else:
                                formatted_value = f'"{value}"' if isinstance(value, str) else str(value)
                            content += f"#define CAN_ICOM_RX_MSG_{msg_id}_{key.upper()}    {formatted_value}\n"
                    
                    # Add signal configurations
                    if rx_msg.get('signal_configs'):
                        content += f"#define CAN_ICOM_RX_MSG_{msg_id}_SIGNAL_COUNT    ({len(rx_msg['signal_configs'])}U)\n"
                        for j, sig_config in enumerate(rx_msg['signal_configs']):
                            content += f"/* ICOM RX Message {msg_id} Signal {j} Configuration */\n"
                            for sig_key, sig_value in sig_config.items():
                                if sig_key != 'container_name':
                                    if isinstance(sig_value, bool):
                                        formatted_value = 'STD_ON' if sig_value else 'STD_OFF'
                                    elif isinstance(sig_value, int):
                                        formatted_value = f"({sig_value}U)"
                                    else:
                                        formatted_value = f'"{sig_value}"' if isinstance(sig_value, str) else str(sig_value)
                                    content += f"#define CAN_ICOM_RX_MSG_{msg_id}_SIG_{j}_{sig_key.upper()}    {formatted_value}\n"
                    content += "\n"
            
            content += "\n"

        content += """/*==================================================================================================
*                              FUNCTION DECLARATIONS
==================================================================================================*/
extern const Can_ConfigType Can_Config;

#endif /* CAN_CFG_H */
"""
        
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        self.status_var.set("CAN_CFG.H generated successfully")

    def save_driver_files(self):
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
            
        directory_path = filedialog.askdirectory(title="Select Directory to Save Driver Files")
        if not directory_path: 
            return
            
        try:
            os.makedirs(directory_path, exist_ok=True) # Added this line
            
            can_cfg_h_content = self.code_text.get(1.0, tk.END)
            generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            can_h_content = CAN_H_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            can_c_content = CAN_C_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            
            files_to_save = [
                ('Can_Cfg.h', can_cfg_h_content),
                ('Can.h', can_h_content),
                ('Can.c', can_c_content),
            ]

            for filename, content in files_to_save:
                with open(os.path.join(directory_path, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
            
            messagebox.showinfo("Success", f"CAN driver files saved successfully to:\n{directory_path}")
            self.status_var.set("Driver files saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save files: {str(e)}")
            self.status_var.set("Error saving files")

def main():
    root = tk.Tk()
    root.title("ARXML to CAN Config Converter")
    root.geometry("1200x800")
    
    app = ARXMLtoCANGenerator(root)
    app.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == '__main__':
    main()