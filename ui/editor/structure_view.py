import tkinter as tk
from tkinter import ttk, messagebox, Menu, simpledialog
import xml.etree.ElementTree as ET

class StructureViewPanel:
    def __init__(self, parent, status_logger=None, on_change_callback=None):
        self.frame = ttk.Frame(parent)
        self.status_logger = status_logger
        self.xml_tree = None
        self.element_map = {}
        self.on_change_callback = on_change_callback

        self.setup_ui()

    def setup_ui(self):
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill="x", padx=5, pady=2)
        
        ttk.Button(toolbar, text="Refresh", command=self.refresh_table).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Expand All", command=self.expand_all).pack(side="left", padx=2)
        ttk.Button(toolbar, text="Collapse All", command=self.collapse_all).pack(side="left", padx=2)
        
        ttk.Label(toolbar, text="Search").pack(side="right", padx=2)
        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(toolbar, textvariable=self.search_var, width=20)
        search_entry.pack(side="right", padx=2)
        search_entry.bind('<KeyRelease>', self.search_table)
        
        table_frame = ttk.Frame(self.frame)
        table_frame.pack(fill="both", expand=True, padx=5, pady=2)
        
        self.table = ttk.Treeview(
            table_frame,
            columns=("Type", "ShortName", "DefinitionRef", "Value"),
            show="tree headings"
        )
        
        self.table.column("#0", width=800, minwidth=600, stretch=True)
        self.table.column("Type", width=200, minwidth=100, stretch=False, anchor="center")
        self.table.column("ShortName", width=220, minwidth=120, stretch=False)
        self.table.column("DefinitionRef", width=100, minwidth=500, stretch=False)
        self.table.column("Value", width=200, minwidth=100, stretch=False, anchor="center")

        self.table.heading("#0", text="Element Hierarchy", anchor="w")
        self.table.heading("Type", text="Type")
        self.table.heading("ShortName", text="Short Name")
        self.table.heading("DefinitionRef", text="Definition Reference")
        self.table.heading("Value", text="Value")
        
        self.table.tag_configure("container", background="#e8f4f8")
        self.table.tag_configure("parameter", background="#f0f8e8")
        self.table.tag_configure("modified", background="#ffe8e8")
        
        table_y_scroll = ttk.Scrollbar(table_frame, orient="vertical", command=self.table.yview)
        table_x_scroll = ttk.Scrollbar(table_frame, orient="horizontal", command=self.table.xview)
        self.table.configure(yscrollcommand=table_y_scroll.set, xscrollcommand=table_x_scroll.set)
        table_x_scroll.pack(side="bottom", fill="x")
        table_y_scroll.pack(side="right", fill="y")
        self.table.pack(fill="both", expand=True)
        
        self.table.bind("<Double-1>", self.on_table_edit)
        self.table.bind("<Button-3>", self.show_context_menu)
        
        self.setup_context_menu()

    def set_xml_tree(self, xml_tree):
        self.xml_tree = xml_tree
        self.refresh_table()

    def clear_table(self):
        for item in self.table.get_children():
            self.table.delete(item)
        self.element_map.clear()

    def populate_table(self, root, parent_item=""):
        self.element_map.clear()
        
        def process_element(element, parent_id="", level=0):
            tag_name = self.clean_tag_name(element.tag)
            element_data = self.extract_element_data_simple(element)
            element_type = self.get_element_type(tag_name)
            
            indent = "  " * level
            short_name = element_data['short_name']
            
            if short_name:
                display_name = f"{indent}{tag_name} ({short_name})"
            elif element_data['value']:
                value_preview = element_data['value'][:20] + "..." if len(element_data['value']) > 20 else element_data['value']
                display_name = f"{indent}{tag_name} = {value_preview}"
            else:
                display_name = f"{indent}{tag_name}"
            
            item_id = self.table.insert(
                parent_id, "end", 
                text=display_name,
                values=(
                    element_type,
                    element_data['short_name'],
                    element_data['definition_ref'],
                    element_data['value'],
                ),
                tags=(element_type.lower().replace(" ", "_"),)
            )
            
            self.element_map[item_id] = {
                'element': element,
                'data': element_data
            }
            
            for child in element:
                process_element(child, item_id, level + 1)
            
            return item_id

        process_element(root)
        
        for item in self.table.get_children():
            self.table.item(item, open=True)

    def extract_element_data_simple(self, element):
        data = {
            'short_name': '',
            'definition_ref': '',
            'value': '',
            'text_content': element.text.strip() if element.text else ''
        }
        
        for child in element:
            child_tag = self.clean_tag_name(child.tag)
            if child_tag == 'SHORT-NAME' and child.text:
                data['short_name'] = child.text.strip()
                break
        
        def_ref = self.find_text_by_tag(element, 'DEFINITION-REF')
        if def_ref:
            data['definition_ref'] = def_ref
        
        value = self.find_text_by_tag(element, 'VALUE')
        if value:
            data['value'] = value
        
        return data

    def find_text_by_tag(self, element, target_tag):
        for child in element:
            if self.clean_tag_name(child.tag) == target_tag and child.text:
                return child.text.strip()
        
        for child in element:
            result = self.find_text_by_tag(child, target_tag)
            if result:
                return result
        
        return None

    def clean_tag_name(self, tag):
        return tag.split("}")[-1] if "}" in tag else tag

    def get_element_type(self, tag_name):
        tag_upper = tag_name.upper()
        if 'CONTAINER' in tag_upper: return "Container"
        if 'PARAM' in tag_upper: return "Parameter"
        if 'MODULE' in tag_upper: return "Module"
        if 'CONFIG' in tag_upper: return "Configuration"
        if 'ELEMENTS' in tag_upper: return "Elements"
        if 'PACKAGES' in tag_upper: return "Packages"
        return "Element"

    def search_table(self, event=None):
        search_text = self.search_var.get().lower()
        if not search_text: return
        
        all_items = self.get_all_items()
        matches_found = 0
        
        for item in all_items:
            text = self.table.item(item, "text").lower()
            values = [str(v).lower() for v in self.table.item(item, "values")]
            
            if search_text in text or any(search_text in v for v in values):
                self.table.set(item, "Type", "🔍 " + self.table.set(item, "Type").replace("🔍 ", ""))
                matches_found += 1
            else:
                self.table.set(item, "Type", self.table.set(item, "Type").replace("🔍 ", ""))
        
        if self.status_logger and search_text:
            self.status_logger.log(f"Search: '{search_text}' - {matches_found} matches found")

    def get_all_items(self, parent=""):
        items = []
        for child in self.table.get_children(parent):
            items.append(child)
            items.extend(self.get_all_items(child))
        return items

    def expand_all(self):
        def expand_recursive(item):
            self.table.item(item, open=True)
            for child in self.table.get_children(item):
                expand_recursive(child)
        
        for item in self.table.get_children():
            expand_recursive(item)
        
        if self.status_logger:
            self.status_logger.log("Expanded all nodes")

    def collapse_all(self):
        def collapse_recursive(item):
            self.table.item(item, open=False)
            for child in self.table.get_children(item):
                collapse_recursive(child)
        
        for item in self.table.get_children():
            collapse_recursive(item)
        
        if self.status_logger:
            self.status_logger.log("Collapsed all nodes")

    def refresh_table(self):
        if self.xml_tree:
            self.clear_table()
            self.populate_table(self.xml_tree.getroot())
            if self.status_logger:
                self.status_logger.log("Table refreshed")

    def on_table_edit(self, event):
        selected_item = self.table.selection()
        if not selected_item: return

        column = self.table.identify_column(event.x)
        col_index = int(column.replace("#", "")) - 1
        
        if col_index < 0: return
        
        item_id = selected_item[0]
        old_values = self.table.item(item_id, "values")
        
        if col_index >= len(old_values): return
        
        column_names = ["Type", "ShortName", "DefinitionRef", "Value"]
        column_name = column_names[col_index]
        old_value = old_values[col_index]
        
        if self.status_logger:
            self.status_logger.log(f"Editing: {column_name} = '{old_value}'")
        
        self.show_edit_dialog(item_id, col_index, old_values, column_name, old_value)

    def show_edit_dialog(self, item_id, col_index, old_values, column_name, old_value):
        edit_popup = tk.Toplevel(self.frame)
        edit_popup.title(f"Edit {column_name}")
        edit_popup.geometry("400x200")
        edit_popup.transient(self.frame)
        
        main_frame = ttk.Frame(edit_popup, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text=f"Edit {column_name}:", font=('TkDefaultFont', 10, 'bold')).pack(anchor="w")
        
        if column_name in ["DefinitionRef"]:
            edit_widget = tk.Text(main_frame, height=6, width=50)
            edit_widget.pack(fill="both", expand=True, pady=5)
            edit_widget.insert("1.0", old_value)
            get_new_value = lambda: edit_widget.get("1.0", "end-1c")
        else:
            ttk.Label(main_frame, text="New Value:").pack(anchor="w", pady=(10, 2))
            entry_var = tk.StringVar(value=old_value)
            edit_widget = ttk.Entry(main_frame, textvariable=entry_var, width=50)
            edit_widget.pack(fill="x", pady=2)
            edit_widget.focus_set()
            edit_widget.select_range(0, tk.END)
            get_new_value = entry_var.get
        
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill="x", pady=(10, 0))
        
        def save_edit():
            try:
                new_value = get_new_value()
                self.apply_edit(item_id, col_index, old_values, new_value, column_name)
                edit_popup.destroy()
            except Exception as e:
                messagebox.showerror("Error", f"Failed to save: {e}")
        
        ttk.Button(button_frame, text="Save", command=save_edit).pack(side="right", padx=2)
        ttk.Button(button_frame, text="Cancel", command=edit_popup.destroy).pack(side="right")
        
        edit_popup.bind('<Return>', lambda e: save_edit())
        edit_popup.bind('<Escape>', lambda e: edit_popup.destroy())

    def apply_edit(self, item_id, col_index, old_values, new_value, column_name):
        try:
            updated_values = list(old_values)
            if col_index < len(updated_values):
                updated_values[col_index] = new_value
            else:
                while len(updated_values) <= col_index:
                    updated_values.append("")
                updated_values[col_index] = new_value
            
            self.table.item(item_id, values=tuple(updated_values))
            self.table.item(item_id, tags=("modified",))
            
            element_info = self.element_map.get(item_id)
            if element_info:
                self.update_xml_element(element_info['element'], column_name, new_value)
            
            if self.on_change_callback:
                self.on_change_callback(self.xml_tree)
            
            if self.status_logger:
                self.status_logger.log(f"Updated {column_name}: '{old_values[col_index] if col_index < len(old_values) else ''}' → '{new_value}'")
                
        except Exception as e:
            if self.status_logger:
                self.status_logger.log(f"Edit failed: {e}")
            raise

    def update_xml_element(self, element, column_name, new_value):
        if column_name == "ShortName":
            short_name_elem = self.find_direct_child_by_tag(element, 'SHORT-NAME')
            if short_name_elem is not None:
                short_name_elem.text = new_value
            elif new_value.strip():
                short_name_elem = ET.Element("SHORT-NAME")
                short_name_elem.text = new_value
                element.insert(0, short_name_elem)
                
        elif column_name == "DefinitionRef":
            def_ref_elem = self.find_any_child_by_tag(element, 'DEFINITION-REF')
            if def_ref_elem is not None:
                def_ref_elem.text = new_value
                
        elif column_name == "Value":
            value_elem = self.find_any_child_by_tag(element, 'VALUE')
            if value_elem is not None:
                value_elem.text = new_value
            elif new_value.strip():
                value_elem = ET.SubElement(element, "VALUE")
                value_elem.text = new_value

    def find_direct_child_by_tag(self, element, tag_name):
        for child in element:
            if self.clean_tag_name(child.tag) == tag_name:
                return child
        return None

    def find_any_child_by_tag(self, element, tag_name):
        for child in element:
            if self.clean_tag_name(child.tag) == tag_name:
                return child
        for child in element:
            result = self.find_any_child_by_tag(child, tag_name)
            if result is not None:
                return result
        return None

    def setup_context_menu(self):
        self.context_menu = Menu(self.frame, tearoff=0)
        self.context_menu.add_command(label="Edit Element", command=self.context_edit_row)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Add Child Element", command=self.context_add_child)
        self.context_menu.add_command(label="Add Element Above", command=self.context_add_above)
        self.context_menu.add_command(label="Add Element Below", command=self.context_add_below)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Delete Element", command=self.context_delete_row)
        self.context_menu.add_command(label="Show Element Info", command=self.context_show_info)

    def show_context_menu(self, event):
        selected_item = self.table.identify_row(event.y)
        if selected_item:
            self.table.selection_set(selected_item)
            self.context_menu.post(event.x_root, event.y_root)

    def context_edit_row(self):
        selected = self.table.selection()
        if selected:
            fake_event = tk.Event()
            fake_event.x = 200
            self.on_table_edit(fake_event)

    def _get_selected_element_and_parent(self):
        selected_id = self.table.selection()
        if not selected_id:
            return None, None, None, None
        
        selected_id = selected_id[0]
        element_info = self.element_map.get(selected_id)
        if not element_info:
            return None, None, None, None
            
        element = element_info['element']
        parent_element = self.find_parent_element(element)
        return selected_id, element, parent_element

    def context_add_child(self):
        selected_id, element, _ = self._get_selected_element_and_parent()
        if not selected_id:
            messagebox.showinfo("Information", "Please select a parent element first.")
            return

        tag_name = simpledialog.askstring("New Child Element", "Enter tag name for the new child element:", parent=self.frame)
        if not tag_name or not tag_name.strip():
            return

        new_element = ET.SubElement(element, tag_name)
        self.refresh_table()
        if self.on_change_callback:
            self.on_change_callback(self.xml_tree)
        if self.status_logger: self.status_logger.log(f"Added child <{tag_name}> to <{self.clean_tag_name(element.tag)}>")

    def context_add_above(self):
        selected_id, element, parent_element = self._get_selected_element_and_parent()
        if not parent_element:
            messagebox.showinfo("Information", "Cannot add an element above the root.")
            return

        tag_name = simpledialog.askstring("New Sibling Element", "Enter tag name for the new element (above):", parent=self.frame)
        if not tag_name or not tag_name.strip():
            return
            
        index = list(parent_element).index(element)
        new_element = ET.Element(tag_name)
        parent_element.insert(index, new_element)
        
        self.refresh_table()
        if self.on_change_callback:
            self.on_change_callback(self.xml_tree)
        if self.status_logger: self.status_logger.log(f"Added <{tag_name}> above the selected element.")

    def context_add_below(self):
        selected_id, element, parent_element = self._get_selected_element_and_parent()
        if not parent_element:
            messagebox.showinfo("Information", "Cannot add an element below the root.")
            return

        tag_name = simpledialog.askstring("New Sibling Element", "Enter tag name for the new element (below):", parent=self.frame)
        if not tag_name or not tag_name.strip():
            return

        index = list(parent_element).index(element) + 1
        new_element = ET.Element(tag_name)
        parent_element.insert(index, new_element)

        self.refresh_table()
        if self.on_change_callback:
            self.on_change_callback(self.xml_tree)
        if self.status_logger: self.status_logger.log(f"Added <{tag_name}> below the selected element.")

    def context_delete_row(self):
        selected = self.table.selection()
        if not selected: return
        
        element_info = self.element_map.get(selected[0])
        element_name = "Unknown"
        if element_info:
            element_name = element_info['data'].get('short_name', 'Unknown Element')
        
        if messagebox.askyesno("Confirm Delete", f"Delete '{element_name}'?"):
            self.table.delete(selected[0])
            if element_info and 'element' in element_info:
                try:
                    element = element_info['element']
                    parent = self.find_parent_element(element)
                    if parent is not None:
                        parent.remove(element)
                        if self.on_change_callback:
                            self.on_change_callback(self.xml_tree)
                except Exception as e:
                    if self.status_logger: self.status_logger.log(f"Could not remove from XML: {e}")
            
            if selected[0] in self.element_map:
                del self.element_map[selected[0]]
            
            if self.status_logger: self.status_logger.log(f"Deleted element: {element_name}")

    def find_parent_element(self, target_element):
        if not self.xml_tree: return None
        
        def search_for_parent(element):
            for child in element:
                if child == target_element:
                    return element
                parent = search_for_parent(child)
                if parent is not None:
                    return parent
            return None
        
        return search_for_parent(self.xml_tree.getroot())

    def context_show_info(self):
        selected = self.table.selection()
        if not selected: return
        
        element_info = self.element_map.get(selected[0])
        if not element_info: return
        
        element = element_info['element']
        element_data = element_info['data']
        
        info_dialog = tk.Toplevel(self.frame)
        info_dialog.title("Element Information")
        info_dialog.geometry("500x350")
        
        main_frame = ttk.Frame(info_dialog, padding=10)
        main_frame.pack(fill="both", expand=True)
        
        ttk.Label(main_frame, text="Element Details", font=('TkDefaultFont', 11, 'bold')).pack(anchor="w")
        
        info_text = tk.Text(main_frame, wrap="word", height=15)
        info_text.pack(fill="both", expand=True, pady=5)
        
        info_content = f"""Tag Name: {self.clean_tag_name(element.tag)}
Short Name: {element_data.get('short_name', 'N/A')}
Definition Reference: {element_data.get('definition_ref', 'N/A')}
Value: {element_data.get('value', 'N/A')}
Text Content: {element_data.get('text_content', 'N/A')}
Children Count: {len(list(element))}\n\nAttributes:\n"""
        
        for attr_name, attr_value in element.attrib.items():
            info_content += f"  {attr_name}: {attr_value}\n"
        
        if not element.attrib: info_content += "  (No attributes)\n"
        
        info_content += f"\nChild Elements:\n"
        for i, child in enumerate(list(element)[:10]):
            child_tag = self.clean_tag_name(child.tag)
            child_short_name = self.find_text_by_tag(child, 'SHORT-NAME')
            if child_short_name:
                info_content += f"  {i+1}. {child_tag} ({child_short_name})\n"
            else:
                info_content += f"  {i+1}. {child_tag}\n"
        
        if len(list(element)) > 10:
            info_content += f"  ... and {len(list(element)) - 10} more children"
        elif len(list(element)) == 0:
            info_content += "  (No child elements)"
        
        info_text.insert("1.0", info_content)
        info_text.configure(state="disabled")
        
        ttk.Button(main_frame, text="Close", command=info_dialog.destroy).pack()