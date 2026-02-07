"""
DestriChiffrage - Dialogue d'import DPGF
=========================================
Import d'un fichier DPGF CSV avec creation de chantier
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme

# Types de marche disponibles
TYPES_MARCHE = {
    'PUBLIC': 'Marche public',
    'PARTICULIER': 'Particulier avec DPGF',
    'ODOO': 'Export Odoo',
}


class DPGFImportDialog:
    """Dialogue d'import DPGF avec creation de chantier"""

    def __init__(self, parent, db):
        self.db = db
        self.parent = parent
        self.result = False
        self.chantier_id = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau chantier / Import DPGF")
        self.dialog.geometry("850x750")
        self.dialog.minsize(800, 700)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 850) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 750) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets du formulaire"""
        # Header
        Theme.create_header(self.dialog, "Nouveau chantier / Import DPGF", icon="📁")

        # Main frame avec scroll
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card - Informations chantier
        info_card = Theme.create_card(main_frame)
        info_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(info_card, text="INFORMATIONS DU CHANTIER",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Formulaire
        form_frame = tk.Frame(info_card, bg=Theme.COLORS['bg_alt'])
        form_frame.pack(fill=tk.X)

        self.entries = {}

        # Ligne 1: Nom du chantier et Nom du client
        row1 = tk.Frame(form_frame, bg=Theme.COLORS['bg_alt'])
        row1.pack(fill=tk.X, pady=4)

        # Nom du chantier
        frame_nom = tk.Frame(row1, bg=Theme.COLORS['bg_alt'])
        frame_nom.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(frame_nom, text="Nom du chantier *", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_light']).pack(anchor='w')
        entry_nom = tk.Entry(frame_nom, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                           bd=1, relief='solid')
        entry_nom.pack(fill=tk.X, pady=(4, 0))
        self.entries['nom'] = entry_nom

        # Nom du client
        frame_client = tk.Frame(row1, bg=Theme.COLORS['bg_alt'])
        frame_client.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(frame_client, text="Nom du client", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_light']).pack(anchor='w')
        entry_client = tk.Entry(frame_client, font=Theme.FONTS['body'],
                               bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                               bd=1, relief='solid')
        entry_client.pack(fill=tk.X, pady=(4, 0))
        self.entries['nom_client'] = entry_client

        # Ligne 2: Type de marche et Lieu
        row2 = tk.Frame(form_frame, bg=Theme.COLORS['bg_alt'])
        row2.pack(fill=tk.X, pady=4)

        # Type de marche
        frame_type = tk.Frame(row2, bg=Theme.COLORS['bg_alt'])
        frame_type.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(frame_type, text="Type de marche", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_light']).pack(anchor='w')
        self.type_marche_var = tk.StringVar(value='PUBLIC')
        type_combo = ttk.Combobox(frame_type, textvariable=self.type_marche_var,
                                 values=list(TYPES_MARCHE.values()),
                                 state='readonly', font=Theme.FONTS['body'])
        type_combo.set(TYPES_MARCHE['PUBLIC'])
        type_combo.pack(fill=tk.X, pady=(4, 0))

        # Lieu
        frame_lieu = tk.Frame(row2, bg=Theme.COLORS['bg_alt'])
        frame_lieu.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(frame_lieu, text="Lieu / Adresse", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_light']).pack(anchor='w')
        entry_lieu = tk.Entry(frame_lieu, font=Theme.FONTS['body'],
                             bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                             bd=1, relief='solid')
        entry_lieu.pack(fill=tk.X, pady=(4, 0))
        self.entries['lieu'] = entry_lieu

        # Ligne 3: Type de projet et Lot
        row3 = tk.Frame(form_frame, bg=Theme.COLORS['bg_alt'])
        row3.pack(fill=tk.X, pady=4)

        # Type de projet
        frame_projet = tk.Frame(row3, bg=Theme.COLORS['bg_alt'])
        frame_projet.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 8))
        tk.Label(frame_projet, text="Type de projet", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_light']).pack(anchor='w')
        entry_projet = tk.Entry(frame_projet, font=Theme.FONTS['body'],
                               bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                               bd=1, relief='solid')
        entry_projet.pack(fill=tk.X, pady=(4, 0))
        self.entries['type_projet'] = entry_projet

        # Lot
        frame_lot = tk.Frame(row3, bg=Theme.COLORS['bg_alt'])
        frame_lot.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(8, 0))
        tk.Label(frame_lot, text="Lot", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_light']).pack(anchor='w')
        entry_lot = tk.Entry(frame_lot, font=Theme.FONTS['body'],
                            bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                            bd=1, relief='solid')
        entry_lot.pack(fill=tk.X, pady=(4, 0))
        self.entries['lot'] = entry_lot

        # Notes
        notes_frame = tk.Frame(info_card, bg=Theme.COLORS['bg_alt'])
        notes_frame.pack(fill=tk.X, pady=(8, 0))

        tk.Label(notes_frame, text="Notes", font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_light']).pack(anchor='w')

        self.notes_text = tk.Text(notes_frame, width=60, height=3, font=Theme.FONTS['body'],
                                 bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                 bd=1, relief='solid')
        self.notes_text.pack(fill=tk.X, pady=(4, 0))

        # Card - Import DPGF
        import_card = Theme.create_card(main_frame)
        import_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(import_card, text="IMPORT DPGF (OPTIONNEL)",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Selection fichier
        file_frame = tk.Frame(import_card, bg=Theme.COLORS['bg_alt'])
        file_frame.pack(fill=tk.X)

        tk.Label(file_frame, text="Fichier DPGF (CSV)",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_light']).pack(anchor='w')

        entry_frame = tk.Frame(file_frame, bg=Theme.COLORS['bg_alt'])
        entry_frame.pack(fill=tk.X, pady=(4, 0))

        self.file_entry = tk.Entry(entry_frame, width=50, font=Theme.FONTS['body'],
                                  bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                  bd=1, relief='solid')
        self.file_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        Theme.create_button(entry_frame, "Parcourir...", command=self._browse_file,
                           style='ghost', padx=16, pady=6).pack(side=tk.LEFT, padx=(8, 0))

        # Info format
        tk.Label(import_card,
                text="Format CSV attendu: CODE;NIVEAU;DESIGNATION;DESCRIPTION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES;TVA",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted'],
                wraplength=600).pack(anchor='w', pady=(12, 0))

        # Bouton template
        Theme.create_button(import_card, "Telecharger le modele DPGF", command=self._download_template,
                           style='secondary', padx=12, pady=4).pack(anchor='w', pady=(8, 0))

        # Boutons action
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(16, 0))

        Theme.create_button(btn_frame, "Annuler", command=self.dialog.destroy,
                           style='ghost', padx=24).pack(side=tk.RIGHT, padx=(8, 0))
        Theme.create_button(btn_frame, "Creer le chantier", command=self._save,
                           style='primary', padx=24).pack(side=tk.RIGHT)

    def _browse_file(self):
        """Ouvre le dialogue de selection de fichier"""
        filepath = filedialog.askopenfilename(
            title="Selectionner un fichier DPGF",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if filepath:
            self.file_entry.delete(0, tk.END)
            self.file_entry.insert(0, filepath)

    def _download_template(self):
        """Telecharge un modele DPGF"""
        filepath = filedialog.asksaveasfilename(
            title="Enregistrer le modele DPGF",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile="modele_dpgf.csv"
        )
        if filepath:
            try:
                self.db.create_dpgf_template(filepath)
                messagebox.showinfo("Modele cree",
                    f"Le modele DPGF a ete cree avec succes!\n\n"
                    f"Fichier: {filepath}")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de la creation:\n{e}")

    def _get_type_marche_key(self):
        """Retourne la cle du type de marche selectionne"""
        value = self.type_marche_var.get()
        for key, label in TYPES_MARCHE.items():
            if label == value:
                return key
        return 'PUBLIC'

    def _save(self):
        """Cree le chantier et importe le DPGF si fourni"""
        # Validation
        nom = self.entries['nom'].get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du chantier est obligatoire")
            return

        # Validation nom_client obligatoire si type = ODOO
        type_marche = self._get_type_marche_key()
        nom_client = self.entries['nom_client'].get().strip()
        if type_marche == 'ODOO' and not nom_client:
            messagebox.showerror("Erreur",
                "Le nom du client est obligatoire pour l'export Odoo")
            return

        # Creer le chantier
        data = {
            'nom': nom,
            'nom_client': nom_client,
            'type_marche': type_marche,
            'lieu': self.entries['lieu'].get().strip(),
            'type_projet': self.entries['type_projet'].get().strip(),
            'lot': self.entries['lot'].get().strip(),
            'notes': self.notes_text.get('1.0', tk.END).strip(),
        }

        try:
            self.chantier_id = self.db.add_chantier(data)

            # Importer le DPGF si fichier fourni
            filepath = self.file_entry.get().strip()
            if filepath and os.path.exists(filepath):
                count = self.db.import_dpgf_csv(self.chantier_id, filepath)
                messagebox.showinfo("Import termine",
                    f"Chantier cree avec succes!\n\n"
                    f"{count} article(s) DPGF importe(s)")
            else:
                messagebox.showinfo("Chantier cree",
                    f"Le chantier '{nom}' a ete cree avec succes!\n\n"
                    f"Vous pouvez maintenant ajouter des articles manuellement.")

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de la creation:\n{e}")


class ChantierEditDialog:
    """Dialogue d'edition d'un chantier existant"""

    def __init__(self, parent, db, chantier_id):
        self.db = db
        self.parent = parent
        self.chantier_id = chantier_id
        self.result = False

        # Charger les donnees
        self.data = self.db.get_chantier(chantier_id) or {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier le chantier")
        self.dialog.geometry("750x680")
        self.dialog.minsize(700, 630)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 750) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 680) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        Theme.create_header(self.dialog, "Modifier le chantier", icon="✏️")

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card - Informations
        info_card = Theme.create_card(main_frame)
        info_card.pack(fill=tk.X)

        self.entries = {}

        fields = [
            ('nom', 'Nom du chantier *'),
            ('nom_client', 'Nom du client'),
            ('lieu', 'Lieu / Adresse'),
            ('type_projet', 'Type de projet'),
            ('lot', 'Lot'),
        ]

        row = 0
        for field, label in fields:
            tk.Label(info_card, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='e', padx=(5, 10), pady=8)

            entry = tk.Entry(info_card, width=36, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                           bd=1, relief='solid')
            entry.insert(0, self.data.get(field, '') or '')
            entry.grid(row=row, column=1, sticky='w', padx=5, pady=8)
            self.entries[field] = entry
            row += 1

        # Type de marche
        tk.Label(info_card, text="Type de marche", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='e', padx=(5, 10), pady=8)

        self.type_marche_var = tk.StringVar()
        current_type = self.data.get('type_marche', 'PUBLIC') or 'PUBLIC'
        self.type_marche_var.set(TYPES_MARCHE.get(current_type, TYPES_MARCHE['PUBLIC']))

        type_combo = ttk.Combobox(info_card, textvariable=self.type_marche_var,
                                 values=list(TYPES_MARCHE.values()),
                                 state='readonly', font=Theme.FONTS['body'], width=34)
        type_combo.grid(row=row, column=1, sticky='w', padx=5, pady=8)
        row += 1

        # Notes
        tk.Label(info_card, text="Notes", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='ne', padx=(5, 10), pady=8)

        self.notes_text = tk.Text(info_card, width=36, height=4, font=Theme.FONTS['body'],
                                 bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                 bd=1, relief='solid')
        self.notes_text.insert('1.0', self.data.get('notes', '') or '')
        self.notes_text.grid(row=row, column=1, sticky='w', padx=5, pady=8)

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(20, 0))

        Theme.create_button(btn_frame, "Annuler", command=self.dialog.destroy,
                           style='ghost', padx=24).pack(side=tk.RIGHT, padx=(8, 0))
        Theme.create_button(btn_frame, "Enregistrer", command=self._save,
                           style='primary', padx=24).pack(side=tk.RIGHT)

    def _get_type_marche_key(self):
        """Retourne la cle du type de marche selectionne"""
        value = self.type_marche_var.get()
        for key, label in TYPES_MARCHE.items():
            if label == value:
                return key
        return 'PUBLIC'

    def _save(self):
        """Enregistre les modifications"""
        nom = self.entries['nom'].get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du chantier est obligatoire")
            return

        # Validation nom_client obligatoire si type = ODOO
        type_marche = self._get_type_marche_key()
        nom_client = self.entries['nom_client'].get().strip()
        if type_marche == 'ODOO' and not nom_client:
            messagebox.showerror("Erreur",
                "Le nom du client est obligatoire pour l'export Odoo")
            return

        data = {
            'nom': nom,
            'nom_client': nom_client,
            'type_marche': type_marche,
            'lieu': self.entries['lieu'].get().strip(),
            'type_projet': self.entries['type_projet'].get().strip(),
            'lot': self.entries['lot'].get().strip(),
            'notes': self.notes_text.get('1.0', tk.END).strip(),
            'montant_ht': self.data.get('montant_ht', 0),
            'resultat': self.data.get('resultat', 'EN_COURS'),
            'concurrent': self.data.get('concurrent', ''),
            'montant_concurrent': self.data.get('montant_concurrent'),
        }

        try:
            self.db.update_chantier(self.chantier_id, data)
            self.result = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur lors de l'enregistrement:\n{e}")
