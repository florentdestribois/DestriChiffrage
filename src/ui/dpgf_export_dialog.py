"""
DestriChiffrage - Dialogue d'export DPGF
=========================================
Export du DPGF chiffre vers CSV avec option d'export des fiches techniques et devis
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
from datetime import datetime

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme


class DPGFExportDialog:
    """Dialogue d'export DPGF avec options pour fiches techniques et devis"""

    def __init__(self, parent, db, chantier_id):
        self.db = db
        self.parent = parent
        self.chantier_id = chantier_id
        self.result = False

        # Charger les donnees du chantier
        self.chantier = self.db.get_chantier(chantier_id) or {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Exporter le DPGF")
        self.dialog.geometry("600x580")
        self.dialog.minsize(580, 560)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 600) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 580) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Variables
        self.version_var = tk.StringVar(value="client")
        self.export_dir_var = tk.StringVar()
        self.include_fiches_var = tk.BooleanVar(value=False)
        self.include_devis_var = tk.BooleanVar(value=False)

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Exporter le DPGF",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame avec scroll
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info chantier
        info_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=16, pady=12,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        info_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(info_card, text=f"Chantier: {self.chantier.get('nom', '')}",
                font=Theme.FONTS['body_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(anchor='w')

        articles = self.db.get_articles_dpgf(self.chantier_id)
        total = sum(a['prix_total_ht'] for a in articles)

        tk.Label(info_card,
                text=f"{len(articles)} article(s) - Total: {total:.2f} EUR HT",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        # Options d'export CSV
        options_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                               highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        options_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(options_card, text="VERSION D'EXPORT",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Version client
        client_frame = tk.Frame(options_card, bg=Theme.COLORS['bg_alt'])
        client_frame.pack(fill=tk.X, pady=4)

        tk.Radiobutton(client_frame, text="Version client (simplifiee)",
                      variable=self.version_var, value="client",
                      font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'],
                      fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'],
                      activebackground=Theme.COLORS['bg_alt']).pack(anchor='w')

        tk.Label(client_frame,
                text="Export avec: Code, Designation, Unite, Quantite, Prix unitaire, Prix total",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w', padx=(24, 0))

        # Version interne
        interne_frame = tk.Frame(options_card, bg=Theme.COLORS['bg_alt'])
        interne_frame.pack(fill=tk.X, pady=4)

        tk.Radiobutton(interne_frame, text="Version interne (complete)",
                      variable=self.version_var, value="interne",
                      font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'],
                      fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'],
                      activebackground=Theme.COLORS['bg_alt']).pack(anchor='w')

        tk.Label(interne_frame,
                text="Export complet avec: Temps MO, Couts detailles, Marge, Produits lies",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w', padx=(24, 0))

        # Section documents PDF
        pdf_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                           highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        pdf_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(pdf_card, text="DOCUMENTS PDF",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Dossier destination
        dir_frame = tk.Frame(pdf_card, bg=Theme.COLORS['bg_alt'])
        dir_frame.pack(fill=tk.X, pady=(0, 10))

        tk.Label(dir_frame, text="Dossier destination:",
                font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 4))

        dir_input_frame = tk.Frame(dir_frame, bg=Theme.COLORS['bg_alt'])
        dir_input_frame.pack(fill=tk.X)

        self.dir_entry = tk.Entry(dir_input_frame, textvariable=self.export_dir_var,
                font=Theme.FONTS['small'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text'], bd=1, relief='solid',
                state='readonly')
        self.dir_entry.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(dir_input_frame, text="Parcourir",
                 font=Theme.FONTS['small'], bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'], bd=0, padx=10, pady=4,
                 cursor='hand2', command=self._browse_dir).pack(side=tk.LEFT, padx=(8, 0))

        # Checkboxes
        tk.Checkbutton(pdf_card, text="Inclure les fiches techniques",
                      variable=self.include_fiches_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2').pack(anchor='w', pady=(8, 4))

        tk.Checkbutton(pdf_card, text="Inclure les devis fournisseur",
                      variable=self.include_devis_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2').pack(anchor='w')

        tk.Label(pdf_card,
                text="Les fichiers seront copies dans des sous-dossiers Fiches_techniques/ et Devis_fournisseur/",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w', pady=(8, 0))

        # Barre de progression (cachee par defaut)
        self.progress_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        self.progress_frame.pack(fill=tk.X, pady=(0, 8))
        self.progress_frame.pack_forget()

        tk.Label(self.progress_frame, text="Export en cours...",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 4))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(8, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Exporter", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._export).pack(side=tk.RIGHT)

    def _browse_dir(self):
        """Ouvre le dialogue de selection du dossier"""
        directory = filedialog.askdirectory(
            title="Selectionner le dossier de destination pour les PDFs"
        )
        if directory:
            self.export_dir_var.set(directory)

    def _export(self):
        """Execute l'export"""
        version_client = self.version_var.get() == "client"
        include_fiches = self.include_fiches_var.get()
        include_devis = self.include_devis_var.get()
        export_dir = self.export_dir_var.get()

        # Validation
        if (include_fiches or include_devis) and not export_dir:
            messagebox.showwarning("Dossier manquant",
                                  "Veuillez selectionner un dossier de destination pour les PDFs.")
            return

        # Nom de fichier par defaut
        chantier_nom = self.chantier.get('nom', 'DPGF').replace(' ', '_')
        date_str = datetime.now().strftime('%Y%m%d')
        suffix = "client" if version_client else "interne"
        default_name = f"DPGF_{chantier_nom}_{suffix}_{date_str}.csv"

        filepath = filedialog.asksaveasfilename(
            title="Enregistrer le DPGF",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile=default_name,
            initialdir=export_dir if export_dir else None
        )

        if not filepath:
            return

        # Afficher la barre de progression si copie de fichiers
        if include_fiches or include_devis:
            self.progress_frame.pack(fill=tk.X, pady=(0, 8))
            self.progress_bar.start(10)
            self.dialog.update()

        try:
            # Export CSV
            count = self.db.export_dpgf_csv(self.chantier_id, filepath, version_client)

            # Export des fichiers PDF si demande
            nb_fiches = 0
            nb_devis = 0
            if (include_fiches or include_devis) and export_dir:
                nb_fiches, nb_devis = self.db.export_dpgf_files(
                    self.chantier_id,
                    export_dir,
                    include_fiches,
                    include_devis
                )

            # Arreter la barre de progression
            if include_fiches or include_devis:
                self.progress_bar.stop()
                self.progress_frame.pack_forget()

            # Construire le message de resultat
            message = f"DPGF exporte avec succes!\n\n"
            message += f"Fichier CSV: {os.path.basename(filepath)}\n"
            message += f"Articles: {count}\n"

            if include_fiches:
                message += f"Fiches techniques copiees: {nb_fiches}\n"
            if include_devis:
                message += f"Devis fournisseur copies: {nb_devis}\n"

            messagebox.showinfo("Export termine", message)

            self.result = True
            self.dialog.destroy()

        except Exception as e:
            if include_fiches or include_devis:
                self.progress_bar.stop()
                self.progress_frame.pack_forget()
            messagebox.showerror("Erreur", f"Erreur lors de l'export:\n{e}")
