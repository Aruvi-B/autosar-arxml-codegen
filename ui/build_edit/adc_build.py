# adc_build.py

import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from .drivers.adc_code import ADC_H_TEMPLATE, ADC_C_TEMPLATE

class ARXMLtoADCGenerator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.config_data = self.get_default_config()
        
        self.arxml_file_path = None
        self.status_var = tk.StringVar(value="Ready")
        self.setup_ui()

    def get_default_config(self):
        return {
            'vendor_id': 1810,
            'module_id': 123,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            # AdcGeneral parameters
            'adc_general': {},
            'adc_deinit_api': True,
            'adc_dev_error_detect': True,
            'adc_enable_limit_check': False,
            'adc_enable_queuing': False,
            'adc_enable_start_stop_group_api': True,
            'adc_grp_notif_capability': True,
            'adc_hw_trigger_api': True,
            'adc_low_power_states_support': False,
            'adc_power_state_asynch_transition_mode': False,
            'adc_read_group_api': True,
            'adc_version_info_api': True,
            'adc_priority_implementation': 'ADC_PRIORITY_NONE',
            'adc_result_alignment': 'ADC_ALIGN_LEFT',
            # AdcConfigSet parameters
            'adc_hw_unit': 0,
            'channels': [],
            'groups': [],
            'published_information': {},
            'power_state_configs': [],
            'hw_units': []
        }

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title_label = ttk.Label(self, text="ARXML to ADC Driver Generator", 
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

        self.generate_btn = ttk.Button(buttons_frame, text="Generate ADC_CFG.H", command=self.generate_adc_cfg_h)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(buttons_frame, text="Save Driver Files", command=self.save_driver_files)
        self.save_btn.pack(side=tk.LEFT)

        code_frame = ttk.LabelFrame(right_frame, text="Generated Adc_Cfg.h", padding="10")
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
                self.generate_adc_cfg_h()
            else:
                self.status_var.set("Warning: Limited configuration found")
                messagebox.showwarning("Warning", "ARXML parsed but limited ADC configuration found. Please verify the file structure.")
            
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

            if 'AdcGeneral' in short_name:
                config_found = True
                self._extract_general_config(container)
            elif 'AdcConfigSet' in short_name:
                config_found = True
                self._extract_config_set(container)
            elif 'AdcChannel' in short_name:
                config_found = True
                self._extract_channel_config(container, short_name)
            elif 'AdcGroup' in short_name:
                config_found = True
                self._extract_group_config(container, short_name)
            elif 'AdcPublishedInformation' in short_name:
                config_found = True
                self._extract_published_information(container)
            elif 'AdcPowerStateConfig' in short_name:
                config_found = True
                self._extract_power_state_config(container, short_name)
            elif 'AdcHwUnit' in short_name:
                config_found = True
                self._extract_hw_unit_config(container, short_name)
        
        return config_found

    def _extract_general_config(self, container):
        """Extract AdcGeneral configuration"""
        adc_general = {}
        
        # Extract boolean parameters
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                
                # Store in adc_general for display
                adc_general[param_name] = value
                
                # Also update main config for backward compatibility
                bool_mapping = {
                    'AdcDeInitApi': 'adc_deinit_api',
                    'AdcDevErrorDetect': 'adc_dev_error_detect',
                    'AdcEnableLimitCheck': 'adc_enable_limit_check',
                    'AdcEnableQueuing': 'adc_enable_queuing',
                    'AdcEnableStartStopGroupApi': 'adc_enable_start_stop_group_api',
                    'AdcGrpNotifCapability': 'adc_grp_notif_capability',
                    'AdcHwTriggerApi': 'adc_hw_trigger_api',
                    'AdcLowPowerStatesSupport': 'adc_low_power_states_support',
                    'AdcPowerStateAsynchTransitionMode': 'adc_power_state_asynch_transition_mode',
                    'AdcReadGroupApi': 'adc_read_group_api',
                    'AdcVersionInfoApi': 'adc_version_info_api'
                }
                
                if param_name in bool_mapping:
                    self.config_data[bool_mapping[param_name]] = value

        # Extract enumeration parameters
        for param in container.findall('.//ECUC-ENUMERATION-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text
                
                # Store in adc_general for display
                adc_general[param_name] = value
                
                if param_name == 'AdcPriorityImplementation':
                    self.config_data['adc_priority_implementation'] = value
                elif param_name == 'AdcResultAlignment':
                    self.config_data['adc_result_alignment'] = value
        
        self.config_data['adc_general'] = adc_general

    def _extract_config_set(self, container):
        """Extract AdcConfigSet configuration"""
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if param_name == 'AdcHwUnit':
                    self.config_data['adc_hw_unit'] = int(value_elem.text)

    def _extract_channel_config(self, container, container_name):
        """Extract AdcChannel configuration"""
        channel_id = None
        channel_symbolic_name = None
        channel_config = {
            'conv_time': 100,
            'high_limit': 4095,
            'low_limit': 0,
            'limit_check': False,
            'range_select': 'ADC_RANGE_UNDER_LOW',
            'ref_voltsrc_high': False,
            'ref_voltsrc_low': False,
            'resolution': 12,
            'samp_time': 10,
            'container_name': container_name
        }
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                try:
                    value = int(value_elem.text)
                    if param_name == 'AdcChannelId':
                        channel_id = value
                    elif param_name == 'AdcChannelConvTime':
                        channel_config['conv_time'] = value
                    elif param_name == 'AdcChannelHighLimit':
                        channel_config['high_limit'] = value
                    elif param_name == 'AdcChannelLowLimit':
                        channel_config['low_limit'] = value
                    elif param_name == 'AdcChannelResolution':
                        channel_config['resolution'] = value
                    elif param_name == 'AdcChannelSampTime':
                        channel_config['samp_time'] = value
                except ValueError:
                    continue

        # Extract textual parameters
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if param_name == 'AdcChannelSymbolicName':
                    channel_symbolic_name = value_elem.text

        # Extract boolean parameters
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                if param_name == 'AdcChannelLimitCheck':
                    channel_config['limit_check'] = value
                elif param_name == 'AdcChannelRefVoltsrcHigh':
                    channel_config['ref_voltsrc_high'] = value
                elif param_name == 'AdcChannelRefVoltsrcLow':
                    channel_config['ref_voltsrc_low'] = value

        # Extract enumeration parameters
        for param in container.findall('.//ECUC-ENUMERATION-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if param_name == 'AdcChannelRangeSelect':
                    channel_config['range_select'] = value_elem.text

        # If no channel ID found, try to extract from container name
        if channel_id is None:
            import re
            match = re.search(r'(\d+)', container_name)
            channel_id = int(match.group(1)) if match else len(self.config_data['channels'])

        if channel_id is not None:
            channel_config.update({
                'id': channel_id,
                'symbolic_name': channel_symbolic_name or f'ADC_CHANNEL_{channel_id}'
            })
            self.config_data['channels'].append(channel_config)

    def _extract_group_config(self, container, container_name):
        """Extract AdcGroup configuration"""
        group_id = None
        group_config = {
            'access_mode': 'ADC_ACCESS_MODE_SINGLE',
            'conversion_mode': 'ADC_CONV_MODE_ONESHOT',
            'priority': 0,
            'replacement': 'ADC_GROUP_REPL_ABORT_RESTART',
            'trigg_src': 'ADC_TRIGG_SRC_SW',
            'hw_trigg_signal': 'ADC_HW_TRIG_RISING_EDGE',
            'hw_trigg_timer': 0,
            'notification': False,
            'streaming_buffer_mode': 'ADC_STREAM_BUFFER_LINEAR',
            'streaming_num_samples': 1,
            'group_definition': [],
            'container_name': container_name
        }
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                try:
                    value = int(value_elem.text)
                    if param_name == 'AdcGroupId':
                        group_id = value
                    elif param_name == 'AdcGroupPriority':
                        group_config['priority'] = value
                    elif param_name == 'AdcStreamingNumSamples':
                        group_config['streaming_num_samples'] = value
                    elif param_name == 'AdcHwTrigTimer':
                        group_config['hw_trigg_timer'] = value
                    elif param_name == 'AdcGroupDefinition':
                        group_config['group_definition'].append(value)
                except ValueError:
                    continue

        # Extract boolean parameters
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                if param_name == 'AdcNotification':
                    group_config['notification'] = value

        # Extract enumeration parameters
        for param in container.findall('.//ECUC-ENUMERATION-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text
                enum_mapping = {
                    'AdcGroupAccessMode': 'access_mode',
                    'AdcGroupConversionMode': 'conversion_mode',
                    'AdcGroupReplacement': 'replacement',
                    'AdcGroupTriggSrc': 'trigg_src',
                    'AdcHwTrigSignal': 'hw_trigg_signal',
                    'AdcStreamingBufferMode': 'streaming_buffer_mode'
                }
                if param_name in enum_mapping:
                    group_config[enum_mapping[param_name]] = value

        # If no group ID found, try to extract from container name
        if group_id is None:
            import re
            match = re.search(r'(\d+)', container_name)
            group_id = int(match.group(1)) if match else len(self.config_data['groups'])

        if group_id is not None:
            group_config['id'] = group_id
            self.config_data['groups'].append(group_config)

    def _extract_published_information(self, container):
        """Extract AdcPublishedInformation configuration"""
        published_info = {}
        
        # Extract boolean parameters
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                published_info[param_name] = value
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                try:
                    published_info[param_name] = int(value_elem.text)
                except ValueError:
                    continue
        
        self.config_data['published_information'] = published_info

    def _extract_power_state_config(self, container, container_name):
        """Extract AdcPowerStateConfig configuration"""
        power_state_config = {'container_name': container_name}
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if param_name == 'AdcPowerState':
                    try:
                        power_state_config['power_state'] = int(value_elem.text)
                    except ValueError:
                        continue
        
        # Extract textual parameters
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if param_name == 'AdcPowerStateReadyCbkRef':
                    power_state_config['ready_callback_ref'] = value_elem.text
        
        self.config_data['power_state_configs'].append(power_state_config)

    def _extract_hw_unit_config(self, container, container_name):
        """Extract AdcHwUnit configuration"""
        hw_unit_config = {'container_name': container_name}
        
        # Extract boolean parameters
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                if param_name == 'AdcClockSource':
                    hw_unit_config['clock_source'] = value
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                try:
                    value = int(value_elem.text)
                    if param_name == 'AdcHwUnitId':
                        hw_unit_config['hw_unit_id'] = value
                    elif param_name == 'AdcPrescale':
                        hw_unit_config['prescale'] = value
                except ValueError:
                    continue
        
        self.config_data['hw_units'].append(hw_unit_config)

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

    def display_configuration(self):
        """Display extracted configuration in structured format"""
        config_text = "=" * 80 + "\n"
        config_text += "EXTRACTED ADC CONFIGURATION FROM ARXML\n"
        config_text += "=" * 80 + "\n\n"
        
        # Module Information
        config_text += "MODULE INFORMATION\n"
        config_text += "-" * 40 + "\n"
        config_text += f"  Vendor ID: {self.config_data['vendor_id']}\n"
        config_text += f"  Module ID: {self.config_data['module_id']}\n"
        config_text += f"  Instance ID: {self.config_data['instance_id']}\n"
        config_text += f"  SW Version: {self.config_data['sw_major_version']}.{self.config_data['sw_minor_version']}.{self.config_data['sw_patch_version']}\n\n"
        
        # ADC Config Set
        config_text += "ADC CONFIG SET\n"
        config_text += "-" * 40 + "\n"
        config_text += f"  ADC HW Unit: {self.config_data['adc_hw_unit']}\n\n"
        
        # ADC General Configuration
        if self.config_data['adc_general']:
            config_text += "ADC GENERAL CONFIGURATION\n"
            config_text += "-" * 40 + "\n"
            for key, value in self.config_data['adc_general'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        
        # ADC Channels
        if self.config_data['channels']:
            config_text += f"ADC CHANNELS ({len(self.config_data['channels'])} found)\n"
            config_text += "-" * 40 + "\n"
            for channel in self.config_data['channels']:
                config_text += f"  Channel {channel['id']}:\n"
                config_text += f"    Symbolic Name: {channel['symbolic_name']}\n"
                config_text += f"    Resolution: {channel['resolution']} bits\n"
                config_text += f"    Conversion Time: {channel['conv_time']}\n"
                config_text += f"    Sample Time: {channel['samp_time']}\n"
                config_text += f"    High Limit: {channel['high_limit']}\n"
                config_text += f"    Low Limit: {channel['low_limit']}\n"
                config_text += f"    Limit Check: {self._format_value(channel['limit_check'])}\n"
                config_text += f"    Range Select: {channel['range_select']}\n"
                config_text += f"    Ref Volt Src High: {self._format_value(channel['ref_voltsrc_high'])}\n"
                config_text += f"    Ref Volt Src Low: {self._format_value(channel['ref_voltsrc_low'])}\n"
                
            config_text += "\n"
        else:
            config_text += "ADC CHANNELS\n"
            config_text += "-" * 40 + "\n"
            config_text += "  No channels configured\n\n"
        
        # ADC Groups
        if self.config_data['groups']:
            config_text += f"ADC GROUPS ({len(self.config_data['groups'])} found)\n"
            config_text += "-" * 40 + "\n"
            for group in self.config_data['groups']:
                config_text += f"  Group {group['id']}:\n"
                config_text += f"    Access Mode: {group['access_mode']}\n"
                config_text += f"    Conversion Mode: {group['conversion_mode']}\n"
                config_text += f"    Priority: {group['priority']}\n"
                config_text += f"    Replacement: {group['replacement']}\n"
                config_text += f"    Trigger Source: {group['trigg_src']}\n"
                config_text += f"    HW Trigger Signal: {group['hw_trigg_signal']}\n"
                config_text += f"    HW Trigger Timer: {group['hw_trigg_timer']}\n"
                config_text += f"    Notification: {self._format_value(group['notification'])}\n"
                config_text += f"    Streaming Buffer Mode: {group['streaming_buffer_mode']}\n"
                config_text += f"    Streaming Num Samples: {group['streaming_num_samples']}\n"
                if group['group_definition']:
                    config_text += f"    Group Definition: {group['group_definition']}\n"
                config_text += f"    Container: {group.get('container_name', 'Unknown')}\n"
            config_text += "\n"
        else:
            config_text += "ADC GROUPS\n"
            config_text += "-" * 40 + "\n"
            config_text += "  No groups configured\n\n"
        
        # ADC Published Information
        if self.config_data['published_information']:
            config_text += "ADC PUBLISHED INFORMATION\n"
            config_text += "-" * 40 + "\n"
            for key, value in self.config_data['published_information'].items():
                formatted_value = self._format_value(value)
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # ADC Power State Configurations
        if self.config_data['power_state_configs']:
            config_text += f"ADC POWER STATE CONFIGS ({len(self.config_data['power_state_configs'])} found)\n"
            config_text += "-" * 40 + "\n"
            for i, power_config in enumerate(self.config_data['power_state_configs']):
                config_text += f"  Power State Config {i}:\n"
                if 'power_state' in power_config:
                    config_text += f"    Power State: {power_config['power_state']}\n"
                if 'ready_callback_ref' in power_config:
                    config_text += f"    Ready Callback Ref: {power_config['ready_callback_ref']}\n"
                config_text += f"    Container: {power_config.get('container_name', 'Unknown')}\n"
            config_text += "\n"
        
        # ADC Hardware Units
        if self.config_data['hw_units']:
            config_text += f"ADC HARDWARE UNITS ({len(self.config_data['hw_units'])} found)\n"
            config_text += "-" * 40 + "\n"
            for i, hw_unit in enumerate(self.config_data['hw_units']):
                config_text += f"  HW Unit {i}:\n"
                if 'hw_unit_id' in hw_unit:
                    config_text += f"    HW Unit ID: {hw_unit['hw_unit_id']}\n"
                if 'clock_source' in hw_unit:
                    config_text += f"    Clock Source: {self._format_value(hw_unit['clock_source'])}\n"
                if 'prescale' in hw_unit:
                    config_text += f"    Prescale: {hw_unit['prescale']}\n"
                config_text += f"    Container: {hw_unit.get('container_name', 'Unknown')}\n"
            config_text += "\n"
        
        # Validation Status
        config_text += "VALIDATION STATUS\n"
        config_text += "-" * 40 + "\n"
        if not self.config_data['channels'] and not self.config_data['groups']:
            config_text += "  WARNING: No ADC configuration found\n"
        else:
            config_text += "  Configuration extracted successfully\n"
        
        config_text += "\n" + "=" * 80 + "\n"
        config_text += "END OF CONFIGURATION\n"
        config_text += "=" * 80 + "\n"
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')

    def generate_adc_cfg_h(self):
        """Generate ADC_CFG.H file content"""
        if not self.config_data['channels'] and not self.config_data['groups']:
            messagebox.showwarning("Warning", "No ADC configuration available.")
            return

        arxml_filename = os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'
        generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')

        content = f"""#ifndef ADC_CFG_H
#define ADC_CFG_H

/**
 * Developer Aruvi B & Auroshaa A from CreamCollar
 * @file Adc_Cfg.h
 * @brief ADC Configuration Header File
 * @details Generated ADC Configuration Header from ARXML
 * 
 * Generated from ARXML: {arxml_filename}
 * Generated on: {generation_date}
 */

#include "Std_Types.h"

/*==================================================================================================
*                              MODULE IDENTIFICATION
==================================================================================================*/
#define ADC_CFG_VENDOR_ID                    ({self.config_data['vendor_id']}U)
#define ADC_CFG_MODULE_ID                    ({self.config_data['module_id']}U)
#define ADC_CFG_INSTANCE_ID                  ({self.config_data['instance_id']}U)

/*==================================================================================================
*                              VERSION INFORMATION
==================================================================================================*/
#define ADC_CFG_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)
#define ADC_CFG_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)
#define ADC_CFG_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)

/*==================================================================================================
*                              ADC GENERAL CONFIGURATION
==================================================================================================*/
#define ADC_DEINIT_API                       {'STD_ON' if self.config_data['adc_deinit_api'] else 'STD_OFF'}
#define ADC_DEV_ERROR_DETECT                 {'STD_ON' if self.config_data['adc_dev_error_detect'] else 'STD_OFF'}
#define ADC_ENABLE_LIMIT_CHECK               {'STD_ON' if self.config_data['adc_enable_limit_check'] else 'STD_OFF'}
#define ADC_ENABLE_QUEUING                   {'STD_ON' if self.config_data['adc_enable_queuing'] else 'STD_OFF'}
#define ADC_ENABLE_START_STOP_GROUP_API      {'STD_ON' if self.config_data['adc_enable_start_stop_group_api'] else 'STD_OFF'}
#define ADC_GRP_NOTIF_CAPABILITY             {'STD_ON' if self.config_data['adc_grp_notif_capability'] else 'STD_OFF'}
#define ADC_HW_TRIGGER_API                   {'STD_ON' if self.config_data['adc_hw_trigger_api'] else 'STD_OFF'}
#define ADC_LOW_POWER_STATES_SUPPORT         {'STD_ON' if self.config_data['adc_low_power_states_support'] else 'STD_OFF'}
#define ADC_POWER_STATE_ASYNCH_TRANSITION_MODE {'STD_ON' if self.config_data['adc_power_state_asynch_transition_mode'] else 'STD_OFF'}
#define ADC_READ_GROUP_API                   {'STD_ON' if self.config_data['adc_read_group_api'] else 'STD_OFF'}
#define ADC_VERSION_INFO_API                 {'STD_ON' if self.config_data['adc_version_info_api'] else 'STD_OFF'}

/*==================================================================================================
*                              ADC PRIORITY AND ALIGNMENT CONFIGURATION
==================================================================================================*/
#define ADC_PRIORITY_IMPLEMENTATION          {self.config_data['adc_priority_implementation']}
#define ADC_RESULT_ALIGNMENT                 {self.config_data['adc_result_alignment']}

/*==================================================================================================
*                              ADC HARDWARE CONFIGURATION
==================================================================================================*/
#define ADC_HW_UNIT                          ({self.config_data['adc_hw_unit']}U)

/*==================================================================================================
*                              CONFIGURATION COUNTS
==================================================================================================*/
#define ADC_CHANNEL_COUNT                    ({len(self.config_data['channels'])}U)
#define ADC_GROUP_COUNT                      ({len(self.config_data['groups'])}U)
#define ADC_HW_UNIT_COUNT                    ({len(self.config_data['hw_units'])}U)

"""

        # Add Channel Symbolic Names and Configuration
        if self.config_data['channels']:
            content += """/*==================================================================================================
*                              ADC CHANNEL SYMBOLIC NAMES
==================================================================================================*/
"""
            for channel in self.config_data['channels']:
                content += f"#define {channel['symbolic_name']:<40} ({channel['id']}U)\n"
            
            content += """
/*==================================================================================================
*                              ADC CHANNEL CONFIGURATION DETAILS
==================================================================================================*/
"""
            for channel in self.config_data['channels']:
                content += f"#define {channel['symbolic_name']}_CONV_TIME        ({channel['conv_time']}U)\n"
                content += f"#define {channel['symbolic_name']}_HIGH_LIMIT       ({channel['high_limit']}U)\n"
                content += f"#define {channel['symbolic_name']}_LIMIT_CHECK      {'STD_ON' if channel['limit_check'] else 'STD_OFF'}\n"
                content += f"#define {channel['symbolic_name']}_LOW_LIMIT        ({channel['low_limit']}U)\n"
                content += f"#define {channel['symbolic_name']}_RANGE_SELECT     {channel['range_select']}\n"
                content += f"#define {channel['symbolic_name']}_REF_VOLT_HIGH    {'STD_ON' if channel['ref_voltsrc_high'] else 'STD_OFF'}\n"
                content += f"#define {channel['symbolic_name']}_REF_VOLT_LOW     {'STD_ON' if channel['ref_voltsrc_low'] else 'STD_OFF'}\n"
                content += f"#define {channel['symbolic_name']}_RESOLUTION       ({channel['resolution']}U)\n"
                content += f"#define {channel['symbolic_name']}_SAMP_TIME        ({channel['samp_time']}U)\n"
                content += "\n"

        # Add Group Symbolic Names and Configuration
        if self.config_data['groups']:
            content += """/*==================================================================================================
*                              ADC GROUP SYMBOLIC NAMES
==================================================================================================*/
"""
            for group in self.config_data['groups']:
                content += f"#define ADC_GROUP_{group['id']:<30} ({group['id']}U)\n"
            
            content += """
/*==================================================================================================
*                              ADC GROUP CONFIGURATION DETAILS
==================================================================================================*/
"""
            for group in self.config_data['groups']:
                content += f"#define ADC_GROUP_{group['id']}_ACCESS_MODE          {group['access_mode']}\n"
                content += f"#define ADC_GROUP_{group['id']}_CONVERSION_MODE      {group['conversion_mode']}\n"
                content += f"#define ADC_GROUP_{group['id']}_PRIORITY             ({group['priority']}U)\n"
                content += f"#define ADC_GROUP_{group['id']}_REPLACEMENT          {group['replacement']}\n"
                content += f"#define ADC_GROUP_{group['id']}_TRIGGER_SRC          {group['trigg_src']}\n"
                content += f"#define ADC_GROUP_{group['id']}_NUM_SAMPLES          ({group['streaming_num_samples']}U)\n"
                content += f"#define ADC_GROUP_{group['id']}_HW_TRIGGER_SIGNAL    {group['hw_trigg_signal']}\n"
                content += f"#define ADC_GROUP_{group['id']}_HW_TRIGGER_TIMER     ({group['hw_trigg_timer']}U)\n"
                content += f"#define ADC_GROUP_{group['id']}_NOTIFICATION         {'STD_ON' if group['notification'] else 'STD_OFF'}\n"
                content += f"#define ADC_GROUP_{group['id']}_STREAM_BUFFER_MODE   {group['streaming_buffer_mode']}\n"
                content += "\n"

        # Add Published Information
        if self.config_data['published_information']:
            content += """/*==================================================================================================
*                              ADC PUBLISHED INFORMATION
==================================================================================================*/
"""
            for key, value in self.config_data['published_information'].items():
                if isinstance(value, bool):
                    formatted_value = 'STD_ON' if value else 'STD_OFF'
                else:
                    formatted_value = f"({value}U)"
                content += f"#define ADC_{key.upper():<35} {formatted_value}\n"
            content += "\n"

        # Add Hardware Unit Configuration
        if self.config_data['hw_units']:
            content += """/*==================================================================================================
*                              ADC HARDWARE UNIT CONFIGURATION
==================================================================================================*/
"""
            for i, hw_unit in enumerate(self.config_data['hw_units']):
                if 'hw_unit_id' in hw_unit:
                    content += f"#define ADC_HW_UNIT_{i}_ID                   ({hw_unit['hw_unit_id']}U)\n"
                if 'clock_source' in hw_unit:
                    content += f"#define ADC_HW_UNIT_{i}_CLOCK_SOURCE         {'STD_ON' if hw_unit['clock_source'] else 'STD_OFF'}\n"
                if 'prescale' in hw_unit:
                    content += f"#define ADC_HW_UNIT_{i}_PRESCALE             ({hw_unit['prescale']}U)\n"
                content += "\n"

        # Add DET Error Codes
        content += """/*==================================================================================================
*                              DET ERROR CODES
==================================================================================================*/
#define ADC_E_UNINIT                         (0x0AU)
#define ADC_E_BUSY                           (0x0BU)
#define ADC_E_IDLE                           (0x0CU)
#define ADC_E_ALREADY_INITIALIZED            (0x0DU)
#define ADC_E_PARAM_CONFIG                   (0x0EU)
#define ADC_E_PARAM_POINTER                  (0x14U)
#define ADC_E_PARAM_GROUP                    (0x15U)
#define ADC_E_WRONG_CONV_MODE                (0x16U)
#define ADC_E_WRONG_TRIGG_SRC                (0x17U)
#define ADC_E_NOTIF_CAPABILITY               (0x18U)
#define ADC_E_BUFFER_UNINIT                  (0x19U)

/*==================================================================================================
*                              SERVICE IDS
==================================================================================================*/
#define ADC_INIT_SID                         (0x00U)
#define ADC_DEINIT_SID                       (0x01U)
#define ADC_START_GROUP_CONVERSION_SID       (0x02U)
#define ADC_STOP_GROUP_CONVERSION_SID        (0x03U)
#define ADC_READ_GROUP_SID                   (0x04U)
#define ADC_ENABLE_HARDWARE_TRIGGER_SID      (0x05U)
#define ADC_DISABLE_HARDWARE_TRIGGER_SID     (0x06U)
#define ADC_ENABLE_GROUP_NOTIFICATION_SID    (0x07U)
#define ADC_DISABLE_GROUP_NOTIFICATION_SID   (0x08U)
#define ADC_GET_GROUP_STATUS_SID             (0x09U)
#define ADC_GET_VERSION_INFO_SID             (0x0AU)
#define ADC_GET_STREAM_LAST_POINTER_SID      (0x0BU)
#define ADC_SETUP_RESULT_BUFFER_SID          (0x0CU)

/*==================================================================================================
*                              TYPE DEFINITIONS
==================================================================================================*/
typedef uint16_t Adc_ChannelType;
typedef uint16_t Adc_GroupType;
typedef uint16_t Adc_ValueGroupType;

typedef enum {{
    ADC_IDLE = 0U,
    ADC_BUSY,
    ADC_COMPLETED,
    ADC_STREAM_COMPLETED
}} Adc_StatusType;

typedef enum {{
    ADC_TRIGG_SRC_SW = 0U,
    ADC_TRIGG_SRC_HW
}} Adc_TriggerSourceType;

typedef enum {{
    ADC_ACCESS_MODE_SINGLE = 0U,
    ADC_ACCESS_MODE_STREAMING
}} Adc_GroupAccessModeType;

typedef enum {{
    ADC_CONV_MODE_ONESHOT = 0U,
    ADC_CONV_MODE_CONTINUOUS
}} Adc_GroupConvModeType;

typedef struct {{
    /* Channel configuration structure */
    Adc_ChannelType channelId;
    uint16_t resolution;
    uint16_t conversionTime;
    uint16_t samplingTime;
    uint16_t highLimit;
    uint16_t lowLimit;
    boolean limitCheckEnabled;
}} Adc_ChannelConfigType;

typedef struct {{
    /* Group configuration structure */
    Adc_GroupType groupId;
    Adc_GroupAccessModeType accessMode;
    Adc_GroupConvModeType conversionMode;
    uint8_t priority;
    Adc_TriggerSourceType triggerSource;
    uint16_t numSamples;
}} Adc_GroupConfigType;

typedef struct {{
    const Adc_ChannelConfigType* channelConfigs;
    const Adc_GroupConfigType* groupConfigs;
    uint16_t numChannels;
    uint16_t numGroups;
}} Adc_ConfigType;

/*==================================================================================================
*                              FUNCTION DECLARATIONS
==================================================================================================*/
extern const Adc_ConfigType Adc_Config;

#endif /* ADC_CFG_H */
"""
        
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        self.status_var.set("ADC_CFG.H generated successfully")

    def save_driver_files(self):
        """Save all ADC driver files"""
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
            
        directory_path = filedialog.askdirectory(title="Select Directory to Save Driver Files")
        if not directory_path: 
            return
            
        try:
            adc_cfg_h_content = self.code_text.get(1.0, tk.END)
            generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            adc_h_content = ADC_H_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            adc_c_content = ADC_C_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            
            files_to_save = [
                ('Adc_Cfg.h', adc_cfg_h_content),
                ('Adc.h', adc_h_content),
                ('Adc.c', adc_c_content),
            ]

            for filename, content in files_to_save:
                with open(os.path.join(directory_path, filename), 'w', encoding='utf-8') as f:
                    f.write(content)
            
            # Create README file
            readme_content = f'''# AUTOSAR ADC Driver Files

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source ARXML: {os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'}

## Files Generated:

- Adc_Cfg.h: ADC Configuration Header
- Adc.h: ADC Driver Header
- Adc.c: ADC Driver Implementation

## Configuration Summary:

### Channels: {len(self.config_data['channels'])}
{chr(10).join([f"- {channel['symbolic_name']} (ID: {channel['id']}, Resolution: {channel['resolution']} bits)" for channel in self.config_data['channels']]) if self.config_data['channels'] else "- No channels configured"}

### Groups: {len(self.config_data['groups'])}
{chr(10).join([f"- Group {group['id']} (Mode: {group['access_mode']}, Priority: {group['priority']})" for group in self.config_data['groups']]) if self.config_data['groups'] else "- No groups configured"}

### Hardware Units: {len(self.config_data['hw_units'])}
{chr(10).join([f"- HW Unit {hw_unit.get('hw_unit_id', 'N/A')} (Prescale: {hw_unit.get('prescale', 'N/A')})" for hw_unit in self.config_data['hw_units']]) if self.config_data['hw_units'] else "- No hardware units configured"}

## API Features:
- DEINIT_API: {'ENABLED' if self.config_data['adc_deinit_api'] else 'DISABLED'}
- DEV_ERROR_DETECT: {'ENABLED' if self.config_data['adc_dev_error_detect'] else 'DISABLED'}
- ENABLE_LIMIT_CHECK: {'ENABLED' if self.config_data['adc_enable_limit_check'] else 'DISABLED'}
- ENABLE_QUEUING: {'ENABLED' if self.config_data['adc_enable_queuing'] else 'DISABLED'}
- START_STOP_GROUP_API: {'ENABLED' if self.config_data['adc_enable_start_stop_group_api'] else 'DISABLED'}
- GRP_NOTIF_CAPABILITY: {'ENABLED' if self.config_data['adc_grp_notif_capability'] else 'DISABLED'}
- HW_TRIGGER_API: {'ENABLED' if self.config_data['adc_hw_trigger_api'] else 'DISABLED'}
- VERSION_INFO_API: {'ENABLED' if self.config_data['adc_version_info_api'] else 'DISABLED'}
'''
            
            with open(os.path.join(directory_path, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(readme_content)

            messagebox.showinfo("Success", f"ADC driver files saved successfully to:\n{directory_path}")
            self.status_var.set("Driver files saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save files: {str(e)}")
            self.status_var.set("Error saving files")

def main():
    root = tk.Tk()
    root.title("ARXML to ADC Config Converter")
    root.geometry("1200x800")
    
    app = ARXMLtoADCGenerator(root)
    app.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == '__main__':
    main()