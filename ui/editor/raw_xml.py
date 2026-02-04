import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import xml.etree.ElementTree as ET
import os
from copy import deepcopy

class RawXmlPanel:
    def __init__(self, parent, status_logger=None, on_change_callback=None):
        self.frame = ttk.Frame(parent)
        self.status_logger = status_logger
        self.xml_tree = None
        self.xml_root = None
        self.xml_file_path = None
        self.on_change_callback = on_change_callback
        self.item_to_elem = {}
        self.is_modified = False
        self.auto_sync = True  # Enable automatic synchronization
        self.suppress_text_events = False  # Flag to prevent recursive events
        
        self.setup_ui()

    def setup_ui(self):
        # Enhanced toolbar with better organization
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill="x", padx=5, pady=2)

        # File operations
        file_frame = ttk.LabelFrame(toolbar, text="File Operations", padding=2)
        file_frame.pack(side="left", padx=2, fill="y")
        
        ttk.Button(file_frame, text="Open ARXML", command=self.open_file).pack(side="left", padx=1)
        ttk.Button(file_frame, text="Refresh File", command=self.refresh_file).pack(side="left", padx=1)
        ttk.Button(file_frame, text="Save Changes", command=self.save_raw_changes).pack(side="left", padx=1)
        ttk.Button(file_frame, text="Save As...", command=self.download_arxml).pack(side="left", padx=1)

        # XML operations
        xml_frame = ttk.LabelFrame(toolbar, text="XML Operations", padding=2)
        xml_frame.pack(side="left", padx=2, fill="y")
        
        ttk.Button(xml_frame, text="Format XML", command=self.format_xml).pack(side="left", padx=1)
        ttk.Button(xml_frame, text="Validate XML", command=self.validate_arxml_file).pack(side="left", padx=1)

        # View operations
        view_frame = ttk.LabelFrame(toolbar, text="View Options", padding=2)
        view_frame.pack(side="left", padx=2, fill="y")
        
        ttk.Button(view_frame, text="Expand All", command=self.expand_all).pack(side="left", padx=1)
        ttk.Button(view_frame, text="Collapse All", command=self.collapse_all).pack(side="left", padx=1)
        # ttk.Button(view_frame, text="Sync Views", command=self.manual_sync).pack(side="left", padx=1)

        # Auto-sync toggle
        self.auto_sync_var = tk.BooleanVar(value=True)
        # ttk.Checkbutton(view_frame, text="Auto-sync", 
                    #    variable=self.auto_sync_var,
                    #    command=self.toggle_auto_sync).pack(side="left", padx=2)

        # Status indicator
        self.status_var = tk.StringVar(value="No file loaded")
        status_label = ttk.Label(toolbar, textvariable=self.status_var, font=('TkDefaultFont', 8))
        status_label.pack(side="right", padx=10)

        # Main content area with paned window
        main_pane = ttk.PanedWindow(self.frame, orient=tk.HORIZONTAL)
        main_pane.pack(fill="both", expand=True, padx=5, pady=2)

        # Left panel - Tree view with node operations
        left_frame = ttk.Frame(main_pane)
        main_pane.add(left_frame, weight=1)

        # Tree operations toolbar
        tree_toolbar = ttk.Frame(left_frame)
        tree_toolbar.pack(fill="x", pady=(0, 2))
        
        ttk.Label(tree_toolbar, text="XML Structure:", font=('TkDefaultFont', 9, 'bold')).pack(side="left")
        
        # Node operation buttons
        node_ops_frame = ttk.Frame(tree_toolbar)
        node_ops_frame.pack(side="right")
        
        ttk.Button(node_ops_frame, text="Add", command=self.add_node, width=6).pack(side="left", padx=1)
        ttk.Button(node_ops_frame, text="Edit", command=self.edit_node, width=6).pack(side="left", padx=1)
        ttk.Button(node_ops_frame, text="Delete", command=self.delete_node, width=6).pack(side="left", padx=1)

        # Tree view
        tree_container = ttk.Frame(left_frame)
        tree_container.pack(fill="both", expand=True)

        yscroll = ttk.Scrollbar(tree_container, orient="vertical")
        xscroll = ttk.Scrollbar(tree_container, orient="horizontal")
        self.tree = ttk.Treeview(tree_container, show="tree", 
                                yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.config(command=self.tree.yview)
        xscroll.config(command=self.tree.xview)
        
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        tree_container.rowconfigure(0, weight=1)
        tree_container.columnconfigure(0, weight=1)
        
        self.tree.bind("<<TreeviewSelect>>", self.on_tree_select)
        self.tree.bind("<Button-3>", self.show_context_menu)
        self.tree.bind("<Double-1>", self.edit_node)

        # Right panel - Text editor with search and line numbers
        right_frame = ttk.Frame(main_pane)
        main_pane.add(right_frame, weight=2)

        # Text editor toolbar with search
        text_toolbar = ttk.Frame(right_frame)
        text_toolbar.pack(fill="x", pady=(0, 2))
        
        ttk.Label(text_toolbar, text="XML Content:", font=('TkDefaultFont', 9, 'bold')).pack(side="left")
        
        # Search functionality in text toolbar
        search_frame = ttk.Frame(text_toolbar)
        search_frame.pack(side="right")
        
        ttk.Label(search_frame, text="Search:").pack(side="left")
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=15)
        self.search_entry.pack(side="left", padx=2)
        self.search_entry.bind('<KeyRelease>', self.search_text)
        self.search_entry.bind('<Return>', self.find_next)
        
        ttk.Button(search_frame, text="Next", command=self.find_next, width=5).pack(side="left", padx=1)
        ttk.Button(search_frame, text="Clear", command=self.clear_search, width=5).pack(side="left", padx=1)

        self.modified_indicator = ttk.Label(text_toolbar, text="", foreground="red")
        self.modified_indicator.pack(side="right", padx=(0, 10))

        # Text editor with line numbers - moved to left side
        editor_frame = ttk.Frame(right_frame)
        editor_frame.pack(fill="both", expand=True)

        # Line numbers text widget (left side)
        self.line_numbers = tk.Text(editor_frame, width=5, padx=3, takefocus=0,
                                   border=0, state='disabled', wrap='none',
                                   bg="#ffffff", fg="#000000", font=('Courier', 10))
        self.line_numbers.pack(side="left", fill="y")

        # Main text editor
        self.text_editor = tk.Text(editor_frame, wrap="none", undo=True, maxundo=50, 
                                  font=('Courier', 10), selectbackground="#0078d7",selectforeground="white")
        self.text_editor.pack(side="left", fill="both", expand=True)
        
        # Scrollbars for text editor
        y_scroll_text = ttk.Scrollbar(editor_frame, orient="vertical")
        y_scroll_text.pack(side="right", fill="y")
        x_scroll_text = ttk.Scrollbar(right_frame, orient="horizontal")
        x_scroll_text.pack(side="bottom", fill="x")
        
        self.text_editor.configure(yscrollcommand=y_scroll_text.set, xscrollcommand=x_scroll_text.set)
        y_scroll_text.configure(command=self.sync_scroll)
        x_scroll_text.configure(command=self.text_editor.xview)

        # Bind text editor events for synchronization
        self.text_editor.bind('<KeyRelease>', self.on_text_change)
        self.text_editor.bind('<ButtonRelease-1>', self.on_text_cursor)
        self.text_editor.bind('<MouseWheel>', self.update_line_numbers)
        self.text_editor.tag_raise("sel") 
        self.text_editor.bind('<Control-s>', lambda e: self.save_raw_changes())

        # Context menu setup
        self.setup_context_menu()
        self.update_line_numbers()

    def toggle_auto_sync(self):
        """Toggle automatic synchronization between views"""
        self.auto_sync = self.auto_sync_var.get()
        self.log_message(f"Auto-sync {'enabled' if self.auto_sync else 'disabled'}")

    def manual_sync(self):
        """Manually synchronize views"""
        if self.xml_tree:
            self.sync_views_from_text()
            self.log_message("Views synchronized manually")

    def setup_context_menu(self):
        """Setup context menu for tree view"""
        self.context_menu = tk.Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Add Child Node", command=self.add_node)
        self.context_menu.add_command(label="Edit Node", command=self.edit_node)
        self.context_menu.add_command(label="Delete Node", command=self.delete_node)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Expand Node", command=self.expand_selected)
        self.context_menu.add_command(label="Collapse Node", command=self.collapse_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copy Element Name", command=self.copy_element_name)
        self.context_menu.add_command(label="Show Element Info", command=self.show_element_info)

    def show_context_menu(self, event):
        """Show context menu on right-click"""
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def add_node(self):
        """Add new XML node"""
        selected = self.tree.selection()
        if not selected and not self.xml_root:
            messagebox.showwarning("No Selection", "No parent node selected and no root element exists")
            return

        dialog = NodeEditDialog(self.frame, "Add New Node")
        if dialog.result:
            tag_name, short_name, text_content = dialog.result
            
            try:
                # Create new element
                new_elem = ET.Element(tag_name)
                if text_content:
                    new_elem.text = text_content
                
                # Add SHORT-NAME if provided
                if short_name:
                    short_name_elem = ET.SubElement(new_elem, "SHORT-NAME")
                    short_name_elem.text = short_name

                # Add to in-memory tree
                if selected:
                    parent_elem = self.item_to_elem[selected[0]]
                    parent_elem.append(new_elem)
                else:
                    # Create new root
                    self.xml_root = new_elem
                    self.xml_tree = ET.ElementTree(self.xml_root)

                self.set_modified(True)
                # Rebuild tree and text views to ensure consistency
                self.build_tree_from_content(update_text=False)
                self.sync_views_from_tree()
                self.log_message(f"Added node: {tag_name}")
                
            except Exception as e:
                messagebox.showerror("Add Error", f"Failed to add node: {e}")

    def edit_node(self, event=None):
        """Edit selected XML node"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a node to edit")
            return

        elem = self.item_to_elem.get(selected[0])
        if not elem:
            return

        # Get current values
        tag_name = self.localname(elem.tag)
        short_name = self.get_short_name(elem)
        text_content = elem.text.strip() if elem.text else ""

        dialog = NodeEditDialog(self.frame, "Edit Node", tag_name, short_name, text_content)
        if dialog.result:
            new_tag, new_short_name, new_text = dialog.result
            
            try:
                # Update element
                elem.tag = new_tag
                elem.text = new_text if new_text else None
                
                # Update or add SHORT-NAME
                short_name_elem = None
                for child in elem:
                    if self.localname(child.tag) == "SHORT-NAME":
                        short_name_elem = child
                        break
                
                if new_short_name:
                    if short_name_elem is None:
                        short_name_elem = ET.SubElement(elem, "SHORT-NAME")
                    short_name_elem.text = new_short_name
                elif short_name_elem is not None:
                    elem.remove(short_name_elem)

                # Update tree display
                display_name = new_short_name if new_short_name else new_tag
                self.tree.item(selected[0], text=display_name)
                
                self.set_modified(True)
                self.sync_views_from_tree()
                self.log_message(f"Edited node: {new_tag}")
                
            except Exception as e:
                messagebox.showerror("Edit Error", f"Failed to edit node: {e}")

    def delete_node(self):
        """Delete selected XML node"""
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("No Selection", "Please select a node to delete")
            return

        elem = self.item_to_elem.get(selected[0])
        if not elem:
            return

        # Confirm deletion
        element_name = self.tree.item(selected[0], "text")
        if not messagebox.askyesno("Confirm Delete", f"Delete node '{element_name}' and all its children?"):
            return

        try:
            # Remove from XML tree
            if elem == self.xml_root:
                self.xml_root = None
                self.xml_tree = None
            else:
                # Find parent and remove
                for parent_item, parent_elem in self.item_to_elem.items():
                    if elem in parent_elem:
                        parent_elem.remove(elem)
                        break

            # Remove from tree view
            self.tree.delete(selected[0])
            del self.item_to_elem[selected[0]]
            
            self.set_modified(True)
            self.sync_views_from_tree()
            self.log_message(f"Deleted node: {element_name}")
            
        except Exception as e:
            messagebox.showerror("Delete Error", f"Failed to delete node: {e}")

    def expand_selected(self):
        """Expand selected tree node"""
        selected = self.tree.selection()
        if selected:
            self.tree.item(selected[0], open=True)

    def collapse_selected(self):
        """Collapse selected tree node"""
        selected = self.tree.selection()
        if selected:
            self.tree.item(selected[0], open=False)

    def copy_element_name(self):
        """Copy selected element name to clipboard"""
        selected = self.tree.selection()
        if selected:
            element_name = self.tree.item(selected[0], "text")
            self.frame.clipboard_clear()
            self.frame.clipboard_append(element_name)
            self.log_message(f"Copied '{element_name}' to clipboard")

    def show_element_info(self):
        """Show detailed information about selected element"""
        selected = self.tree.selection()
        if not selected:
            return
        
        elem = self.item_to_elem.get(selected[0])
        if not elem:
            return

        info_dialog = tk.Toplevel(self.frame)
        info_dialog.title("Element Information")
        info_dialog.geometry("500x300")
        info_dialog.transient(self.frame.winfo_toplevel())

        main_frame = ttk.Frame(info_dialog, padding=10)
        main_frame.pack(fill="both", expand=True)

        info_text = tk.Text(main_frame, wrap="word", height=15)
        info_text.pack(fill="both", expand=True, pady=(0, 10))

        short_name = self.get_short_name(elem)
        info_content = f"""Element Information:
{'='*50}

Tag: {self.localname(elem.tag)}
Short Name: {short_name if short_name else 'N/A'}
Text Content: {elem.text.strip() if elem.text else 'N/A'}
Children: {len(list(elem))}
Attributes: {len(elem.attrib)}

Attributes:
"""
        for key, value in elem.attrib.items():
            info_content += f"  {key}: {value}\n"

        if not elem.attrib:
            info_content += "  (No attributes)\n"

        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")

        ttk.Button(main_frame, text="Close", command=info_dialog.destroy).pack()

    def search_text(self, event=None):
        """Search in text editor"""
        search_term = self.search_var.get()
        if not search_term:
            self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
            return

        # Clear previous highlights
        self.text_editor.tag_remove("search_highlight", "1.0", tk.END)
        
        # Configure highlight tag
        self.text_editor.tag_configure("search_highlight", background="yellow")
        
        # Search and highlight all occurrences
        start_pos = "1.0"
        count = 0
        while True:
            start_pos = self.text_editor.search(search_term, start_pos, stopindex=tk.END)
            if not start_pos:
                break
            end_pos = f"{start_pos}+{len(search_term)}c"
            self.text_editor.tag_add("search_highlight", start_pos, end_pos)
            start_pos = end_pos
            count += 1
        
        if count > 0:
            # Move to first occurrence
            first_pos = self.text_editor.search(search_term, "1.0", stopindex=tk.END)
            if first_pos:
                self.text_editor.see(first_pos)
                self.text_editor.mark_set(tk.INSERT, first_pos)

    def find_next(self, event=None):
        """Find next occurrence of search term"""
        search_term = self.search_var.get()
        if not search_term:
            return

        current_pos = self.text_editor.index(tk.INSERT)
        next_pos = self.text_editor.search(search_term, f"{current_pos}+1c", stopindex=tk.END)
        
        if next_pos:
            self.text_editor.see(next_pos)
            self.text_editor.mark_set(tk.INSERT, next_pos)
        else:
            # Wrap to beginning
            next_pos = self.text_editor.search(search_term, "1.0", stopindex=tk.END)
            if next_pos:
                self.text_editor.see(next_pos)
                self.text_editor.mark_set(tk.INSERT, next_pos)

    def clear_search(self):
        """Clear search field and highlights"""
        self.search_var.set("")
        self.text_editor.tag_remove("search_highlight", "1.0", tk.END)

    def sync_scroll(self, *args):
        """Sync scrolling between text editor and line numbers"""
        self.text_editor.yview(*args)
        self.line_numbers.yview(*args)

    def update_line_numbers(self, event=None):
        """Update line numbers in sync with text editor"""
        try:
            self.line_numbers.config(state='normal')
            self.line_numbers.delete("1.0", tk.END)
            
            line_count = int(self.text_editor.index('end-1c').split('.')[0])
            line_number_string = "\n".join(str(i) for i in range(1, line_count))
            
            self.line_numbers.insert("1.0", line_number_string)
            self.line_numbers.config(state='disabled')
            
            # Sync scroll position
            self.line_numbers.yview_moveto(self.text_editor.yview()[0])
        except Exception:
            pass

    def on_text_change(self, event=None):
        """Handle text editor changes with auto-sync"""
        if self.suppress_text_events:
            return
            
        self.set_modified(True)
        self.update_line_numbers()
        
        # Auto-sync if enabled
        if self.auto_sync:
            # Debounce rapid changes
            if hasattr(self, '_sync_timer'):
                self.frame.after_cancel(self._sync_timer)
            self._sync_timer = self.frame.after(1000, self.sync_views_from_text)  # 1 second delay

    def _serialize_xml_to_string(self, root_element):
        """Serializes an XML element to a string, handling default namespace."""
        if '}' in root_element.tag:
            namespace_uri = root_element.tag.split('}')[0][1:]
            ET.register_namespace('', namespace_uri)
        
        # Create a deepcopy to avoid modifying the original tree with indent
        formatted_root = deepcopy(root_element)
        self.indent(formatted_root)
        content = ET.tostring(formatted_root, encoding='unicode')
        
        # Add XML declaration if missing
        if not content.startswith('<?xml'):
            content = '<?xml version="1.0" encoding="utf-8"?>\n' + content
            
        return content

    def sync_views_from_text(self):
        """Synchronize tree view from text editor content"""
        try:
            content = self.get_content()
            if content.strip():
                self.xml_root = ET.fromstring(content)
                self.xml_tree = ET.ElementTree(self.xml_root)
                self.build_tree_from_content(update_text=False)
                
                # Notify parent component
                if self.on_change_callback:
                    self.on_change_callback(self.xml_tree)
        except ET.ParseError:
            # Ignore parse errors during typing
            pass
        except Exception as e:
            self.log_message(f"Sync error: {e}")

    def sync_views_from_tree(self):
        """Synchronize text editor from tree structure"""
        if self.xml_tree:
            try:
                content = self._serialize_xml_to_string(self.xml_root)
                
                # Preserve cursor position and suppress events
                cursor_pos = self.text_editor.index(tk.INSERT)
                self.suppress_text_events = True
                
                self.text_editor.delete("1.0", tk.END)
                self.text_editor.insert("1.0", content)
                self.update_line_numbers()
                
                try:
                    self.text_editor.mark_set(tk.INSERT, cursor_pos)
                except:
                    pass
                
                self.suppress_text_events = False
                    
                # Notify parent component
                if self.on_change_callback:
                    self.on_change_callback(self.xml_tree)
            except Exception as e:
                self.suppress_text_events = False
                self.log_message(f"Tree sync error: {e}")

    def set_modified(self, is_modified):
        """Update modification status"""
        self.is_modified = is_modified
        if is_modified:
            self.modified_indicator.config(text="● Modified")
        else:
            self.modified_indicator.config(text="")

    def refresh_file(self):
        """Refresh file from disk"""
        if not self.xml_file_path or not os.path.exists(self.xml_file_path):
            messagebox.showwarning("No File", "No file path available or file does not exist")
            return

        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "Current file has unsaved changes. Refresh anyway?\n\nYes: Discard changes and refresh\nNo: Keep current changes\nCancel: Do nothing"
            )
            if result is None:  # Cancel
                return
            elif result is False:  # No - keep changes
                return

        try:
            with open(self.xml_file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.set_content(content)
            self.set_modified(False)
            self.log_message(f"Refreshed file: {os.path.basename(self.xml_file_path)}")
            
        except Exception as e:
            messagebox.showerror("Refresh Error", f"Failed to refresh file: {e}")
            self.log_message(f"Refresh error: {e}")

    def open_file(self):
        """Open ARXML file with enhanced error handling"""
        path = filedialog.askopenfilename(
            title="Select ARXML/XML file",
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.*")]
        )
        if not path:
            return

        try:
            with open(path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.xml_file_path = path
            self.set_content(content)
            self.set_modified(False)
            self.status_var.set(f"Loaded: {os.path.basename(path)}")
            self.log_message(f"Opened file: {os.path.basename(path)}")
            
        except UnicodeDecodeError:
            # Try different encodings
            for encoding in ['latin-1', 'cp1252', 'iso-8859-1']:
                try:
                    with open(path, 'r', encoding=encoding) as f:
                        content = f.read()
                    self.xml_file_path = path
                    self.set_content(content)
                    self.set_modified(False)
                    self.status_var.set(f"Loaded: {os.path.basename(path)} ({encoding})")
                    self.log_message(f"Opened file with {encoding} encoding: {os.path.basename(path)}")
                    return
                except UnicodeDecodeError:
                    continue
            
            messagebox.showerror("Encoding Error", "Could not decode file with any supported encoding")
            
        except Exception as e:
            messagebox.showerror("File Open Error", f"Failed to open file: {e}")
            self.log_message(f"File open error: {e}")

    def set_content(self, content):
        """Set content in text editor and rebuild tree"""
        self.suppress_text_events = True
        self.text_editor.delete("1.0", tk.END)
        self.text_editor.insert("1.0", content)
        self.build_tree_from_content()
        self.update_line_numbers()
        self.suppress_text_events = False

    def get_content(self):
        """Get current content from text editor"""
        return self.text_editor.get("1.0", tk.END + "-1c")

    def _get_item_path(self, item):
        """Generate a path of names from the root to the item."""
        path = []
        while item:
            path.insert(0, self.tree.item(item, "text"))
            item = self.tree.parent(item)
        return tuple(path)

    def _save_expansion_state(self):
        """Save the expansion state of the tree view."""
        expanded_paths = set()
        
        def traverse(item):
            if self.tree.item(item, "open"):
                expanded_paths.add(self._get_item_path(item))
            for child in self.tree.get_children(item):
                traverse(child)

        for root_item in self.tree.get_children(""):
            traverse(root_item)
        return expanded_paths

    def _restore_expansion_state(self, expanded_paths):
        """Restore the expansion state of the tree view."""
        def traverse(item):
            path = self._get_item_path(item)
            if path in expanded_paths:
                self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                traverse(child)

        for root_item in self.tree.get_children(""):
            traverse(root_item)

    def build_tree_from_content(self, update_text=True):
        """Build tree view from current XML content, preserving expansion state."""
        expanded_state = self._save_expansion_state()

        self.tree.delete(*self.tree.get_children())
        self.item_to_elem.clear()
        
        try:
            content = self.get_content() if update_text else ET.tostring(self.xml_root, encoding='unicode')
            if not content.strip():
                return
            
            if update_text:
                self.xml_root = ET.fromstring(content)
                self.xml_tree = ET.ElementTree(self.xml_root)
            
            root_short = self.get_short_name(self.xml_root)
            root_label = root_short if root_short else self.localname(self.xml_root.tag)
            root_item = self.tree.insert("", "end", text=root_label, open=True)
            self.item_to_elem[root_item] = self.xml_root

            self._build_tree_recursive(self.xml_root, root_item)
            
            self._restore_expansion_state(expanded_state)
            
            self.log_message("Tree view updated from XML content")
            
        except ET.ParseError as e:
            if update_text:  # Only show error if parsing from text
                self.log_message(f"XML Parse Error: {e}")
        except Exception as e:
            self.log_message(f"Error building tree: {e}")

    def _build_tree_recursive(self, elem, parent_item):
        """Recursively build tree structure"""
        for child in elem:
            # If an element is a SHORT-NAME, but has children, it's probably a structural element
            # that happens to be named SHORT-NAME. So, only skip it if it's a leaf.
            if self.localname(child.tag).upper() == "SHORT-NAME" and len(child) == 0:
                continue

            short = self.get_short_name(child)
            display_name = short if short else self.localname(child.tag)
            
            item = self.tree.insert(parent_item, "end", text=display_name, open=False)
            self.item_to_elem[item] = child
            self._build_tree_recursive(child, item)

    def on_tree_select(self, event):
        """Handle tree selection - highlight element in text editor without replacing content"""
        if self.suppress_text_events: # Prevent recursion
            return
            
        sel = self.tree.selection()
        if not sel:
            return
        
        item = sel[0]
        elem = self.item_to_elem.get(item)
        
        if elem is None:
            return

        try:
            element_tag = self.localname(elem.tag)
            
            # Find the occurrence index of this element among those with the same tag
            occurrence = -1
            i = 0
            for e in self.xml_root.iter():
                if self.localname(e.tag) == element_tag:
                    if e is elem:
                        occurrence = i
                        break
                    i += 1
            
            if occurrence == -1:
                return # Element not in the main tree for some reason

            # Now search for the (occurrence + 1)th match in the text editor.
            self.text_editor.tag_remove("tree_highlight", "1.0", tk.END)
            self.text_editor.tag_configure("tree_highlight", background="#F8EE8E", foreground="black")

            search_term = f"<{element_tag}"
            start_pos = "1.0"
            for _ in range(occurrence + 1):
                # The `+1c` is to start search after the previous match
                start_pos = self.text_editor.search(search_term, f"{start_pos}+1c" if start_pos != "1.0" else start_pos, stopindex=tk.END)
                if not start_pos:
                    return
            
            # Find the end of the element for highlighting
            closing_tag = f"</{element_tag}>"
            end_pos = self.text_editor.search(closing_tag, start_pos, stopindex=tk.END)
            
            if end_pos:
                # Include the closing tag in the highlight
                end_pos = f"{end_pos}+{len(closing_tag)}c"
            else:
                # Handle self-closing tags
                end_pos = self.text_editor.search("/>", start_pos, stopindex=f"{start_pos} lineend")
                if end_pos:
                    end_pos = f"{end_pos}+2c"
                else:
                    end_pos = f"{start_pos} lineend"
            
            self.text_editor.tag_add("tree_highlight", start_pos, end_pos)
            self.text_editor.see(start_pos)
            
            # Synchronize cursor position with tree selection
            self.suppress_text_events = True
            self.text_editor.mark_set(tk.INSERT, start_pos)
            self.suppress_text_events = False

        except Exception as e:
            self.log_message(f"Selection highlight error: {e}")

    def on_text_cursor(self, event=None):
        if self.suppress_text_events:
            return
            
        cursor_pos = self.text_editor.index(tk.INSERT)
        
        # Find the tag at the cursor
        tag_search_pos = self.text_editor.search(r"<[^\s>/]+", cursor_pos, backwards=True, regexp=True, stopindex="1.0")
        if not tag_search_pos:
            return

        tag_name_end = self.text_editor.search(r"[\s>]", tag_search_pos, regexp=True)
        if not tag_name_end:
            return
            
        tag_name = self.text_editor.get(f"{tag_search_pos}+1c", tag_name_end)

        # Count occurrences of this tag before the cursor
        occurrence = 0
        pos = "1.0"
        while True:
            pos = self.text_editor.search(f"<{tag_name}", f"{pos}+1c", stopindex=tag_search_pos)
            if not pos:
                break
            occurrence += 1

        # Find the corresponding element in the XML tree
        try:
            target_elem = None
            i = 0
            for e in self.xml_root.iter():
                if self.localname(e.tag) == tag_name:
                    if i == occurrence:
                        target_elem = e
                        break
                    i += 1
            
            if target_elem is None:
                return

            # Find the item in the tree view and select it
            for item, elem in self.item_to_elem.items():
                if elem is target_elem:
                    self.suppress_text_events = True
                    if self.tree.selection() != (item,):
                        self.tree.selection_set(item)
                        self.tree.see(item)
                    self.suppress_text_events = False
                    break
        except Exception as e:
            self.log_message(f"Text cursor sync error: {e}")

    def expand_all(self):
        """Expand all tree nodes"""
        for item in self.tree.get_children():
            self.tree.item(item, open=True)
            self._expand_recursive(item)
        self.log_message("Expanded all nodes")

    def _expand_recursive(self, item):
        """Recursively expand tree nodes"""
        for child in self.tree.get_children(item):
            self.tree.item(child, open=True)
            self._expand_recursive(child)

    def collapse_all(self):
        """Collapse all tree nodes"""
        for item in self.tree.get_children():
            self.tree.item(item, open=False)
            self._collapse_recursive(item)
        self.log_message("Collapsed all nodes")

    def _collapse_recursive(self, item):
        """Recursively collapse tree nodes"""
        for child in self.tree.get_children(item):
            self.tree.item(child, open=False)
            self._collapse_recursive(child)

    def save_raw_changes(self):
        """Save changes with complete file preservation"""
        if not self.is_modified and self.xml_file_path:
            messagebox.showinfo("No Changes", "No changes to save.")
            return

        try:
            raw_content = self.get_content()
            if not raw_content.strip():
                messagebox.showwarning("Empty Content", "Cannot save empty content.")
                return

            # Parse to validate XML but preserve original formatting
            try:
                # Just validate, don't change the content
                ET.fromstring(raw_content)
            except ET.ParseError as e:
                messagebox.showerror("XML Error", f"Invalid XML syntax: {e}")
                return

            # Save to file if we have a file path
            if self.xml_file_path:
                # Create backup
                backup_path = self.xml_file_path + ".backup"
                if os.path.exists(self.xml_file_path):
                    try:
                        with open(self.xml_file_path, 'r', encoding='utf-8') as f:
                            backup_content = f.read()
                        with open(backup_path, 'w', encoding='utf-8') as f:
                            f.write(backup_content)
                        self.log_message(f"Backup created: {backup_path}")
                    except Exception as e:
                        self.log_message(f"Backup creation failed: {e}")

                # Save the exact content from text editor (preserving user formatting)
                with open(self.xml_file_path, 'w', encoding='utf-8') as f:
                    f.write(raw_content)
                
                # Update internal XML tree for synchronization
                self.xml_root = ET.fromstring(raw_content)
                self.xml_tree = ET.ElementTree(self.xml_root)
                
                self.set_modified(False)
                self.status_var.set(f"Saved: {os.path.basename(self.xml_file_path)}")
                self.log_message(f"Changes saved to: {os.path.basename(self.xml_file_path)}")
            else:
                # No file path, trigger Save As
                self.download_arxml()

            # Notify parent component
            if self.on_change_callback:
                self.on_change_callback(self.xml_tree)

            # Update tree view to reflect changes
            self.build_tree_from_content()

        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save changes: {e}")
            self.log_message(f"Save error: {e}")

    def download_arxml(self):
        """Save As functionality preserving content exactly"""
        content = self.get_content()
        if not content.strip():
            messagebox.showwarning("No Content", "No content to save!")
            return

        # Determine default filename
        if self.xml_file_path:
            default_name = os.path.splitext(os.path.basename(self.xml_file_path))[0] + "_modified.arxml"
        else:
            default_name = "configuration.arxml"

        save_path = filedialog.asksaveasfilename(
            defaultextension=".arxml",
            filetypes=[("ARXML files", "*.arxml"), ("XML files", "*.xml"), ("All files", "*.*")],
            initialfile=default_name
        )
        
        if not save_path:
            return
        
        try:
            # Save exact content from text editor
            with open(save_path, 'w', encoding='utf-8') as f:
                f.write(content)

            # Update internal state
            try:
                self.xml_root = ET.fromstring(content)
                self.xml_tree = ET.ElementTree(self.xml_root)
            except ET.ParseError:
                pass  # Content might be invalid, but still save it

            self.xml_file_path = save_path
            self.set_modified(False)
            self.status_var.set(f"Saved: {os.path.basename(save_path)}")
            self.log_message(f"File saved as: {os.path.basename(save_path)}")
            
        except Exception as e:
            messagebox.showerror("Save Error", f"Failed to save file: {e}")
            self.log_message(f"Save error: {e}")

    def format_xml(self):
        """Format XML with improved formatting"""
        try:
            content = self.get_content()
            if not content.strip():
                messagebox.showinfo("No Content", "No content to format.")
                return

            root = ET.fromstring(content)
            formatted_content = self._serialize_xml_to_string(root)
            
            self.set_content(formatted_content)
            self.set_modified(True)
            self.log_message("XML formatted successfully")
            
        except ET.ParseError as e:
            messagebox.showerror("Format Error", f"Cannot format invalid XML: {e}")
            self.log_message(f"Format error: {e}")
        except Exception as e:
            messagebox.showerror("Format Error", f"Formatting failed: {e}")
            self.log_message(f"Format error: {e}")

    def validate_arxml_file(self):
        """Enhanced ARXML validation"""
        try:
            content = self.get_content()
            if not content.strip():
                messagebox.showwarning("No Content", "No content to validate")
                return

            root = ET.fromstring(content)
            validation_results = []
            
            # Basic XML structure checks
            if 'AUTOSAR' not in root.tag:
                validation_results.append(("Warning", "Root element is not AUTOSAR"))
            
            if 'autosar.org' in str(ET.tostring(root, encoding='unicode')):
                validation_results.append(("Info", "AUTOSAR namespace detected"))
            
            # Check for required elements
            packages = [el for el in root.iter() if self.localname(el.tag) == 'AR-PACKAGES']
            if packages:
                validation_results.append(("Info", f"Found {len(packages)} AR-PACKAGES element(s)"))
            else:
                validation_results.append(("Warning", "No AR-PACKAGES element found"))
            
            # Check for AR-PACKAGE elements
            ar_packages = [el for el in root.iter() if self.localname(el.tag) == 'AR-PACKAGE']
            if ar_packages:
                validation_results.append(("Info", f"Found {len(ar_packages)} AR-PACKAGE element(s)"))
            else:
                validation_results.append(("Warning", "No AR-PACKAGE elements found"))

            # Check for SHORT-NAME elements
            short_names = [el for el in root.iter() if self.localname(el.tag) == 'SHORT-NAME']
            if short_names:
                validation_results.append(("Info", f"Found {len(short_names)} SHORT-NAME element(s)"))

            # Show results
            if not validation_results or all(r[0] == 'Info' for r in validation_results):
                messagebox.showinfo("Validation Success", "Valid ARXML file structure detected!")
                self.log_message("ARXML validation passed")
            else:
                self.show_validation_results(validation_results)
                
        except ET.ParseError as e:
            messagebox.showerror("Validation Error", f"Invalid XML syntax: {e}")
            self.log_message(f"Validation error: {e}")
        except Exception as e:
            messagebox.showerror("Validation Error", f"Validation failed: {e}")
            self.log_message(f"Validation error: {e}")

    def show_validation_results(self, results):
        """Display validation results in a dialog"""
        dialog = tk.Toplevel(self.frame)
        dialog.title("ARXML Validation Results")
        dialog.geometry("600x400")
        dialog.transient(self.frame.winfo_toplevel())
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="ARXML Validation Results", 
                 font=('TkDefaultFont', 11, 'bold')).pack(anchor="w")
        
        results_text = tk.Text(main_frame, wrap="word", height=15)
        results_text.pack(fill="both", expand=True, pady=10)
        
        results_content = "Validation Report:\n" + "="*50 + "\n\n"
        
        for result_type, message in results:
            icon = {"Info": "ℹ️", "Warning": "⚠️", "Error": "❌"}.get(result_type, "📋")
            results_content += f"{icon} {result_type}: {message}\n"
        
        results_content += f"\nOverall Status: "
        if any(r[0] == "Error" for r in results):
            results_content += "❌ Issues found that need attention"
        elif any(r[0] == "Warning" for r in results):
            results_content += "⚠️ File is valid but has warnings"
        else:
            results_content += "✅ Valid ARXML structure"
        
        results_text.insert("1.0", results_content)
        results_text.configure(state="disabled")
        
        ttk.Button(main_frame, text="Close", command=dialog.destroy).pack()

    def log_message(self, message):
        """Log message to status logger if available"""
        if self.status_logger:
            self.status_logger.log(message)

    # Helper methods
    def localname(self, tag: str) -> str:
        """Strip namespace from tag"""
        return tag.split('}', 1)[1] if '}' in tag else tag

    def get_short_name(self, elem: ET.Element):
        """Get SHORT-NAME text from element"""
        for child in elem:
            if self.localname(child.tag).upper() == "SHORT-NAME":
                return (child.text or "").strip()
        return None

    def strip_namespaces(self, elem: ET.Element):
        """Return copy of element with namespaces removed"""
        new_elem = deepcopy(elem)
        def _strip(e):
            e.tag = self.localname(e.tag)
            for child in e:
                _strip(child)
        _strip(new_elem)
        return new_elem

    def strip_whitespace(self, elem):
        """Recursively strip whitespace from text/tail"""
        if elem.text:
            elem.text = elem.text.strip()
        for child in elem:
            self.strip_whitespace(child)
            if child.tail:
                child.tail = child.tail.strip()

    def indent(self, elem, level=0):
        """Pretty-print XML with consistent indentation"""
        i = "\n" + level * "    "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "    "
            for child in elem:
                self.indent(child, level + 1)
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
        else:
            if elem.text:
                elem.text = elem.text.strip()
            if not elem.tail or not elem.tail.strip():
                elem.tail = i

    # Integration methods for main application
    def load_arxml_file(self, file_path):
        """Load ARXML file - called by main application"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            self.xml_file_path = file_path
            self.set_content(content)
            self.set_modified(False)
            self.status_var.set(f"Loaded: {os.path.basename(file_path)}")
            self.log_message(f"Loaded ARXML file: {os.path.basename(file_path)}")
            return True
            
        except Exception as e:
            messagebox.showerror("Load Error", f"Failed to load ARXML file: {e}")
            self.log_message(f"Load error: {e}")
            return False

    def get_xml_tree(self):
        """Get current XML tree"""
        return self.xml_tree

    def get_xml_root(self):
        """Get current XML root element"""
        return self.xml_root

    def set_xml_tree(self, xml_tree):
        """Set XML tree from external source"""
        if xml_tree is not None:
            self.xml_tree = xml_tree
            self.xml_root = xml_tree.getroot()
            
            # Update both text editor and tree view
            formatted_root = deepcopy(self.xml_root)
            self.indent(formatted_root)
            content = ET.tostring(formatted_root, encoding='unicode')
            
            # Add XML declaration
            if not content.startswith('<?xml'):
                content = '<?xml version="1.0" encoding="utf-8"?>\n' + content
                
            self.set_content(content)
            self.set_modified(False)
            self.log_message("XML tree updated from external source")

    def has_unsaved_changes(self):
        """Check if there are unsaved changes"""
        return self.is_modified

    def get_file_path(self):
        """Get current file path"""
        return self.xml_file_path

    def close_file(self):
        """Close current file with save confirmation"""
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes", 
                "There are unsaved changes. Do you want to save them?"
            )
            if result is True:  # Yes - save
                self.save_raw_changes()
            elif result is None:  # Cancel
                return False
        
        # Clear content
        self.text_editor.delete("1.0", tk.END)
        self.tree.delete(*self.tree.get_children())
        self.item_to_elem.clear()
        self.xml_tree = None
        self.xml_root = None
        self.xml_file_path = None
        self.set_modified(False)
        self.status_var.set("No file loaded")
        self.log_message("File closed")
        return True


class NodeEditDialog:
    """Dialog for editing XML nodes"""
    def __init__(self, parent, title, tag_name="", short_name="", text_content=""):
        self.result = None
        
        dialog = tk.Toplevel(parent)
        dialog.title(title)
        dialog.geometry("400x300")
        dialog.transient(parent)
        dialog.grab_set()
        
        # Center dialog
        dialog.geometry(f"+{parent.winfo_toplevel().winfo_x() + 50}+{parent.winfo_toplevel().winfo_y() + 50}")
        
        main_frame = ttk.Frame(dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        # Tag name
        ttk.Label(main_frame, text="Element Tag:").grid(row=0, column=0, sticky="w", pady=2)
        self.tag_entry = ttk.Entry(main_frame, width=40)
        self.tag_entry.grid(row=0, column=1, sticky="ew", padx=(5, 0), pady=2)
        self.tag_entry.insert(0, tag_name)
        
        # Short name
        ttk.Label(main_frame, text="Short Name:").grid(row=1, column=0, sticky="w", pady=2)
        self.short_entry = ttk.Entry(main_frame, width=40)
        self.short_entry.grid(row=1, column=1, sticky="ew", padx=(5, 0), pady=2)
        # self.short_entry.insert(0, short_name)
        if short_name is not None:
            self.short_entry.insert(0, short_name)
        
        # Text content
        ttk.Label(main_frame, text="Text Content:").grid(row=2, column=0, sticky="nw", pady=2)
        self.text_widget = tk.Text(main_frame, width=40, height=6)
        self.text_widget.grid(row=2, column=1, sticky="ew", padx=(5, 0), pady=2)
        self.text_widget.insert("1.0", text_content)
        
        main_frame.columnconfigure(1, weight=1)
        
        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.grid(row=3, column=0, columnspan=2, pady=10)
        
        def save_changes():
            tag = self.tag_entry.get().strip()
            if not tag:
                messagebox.showwarning("Invalid Input", "Tag name is required")
                return
            
            short = self.short_entry.get().strip()
            text = self.text_widget.get("1.0", "end-1c").strip()
            
            self.result = (tag, short, text)
            dialog.destroy()
        
        def cancel_changes():
            self.result = None
            dialog.destroy()
        
        ttk.Button(button_frame, text="OK", command=save_changes).pack(side="left", padx=5)
        ttk.Button(button_frame, text="Cancel", command=cancel_changes).pack(side="left", padx=5)
        
        # Focus on tag entry
        self.tag_entry.focus_set()
        if tag_name:
            self.tag_entry.select_range(0, tk.END)
        
        # Wait for dialog to close
        dialog.wait_window()