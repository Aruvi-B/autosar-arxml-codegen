import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import xml.etree.ElementTree as ET
import os
from datetime import datetime
# from .drivers.spi_code import SPI_H_TEMPLATE, SPI_C_TEMPLATE

class ARXMLtoSPIGenerator(ttk.Frame):
    def __init__(self, parent):
        super().__init__(parent)
        
        # Configuration data
        self.config_data = {
            'vendor_id': 1810,
            'module_id': 83,
            'instance_id': 0,
            'sw_major_version': 1,
            'sw_minor_version': 0,
            'sw_patch_version': 0,
            
            # SpiGeneral
            'cancel_api': True,
            'channel_buffers_allowed': 1,
            'dev_error_detect': True,
            'hw_status_api': True,
            'interruptible_seq_allowed': True,
            'level_delivered': 2,
            'main_function_period': 0.01,
            'support_concurrent_sync_transmit': False,
            'user_callback_header_file': '',
            'version_info_api': True,
            
            # SpiDriver
            'max_channel': 0,
            'max_job': 0,
            'max_sequence': 0,
            
            # SpiPublishedInformation
            'max_hw_unit': 4,
            
            # Configuration arrays
            'sequences': [],
            'channels': [],
            'channel_lists': [],
            'jobs': [],
            'external_devices': [],
            'dem_events': []
        }
        
        self.arxml_file_path = None
        self.status_var = tk.StringVar(value="Ready")
        self.setup_ui()

    def setup_ui(self):
        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        title_label = ttk.Label(self, text="ARXML to SPI_CFG.H Generator", 
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

        self.generate_btn = ttk.Button(buttons_frame, text="Generate SPI_CFG.H", command=self.generate_spi_cfg_h)
        self.generate_btn.pack(side=tk.LEFT, padx=(0, 10))

        self.save_btn = ttk.Button(buttons_frame, text="Save SPI_CFG.H", command=self.save_spi_cfg_h)
        self.save_btn.pack(side=tk.LEFT)

        code_frame = ttk.LabelFrame(right_frame, text="Generated Spi_Cfg.h", padding="10")
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
            self.generate_spi_cfg_h()
            
        except ET.ParseError as e:
            messagebox.showerror("Parse Error", f"Failed to parse ARXML file: {str(e)}")
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred: {str(e)}")

    def extract_config_from_arxml(self, root):
        # Clear existing data
        self.config_data['sequences'] = []
        self.config_data['channels'] = []
        self.config_data['channel_lists'] = []
        self.config_data['jobs'] = []
        self.config_data['external_devices'] = []
        self.config_data['dem_events'] = []

        # Find all containers
        containers = root.findall('.//ECUC-CONTAINER-VALUE')
        
        for container in containers:
            short_name_elem = container.find('SHORT-NAME')
            if short_name_elem is None:
                continue

            short_name = short_name_elem.text

            if short_name == 'SpiGeneral':
                self.extract_spi_general(container)
            elif short_name == 'SpiDriver':
                self.extract_spi_driver(container)
            elif short_name == 'SpiPublishedInformation':
                self.extract_spi_published_info(container)
            elif short_name == 'SpiSequence':
                self.extract_spi_sequence(container)
            elif short_name == 'SpiChannel':
                self.extract_spi_channel(container)
            elif short_name == 'SpiChannelList':
                self.extract_spi_channel_list(container)
            elif short_name == 'SpiJob':
                self.extract_spi_job(container)
            elif short_name == 'SpiExternalDevice':
                self.extract_spi_external_device(container)
            elif short_name == 'SpiDemEventParameterRefs':
                self.extract_dem_events(container)

    def extract_spi_general(self, container):
        """Extract SpiGeneral configuration"""
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        text_params = container.findall('.//ECUC-TEXTUAL-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SpiCancelApi':
                self.config_data['cancel_api'] = value
            elif param_name == 'SpiDevErrorDetect':
                self.config_data['dev_error_detect'] = value
            elif param_name == 'SpiHwStatusApi':
                self.config_data['hw_status_api'] = value
            elif param_name == 'SpiInterruptibleSeqAllowed':
                self.config_data['interruptible_seq_allowed'] = value
            elif param_name == 'SpiSupportConcurrentSyncTransmit':
                self.config_data['support_concurrent_sync_transmit'] = value
            elif param_name == 'SpiVersionInfoApi':
                self.config_data['version_info_api'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiChannelBuffersAllowed':
                self.config_data['channel_buffers_allowed'] = value
            elif param_name == 'SpiLevelDelivered':
                self.config_data['level_delivered'] = value
            elif param_name == 'SpiMainFunctionPeriod':
                self.config_data['main_function_period'] = value
        
        for param in text_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'SpiUserCallbackHeaderFile':
                self.config_data['user_callback_header_file'] = value

    def extract_spi_driver(self, container):
        """Extract SpiDriver configuration"""
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiMaxChannel':
                self.config_data['max_channel'] = value
            elif param_name == 'SpiMaxJob':
                self.config_data['max_job'] = value
            elif param_name == 'SpiMaxSequence':
                self.config_data['max_sequence'] = value

    def extract_spi_published_info(self, container):
        """Extract SpiPublishedInformation configuration"""
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiMaxHwUnit':
                self.config_data['max_hw_unit'] = value

    def extract_spi_sequence(self, container):
        """Extract SpiSequence configuration"""
        sequence = {
            'interruptible_sequence': False,
            'seq_end_notification': False,
            'sequence_id': 0,
            'job_assignment': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SpiInterruptibleSequence':
                sequence['interruptible_sequence'] = value
            elif param_name == 'SpiSeqEndNotification':
                sequence['seq_end_notification'] = value
            elif param_name == 'SpiJobAssignment':
                sequence['job_assignment'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiSequenceId':
                sequence['sequence_id'] = value
        
        self.config_data['sequences'].append(sequence)

    def extract_spi_channel(self, container):
        """Extract SpiChannel configuration"""
        channel = {
            'channel_id': 0,
            'channel_type': False,
            'data_width': 8,
            'default_data': 0,
            'eb_max_length': 1,
            'ib_n_buffers': 1,
            'transfer_start': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SpiChannelType':
                channel['channel_type'] = value
            elif param_name == 'SpiTransferStart':
                channel['transfer_start'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiChannelId':
                channel['channel_id'] = value
            elif param_name == 'SpiDataWidth':
                channel['data_width'] = value
            elif param_name == 'SpiDefaultData':
                channel['default_data'] = value
            elif param_name == 'SpiEbMaxLength':
                channel['eb_max_length'] = value
            elif param_name == 'SpiIbNBuffers':
                channel['ib_n_buffers'] = value
        
        self.config_data['channels'].append(channel)

    def extract_spi_channel_list(self, container):
        """Extract SpiChannelList configuration"""
        channel_list = {
            'channel_index': 0,
            'channel_assignment': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SpiChannelAssignment':
                channel_list['channel_assignment'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiChannelIndex':
                channel_list['channel_index'] = value
        
        self.config_data['channel_lists'].append(channel_list)

    def extract_spi_job(self, container):
        """Extract SpiJob configuration"""
        job = {
            'hw_unit_synchronous': 'ASYNCHRONOUS',
            'job_end_notification': False,
            'job_id': 0,
            'job_priority': 0,
            'device_assignment': False
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SpiJobEndNotification':
                job['job_end_notification'] = value
            elif param_name == 'SpiDeviceAssignment':
                job['device_assignment'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiJobId':
                job['job_id'] = value
            elif param_name == 'SpiJobPriority':
                job['job_priority'] = value
        
        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'SpiHwUnitSynchronous':
                job['hw_unit_synchronous'] = value
        
        self.config_data['jobs'].append(job)

    def extract_spi_external_device(self, container):
        """Extract SpiExternalDevice configuration"""
        device = {
            'baudrate': 1000000,
            'cs_identifier': '',
            'cs_polarity': 'HIGH',
            'cs_selection': 'CS_VIA_GPIO',
            'data_shift_edge': 'LEADING',
            'enable_cs': True,
            'hw_unit': 'CSIB0',
            'shift_clock_idle_level': 'HIGH',
            'time_clk2cs': 0,
            'cs_behavior': 'CS_KEEP_ASSERTED',
            'time_cs2clk': 0,
            'time_cs2cs': 0
        }
        
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        num_params = container.findall('.//ECUC-NUMERICAL-PARAM-VALUE')
        text_params = container.findall('.//ECUC-TEXTUAL-PARAM-VALUE')
        enum_params = container.findall('.//ECUC-ENUMERATION-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SpiEnableCs':
                device['enable_cs'] = value
        
        for param in num_params:
            param_name = self.get_param_name(param)
            value = self.get_num_value(param)
            
            if param_name == 'SpiBaudrate':
                device['baudrate'] = value
            elif param_name == 'SpiTimeClk2Cs':
                device['time_clk2cs'] = value
            elif param_name == 'SpiTimeCs2Clk':
                device['time_cs2clk'] = value
            elif param_name == 'SpiTimeCs2Cs':
                device['time_cs2cs'] = value
        
        for param in text_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'SpiCsIdentifier':
                device['cs_identifier'] = value
        
        for param in enum_params:
            param_name = self.get_param_name(param)
            value = self.get_text_value(param)
            
            if param_name == 'SpiCsPolarity':
                device['cs_polarity'] = value
            elif param_name == 'SpiCsSelection':
                device['cs_selection'] = value
            elif param_name == 'SpiDataShiftEdge':
                device['data_shift_edge'] = value
            elif param_name == 'SpiHwUnit':
                device['hw_unit'] = value
            elif param_name == 'SpiShiftClockIdleLevel':
                device['shift_clock_idle_level'] = value
            elif param_name == 'SpiCsBehavior':
                device['cs_behavior'] = value
        
        self.config_data['external_devices'].append(device)

    def extract_dem_events(self, container):
        """Extract DEM events configuration"""
        bool_params = container.findall('.//ECUC-BOOLEAN-PARAM-VALUE')
        
        for param in bool_params:
            param_name = self.get_param_name(param)
            value = self.get_bool_value(param)
            
            if param_name == 'SPI_E_HARDWARE_ERROR':
                self.config_data['dem_events'].append({
                    'name': 'SPI_E_HARDWARE_ERROR',
                    'enabled': value
                })

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
        
        config_text += f"SPI General Configuration:\n"
        config_text += f"- SPI_CANCEL_API: {'STD_ON' if self.config_data.get('cancel_api') else 'STD_OFF'}\n"
        config_text += f"- SPI_CHANNEL_BUFFERS_ALLOWED: {self.config_data.get('channel_buffers_allowed', 0)}\n"
        config_text += f"- SPI_DEV_ERROR_DETECT: {'STD_ON' if self.config_data.get('dev_error_detect') else 'STD_OFF'}\n"
        config_text += f"- SPI_HW_STATUS_API: {'STD_ON' if self.config_data.get('hw_status_api') else 'STD_OFF'}\n"
        config_text += f"- SPI_INTERRUPTIBLE_SEQ_ALLOWED: {'STD_ON' if self.config_data.get('interruptible_seq_allowed') else 'STD_OFF'}\n"
        config_text += f"- SPI_LEVEL_DELIVERED: {self.config_data.get('level_delivered', 0)}\n"
        config_text += f"- SPI_MAIN_FUNCTION_PERIOD: {self.config_data.get('main_function_period', 0.0)}\n"
        config_text += f"- SPI_SUPPORT_CONCURRENT_SYNC_TRANSMIT: {'STD_ON' if self.config_data.get('support_concurrent_sync_transmit') else 'STD_OFF'}\n"
        config_text += f"- SPI_USER_CALLBACK_HEADER_FILE: {self.config_data.get('user_callback_header_file', '')}\n"
        config_text += f"- SPI_VERSION_INFO_API: {'STD_ON' if self.config_data.get('version_info_api') else 'STD_OFF'}\n\n"
        
        config_text += f"SPI Driver Configuration:\n"
        config_text += f"- SPI_MAX_CHANNEL: {self.config_data.get('max_channel', 0)}\n"
        config_text += f"- SPI_MAX_JOB: {self.config_data.get('max_job', 0)}\n"
        config_text += f"- SPI_MAX_SEQUENCE: {self.config_data.get('max_sequence', 0)}\n\n"
        
        config_text += f"SPI Published Information:\n"
        config_text += f"- SPI_MAX_HW_UNIT: {self.config_data.get('max_hw_unit', 0)}\n\n"
        
        config_text += f"Sequences ({len(self.config_data.get('sequences', []))}):\n"
        for i, seq in enumerate(self.config_data.get('sequences', [])):
            config_text += f"- Sequence {i}: ID={seq.get('sequence_id', 0)}, Interruptible={seq.get('interruptible_sequence', False)}\n"
        
        config_text += f"\nChannels ({len(self.config_data.get('channels', []))}):\n"
        for i, ch in enumerate(self.config_data.get('channels', [])):
            config_text += f"- Channel {i}: ID={ch.get('channel_id', 0)}, Width={ch.get('data_width', 0)}, Type={'EB' if ch.get('channel_type') else 'IB'}\n"
        
        config_text += f"\nJobs ({len(self.config_data.get('jobs', []))}):\n"
        for i, job in enumerate(self.config_data.get('jobs', [])):
            config_text += f"- Job {i}: ID={job.get('job_id', 0)}, Priority={job.get('job_priority', 0)}, Sync={job.get('hw_unit_synchronous', 'ASYNCHRONOUS')}\n"
        
        config_text += f"\nExternal Devices ({len(self.config_data.get('external_devices', []))}):\n"
        for i, dev in enumerate(self.config_data.get('external_devices', [])):
            config_text += f"- Device {i}: Baudrate={dev.get('baudrate', 0)}, HW Unit={dev.get('hw_unit', 'CSIB0')}, CS={dev.get('cs_polarity', 'HIGH')}, Behavior={dev.get('cs_behavior', 'CS_KEEP_ASSERTED')}\n"
        
        self.config_text.config(state='normal')
        self.config_text.delete(1.0, tk.END)
        self.config_text.insert(1.0, config_text)
        self.config_text.config(state='disabled')

    def generate_spi_cfg_h(self):
        """Generate the SPI_CFG.H file content"""
        content = f"""#ifndef SPI_CFG_H_
#define SPI_CFG_H_

/*
 * Developer Aruvi B and Auroshaa from CreamCollar
 * Generated SPI Configuration Header
 * Generated from ARXML: {os.path.basename(self.arxml_file_path) if self.arxml_file_path else 'Unknown'}
 * Generated on: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
 */

/* Module identification */
#define SPI_VENDOR_ID                    ({self.config_data['vendor_id']}U)
#define SPI_MODULE_ID                    ({self.config_data['module_id']}U)
#define SPI_INSTANCE_ID                  ({self.config_data['instance_id']}U)

/* Module version information */
#define SPI_SW_MAJOR_VERSION             ({self.config_data['sw_major_version']}U)
#define SPI_SW_MINOR_VERSION             ({self.config_data['sw_minor_version']}U)
#define SPI_SW_PATCH_VERSION             ({self.config_data['sw_patch_version']}U)

/* SPI General Configuration */
#define SPI_CANCEL_API                   {'STD_ON' if self.config_data['cancel_api'] else 'STD_OFF'}
#define SPI_CHANNEL_BUFFERS_ALLOWED      ({self.config_data['channel_buffers_allowed']}U)
#define SPI_DEV_ERROR_DETECT             {'STD_ON' if self.config_data['dev_error_detect'] else 'STD_OFF'}
#define SPI_HW_STATUS_API                {'STD_ON' if self.config_data['hw_status_api'] else 'STD_OFF'}
#define SPI_INTERRUPTIBLE_SEQ_ALLOWED    {'STD_ON' if self.config_data['interruptible_seq_allowed'] else 'STD_OFF'}
#define SPI_LEVEL_DELIVERED              ({self.config_data['level_delivered']}U)
#define SPI_MAIN_FUNCTION_PERIOD         ({self.config_data['main_function_period']}f)
#define SPI_SUPPORT_CONCURRENT_SYNC_TRANSMIT {'STD_ON' if self.config_data['support_concurrent_sync_transmit'] else 'STD_OFF'}
#define SPI_VERSION_INFO_API             {'STD_ON' if self.config_data['version_info_api'] else 'STD_OFF'}

/* User callback header file */
"""
        
        if self.config_data['user_callback_header_file']:
            content += f"#include \"{self.config_data['user_callback_header_file']}\"\n"
        
        content += f"""
/* SPI Driver Configuration */
#define SPI_MAX_CHANNEL                  ({self.config_data['max_channel']}U)
#define SPI_MAX_JOB                      ({self.config_data['max_job']}U)
#define SPI_MAX_SEQUENCE                 ({self.config_data['max_sequence']}U)

/* SPI Published Information */
#define SPI_MAX_HW_UNIT                  ({self.config_data['max_hw_unit']}U)

/* SPI Error Codes */
#define SPI_E_PARAM_CHANNEL              (0x0AU)
#define SPI_E_PARAM_JOB                  (0x0BU)
#define SPI_E_PARAM_SEQ                  (0x0CU)
#define SPI_E_PARAM_LENGTH               (0x0DU)
#define SPI_E_PARAM_UNIT                 (0x0EU)
#define SPI_E_PARAM_POINTER              (0x10U)
#define SPI_E_UNINIT                     (0x1AU)
#define SPI_E_SEQ_PENDING                (0x2AU)
#define SPI_E_SEQ_IN_PROCESS             (0x3AU)
#define SPI_E_ALREADY_INITIALIZED        (0x4AU)

/* Service IDs */
#define SPI_INIT_SID                     (0x00U)
#define SPI_DEINIT_SID                   (0x01U)
#define SPI_WRITEIB_SID                  (0x02U)
#define SPI_ASYNCTRANSMIT_SID            (0x03U)
#define SPI_READIB_SID                   (0x04U)
#define SPI_SETUPEB_SID                  (0x05U)
#define SPI_GETSTATUS_SID                (0x06U)
#define SPI_GETJOBRESULT_SID             (0x07U)
#define SPI_GETSEQUENCERESULT_SID        (0x08U)
#define SPI_GETVERSIONINFO_SID           (0x09U)
#define SPI_SYNCTRANSMIT_SID             (0x0AU)
#define SPI_GETHWUNITSTATUS_SID          (0x0BU)
#define SPI_CANCEL_SID                   (0x0CU)
#define SPI_SETASYNCMODE_SID             (0x0DU)
#define SPI_MAINFUNCTION_HANDLING_SID    (0x10U)

/* SPI Job Result */
#define SPI_JOB_OK                       (0x00U)
#define SPI_JOB_PENDING                  (0x01U)
#define SPI_JOB_FAILED                   (0x02U)
#define SPI_JOB_QUEUED                   (0x03U)

/* SPI Sequence Result */
#define SPI_SEQ_OK                       (0x00U)
#define SPI_SEQ_PENDING                  (0x01U)
#define SPI_SEQ_FAILED                   (0x02U)
#define SPI_SEQ_CANCELLED                (0x03U)

/* SPI Status */
#define SPI_UNINIT                       (0x00U)
#define SPI_IDLE                         (0x01U)
#define SPI_BUSY                         (0x02U)

/* SPI Hardware Unit Status */
#define SPI_IDLE                         (0x00U)
#define SPI_BUSY                         (0x01U)

/* SPI Asynchronous Mode */
#define SPI_POLLING_MODE                 (0x00U)
#define SPI_INTERRUPT_MODE               (0x01U)

"""

        # Add Channel definitions
        if self.config_data['channels']:
            content += "/* SPI Channel Symbolic Names */\n"
            for i, channel in enumerate(self.config_data['channels']):
                content += f"#define SpiConf_SpiChannel_Channel_{channel['channel_id']}     ({channel['channel_id']}U)\n"
            
            content += "\n/* SPI Channel Configuration */\n"
            for i, channel in enumerate(self.config_data['channels']):
                content += f"#define SPI_CHANNEL_{channel['channel_id']}_DATA_WIDTH          ({channel['data_width']}U)\n"
                content += f"#define SPI_CHANNEL_{channel['channel_id']}_DEFAULT_DATA        (0x{channel['default_data']:04X}U)\n"
                content += f"#define SPI_CHANNEL_{channel['channel_id']}_EB_MAX_LENGTH       ({channel['eb_max_length']}U)\n"
                content += f"#define SPI_CHANNEL_{channel['channel_id']}_IB_N_BUFFERS        ({channel['ib_n_buffers']}U)\n"
                content += f"#define SPI_CHANNEL_{channel['channel_id']}_TYPE                ({'SPI_EB' if channel['channel_type'] else 'SPI_IB'})\n\n"

        # Add Job definitions
        if self.config_data['jobs']:
            content += "/* SPI Job Symbolic Names */\n"
            for i, job in enumerate(self.config_data['jobs']):
                content += f"#define SpiConf_SpiJob_Job_{job['job_id']}                ({job['job_id']}U)\n"
            
            content += "\n/* SPI Job Configuration */\n"
            for i, job in enumerate(self.config_data['jobs']):
                content += f"#define SPI_JOB_{job['job_id']}_PRIORITY                    ({job['job_priority']}U)\n"
                content += f"#define SPI_JOB_{job['job_id']}_HW_UNIT_SYNC                (SPI_{job['hw_unit_synchronous']})\n"
                if job['job_end_notification']:
                    content += f"#define SPI_JOB_{job['job_id']}_END_NOTIFICATION            (STD_ON)\n"
                content += "\n"

        # Add Sequence definitions
        if self.config_data['sequences']:
            content += "/* SPI Sequence Symbolic Names */\n"
            for i, seq in enumerate(self.config_data['sequences']):
                content += f"#define SpiConf_SpiSequence_Sequence_{seq['sequence_id']}   ({seq['sequence_id']}U)\n"
            
            content += "\n/* SPI Sequence Configuration */\n"
            for i, seq in enumerate(self.config_data['sequences']):
                content += f"#define SPI_SEQUENCE_{seq['sequence_id']}_INTERRUPTIBLE          ({'STD_ON' if seq['interruptible_sequence'] else 'STD_OFF'})\n"
                if seq['seq_end_notification']:
                    content += f"#define SPI_SEQUENCE_{seq['sequence_id']}_END_NOTIFICATION      (STD_ON)\n"
                content += "\n"

        # Add External Device definitions
        if self.config_data['external_devices']:
            content += "/* SPI External Device Configuration */\n"
            for i, dev in enumerate(self.config_data['external_devices']):
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_BAUDRATE            ({dev['baudrate']}U)\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_CS_BEHAVIOR         (SPI_{dev['cs_behavior']})\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_CS_POLARITY         (SPI_CS_{dev['cs_polarity']})\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_CS_SELECTION        (SPI_{dev['cs_selection']})\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_DATA_SHIFT_EDGE     (SPI_{dev['data_shift_edge']})\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_HW_UNIT             (SPI_{dev['hw_unit']})\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_SHIFT_CLOCK_IDLE    (SPI_{dev['shift_clock_idle_level']})\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_TIME_CLK2CS         ({dev['time_clk2cs']}U)\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_TIME_CS2CLK         ({dev['time_cs2clk']}U)\n"
                content += f"#define SPI_EXTERNAL_DEVICE_{i}_TIME_CS2CS          ({dev['time_cs2cs']}U)\n"
                if dev['cs_identifier']:
                    content += f"#define SPI_EXTERNAL_DEVICE_{i}_CS_IDENTIFIER       \"{dev['cs_identifier']}\"\n"
                content += "\n"

        # Add HW Unit definitions
        content += f"""/* SPI Hardware Unit Definitions */
#define SPI_CSIB0                        (0x00U)
#define SPI_CSIB1                        (0x01U)
#define SPI_CSIB2                        (0x02U)
#define SPI_CSIB3                        (0x03U)

/* SPI CS Behavior Definitions */
#define SPI_CS_KEEP_ASSERTED             (0x00U)
#define SPI_CS_TOGGLE                    (0x01U)

/* SPI CS Polarity Definitions */
#define SPI_CS_HIGH                      (0x01U)
#define SPI_CS_LOW                       (0x00U)

/* SPI CS Selection Definitions */
#define SPI_CS_VIA_GPIO                  (0x00U)
#define SPI_CS_VIA_PERIPHERAL_ENGINE     (0x01U)

/* SPI Data Shift Edge Definitions */
#define SPI_LEADING                      (0x00U)
#define SPI_TRAILING                     (0x01U)

/* SPI Synchronous Mode Definitions */
#define SPI_ASYNCHRONOUS                 (0x00U)
#define SPI_SYNCHRONOUS                  (0x01U)

/* SPI Buffer Type Definitions */
#define SPI_IB                           (0x00U)
#define SPI_EB                           (0x01U)

"""

        # Add configuration counts
        content += f"/* Configuration Counts */\n"
        content += f"#define SPI_CONFIG_CHANNELS_COUNT        ({len(self.config_data['channels'])}U)\n"
        content += f"#define SPI_CONFIG_JOBS_COUNT            ({len(self.config_data['jobs'])}U)\n"
        content += f"#define SPI_CONFIG_SEQUENCES_COUNT       ({len(self.config_data['sequences'])}U)\n"
        content += f"#define SPI_CONFIG_EXTERNAL_DEVICES_COUNT ({len(self.config_data['external_devices'])}U)\n"
        
        # Add DEM events if any
        if self.config_data['dem_events']:
            content += f"\n/* DEM Event Configuration */\n"
            for event in self.config_data['dem_events']:
                content += f"#define SPI_DEM_{event['name']}_ENABLED      ({'STD_ON' if event['enabled'] else 'STD_OFF'})\n"
        
        content += "\n#endif /* SPI_CFG_H_ */\n"
        
        # Display generated code
        self.code_text.delete(1.0, tk.END)
        self.code_text.insert(1.0, content)
        
        # messagebox.showinfo("Success", "SPI_CFG.H generated successfully!")

    def save_spi_cfg_h(self):
        if not self.code_text.get(1.0, tk.END).strip():
            messagebox.showwarning("Warning", "Please generate the code first")
            return
        
        file_path = filedialog.asksaveasfilename(
            title="Save SPI_CFG.H File",
            # filename="Spi_Cfg.h",
            defaultextension=".h",
            filetypes=[("Header files", "*.h"), ("All files", "*.*")]
        )
        
        if file_path:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(self.code_text.get(1.0, tk.END))
                messagebox.showinfo("Success", f"SPI_CFG.H saved successfully!\n\nLocation: {file_path}")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save file: {str(e)}")

    
