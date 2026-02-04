import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
# from ..channel_editor import ChannelEditor
from .drivers.dio_code import DIO_H_TEMPLATE, DIO_C_TEMPLATE
from ..editor.peripheral_config.dio_config import DioAppModel

class ARXMLtoDIOConfigGUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        model = DioAppModel()
        self.config_data = {
            'vendor_id': 1810,
            'module_id': 202,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            'include_dio_config_set': True,
            'DioConfigSet': model.DioConfigSet,
            'dev_error_detect': model.DioGeneral.DioDevErrorDetect,
            'version_info_api': model.DioGeneral.DioVersionInfoApi,
            'flip_channel_api': model.DioGeneral.DioFlipChannelApi,
            'masked_write_port_api': model.DioGeneral.DioMaskedWritePortApi,
            'channels': [],
            'ports': [],
            'channel_groups': [],
            'dio_config': model.DioConfig.DioConfig,
            'dio_general': {}
        }
        
        self.arxml_file_path = None
        self.status_var = tk.StringVar(value="Ready")
        self.channel_editor = None
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title_label = ttk.Label(self, text="ARXML to DIO_CFG.H Generator", 
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

        # self.channel_editor = ChannelEditor(left_frame, self.config_data, self.display_configuration)
        # self.channel_editor.grid(row=1, column=0, sticky='ew', pady=(10, 0))

        buttons_frame = ttk.Frame(left_frame)
        buttons_frame.grid(row=2, column=0, sticky='w', pady=(10, 0))

        self.generate_btn = ttk.Button(buttons_frame, text="Generate DIO_CFG.H", command=self.generate_dio_cfg_h)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(buttons_frame, text="Save Driver Files", command=self.save_driver_files)
        self.save_btn.pack(side=tk.LEFT)

        code_frame = ttk.LabelFrame(right_frame, text="Generated Dio_Cfg.h", padding="10")
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
            tree = ET.parse(self.arxml_file_path)
            root = tree.getroot()
            
            success = self.extract_config_from_arxml(root)
            
            if success:
                self.display_configuration()
                self.status_var.set("ARXML parsed successfully")
                messagebox.showinfo("Success", "ARXML parsed successfully!")
                self.generate_dio_cfg_h()
            else:
                self.status_var.set("Warning: Limited configuration found")
                messagebox.showwarning("Warning", "ARXML parsed but limited DIO configuration found. Please verify the file structure.")
            
        except ET.ParseError as e:
            self.status_var.set("Parse error")
            messagebox.showerror("Parse Error", f"Failed to parse ARXML file: {str(e)}")
        except Exception as e:
            self.status_var.set("Error occurred")
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_config_from_arxml(self, root):
        # Reset configuration data
        self.config_data['channels'] = []
        self.config_data['ports'] = []
        self.config_data['channel_groups'] = []
        self.config_data['dio_general'] = {}
        
        # Set up namespaces
        namespaces = {'ar': 'http://autosar.org/schema/r4.0'}
        if hasattr(root, 'nsmap'):
            for prefix, uri in root.nsmap.items():
                if 'autosar' in uri.lower():
                    namespaces['ar'] = uri
                    break

        config_found = False
        
        # Search for containers using multiple paths
        container_paths = [
            './/ECUC-CONTAINER-VALUE',
            './/{http://autosar.org/schema/r4.0}ECUC-CONTAINER-VALUE',
            './/CONTAINER-VALUE',
            './/ECUC-CONTAINER'
        ]
        
        containers = []
        for path in container_paths:
            found = root.findall(path)
            if found:
                containers.extend(found)

        # Process each container
        for container in containers:
            short_name_elem = container.find('SHORT-NAME')
            if short_name_elem is None:
                short_name_elem = container.find('.//{http://autosar.org/schema/r4.0}SHORT-NAME')
            if short_name_elem is None: 
                continue
                
            short_name = short_name_elem.text

            if 'DioConfigSet' in short_name:
                config_found = True
                self._extract_config_set(container)
            elif 'DioGeneral' in short_name:
                config_found = True
                self._extract_general_config(container)
            elif 'DioPort' in short_name and 'Group' not in short_name:
                config_found = True
                self._extract_port_config(container, short_name)
            elif 'DioChannel' in short_name and 'Group' not in short_name:
                config_found = True
                self._extract_channel_config(container, short_name)
            elif 'DioChannelGroup' in short_name:
                config_found = True
                self._extract_channel_group_config(container, short_name)
            elif 'DioConfig' in short_name and 'Set' not in short_name:
                config_found = True
                self._extract_dio_config(container)

        # Sort configurations by ID
        self.config_data['ports'].sort(key=lambda x: x['id'])
        self.config_data['channels'].sort(key=lambda x: x['id'])
        
        if self.channel_editor: 
            self.channel_editor.load_channels()
            
        return config_found

    def _extract_config_set(self, container):
        """Extract DioConfigSet configuration"""
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                if 'IncludeDioConfigSet' in param_name:
                    self.config_data['include_dio_config_set'] = value

    def _extract_general_config(self, container):
        """Extract DioGeneral configuration"""
        dio_general = {}
        
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                
                # Store in dio_general for display
                dio_general[param_name] = value
                
                # Also update main config for backward compatibility
                if 'DioDevErrorDetect' in param_name:
                    self.config_data['dev_error_detect'] = value
                elif 'DioVersionInfoApi' in param_name:
                    self.config_data['version_info_api'] = value
                elif 'DioFlipChannelApi' in param_name:
                    self.config_data['flip_channel_api'] = value
                elif 'DioMaskedWritePortApi' in param_name:
                    self.config_data['masked_write_port_api'] = value
        
        self.config_data['dio_general'] = dio_general

    def _extract_port_config(self, container, container_name):
        """Extract DioPort configuration"""
        port_id = None
        port_symbolic_name = container_name
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if 'DioPortId' in param_name:
                    try:
                        port_id = int(value_elem.text)
                    except ValueError:
                        continue
        
        # Extract textual parameters
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if 'SymbolicName' in param_name:
                    port_symbolic_name = value_elem.text
        
        # If no port ID found, try to extract from container name
        if port_id is None:
            import re
            match = re.search(r'(\d+)', container_name)
            port_id = int(match.group(1)) if match else len(self.config_data['ports'])
        
        # Add port if not already exists
        if port_id is not None and not any(p['id'] == port_id for p in self.config_data['ports']):
            self.config_data['ports'].append({
                'id': port_id, 
                'symbolic_name': port_symbolic_name or f'DIO_PORT_{port_id}',
                'container_name': container_name
            })

    def _extract_channel_config(self, container, container_name):
        """Extract DioChannel configuration"""
        channel_id = None
        channel_symbolic_name = container_name
        port_ref = 0
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                try:
                    if 'DioChannelId' in param_name:
                        channel_id = int(value_elem.text)
                    elif 'DioPortRef' in param_name or 'PortRef' in param_name:
                        port_ref = int(value_elem.text)
                except ValueError:
                    continue
        
        # Extract textual parameters
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if 'SymbolicName' in param_name:
                    channel_symbolic_name = value_elem.text
        
        # If no channel ID found, try to extract from container name
        if channel_id is None:
            import re
            match = re.search(r'(\d+)', container_name)
            channel_id = int(match.group(1)) if match else len(self.config_data['channels'])
        
        # Add channel if not already exists
        if channel_id is not None and not any(c['id'] == channel_id for c in self.config_data['channels']):
            self.config_data['channels'].append({
                'id': channel_id, 
                'port': port_ref, 
                'symbolic_name': channel_symbolic_name or f'DIO_CHANNEL_{channel_id}',
                'container_name': container_name
            })

    def _extract_channel_group_config(self, container, container_name):
        """Extract DioChannelGroup configuration"""
        group_id = container_name
        group_identification = container_name
        port_mask = 0xFF
        port_offset = 0
        port_ref = 0
        
        # Extract numerical parameters
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                try:
                    if 'DioPortMask' in param_name:
                        port_mask = int(value_elem.text, 0)
                    elif 'DioPortOffset' in param_name:
                        port_offset = int(value_elem.text)
                    elif 'DioPortRef' in param_name or 'PortRef' in param_name:
                        port_ref = int(value_elem.text)
                except ValueError:
                    continue
        
        # Extract textual parameters
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                if 'DioChannelGroupIdentification' in param_name:
                    group_identification = value_elem.text
                    group_id = group_identification
                elif 'GroupId' in param_name:
                    group_id = value_elem.text
        
        # Add channel group if not already exists
        if not any(g['id'] == group_id for g in self.config_data['channel_groups']):
            self.config_data['channel_groups'].append({
                'id': group_id,
                'identification': group_identification, 
                'mask': port_mask, 
                'offset': port_offset, 
                'port': port_ref,
                'container_name': container_name
            })

    def _extract_dio_config(self, container):
        """Extract DioConfig configuration"""
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                if 'DioConfig' in param_name:
                    self.config_data['dio_config'] = value

    def display_configuration(self):
        """Display extracted configuration in structured format"""
        config_text = "═" * 80 + "\n"
        config_text += "EXTRACTED DIO CONFIGURATION FROM ARXML\n"
        config_text += "═" * 80 + "\n\n"
        
        # Module Information
        config_text += "MODULE INFORMATION\n"
        # config_text += "─" * 40 + "\n"
        config_text += f"  Vendor ID: {self.config_data['vendor_id']}\n"
        config_text += f"  Module ID: {self.config_data['module_id']}\n"
        config_text += f"  Instance ID: {self.config_data['instance_id']}\n"
        config_text += f"  SW Version: {self.config_data['sw_major_version']}.{self.config_data['sw_minor_version']}.{self.config_data['sw_patch_version']}\n\n"
        
        # DIO Config Set
        config_text += "DIO CONFIG SET\n"
        # config_text += "─" * 40 + "\n"
        config_text += f"  Include DIO Config Set: {'Yes' if self.config_data['include_dio_config_set'] else 'No'}\n\n"
        
        # DIO General Configuration
        if self.config_data['dio_general']:
            config_text += "DIO GENERAL CONFIGURATION\n"
            # config_text += "─" * 40 + "\n"
            for key, value in self.config_data['dio_general'].items():
                formatted_value = "Yes" if value else "No"
                config_text += f"  {key}: {formatted_value}\n"
            config_text += "\n"
        
        # API Configuration Summary
        config_text += "API CONFIGURATION SUMMARY\n"
        # config_text += "─" * 40 + "\n"
        config_text += f"  DIO_DEV_ERROR_DETECT: {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}\n"
        config_text += f"  DIO_VERSION_INFO_API: {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}\n"
        config_text += f"  DIO_FLIP_CHANNEL_API: {'STD_ON' if self.config_data['flip_channel_api'] else 'STD_OFF'}\n"
        config_text += f"  DIO_MASKED_WRITE_PORT_API: {'STD_ON' if self.config_data['masked_write_port_api'] else 'STD_OFF'}\n\n"
        
        # DIO Ports
        if self.config_data['ports']:
            config_text += f"DIO PORTS ({len(self.config_data['ports'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for port in self.config_data['ports']:
                config_text += f"  Port {port['id']}:\n"
                config_text += f"    Symbolic Name: {port['symbolic_name']}\n"
                config_text += f"    Container: {port.get('container_name', 'Unknown')}\n"
            config_text += "\n"
        else:
            config_text += "DIO PORTS\n"
            # config_text += "─" * 40 + "\n"
            config_text += "  No ports configured\n\n"
        
        # DIO Channels
        if self.config_data['channels']:
            config_text += f"DIO CHANNELS ({len(self.config_data['channels'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for channel in self.config_data['channels']:
                config_text += f"  Channel {channel['id']}:\n"
                config_text += f"    Symbolic Name: {channel['symbolic_name']}\n"
                config_text += f"    Port Reference: {channel['port']}\n"
                config_text += f"    Container: {channel.get('container_name', 'Unknown')}\n"
            config_text += "\n"
        else:
            config_text += "DIO CHANNELS\n"
            # config_text += "─" * 40 + "\n"
            config_text += "  No channels configured\n\n"
        
        # DIO Channel Groups
        if self.config_data['channel_groups']:
            config_text += f"DIO CHANNEL GROUPS ({len(self.config_data['channel_groups'])} found)\n"
            # config_text += "─" * 40 + "\n"
            for group in self.config_data['channel_groups']:
                config_text += f"  Channel Group: {group['id']}\n"
                config_text += f"    Identification: {group.get('identification', group['id'])}\n"
                config_text += f"    Port Reference: {group['port']}\n"
                config_text += f"    Port Mask: 0x{group['mask']:04X} ({group['mask']})\n"
                config_text += f"    Port Offset: {group['offset']}\n"
                config_text += f"    Container: {group.get('container_name', 'Unknown')}\n"
            config_text += "\n"
        else:
            config_text += "DIO CHANNEL GROUPS\n"
            # config_text += "─" * 40 + "\n"
            config_text += "  No channel groups configured\n\n"
        
        # DIO Config
        config_text += "DIO CONFIG\n"
        # config_text += "─" * 40 + "\n"
        config_text += f"  DIO Config: {'Yes' if self.config_data['dio_config'] else 'No'}\n\n"
        
        # Validation Status
        config_text += "VALIDATION STATUS\n"
        # config_text += "─" * 40 + "\n"
        if not self.config_data['ports'] and not self.config_data['channels']:
            config_text += "  WARNING: No DIO configuration found\n"
        else:
            config_text += "  Configuration extracted successfully\n"
        
        config_text += "\n" + "═" * 80 + "\n"
        config_text += "END OF CONFIGURATION\n"
        config_text += "═" * 80 + "\n"
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')
        
        if self.channel_editor: 
            self.channel_editor.load_channels()

    def generate_dio_cfg_h(self):
        """Generate DIO_CFG.H file content"""
        if not self.config_data['channels'] and not self.config_data['ports']:
            messagebox.showwarning("Warning", "No DIO configuration available.")
            return
            
        arxml_filename = os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'
        generation_date = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        content = f'''#ifndef DIO_CFG_H
#define DIO_CFG_H

/**
 * Developer Aruvi B & Auroshaa A from CreamCollar
 * @file Dio_Cfg.h
 * @brief DIO Configuration Header File
 * @details Generated DIO Configuration Header from ARXML
 * 
 * Generated from ARXML: {arxml_filename}
 * Generated on: {generation_date}
 */

#include "Std_Types.h"

/*==================================================================================================
*                              MODULE IDENTIFICATION
==================================================================================================*/
#define DIO_CFG_VENDOR_ID                    ({self.config_data['vendor_id']}U)
#define DIO_CFG_MODULE_ID                    ({self.config_data['module_id']}U)
#define DIO_CFG_INSTANCE_ID                  ({self.config_data['instance_id']}U)

/*==================================================================================================
*                              VERSION INFORMATION
==================================================================================================*/
#define DIO_CFG_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)
#define DIO_CFG_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)
#define DIO_CFG_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)

/*==================================================================================================
*                              CONFIGURATION SET
==================================================================================================*/
#define DIO_INCLUDE_CONFIG_SET               {'STD_ON' if self.config_data['include_dio_config_set'] else 'STD_OFF'}
#define DIO_CONFIG                           {'STD_ON' if self.config_data['dio_config'] else 'STD_OFF'}

/*==================================================================================================
*                              API CONFIGURATION
==================================================================================================*/
#define DIO_DEV_ERROR_DETECT                 {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}
#define DIO_VERSION_INFO_API                 {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}
#define DIO_FLIP_CHANNEL_API                 {'STD_ON' if self.config_data['flip_channel_api'] else 'STD_OFF'}
#define DIO_MASKED_WRITE_PORT_API            {'STD_ON' if self.config_data['masked_write_port_api'] else 'STD_OFF'}

/*==================================================================================================
*                              CONFIGURATION COUNTS
==================================================================================================*/
#define DIO_PORT_COUNT                       ({len(self.config_data['ports'])}U)
#define DIO_CHANNEL_COUNT                    ({len(self.config_data['channels'])}U)
#define DIO_CHANNEL_GROUP_COUNT              ({len(self.config_data['channel_groups'])}U)

'''

        # Add Port Symbolic Names
        if self.config_data['ports']:
            content += """/*==================================================================================================
*                              DIO PORT SYMBOLIC NAMES
==================================================================================================*/
"""
            for port in self.config_data['ports']:
                content += f"#define {port['symbolic_name']:<40} ({port['id']}U)\n"
            content += "\n"

        # Add Channel Symbolic Names
        if self.config_data['channels']:
            content += """/*==================================================================================================
*                              DIO CHANNEL SYMBOLIC NAMES
==================================================================================================*/
"""
            for channel in self.config_data['channels']:
                content += f"#define {channel['symbolic_name']:<40} ({channel['id']}U)\n"
            content += "\n"

        # Add Channel Group Symbolic Names
        if self.config_data['channel_groups']:
            content += """/*==================================================================================================
*                              DIO CHANNEL GROUP SYMBOLIC NAMES
==================================================================================================*/
"""
            for group in self.config_data['channel_groups']:
                content += f"#define {group['id']:<40} ({group['port']}U)\n"
                content += f"#define {group['id']}_MASK{' ':<31} (0x{group['mask']:04X}U)\n"
                content += f"#define {group['id']}_OFFSET{' ':<28} ({group['offset']}U)\n"
                content += f"#define {group['id']}_IDENTIFICATION{' ':<20} \"{group.get('identification', group['id'])}\"\n"
                content += "\n"

        content += """/*==================================================================================================
*                              FUNCTION DECLARATIONS
==================================================================================================*/
extern const Dio_ConfigType Dio_Config;

#endif /* DIO_CFG_H */
"""
        
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        self.status_var.set("DIO_CFG.H generated successfully")

    def save_driver_files(self):
        """Save all DIO driver files"""
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
            
        directory_path = filedialog.askdirectory(title="Select Directory to Save Driver Files")
        if not directory_path: 
            return
            
        try:
            os.makedirs(directory_path, exist_ok=True) # Added this line
            
            dio_cfg_h_content = self.code_text.get(1.0, tk.END)
            generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dio_h_content = DIO_H_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            dio_c_content = DIO_C_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            
            files_to_save = [
                ('Dio_Cfg.h', dio_cfg_h_content),
                ('Dio.h', dio_h_content),
                ('Dio.c', dio_c_content),
            ]

            for filename, content in files_to_save:
                try:
                    with open(os.path.join(directory_path, filename), 'w', encoding='utf-8') as f:
                        f.write(content)
                except Exception as e:
                    messagebox.showerror("Error", f"Failed to save file '{filename}': {str(e)}")
                    self.status_var.set(f"Error saving {filename}")
                    return # Stop saving other files if one fails
            
            # Create README file
            readme_content = f'''# AUTOSAR DIO Driver Files

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source ARXML: {os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'}

## Files Generated:

- Dio_Cfg.h: DIO Configuration Header
- Dio.h: DIO Driver Header
- Dio.c: DIO Driver Implementation

## Configuration Summary:

### Ports: {len(self.config_data['ports'])}
{chr(10).join([f"- {port['symbolic_name']} (ID: {port['id']})" for port in self.config_data['ports']]) if self.config_data['ports'] else "- No ports configured"}

### Channels: {len(self.config_data['channels'])}
{chr(10).join([f"- {channel['symbolic_name']} (ID: {channel['id']}, Port: {channel['port']})" for channel in self.config_data['channels']]) if self.config_data['channels'] else "- No channels configured"}

### Channel Groups: {len(self.config_data['channel_groups'])}
{chr(10).join([f"- {group['id']} (Port: {group['port']}, Mask: 0x{group['mask']:04X}, Offset: {group['offset']})" for group in self.config_data['channel_groups']]) if self.config_data['channel_groups'] else "- No channel groups configured"}

## API Features:
- DEV_ERROR_DETECT: {'ENABLED'} if self.config_data['dev_error_detect'] else {'DISABLED'}
- VERSION_INFO_API: {'ENABLED'} if self.config_data['version_info_api'] else {'DISABLED'}
- FLIP_CHANNEL_API: {'ENABLED'} if self.config_data['flip_channel_api'] else {'DISABLED'}
- MASKED_WRITE_PORT_API: {'ENABLED'} if self.config_data['masked_write_port_api'] else {'DISABLED'}
'''
            
            with open(os.path.join(directory_path, 'README.md'), 'w', encoding='utf-8') as f:
                f.write(readme_content)

            messagebox.showinfo("Success", f"DIO driver files saved successfully to:\n{directory_path}")
            self.status_var.set("Driver files saved successfully")

        except Exception as e:
            messagebox.showerror("Error", f"Failed to save files: {str(e)}")
            self.status_var.set("Error saving files")

def main():
    root = tk.Tk()
    root.title("ARXML to DIO Config Converter")
    root.geometry("1200x800")
    
    app = ARXMLtoDIOConfigGUI(root)
    app.grid(row=0, column=0, sticky='nsew', padx=5, pady=5)
    
    root.columnconfigure(0, weight=1)
    root.rowconfigure(0, weight=1)
    
    root.mainloop()

if __name__ == '__main__':
    main()