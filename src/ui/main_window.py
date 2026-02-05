"""
DestriChiffrage - Fenetre principale
=====================================
Interface principale moderne et professionnelle
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys
import subprocess
from datetime import datetime

# Pour le logo
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import Database
from ui.theme import Theme
from ui.dialogs import ProductDialog, SettingsDialog, AboutDialog, CategoryDialog


class MainWindow:
    """Fenetre principale de l'application"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.db = Database()

        # Variables
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Toutes")
        self.subcategory_var = tk.StringVar(value="Toutes")
        self.hauteur_var = tk.StringVar(value="Toutes")
        self.largeur_var = tk.StringVar(value="Toutes")
        self.marge_var = tk.StringVar(value=str(self.db.get_marge()))

        # Charger les icones PDF et Devis
        self.pdf_icon = None
        self.devis_icon = None
        self.pdf_labels = []  # Labels pour afficher les icônes PDF
        self.devis_labels = []  # Labels pour afficher les icônes Devis
        self._load_pdf_icon()
        self._load_devis_icon()

        # Construction de l'interface
        self._create_menu()
        self._create_header()
        self._create_toolbar()
        self._create_main_content()
        self._create_status_bar()

        # Charger les donnees
        self.refresh_data()

        # Bindings
        self.search_var.trace('w', lambda *args: self.on_search())

    def _load_pdf_icon(self):
        """Charge l'icone PDF"""
        if HAS_PIL:
            try:
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'pdf.png')
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    # Redimensionner l'icone pour qu'elle tienne dans la cellule
                    img = img.resize((24, 24), Image.Resampling.LANCZOS)
                    self.pdf_icon = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erreur chargement icone PDF: {e}")

    def _load_devis_icon(self):
        """Charge l'icone Devis (identique au PDF)"""
        if HAS_PIL:
            try:
                icon_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'pdf.png')
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    # Redimensionner l'icone pour qu'elle tienne dans la cellule
                    img = img.resize((24, 24), Image.Resampling.LANCZOS)
                    self.devis_icon = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erreur chargement icone Devis: {e}")

    def _create_menu(self):
        """Cree la barre de menu"""
        menubar = tk.Menu(self.root, bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                         activebackground=Theme.COLORS['accent'], activeforeground=Theme.COLORS['white'])
        self.root.config(menu=menubar)

        # Menu Fichier
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Fichier", menu=file_menu)
        file_menu.add_command(label="Importer CSV...", command=self.on_import, accelerator="Ctrl+I")
        file_menu.add_command(label="Exporter CSV...", command=self.on_export, accelerator="Ctrl+E")
        file_menu.add_separator()
        file_menu.add_command(label="Telecharger modele d'import...", command=self.on_download_template)
        file_menu.add_separator()
        file_menu.add_command(label="Quitter", command=self.on_closing, accelerator="Alt+F4")

        # Menu Edition
        edit_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Edition", menu=edit_menu)
        edit_menu.add_command(label="Nouveau produit", command=self.on_add, accelerator="Ctrl+N")
        edit_menu.add_command(label="Modifier", command=self.on_edit, accelerator="Ctrl+M")
        edit_menu.add_command(label="Supprimer", command=self.on_delete, accelerator="Suppr")
        edit_menu.add_separator()
        edit_menu.add_command(label="Gerer les categories...", command=self.on_manage_categories, accelerator="Ctrl+G")
        edit_menu.add_separator()
        edit_menu.add_command(label="Vider la base de donnees...", command=self.on_clear_database)
        edit_menu.add_separator()
        edit_menu.add_command(label="Parametres...", command=self.on_settings)

        # Menu Affichage
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        view_menu.add_command(label="Actualiser", command=self.refresh_data, accelerator="F5")
        view_menu.add_command(label="Statistiques", command=self.show_stats)

        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="A propos", command=self.on_about)

        # Raccourcis clavier
        self.root.bind('<Control-i>', lambda e: self.on_import())
        self.root.bind('<Control-e>', lambda e: self.on_export())
        self.root.bind('<Control-n>', lambda e: self.on_add())
        self.root.bind('<Control-m>', lambda e: self.on_edit())
        self.root.bind('<Control-g>', lambda e: self.on_manage_categories())
        self.root.bind('<Delete>', lambda e: self.on_delete())
        self.root.bind('<F5>', lambda e: self.refresh_data())

    def _create_header(self):
        """Cree l'en-tete moderne et elegant"""
        # Header avec fond sombre
        header = tk.Frame(self.root, bg=Theme.COLORS['primary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Conteneur principal du header
        header_content = tk.Frame(header, bg=Theme.COLORS['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        # Gauche: Logo + Titre
        left_frame = tk.Frame(header_content, bg=Theme.COLORS['primary'])
        left_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Logo image
        self.logo_image = None
        if HAS_PIL:
            try:
                logo_path = os.path.join(os.path.dirname(__file__), '..', 'assets', 'logo.png')
                if os.path.exists(logo_path):
                    img = Image.open(logo_path)
                    img = img.resize((44, 44), Image.Resampling.LANCZOS)
                    self.logo_image = ImageTk.PhotoImage(img)

                    logo_label = tk.Label(left_frame, image=self.logo_image,
                                         bg=Theme.COLORS['primary'])
                    logo_label.pack(side=tk.LEFT)
            except Exception:
                pass

        # Fallback si pas d'image
        if not self.logo_image:
            logo_frame = tk.Frame(left_frame, bg=Theme.COLORS['secondary'], width=44, height=44)
            logo_frame.pack(side=tk.LEFT)
            logo_frame.pack_propagate(False)
            tk.Label(logo_frame, text="DC", font=('Segoe UI', 14, 'bold'),
                    bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white']).place(relx=0.5, rely=0.5, anchor='center')

        # Titre et sous-titre
        title_frame = tk.Frame(left_frame, bg=Theme.COLORS['primary'])
        title_frame.pack(side=tk.LEFT, padx=(16, 0))

        tk.Label(title_frame, text="DestriChiffrage",
                font=('Segoe UI', 18, 'bold'), bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(anchor='w')

        tk.Label(title_frame, text="Catalogue et chiffrage de portes",
                font=('Segoe UI', 9), bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        # Droite: Controle de marge
        right_frame = tk.Frame(header_content, bg=Theme.COLORS['primary'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Label Marge
        tk.Label(right_frame, text="Marge",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['text_muted']).pack(anchor='e')

        # Conteneur marge
        marge_frame = tk.Frame(right_frame, bg=Theme.COLORS['primary'])
        marge_frame.pack(anchor='e')

        marge_entry = tk.Entry(marge_frame, textvariable=self.marge_var,
                              width=6, font=('Consolas', 14, 'bold'),
                              justify='center', bd=0,
                              bg=Theme.COLORS['primary_light'],
                              fg=Theme.COLORS['white'],
                              insertbackground=Theme.COLORS['white'])
        marge_entry.pack(side=tk.LEFT)

        tk.Label(marge_frame, text=" %", font=('Segoe UI', 14, 'bold'),
                bg=Theme.COLORS['primary'], fg=Theme.COLORS['white']).pack(side=tk.LEFT)

        # Bouton appliquer discret
        apply_btn = tk.Button(right_frame, text="Appliquer",
                             font=Theme.FONTS['tiny'],
                             bg=Theme.COLORS['primary_light'],
                             fg=Theme.COLORS['text_muted'],
                             activebackground=Theme.COLORS['primary'],
                             activeforeground=Theme.COLORS['white'],
                             bd=0, padx=10, pady=2, cursor='hand2',
                             command=self.on_apply_marge)
        apply_btn.pack(anchor='e', pady=(4, 0))

    def _create_toolbar(self):
        """Cree la barre d'outils avec recherche et filtres"""
        # Container principal
        toolbar = tk.Frame(self.root, bg=Theme.COLORS['bg_alt'])
        toolbar.pack(fill=tk.X, padx=16, pady=(16, 0))

        # Padding interne
        toolbar_inner = tk.Frame(toolbar, bg=Theme.COLORS['bg_alt'], padx=20, pady=16)
        toolbar_inner.pack(fill=tk.X)

        # Ligne 1: Recherche
        search_row = tk.Frame(toolbar_inner, bg=Theme.COLORS['bg_alt'])
        search_row.pack(fill=tk.X, pady=(0, 12))

        # Icone recherche + Entry
        search_container = tk.Frame(search_row, bg=Theme.COLORS['bg_dark'], padx=2, pady=2)
        search_container.pack(side=tk.LEFT, fill=tk.X, expand=True)

        search_inner = tk.Frame(search_container, bg=Theme.COLORS['bg_alt'])
        search_inner.pack(fill=tk.X)

        tk.Label(search_inner, text=" \u2315 ", font=('Segoe UI', 12),
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text_muted']).pack(side=tk.LEFT)

        search_entry = tk.Entry(search_inner, textvariable=self.search_var,
                               font=Theme.FONTS['body'],
                               bd=0, bg=Theme.COLORS['bg_alt'],
                               fg=Theme.COLORS['text'])
        search_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10), pady=8)
        search_entry.focus()

        # Compteur
        self.count_label = tk.Label(search_row, text="0 produits",
                                   font=Theme.FONTS['small_bold'],
                                   bg=Theme.COLORS['bg_alt'],
                                   fg=Theme.COLORS['text_muted'],
                                   padx=16)
        self.count_label.pack(side=tk.RIGHT)

        # Separateur
        ttk.Separator(toolbar_inner, orient='horizontal').pack(fill=tk.X, pady=8)

        # Ligne 2: Filtres
        filter_row = tk.Frame(toolbar_inner, bg=Theme.COLORS['bg_alt'])
        filter_row.pack(fill=tk.X)

        # Filtre categorie
        cat_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        cat_frame.pack(side=tk.LEFT, padx=(0, 24))

        tk.Label(cat_frame, text="Categorie",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.category_combo = ttk.Combobox(cat_frame, textvariable=self.category_var,
                                          width=20, state='readonly',
                                          font=Theme.FONTS['body'])
        self.category_combo.pack(pady=(2, 0))
        self.category_combo.bind('<<ComboboxSelected>>', self.on_category_change)

        # Filtre sous-categorie
        subcat_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        subcat_frame.pack(side=tk.LEFT, padx=(0, 24))

        tk.Label(subcat_frame, text="Sous-categorie",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.subcategory_combo = ttk.Combobox(subcat_frame, textvariable=self.subcategory_var,
                                             width=28, state='readonly',
                                             font=Theme.FONTS['body'])
        self.subcategory_combo.pack(pady=(2, 0))
        self.subcategory_combo.bind('<<ComboboxSelected>>', lambda e: self.on_search())

        # Filtre hauteur
        hauteur_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        hauteur_frame.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(hauteur_frame, text="Hauteur",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.hauteur_combo = ttk.Combobox(hauteur_frame, textvariable=self.hauteur_var,
                                         width=10, state='readonly',
                                         font=Theme.FONTS['body'])
        self.hauteur_combo.pack(pady=(2, 0))
        self.hauteur_combo.bind('<<ComboboxSelected>>', self.on_hauteur_change)

        # Filtre largeur
        largeur_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        largeur_frame.pack(side=tk.LEFT, padx=(0, 24))

        tk.Label(largeur_frame, text="Largeur",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.largeur_combo = ttk.Combobox(largeur_frame, textvariable=self.largeur_var,
                                         width=10, state='readonly',
                                         font=Theme.FONTS['body'])
        self.largeur_combo.pack(pady=(2, 0))
        self.largeur_combo.bind('<<ComboboxSelected>>', lambda e: self.on_search())

        # Bouton effacer
        clear_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        clear_frame.pack(side=tk.LEFT, pady=(12, 0))

        clear_btn = tk.Button(clear_frame, text="Effacer les filtres",
                             font=Theme.FONTS['small'],
                             bg=Theme.COLORS['bg_alt'],
                             fg=Theme.COLORS['text_light'],
                             activebackground=Theme.COLORS['bg_dark'],
                             bd=0, padx=12, pady=4, cursor='hand2',
                             command=self.clear_search)
        clear_btn.pack()

    def _create_main_content(self):
        """Cree le contenu principal avec tableau et actions"""
        # Container principal
        main_container = tk.Frame(self.root, bg=Theme.COLORS['bg'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=16, pady=16)

        # Card pour le tableau
        table_card = tk.Frame(main_container, bg=Theme.COLORS['bg_alt'])
        table_card.pack(fill=tk.BOTH, expand=True)

        # Frame pour le tableau
        table_frame = tk.Frame(table_card, bg=Theme.COLORS['bg_alt'])
        table_frame.pack(fill=tk.BOTH, expand=True, padx=1, pady=1)

        # Colonnes du tableau
        columns = ('id', 'categorie', 'sous_categorie', 'designation',
                  'hauteur', 'largeur', 'prix_achat', 'prix_vente', 'reference', 'pdf', 'devis')

        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                selectmode='browse')

        # Configuration des colonnes
        col_config = {
            'id': ('ID', 60, 'center'),
            'categorie': ('Categorie', 110, 'w'),
            'sous_categorie': ('Sous-cat.', 130, 'w'),
            'designation': ('Designation', 280, 'w'),
            'hauteur': ('Hauteur', 70, 'center'),
            'largeur': ('Largeur', 70, 'center'),
            'prix_achat': ('Achat HT', 90, 'e'),
            'prix_vente': ('Vente HT', 90, 'e'),
            'reference': ('Ref.', 80, 'center'),
            'pdf': ('Fiche', 60, 'center'),
            'devis': ('Devis', 60, 'center'),
        }

        for col, (text, width, anchor) in col_config.items():
            self.tree.heading(col, text=text, command=lambda c=col: self.sort_column(c))
            self.tree.column(col, width=width, anchor=anchor, minwidth=50)

        # Scrollbars
        self.vsb = ttk.Scrollbar(table_frame, orient="vertical", command=self._on_vsb_scroll)
        self.hsb = ttk.Scrollbar(table_frame, orient="horizontal", command=self._on_hsb_scroll)
        self.tree.configure(yscrollcommand=self._on_tree_vsb, xscrollcommand=self._on_tree_hsb)

        # Grid layout
        self.tree.grid(row=0, column=0, sticky='nsew')
        self.vsb.grid(row=0, column=1, sticky='ns')
        self.hsb.grid(row=1, column=0, sticky='ew')

        table_frame.grid_columnconfigure(0, weight=1)
        table_frame.grid_rowconfigure(0, weight=1)

        # Frame overlay pour les icônes PDF
        self.pdf_overlay_frame = tk.Frame(table_frame, bg='')

        # Bindings pour mettre à jour les icônes
        self.tree.bind('<Configure>', lambda e: self._update_all_icons())
        self.vsb.bind('<B1-Motion>', lambda e: self.root.after(10, self._update_all_icons))
        self.hsb.bind('<B1-Motion>', lambda e: self.root.after(10, self._update_all_icons))

        # Bindings
        self.tree.bind('<Double-1>', self._on_tree_double_click)
        self.tree.bind('<Button-1>', self._on_tree_click)
        self.tree.bind('<Return>', lambda e: self.on_edit())

        # Barre d'actions en bas
        action_bar = tk.Frame(main_container, bg=Theme.COLORS['bg'], height=56)
        action_bar.pack(fill=tk.X, pady=(12, 0))

        # Boutons gauche
        left_btns = tk.Frame(action_bar, bg=Theme.COLORS['bg'])
        left_btns.pack(side=tk.LEFT)

        # Bouton Nouveau
        add_btn = tk.Button(left_btns, text="+ Nouveau produit",
                           font=Theme.FONTS['body_bold'],
                           bg=Theme.COLORS['accent'],
                           fg=Theme.COLORS['white'],
                           activebackground=Theme.COLORS['accent_light'],
                           activeforeground=Theme.COLORS['white'],
                           bd=0, padx=20, pady=10, cursor='hand2',
                           command=self.on_add)
        add_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Modifier
        edit_btn = tk.Button(left_btns, text="Modifier",
                            font=Theme.FONTS['body'],
                            bg=Theme.COLORS['bg_dark'],
                            fg=Theme.COLORS['text'],
                            activebackground=Theme.COLORS['border'],
                            bd=0, padx=16, pady=10, cursor='hand2',
                            command=self.on_edit)
        edit_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Supprimer
        del_btn = tk.Button(left_btns, text="Supprimer",
                           font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg_dark'],
                           fg=Theme.COLORS['danger'],
                           activebackground=Theme.COLORS['danger_light'],
                           bd=0, padx=16, pady=10, cursor='hand2',
                           command=self.on_delete)
        del_btn.pack(side=tk.LEFT)

        # Boutons droite
        right_btns = tk.Frame(action_bar, bg=Theme.COLORS['bg'])
        right_btns.pack(side=tk.RIGHT)

        # Bouton Categories
        cat_btn = tk.Button(right_btns, text="Categories",
                           font=Theme.FONTS['body'],
                           bg=Theme.COLORS['bg_dark'],
                           fg=Theme.COLORS['text'],
                           activebackground=Theme.COLORS['border'],
                           bd=0, padx=16, pady=10, cursor='hand2',
                           command=self.on_manage_categories)
        cat_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Importer
        import_btn = tk.Button(right_btns, text="Importer",
                              font=Theme.FONTS['body'],
                              bg=Theme.COLORS['bg_dark'],
                              fg=Theme.COLORS['text'],
                              activebackground=Theme.COLORS['border'],
                              bd=0, padx=16, pady=10, cursor='hand2',
                              command=self.on_import)
        import_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Exporter
        export_btn = tk.Button(right_btns, text="Exporter",
                              font=Theme.FONTS['body_bold'],
                              bg=Theme.COLORS['secondary'],
                              fg=Theme.COLORS['white'],
                              activebackground=Theme.COLORS['secondary_light'],
                              bd=0, padx=16, pady=10, cursor='hand2',
                              command=self.on_export_selection)
        export_btn.pack(side=tk.LEFT)

    def _create_status_bar(self):
        """Cree la barre de statut minimaliste"""
        status_frame = tk.Frame(self.root, bg=Theme.COLORS['border'], height=28)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)

        inner = tk.Frame(status_frame, bg=Theme.COLORS['bg_alt'])
        inner.pack(fill=tk.BOTH, expand=True)

        self.status_label = tk.Label(inner, text="Pret",
                                    bg=Theme.COLORS['bg_alt'],
                                    fg=Theme.COLORS['text_muted'],
                                    font=Theme.FONTS['tiny'])
        self.status_label.pack(side=tk.LEFT, padx=16, pady=4)

        # Version
        tk.Label(inner, text="v1.0.0",
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted'],
                font=Theme.FONTS['tiny']).pack(side=tk.RIGHT, padx=16, pady=4)

    def set_status(self, message: str):
        """Met a jour le message de statut"""
        self.status_label.config(text=message)
        self.root.update_idletasks()

    def refresh_data(self):
        """Rafraichit les donnees"""
        # Mettre a jour les categories
        cats = ['Toutes'] + self.db.get_categories_names()
        self.category_combo['values'] = cats

        # Mettre a jour les sous-categories
        self.update_subcategories()

        # Mettre a jour les hauteurs et largeurs
        self.update_hauteurs()
        self.update_largeurs()

        # Mettre a jour la marge
        self.marge_var.set(str(self.db.get_marge()))

        # Rechercher
        self.on_search()

        self.set_status(f"Actualise - {datetime.now().strftime('%H:%M')}")

    def update_subcategories(self):
        """Met a jour la liste des sous-categories selon la categorie selectionnee"""
        categorie = self.category_var.get()

        if categorie == "Toutes":
            produits = self.db.search_produits()
        else:
            produits = self.db.search_produits(categorie=categorie)

        # Extraire les sous-categories uniques
        subcats = sorted(set(p['sous_categorie'] for p in produits if p['sous_categorie']))
        self.subcategory_combo['values'] = ['Toutes'] + subcats
        self.subcategory_var.set('Toutes')

    def on_category_change(self, event=None):
        """Callback quand la categorie change"""
        self.update_subcategories()
        self.update_hauteurs()
        self.update_largeurs()
        self.on_search()

    def update_hauteurs(self):
        """Met a jour la liste des hauteurs disponibles"""
        categorie = self.category_var.get()
        categorie = categorie if categorie != "Toutes" else None
        hauteurs = self.db.get_hauteurs_distinctes(categorie)
        self.hauteur_combo['values'] = ['Toutes'] + [str(h) for h in hauteurs]
        self.hauteur_var.set('Toutes')

    def update_largeurs(self):
        """Met a jour la liste des largeurs disponibles"""
        categorie = self.category_var.get()
        categorie = categorie if categorie != "Toutes" else None
        hauteur_str = self.hauteur_var.get()
        hauteur = int(hauteur_str) if hauteur_str and hauteur_str != "Toutes" else None
        largeurs = self.db.get_largeurs_distinctes(categorie, hauteur)
        self.largeur_combo['values'] = ['Toutes'] + [str(l) for l in largeurs]
        self.largeur_var.set('Toutes')

    def on_hauteur_change(self, event=None):
        """Callback quand la hauteur change"""
        self.update_largeurs()
        self.on_search()

    def on_search(self, *args):
        """Execute la recherche"""
        terme = self.search_var.get()
        categorie = self.category_var.get()
        subcategorie = self.subcategory_var.get()
        hauteur_str = self.hauteur_var.get()
        largeur_str = self.largeur_var.get()

        # Convertir hauteur/largeur
        hauteur = int(hauteur_str) if hauteur_str and hauteur_str != "Toutes" else None
        largeur = int(largeur_str) if largeur_str and largeur_str != "Toutes" else None

        # Recherche de base avec filtres
        produits = self.db.search_produits(terme, categorie, hauteur=hauteur, largeur=largeur)

        # Filtre par sous-categorie
        if subcategorie and subcategorie != "Toutes":
            produits = [p for p in produits if p['sous_categorie'] == subcategorie]

        try:
            valeur_marge = self.marge_var.get().replace(',', '.').replace('%', '').strip()
            marge = float(valeur_marge) if valeur_marge else 20
        except ValueError:
            marge = 20

        # Nettoyer les icônes PDF existantes avant de vider le tableau
        self._clear_pdf_icons()

        # Vider le tableau
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Remplir
        for p in produits:
            prix_vente = p['prix_achat'] * (1 + marge / 100)
            has_pdf = 'PDF' if p.get('fiche_technique') else ''  # Texte temporaire
            has_devis = 'DEVIS' if p.get('devis_fournisseur') else ''  # Texte temporaire
            self.tree.insert('', tk.END, values=(
                p['id'],
                p['categorie'],
                p['sous_categorie'] or '-',
                p['designation'],
                p['hauteur'] or '-',
                p['largeur'] or '-',
                f"{p['prix_achat']:.2f} EUR",
                f"{prix_vente:.2f} EUR",
                p['reference'] or '-',
                has_pdf,
                has_devis
            ))

        # Mise a jour compteur
        count = len(produits)
        self.count_label.config(text=f"{count} produit{'s' if count != 1 else ''}")

        # Mettre à jour les icônes après un court délai
        self.root.after(150, self._update_all_icons)

    def clear_search(self):
        """Efface la recherche"""
        self.search_var.set("")
        self.category_var.set("Toutes")
        self.subcategory_var.set("Toutes")
        self.hauteur_var.set("Toutes")
        self.largeur_var.set("Toutes")
        self.update_subcategories()
        self.update_hauteurs()
        self.update_largeurs()

    def on_apply_marge(self):
        """Applique la nouvelle marge"""
        try:
            valeur = self.marge_var.get().strip()
            valeur = valeur.replace(',', '.').replace('%', '').strip()

            if not valeur:
                messagebox.showerror("Erreur", "Veuillez entrer une valeur de marge")
                return

            marge = float(valeur)

            if marge < 0:
                messagebox.showwarning("Attention", "La marge est negative")

            self.db.set_marge(marge)
            self.marge_var.set(str(marge))
            self.on_search()
            self.set_status(f"Marge: {marge}%")
        except ValueError:
            messagebox.showerror("Erreur", "Valeur invalide. Entrez un nombre (ex: 20)")

    def sort_column(self, col):
        """Trie le tableau par colonne"""
        items = [(self.tree.set(k, col), k) for k in self.tree.get_children('')]
        items.sort()
        for index, (val, k) in enumerate(items):
            self.tree.move(k, '', index)

    def on_add(self):
        """Ajoute un nouveau produit"""
        dialog = ProductDialog(self.root, self.db)
        if dialog.result:
            self.refresh_data()
            self.set_status("Produit ajoute")

    def on_edit(self):
        """Modifie le produit selectionne"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez un produit")
            return

        item = self.tree.item(selection[0])
        product_id = item['values'][0]

        dialog = ProductDialog(self.root, self.db, product_id)
        if dialog.result:
            self.refresh_data()
            self.set_status("Produit modifie")

    def on_delete(self):
        """Supprime le produit selectionne"""
        selection = self.tree.selection()
        if not selection:
            messagebox.showwarning("Attention", "Selectionnez un produit")
            return

        if messagebox.askyesno("Confirmer", "Supprimer ce produit ?"):
            item = self.tree.item(selection[0])
            product_id = item['values'][0]
            self.db.delete_produit(product_id)
            self.refresh_data()
            self.set_status("Produit supprime")

    def on_import(self):
        """Importe un fichier CSV"""
        filepath = filedialog.askopenfilename(
            title="Importer CSV",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous", "*.*")]
        )
        if filepath:
            try:
                self.set_status("Import en cours...")
                count = self.db.import_csv(filepath)
                self.refresh_data()
                messagebox.showinfo("Import termine", f"{count} produit(s) importe(s)")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur d'import:\n{e}")

    def on_download_template(self):
        """Telecharge un modele CSV pour l'import"""
        filepath = filedialog.asksaveasfilename(
            title="Enregistrer le modele d'import",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfilename="modele_import.csv"
        )
        if filepath:
            try:
                self.db.create_import_template(filepath)
                messagebox.showinfo("Modele cree",
                    f"Le modele d'import a ete cree.\n\n"
                    f"Colonnes du fichier:\n"
                    f"- CATEGORIE: Categorie du produit (obligatoire)\n"
                    f"- SOUS-CATEGORIE: Sous-categorie (optionnel)\n"
                    f"- DESIGNATION: Nom du produit (obligatoire)\n"
                    f"- HAUTEUR: Hauteur en mm (optionnel)\n"
                    f"- LARGEUR: Largeur en mm (optionnel)\n"
                    f"- PRIX_UNITAIRE_HT: Prix d'achat (optionnel)\n"
                    f"- ARTICLE: Reference produit (optionnel)\n"
                    f"- FOURNISSEUR: Nom du fournisseur (optionnel)\n"
                    f"- CHANTIER: Nom du chantier/projet (optionnel)\n"
                    f"- FICHE_TECHNIQUE: Chemin du fichier PDF (optionnel)")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur:\n{e}")

    def on_export(self):
        """Exporte tous les produits"""
        filepath = filedialog.asksaveasfilename(
            title="Exporter CSV",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfilename=f"catalogue_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        if filepath:
            try:
                count = self.db.export_csv(filepath)
                messagebox.showinfo("Export termine", f"{count} produit(s) exporte(s)")
                self.set_status(f"Export: {count} produits")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur d'export:\n{e}")

    def on_export_selection(self):
        """Exporte la selection actuelle"""
        terme = self.search_var.get()
        categorie = self.category_var.get()
        produits = self.db.search_produits(terme, categorie)

        subcategorie = self.subcategory_var.get()
        if subcategorie and subcategorie != "Toutes":
            produits = [p for p in produits if p['sous_categorie'] == subcategorie]

        if not produits:
            messagebox.showwarning("Attention", "Aucun produit a exporter")
            return

        filepath = filedialog.asksaveasfilename(
            title="Exporter la selection",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfilename=f"selection_{datetime.now().strftime('%Y%m%d_%H%M')}.csv"
        )
        if filepath:
            try:
                marge = float(self.marge_var.get().replace(',', '.').replace('%', '').strip() or '20')
                count = self.db.export_csv(filepath, produits, marge)
                messagebox.showinfo("Export termine", f"{count} produit(s) exporte(s)")
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur d'export:\n{e}")

    def on_settings(self):
        """Ouvre les parametres"""
        dialog = SettingsDialog(self.root, self.db)
        if dialog.result:
            self.refresh_data()

    def on_manage_categories(self):
        """Ouvre la gestion des categories"""
        dialog = CategoryDialog(self.root, self.db)
        if dialog.result:
            self.refresh_data()
            self.set_status("Categories mises a jour")

    def show_stats(self):
        """Affiche les statistiques"""
        stats = self.db.get_stats()

        msg = f"""Statistiques du catalogue

Total produits: {stats['total_produits']}

Par categorie:
"""
        for cat, count in stats['par_categorie'].items():
            msg += f"  {cat}: {count}\n"

        msg += f"""
Prix moyen: {stats['prix_moyen']:.2f} EUR
Prix min: {stats['prix_min']:.2f} EUR
Prix max: {stats['prix_max']:.2f} EUR
"""
        messagebox.showinfo("Statistiques", msg)

    def _on_tree_click(self, event):
        """Gere le clic simple sur le tableau"""
        # Identifier la region cliquee
        region = self.tree.identify_region(event.x, event.y)
        if region != 'cell':
            return

        # Identifier la colonne
        column = self.tree.identify_column(event.x)
        # La colonne pdf est la 10eme (#10)
        if column == '#10':
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self._open_pdf_for_item(item)

    def _on_tree_double_click(self, event):
        """Gere le double-clic sur le tableau"""
        # Identifier la colonne
        column = self.tree.identify_column(event.x)
        # Si c'est la colonne PDF, ne pas ouvrir l'edition
        if column == '#10':
            return
        self.on_edit()

    def _open_pdf_for_item(self, item):
        """Ouvre la fiche PDF pour un item du tableau"""
        values = self.tree.item(item)['values']
        if not values:
            return

        product_id = values[0]
        produit = self.db.get_produit(product_id)
        if not produit:
            return

        filepath = produit.get('fiche_technique')
        if not filepath:
            return

        if not os.path.exists(filepath):
            messagebox.showerror("Erreur", f"Le fichier n'existe pas:\n{filepath}")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
            self.set_status(f"Ouverture: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")

    def on_about(self):
        """Affiche la boite A propos"""
        AboutDialog(self.root)

    def on_clear_database(self):
        """Vide la base de donnees (tous les produits)"""
        # Double confirmation
        response = messagebox.askyesno(
            "Vider la base de donnees",
            "ATTENTION: Cette action va supprimer TOUS les produits du catalogue.\n\n"
            "Cette action est IRREVERSIBLE.\n\n"
            "Voulez-vous vraiment continuer?"
        )

        if not response:
            return

        # Seconde confirmation
        confirm = messagebox.askyesno(
            "Confirmation DEFINITIVE",
            "Derniere chance!\n\n"
            "Tous les produits vont etre supprimes definitivement.\n\n"
            "Confirmer la suppression?"
        )

        if not confirm:
            return

        # Supprimer tous les produits
        self.db.clear_all_produits()
        self.refresh_data()
        self.set_status("Base de donnees videe")
        messagebox.showinfo("Termine", "Tous les produits ont ete supprimes.")

    def _on_vsb_scroll(self, *args):
        """Callback pour le scroll vertical"""
        self.tree.yview(*args)
        self._update_all_icons()

    def _on_hsb_scroll(self, *args):
        """Callback pour le scroll horizontal"""
        self.tree.xview(*args)
        self._update_all_icons()

    def _on_tree_vsb(self, *args):
        """Callback quand le Treeview scrolle verticalement"""
        self.vsb.set(*args)
        self._update_all_icons()

    def _on_tree_hsb(self, *args):
        """Callback quand le Treeview scrolle horizontalement"""
        self.hsb.set(*args)
        self._update_all_icons()

    def _clear_pdf_icons(self):
        """Nettoie toutes les icônes affichées (PDF et Devis)"""
        for label in self.pdf_labels:
            try:
                label.place_forget()
                label.destroy()
            except:
                pass
        self.pdf_labels.clear()

        for label in self.devis_labels:
            try:
                label.place_forget()
                label.destroy()
            except:
                pass
        self.devis_labels.clear()

    def _update_all_icons(self):
        """Met à jour toutes les icônes (PDF et Devis)"""
        self._update_pdf_icons()
        self._update_devis_icons()

    def _update_pdf_icons(self):
        """Met à jour les positions des icônes PDF avec des Labels overlay"""
        if not self.pdf_icon:
            return

        # Nettoyer les anciennes icônes
        self._clear_pdf_icons()

        # Obtenir les limites du Treeview
        try:
            tree_height = self.tree.winfo_height()
            tree_width = self.tree.winfo_width()
        except:
            return

        # Obtenir la colonne PDF (index 9)
        try:
            # Parcourir les items visibles
            for item in self.tree.get_children():
                bbox = self.tree.bbox(item, 'pdf')
                if bbox:  # Item visible
                    # Vérifier que la cellule est bien dans les limites du Treeview
                    if bbox[1] < 0 or bbox[1] + bbox[3] > tree_height:
                        continue  # Cellule en dehors de la vue verticale

                    if bbox[0] < 0 or bbox[0] + bbox[2] > tree_width:
                        continue  # Cellule en dehors de la vue horizontale

                    values = self.tree.item(item)['values']
                    if len(values) > 9 and values[9] == 'PDF':  # A un PDF
                        # Créer un label avec l'icône
                        # bbox retourne (x, y, width, height) de la cellule
                        x = bbox[0] + (bbox[2] - 24) // 2  # Centrer horizontalement
                        y = bbox[1] + (bbox[3] - 24) // 2 + 1  # Centrer verticalement avec petit ajustement

                        label = tk.Label(self.tree.master, image=self.pdf_icon,
                                        bg='white', cursor='hand2',
                                        bd=0, relief='flat')
                        label.place(x=x, y=y, width=24, height=24)

                        # Bind pour ouvrir le PDF au clic
                        label.bind('<Button-1>', lambda e, i=item: self._on_pdf_icon_click(i))

                        self.pdf_labels.append(label)

        except Exception as e:
            pass  # Ignorer les erreurs de positionnement

    def _update_devis_icons(self):
        """Met à jour les positions des icônes Devis avec des Labels overlay"""
        if not self.devis_icon:
            return

        # Obtenir les limites du Treeview
        try:
            tree_height = self.tree.winfo_height()
            tree_width = self.tree.winfo_width()
        except:
            return

        # Obtenir la colonne Devis (index 10)
        try:
            # Parcourir les items visibles
            for item in self.tree.get_children():
                bbox = self.tree.bbox(item, 'devis')
                if bbox:  # Item visible
                    # Vérifier que la cellule est bien dans les limites du Treeview
                    if bbox[1] < 0 or bbox[1] + bbox[3] > tree_height:
                        continue  # Cellule en dehors de la vue verticale

                    if bbox[0] < 0 or bbox[0] + bbox[2] > tree_width:
                        continue  # Cellule en dehors de la vue horizontale

                    values = self.tree.item(item)['values']
                    if len(values) > 10 and values[10] == 'DEVIS':  # A un devis
                        # Créer un label avec l'icône
                        x = bbox[0] + (bbox[2] - 24) // 2  # Centrer horizontalement
                        y = bbox[1] + (bbox[3] - 24) // 2 + 1  # Centrer verticalement

                        label = tk.Label(self.tree.master, image=self.devis_icon,
                                        bg='white', cursor='hand2',
                                        bd=0, relief='flat')
                        label.place(x=x, y=y, width=24, height=24)

                        # Bind pour ouvrir le devis au clic
                        label.bind('<Button-1>', lambda e, i=item: self._on_devis_icon_click(i))

                        self.devis_labels.append(label)

        except Exception as e:
            pass  # Ignorer les erreurs de positionnement

    def _on_pdf_icon_click(self, item):
        """Gère le clic sur une icône PDF"""
        self.tree.selection_set(item)
        self._open_pdf_for_item(item)

    def _on_devis_icon_click(self, item):
        """Gère le clic sur une icône Devis"""
        self.tree.selection_set(item)
        self._open_devis_for_item(item)

    def _open_devis_for_item(self, item):
        """Ouvre le devis pour un item du tableau"""
        values = self.tree.item(item)['values']
        if not values:
            return

        product_id = values[0]
        produit = self.db.get_produit(product_id)
        if not produit:
            return

        filepath = produit.get('devis_fournisseur')
        if not filepath:
            return

        # Résoudre le chemin
        filepath = self.db.resolve_fiche_path(filepath)

        if not os.path.exists(filepath):
            messagebox.showerror("Erreur", f"Le fichier n'existe pas:\n{filepath}")
            return

        try:
            if sys.platform == 'win32':
                os.startfile(filepath)
            elif sys.platform == 'darwin':
                subprocess.run(['open', filepath])
            else:
                subprocess.run(['xdg-open', filepath])
            self.set_status(f"Ouverture: {os.path.basename(filepath)}")
        except Exception as e:
            messagebox.showerror("Erreur", f"Impossible d'ouvrir le fichier:\n{e}")

    def on_closing(self):
        """Ferme l'application"""
        # Nettoyer les icônes PDF
        self._clear_pdf_icons()

        self.db.close()
        self.root.destroy()
