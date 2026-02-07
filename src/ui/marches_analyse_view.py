"""
DestriChiffrage - Vue d'analyse des marches
=============================================
Liste et analyse globale des marches/chantiers
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme
from ui.dpgf_import_dialog import DPGFImportDialog, ChantierEditDialog, TYPES_MARCHE
from ui.dpgf_chiffrage_view import DPGFChiffrageView
from ui.resultat_marche_dialog import get_resultat_color, get_resultat_label, RESULTATS


class MarchesAnalyseView:
    """Vue d'analyse des marches"""

    def __init__(self, parent, db, on_close_callback=None):
        self.db = db
        self.parent = parent
        self.on_close_callback = on_close_callback

        self.window = tk.Toplevel(parent)
        self.window.title("Analyse des marches")
        self.window.geometry("1200x700")
        self.window.minsize(1100, 650)
        self.window.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 1200) // 2
        y = (self.window.winfo_screenheight() - 700) // 2
        self.window.geometry(f"+{x}+{y}")

        # Fermeture
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Variables
        self.filter_var = tk.StringVar(value="Tous")
        self.type_marche_var = tk.StringVar(value="Tous")

        self._create_widgets()
        self._load_chantiers()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.window, bg=Theme.COLORS['primary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg=Theme.COLORS['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        tk.Label(header_content, text="Analyse des marches",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT)

        tk.Button(header_content, text="+ Nouveau chantier",
                 font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['secondary'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=16, pady=8, cursor='hand2',
                 command=self._new_chantier).pack(side=tk.RIGHT)

        # Main content
        main_frame = tk.Frame(self.window, bg=Theme.COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Barre de filtre + stats
        top_bar = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        top_bar.pack(fill=tk.X, pady=(0, 12))

        # Filtres
        filter_frame = tk.Frame(top_bar, bg=Theme.COLORS['bg_alt'], padx=12, pady=8,
                               highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        filter_frame.pack(side=tk.LEFT)

        tk.Label(filter_frame, text="Filtrer par resultat:",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        filter_combo = ttk.Combobox(filter_frame, textvariable=self.filter_var,
                                   width=15, state='readonly',
                                   font=Theme.FONTS['body'])
        filter_values = ['Tous'] + [info['label'] for info in RESULTATS.values()]
        filter_combo['values'] = filter_values
        filter_combo.pack(side=tk.LEFT, padx=(8, 0))
        filter_combo.bind('<<ComboboxSelected>>', lambda e: self._load_chantiers())

        tk.Label(filter_frame, text="Type de marche:",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT, padx=(16, 0))

        type_marche_combo = ttk.Combobox(filter_frame, textvariable=self.type_marche_var,
                                        width=18, state='readonly',
                                        font=Theme.FONTS['body'])
        type_marche_values = ['Tous'] + list(TYPES_MARCHE.values())
        type_marche_combo['values'] = type_marche_values
        type_marche_combo.pack(side=tk.LEFT, padx=(8, 0))
        type_marche_combo.bind('<<ComboboxSelected>>', lambda e: self._load_chantiers())

        # Stats
        self.stats_frame = tk.Frame(top_bar, bg=Theme.COLORS['bg_alt'], padx=12, pady=8,
                                   highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        self.stats_frame.pack(side=tk.RIGHT)

        self.stats_labels = {}

        # Tableau des chantiers
        table_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                              highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'nom', 'lieu', 'lot', 'type_marche', 'montant', 'resultat', 'concurrent', 'date')
        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        col_config = {
            'id': ('ID', 50, 'center'),
            'nom': ('Nom du chantier', 220, 'w'),
            'lieu': ('Lieu', 130, 'w'),
            'lot': ('Lot', 70, 'center'),
            'type_marche': ('Type', 130, 'center'),
            'montant': ('Montant HT', 110, 'e'),
            'resultat': ('Resultat', 90, 'center'),
            'concurrent': ('Concurrent', 130, 'w'),
            'date': ('Date', 90, 'center'),
        }

        for col, (text, width, anchor) in col_config.items():
            self.tree.heading(col, text=text)
            self.tree.column(col, width=width, anchor=anchor, minwidth=40)

        # Tags pour les couleurs
        for key, info in RESULTATS.items():
            self.tree.tag_configure(key, background=info['bg'])

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.tree.yview)
        hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky='nsew')
        vsb.grid(row=0, column=1, sticky='ns')
        hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Double-clic pour ouvrir
        self.tree.bind('<Double-1>', lambda e: self._open_chantier())

        # Menu contextuel (clic droit)
        self.context_menu = tk.Menu(self.tree, tearoff=0)

        # Sous-menu Copier
        self.copy_menu = tk.Menu(self.context_menu, tearoff=0)
        self.copy_menu.add_command(label="Nom du chantier", command=lambda: self._copy_field('nom'))
        self.copy_menu.add_command(label="Lieu", command=lambda: self._copy_field('lieu'))
        self.copy_menu.add_command(label="Lot", command=lambda: self._copy_field('lot'))
        self.copy_menu.add_command(label="Type de marche", command=lambda: self._copy_field('type_marche'))
        self.copy_menu.add_command(label="Montant HT", command=lambda: self._copy_field('montant'))
        self.copy_menu.add_command(label="Resultat", command=lambda: self._copy_field('resultat'))
        self.copy_menu.add_command(label="Concurrent", command=lambda: self._copy_field('concurrent'))
        self.copy_menu.add_command(label="Date", command=lambda: self._copy_field('date'))
        self.copy_menu.add_separator()
        self.copy_menu.add_command(label="Toutes les informations", command=self._copy_all_fields)

        self.context_menu.add_cascade(label="Copier", menu=self.copy_menu)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Ouvrir le chiffrage", command=self._open_chantier)
        self.context_menu.add_command(label="Modifier le chantier", command=self._edit_chantier)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Supprimer le chantier", command=self._delete_chantier)

        self.tree.bind('<Button-3>', self._show_context_menu)

        # Barre d'actions
        action_bar = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=56)
        action_bar.pack(fill=tk.X, pady=(12, 0))

        tk.Button(action_bar, text="Ouvrir le chiffrage",
                 font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._open_chantier).pack(side=tk.LEFT)

        tk.Button(action_bar, text="Modifier",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'],
                 bd=0, padx=16, pady=10, cursor='hand2',
                 command=self._edit_chantier).pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(action_bar, text="Supprimer",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['danger'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=16, pady=10, cursor='hand2',
                 command=self._delete_chantier).pack(side=tk.LEFT, padx=(8, 0))

        tk.Button(action_bar, text="Fermer",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._on_close).pack(side=tk.RIGHT)

    def _load_chantiers(self):
        """Charge la liste des chantiers"""
        # Determiner le filtre resultat
        filtre = self.filter_var.get()
        resultat_filtre = None

        if filtre != "Tous":
            for key, info in RESULTATS.items():
                if info['label'] == filtre:
                    resultat_filtre = key
                    break

        # Determiner le filtre type de marche
        type_marche_filtre_label = self.type_marche_var.get()
        type_marche_filtre = None

        if type_marche_filtre_label != "Tous":
            for key, label in TYPES_MARCHE.items():
                if label == type_marche_filtre_label:
                    type_marche_filtre = key
                    break

        chantiers = self.db.get_chantiers(resultat_filtre, type_marche_filtre)

        # Vider le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Remplir
        for c in chantiers:
            resultat = c.get('resultat', 'INCONNU')
            date = c.get('date_creation', '')[:10] if c.get('date_creation') else ''

            type_marche = c.get('type_marche', 'PUBLIC')
            type_marche_label = TYPES_MARCHE.get(type_marche, TYPES_MARCHE['PUBLIC'])

            self.tree.insert('', tk.END, values=(
                c['id'],
                c['nom'],
                c.get('lieu', '') or '-',
                c.get('lot', '') or '-',
                type_marche_label,
                f"{c.get('montant_ht', 0):.2f} EUR",
                get_resultat_label(resultat),
                c.get('concurrent', '') or '-',
                date,
            ), tags=(resultat,))

        # Mettre a jour les stats
        self._update_stats()

    def _update_stats(self):
        """Met a jour les statistiques"""
        stats = self.db.get_stats_marches()

        # Nettoyer
        for widget in self.stats_frame.winfo_children():
            widget.destroy()

        # Afficher
        tk.Label(self.stats_frame,
                text=f"Total: {stats['total_chantiers']} chantier(s)",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT, padx=(0, 16))

        if stats['total_chantiers'] > 0:
            tk.Label(self.stats_frame,
                    text=f"Gagnes: {stats['par_resultat'].get('GAGNE', 0)}",
                    font=Theme.FONTS['small'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=RESULTATS['GAGNE']['color']).pack(side=tk.LEFT, padx=(0, 8))

            tk.Label(self.stats_frame,
                    text=f"Perdus: {stats['par_resultat'].get('PERDU', 0)}",
                    font=Theme.FONTS['small'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=RESULTATS['PERDU']['color']).pack(side=tk.LEFT, padx=(0, 16))

            if stats['taux_reussite'] > 0:
                tk.Label(self.stats_frame,
                        text=f"Taux reussite: {stats['taux_reussite']:.1f}%",
                        font=Theme.FONTS['small_bold'],
                        bg=Theme.COLORS['bg_alt'],
                        fg=Theme.COLORS['success']).pack(side=tk.LEFT, padx=(0, 16))

            tk.Label(self.stats_frame,
                    text=f"CA gagne: {stats['montant_gagne']:.0f} EUR",
                    font=Theme.FONTS['small_bold'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['secondary']).pack(side=tk.LEFT)

    def _new_chantier(self):
        """Cree un nouveau chantier"""
        dialog = DPGFImportDialog(self.window, self.db)
        if dialog.result and dialog.chantier_id:
            self._load_chantiers()
            # Ouvrir le chiffrage
            DPGFChiffrageView(self.window, self.db, dialog.chantier_id,
                             on_close_callback=self._load_chantiers)

    def _open_chantier(self):
        """Ouvre le chiffrage du chantier selectionne"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez un chantier")
            return

        item = self.tree.item(selection[0])
        chantier_id = item['values'][0]

        DPGFChiffrageView(self.window, self.db, chantier_id,
                         on_close_callback=self._load_chantiers)

    def _edit_chantier(self):
        """Modifie le chantier selectionne"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez un chantier")
            return

        item = self.tree.item(selection[0])
        chantier_id = item['values'][0]

        dialog = ChantierEditDialog(self.window, self.db, chantier_id)
        if dialog.result:
            self._load_chantiers()

    def _delete_chantier(self):
        """Supprime le chantier selectionne"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez un chantier")
            return

        item = self.tree.item(selection[0])
        chantier_id = item['values'][0]
        nom = item['values'][1]

        if messagebox.askyesno("Confirmer",
            f"Supprimer le chantier '{nom}' et tous ses articles ?\n\n"
            f"Cette action est irreversible."):
            self.db.delete_chantier(chantier_id)
            self._load_chantiers()

    def _show_context_menu(self, event):
        """Affiche le menu contextuel"""
        # Selectionner la ligne sous le curseur
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.tk_popup(event.x_root, event.y_root)

    def _copy_field(self, field):
        """Copie un champ specifique dans le presse-papier"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        # Mapping des champs vers les indices
        field_indices = {
            'nom': 1,
            'lieu': 2,
            'lot': 3,
            'type_marche': 4,
            'montant': 5,
            'resultat': 6,
            'concurrent': 7,
            'date': 8,
        }

        if field in field_indices:
            value = str(values[field_indices[field]])
            self.window.clipboard_clear()
            self.window.clipboard_append(value)

    def _copy_all_fields(self):
        """Copie toutes les informations dans le presse-papier"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        values = item['values']

        text = f"""Nom: {values[1]}
Lieu: {values[2]}
Lot: {values[3]}
Type de marche: {values[4]}
Montant HT: {values[5]}
Resultat: {values[6]}
Concurrent: {values[7]}
Date: {values[8]}"""

        self.window.clipboard_clear()
        self.window.clipboard_append(text)

    def _on_close(self):
        """Ferme la vue"""
        if self.on_close_callback:
            self.on_close_callback()
        self.window.destroy()
