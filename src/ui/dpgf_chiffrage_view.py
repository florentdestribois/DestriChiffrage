"""
DestriChiffrage - Vue de chiffrage DPGF
========================================
Vue principale pour chiffrer un DPGF avec support multi-produits
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog, filedialog
import os
import sys
import subprocess
import platform

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme
from ui.product_search_dialog import ProductSearchDialog, MultiProductSearchDialog


class DPGFChiffrageView:
    """Vue de chiffrage d'un DPGF"""

    def __init__(self, parent, db, chantier_id, on_close_callback=None):
        self.db = db
        self.parent = parent
        self.chantier_id = chantier_id
        self.on_close_callback = on_close_callback
        self.current_article_id = None

        # Charger les donnees du chantier
        self.chantier = self.db.get_chantier(chantier_id) or {}

        self.window = tk.Toplevel(parent)
        self.window.title(f"Chiffrage DPGF - {self.chantier.get('nom', 'Chantier')}")
        self.window.geometry("1400x800")
        self.window.minsize(1200, 700)
        self.window.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 1400) // 2
        y = (self.window.winfo_screenheight() - 800) // 2
        self.window.geometry(f"+{x}+{y}")

        # Fermeture
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        self._create_widgets()
        self._load_articles()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.window, bg=Theme.COLORS['primary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg=Theme.COLORS['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        # Titre
        title_frame = tk.Frame(header_content, bg=Theme.COLORS['primary'])
        title_frame.pack(side=tk.LEFT)

        tk.Label(title_frame, text=f"Chiffrage: {self.chantier.get('nom', '')}",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(anchor='w')

        info = f"{self.chantier.get('lieu', '')} - {self.chantier.get('lot', '')}"
        tk.Label(title_frame, text=info,
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        # Total
        self.total_label = tk.Label(header_content, text="Total: 0.00 EUR HT",
                                   font=Theme.FONTS['heading'],
                                   bg=Theme.COLORS['primary'],
                                   fg=Theme.COLORS['secondary'])
        self.total_label.pack(side=tk.RIGHT)

        # Main content - 2 colonnes
        main_frame = tk.Frame(self.window, bg=Theme.COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # PanedWindow pour redimensionner
        self.paned = ttk.PanedWindow(main_frame, orient=tk.HORIZONTAL)
        self.paned.pack(fill=tk.BOTH, expand=True)

        # Colonne gauche - Liste des articles
        left_frame = tk.Frame(self.paned, bg=Theme.COLORS['bg'])
        self.paned.add(left_frame, weight=3)

        # Header articles
        articles_header = tk.Frame(left_frame, bg=Theme.COLORS['bg'])
        articles_header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(articles_header, text="ARTICLES DPGF",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['secondary']).pack(side=tk.LEFT)

        tk.Button(articles_header, text="+ Ajouter article",
                 font=Theme.FONTS['small'],
                 bg=Theme.COLORS['accent'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=12, pady=4, cursor='hand2',
                 command=self._add_article).pack(side=tk.RIGHT)

        tk.Button(articles_header, text="Import catalogue",
                 font=Theme.FONTS['small'],
                 bg=Theme.COLORS['secondary'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=12, pady=4, cursor='hand2',
                 command=self._import_from_catalog).pack(side=tk.RIGHT, padx=(0, 8))

        tk.Button(articles_header, text="Import DPGF",
                 font=Theme.FONTS['small'],
                 bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'],
                 bd=0, padx=12, pady=4, cursor='hand2',
                 command=self._import_dpgf).pack(side=tk.RIGHT, padx=(0, 8))

        # Tableau articles
        table_frame = tk.Frame(left_frame, bg=Theme.COLORS['bg_alt'],
                              highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        table_frame.pack(fill=tk.BOTH, expand=True)

        columns = ('id', 'code', 'designation', 'qte', 'cout_mat', 'cout_mo', 'prix_unit', 'prix_total')
        self.articles_tree = ttk.Treeview(table_frame, columns=columns, show='headings', height=20)

        col_config = {
            'id': ('ID', 40, 'center'),
            'code': ('Code', 70, 'center'),
            'designation': ('Designation', 250, 'w'),
            'qte': ('Qte', 50, 'center'),
            'cout_mat': ('Mat.', 80, 'e'),
            'cout_mo': ('MO', 80, 'e'),
            'prix_unit': ('P.U. HT', 90, 'e'),
            'prix_total': ('Total HT', 100, 'e'),
        }

        for col, (text, width, anchor) in col_config.items():
            self.articles_tree.heading(col, text=text)
            self.articles_tree.column(col, width=width, anchor=anchor, minwidth=30)

        vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self.articles_tree.yview)
        self.articles_tree.configure(yscrollcommand=vsb.set)

        self.articles_tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        vsb.pack(side=tk.RIGHT, fill=tk.Y)

        # Selection
        self.articles_tree.bind('<<TreeviewSelect>>', self._on_article_select)
        self.articles_tree.bind('<Delete>', lambda e: self._delete_article())

        # Colonne droite - Detail article
        right_frame = tk.Frame(self.paned, bg=Theme.COLORS['bg'])
        self.paned.add(right_frame, weight=2)

        # Header detail
        detail_header = tk.Frame(right_frame, bg=Theme.COLORS['bg'])
        detail_header.pack(fill=tk.X, pady=(0, 8))

        tk.Label(detail_header, text="DETAIL ARTICLE",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['secondary']).pack(side=tk.LEFT)

        # Card detail
        self.detail_card = tk.Frame(right_frame, bg=Theme.COLORS['bg_alt'], padx=16, pady=16,
                                   highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        self.detail_card.pack(fill=tk.BOTH, expand=True)

        # Message initial
        self.no_selection_label = tk.Label(self.detail_card,
                                          text="Selectionnez un article pour voir le detail",
                                          font=Theme.FONTS['body'],
                                          bg=Theme.COLORS['bg_alt'],
                                          fg=Theme.COLORS['text_muted'])
        self.no_selection_label.pack(expand=True)

        # Frame de detail (cache au debut)
        self.detail_content = tk.Frame(self.detail_card, bg=Theme.COLORS['bg_alt'])

        self._create_detail_widgets()

        # Barre d'actions
        action_bar = tk.Frame(self.window, bg=Theme.COLORS['bg'], height=56)
        action_bar.pack(fill=tk.X, padx=16, pady=(0, 16))

        tk.Button(action_bar, text="Fermer",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._on_close).pack(side=tk.LEFT)

        tk.Button(action_bar, text="Exporter DPGF",
                 font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._export_dpgf).pack(side=tk.RIGHT)

        tk.Button(action_bar, text="Resultat marche",
                 font=Theme.FONTS['body'],
                 bg=Theme.COLORS['secondary'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=10, cursor='hand2',
                 command=self._set_resultat).pack(side=tk.RIGHT, padx=(0, 8))

    def _create_detail_widgets(self):
        """Cree les widgets du panneau de detail"""
        # Designation
        tk.Label(self.detail_content, text="Designation",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.designation_label = tk.Label(self.detail_content, text="",
                                         font=Theme.FONTS['body_bold'],
                                         bg=Theme.COLORS['bg_alt'],
                                         fg=Theme.COLORS['text'],
                                         wraplength=350, justify='left')
        self.designation_label.pack(anchor='w', pady=(0, 8))

        # Description
        tk.Label(self.detail_content, text="Description",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.description_text = tk.Text(self.detail_content, width=40, height=3,
                                        font=Theme.FONTS['body'],
                                        bg=Theme.COLORS['bg'],
                                        fg=Theme.COLORS['text'],
                                        bd=1, relief='solid', wrap='word')
        self.description_text.pack(anchor='w', fill=tk.X, pady=(0, 12))
        self.description_text.bind('<FocusOut>', lambda e: self._save_description())

        # Infos article
        info_frame = tk.Frame(self.detail_content, bg=Theme.COLORS['bg_alt'])
        info_frame.pack(fill=tk.X, pady=(0, 12))

        self.info_labels = {}
        for i, (key, label) in enumerate([('code', 'Code'), ('unite', 'Unite'), ('quantite', 'Quantite')]):
            frame = tk.Frame(info_frame, bg=Theme.COLORS['bg_alt'])
            frame.pack(side=tk.LEFT, padx=(0, 16))
            tk.Label(frame, text=label, font=Theme.FONTS['tiny'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text_muted']).pack(anchor='w')
            self.info_labels[key] = tk.Label(frame, text="-",
                                            font=Theme.FONTS['body'],
                                            bg=Theme.COLORS['bg_alt'],
                                            fg=Theme.COLORS['text'])
            self.info_labels[key].pack(anchor='w')

        ttk.Separator(self.detail_content, orient='horizontal').pack(fill=tk.X, pady=12)

        # Section produits lies
        produits_header = tk.Frame(self.detail_content, bg=Theme.COLORS['bg_alt'])
        produits_header.pack(fill=tk.X)

        tk.Label(produits_header, text="PRODUITS LIES",
                font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(side=tk.LEFT)

        tk.Button(produits_header, text="+ Ajouter",
                 font=Theme.FONTS['tiny'],
                 bg=Theme.COLORS['accent'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=8, pady=2, cursor='hand2',
                 command=self._add_produit).pack(side=tk.RIGHT)

        # Liste produits
        produits_frame = tk.Frame(self.detail_content, bg=Theme.COLORS['bg'],
                                 highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        produits_frame.pack(fill=tk.X, pady=(8, 12))

        columns = ('id', 'designation', 'qte', 'prix')
        self.produits_tree = ttk.Treeview(produits_frame, columns=columns, show='headings', height=4)

        self.produits_tree.heading('id', text='ID')
        self.produits_tree.heading('designation', text='Produit')
        self.produits_tree.heading('qte', text='Qte')
        self.produits_tree.heading('prix', text='Prix')

        self.produits_tree.column('id', width=40, anchor='center')
        self.produits_tree.column('designation', width=180, anchor='w')
        self.produits_tree.column('qte', width=50, anchor='center')
        self.produits_tree.column('prix', width=70, anchor='e')

        self.produits_tree.pack(fill=tk.X)

        # Menu contextuel pour les produits lies
        self.produit_context_menu = tk.Menu(self.produits_tree, tearoff=0)
        self.produit_context_menu.add_command(label="Copier les informations",
                                              command=self._copy_produit_info)
        self.produit_context_menu.add_command(label="Copier la description",
                                              command=self._copy_produit_description)
        self.produit_context_menu.add_separator()
        self.produit_context_menu.add_command(label="Ouvrir la fiche technique",
                                              command=self._open_fiche_technique)
        self.produit_context_menu.add_command(label="Ouvrir le devis fournisseur",
                                              command=self._open_devis_fournisseur)
        self.produit_context_menu.add_separator()
        self.produit_context_menu.add_command(label="Retirer du chiffrage",
                                              command=self._remove_produit)

        # Lier le clic droit au menu contextuel
        self.produits_tree.bind('<Button-3>', self._show_produit_context_menu)

        # Bouton supprimer produit
        tk.Button(self.detail_content, text="Retirer le produit selectionne",
                 font=Theme.FONTS['tiny'],
                 bg=Theme.COLORS['danger'],
                 fg=Theme.COLORS['white'],
                 bd=0, padx=8, pady=2, cursor='hand2',
                 command=self._remove_produit).pack(anchor='e', pady=(0, 8))

        ttk.Separator(self.detail_content, orient='horizontal').pack(fill=tk.X, pady=8)

        # Section Main d'oeuvre
        tk.Label(self.detail_content, text="MAIN D'OEUVRE (heures)",
                font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 8))

        mo_frame = tk.Frame(self.detail_content, bg=Theme.COLORS['bg_alt'])
        mo_frame.pack(fill=tk.X)

        self.mo_entries = {}
        taux = self.db.get_taux_horaires()

        for i, (key, label) in enumerate([
            ('conception', 'Conception'),
            ('fabrication', 'Fabrication'),
            ('pose', 'Pose')
        ]):
            frame = tk.Frame(mo_frame, bg=Theme.COLORS['bg_alt'])
            frame.grid(row=0, column=i, padx=(0, 12))

            # Afficher le type de MO
            taux_info = taux[key]
            tk.Label(frame, text=f"{label}",
                    font=Theme.FONTS['tiny'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text']).pack(anchor='w')

            # Afficher prix de vente
            tk.Label(frame, text=f"{taux_info['vente']:.0f} EUR/h",
                    font=Theme.FONTS['tiny'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text_muted']).pack(anchor='w')

            # Calculer et afficher la marge
            cout = taux_info['cout']
            vente = taux_info['vente']
            marge_mo = ((vente - cout) / cout * 100) if cout > 0 else 0
            marge_color = Theme.COLORS['success'] if marge_mo > 0 else Theme.COLORS['danger']
            tk.Label(frame, text=f"Marge: {marge_mo:.1f}%",
                    font=Theme.FONTS['tiny'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=marge_color).pack(anchor='w')

            entry = tk.Entry(frame, width=8, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                           bd=1, relief='solid', justify='center')
            entry.insert(0, "0")
            entry.pack(pady=(2, 0))
            entry.bind('<FocusOut>', lambda e: self._update_mo())
            entry.bind('<Return>', lambda e: self._update_mo())
            self.mo_entries[key] = entry

        tk.Label(mo_frame, text="h", font=Theme.FONTS['tiny'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).grid(row=0, column=3, padx=(0, 8))

        ttk.Separator(self.detail_content, orient='horizontal').pack(fill=tk.X, pady=12)

        # Section TVA
        tva_frame = tk.Frame(self.detail_content, bg=Theme.COLORS['bg_alt'])
        tva_frame.pack(fill=tk.X, pady=(8, 12))

        tk.Label(tva_frame, text="TVA",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.tva_var = tk.StringVar(value="20%")
        self.tva_options = [0, 5.5, 10, 20]
        self.tva_combo = ttk.Combobox(tva_frame, textvariable=self.tva_var,
                                      values=["0%", "5.5%", "10%", "20%"],
                                      state='readonly', width=8,
                                      font=Theme.FONTS['body'])
        self.tva_combo.pack(side=tk.LEFT, padx=(8, 0))
        self.tva_combo.bind('<<ComboboxSelected>>', lambda e: self._save_tva())

        # Resume couts
        ttk.Separator(self.detail_content, orient='horizontal').pack(fill=tk.X, pady=8)

        tk.Label(self.detail_content, text="RESUME DES COUTS",
                font=Theme.FONTS['small_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 8))

        self.couts_labels = {}
        couts_frame = tk.Frame(self.detail_content, bg=Theme.COLORS['bg_alt'])
        couts_frame.pack(fill=tk.X)

        for key, label in [('materiaux', 'Materiaux'), ('mo', 'Main d\'oeuvre'),
                          ('revient', 'Cout revient'), ('prix_unit', 'Prix unitaire HT'),
                          ('prix_total', 'Prix total HT')]:
            row = tk.Frame(couts_frame, bg=Theme.COLORS['bg_alt'])
            row.pack(fill=tk.X, pady=2)
            tk.Label(row, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text']).pack(side=tk.LEFT)
            self.couts_labels[key] = tk.Label(row, text="0.00 EUR",
                                             font=Theme.FONTS['body_bold'] if key == 'prix_total' else Theme.FONTS['body'],
                                             bg=Theme.COLORS['bg_alt'],
                                             fg=Theme.COLORS['accent'] if key == 'prix_total' else Theme.COLORS['text'])
            self.couts_labels[key].pack(side=tk.RIGHT)

    def _load_articles(self):
        """Charge les articles du chantier"""
        articles = self.db.get_articles_dpgf(self.chantier_id)

        for item in self.articles_tree.get_children():
            self.articles_tree.delete(item)

        total = 0
        for a in articles:
            self.articles_tree.insert('', tk.END, values=(
                a['id'],
                a['code'] or '-',
                a['designation'],
                a['quantite'],
                f"{a['cout_materiaux']:.2f}",
                f"{a['cout_mo_total']:.2f}",
                f"{a['prix_unitaire_ht']:.2f}",
                f"{a['prix_total_ht']:.2f}",
            ))
            total += a['prix_total_ht']

        self.total_label.config(text=f"Total: {total:.2f} EUR HT")

    def _on_article_select(self, event=None):
        """Selection d'un article"""
        selection = self.articles_tree.selection()
        if not selection:
            return

        item = self.articles_tree.item(selection[0])
        article_id = item['values'][0]
        self.current_article_id = article_id

        # Afficher le detail
        self.no_selection_label.pack_forget()
        self.detail_content.pack(fill=tk.BOTH, expand=True)

        # Charger les donnees
        article = self.db.get_article_dpgf(article_id)
        if not article:
            return

        self.designation_label.config(text=article['designation'])
        self.info_labels['code'].config(text=article['code'] or '-')
        self.info_labels['unite'].config(text=article['unite'] or 'U')
        self.info_labels['quantite'].config(text=str(article['quantite']))

        # Description
        self.description_text.delete('1.0', tk.END)
        self.description_text.insert('1.0', article.get('description', '') or '')

        # Temps MO
        self.mo_entries['conception'].delete(0, tk.END)
        self.mo_entries['conception'].insert(0, str(article['temps_conception']))
        self.mo_entries['fabrication'].delete(0, tk.END)
        self.mo_entries['fabrication'].insert(0, str(article['temps_fabrication']))
        self.mo_entries['pose'].delete(0, tk.END)
        self.mo_entries['pose'].insert(0, str(article['temps_pose']))

        # TVA
        taux_tva = article.get('taux_tva', 20) or 20
        self.tva_var.set(f"{taux_tva}%")

        # Produits lies
        self._load_produits_lies()

        # Couts
        self._update_couts_display()

    def _load_produits_lies(self):
        """Charge les produits lies a l'article"""
        if not self.current_article_id:
            return

        produits = self.db.get_produits_article(self.current_article_id)

        for item in self.produits_tree.get_children():
            self.produits_tree.delete(item)

        for p in produits:
            self.produits_tree.insert('', tk.END, values=(
                p['id'],  # ID de la liaison
                p['produit_designation'][:30],
                p['quantite'],
                f"{p['prix_unitaire']:.2f}",
            ))

    def _update_couts_display(self):
        """Met a jour l'affichage des couts"""
        if not self.current_article_id:
            return

        article = self.db.get_article_dpgf(self.current_article_id)
        if not article:
            return

        self.couts_labels['materiaux'].config(text=f"{article['cout_materiaux']:.2f} EUR")
        self.couts_labels['mo'].config(text=f"{article['cout_mo_total']:.2f} EUR")
        self.couts_labels['revient'].config(text=f"{article['cout_revient']:.2f} EUR")
        self.couts_labels['prix_unit'].config(text=f"{article['prix_unitaire_ht']:.2f} EUR")
        self.couts_labels['prix_total'].config(text=f"{article['prix_total_ht']:.2f} EUR")

    def _add_article(self):
        """Ajoute un nouvel article"""
        dialog = ArticleDialog(self.window, self.db, self.chantier_id)
        if dialog.result:
            self._load_articles()

    def _import_from_catalog(self):
        """Importe un article depuis le catalogue produits"""
        dialog = ProductSearchDialog(self.window, self.db)
        if dialog.result and dialog.selected_product:
            produit = dialog.selected_product
            # Creer l'article DPGF avec les donnees du produit
            article_data = {
                'code': produit.get('article', ''),
                'designation': produit.get('designation', ''),
                'description': produit.get('designation', ''),
                'quantite': 1,
                'marge_pct': 20.0,
                'taux_tva': 20.0
            }
            article_id = self.db.add_article_dpgf(self.chantier_id, article_data)
            # Lier le produit a l'article
            self.db.add_produit_article(article_id, produit['id'], quantite=1)
            self._load_articles()

    def _import_dpgf(self):
        """Importe un fichier DPGF CSV dans le chantier courant"""
        filepath = filedialog.askopenfilename(
            parent=self.window,
            title="Importer un fichier DPGF",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if filepath:
            try:
                count = self.db.import_dpgf_csv(self.chantier_id, filepath)
                self._load_articles()
                messagebox.showinfo("Import", f"{count} article(s) importe(s) avec succes")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur lors de l'import : {str(e)}")

    def _delete_article(self):
        """Supprime l'article selectionne"""
        selection = self.articles_tree.selection()
        if not selection:
            return

        if messagebox.askyesno("Confirmer", "Supprimer cet article ?"):
            item = self.articles_tree.item(selection[0])
            article_id = item['values'][0]
            self.db.delete_article_dpgf(article_id)
            self.current_article_id = None
            self._load_articles()

            # Masquer le detail
            self.detail_content.pack_forget()
            self.no_selection_label.pack(expand=True)

    def _add_produit(self):
        """Ajoute un produit a l'article"""
        if not self.current_article_id:
            return

        dialog = ProductSearchDialog(self.window, self.db)
        if dialog.result and dialog.selected_product:
            self.db.add_produit_article(
                self.current_article_id,
                dialog.selected_product['id'],
                dialog.selected_quantity
            )
            self._load_produits_lies()
            self._update_couts_display()
            self._load_articles()

    def _remove_produit(self):
        """Retire un produit de l'article"""
        selection = self.produits_tree.selection()
        if not selection:
            return

        item = self.produits_tree.item(selection[0])
        liaison_id = item['values'][0]

        self.db.remove_produit_article(liaison_id)
        self._load_produits_lies()
        self._update_couts_display()
        self._load_articles()

    def _update_mo(self):
        """Met a jour les temps de main d'oeuvre"""
        if not self.current_article_id:
            return

        try:
            temps_conception = float(self.mo_entries['conception'].get().replace(',', '.') or 0)
            temps_fabrication = float(self.mo_entries['fabrication'].get().replace(',', '.') or 0)
            temps_pose = float(self.mo_entries['pose'].get().replace(',', '.') or 0)
        except ValueError:
            return

        article = self.db.get_article_dpgf(self.current_article_id)
        if not article:
            return

        data = {
            'code': article['code'],
            'designation': article['designation'],
            'description': article.get('description', ''),
            'categorie': article['categorie'],
            'largeur_mm': article['largeur_mm'],
            'hauteur_mm': article['hauteur_mm'],
            'caracteristiques': article['caracteristiques'],
            'unite': article['unite'],
            'quantite': article['quantite'],
            'localisation': article['localisation'],
            'notes': article['notes'],
            'temps_conception': temps_conception,
            'temps_fabrication': temps_fabrication,
            'temps_pose': temps_pose,
            'marge_pct': article['marge_pct'],
            'taux_tva': article.get('taux_tva', 20),
        }

        self.db.update_article_dpgf(self.current_article_id, data)
        self._update_couts_display()
        self._load_articles()

    def _save_description(self):
        """Sauvegarde la description de l'article"""
        if not self.current_article_id:
            return

        description = self.description_text.get('1.0', tk.END).strip()

        article = self.db.get_article_dpgf(self.current_article_id)
        if not article:
            return

        data = {
            'code': article['code'],
            'designation': article['designation'],
            'description': description,
            'categorie': article['categorie'],
            'largeur_mm': article['largeur_mm'],
            'hauteur_mm': article['hauteur_mm'],
            'caracteristiques': article['caracteristiques'],
            'unite': article['unite'],
            'quantite': article['quantite'],
            'localisation': article['localisation'],
            'notes': article['notes'],
            'temps_conception': article['temps_conception'],
            'temps_fabrication': article['temps_fabrication'],
            'temps_pose': article['temps_pose'],
            'marge_pct': article['marge_pct'],
            'taux_tva': article.get('taux_tva', 20),
        }

        self.db.update_article_dpgf(self.current_article_id, data)

    def _save_tva(self):
        """Sauvegarde le taux de TVA de l'article"""
        if not self.current_article_id:
            return

        # Extraire le taux du texte (ex: "20%" -> 20)
        tva_text = self.tva_var.get().replace('%', '')
        try:
            taux_tva = float(tva_text)
        except ValueError:
            taux_tva = 20

        article = self.db.get_article_dpgf(self.current_article_id)
        if not article:
            return

        data = {
            'code': article['code'],
            'designation': article['designation'],
            'description': article.get('description', ''),
            'categorie': article['categorie'],
            'largeur_mm': article['largeur_mm'],
            'hauteur_mm': article['hauteur_mm'],
            'caracteristiques': article['caracteristiques'],
            'unite': article['unite'],
            'quantite': article['quantite'],
            'localisation': article['localisation'],
            'notes': article['notes'],
            'temps_conception': article['temps_conception'],
            'temps_fabrication': article['temps_fabrication'],
            'temps_pose': article['temps_pose'],
            'marge_pct': article['marge_pct'],
            'taux_tva': taux_tva,
        }

        self.db.update_article_dpgf(self.current_article_id, data)

    def _export_dpgf(self):
        """Exporte le DPGF"""
        from ui.dpgf_export_dialog import DPGFExportDialog
        DPGFExportDialog(self.window, self.db, self.chantier_id)

    def _set_resultat(self):
        """Definit le resultat du marche"""
        from ui.resultat_marche_dialog import ResultatMarcheDialog
        dialog = ResultatMarcheDialog(self.window, self.db, self.chantier_id)
        if dialog.result:
            self.chantier = self.db.get_chantier(self.chantier_id)

    def _on_close(self):
        """Ferme la vue"""
        if self.on_close_callback:
            self.on_close_callback()
        self.window.destroy()

    # ==================== MENU CONTEXTUEL PRODUITS ====================

    def _show_produit_context_menu(self, event):
        """Affiche le menu contextuel pour un produit"""
        # Selectionner l'item sous le curseur
        item = self.produits_tree.identify_row(event.y)
        if item:
            self.produits_tree.selection_set(item)

            # Recuperer les infos du produit
            liaison_id = self.produits_tree.item(item)['values'][0]
            produits = self.db.get_produits_article(self.current_article_id)
            produit_info = next((p for p in produits if p['id'] == liaison_id), None)

            if produit_info:
                # Recuperer le produit complet du catalogue
                produit = self.db.get_produit(produit_info['produit_id'])

                # Activer/desactiver les options selon disponibilite
                has_fiche = produit and produit.get('fiche_technique')
                has_devis = produit and produit.get('devis_fournisseur')

                # Mettre a jour l'etat des commandes (indices: 0=copier info, 1=copier desc, 2=sep, 3=fiche, 4=devis)
                self.produit_context_menu.entryconfig(3, state='normal' if has_fiche else 'disabled')
                self.produit_context_menu.entryconfig(4, state='normal' if has_devis else 'disabled')

            # Afficher le menu
            self.produit_context_menu.tk_popup(event.x_root, event.y_root)

    def _get_selected_produit_info(self):
        """Recupere les informations du produit selectionne"""
        selection = self.produits_tree.selection()
        if not selection:
            return None, None

        liaison_id = self.produits_tree.item(selection[0])['values'][0]
        produits = self.db.get_produits_article(self.current_article_id)
        liaison_info = next((p for p in produits if p['id'] == liaison_id), None)

        if not liaison_info:
            return None, None

        produit = self.db.get_produit(liaison_info['produit_id'])
        return liaison_info, produit

    def _copy_produit_info(self):
        """Copie les informations du produit dans le presse-papier"""
        liaison_info, produit = self._get_selected_produit_info()
        if not produit:
            messagebox.showwarning("Attention", "Aucun produit selectionne")
            return

        # Construire le texte a copier
        info_lines = [
            f"Designation: {produit.get('designation', '-')}",
            f"Reference: {produit.get('reference', '-')}",
            f"Categorie: {produit.get('categorie', '-')}",
            f"Fournisseur: {produit.get('fournisseur', '-')}",
            f"Prix achat: {produit.get('prix_achat', 0):.2f} EUR",
        ]
        if liaison_info:
            info_lines.append(f"Quantite: {liaison_info['quantite']}")
            info_lines.append(f"Sous-total: {liaison_info['quantite'] * liaison_info['prix_unitaire']:.2f} EUR")

        info_text = "\n".join(info_lines)

        # Copier dans le presse-papier
        self.window.clipboard_clear()
        self.window.clipboard_append(info_text)
        self.window.update()

        messagebox.showinfo("Copie", "Informations copiees dans le presse-papier")

    def _copy_produit_description(self):
        """Copie la description du produit dans le presse-papier"""
        liaison_info, produit = self._get_selected_produit_info()
        if not produit:
            messagebox.showwarning("Attention", "Aucun produit selectionne")
            return

        # Recuperer la description du produit
        description = produit.get('description', '') or produit.get('designation', '')

        if not description:
            messagebox.showwarning("Attention", "Ce produit n'a pas de description")
            return

        # Copier dans le presse-papier
        self.window.clipboard_clear()
        self.window.clipboard_append(description)
        self.window.update()

        messagebox.showinfo("Copie", "Description copiee dans le presse-papier")

    def _open_fiche_technique(self):
        """Ouvre la fiche technique du produit"""
        _, produit = self._get_selected_produit_info()
        if not produit:
            return

        fiche_path = produit.get('fiche_technique')
        if not fiche_path:
            messagebox.showwarning("Attention", "Aucune fiche technique associee a ce produit")
            return

        # Le chemin est deja resolu par get_produit
        if not os.path.exists(fiche_path):
            messagebox.showerror("Erreur", f"Fichier introuvable:\n{fiche_path}")
            return

        self._open_file(fiche_path)

    def _open_devis_fournisseur(self):
        """Ouvre le devis fournisseur du produit"""
        _, produit = self._get_selected_produit_info()
        if not produit:
            return

        devis_path = produit.get('devis_fournisseur')
        if not devis_path:
            messagebox.showwarning("Attention", "Aucun devis fournisseur associe a ce produit")
            return

        # Le chemin est deja resolu par get_produit
        if not os.path.exists(devis_path):
            messagebox.showerror("Erreur", f"Fichier introuvable:\n{devis_path}")
            return

        self._open_file(devis_path)

    def _open_file(self, filepath):
        """Ouvre un fichier avec l'application par defaut"""
        try:
            if platform.system() == 'Windows':
                os.startfile(filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.run(['open', filepath])
            else:  # Linux
                subprocess.run(['xdg-open', filepath])
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")


class ArticleDialog:
    """Dialogue d'ajout/modification d'article DPGF"""

    def __init__(self, parent, db, chantier_id, article_id=None):
        self.db = db
        self.chantier_id = chantier_id
        self.article_id = article_id
        self.result = False

        # Charger les donnees si modification
        self.data = {}
        if article_id:
            self.data = self.db.get_article_dpgf(article_id) or {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Modifier l'article" if article_id else "Nouvel article")
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
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        title = "Modifier l'article" if self.article_id else "Nouvel article DPGF"
        tk.Label(header, text=title,
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Card
        form_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        form_card.pack(fill=tk.BOTH, expand=True)

        self.entries = {}

        fields = [
            ('code', 'Code'),
            ('designation', 'Designation *'),
            ('categorie', 'Categorie'),
            ('unite', 'Unite'),
            ('quantite', 'Quantite'),
            ('localisation', 'Localisation'),
        ]

        for i, (field, label) in enumerate(fields):
            tk.Label(form_card, text=label, font=Theme.FONTS['body'],
                    bg=Theme.COLORS['bg_alt'],
                    fg=Theme.COLORS['text']).grid(row=i, column=0, sticky='e', padx=(5, 10), pady=8)

            entry = tk.Entry(form_card, width=36, font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                           bd=1, relief='solid')

            default = self.data.get(field, '')
            if field == 'quantite':
                default = self.data.get('quantite', 1)
            elif field == 'unite':
                default = self.data.get('unite', 'U')

            entry.insert(0, str(default) if default else '')
            entry.grid(row=i, column=1, sticky='w', padx=5, pady=8)
            self.entries[field] = entry

        # Description
        row = len(fields)
        tk.Label(form_card, text="Description", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='ne', padx=(5, 10), pady=8)

        self.description_text = tk.Text(form_card, width=36, height=3, font=Theme.FONTS['body'],
                                       bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                       bd=1, relief='solid', wrap='word')
        self.description_text.insert('1.0', self.data.get('description', '') or '')
        self.description_text.grid(row=row, column=1, sticky='w', padx=5, pady=8)

        # Notes
        row += 1
        tk.Label(form_card, text="Notes", font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).grid(row=row, column=0, sticky='ne', padx=(5, 10), pady=8)

        self.notes_text = tk.Text(form_card, width=36, height=3, font=Theme.FONTS['body'],
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
        """Enregistre l'article"""
        designation = self.entries['designation'].get().strip()
        if not designation:
            messagebox.showerror("Erreur", "La designation est obligatoire")
            return

        try:
            quantite = float(self.entries['quantite'].get().replace(',', '.') or 1)
        except:
            quantite = 1

        data = {
            'code': self.entries['code'].get().strip(),
            'designation': designation,
            'description': self.description_text.get('1.0', tk.END).strip(),
            'categorie': self.entries['categorie'].get().strip(),
            'unite': self.entries['unite'].get().strip() or 'U',
            'quantite': quantite,
            'localisation': self.entries['localisation'].get().strip(),
            'notes': self.notes_text.get('1.0', tk.END).strip(),
        }

        try:
            if self.article_id:
                # Conserver les temps MO et autres donnees existantes
                article = self.db.get_article_dpgf(self.article_id)
                data['temps_conception'] = article['temps_conception']
                data['temps_fabrication'] = article['temps_fabrication']
                data['temps_pose'] = article['temps_pose']
                data['marge_pct'] = article['marge_pct']
                data['taux_tva'] = article.get('taux_tva', 20)
                self.db.update_article_dpgf(self.article_id, data)
            else:
                self.db.add_article_dpgf(self.chantier_id, data)

            self.result = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")
