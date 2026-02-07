"""
DestriChiffrage - Dialogues
===========================
Boites de dialogue de l'application - Style Destribois
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme
from version import __version__


class ProductDialog:
    """Dialogue d'ajout/modification de produit"""

    def __init__(self, parent, db, product_id=None):
        self.db = db
        self.product_id = product_id
        self.result = False

        # Creer la fenetre
        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau produit" if not product_id else "Modifier le produit")
        self.dialog.geometry("680x860")
        self.dialog.minsize(660, 840)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 680) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 780) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Charger les donnees existantes
        self.data = {}
        if product_id:
            self.data = self.db.get_produit(product_id) or {}

        self._create_widgets()

        # Attendre la fermeture
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets du formulaire"""
        # Header - Style fenetre principale (primary au lieu de accent)
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = "Nouveau produit" if not self.product_id else "Modifier le produit"
        tk.Label(header, text=title, font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame - Card style
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Formulaire dans une card avec scroll
        form_outer = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                             highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        form_outer.pack(fill=tk.BOTH, expand=True)

        # Canvas pour le scroll
        canvas = tk.Canvas(form_outer, bg=Theme.COLORS['bg_alt'], highlightthickness=0)
        scrollbar = ttk.Scrollbar(form_outer, orient="vertical", command=canvas.yview)
        form_card = tk.Frame(canvas, bg=Theme.COLORS['bg_alt'], padx=20, pady=16)

        form_card.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=form_card, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Scroll avec la molette (seulement quand la souris est sur le canvas)
        def _on_mousewheel(event):
            canvas.yview_scroll(int(-1*(event.delta/120)), "units")
        def _bind_mousewheel(event):
            canvas.bind_all("<MouseWheel>", _on_mousewheel)
        def _unbind_mousewheel(event):
            canvas.unbind_all("<MouseWheel>")
        canvas.bind("<Enter>", _bind_mousewheel)
        canvas.bind("<Leave>", _unbind_mousewheel)

        self.entries = {}
        fields = [
            ('categorie', 'Categorie *', 'combobox'),
            ('sous_categorie', 'Sous-categorie', 'combobox'),
            ('sous_categorie_2', 'Sous-categorie 2', 'combobox'),
            ('sous_categorie_3', 'Sous-categorie 3', 'combobox'),
            ('designation', 'Designation *', 'entry'),
            ('description', 'Description', 'text'),
            ('hauteur', 'Hauteur (mm)', 'entry'),
            ('largeur', 'Largeur (mm)', 'entry'),
            ('prix_achat', 'Prix Achat HT (EUR)', 'entry'),
            ('reference', 'Reference', 'entry'),
            ('fournisseur', 'Fournisseur', 'entry'),
            ('chantier', 'Chantier/Projet', 'entry'),
            ('fiche_technique', 'Fiche technique (PDF)', 'file'),
            ('devis_fournisseur', 'Devis fournisseur (PDF)', 'file'),
            ('notes', 'Notes', 'text'),
        ]

        for i, (field, label, widget_type) in enumerate(fields):
            tk.Label(form_card, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).grid(row=i, column=0, sticky='e', padx=(5, 10), pady=8)

            if widget_type == 'combobox':
                widget = ttk.Combobox(form_card, width=36, font=Theme.FONTS['body'])
                # Remplir avec les valeurs appropriees selon le champ
                if field == 'categorie':
                    widget['values'] = self.db.get_categories_names()
                elif field == 'sous_categorie':
                    widget['values'] = self.db.get_subcategories_names(level=1)
                elif field == 'sous_categorie_2':
                    widget['values'] = self.db.get_subcategories_names(level=2)
                elif field == 'sous_categorie_3':
                    widget['values'] = self.db.get_subcategories_names(level=3)
                widget.set(self.data.get(field, ''))
                widget.grid(row=i, column=1, sticky='w', padx=5, pady=8)
            elif widget_type == 'text':
                widget = tk.Text(form_card, width=38, height=3, font=Theme.FONTS['body'],
                               bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
                text_value = self.data.get(field, '') or ''
                widget.insert('1.0', text_value)
                widget.grid(row=i, column=1, sticky='w', padx=5, pady=8)
            elif widget_type == 'file':
                # Frame pour le champ fichier + boutons
                file_frame = tk.Frame(form_card, bg=Theme.COLORS['bg_alt'])
                file_frame.grid(row=i, column=1, sticky='w', padx=5, pady=8)

                widget = tk.Entry(file_frame, width=28, font=Theme.FONTS['body'],
                                 bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
                widget.pack(side=tk.LEFT)
                value = self.data.get(field, '') or ''
                widget.insert(0, value)

                # Bouton parcourir
                browse_btn = tk.Button(file_frame, text="...", font=Theme.FONTS['small'],
                                      bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                                      bd=0, padx=8, pady=4, cursor='hand2',
                                      command=lambda w=widget: self._browse_file(w))
                browse_btn.pack(side=tk.LEFT, padx=(4, 0))

                # Bouton ouvrir (si fichier existe)
                open_btn = tk.Button(file_frame, text="Ouvrir", font=Theme.FONTS['small'],
                                    bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white'],
                                    bd=0, padx=8, pady=4, cursor='hand2',
                                    command=lambda w=widget: self._open_file(w))
                open_btn.pack(side=tk.LEFT, padx=(4, 0))
            else:
                widget = tk.Entry(form_card, width=38, font=Theme.FONTS['body'],
                                 bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
                value = self.data.get(field, '')
                if field == 'prix_achat' and value:
                    value = f"{value:.2f}"
                elif field in ('hauteur', 'largeur') and value:
                    value = str(value) if value else ''
                widget.insert(0, str(value) if value else '')
                widget.grid(row=i, column=1, sticky='w', padx=5, pady=8)

            self.entries[field] = widget

        # Boutons - Fixed at bottom
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Enregistrer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._save).pack(side=tk.RIGHT)

    def _browse_file(self, entry_widget):
        """Ouvre un dialogue pour selectionner un fichier PDF"""
        filepath = filedialog.askopenfilename(
            title="Selectionner une fiche technique",
            filetypes=[("Fichiers PDF", "*.pdf"), ("Tous les fichiers", "*.*")]
        )
        if filepath:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, filepath)

    def _open_file(self, entry_widget):
        """Ouvre le fichier PDF associe"""
        filepath = entry_widget.get().strip()
        if not filepath:
            messagebox.showwarning("Attention", "Aucune fiche technique renseignee")
            return

        if not os.path.exists(filepath):
            messagebox.showerror("Erreur", f"Le fichier n'existe pas:\n{filepath}")
            return

        try:
            # Ouvrir avec l'application par defaut du systeme
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")

    def _save(self):
        """Enregistre le produit"""
        data = {}
        for field, widget in self.entries.items():
            if isinstance(widget, tk.Text):
                value = widget.get('1.0', tk.END).strip()
            elif isinstance(widget, ttk.Combobox):
                value = widget.get()
            else:
                value = widget.get()

            if field == 'prix_achat':
                try:
                    value = float(value.replace(',', '.')) if value else 0
                except:
                    value = 0
            elif field in ('hauteur', 'largeur'):
                try:
                    value = int(value) if value and value.strip().isdigit() else None
                except:
                    value = None

            data[field] = value

        if not data.get('designation'):
            messagebox.showerror("Erreur", "La designation est obligatoire")
            return

        if not data.get('categorie'):
            messagebox.showerror("Erreur", "La categorie est obligatoire")
            return

        if self.product_id:
            self.db.update_produit(self.product_id, data)
        else:
            self.db.add_produit(data)

        self.result = True
        self.dialog.destroy()


class CategoryDialog:
    """Dialogue de gestion des categories"""

    def __init__(self, parent, db):
        self.db = db
        self.parent = parent
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Gestion des categories")
        self.dialog.geometry("780x750")
        self.dialog.minsize(750, 730)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 780) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 750) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self._refresh_list()

        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header - Style fenetre principale
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Gestion des categories", font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Section ajout - Card style
        add_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        add_frame.pack(fill=tk.X, pady=(0, 16))

        tk.Label(add_frame, text="AJOUTER UNE CATEGORIE", font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        input_row = tk.Frame(add_frame, bg=Theme.COLORS['bg_alt'])
        input_row.pack(fill=tk.X)

        tk.Label(input_row, text="Nom:", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.new_cat_entry = tk.Entry(input_row, width=22, font=Theme.FONTS['body'],
                                     bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                     bd=1, relief='solid')
        self.new_cat_entry.pack(side=tk.LEFT, padx=(10, 16))

        tk.Label(input_row, text="Description:", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.new_desc_entry = tk.Entry(input_row, width=22, font=Theme.FONTS['body'],
                                      bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                      bd=1, relief='solid')
        self.new_desc_entry.pack(side=tk.LEFT, padx=(10, 16))

        tk.Button(input_row, text="+ Ajouter", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['success'], fg=Theme.COLORS['white'],
                 bd=0, padx=16, pady=6, cursor='hand2',
                 command=self._add_category).pack(side=tk.LEFT)

        # Liste des categories - Card style
        list_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                             highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Header de liste - Style primary comme fenetre principale
        list_header = tk.Frame(list_frame, bg=Theme.COLORS['primary_light'], height=40)
        list_header.pack(fill=tk.X)
        list_header.pack_propagate(False)

        tk.Label(list_header, text="CATEGORIES EXISTANTES", font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['primary_light'], fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=16, pady=8)

        # Treeview pour la liste
        tree_frame = tk.Frame(list_frame, bg=Theme.COLORS['bg_alt'])
        tree_frame.pack(fill=tk.BOTH, expand=True, padx=12, pady=12)

        columns = ('nom', 'description', 'produits')
        self.tree = ttk.Treeview(tree_frame, columns=columns, show='headings', height=8)

        self.tree.heading('nom', text='Nom')
        self.tree.heading('description', text='Description')
        self.tree.heading('produits', text='Nb Produits')

        self.tree.column('nom', width=160)
        self.tree.column('description', width=280)
        self.tree.column('produits', width=100, anchor='center')

        vsb = ttk.Scrollbar(tree_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=vsb.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Boutons d'action
        action_frame = tk.Frame(list_frame, bg=Theme.COLORS['bg_alt'], padx=12, pady=12)
        action_frame.pack(fill=tk.X)

        tk.Button(action_frame, text="Modifier", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white'],
                 bd=0, padx=18, pady=8, cursor='hand2',
                 command=self._edit_category).pack(side=tk.LEFT, padx=(0, 8))

        tk.Button(action_frame, text="Supprimer", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['danger'], fg=Theme.COLORS['white'],
                 bd=0, padx=18, pady=8, cursor='hand2',
                 command=self._delete_category).pack(side=tk.LEFT)

        # Bouton fermer - Fixed at bottom
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(16, 0))

        tk.Button(btn_frame, text="Fermer", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._close).pack(side=tk.RIGHT)

    def _refresh_list(self):
        """Rafraichit la liste des categories"""
        for item in self.tree.get_children():
            self.tree.delete(item)

        categories = self.db.get_categories()
        for cat in categories:
            # Compter les produits dans cette categorie
            count = self.db.count_produits(cat['nom'])
            self.tree.insert('', tk.END, values=(cat['nom'], cat['description'] or '', count))

    def _add_category(self):
        """Ajoute une nouvelle categorie"""
        nom = self.new_cat_entry.get().strip().upper()
        description = self.new_desc_entry.get().strip()

        if not nom:
            messagebox.showerror("Erreur", "Le nom de la categorie est obligatoire")
            return

        # Verifier si la categorie existe deja
        existing = self.db.get_categories_names()
        if nom in existing:
            messagebox.showerror("Erreur", f"La categorie '{nom}' existe deja")
            return

        self.db.add_categorie(nom, description)
        self.new_cat_entry.delete(0, tk.END)
        self.new_desc_entry.delete(0, tk.END)
        self._refresh_list()
        self.result = True

    def _edit_category(self):
        """Modifie la categorie selectionnee"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez une categorie a modifier")
            return

        item = self.tree.item(selection[0])
        old_nom = str(item['values'][0])
        old_desc = str(item['values'][1]) if item['values'][1] else ""

        # Ouvrir dialogue d'edition
        EditCategoryDialog(self.dialog, self.db, old_nom, old_desc, self._refresh_list)
        self.result = True

    def _delete_category(self):
        """Supprime la categorie selectionnee"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez une categorie a supprimer")
            return

        item = self.tree.item(selection[0])
        nom = str(item['values'][0])
        nb_produits = int(item['values'][2])

        if nb_produits > 0:
            # Alerte: des produits sont dans cette categorie
            response = messagebox.askyesnocancel(
                "Attention - Produits associes",
                f"La categorie '{nom}' contient {nb_produits} produit(s).\n\n"
                f"Voulez-vous reassigner ces produits a une autre categorie?\n\n"
                f"- Oui: Choisir une nouvelle categorie pour les produits\n"
                f"- Non: Supprimer la categorie ET tous ses produits\n"
                f"- Annuler: Ne rien faire"
            )

            if response is None:  # Annuler
                return
            elif response:  # Oui - Reassigner
                ReassignProductsDialog(self.dialog, self.db, nom, self._refresh_list)
                self.result = True
                return
            else:  # Non - Supprimer tout
                confirm = messagebox.askyesno(
                    "Confirmation DEFINITIVE",
                    f"ATTENTION: Vous allez supprimer definitivement:\n"
                    f"- La categorie '{nom}'\n"
                    f"- Les {nb_produits} produit(s) associe(s)\n\n"
                    f"Cette action est IRREVERSIBLE.\n\n"
                    f"Confirmer la suppression?"
                )
                if not confirm:
                    return

                # Supprimer les produits de cette categorie
                self.db.delete_produits_by_category(nom)
        else:
            # Pas de produits, demander confirmation simple
            if not messagebox.askyesno("Confirmer", f"Supprimer la categorie '{nom}'?"):
                return

        # Supprimer la categorie
        self.db.delete_categorie(nom)
        self._refresh_list()
        self.result = True

    def _close(self):
        """Ferme le dialogue"""
        self.dialog.destroy()


class EditCategoryDialog:
    """Dialogue d'edition d'une categorie"""

    def __init__(self, parent, db, nom, description, callback):
        self.db = db
        self.old_nom = nom
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier la categorie")
        self.dialog.geometry("500x320")
        self.dialog.minsize(480, 300)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 500) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 320) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Header - Style primary
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Modifier la categorie", font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=20, pady=12)

        # Main frame - Card style
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card pour le formulaire
        form_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        form_card.pack(fill=tk.X)

        # Nom
        tk.Label(form_card, text="Nom:", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).grid(row=0, column=0, sticky='e', padx=(5, 10), pady=12)

        self.nom_entry = tk.Entry(form_card, width=28, font=Theme.FONTS['body'],
                                 bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
        self.nom_entry.insert(0, nom)
        self.nom_entry.grid(row=0, column=1, sticky='w', padx=5, pady=12)

        # Description
        tk.Label(form_card, text="Description:", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).grid(row=1, column=0, sticky='e', padx=(5, 10), pady=12)

        self.desc_entry = tk.Entry(form_card, width=28, font=Theme.FONTS['body'],
                                  bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
        self.desc_entry.insert(0, description or '')
        self.desc_entry.grid(row=1, column=1, sticky='w', padx=5, pady=12)

        # Boutons - Fixed at bottom
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=20, pady=8, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Enregistrer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=8, cursor='hand2',
                 command=self._save).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def _save(self):
        """Enregistre les modifications"""
        new_nom = self.nom_entry.get().strip().upper()
        new_desc = self.desc_entry.get().strip()

        if not new_nom:
            messagebox.showerror("Erreur", "Le nom est obligatoire")
            return

        # Mettre a jour la categorie (met aussi a jour les produits si le nom change)
        self.db.update_categorie(self.old_nom, new_nom, new_desc)

        self.callback()
        self.dialog.destroy()


class ReassignProductsDialog:
    """Dialogue pour reassigner les produits a une autre categorie"""

    def __init__(self, parent, db, old_category, callback):
        self.db = db
        self.old_category = old_category
        self.callback = callback

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Reassigner les produits")
        self.dialog.geometry("560x400")
        self.dialog.minsize(540, 380)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 560) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 400) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Header - Style warning avec icone
        header = tk.Frame(self.dialog, bg=Theme.COLORS['warning'], height=50)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Reassigner les produits", font=Theme.FONTS['heading'],
                bg=Theme.COLORS['warning'], fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=20, pady=12)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card pour le contenu
        content_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                               highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        content_card.pack(fill=tk.X)

        # Compte des produits
        nb_produits = self.db.count_produits(old_category)

        tk.Label(content_card, text=f"La categorie '{old_category}' contient {nb_produits} produit(s).",
                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 16))

        tk.Label(content_card, text="Choisissez la nouvelle categorie pour ces produits:",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 12))

        # Combobox pour choisir la nouvelle categorie
        cat_frame = tk.Frame(content_card, bg=Theme.COLORS['bg_alt'])
        cat_frame.pack(fill=tk.X, pady=8)

        tk.Label(cat_frame, text="Nouvelle categorie:", font=Theme.FONTS['body_bold'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.category_var = tk.StringVar()
        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var,
                                          width=24, state='readonly', font=Theme.FONTS['body'])

        # Exclure la categorie actuelle de la liste
        categories = [c for c in self.db.get_categories_names() if c != old_category]
        self.category_combo['values'] = categories
        if categories:
            self.category_combo.set(categories[0])

        self.category_combo.pack(side=tk.LEFT, padx=16)

        # Boutons - Fixed at bottom
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(24, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Reassigner et supprimer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._reassign).pack(side=tk.RIGHT)

        self.dialog.wait_window()

    def _reassign(self):
        """Reassigne les produits et supprime la categorie"""
        new_category = self.category_var.get()

        if not new_category:
            messagebox.showerror("Erreur", "Selectionnez une categorie de destination")
            return

        # Reassigner les produits
        self.db.update_produits_category(self.old_category, new_category)

        # Supprimer l'ancienne categorie
        self.db.delete_categorie(self.old_category)

        self.callback()
        self.dialog.destroy()


class SettingsDialog:
    """Dialogue des parametres"""

    def __init__(self, parent, db):
        self.db = db
        self.parent = parent
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Parametres")
        self.dialog.geometry("620x620")
        self.dialog.minsize(580, 600)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 620) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 620) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header - Style primary
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Parametres", font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Notebook pour les onglets
        notebook = ttk.Notebook(main_frame)
        notebook.pack(fill=tk.BOTH, expand=True)

        # Onglet General
        general_frame = tk.Frame(notebook, bg=Theme.COLORS['bg_alt'], padx=24, pady=24)
        notebook.add(general_frame, text="  General  ")

        self.entries = {}
        row = 0

        # Paramètre data_dir avec sélecteur de dossier
        tk.Label(general_frame, text="Dossier des donnees", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='e', padx=(5, 12), pady=14)

        data_frame = tk.Frame(general_frame, bg=Theme.COLORS['bg_alt'])
        data_frame.grid(row=row, column=1, sticky='w', padx=5, pady=14)

        data_entry = tk.Entry(data_frame, width=18, font=Theme.FONTS['body'],
                             bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
        data_entry.insert(0, self.db.get_parametre('data_dir', ''))
        data_entry.pack(side=tk.LEFT)

        browse_btn = tk.Button(data_frame, text="...", font=Theme.FONTS['small'],
                              bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                              bd=0, padx=8, pady=4, cursor='hand2',
                              command=lambda: self._browse_data_dir(data_entry))
        browse_btn.pack(side=tk.LEFT, padx=(4, 0))

        self.entries['data_dir'] = data_entry
        row += 1

        # Autres paramètres
        params = [
            ('entreprise', "Nom de l'entreprise"),
            ('marge', "Marge par defaut (%)"),
            ('tva', "Taux de TVA (%)"),
            ('devise', "Devise"),
        ]

        for key, label in params:
            tk.Label(general_frame, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='e', padx=(5, 12), pady=14)

            entry = tk.Entry(general_frame, width=24, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'], bd=1, relief='solid')
            entry.insert(0, self.db.get_parametre(key, ''))
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=14)
            self.entries[key] = entry
            row += 1

        # Onglet Chiffrage Marches
        chiffrage_frame = tk.Frame(notebook, bg=Theme.COLORS['bg_alt'], padx=24, pady=24)
        notebook.add(chiffrage_frame, text="  Chiffrage marches  ")

        tk.Label(chiffrage_frame, text="TAUX HORAIRES MAIN D'OEUVRE",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        taux_frame = tk.Frame(chiffrage_frame, bg=Theme.COLORS['bg_alt'])
        taux_frame.pack(fill=tk.X, pady=(0, 16))

        # En-tetes des colonnes
        tk.Label(taux_frame, text="", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt']).grid(row=0, column=0, padx=5)
        tk.Label(taux_frame, text="Cout entreprise", font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).grid(row=0, column=1, padx=5, pady=(0, 8))
        tk.Label(taux_frame, text="Prix de vente", font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).grid(row=0, column=2, padx=5, pady=(0, 8))
        tk.Label(taux_frame, text="Marge", font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).grid(row=0, column=3, padx=5, pady=(0, 8))

        taux_params = [
            ('conception', 'Conception (EUR/h)'),
            ('fabrication', 'Fabrication (EUR/h)'),
            ('pose', 'Pose (EUR/h)'),
        ]

        self.marge_labels = {}

        for i, (type_taux, label) in enumerate(taux_params):
            row = i + 1
            # Label du type
            tk.Label(taux_frame, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='e', padx=(5, 12), pady=8)

            # Cout entreprise
            cout_key = f'taux_cout_{type_taux}'
            cout_entry = tk.Entry(taux_frame, width=8, font=Theme.FONTS['body'],
                                 bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                 bd=1, relief='solid', justify='center')
            cout_entry.insert(0, self.db.get_parametre(cout_key, '35'))
            cout_entry.grid(row=row, column=1, padx=5, pady=8)
            cout_entry.bind('<KeyRelease>', lambda e, t=type_taux: self._update_marge_display(t))
            self.entries[cout_key] = cout_entry

            # Prix de vente
            vente_key = f'taux_vente_{type_taux}'
            vente_entry = tk.Entry(taux_frame, width=8, font=Theme.FONTS['body'],
                                  bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                  bd=1, relief='solid', justify='center')
            vente_entry.insert(0, self.db.get_parametre(vente_key, '45'))
            vente_entry.grid(row=row, column=2, padx=5, pady=8)
            vente_entry.bind('<KeyRelease>', lambda e, t=type_taux: self._update_marge_display(t))
            self.entries[vente_key] = vente_entry

            # Marge calculee (lecture seule)
            marge_label = tk.Label(taux_frame, text="0.0%", font=Theme.FONTS['body'],
                                  bg=Theme.COLORS['bg_alt'],
                                  fg=Theme.COLORS['success'], width=8)
            marge_label.grid(row=row, column=3, padx=5, pady=8)
            self.marge_labels[type_taux] = marge_label

        # Calculer les marges initiales
        for type_taux, _ in taux_params:
            self._update_marge_display(type_taux)

        tk.Label(chiffrage_frame, text="MARGE MATERIAUX",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(16, 12))

        marge_frame = tk.Frame(chiffrage_frame, bg=Theme.COLORS['bg_alt'])
        marge_frame.pack(fill=tk.X)

        tk.Label(marge_frame, text="Marge par defaut sur materiaux (%)",
                font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        marge_entry = tk.Entry(marge_frame, width=10, font=Theme.FONTS['body'],
                              bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                              bd=1, relief='solid', justify='center')
        marge_entry.insert(0, self.db.get_parametre('marge_marche', '25'))
        marge_entry.pack(side=tk.LEFT, padx=(12, 0))
        self.entries['marge_marche'] = marge_entry

        tk.Label(chiffrage_frame,
                text="La marge MO est calculee automatiquement a partir des couts et prix de vente.\n"
                     "La marge materiaux s'applique sur le cout d'achat des produits lies.",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted'],
                justify='left').pack(anchor='w', pady=(24, 0))

        # Onglet Categories
        cat_frame = tk.Frame(notebook, bg=Theme.COLORS['bg_alt'], padx=24, pady=24)
        notebook.add(cat_frame, text="  Categories  ")

        tk.Label(cat_frame, text="Gestion des categories du catalogue",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 16))

        tk.Button(cat_frame, text="Gerer les categories", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._open_category_manager).pack(anchor='w')

        # Resume des categories
        tk.Label(cat_frame, text="Categories actuelles:", font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(24, 12))

        cat_listbox = tk.Listbox(cat_frame, height=6, font=Theme.FONTS['body'],
                                bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                bd=1, relief='solid')
        cat_listbox.pack(fill=tk.X)

        for cat in self.db.get_categories():
            count = self.db.count_produits(cat['nom'])
            cat_listbox.insert(tk.END, f"{cat['nom']} ({count} produits)")

        # Boutons - Fixed at bottom
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Enregistrer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._save).pack(side=tk.RIGHT)

    def _open_category_manager(self):
        """Ouvre le gestionnaire de categories"""
        dialog = CategoryDialog(self.dialog, self.db)
        if dialog.result:
            self.result = True

    def _update_marge_display(self, type_taux):
        """Met a jour l'affichage de la marge pour un type de taux"""
        try:
            cout_key = f'taux_cout_{type_taux}'
            vente_key = f'taux_vente_{type_taux}'

            cout = float(self.entries[cout_key].get().replace(',', '.') or 0)
            vente = float(self.entries[vente_key].get().replace(',', '.') or 0)

            if cout > 0:
                marge = ((vente - cout) / cout) * 100
                self.marge_labels[type_taux].config(
                    text=f"{marge:.1f}%",
                    fg=Theme.COLORS['success'] if marge > 0 else Theme.COLORS['danger']
                )
            else:
                self.marge_labels[type_taux].config(text="-", fg=Theme.COLORS['text_muted'])
        except (ValueError, KeyError):
            pass

    def _browse_data_dir(self, entry_widget):
        """Ouvre un dialogue pour selectionner le dossier data"""
        directory = filedialog.askdirectory(
            title="Selectionner le dossier des donnees",
            initialdir=entry_widget.get() or os.path.dirname(__file__)
        )
        if directory:
            entry_widget.delete(0, tk.END)
            entry_widget.insert(0, directory)

    def _save(self):
        """Enregistre les parametres"""
        import sys
        sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
        from config import get_config
        from database import Database

        # Valider le dossier data
        data_dir = self.entries.get('data_dir').get() if 'data_dir' in self.entries else None
        data_dir_changed = False

        if data_dir:
            # Normaliser le chemin
            data_dir = os.path.normpath(os.path.abspath(data_dir))

            # Vérifier si le dossier a changé
            if data_dir != self.db.data_dir:
                data_dir_changed = True

                # Vérifier si le dossier existe, sinon proposer de le créer
                if not os.path.exists(data_dir):
                    if messagebox.askyesno("Creer le dossier?",
                        f"Le dossier n'existe pas:\n{data_dir}\n\n"
                        f"Voulez-vous le creer?"):
                        try:
                            os.makedirs(data_dir, exist_ok=True)
                        except Exception as e:
                            messagebox.showerror("Erreur",
                                f"Impossible de creer le dossier:\n{e}")
                            return
                    else:
                        return

                # Vérifier si une base existe déjà dans le nouveau dossier
                new_db_path = os.path.join(data_dir, "catalogue.db")

                if not os.path.exists(new_db_path):
                    # Proposer de copier la base actuelle
                    response = messagebox.askyesnocancel(
                        "Nouvelle base de donnees",
                        f"Aucune base de donnees n'existe dans:\n{data_dir}\n\n"
                        f"Voulez-vous copier la base actuelle vers ce dossier?\n\n"
                        f"- Oui: Copier la base avec tous les produits\n"
                        f"- Non: Creer une nouvelle base vide\n"
                        f"- Annuler: Ne rien faire"
                    )

                    if response is None:  # Annuler
                        return
                    elif response:  # Oui - Copier
                        try:
                            Database.copy_database_to_directory(self.db.db_path, data_dir)
                            messagebox.showinfo("Succes",
                                f"La base de donnees a ete copiee vers:\n{data_dir}")
                        except Exception as e:
                            messagebox.showerror("Erreur",
                                f"Impossible de copier la base:\n{e}")
                            return
                    else:  # Non - Créer nouvelle base
                        # Les sous-dossiers seront créés automatiquement
                        try:
                            os.makedirs(os.path.join(data_dir, "Devis_fournisseur"), exist_ok=True)
                            os.makedirs(os.path.join(data_dir, "Fiches_techniques"), exist_ok=True)
                        except Exception as e:
                            messagebox.showwarning("Attention",
                                f"Impossible de creer les sous-dossiers:\n{e}")

        # Sauvegarder les paramètres (sauf data_dir qui est géré séparément)
        for key, entry in self.entries.items():
            if key != 'data_dir':
                value = entry.get()
                self.db.set_parametre(key, value)

        # Si le dossier data a changé, sauvegarder dans la configuration globale
        if data_dir_changed:
            config = get_config()
            config.set_data_dir(data_dir)

            messagebox.showinfo("Redemarrage necessaire",
                "Le dossier data a ete modifie.\n\n"
                "Veuillez redemarrer l'application pour que\n"
                "les changements prennent effet.")

        self.result = True
        self.dialog.destroy()


class AboutDialog:
    """Dialogue A propos - Style Destribois"""

    def __init__(self, parent):
        dialog = tk.Toplevel(parent)
        dialog.title("A propos")
        dialog.geometry("480x440")
        dialog.minsize(460, 420)
        dialog.transient(parent)
        dialog.grab_set()
        dialog.resizable(False, False)
        dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 480) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 440) // 2
        dialog.geometry(f"+{x}+{y}")

        # Header - Style primary comme fenetre principale
        header = tk.Frame(dialog, bg=Theme.COLORS['primary'], height=90)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="DestriChiffrage", font=Theme.FONTS['title'],
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['white']).pack(pady=(20, 0))

        tk.Label(header, text="Catalogue et chiffrage de portes", font=Theme.FONTS['small'],
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['text_muted']).pack()

        # Main frame
        main_frame = tk.Frame(dialog, bg=Theme.COLORS['bg'], padx=32, pady=24)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card pour le contenu
        content_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=24, pady=20,
                               highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        content_card.pack(fill=tk.BOTH, expand=True)

        tk.Label(content_card, text=f"Version {__version__}", font=Theme.FONTS['body_bold'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(pady=(0, 16))

        tk.Label(content_card, text="Application de gestion de catalogue\net de calcul de prix de vente.",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                justify='center').pack()

        tk.Label(content_card, text="Developpe avec Python et Tkinter\nStyle Destribois",
                font=Theme.FONTS['small'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_light'], justify='center').pack(pady=(16, 0))

        tk.Button(content_card, text="Fermer", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white'],
                 bd=0, padx=28, pady=10, cursor='hand2',
                 command=dialog.destroy).pack(pady=(24, 0))

        dialog.wait_window()
