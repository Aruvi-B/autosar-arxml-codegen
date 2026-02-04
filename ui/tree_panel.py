import tkinter as tk
from tkinter import ttk

class TreePanel:
    def __init__(self, parent):
        self.frame = ttk.Frame(parent, width=300)

        # === Toolbar for Expand/Collapse ===
        toolbar = ttk.Frame(self.frame)
        toolbar.pack(fill="x")

        expand_btn = ttk.Button(toolbar, text="Expand All", command=self.expand_all)
        expand_btn.pack(side="left", padx=2, pady=2)

        collapse_btn = ttk.Button(toolbar, text="Collapse All", command=self.collapse_all)
        collapse_btn.pack(side="left", padx=2, pady=2)
        
        # === Scrollable Tree Frame ===
        tree_frame = ttk.Frame(self.frame)
        tree_frame.pack(fill="both", expand=True)

        # Treeview
        self.tree = ttk.Treeview(tree_frame)

        # Scrollbars
        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(tree_frame, orient="horizontal", command=self.tree.xview)

        # Link scrollbars with tree
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        # Layout
        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        # Expandable frame
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)

        # Default column setup
        self.tree.column("#0", anchor="w", stretch=True, minwidth=200, width=400)

    def clear_tree(self):
        for item in self.tree.get_children():
            self.tree.delete(item)

    def populate_from_arxml(self, parsed_data):
        """Recursively add dict/list to tree"""
        # === path of the file ===
        
        self.clear_tree()
        longest_text_length = [0]

        def add_nodes(parent, key, value):
            node_text = str(key)
            longest_text_length[0] = max(longest_text_length[0], len(node_text))
            node = self.tree.insert(parent, "end", text=node_text, open=True)

            if isinstance(value, dict):
                for k, v in value.items():
                    add_nodes(node, k, v)
            elif isinstance(value, list):
                for idx, item in enumerate(value):
                    if isinstance(item, dict):
                        add_nodes(node, f"{key}[{idx}]", item)
                    else:
                        text_val = str(item)
                        longest_text_length[0] = max(longest_text_length[0], len(text_val))
                        self.tree.insert(node, "end", text=text_val)
            else:
                leaf_text = str(value)
                longest_text_length[0] = max(longest_text_length[0], len(leaf_text))
                self.tree.insert(node, "end", text=leaf_text)

        # Top-level nodes
        for k, v in parsed_data.items():
            add_nodes("", k, v)

        # === Auto-adjust column width ===
        pixel_width = longest_text_length[0] * 8  # approx 8px per char
        self.tree.column("#0", width=pixel_width, stretch=False)

        # Force refresh so scrollbar knows new width
        self.tree.update_idletasks()

        # # === Auto-adjust column width and enable horizontal scrolling ===
        # pixel_width = longest_text_length[0] * 8  # each char ~8px
        # self.tree.column("#0", width=pixel_width, stretch=False)

        # # Update scrollregion so horizontal scrollbar knows the new width
        # self.tree.update_idletasks()
        # self.tree.configure(scrollregion=self.tree.bbox(""))

    # === Expand/Collapse ===
    def expand_all(self):
        """Expand all tree nodes"""
        def recurse_expand(item):
            self.tree.item(item, open=True)
            for child in self.tree.get_children(item):
                recurse_expand(child)

        for item in self.tree.get_children():
            recurse_expand(item)

    def collapse_all(self):
        """Collapse all tree nodes"""
        def recurse_collapse(item):
            self.tree.item(item, open=False)
            for child in self.tree.get_children(item):
                recurse_collapse(child)

        for item in self.tree.get_children():
            recurse_collapse(item)
