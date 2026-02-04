import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
# from .drivers.gpt_code import GPT_H_TEMPLATE, GPT_C_TEMPLATE

class ARXMLtoGPTConfigGUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        
        
        self.status_var = tk.StringVar(value="Ready")
        

        self.config_data = {
            'vendor_id': 1810,
            'module_id': 100,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            
            # Main GPT containers
            'channel_config_set': False,
            'config_of_opt_api_service': False,
            'driver_configuration': False,
            
            # GptDriverConfiguration
            'dev_error_detect': True,
            'predef_timer_100us_32bit_enable': False,
            'predef_timer_1us_enabling_grade': 'GPT_PREDEF_TIMER_1US_DISABLED',
            'report_wakeup_source': False,
            
            # GptConfigurationOfOptApiServices
            'deinit_api': True,
            'enable_disable_notification_api': True,
            'time_elapsed_api': True,
            'time_remaining_api': True,
            'version_info_api': True,
            'wakeup_functionality_api': False,
            
            # Configuration arrays
            'clock_reference_points': [],
            'channel_config_sets': [],
            'channel_configurations': [],
            'wakeup_configurations': []
        }
        
        self.arxml_file_path = None
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title_label = ttk.Label(self, text="ARXML to GPT Driver Generator", 
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

        self.generate_btn = ttk.Button(buttons_frame, text="Generate GPT_CFG.H", command=self.generate_gpt_cfg_h)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(buttons_frame, text="Save GPT_CFG.H", command=self.save_gpt_cfg_h)
        self.save_btn.pack(side=tk.LEFT)

        code_frame = ttk.LabelFrame(right_frame, text="Generated Gpt_Cfg.h", padding="10")
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
    def browse_arxml_file(self):
        file_path = filedialog.askopenfilename(
            title="Select ARXML File",
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.* אמיתי") ]
        )
        
        if file_path:
            self.arxml_file_path = file_path
            self.file_path_var.set(os.path.basename(file_path))
            self.parse_btn.config(state='normal')

    def parse_arxml(self):
        if not self.arxml_file_path:
            messagebox.showerror("Error", "No ARXML file selected")
            return

        try:
            tree = ET.parse(self.arxml_file_path)
            root = tree.getroot()
            
            # Extract configuration
            self.extract_config_from_arxml(root)
            self.display_configuration()
            self.generate_gpt_cfg_h()
            
            messagebox.showinfo("Success", "ARXML parsed successfully!")
            
        except ET.ParseError as e:
            messagebox.showerror("Parse Error", f"Failed to parse ARXML file: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_config_from_arxml(self, root):
        # Clear existing data
        self.config_data['clock_reference_points'] = []
        self.config_data['channel_config_sets'] = []
        self.config_data['channel_configurations'] = []
        self.config_data['wakeup_configurations'] = []

        # Find all containers
        containers = root.findall('.//ECUC-CONTAINER-VALUE')
        
        for container in containers:
            short_name_elem = container.find('SHORT-NAME')
            if short_name_elem is None:
                continue

            short_name = short_name_elem.text

            if short_name == 'Gpt':
                self.extract_main_gpt_container(container)
            elif short_name == 'GptDriverConfiguration':
                self.extract_gpt_driver_config(container)
            elif short_name == 'GptConfigurationOfOptApiServices':
                self.extract_gpt_opt_api_services(container)
            elif short_name == 'GptClockReferencePoint':
                self.extract_gpt_clock_reference_point(container)
            elif short_name == 'GptChannelConfigSet':
                self.extract_gpt_channel_config_set(container)
            elif short_name == 'GptChannelConfiguration':
                self.extract_gpt_channel_configuration(container)
            elif short_name == 'GptWakeupConfiguration':
                self.extract_gpt_wakeup_configuration(container)

    def extract_main_gpt_container(self, container):
        """Extract main GPT container configuration"""
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'GptChannelConfigSet':
                self.config_data['channel_config_set'] = value
            elif param_name == 'GptConfigurationOfOptApiService':
                self.config_data['config_of_opt_api_service'] = value
            elif param_name == 'GptDriverConfiguration':
                self.config_data['driver_configuration'] = value

    def extract_gpt_driver_config(self, container):
        """Extract GptDriverConfiguration"""
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'GptDevErrorDetect':
                self.config_data['dev_error_detect'] = value
            elif param_name == 'GptPredefTimer100us32bitEnable':
                self.config_data['predef_timer_100us_32bit_enable'] = value
            elif param_name == 'GptReportWakeupSource':
                self.config_data['report_wakeup_source'] = value
        
        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'GptPredefTimer1usEnablingGrade':
                self.config_data['predef_timer_1us_enabling_grade'] = value

    def extract_gpt_opt_api_services(self, container):
        """Extract GptConfigurationOfOptApiServices"""
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'GptDeinitApi':
                self.config_data['deinit_api'] = value
            elif param_name == 'GptEnableDisableNotificationApi':
                self.config_data['enable_disable_notification_api'] = value
            elif param_name == 'GptTimeElapsedApi':
                self.config_data['time_elapsed_api'] = value
            elif param_name == 'GptTimeRemainingApi':
                self.config_data['time_remaining_api'] = value
            elif param_name == 'GptVersionInfoApi':
                self.config_data['version_info_api'] = value
            elif param_name == 'GptWakeupFunctionalityApi':
                self.config_data['wakeup_functionality_api'] = value

    def extract_gpt_clock_reference_point(self, container):
        """Extract GptClockReferencePoint configuration"""
        clock_ref = {
            'clock_reference': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'GptClockReference':
                clock_ref['clock_reference'] = value
        
        self.config_data['clock_reference_points'].append(clock_ref)

    def extract_gpt_channel_config_set(self, container):
        """Extract GptChannelConfigSet configuration"""
        config_set = {}
        
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            # The container name itself might contain the value
            config_set['value'] = value if param_name else 0
        
        self.config_data['channel_config_sets'].append(config_set)

    def extract_gpt_channel_configuration(self, container):
        """Extract GptChannelConfiguration"""
        channel_config = {
            'channel_id': 0,
            'channel_mode': 'GPT_CH_MODE_ONESHOT',
            'channel_tick_frequency': 0.0,
            'channel_tick_value_max': 0,
            'enable_wakeup': False,
            'notification': '',
            'channel_clk_src_ref': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        text_params = container.findall('.//ECUC-TEXTUAL-PARAM-VALUE')
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'GptEnableWakeup':
                channel_config['enable_wakeup'] = value
            elif param_name == 'GptChannelClkSrcRef':
                channel_config['channel_clk_src_ref'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'GptChannelId':
                channel_config['channel_id'] = value
            elif param_name == 'GptChannelTickFrequency':
                channel_config['channel_tick_frequency'] = value
            elif param_name == 'GptChannelTickValueMax':
                channel_config['channel_tick_value_max'] = value
        
        for param in text_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'GptNotification':
                channel_config['notification'] = value
        
        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'GptChannelMode':
                channel_config['channel_mode'] = value
        
        self.config_data['channel_configurations'].append(channel_config)

    def extract_gpt_wakeup_configuration(self, container):
        """Extract GptWakeupConfiguration"""
        wakeup_config = {
            'wakeup_source_ref': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'GptWakeupSourceRef':
                wakeup_config['wakeup_source_ref'] = value
        
        self.config_data['wakeup_configurations'].append(wakeup_config)

    def get_param_name(self, param):
        """Helper method to get parameter name"""
        param_name_elem = param.find('SHORT-NAME')
        return param_name_elem.text if param_name_elem is not None else ''

    def get_bool_value(self, param):
        """Helper method to get boolean value"""
        value_elem = param.find('VALUE')
        if value_elem is not None:
            return value_elem.text.strip().lower() == 'true'
        return False

    def get_num_value(self, param):
        """Helper method to get numerical value"""
        value_elem = param.find('VALUE')
        if value_elem is not None:
            try:
                return int(value_elem.text)
            except ValueError:
                try:
                    return float(value_elem.text)
                except ValueError:
                    return 0
        return 0

    def get_text_value(self, param):
        """Helper method to get text value"""
        value_elem = param.find('VALUE')
        return value_elem.text if value_elem is not None else ''

    def display_configuration(self):
        """Display extracted configuration"""
        config_text = f"Extracted Configuration from ARXML:\n"
        config_text += f"{ '='*60}\n\n"
        
        config_text += f"GPT Main Configuration:\n"
        config_text += f"- GptChannelConfigSet: {'STD_ON' if self.config_data['channel_config_set'] else 'STD_OFF'}\n"
        config_text += f"- GptConfigurationOfOptApiService: {'STD_ON' if self.config_data['config_of_opt_api_service'] else 'STD_OFF'}\n"
        config_text += f"- GptDriverConfiguration: {'STD_ON' if self.config_data['driver_configuration'] else 'STD_OFF'}\n\n"
        
        config_text += f"GPT Driver Configuration:\n"
        config_text += f"- GPT_DEV_ERROR_DETECT: {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}\n"
        config_text += f"- GPT_PREDEF_TIMER_100US_32BIT_ENABLE: {'STD_ON' if self.config_data['predef_timer_100us_32bit_enable'] else 'STD_OFF'}\n"
        config_text += f"- GPT_PREDEF_TIMER_1US_ENABLING_GRADE: {self.config_data['predef_timer_1us_enabling_grade']}\n"
        config_text += f"- GPT_REPORT_WAKEUP_SOURCE: {'STD_ON' if self.config_data['report_wakeup_source'] else 'STD_OFF'}\n\n"
        
        config_text += f"GPT Optional API Services:\n"
        config_text += f"- GPT_DEINIT_API: {'STD_ON' if self.config_data['deinit_api'] else 'STD_OFF'}\n"
        config_text += f"- GPT_ENABLE_DISABLE_NOTIFICATION_API: {'STD_ON' if self.config_data['enable_disable_notification_api'] else 'STD_OFF'}\n"
        config_text += f"- GPT_TIME_ELAPSED_API: {'STD_ON' if self.config_data['time_elapsed_api'] else 'STD_OFF'}\n"
        config_text += f"- GPT_TIME_REMAINING_API: {'STD_ON' if self.config_data['time_remaining_api'] else 'STD_OFF'}\n"
        config_text += f"- GPT_VERSION_INFO_API: {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}\n"
        config_text += f"- GPT_WAKEUP_FUNCTIONALITY_API: {'STD_ON' if self.config_data['wakeup_functionality_api'] else 'STD_OFF'}\n\n"
        
        config_text += f"Clock Reference Points ({len(self.config_data['clock_reference_points'])}):\n"
        for i, clock_ref in enumerate(self.config_data['clock_reference_points']):
            config_text += f"- Clock Ref {i}: Reference={clock_ref['clock_reference']}\n"
        
        config_text += f"\nChannel Config Sets ({len(self.config_data['channel_config_sets'])}):\n"
        for i, config_set in enumerate(self.config_data['channel_config_sets']):
            config_text += f"- Config Set {i}: Value={config_set.get('value', 0)}\n"
        
        config_text += f"\nChannel Configurations ({len(self.config_data['channel_configurations'])}):\n"
        for i, ch in enumerate(self.config_data['channel_configurations']):
            config_text += f"- Channel {i}: ID={ch['channel_id']}, Mode={ch['channel_mode']}, "
            config_text += f"Freq={ch['channel_tick_frequency']}, Max={ch['channel_tick_value_max']}\n"
            if ch['notification']:
                config_text += f"  Notification: {ch['notification']}\n"
        
        config_text += f"\nWakeup Configurations ({len(self.config_data['wakeup_configurations'])}):\n"
        for i, wakeup in enumerate(self.config_data['wakeup_configurations']):
            config_text += f"- Wakeup {i}: Source Ref={wakeup['wakeup_source_ref']}\n"
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')

    def generate_gpt_cfg_h(self):
        """Generate the GPT_CFG.H file content"""
        content = f"#ifndef GPT_CFG_H_\n#define GPT_CFG_H_\n\n/*\n * Developer Aruvi B and Auroshaa from CreamCollar\n * Generated GPT Configuration Header\n * Generated from ARXML: {os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'}\n * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n */\n\n/* Module identification */\n#define GPT_VENDOR_ID                    ({self.config_data['vendor_id']}U)\n#define GPT_MODULE_ID                    ({self.config_data['module_id']}U)\n#define GPT_INSTANCE_ID                  ({self.config_data['instance_id']}U)\n\n/* Module version information */\n#define GPT_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)\n#define GPT_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)\n#define GPT_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)\n\n/* GPT Driver Configuration */\n#define GPT_DEV_ERROR_DETECT             {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}\n#define GPT_PREDEF_TIMER_100US_32BIT_ENABLE {'STD_ON' if self.config_data['predef_timer_100us_32bit_enable'] else 'STD_OFF'}\n#define GPT_PREDEF_TIMER_1US_ENABLING_GRADE ({self.config_data['predef_timer_1us_enabling_grade']})\n#define GPT_REPORT_WAKEUP_SOURCE         {'STD_ON' if self.config_data['report_wakeup_source'] else 'STD_OFF'}\n\n/* GPT Optional API Services */\n#define GPT_DEINIT_API                   {'STD_ON' if self.config_data['deinit_api'] else 'STD_OFF'}\n#define GPT_ENABLE_DISABLE_NOTIFICATION_API {'STD_ON' if self.config_data['enable_disable_notification_api'] else 'STD_OFF'}\n#define GPT_TIME_ELAPSED_API             {'STD_ON' if self.config_data['time_elapsed_api'] else 'STD_OFF'}\n#define GPT_TIME_REMAINING_API           {'STD_ON' if self.config_data['time_remaining_api'] else 'STD_OFF'}\n#define GPT_VERSION_INFO_API             {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}\n#define GPT_WAKEUP_FUNCTIONALITY_API     {'STD_ON' if self.config_data['wakeup_functionality_api'] else 'STD_OFF'}\n\n/* GPT Predef Timer 1us Enabling Grade Options */\n#define GPT_PREDEF_TIMER_1US_16BIT_ENABLED          (0x01U)\n#define GPT_PREDEF_TIMER_1US_16_24BIT_ENABLED       (0x02U)\n#define GPT_PREDEF_TIMER_1US_16_24_32BIT_ENABLED    (0x03U)\n#define GPT_PREDEF_TIMER_1US_DISABLED               (0x00U)\n\n/* GPT Error Codes */\n#define GPT_E_UNINIT                     (0x0AU)\n#define GPT_E_BUSY                       (0x0BU)\n#define GPT_E_MODE                       (0x0CU)\n#define GPT_E_PARAM_CHANNEL              (0x14U)\n#define GPT_E_PARAM_VALUE                (0x15U)\n#define GPT_E_PARAM_POINTER              (0x16U)\n#define GPT_E_PARAM_PREDEF_TIMER         (0x17U)\n#define GPT_E_PARAM_MODE                 (0x1FU)\n\n/* Service IDs */\n#define GPT_INIT_SID                     (0x01U)\n#define GPT_DEINIT_SID                   (0x02U)\n#define GPT_GET_TIME_ELAPSED_SID         (0x03U)\n#define GPT_GET_TIME_REMAINING_SID       (0x04U)\n#define GPT_START_TIMER_SID              (0x05U)\n#define GPT_STOP_TIMER_SID               (0x06U)\n#define GPT_ENABLE_NOTIFICATION_SID      (0x07U)\n#define GPT_DISABLE_NOTIFICATION_SID     (0x08U)\n#define GPT_SET_MODE_SID                 (0x09U)\n#define GPT_DISABLE_WAKEUP_SID           (0x0AU)\n#define GPT_ENABLE_WAKEUP_SID            (0x0BU)\n#define GPT_CHECK_WAKEUP_SID             (0x0CU)\n#define GPT_GET_VERSION_INFO_SID         (0x00U)\n#define GPT_GET_PREDEF_TIMER_VALUE_SID   (0x0DU)\n\n/* GPT Channel Mode */\n#define GPT_CH_MODE_CONTINUOUS           (0x00U)\n#define GPT_CH_MODE_ONESHOT              (0x01U)\n\n/* GPT Mode Type */\n#define GPT_MODE_NORMAL                  (0x00U)\n#define GPT_MODE_SLEEP                   (0x01U)\n\n/* GPT Predef Timer Type */\n#define GPT_PREDEF_TIMER_1US_16BIT       (0x00U)\n#define GPT_PREDEF_TIMER_1US_24BIT       (0x01U)\n#define GPT_PREDEF_TIMER_1US_32BIT       (0x02U)\n#define GPT_PREDEF_TIMER_100US_32BIT     (0x03U)\n"

        # Add Channel definitions
        if self.config_data['channel_configurations']:
            content += "/* GPT Channel Symbolic Names */\n"
            for i, channel in enumerate(self.config_data['channel_configurations']):
                content += f"#define GptConf_GptChannelConfiguration_Channel_{channel['channel_id']}    ({channel['channel_id']}U)\n"
            
            content += "\n/* GPT Channel Configuration */\n"
            for i, channel in enumerate(self.config_data['channel_configurations']):
                content += f"#define GPT_CHANNEL_{channel['channel_id']}_MODE                     ({channel['channel_mode']})\n"
                content += f"#define GPT_CHANNEL_{channel['channel_id']}_TICK_FREQUENCY           ({channel['channel_tick_frequency']}f)\n"
                content += f"#define GPT_CHANNEL_{channel['channel_id']}_TICK_VALUE_MAX           ({channel['channel_tick_value_max']}U)\n"
                content += f"#define GPT_CHANNEL_{channel['channel_id']}_ENABLE_WAKEUP            ({'STD_ON' if channel['enable_wakeup'] else 'STD_OFF'})\n"
                content += f"#define GPT_CHANNEL_{channel['channel_id']}_CLK_SRC_REF              ({'STD_ON' if channel['channel_clk_src_ref'] else 'STD_OFF'})\n"
                
                if channel['notification']:
                    content += f"#define GPT_CHANNEL_{channel['channel_id']}_NOTIFICATION             {channel['notification']}\n"
                    content += f"#define GPT_CHANNEL_{channel['channel_id']}_NOTIFICATION_ENABLED     (STD_ON)\n"
                else:
                    content += f"#define GPT_CHANNEL_{channel['channel_id']}_NOTIFICATION_ENABLED     (STD_OFF)\n"
                content += "\n"

        # Add configuration counts
        content += f"/* Configuration Counts */\n"
        content += f"#define GPT_CONFIG_CHANNELS_COUNT            ({len(self.config_data['channel_configurations'])}U)\n"
        content += f"#define GPT_CONFIG_CLOCK_REFERENCE_POINTS    ({len(self.config_data['clock_reference_points'])}U)\n"
        content += f"#define GPT_CONFIG_WAKEUP_SOURCES_COUNT      ({len(self.config_data['wakeup_configurations'])}U)\n"
        content += f"#define GPT_CONFIG_CHANNEL_CONFIG_SETS       ({len(self.config_data['channel_config_sets'])}U)\n"

        # Add maximum channel ID
        if self.config_data['channel_configurations']:
            max_channel_id = max(ch['channel_id'] for ch in self.config_data['channel_configurations'])
            content += f"#define GPT_MAX_CHANNEL_ID                   ({max_channel_id}U)\n"
        else:
            content += f"#define GPT_MAX_CHANNEL_ID                   (0U)\n"

        # Add channel notification function declarations if notifications are defined
        notification_functions = []
        for channel in self.config_data['channel_configurations']:
            if channel['notification']:
                notification_functions.append(channel['notification'])
        
        if notification_functions:
            content += f"\n/* GPT Channel Notification Function Declarations */\n"
            for func in set(notification_functions):  # Remove duplicates
                content += f"extern void {func}(void);\n"

        # Add predef timer configuration
        content += f"\n/* GPT Predef Timer Configuration */\n"
        if self.config_data['predef_timer_1us_enabling_grade'] != 'GPT_PREDEF_TIMER_1US_DISABLED':
            content += f"#define GPT_PREDEF_TIMER_1US_ENABLED         (STD_ON)\n"
            content += f"#define GPT_PREDEF_TIMER_1US_GRADE           ({self.config_data['predef_timer_1us_enabling_grade']})\n"
        else:
            content += f"#define GPT_PREDEF_TIMER_1US_ENABLED         (STD_OFF)\n"
            
        if self.config_data['predef_timer_100us_32bit_enable']:
            content += f"#define GPT_PREDEF_TIMER_100US_32BIT_ENABLED (STD_ON)\n"
        else:
            content += f"#define GPT_PREDEF_TIMER_100US_32BIT_ENABLED (STD_OFF)\n"

        # Add channel array size definitions
        content += f"\n/* GPT Channel Array Sizes */\n"
        continuous_channels = [ch for ch in self.config_data['channel_configurations'] if ch['channel_mode'] == 'GPT_CH_MODE_CONTINUOUS']
        oneshot_channels = [ch for ch in self.config_data['channel_configurations'] if ch['channel_mode'] == 'GPT_CH_MODE_ONESHOT']
        wakeup_channels = [ch for ch in self.config_data['channel_configurations'] if ch['enable_wakeup']]
        
        content += f"#define GPT_CONTINUOUS_CHANNELS_COUNT        ({len(continuous_channels)}U)\n"
        content += f"#define GPT_ONESHOT_CHANNELS_COUNT           ({len(oneshot_channels)}U)\n"
        content += f"#define GPT_WAKEUP_CHANNELS_COUNT            ({len(wakeup_channels)}U)\n"

        # Add channel lists by mode
        if continuous_channels:
            content += f"\n/* GPT Continuous Mode Channels */\n"
            for i, ch in enumerate(continuous_channels):
                content += f"#define GPT_CONTINUOUS_CHANNEL_{i}           ({ch['channel_id']}U)\n"
        
        if oneshot_channels:
            content += f"\n/* GPT One-Shot Mode Channels */\n"
            for i, ch in enumerate(oneshot_channels):
                content += f"#define GPT_ONESHOT_CHANNEL_{i}              ({ch['channel_id']}U)\n"
        
        if wakeup_channels:
            content += f"\n/* GPT Wakeup Enabled Channels */\n"
            for i, ch in enumerate(wakeup_channels):
                content += f"#define GPT_WAKEUP_CHANNEL_{i}               ({ch['channel_id']}U)\n"

        # Add clock reference configuration
        if self.config_data['clock_reference_points']:
            content += f"\n/* GPT Clock Reference Points Configuration */\n"
            for i, clock_ref in enumerate(self.config_data['clock_reference_points']):
                content += f"#define GPT_CLOCK_REFERENCE_{i}_ENABLED      ({'STD_ON' if clock_ref['clock_reference'] else 'STD_OFF'})\n"

        # Add timer value type definitions based on predef timer configuration
        content += f"\n/* GPT Timer Value Type Definitions */\n"
        content += f"typedef uint16 Gpt_ValueType;\n"
        content += f"typedef uint32 Gpt_ChannelType;\n"
        
        # Add predef timer value type definitions
        if self.config_data['predef_timer_1us_enabling_grade'] == 'GPT_PREDEF_TIMER_1US_16BIT_ENABLED':
            content += f"typedef uint16 Gpt_PredefTimer1usValueType;\n"
        elif self.config_data['predef_timer_1us_enabling_grade'] == 'GPT_PREDEF_TIMER_1US_16_24BIT_ENABLED':
            content += f"typedef uint32 Gpt_PredefTimer1usValueType;\n"
        elif self.config_data['predef_timer_1us_enabling_grade'] == 'GPT_PREDEF_TIMER_1US_16_24_32BIT_ENABLED':
            content += f"typedef uint32 Gpt_PredefTimer1usValueType;\n"
        
        if self.config_data['predef_timer_100us_32bit_enable']:
            content += f"typedef uint32 Gpt_PredefTimer100usValueType;\n"

        # Add channel mode type definition
        content += f"\n/* GPT Channel Mode Type */\n"
        content += f"typedef uint8 Gpt_ModeType;\n"
        content += f"typedef uint8 Gpt_ChannelModeType;\n"

        # Add notification function type definition
        content += f"\n/* GPT Notification Function Type */\n"
        content += f"typedef void (*Gpt_NotificationCallbackType)(void);\n"

        # Add wakeup source definitions if wakeup functionality is enabled
        if self.config_data['wakeup_functionality_api'] and self.config_data['wakeup_configurations']:
            content += f"\n/* GPT Wakeup Source Definitions */\n"
            for i, wakeup in enumerate(self.config_data['wakeup_configurations']):
                if wakeup['wakeup_source_ref']:
                    content += f"#define GPT_WAKEUP_SOURCE_{i}                (EcuM_WakeupSourceType)(1U << {i})\n"

        # Add hardware specific definitions
        content += f"\n/* GPT Hardware Specific Definitions */\n"
        content += f"#define GPT_HW_CHANNEL_OFFSET                (0x00U)\n"
        content += f"#define GPT_PRESCALER_MIN                    (1U)\n"
        content += f"#define GPT_PRESCALER_MAX                    (65535U)\n"
        
        # Add frequency calculations for each channel
        if self.config_data['channel_configurations']:
            content += f"\n/* GPT Channel Frequency Calculations */\n"
            for channel in self.config_data['channel_configurations']:
                if channel['channel_tick_frequency'] > 0:
                    period_us = 1000000 / channel['channel_tick_frequency']
                    content += f"#define GPT_CHANNEL_{channel['channel_id']}_PERIOD_US            ({period_us:.2f}f)\n"

        # Add configuration structure forward declarations
        content += f"\n/* GPT Configuration Structure Forward Declarations */\n"
        content += f"typedef struct Gpt_ConfigType Gpt_ConfigType;\n"
        content += f"typedef struct Gpt_ChannelConfigType Gpt_ChannelConfigType;\n"

        # Add external configuration variable declaration
        content += f"\n/* GPT Configuration Variable Declaration */\n"
        content += f"extern const Gpt_ConfigType GptConfigSet;\n"

        # Add conditional compilation guards for optional features
        content += f"\n/* GPT Conditional Compilation Guards */\n"
        if not self.config_data['deinit_api']:
            content += f"#define Gpt_DeInit()    /* Not configured */\n"
        
        if not self.config_data['enable_disable_notification_api']:
            content += f"#define Gpt_EnableNotification(Channel)     /* Not configured */\n"
            content += f"#define Gpt_DisableNotification(Channel)    /* Not configured */\n"
        
        if not self.config_data['time_elapsed_api']:
            content += f"#define Gpt_GetTimeElapsed(Channel)         /* Not configured */\n"
        
        if not self.config_data['time_remaining_api']:
            content += f"#define Gpt_GetTimeRemaining(Channel)       /* Not configured */\n"
        
        if not self.config_data['version_info_api']:
            content += f"#define Gpt_GetVersionInfo(VersionInfo)     /* Not configured */\n"
        
        if not self.config_data['wakeup_functionality_api']:
            content += f"#define Gpt_SetWakeup(Channel)              /* Not configured */\n"
            content += f"#define Gpt_CheckWakeup(WakeupSource)       /* Not configured */\n"

        content += f"\n#endif /* GPT_CFG_H_ */\n"
        
        # Display generated code
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        
        # messagebox.showinfo("Success", "GPT_CFG.H generated successfully!")

    def save_gpt_cfg_h(self):
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save GPT_CFG.H File",
            # filename="Gpt_Cfg.h",
            defaultextension=".h",
            filetypes=[("Header files", "*.h"), ("All files", "*.* אמיתי")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"GPT_CFG.H saved successfully!\n\nLocation: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    root.title("ARXML to DIO Config Converter")
    app = ARXMLtoGPTConfigGUI(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()
