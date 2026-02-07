"""
DestriChiffrage - Dialogue de recherche produit
================================================
Recherche et selection d'un produit du catalogue
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme


class ProductSearchDialog:
    """Dialogue de recherche et selection de produit"""

    def __init__(self, parent, db):
        self.db = db
        self.parent = parent
        self.result = False
        self.selected_product = None
        self.selected_quantity = 1

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Rechercher un produit")
        self.dialog.geometry("900x600")
        self.dialog.minsize(850, 550)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 900) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Variables
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Toutes")
        self.quantity_var = tk.StringVar(value="1")

        self._create_widgets()
        self._load_products()

        # Binding recherche
        self.search_var.trace('w', lambda *args: self._on_search())

        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Rechercher un produit",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Barre de recherche
        search_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=16, pady=12,
                               highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        search_frame.pack(fill=tk.X, pady=(0, 12))

        # Recherche texte
        tk.Label(search_frame, text="Recherche",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(side=tk.LEFT)

        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               width=30, font=Theme.FONTS['body'],
                               bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                               bd=1, relief='solid')
        search_entry.pack(side=tk.LEFT, padx=(8, 24))
        search_entry.focus()

        # Filtre categorie
        tk.Label(search_frame, text="Categorie",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(side=tk.LEFT)

        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var,
                                          width=18, state='readonly',
                                          font=Theme.FONTS['body'])
        cats = ['Toutes'] + self.db.get_categories_names()
        self.category_combo['values'] = cats
        self.category_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self._on_search())

        # Tableau des produits
        table_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                              highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))

        columns = ('id', 'categorie', 'designation', 'hauteur', 'largeur', 'prix', 'reference')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=12)

        col_config = {
            'id': ('ID', 50, 'center'),
            'categorie': ('Categorie', 120, 'w'),
            'designation': ('Designation', 280, 'w'),
            'hauteur': ('Hauteur', 70, 'center'),
            'largeur': ('Largeur', 70, 'center'),
            'prix': ('Prix HT', 90, 'e'),
            'reference': ('Reference', 100, 'center'),
        }

        for col, (text, width, anchor) in col_config.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor, minwidth=40)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Double-clic pour selectionner
        self.tree.bind('<Double-1>', lambda e: self._on_select())

        # Zone quantite
        qty_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=16, pady=12,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        qty_frame.pack(fill=tk.X, pady=(0, 12))

        tk.Label(qty_frame, text="Quantite a ajouter:",
                font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        qty_entry = tk.Entry(qty_frame, textvariable=self.quantity_var,
                            width=8, font=Theme.FONTS['body'],
                            bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                            bd=1, relief='solid', justify='center')
        qty_entry.pack(side=tk.LEFT, padx=(12, 0))

        # Compteur
        self.count_label = tk.Label(qty_frame, text="0 produit(s)",
                                   font=Theme.FONTS['small'],
                                   bg=Theme.COLORS['bg_alt'],
                                   fg=Theme.COLORS['text_muted'])
        self.count_label.pack(side=tk.RIGHT)

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Ajouter le produit", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._on_select).pack(side=tk.RIGHT)

    def _load_products(self):
        """Charge tous les produits"""
        self._on_search()

    def _on_search(self):
        """Execute la recherche"""
        terme = self.search_var.get()
        categorie = self.category_var.get()

        produits = self.db.search_produits(terme, categorie)

        # Vider le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Remplir
        for p in produits:
            self.tree.insert('', tk.END, values=(
                p['id'],
                p['categorie'],
                p['designation'],
                p['hauteur'] or '-',
                p['largeur'] or '-',
                f"{p['prix_achat']:.2f} EUR",
                p['reference'] or '-',
            ))

        self.count_label.config(text=f"{len(produits)} produit(s)")

    def _on_select(self):
        """Selectionne le produit"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez un produit")
            return

        # Valider la quantite
        try:
            qty = float(self.quantity_var.get().replace(',', '.'))
            if qty <= 0:
                raise ValueError()
        except:
            messagebox.showerror("Erreur", "La quantite doit etre un nombre positif")
            return

        item = self.tree.item(selection[0])
        product_id = item['values'][0]

        self.selected_product = self.db.get_produit(product_id)
        self.selected_quantity = qty
        self.result = True
        self.dialog.destroy()


class MultiProductSearchDialog:
    """Dialogue pour ajouter plusieurs produits en une fois"""

    def __init__(self, parent, db):
        self.db = db
        self.parent = parent
        self.result = False
        self.selected_products = []  # Liste de tuples (produit, quantite)

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Ajouter des produits")
        self.dialog.geometry("1000x700")
        self.dialog.minsize(950, 650)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 1000) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 700) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Variables
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Toutes")

        self._create_widgets()
        self._load_products()

        self.search_var.trace('w', lambda *args: self._on_search())

        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Ajouter des produits",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame - 2 colonnes
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=16, pady=16)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Colonne gauche - Catalogue
        left_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        left_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(0, 8))

        tk.Label(left_frame, text="CATALOGUE",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 8))

        # Recherche
        search_frame = tk.Frame(left_frame, bg=Theme.COLORS['bg_alt'], padx=12, pady=8,
                               highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        search_frame.pack(fill=tk.X, pady=(0, 8))

        search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                               width=20, font=Theme.FONTS['body'],
                               bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                               bd=1, relief='solid')
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.category_combo = ttk.Combobox(search_frame, textvariable=self.category_var,
                                          width=15, state='readonly',
                                          font=Theme.FONTS['body'])
        cats = ['Toutes'] + self.db.get_categories_names()
        self.category_combo['values'] = cats
        self.category_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.category_combo.bind('<<ComboboxSelected>>', lambda e: self._on_search())

        # Tableau catalogue
        cat_table_frame = tk.Frame(left_frame, bg=Theme.COLORS['bg_alt'],
                                  highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        cat_table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'designation', 'prix')
        self.cat_tree = ttk.Treeview(cat_table_frame, columns=columns, show='headings', height=15)

        self.cat_tree.heading('id', text='ID')
        self.cat_tree.heading('designation', text='Designation')
        self.cat_tree.heading('prix', text='Prix HT')

        self.cat_tree.column('id', width=50, anchor='center')
        self.cat_tree.column('designation', width=300, anchor='w')
        self.cat_tree.column('prix', width=80, anchor='e')

        vsb = ttk.Scrollbar(cat_table_frame, orient="vertical", command=self.cat_tree.yview)
        self.cat_tree.configure(yscrollcommand=vsb.set)

        self.cat_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Bouton ajouter
        tk.Button(left_frame, text="Ajouter au panier >>",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['secondary'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=16, pady=8, cursor='hand2',
                 command=self._add_to_selection).pack(pady=(8, 0))

        # Colonne droite - Selection
        right_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        right_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=(8, 0))

        tk.Label(right_frame, text="PRODUITS SELECTIONNES",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 8))

        # Tableau selection
        sel_table_frame = tk.Frame(right_frame, bg=Theme.COLORS['bg_alt'],
                                  highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        sel_table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'designation', 'quantite', 'prix')
        self.sel_tree = ttk.Treeview(sel_table_frame, columns=columns, show='headings', height=15)

        self.sel_tree.heading('id', text='ID')
        self.sel_tree.heading('designation', text='Designation')
        self.sel_tree.heading('quantite', text='Qte')
        self.sel_tree.heading('prix', text='Prix HT')

        self.sel_tree.column('id', width=50, anchor='center')
        self.sel_tree.column('designation', width=250, anchor='w')
        self.sel_tree.column('quantite', width=60, anchor='center')
        self.sel_tree.column('prix', width=80, anchor='e')

        vsb2 = ttk.Scrollbar(sel_table_frame, orient="vertical", command=self.sel_tree.yview)
        self.sel_tree.configure(yscrollcommand=vsb2.set)

        self.sel_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb2.pack(side=tk.RIGHT, fill=tk.Y)

        # Actions selection
        sel_actions = tk.Frame(right_frame, bg=Theme.COLORS['bg'])
        sel_actions.pack(fill=tk.X, pady=(8, 0))

        tk.Button(sel_actions, text="Retirer",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['danger'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=16, pady=6, cursor='hand2',
                 command=self._remove_from_selection).pack(side=tk.LEFT)

        tk.Button(sel_actions, text="Modifier qte",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'],
                 bd=0, padx=16, pady=6, cursor='hand2',
                 command=self._edit_quantity).pack(side=tk.LEFT, padx=(8, 0))

        # Total
        self.total_label = tk.Label(right_frame, text="Total: 0.00 EUR",
                                   font=Theme.FONTS['heading'],
                                   bg=Theme.COLORS['bg'],
                                   fg=Theme.COLORS['text'])
        self.total_label.pack(anchor='e', pady=(16, 0))

        # Boutons finaux
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        btn_frame.pack(side=tk.BOTTOM, fill=tk.X, pady=(16, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Valider la selection", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._validate).pack(side=tk.RIGHT)

    def _load_products(self):
        """Charge les produits"""
        self._on_search()

    def _on_search(self):
        """Recherche dans le catalogue"""
        terme = self.search_var.get()
        categorie = self.category_var.get()

        produits = self.db.search_produits(terme, categorie)

        for item in self.cat_tree.get_children():
            self.cat_tree.delete(item)

        for p in produits:
            self.cat_tree.insert('', tk.END, values=(
                p['id'],
                p['designation'],
                f"{p['prix_achat']:.2f} EUR",
            ))

    def _add_to_selection(self):
        """Ajoute le produit selectionne a la liste"""
        selection = self.cat_tree.selection()
        if not selection:
            return

        item = self.cat_tree.item(selection[0])
        product_id = item['values'][0]

        # Verifier si deja present
        for child in self.sel_tree.get_children():
            if self.sel_tree.item(child)['values'][0] == product_id:
                messagebox.showinfo("Info", "Ce produit est deja dans la selection")
                return

        produit = self.db.get_produit(product_id)
        if produit:
            self.sel_tree.insert('', tk.END, values=(
                produit['id'],
                produit['designation'],
                1,
                f"{produit['prix_achat']:.2f} EUR",
            ))
            self._update_total()

    def _remove_from_selection(self):
        """Retire le produit de la selection"""
        selection = self.sel_tree.selection()
        if selection:
            self.sel_tree.delete(selection[0])
            self._update_total()

    def _edit_quantity(self):
        """Modifie la quantite d'un produit"""
        selection = self.sel_tree.selection()
        if not selection:
            return

        item = self.sel_tree.item(selection[0])
        current_qty = item['values'][2]

        # Simple dialogue de saisie
        dialog = tk.Toplevel(self.dialog)
        dialog.title("Modifier la quantite")
        dialog.geometry("380x200")
        dialog.minsize(350, 180)
        dialog.transient(self.dialog)
        dialog.grab_set()
        dialog.configure(bg=Theme.COLORS['bg'])

        dialog.update_idletasks()
        x = self.dialog.winfo_x() + 100
        y = self.dialog.winfo_y() + 100
        dialog.geometry(f"+{x}+{y}")

        tk.Label(dialog, text="Nouvelle quantite:",
                font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg']).pack(pady=(24, 12))

        qty_var = tk.StringVar(value=str(current_qty))
        entry = tk.Entry(dialog, textvariable=qty_var, width=12,
                        font=Theme.FONTS['body'], justify='center')
        entry.pack()
        entry.select_range(0, tk.END)
        entry.focus()

        def save():
            try:
                new_qty = float(qty_var.get().replace(',', '.'))
                if new_qty <= 0:
                    raise ValueError()
                values = list(item['values'])
                values[2] = new_qty
                self.sel_tree.item(selection[0], values=values)
                self._update_total()
                dialog.destroy()
            except:
                messagebox.showerror("Erreur", "Quantite invalide")

        btn_frame = tk.Frame(dialog, bg=Theme.COLORS['bg'])
        btn_frame.pack(pady=20)

        tk.Button(btn_frame, text="Annuler",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=16, pady=8, cursor='hand2',
                 command=dialog.destroy).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(btn_frame, text="OK", command=save,
                 font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=8, cursor='hand2').pack(side=tk.LEFT)

        dialog.wait_window()

    def _update_total(self):
        """Met a jour le total"""
        total = 0
        for child in self.sel_tree.get_children():
            values = self.sel_tree.item(child)['values']
            qty = float(values[2])
            prix = float(values[3].replace(' EUR', '').replace(',', '.'))
            total += qty * prix

        self.total_label.config(text=f"Total: {total:.2f} EUR")

    def _validate(self):
        """Valide la selection"""
        self.selected_products = []

        for child in self.sel_tree.get_children():
            values = self.sel_tree.item(child)['values']
            product_id = values[0]
            qty = float(values[2])

            produit = self.db.get_produit(product_id)
            if produit:
                self.selected_products.append((produit, qty))

        if self.selected_products:
            self.result = True

        self.dialog.destroy()
