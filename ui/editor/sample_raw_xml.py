# arxml_shortname_viewer.py
import xml.etree.ElementTree as ET
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from pathlib import Path
from copy import deepcopy

def localname(tag: str) -> str:
    """Strip namespace from tag: '{ns}TAG' -> 'TAG'."""
    return tag.split('}', 1)[1] if '}' in tag else tag

def get_short_name(elem: ET.Element):
    """Return text of the direct SHORT-NAME child (namespace-agnostic) or None."""
    for child in elem:
        if localname(child.tag).upper() == "SHORT-NAME":
            return (child.text or "").strip()
    return None

def strip_namespaces(elem: ET.Element):
    """Return a deep copy of elem with all namespaces removed."""
    new_elem = deepcopy(elem)
    def _strip(e):
        e.tag = localname(e.tag)
        for child in e:
            _strip(child)
    _strip(new_elem)
    return new_elem

def strip_whitespace(elem):
    """Recursively strip leading/trailing whitespace from text/tail."""
    if elem.text:
        elem.text = elem.text.strip()
    for child in elem:
        strip_whitespace(child)
        if child.tail:
            child.tail = child.tail.strip()

def indent(elem, level=0):
    """Pretty-print XML with consistent indentation and no extra spaces."""
    i = "\n" + level * "    "
    if len(elem):
        if not elem.text or not elem.text.strip():
            elem.text = i + "    "
        for child in elem:
            indent(child, level + 1)
        if not elem.tail or not elem.tail.strip():
            elem.tail = i
    else:
        if elem.text:
            elem.text = elem.text.strip()
        if not elem.tail or not elem.tail.strip():
            elem.tail = i

class ARXMLShortnameViewer:
    def __init__(self, root):
        self.root = root
        self.root.title("ARXML SHORT-NAME Viewer")
        self.root.geometry("900x600")

        # Top controls
        top = ttk.Frame(root)
        top.pack(fill="x", padx=6, pady=6)
        ttk.Button(top, text="Open ARXML", command=self.open_file).pack(side="left")
        ttk.Button(top, text="Expand All", command=self.expand_all).pack(side="left", padx=6)
        ttk.Button(top, text="Collapse All", command=self.collapse_all).pack(side="left")

        # Main frame: left tree + right details
        main = ttk.Frame(root)
        main.pack(fill="both", expand=True, padx=6, pady=6)

        # --- Treeview (left) ---
        left = ttk.Frame(text_frame=main)
        left.pack(side="left", fill="both", expand=True)

        yscroll = ttk.Scrollbar(left, orient="vertical")
        xscroll = ttk.Scrollbar(left, orient="horizontal")
        self.tree = ttk.Treeview(left, show="tree", yscrollcommand=yscroll.set, xscrollcommand=xscroll.set)
        yscroll.config(command=self.tree.yview)
        xscroll.config(command=self.tree.xview)
        self.tree.grid(row=0, column=0, sticky="nsew")
        yscroll.grid(row=0, column=1, sticky="ns")
        xscroll.grid(row=1, column=0, sticky="ew")
        left.rowconfigure(0, weight=1)
        left.columnconfigure(0, weight=1)

        # --- Details pane (right) ---
        right = ttk.Frame(main)
        right.pack(side="right", fill="both", padx=6, expand=True)
        ttk.Label(right, text="Selected element (raw XML, no namespaces):").pack(anchor="w")
        self.details = tk.Text(right, wrap="none", height=20)
        self.details.pack(fill="both", expand=True)
        d_yscroll = ttk.Scrollbar(right, orient="vertical", command=self.details.yview)
        self.details.configure(yscrollcommand=d_yscroll.set)
        d_yscroll.pack(side="right", fill="y")

        # Mapping: tree item -> element
        self.item_to_elem = {}

        # Bind selection
        self.tree.bind("<<TreeviewSelect>>", self.on_select)

    def open_file(self):
        path = filedialog.askopenfilename(title="Select ARXML/XML file",
                                          filetypes=[("ARXML/XML", "*.arxml *.xml"), ("All files", "*.*")])
        if not path:
            return
        try:
            tree = ET.parse(path)
            self.xml_root = tree.getroot()
        except Exception as e:
            messagebox.showerror("Parse error", f"Failed to parse XML:\n{e}")
            return

        # Clear previous
        self.tree.delete(*self.tree.get_children())
        self.item_to_elem.clear()

        root_short = get_short_name(self.xml_root)
        root_label = root_short if root_short else localname(self.xml_root.tag)
        root_item = self.tree.insert("", "end", text=root_label)
        if root_short:
            self.item_to_elem[root_item] = self.xml_root

        # Populate tree
        for child in self.xml_root:
            self._build_tree(child, root_item)

        self.expand_all()
        self.details.delete("1.0", tk.END)
        self.root.title(f"ARXML SHORT-NAME Viewer — {Path(path).name}")

    def _build_tree(self, elem: ET.Element, parent_item):
        """DFS: create tree node only when element has a SHORT-NAME."""
        short = get_short_name(elem)
        if short:
            item = self.tree.insert(parent_item, "end", text=short)
            self.item_to_elem[item] = elem
            new_parent = item
        else:
            new_parent = parent_item
        for child in elem:
            if localname(child.tag).upper() == "SHORT-NAME":
                continue
            self._build_tree(child, new_parent)

    def expand_all(self):
        def _expand(item=""):
            for child in self.tree.get_children(item):
                self.tree.item(child, open=True)
                _expand(child)
        _expand()

    def collapse_all(self):
        def _collapse(item=""):
            for child in self.tree.get_children(item):
                self.tree.item(child, open=False)
                _collapse(child)
        _collapse()

    def on_select(self, _evt):
        sel = self.tree.selection()
        if not sel:
            return
        item = sel[0]
        elem = self.item_to_elem.get(item)
        self.details.delete("1.0", tk.END)
        if elem is None:
            self.details.insert(tk.END, "No element mapped to this node.")
            return

        # Strip namespaces and whitespace
        clean_elem = strip_namespaces(elem)
        strip_whitespace(clean_elem)

        # Indent clean XML
        indent(clean_elem)

        # Display
        raw = ET.tostring(clean_elem, encoding="unicode")
        self.details.insert(tk.END, raw)

if __name__ == "__main__":
    root = tk.Tk()
    app = ARXMLShortnameViewer(root)
    root.mainloop()
 