import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
from .channel_editor import ChannelEditor
from .c_code_templates import DIO_H_TEMPLATE, DIO_C_TEMPLATE

class ARXMLtoDIOConfigGUI(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        self.config_data = {
            'vendor_id': 1810,
            'module_id': 202,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            'dev_error_detect': False,
            'version_info_api': True,
            'flip_channel_api': True,
            'channels': [],
            'ports': [],
            'channel_groups': []
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

        self.channel_editor = ChannelEditor(left_frame, self.config_data, self.display_configuration)
        self.channel_editor.grid(row=1, column=0, sticky='ew', pady=(10, 0))

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
        self.config_data['channels'] = []
        self.config_data['ports'] = []
        self.config_data['channel_groups'] = []
        
        namespaces = {'ar': 'http://autosar.org/schema/r4.0'}
        if hasattr(root, 'nsmap'):
            for prefix, uri in root.nsmap.items():
                if 'autosar' in uri.lower():
                    namespaces['ar'] = uri
                    break

        config_found = False
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
                break

        for container in containers:
            short_name_elem = container.find('SHORT-NAME')
            if short_name_elem is None:
                short_name_elem = container.find('.//{http://autosar.org/schema/r4.0}SHORT-NAME')
            if short_name_elem is None: continue
            short_name = short_name_elem.text

            if 'DioGeneral' in short_name: config_found = True; self._extract_general_config(container)
            elif 'DioPort' in short_name: config_found = True; self._extract_port_config(container, short_name)
            elif 'DioChannel' in short_name and 'Group' not in short_name: config_found = True; self._extract_channel_config(container, short_name)
            elif 'DioChannelGroup' in short_name: config_found = True; self._extract_channel_group_config(container, short_name)

        self.config_data['ports'].sort(key=lambda x: x['id'])
        self.config_data['channels'].sort(key=lambda x: x['id'])
        
        if self.channel_editor: self.channel_editor.load_channels()
        return config_found

    def _extract_general_config(self, container):
        for param in container.findall('.//ECUC-BOOLEAN-PARAM-VALUE'):
            param_name_elem = param.find('SHORT-NAME')
            value_elem = param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                param_name = param_name_elem.text
                value = value_elem.text.strip().lower() in ['true', '1', 'on', 'std_on']
                if 'DevErrorDetect' in param_name: self.config_data['dev_error_detect'] = value
                elif 'VersionInfoApi' in param_name: self.config_data['version_info_api'] = value
                elif 'FlipChannelApi' in param_name: self.config_data['flip_channel_api'] = value

    def _extract_port_config(self, container, container_name):
        port_id, port_symbolic_name = None, container_name
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem, value_elem = param.find('SHORT-NAME'), param.find('VALUE')
            if param_name_elem is not None and value_elem is not None and 'PortId' in param_name_elem.text:
                try: port_id = int(value_elem.text)
                except ValueError: continue
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem, value_elem = param.find('SHORT-NAME'), param.find('VALUE')
            if param_name_elem is not None and value_elem is not None and 'SymbolicName' in param_name_elem.text:
                port_symbolic_name = value_elem.text
        if port_id is None:
            import re
            match = re.search(r'(\d+)', container_name)
            port_id = int(match.group(1)) if match else len(self.config_data['ports'])
        if port_id is not None and not any(p['id'] == port_id for p in self.config_data['ports']):
            self.config_data['ports'].append({'id': port_id, 'symbolic_name': port_symbolic_name or f'DIO_PORT_{port_id}'})

    def _extract_channel_config(self, container, container_name):
        channel_id, channel_symbolic_name, port_ref = None, container_name, 0
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem, value_elem = param.find('SHORT-NAME'), param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                try:
                    if 'ChannelId' in param_name_elem.text: channel_id = int(value_elem.text)
                    elif 'PortRef' in param_name_elem.text: port_ref = int(value_elem.text)
                except ValueError: continue
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem, value_elem = param.find('SHORT-NAME'), param.find('VALUE')
            if param_name_elem is not None and value_elem is not None and 'SymbolicName' in param_name_elem.text:
                channel_symbolic_name = value_elem.text
        if channel_id is None:
            import re
            match = re.search(r'(\d+)', container_name)
            channel_id = int(match.group(1)) if match else len(self.config_data['channels'])
        if channel_id is not None and not any(c['id'] == channel_id for c in self.config_data['channels']):
            self.config_data['channels'].append({'id': channel_id, 'port': port_ref, 'symbolic_name': channel_symbolic_name or f'DIO_CHANNEL_{channel_id}'})

    def _extract_channel_group_config(self, container, container_name):
        group_id, port_mask, port_offset, port_ref = container_name, 0xFF, 0, 0
        for param in container.findall('.//ECUC-NUMERICAL-PARAM-VALUE'):
            param_name_elem, value_elem = param.find('SHORT-NAME'), param.find('VALUE')
            if param_name_elem is not None and value_elem is not None:
                try:
                    if 'PortMask' in param_name_elem.text: port_mask = int(value_elem.text, 0)
                    elif 'PortOffset' in param_name_elem.text: port_offset = int(value_elem.text)
                    elif 'PortRef' in param_name_elem.text: port_ref = int(value_elem.text)
                except ValueError: continue
        for param in container.findall('.//ECUC-TEXTUAL-PARAM-VALUE'):
            param_name_elem, value_elem = param.find('SHORT-NAME'), param.find('VALUE')
            if param_name_elem is not None and value_elem is not None and 'GroupId' in param_name_elem.text:
                group_id = value_elem.text
        if not any(g['id'] == group_id for g in self.config_data['channel_groups']):
            self.config_data['channel_groups'].append({'id': group_id, 'mask': port_mask, 'offset': port_offset, 'port': port_ref})

    def display_configuration(self):
        config_text = f"""Extracted Configuration from ARXML:
{'='*60}

Module Information:
- Vendor ID: {self.config_data['vendor_id']}
- Module ID: {self.config_data['module_id']}
- Instance ID: {self.config_data['instance_id']}
- SW Version: {self.config_data['sw_major_version']}.{self.config_data['sw_minor_version']}.{self.config_data['sw_patch_version']}

API Configuration:
- DIO_DEV_ERROR_DETECT: {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}
- DIO_VERSION_INFO_API: {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}
- DIO_FLIP_CHANNEL_API: {'STD_ON' if self.config_data['flip_channel_api'] else 'STD_OFF'}

Ports Configuration ({len(self.config_data['ports'])}):
"""
        config_text += "- No ports configured\n" if not self.config_data['ports'] else "".join(f"- {port['symbolic_name']} (ID: {port['id']})\n" for port in self.config_data['ports'])
        config_text += f"\nChannels Configuration ({len(self.config_data['channels'])}):\n"
        config_text += "- No channels configured\n" if not self.config_data['channels'] else "".join(f"- {channel['symbolic_name']} (ID: {channel['id']}, Port: {channel['port']})\n" for channel in self.config_data['channels'])
        config_text += f"\nChannel Groups Configuration ({len(self.config_data['channel_groups'])}):\n"
        config_text += "- No channel groups configured\n" if not self.config_data['channel_groups'] else "".join(f"- {group['id']} (Port: {group['port']}, Mask: 0x{group['mask']:04X}, Offset: {group['offset']})\n" for group in self.config_data['channel_groups'])
        config_text += "\nValidation Status:\n" + ("- WARNING: No DIO configuration found\n" if not self.config_data['ports'] and not self.config_data['channels'] else "- Configuration extracted successfully\n")
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')
        if self.channel_editor: self.channel_editor.load_channels()

    def generate_dio_cfg_h(self):
        if not self.config_data['channels'] and not self.config_data['ports']:
            messagebox.showwarning("Warning", "No DIO configuration available.")
            return
        content = f'''#ifndef DIO_CFG_H
#define DIO_CFG_H

/* Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} */

#define DIO_CFG_VENDOR_ID                    ({self.config_data['vendor_id']}U)
#define DIO_CFG_MODULE_ID                    ({self.config_data['module_id']}U)
#define DIO_CFG_INSTANCE_ID                  ({self.config_data['instance_id']}U)

#define DIO_CFG_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)
#define DIO_CFG_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)
#define DIO_CFG_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)

#define DIO_DEV_ERROR_DETECT                 {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}
#define DIO_VERSION_INFO_API                 {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}
#define DIO_FLIP_CHANNEL_API                 {'STD_ON' if self.config_data['flip_channel_api'] else 'STD_OFF'}

'''
        if self.config_data['ports']: content += "\n/* DIO Port Symbolic Names */\n" + "".join(f"#define {port['symbolic_name']:<40} ({port['id']}U)\n" for port in self.config_data['ports'])
        if self.config_data['channels']: content += "\n/* DIO Channel Symbolic Names */\n" + "".join(f"#define {channel['symbolic_name']:<40} ({channel['id']}U)\n" for channel in self.config_data['channels'])
        content += "\n#endif /* DIO_CFG.H */\n"
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        self.status_var.set("DIO_CFG.H generated successfully")

    def save_driver_files(self):
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
        directory_path = filedialog.askdirectory(title="Select Directory to Save Driver Files")
        if not directory_path: return
        try:
            dio_cfg_h_content = self.code_text.get(1.0, tk.END)
            generation_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
            dio_h_content = DIO_H_TEMPLATE.replace('##GENERATION_TIME##', generation_time)
            dio_c_content = DIO_C_TEMPLATE.replace('##GENERATION_TIME##', generation_time)

            std_types_content = '''#ifndef STD_TYPES_H
#define STD_TYPES_H
#include <stdint.h>
#include <stdbool.h>
#ifndef TRUE
#define TRUE                             (1U)
#endif
#ifndef FALSE
#define FALSE                            (0U)
#endif
#ifndef STD_ON
#define STD_ON                           (1U)
#endif
#ifndef STD_OFF
#define STD_OFF                          (0U)
#endif
#ifndef STD_HIGH
#define STD_HIGH                         (1U)
#endif
#ifndef STD_LOW
#define STD_LOW                          (0U)
#endif
#ifndef NULL_PTR
#define NULL_PTR                         ((void*)0)
#endif
typedef uint8_t boolean;
typedef struct {
    uint16_t vendorID;
    uint16_t moduleID;
    uint8_t sw_major_version;
    uint8_t sw_minor_version;
    uint8_t sw_patch_version;
} Std_VersionInfoType;
#endif /* STD_TYPES_H */
'''
            det_h_content = '''#ifndef DET_H
#define DET_H
#include "Std_Types.h"
#define DET_VENDOR_ID                    (1U)
#define DET_MODULE_ID                    (15U)
#if (DIO_DEV_ERROR_DETECT == STD_ON)
void Det_ReportError(uint16_t ModuleId, uint8_t InstanceId, uint8_t ApiId, uint8_t ErrorId);
#else
#define Det_ReportError(ModuleId, InstanceId, ApiId, ErrorId) ((void)0)
#endif
#endif /* DET_H */
'''
            det_c_content = '''#include "Det.h"
#if (DIO_DEV_ERROR_DETECT == STD_ON)
void Det_ReportError(uint16_t ModuleId, uint8_t InstanceId, uint8_t ApiId, uint8_t ErrorId)
{
    (void)ModuleId;
    (void)InstanceId;
    (void)ApiId;
    (void)ErrorId;
}
#endif
'''

            files_to_save = [
                ('Dio_Cfg.h', dio_cfg_h_content),
                ('Dio.h', dio_h_content),
                ('Dio.c', dio_c_content),
                ('Std_Types.h', std_types_content),
                ('Det.h', det_h_content),
                ('Det.c', det_c_content)
            ]

            for filename, content in files_to_save:
                with open(os.path.join(directory_path, filename), 'w', encoding='utf-8') as f: f.write(content)
            
            readme_content = f'''# AUTOSAR DIO Driver Files

Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
Source ARXML: {os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'}

## Files Generated:

- Dio_Cfg.h
- Dio.h
- Dio.c
- Std_Types.h
- Det.h
- Det.c

'''
            with open(os.path.join(directory_path, 'README.md'), 'w', encoding='utf-8') as f: f.write(readme_content)

            messagebox.showinfo("Success", f"Driver files saved to {directory_path}")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to save files: {str(e)}")

if __name__ == '__main__':
    root = tk.Tk()
    root.title("ARXML to DIO Config Converter")
    app = ARXMLtoDIOConfigGUI(root)
    app.pack(fill=tk.BOTH, expand=True)
    root.mainloop()