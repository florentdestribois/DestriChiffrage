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


class DPGFImportDialog:
    """Dialogue d'import DPGF avec creation de chantier"""

    def __init__(self, parent, db):
        self.db = db
        self.parent = parent
        self.result = False
        self.chantier_id = None

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Nouveau chantier / Import DPGF")
        self.dialog.geometry("700x580")
        self.dialog.minsize(680, 560)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 580) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets du formulaire"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Nouveau chantier / Import DPGF",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card - Informations chantier
        info_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        info_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(info_card, text="INFORMATIONS DU CHANTIER",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Formulaire
        form_frame = tk.Frame(info_card, bg=Theme.COLORS['bg_alt'])
        form_frame.pack(fill=tk.X)

        self.entries = {}

        fields = [
            ('nom', 'Nom du chantier *', 0, 0),
            ('lieu', 'Lieu / Adresse', 0, 1),
            ('type_projet', 'Type de projet', 1, 0),
            ('lot', 'Lot', 1, 1),
        ]

        for field, label, row, col in fields:
            frame = tk.Frame(form_frame, bg=Theme.COLORS['bg_alt'])
            frame.grid(row=row, column=col, sticky='ew', padx=8, pady=8)

            tk.Label(frame, text=label, font=Theme.FONTS['small'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text_light']).pack(anchor='w')

            entry = tk.Entry(frame, width=28, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                           bd=1, relief='solid')
            entry.pack(fill=tk.X, pady=(4, 0))
            self.entries[field] = entry

        form_frame.columnconfigure(0, weight=1)
        form_frame.columnconfigure(1, weight=1)

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
        import_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                              highlightbackground=Theme.COLORS['border'], highlightthickness=1)
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

        tk.Button(entry_frame, text="Parcourir...", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=16, pady=6, cursor='hand2',
                 command=self._browse_file).pack(side=tk.LEFT, padx=(8, 0))

        # Info format
        tk.Label(import_card,
                text="Format CSV attendu: CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted'],
                wraplength=600).pack(anchor='w', pady=(12, 0))

        # Bouton template
        tk.Button(import_card, text="Telecharger le modele DPGF",
                 font=Theme.FONTS['small'],
                 bg=Theme.COLORS['secondary'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=12, pady=4, cursor='hand2',
                 command=self._download_template).pack(anchor='w', pady=(8, 0))

        # Boutons action
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(16, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Creer le chantier", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._save).pack(side=tk.RIGHT)

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

    def _save(self):
        """Cree le chantier et importe le DPGF si fourni"""
        # Validation
        nom = self.entries['nom'].get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du chantier est obligatoire")
            return

        # Creer le chantier
        data = {
            'nom': nom,
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
        self.dialog.geometry("600x500")
        self.dialog.minsize(580, 480)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 500) // 2
        self.dialog.geometry(f"+{x}+{y}")

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Modifier le chantier",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card - Informations
        info_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        info_card.pack(fill=tk.X)

        self.entries = {}

        fields = [
            ('nom', 'Nom du chantier *'),
            ('lieu', 'Lieu / Adresse'),
            ('type_projet', 'Type de projet'),
            ('lot', 'Lot'),
        ]

        for i, (field, label) in enumerate(fields):
            tk.Label(info_card, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text']).grid(row=i, column=0, sticky='e', padx=(5, 10), pady=8)

            entry = tk.Entry(info_card, width=36, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                           bd=1, relief='solid')
            entry.insert(0, self.data.get(field, '') or '')
            entry.grid(row=i, column=1, sticky='w', padx=5, pady=8)
            self.entries[field] = entry

        # Notes
        row = len(fields)
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

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Enregistrer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._save).pack(side=tk.RIGHT)

    def _save(self):
        """Enregistre les modifications"""
        nom = self.entries['nom'].get().strip()
        if not nom:
            messagebox.showerror("Erreur", "Le nom du chantier est obligatoire")
            return

        data = {
            'nom': nom,
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
