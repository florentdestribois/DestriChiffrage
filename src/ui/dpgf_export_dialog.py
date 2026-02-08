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

        # Ouvrir sur toute la hauteur de l'ecran
        screen_height = self.dialog.winfo_screenheight()
        window_height = screen_height - 80  # Marge pour la barre des taches
        self.dialog.geometry(f"1100x{window_height}")
        self.dialog.minsize(1000, 800)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer horizontalement, en haut de l'ecran
        self.dialog.update_idletasks()
        x = (self.dialog.winfo_screenwidth() - 1100) // 2
        self.dialog.geometry(f"+{x}+0")

        # Charger les donnees du premier article et produit pour l'apercu
        self._load_preview_data()

        # Variables
        self.version_var = tk.StringVar(value="client")
        self.export_dir_var = tk.StringVar()
        self.include_fiches_var = tk.BooleanVar(value=False)
        self.include_devis_var = tk.BooleanVar(value=False)

        # Options de nommage des fichiers PDF (issue #22)
        self.prefix_code_article_var = tk.BooleanVar(value=True)
        self.include_id_produit_var = tk.BooleanVar(value=False)
        self.include_designation_var = tk.BooleanVar(value=True)

        self._create_widgets()
        self.dialog.wait_window()

    def _load_preview_data(self):
        """Charge les donnees du premier article et produit pour l'apercu"""
        self.preview_code_article = ""
        self.preview_produit_id = ""
        self.preview_designation = ""

        # Recuperer le premier article du chantier
        articles = self.db.get_articles_dpgf(self.chantier_id)
        if articles:
            first_article = articles[0]
            self.preview_code_article = first_article.get('code', '') or ''

            # Recuperer le premier produit lie a cet article
            produits_lies = self.db.get_produits_article(first_article['id'])
            if produits_lies:
                first_liaison = produits_lies[0]
                self.preview_produit_id = str(first_liaison.get('produit_id', ''))
                produit = self.db.get_produit(first_liaison['produit_id'])
                if produit:
                    self.preview_designation = produit.get('designation', '') or ''

        # Valeurs par defaut si aucune donnee
        if not self.preview_code_article:
            self.preview_code_article = "(aucun code)"
        if not self.preview_produit_id:
            self.preview_produit_id = "(aucun ID)"
        if not self.preview_designation:
            self.preview_designation = "(aucune designation)"

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
                      activebackground=Theme.COLORS['bg_alt'],
                      command=self._on_version_change).pack(anchor='w')

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
                      activebackground=Theme.COLORS['bg_alt'],
                      command=self._on_version_change).pack(anchor='w')

        tk.Label(interne_frame,
                text="Export complet avec: Temps MO, Couts detailles, Marge, Produits lies",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w', padx=(24, 0))

        # Version Odoo
        odoo_frame = tk.Frame(options_card, bg=Theme.COLORS['bg_alt'])
        odoo_frame.pack(fill=tk.X, pady=4)

        tk.Radiobutton(odoo_frame, text="Version Odoo (format compatible ERP)",
                      variable=self.version_var, value="odoo",
                      font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'],
                      fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'],
                      activebackground=Theme.COLORS['bg_alt'],
                      command=self._on_version_change).pack(anchor='w')

        tk.Label(odoo_frame,
                text="Export au format Odoo: Client, Articles, Description, Quantite, Prix, TVA",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w', padx=(24, 0))

        # Section documents PDF
        self.pdf_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                           highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        self.pdf_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(self.pdf_card, text="DOCUMENTS PDF",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Dossier destination
        dir_frame = tk.Frame(self.pdf_card, bg=Theme.COLORS['bg_alt'])
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
        tk.Checkbutton(self.pdf_card, text="Inclure les fiches techniques",
                      variable=self.include_fiches_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2', command=self._toggle_naming_options).pack(anchor='w', pady=(8, 4))

        tk.Checkbutton(self.pdf_card, text="Inclure les devis fournisseur",
                      variable=self.include_devis_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2', command=self._toggle_naming_options).pack(anchor='w')

        tk.Label(self.pdf_card,
                text="Les fichiers seront copies dans des sous-dossiers Fiches_techniques/ et Devis_fournisseur/",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w', pady=(8, 0))

        # Section options de nommage des fichiers PDF (issue #22)
        # Cette section est affichee uniquement si fiches ou devis sont selectionnes
        self.naming_frame = tk.Frame(self.pdf_card, bg=Theme.COLORS['bg_alt'])

        ttk.Separator(self.naming_frame, orient='horizontal').pack(fill=tk.X, pady=(12, 8))

        tk.Label(self.naming_frame, text="NOMMAGE DES FICHIERS",
                font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 8))

        tk.Checkbutton(self.naming_frame, text="Prefixer avec le code article DPGF",
                      variable=self.prefix_code_article_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2', command=self._update_naming_preview).pack(anchor='w', pady=(0, 4))

        tk.Checkbutton(self.naming_frame, text="Inclure l'ID du produit",
                      variable=self.include_id_produit_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2', command=self._update_naming_preview).pack(anchor='w', pady=(0, 4))

        tk.Checkbutton(self.naming_frame, text="Inclure la designation du produit",
                      variable=self.include_designation_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2', command=self._update_naming_preview).pack(anchor='w')

        # Apercu du format de nom
        preview_frame = tk.Frame(self.naming_frame, bg=Theme.COLORS['bg'], padx=8, pady=6)
        preview_frame.pack(fill=tk.X, pady=(8, 0))

        tk.Label(preview_frame, text="Apercu:",
                font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.naming_preview_label = tk.Label(preview_frame, text="",
                font=Theme.FONTS['mono'],
                bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text'])
        self.naming_preview_label.pack(anchor='w')

        self._update_naming_preview()
        # Masquer par defaut (sera affiche si fiches ou devis selectionnes)
        # self.naming_frame n'est pas pack() ici, il sera affiche par _toggle_naming_options

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

    def _on_version_change(self):
        """Gere le changement de version d'export"""
        # La section PDF est toujours visible pour tous les formats
        pass

    def _toggle_naming_options(self):
        """Affiche ou masque les options de nommage selon si fiches ou devis sont selectionnes"""
        if self.include_fiches_var.get() or self.include_devis_var.get():
            self.naming_frame.pack(fill=tk.X)
            self._update_naming_preview()
        else:
            self.naming_frame.pack_forget()

    def _update_naming_preview(self):
        """Met a jour l'apercu du format de nommage des fichiers base sur le premier article/produit"""
        parts = []

        if self.prefix_code_article_var.get():
            if self.preview_code_article and self.preview_code_article != "(aucun code)":
                # Nettoyer le code article
                safe_code = "".join(c for c in self.preview_code_article if c.isalnum() or c in ('-', '_', '.')).strip()
                if safe_code:
                    parts.append(safe_code)

        if self.include_id_produit_var.get():
            if self.preview_produit_id and self.preview_produit_id != "(aucun ID)":
                parts.append(self.preview_produit_id)

        if self.include_designation_var.get():
            if self.preview_designation and self.preview_designation != "(aucune designation)":
                # Nettoyer la designation
                safe_des = "".join(c for c in self.preview_designation if c.isalnum() or c in (' ', '-', '_')).strip()
                safe_des = safe_des[:50]  # Limiter la longueur
                if safe_des:
                    parts.append(safe_des)

        if parts:
            preview = "_".join(parts) + "_fiche.pdf"
        else:
            preview = "(aucune option selectionnee - nom par defaut)"

        self.naming_preview_label.config(text=preview)

    def _export(self):
        """Execute l'export"""
        version = self.version_var.get()
        version_client = version == "client"
        version_odoo = version == "odoo"
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
        if version_odoo:
            suffix = "odoo"
        elif version_client:
            suffix = "client"
        else:
            suffix = "interne"
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
            # Export CSV selon le format
            if version_odoo:
                count = self.db.export_dpgf_odoo(self.chantier_id, filepath)
            else:
                count = self.db.export_dpgf_csv(self.chantier_id, filepath, version_client)

            # Export des fichiers PDF si demande
            nb_fiches = 0
            nb_devis = 0
            if (include_fiches or include_devis) and export_dir:
                # Options de nommage (issue #22)
                naming_options = {
                    'prefix_code_article': self.prefix_code_article_var.get(),
                    'include_id_produit': self.include_id_produit_var.get(),
                    'include_designation': self.include_designation_var.get()
                }
                nb_fiches, nb_devis = self.db.export_dpgf_files(
                    self.chantier_id,
                    export_dir,
                    include_fiches,
                    include_devis,
                    naming_options
                )

            # Arreter la barre de progression
            if include_fiches or include_devis:
                self.progress_bar.stop()
                self.progress_frame.pack_forget()

            # Construire le message de resultat
            message = f"DPGF exporte avec succes!\n\n"
            message += f"Fichier CSV: {os.path.basename(filepath)}\n"
            message += f"Articles exportes: {count}\n"

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
