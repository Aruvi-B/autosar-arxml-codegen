import tkinter as tk
from tkinter import ttk, messagebox

class ChannelEditor(ttk.Frame):
    def __init__(self, parent, config_data, on_change_callback=None):
        super().__init__(parent, padding="10")
        self.config_data = config_data
        self.on_change_callback = on_change_callback

        self.setup_ui()
        self.load_channels()

    def setup_ui(self):
        channels_frame = ttk.LabelFrame(self, text="Manual Channel Editor", padding="10")
        channels_frame.pack(fill='x', expand=True)
        channels_frame.columnconfigure(0, weight=1)

        # Channels treeview
        self.channels_tree = ttk.Treeview(channels_frame, columns=('ID', 'Name', 'Port'),
                                          show='headings', height=5)
        self.channels_tree.heading('ID', text='Channel ID')
        self.channels_tree.heading('Name', text='Symbolic Name')
        self.channels_tree.heading('Port', text='Port Ref')
        self.channels_tree.grid(row=0, column=0, columnspan=3, sticky=(tk.W, tk.E))
        self.channels_tree.bind("<Double-1>", self.edit_channel_event)

        # Channel buttons
        buttons_frame = ttk.Frame(channels_frame)
        buttons_frame.grid(row=1, column=0, columnspan=3, pady=(5, 0))
        
        ttk.Button(buttons_frame, text="Add Channel",
                   command=self.add_channel).pack(side="left")
        ttk.Button(buttons_frame, text="Edit Selected",
                   command=self.edit_channel).pack(side="left", padx=5)
        ttk.Button(buttons_frame, text="Delete Selected",
                   command=self.delete_channel).pack(side="left")

    def load_channels(self):
        for item in self.channels_tree.get_children():
            self.channels_tree.delete(item)
        for channel in self.config_data.get('channels', []):
            self.channels_tree.insert('', 'end', values=(channel['id'], channel['symbolic_name'], channel['port']))

    def add_channel(self):
        self.channel_dialog()

    def edit_channel_event(self, event):
        self.edit_channel()

    def edit_channel(self):
        selection = self.channels_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a channel to edit.", parent=self)
            return

        item = self.channels_tree.item(selection[0])
        values = item['values']
        self.channel_dialog(channel_id=values[0], channel_name=values[1], port=values[2], edit_index=selection[0])

    def delete_channel(self):
        selection = self.channels_tree.selection()
        if not selection:
            messagebox.showwarning("Warning", "Please select a channel to delete.", parent=self)
            return

        if messagebox.askyesno("Confirm", "Delete selected channel?", parent=self):
            item = self.channels_tree.item(selection[0])
            values = item['values']

            self.config_data['channels'] = [
                ch for ch in self.config_data['channels']
                if not (ch['id'] == values[0] and ch['symbolic_name'] == values[1])
            ]
            self.channels_tree.delete(selection[0])
            if self.on_change_callback:
                self.on_change_callback()

    def channel_dialog(self, channel_id='', channel_name='', port='', edit_index=None):
        dialog = tk.Toplevel(self)
        dialog.title("Add Channel" if edit_index is None else "Edit Channel")
        dialog.geometry("350x200")
        dialog.resizable(False, False)
        dialog.transient(self)
        dialog.grab_set()

        main_frame = ttk.Frame(dialog, padding="10")
        main_frame.pack(fill="both", expand=True)

        ttk.Label(main_frame, text="Channel ID:").grid(row=0, column=0, padx=10, pady=5, sticky=tk.W)
        id_var = tk.StringVar(value=str(channel_id))
        ttk.Entry(main_frame, textvariable=id_var).grid(row=0, column=1, padx=10, pady=5)

        ttk.Label(main_frame, text="Symbolic Name:").grid(row=1, column=0, padx=10, pady=5, sticky=tk.W)
        name_var = tk.StringVar(value=channel_name)
        ttk.Entry(main_frame, textvariable=name_var).grid(row=1, column=1, padx=10, pady=5)

        ttk.Label(main_frame, text="Port Reference:").grid(row=2, column=0, padx=10, pady=5, sticky=tk.W)
        port_var = tk.StringVar(value=str(port))
        ttk.Entry(main_frame, textvariable=port_var).grid(row=2, column=1, padx=10, pady=5)

        def save_channel():
            try:
                ch_id = int(id_var.get())
                ch_name = name_var.get().strip()
                ch_port = int(port_var.get())

                if not ch_name:
                    messagebox.showerror("Error", "Channel name cannot be empty", parent=dialog)
                    return

                channel_data = {'id': ch_id, 'symbolic_name': ch_name, 'port': ch_port}

                if edit_index is None:
                    self.config_data['channels'].append(channel_data)
                else:
                    for i, ch in enumerate(self.config_data['channels']):
                        if ch['id'] == channel_id and ch['symbolic_name'] == channel_name:
                            self.config_data['channels'][i] = channel_data
                            break
                
                self.load_channels()
                if self.on_change_callback:
                    self.on_change_callback()
                dialog.destroy()

            except ValueError:
                messagebox.showerror("Error", "Invalid numeric values", parent=dialog)

        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=20)

        ttk.Button(button_frame, text="Save", command=save_channel).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=dialog.destroy).pack(side="left")
