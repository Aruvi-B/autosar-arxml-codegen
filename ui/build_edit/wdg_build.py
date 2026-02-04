import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
# from .drivers.wdg_code import WDG_H_TEMPLATE, WDG_C_TEMPLATE

class ARXMLtoWDGGenerator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configuration data
        self.config_data = {
            'vendor_id': 1810,
            'module_id': 102,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            
            # WdgGeneral
            'dev_error_detect': True,
            'disable_allowed': False,
            'index': 0,
            'initial_timeout': 1000,
            'max_timeout': 65535,
            'run_area': 'ROM',
            'version_info_api': True,
            
            # WdgSettingsConfig
            'default_mode': 'WDGIF_SLOW_MODE',
            'external_configuration': False,
            'settings_fast': True,
            'settings_off': True,
            'settings_slow': True,

            # WdgPublishedInformation
            'trigger_mode': 'WDG_TOGGLE',
        }
        
        self.arxml_file_path = None
        self.status_var = tk.StringVar(value="Ready")
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title_label = ttk.Label(self, text="ARXML to WDG_CFG.H Generator", 
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

        self.generate_btn = ttk.Button(buttons_frame, text="Generate WDG_CFG.H", command=self.generate_wdg_cfg_h)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(buttons_frame, text="Save WDG_CFG.H", command=self.save_wdg_cfg_h)
        self.save_btn.pack(side=tk.LEFT)
        
        code_frame = ttk.LabelFrame(right_frame, text="Generated Wdg_Cfg.h", padding="10")
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
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.*")]
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
            
            messagebox.showinfo("Success", "ARXML parsed successfully!")
            self.generate_wdg_cfg_h()
            
        except ET.ParseError as e:
            messagebox.showerror("Parse Error", f"Failed to parse ARXML file: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_config_from_arxml(self, root):
        # Find all containers
        containers = root.findall('.//ECUC-CONTAINER-VALUE')
        
        for container in containers:
            short_name_elem = container.find('SHORT-NAME')
            if short_name_elem is None:
                continue

            short_name = short_name_elem.text

            if short_name == 'WdgGeneral':
                self.extract_wdg_general(container)
            elif short_name == 'WdgSettingsConfig':
                self.extract_wdg_settings_config(container)
            elif short_name == 'WdgPublishedInformation':
                self.extract_wdg_published_information(container)

    def extract_wdg_general(self, container):
        """Extract WdgGeneral configuration"""
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'WdgDevErrorDetect':
                self.config_data['dev_error_detect'] = value
            elif param_name == 'WdgDisableAllowed':
                self.config_data['disable_allowed'] = value
            elif param_name == 'WdgVersionInfoApi':
                self.config_data['version_info_api'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'WdgIndex':
                self.config_data['index'] = value
            elif param_name == 'WdgInitialTimeout':
                self.config_data['initial_timeout'] = value
            elif param_name == 'WdgMaxTimeout':
                self.config_data['max_timeout'] = value
        
        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'WdgRunArea':
                self.config_data['run_area'] = value

    def extract_wdg_settings_config(self, container):
        """Extract WdgSettingsConfig configuration"""
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')

        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'WdgDefaultMode':
                self.config_data['default_mode'] = value

        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)

            if param_name == 'WdgExternalConfiguration':
                self.config_data['external_configuration'] = value
            elif param_name == 'WdgSettingsFast':
                self.config_data['settings_fast'] = value
            elif param_name == 'WdgSettingsOff':
                self.config_data['settings_off'] = value
            elif param_name == 'WdgSettingsSlow':
                self.config_data['settings_slow'] = value

    def extract_wdg_published_information(self, container):
        """Extract WdgPublishedInformation configuration"""
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        
        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'WdgTriggerMode':
                self.config_data['trigger_mode'] = value

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
        config_text += f"{'='*60}\n\n"
        
        config_text += f"WDG General Configuration:\n"
        config_text += f"- WdgDevErrorDetect: {'STD_ON' if self.config_data.get('dev_error_detect') else 'STD_OFF'}\n"
        config_text += f"- WdgDisableAllowed: {'STD_ON' if self.config_data.get('disable_allowed') else 'STD_OFF'}\n"
        config_text += f"- WdgIndex: {self.config_data.get('index', 0)}\n"
        config_text += f"- WdgInitialTimeout: {self.config_data.get('initial_timeout', 0)}\n"
        config_text += f"- WdgMaxTimeout: {self.config_data.get('max_timeout', 0)}\n"
        config_text += f"- WdgRunArea: {self.config_data.get('run_area', 'ROM')}\n"
        config_text += f"- WdgVersionInfoApi: {'STD_ON' if self.config_data.get('version_info_api') else 'STD_OFF'}\n\n"
        
        config_text += f"WDG Settings Configuration:\n"
        config_text += f"- WdgDefaultMode: {self.config_data.get('default_mode', 'WDGIF_SLOW_MODE')}\n"
        config_text += f"- WdgExternalConfiguration: {'STD_ON' if self.config_data.get('external_configuration') else 'STD_OFF'}\n"
        config_text += f"- WdgSettingsFast: {'STD_ON' if self.config_data.get('settings_fast') else 'STD_OFF'}\n"
        config_text += f"- WdgSettingsOff: {'STD_ON' if self.config_data.get('settings_off') else 'STD_OFF'}\n"
        config_text += f"- WdgSettingsSlow: {'STD_ON' if self.config_data.get('settings_slow') else 'STD_OFF'}\n\n"
        
        config_text += f"WDG Published Information:\n"
        config_text += f"- WdgTriggerMode: {self.config_data.get('trigger_mode', 'WDG_TOGGLE')}\n\n"
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')

    def generate_wdg_cfg_h(self):
        """Generate the WDG_CFG.H file content"""
        content = f"""#ifndef WDG_CFG_H_
#define WDG_CFG_H_

/*
 * Developer Aruvi B and Auroshaa from CreamCollar
 * Generated WDG Configuration Header
 * Generated from ARXML: {os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'}
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

/* Module identification */
#define WDG_VENDOR_ID                    ({self.config_data['vendor_id']}U)
#define WDG_MODULE_ID                    ({self.config_data['module_id']}U)
#define WDG_INSTANCE_ID                  ({self.config_data['instance_id']}U)

/* Module version information */
#define WDG_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)
#define WDG_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)
#define WDG_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)

/* WDG General Configuration */
#define WDG_DEV_ERROR_DETECT             {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}
#define WDG_DISABLE_ALLOWED              {'STD_ON' if self.config_data['disable_allowed'] else 'STD_OFF'}
#define WDG_INDEX                        ({self.config_data['index']}U)
#define WDG_INITIAL_TIMEOUT              ({self.config_data['initial_timeout']}U)
#define WDG_MAX_TIMEOUT                  ({self.config_data['max_timeout']}U)
#define WDG_VERSION_INFO_API             {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}

/* WDG Run Area Configuration */
#define WDG_RUN_AREA                     (WDG_{self.config_data['run_area']})
#define WDG_RAM                          (0x00U)
#define WDG_ROM                          (0x01U)

/* WDG Settings Configuration */
#define WDG_DEFAULT_MODE                 ({self.config_data['default_mode']})

#define WDG_TRIGGER_MODE                 ({self.config_data['trigger_mode']})

/* WDG Mode Definitions */
#define WDGIF_OFF_MODE                   (0x00U)
#define WDGIF_SLOW_MODE                  (0x01U)
#define WDGIF_FAST_MODE                  (0x02U)

/* WDG Trigger Mode Definitions */
#define WDG_TOGGLE                       (0x00U)
#define WDG_WINDOW                       (0x01U)
#define WDG_BOTH                         (0x02U)

#endif /* WDG_CFG_H_ */
"""
        
        # Display generated code
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        
        # messagebox.showinfo("Success", "WDG_CFG.H generated successfully!")

    def save_wdg_cfg_h(self):
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save WDG_CFG.H File",
            # filename="Wdg_Cfg.h",
            defaultextension=".h",
            filetypes=[("Header files", "*.h"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"WDG_CFG.H saved successfully!\n\nLocation: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")
