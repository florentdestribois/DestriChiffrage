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

# Pour le logo et icones
try:
    from PIL import Image, ImageTk
    HAS_PIL = True
except ImportError:
    HAS_PIL = False

# Gestionnaire de devis rapide
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from cart_manager import CartManager
from ui.cart_panel import CartPanel
from ui.cart_export_dialog import CartExportDialog

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from database import Database
from ui.theme import Theme
from ui.dialogs import ProductDialog, SettingsDialog, AboutDialog, CategoryDialog
from ui.marches_analyse_view import MarchesAnalyseView
from ui.dpgf_import_dialog import DPGFImportDialog
from utils import get_resource_path


class MainWindow:
    """Fenetre principale de l'application"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.db = Database()

        # Variables
        self.search_var = tk.StringVar()
        self.category_var = tk.StringVar(value="Toutes")
        self.subcategory_var = tk.StringVar(value="Toutes")
        self.subcategory2_var = tk.StringVar(value="Toutes")
        self.subcategory3_var = tk.StringVar(value="Toutes")
        self.hauteur_var = tk.StringVar(value="Toutes")
        self.largeur_var = tk.StringVar(value="Toutes")
        self.marge_var = tk.StringVar(value=str(self.db.get_marge()))

        # Charger les icones PDF, Devis et Devis rapide
        self.pdf_icon = None
        self.devis_icon = None
        self.cart_icon = None
        self.pdf_labels = []  # Labels pour afficher les icônes PDF
        self.devis_labels = []  # Labels pour afficher les icônes Devis
        self.cart_labels = []  # Labels pour afficher les icônes Devis rapide
        self._load_pdf_icon()
        self._load_devis_icon()
        self._load_cart_icon()

        # Gestionnaire de devis rapide
        self.cart_manager = CartManager.get_instance()

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
                icon_path = get_resource_path('src/assets/pdf.png')
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
                icon_path = get_resource_path('src/assets/pdf.png')
                if os.path.exists(icon_path):
                    img = Image.open(icon_path)
                    # Redimensionner l'icone pour qu'elle tienne dans la cellule
                    img = img.resize((24, 24), Image.Resampling.LANCZOS)
                    self.devis_icon = ImageTk.PhotoImage(img)
            except Exception as e:
                print(f"Erreur chargement icone Devis: {e}")

    def _load_cart_icon(self):
        """Charge l'icone Devis rapide (utilise emoji Unicode)"""
        # Pour l'instant, on n'utilisera pas d'image mais un label texte
        # avec l'emoji panier Unicode
        pass

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

        # Menu Marches
        marches_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Marches", menu=marches_menu)
        marches_menu.add_command(label="Analyse des marches...", command=self.on_marches_analyse)
        marches_menu.add_command(label="Nouveau chantier / DPGF...", command=self.on_new_chantier, accelerator="Ctrl+Shift+N")
        marches_menu.add_separator()
        marches_menu.add_command(label="Telecharger modele DPGF...", command=self.on_download_dpgf_template)

        # Menu Affichage
        view_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Affichage", menu=view_menu)
        view_menu.add_command(label="Actualiser", command=self.refresh_data, accelerator="F5")
        view_menu.add_command(label="Statistiques", command=self.show_stats)

        # Menu Aide
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Aide", menu=help_menu)
        help_menu.add_command(label="Verifier les mises a jour...", command=self.on_check_updates)
        help_menu.add_separator()
        help_menu.add_command(label="A propos", command=self.on_about)

        # Raccourcis clavier
        self.root.bind('<Control-i>', lambda e: self.on_import())
        self.root.bind('<Control-e>', lambda e: self.on_export())
        self.root.bind('<Control-n>', lambda e: self.on_add())
        self.root.bind('<Control-m>', lambda e: self.on_edit())
        self.root.bind('<Control-g>', lambda e: self.on_manage_categories())
        self.root.bind('<Control-Shift-N>', lambda e: self.on_new_chantier())
        self.root.bind('<Delete>', lambda e: self.on_delete())
        self.root.bind('<F5>', lambda e: self.refresh_data())

    def _create_header(self):
        """Cree l'en-tete moderne et elegant"""
        # Header avec fond sombre - Utilise un Frame personnalisé car create_header ne convient pas ici
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
                logo_path = get_resource_path('src/assets/logo.png')
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

        tk.Label(title_frame, text="Chiffrage et approvisionnement",
                font=('Segoe UI', 9), bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        # Droite: Controle de marge (pack en premier pour que le centre prenne l'espace restant)
        right_frame = tk.Frame(header_content, bg=Theme.COLORS['primary'])
        right_frame.pack(side=tk.RIGHT, fill=tk.Y)

        # Centre: Menu Vente
        center_frame = tk.Frame(header_content, bg=Theme.COLORS['primary'])
        center_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(40, 0))

        # Bouton menu deroulant "Vente" - Style moderne
        self.vente_menubutton = tk.Menubutton(center_frame,
                                              text="Vente \u25BC",
                                              font=('Segoe UI', 11, 'bold'),
                                              bg=Theme.COLORS['primary_light'],
                                              fg=Theme.COLORS['white'],
                                              activebackground=Theme.COLORS['accent'],
                                              activeforeground=Theme.COLORS['white'],
                                              bd=0, padx=20, pady=10, cursor='hand2',
                                              relief='flat')
        self.vente_menubutton.pack(side=tk.LEFT)

        # Menu deroulant
        vente_menu = tk.Menu(self.vente_menubutton, tearoff=0,
                            bg=Theme.COLORS['bg_alt'],
                            fg=Theme.COLORS['text'],
                            activebackground=Theme.COLORS['secondary'],
                            activeforeground=Theme.COLORS['white'],
                            font=('Segoe UI', 10))
        vente_menu.add_command(label="Analyse des ventes", command=self.on_marches_analyse)
        vente_menu.add_command(label="Nouveau chantier", command=self.on_new_chantier)
        self.vente_menubutton.config(menu=vente_menu)

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

        # Filtre sous-categorie niveau 1
        subcat_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        subcat_frame.pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(subcat_frame, text="Sous-cat. 1",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.subcategory_combo = ttk.Combobox(subcat_frame, textvariable=self.subcategory_var,
                                             width=18, state='readonly',
                                             font=Theme.FONTS['body'])
        self.subcategory_combo.pack(pady=(2, 0))
        self.subcategory_combo.bind('<<ComboboxSelected>>', self.on_subcategory_change)

        # Filtre sous-categorie niveau 2
        subcat2_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        subcat2_frame.pack(side=tk.LEFT, padx=(0, 12))

        tk.Label(subcat2_frame, text="Sous-cat. 2",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.subcategory2_combo = ttk.Combobox(subcat2_frame, textvariable=self.subcategory2_var,
                                              width=18, state='readonly',
                                              font=Theme.FONTS['body'])
        self.subcategory2_combo.pack(pady=(2, 0))
        self.subcategory2_combo.bind('<<ComboboxSelected>>', self.on_subcategory2_change)

        # Filtre sous-categorie niveau 3
        subcat3_frame = tk.Frame(filter_row, bg=Theme.COLORS['bg_alt'])
        subcat3_frame.pack(side=tk.LEFT, padx=(0, 16))

        tk.Label(subcat3_frame, text="Sous-cat. 3",
                font=Theme.FONTS['tiny'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        self.subcategory3_combo = ttk.Combobox(subcat3_frame, textvariable=self.subcategory3_var,
                                              width=18, state='readonly',
                                              font=Theme.FONTS['body'])
        self.subcategory3_combo.pack(pady=(2, 0))
        self.subcategory3_combo.bind('<<ComboboxSelected>>', lambda e: self.on_search())

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

        clear_btn = Theme.create_button(clear_frame, "Effacer les filtres", command=self.clear_search,
                                       style='ghost', padx=12, pady=4)
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
        columns = ('id', 'categorie', 'sous_categorie', 'sous_categorie_2', 'sous_categorie_3',
                  'designation', 'hauteur', 'largeur', 'prix_achat', 'prix_vente', 'reference',
                  'pdf', 'devis', 'cart')

        self.tree = ttk.Treeview(table_frame, columns=columns, show='headings',
                                selectmode='browse')

        # Configuration des colonnes
        col_config = {
            'id': ('ID', 50, 'center'),
            'categorie': ('Categorie', 100, 'w'),
            'sous_categorie': ('Sous-cat. 1', 100, 'w'),
            'sous_categorie_2': ('Sous-cat. 2', 100, 'w'),
            'sous_categorie_3': ('Sous-cat. 3', 100, 'w'),
            'designation': ('Designation', 220, 'w'),
            'hauteur': ('Hauteur', 60, 'center'),
            'largeur': ('Largeur', 60, 'center'),
            'prix_achat': ('Achat HT', 80, 'e'),
            'prix_vente': ('Vente HT', 80, 'e'),
            'reference': ('Ref.', 70, 'center'),
            'pdf': ('Fiche', 50, 'center'),
            'devis': ('Devis', 50, 'center'),
            'cart': ('Devis', 50, 'center'),
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
        self.tree.bind('<Button-3>', self._show_context_menu)  # Clic droit
        self.tree.bind('<Control-c>', self._copy_row)  # Ctrl+C

        # Menu contextuel
        self._create_context_menu()

        # Barre d'actions en bas
        action_bar = tk.Frame(main_container, bg=Theme.COLORS['bg'], height=56)
        action_bar.pack(fill=tk.X, pady=(12, 0))

        # Boutons gauche
        left_btns = tk.Frame(action_bar, bg=Theme.COLORS['bg'])
        left_btns.pack(side=tk.LEFT)

        # Bouton Nouveau - Action principale en Or Destribois
        add_btn = Theme.create_button(left_btns, "+ Nouveau produit", command=self.on_add,
                                     style='secondary')
        add_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Modifier - Style discret
        edit_btn = Theme.create_button(left_btns, "Modifier", command=self.on_edit,
                                      style='ghost', padx=16)
        edit_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Supprimer - Ghost avec texte rouge discret
        del_btn = Theme.create_button(left_btns, "Supprimer", command=self.on_delete,
                                     style='danger-ghost', padx=16)
        del_btn.pack(side=tk.LEFT)

        # Boutons droite
        right_btns = tk.Frame(action_bar, bg=Theme.COLORS['bg'])
        right_btns.pack(side=tk.RIGHT)

        # Bouton Panier
        self.cart_btn = Theme.create_button(right_btns, "\U0001F4CB Devis rapide (0)",
                                           command=self._show_cart_panel, style='secondary', padx=16)
        self.cart_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Categories
        cat_btn = Theme.create_button(right_btns, "Categories", command=self.on_manage_categories,
                                     style='ghost', padx=16)
        cat_btn.pack(side=tk.LEFT, padx=(0, 8))

        # Bouton Importer
        import_btn = Theme.create_button(right_btns, "Importer", command=self.on_import,
                                        style='ghost', padx=16)
        import_btn.pack(side=tk.LEFT, padx=(0, 8))

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

        # Mettre a jour les sous-categories (avec preservation des selections)
        self.update_subcategories(preserve_selection=True)

        # Mettre a jour les hauteurs et largeurs
        self.update_hauteurs()
        self.update_largeurs()

        # Mettre a jour la marge
        self.marge_var.set(str(self.db.get_marge()))

        # Rechercher
        self.on_search()

        self.set_status(f"Actualise - {datetime.now().strftime('%H:%M')}")

    def update_subcategories(self, preserve_selection: bool = False):
        """Met a jour la liste des sous-categories niveau 1 selon la categorie selectionnee"""
        categorie = self.category_var.get()
        current_selection = self.subcategory_var.get()

        # Utiliser la nouvelle methode avec filtrage
        subcats = self.db.get_subcategories_filtered(
            level=1,
            categorie=categorie if categorie != "Toutes" else None
        )

        self.subcategory_combo['values'] = ['Toutes'] + subcats

        # Preserver la selection si demande et si elle existe encore
        if preserve_selection and current_selection in subcats:
            self.subcategory_var.set(current_selection)
        else:
            self.subcategory_var.set('Toutes')

        # Mettre a jour les sous-categories niveau 2
        self.update_subcategories2(preserve_selection)

    def update_subcategories2(self, preserve_selection: bool = False):
        """Met a jour la liste des sous-categories niveau 2 selon les filtres precedents"""
        categorie = self.category_var.get()
        sous_cat1 = self.subcategory_var.get()
        current_selection = self.subcategory2_var.get()

        # Utiliser la methode avec filtrage en cascade
        subcats2 = self.db.get_subcategories_filtered(
            level=2,
            categorie=categorie if categorie != "Toutes" else None,
            sous_categorie=sous_cat1 if sous_cat1 != "Toutes" else None
        )

        self.subcategory2_combo['values'] = ['Toutes'] + subcats2

        # Preserver la selection si demande et si elle existe encore
        if preserve_selection and current_selection in subcats2:
            self.subcategory2_var.set(current_selection)
        else:
            self.subcategory2_var.set('Toutes')

        # Mettre a jour les sous-categories niveau 3
        self.update_subcategories3(preserve_selection)

    def update_subcategories3(self, preserve_selection: bool = False):
        """Met a jour la liste des sous-categories niveau 3 selon les filtres precedents"""
        categorie = self.category_var.get()
        sous_cat1 = self.subcategory_var.get()
        sous_cat2 = self.subcategory2_var.get()
        current_selection = self.subcategory3_var.get()

        # Utiliser la methode avec filtrage en cascade
        subcats3 = self.db.get_subcategories_filtered(
            level=3,
            categorie=categorie if categorie != "Toutes" else None,
            sous_categorie=sous_cat1 if sous_cat1 != "Toutes" else None,
            sous_categorie_2=sous_cat2 if sous_cat2 != "Toutes" else None
        )

        self.subcategory3_combo['values'] = ['Toutes'] + subcats3

        # Preserver la selection si demande et si elle existe encore
        if preserve_selection and current_selection in subcats3:
            self.subcategory3_var.set(current_selection)
        else:
            self.subcategory3_var.set('Toutes')

    def on_category_change(self, event=None):
        """Callback quand la categorie change"""
        self.update_subcategories(preserve_selection=False)
        self.update_hauteurs()
        self.update_largeurs()
        self.on_search()

    def on_subcategory_change(self, event=None):
        """Callback quand la sous-categorie niveau 1 change"""
        self.update_subcategories2(preserve_selection=False)
        self.on_search()

    def on_subcategory2_change(self, event=None):
        """Callback quand la sous-categorie niveau 2 change"""
        self.update_subcategories3(preserve_selection=False)
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
        subcategorie2 = self.subcategory2_var.get()
        subcategorie3 = self.subcategory3_var.get()
        hauteur_str = self.hauteur_var.get()
        largeur_str = self.largeur_var.get()

        # Convertir hauteur/largeur
        hauteur = int(hauteur_str) if hauteur_str and hauteur_str != "Toutes" else None
        largeur = int(largeur_str) if largeur_str and largeur_str != "Toutes" else None

        # Recherche de base avec filtres
        produits = self.db.search_produits(terme, categorie, hauteur=hauteur, largeur=largeur)

        # Filtre par sous-categorie niveau 1
        if subcategorie and subcategorie != "Toutes":
            produits = [p for p in produits if p['sous_categorie'] == subcategorie]

        # Filtre par sous-categorie niveau 2
        if subcategorie2 and subcategorie2 != "Toutes":
            produits = [p for p in produits if p.get('sous_categorie_2') == subcategorie2]

        # Filtre par sous-categorie niveau 3
        if subcategorie3 and subcategorie3 != "Toutes":
            produits = [p for p in produits if p.get('sous_categorie_3') == subcategorie3]

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
            # Determiner si PDF/Devis/Devis rapide sont presents (tags seulement, pas de texte visible)
            has_pdf = bool(p.get('fiche_technique'))
            has_devis = bool(p.get('devis_fournisseur'))
            in_cart = self.cart_manager.is_in_cart(p['id'])
            tags = []
            if has_pdf:
                tags.append('has_pdf')
            if has_devis:
                tags.append('has_devis')
            if in_cart:
                tags.append('in_cart')

            self.tree.insert('', tk.END, values=(
                p['id'],
                p['categorie'],
                p['sous_categorie'] or '-',
                p.get('sous_categorie_2') or '-',
                p.get('sous_categorie_3') or '-',
                p['designation'],
                p['hauteur'] or '-',
                p['largeur'] or '-',
                f"{p['prix_achat']:.2f} EUR",
                f"{prix_vente:.2f} EUR",
                p['reference'] or '-',
                '',  # Colonne pdf : vide, icone affichee via overlay
                '',  # Colonne devis : vide, icone affichee via overlay
                ''   # Colonne cart : vide, icone affichee via overlay
            ), tags=tuple(tags))

        # Mise a jour compteur
        count = len(produits)
        self.count_label.config(text=f"{count} produit{'s' if count != 1 else ''}")

        # Forcer la mise à jour du Treeview
        self.tree.update_idletasks()

        # Mettre à jour les icônes après un court délai
        self.root.after(300, self._update_all_icons)

    def clear_search(self):
        """Efface la recherche"""
        self.search_var.set("")
        self.category_var.set("Toutes")
        self.subcategory_var.set("Toutes")
        self.subcategory2_var.set("Toutes")
        self.subcategory3_var.set("Toutes")
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
        print("[DEBUG] on_download_template() appelée")
        filepath = filedialog.asksaveasfilename(
            title="Enregistrer le modele d'import",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile="modele_import.csv"
        )
        print(f"[DEBUG] Fichier sélectionné: {filepath}")
        if filepath:
            try:
                print("[DEBUG] Appel de create_import_template()")
                self.db.create_import_template(filepath)
                print("[DEBUG] Template créé avec succès")
                messagebox.showinfo("Modele cree",
                    f"Le modele d'import a ete cree avec succes!\n\n"
                    f"Fichier: {filepath}\n\n"
                    f"Colonnes du fichier:\n"
                    f"- CATEGORIE: Categorie du produit (obligatoire)\n"
                    f"- SOUS-CATEGORIE: Sous-categorie (optionnel)\n"
                    f"- DESIGNATION: Nom du produit (obligatoire)\n"
                    f"- DESCRIPTION: Description detaillee (optionnel)\n"
                    f"- HAUTEUR: Hauteur en mm (optionnel)\n"
                    f"- LARGEUR: Largeur en mm (optionnel)\n"
                    f"- PRIX_UNITAIRE_HT: Prix d'achat (optionnel)\n"
                    f"- ARTICLE: Reference produit (optionnel)\n"
                    f"- FOURNISSEUR: Nom du fournisseur (optionnel)\n"
                    f"- CHANTIER: Nom du chantier/projet (optionnel)\n"
                    f"- FICHE_TECHNIQUE: Chemin du fichier PDF (optionnel)")
            except Exception as e:
                print(f"[DEBUG] ERREUR: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erreur", f"Erreur:\n{e}")
        else:
            print("[DEBUG] Aucun fichier sélectionné (annulé)")

    def on_export(self):
        """Exporte tous les produits"""
        print("[DEBUG] on_export() appelée")
        filepath = filedialog.asksaveasfilename(
            title="Exporter CSV",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv")],
            initialfile=f"catalogue_{datetime.now().strftime('%Y%m%d')}.csv"
        )
        print(f"[DEBUG] Fichier sélectionné: {filepath}")
        if filepath:
            try:
                print("[DEBUG] Appel de export_csv()")
                count = self.db.export_csv(filepath)
                print(f"[DEBUG] Export réussi: {count} produits")
                messagebox.showinfo("Export termine",
                    f"{count} produit(s) exporte(s) avec succes!\n\n"
                    f"Fichier: {filepath}")
                self.set_status(f"Export: {count} produits")
            except Exception as e:
                print(f"[DEBUG] ERREUR: {e}")
                import traceback
                traceback.print_exc()
                messagebox.showerror("Erreur", f"Erreur d'export:\n{e}")
        else:
            print("[DEBUG] Aucun fichier sélectionné (annulé)")

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
        # La colonne pdf est la 12eme (#12)
        if column == '#12':
            item = self.tree.identify_row(event.y)
            if item:
                self.tree.selection_set(item)
                self._open_pdf_for_item(item)

    def _on_tree_double_click(self, event):
        """Gere le double-clic sur le tableau"""
        # Identifier la colonne
        column = self.tree.identify_column(event.x)
        # Si c'est la colonne PDF, ne pas ouvrir l'edition
        if column == '#12':
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

    def on_check_updates(self):
        """Verifie les mises a jour disponibles"""
        import threading

        def check_in_thread():
            """Verifie les mises a jour dans un thread"""
            try:
                from ui.update_dialog import UpdateDialog, show_no_update_dialog, show_check_error_dialog
                from updater import Updater

                updater = Updater()
                update_info = updater.check_for_updates()

                # Afficher le resultat dans le thread principal
                self.root.after(0, lambda: self._show_update_result(update_info))

            except Exception as e:
                import traceback
                traceback.print_exc()
                # Afficher l'erreur à l'utilisateur
                self.root.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de la vérification:\n{str(e)}"))

        # Afficher un message temporaire
        self.set_status("Verification des mises a jour...")

        # Lancer la verification dans un thread
        thread = threading.Thread(target=check_in_thread)
        thread.daemon = True
        thread.start()

    def _show_update_result(self, update_info):
        """Affiche le resultat de la verification de mise a jour"""
        try:
            from ui.update_dialog import UpdateDialog, show_no_update_dialog, show_check_error_dialog

            if update_info.get('error'):
                # Erreur
                show_check_error_dialog(self.root, update_info['error'])
                self.set_status("Erreur lors de la verification des mises a jour")
            elif update_info.get('available'):
                # Mise a jour disponible
                UpdateDialog(self.root, update_info)
                self.set_status(f"Mise a jour {update_info['latest_version']} disponible")
            else:
                # Pas de mise a jour
                show_no_update_dialog(self.root)
                self.set_status("Aucune mise a jour disponible")

        except Exception as e:
            import traceback
            traceback.print_exc()
            messagebox.showerror("Erreur", f"Erreur affichage résultat:\n{str(e)}")

    def on_about(self):
        """Affiche la boite A propos"""
        AboutDialog(self.root)

    # ==================== MODULE MARCHES PUBLICS ====================

    def on_marches_analyse(self):
        """Ouvre la vue d'analyse des marches"""
        MarchesAnalyseView(self.root, self.db)

    def on_new_chantier(self):
        """Cree un nouveau chantier avec import DPGF"""
        from ui.dpgf_chiffrage_view import DPGFChiffrageView

        dialog = DPGFImportDialog(self.root, self.db)
        if dialog.result and dialog.chantier_id:
            # Ouvrir directement la vue de chiffrage
            DPGFChiffrageView(self.root, self.db, dialog.chantier_id)

    def on_download_dpgf_template(self):
        """Telecharge un modele DPGF vierge"""
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
                    f"Fichier: {filepath}\n\n"
                    f"Format attendu:\n"
                    f"- NIVEAU 1-3: Structure hierarchique\n"
                    f"- NIVEAU 4: Articles chiffrables"
                )
            except Exception as e:
                messagebox.showerror("Erreur", f"Erreur: {e}")

    def on_clear_database(self):
        """Vide la base de donnees (produits, chantiers, etc.) - Ne touche pas aux parametres"""
        # Dialogue personnalise avec cases a cocher
        dialog = tk.Toplevel(self.root)
        dialog.title("Vider la base de donnees")
        dialog.geometry("450x420")
        dialog.minsize(430, 400)
        dialog.transient(self.root)
        dialog.grab_set()
        dialog.resizable(False, False)

        # Centrer le dialogue
        dialog.update_idletasks()
        x = (dialog.winfo_screenwidth() // 2) - (dialog.winfo_width() // 2)
        y = (dialog.winfo_screenheight() // 2) - (dialog.winfo_height() // 2)
        dialog.geometry(f"+{x}+{y}")

        # Variables pour les cases a cocher
        clear_categories_var = tk.BooleanVar(value=False)
        clear_chantiers_var = tk.BooleanVar(value=True)
        result = {'confirmed': False, 'clear_categories': False, 'clear_chantiers': True}

        # Frame principal
        main_frame = tk.Frame(dialog, bg=Theme.COLORS['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icone et titre
        title_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        title_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(title_frame, text="ATTENTION", font=Theme.FONTS['title'],
                bg=Theme.COLORS['bg'], fg=Theme.COLORS['danger']).pack()

        # Message
        message = ("Cette action va supprimer TOUS les produits du catalogue\n"
                  "et TOUS les chantiers avec leurs donnees.\n\n"
                  "Les parametres (marge, taux horaires) seront conserves.\n"
                  "Les IDs seront reinitialises.\n\n"
                  "Cette action est IRREVERSIBLE.")
        tk.Label(main_frame, text=message, font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                justify=tk.LEFT, wraplength=400).pack(pady=(0, 15))

        # Cases a cocher
        check_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=10, pady=10,
                              highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        check_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Checkbutton(check_frame, text="Supprimer aussi toutes les categories",
                      variable=clear_categories_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2').pack(anchor='w')

        tk.Checkbutton(check_frame, text="Supprimer tous les chantiers et marches",
                      variable=clear_chantiers_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2').pack(anchor='w', pady=(5, 0))

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        btn_frame.pack(fill=tk.X)

        def on_cancel():
            result['confirmed'] = False
            dialog.destroy()

        def on_confirm():
            result['confirmed'] = True
            result['clear_categories'] = clear_categories_var.get()
            result['clear_chantiers'] = clear_chantiers_var.get()
            dialog.destroy()

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=20, pady=8, cursor='hand2',
                 command=on_cancel).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(btn_frame, text="Continuer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['danger'], fg=Theme.COLORS['white'],
                 bd=0, padx=20, pady=8, cursor='hand2',
                 command=on_confirm).pack(side=tk.LEFT)

        # Attendre la fermeture du dialogue
        self.root.wait_window(dialog)

        if not result['confirmed']:
            return

        # Seconde confirmation
        confirm_msg = "Derniere chance!\n\nTous les produits vont etre supprimes definitivement."
        if result['clear_chantiers']:
            confirm_msg += "\n\nTous les chantiers et marches seront aussi supprimes."
        if result['clear_categories']:
            confirm_msg += "\n\nToutes les categories seront aussi supprimees."
        confirm_msg += "\n\nLes IDs seront reinitialises.\n\nConfirmer la suppression?"

        confirm = messagebox.askyesno("Confirmation DEFINITIVE", confirm_msg)

        if not confirm:
            return

        # Supprimer toutes les donnees
        self.db.clear_all_data(
            clear_categories=result['clear_categories'],
            clear_chantiers=result['clear_chantiers']
        )
        self.refresh_data()

        # Message de confirmation
        elements_supprimes = ["produits"]
        if result['clear_chantiers']:
            elements_supprimes.append("chantiers")
        if result['clear_categories']:
            elements_supprimes.append("categories")

        msg = f"Tous les {', '.join(elements_supprimes)} ont ete supprimes.\nLes IDs ont ete reinitialises."
        self.set_status("Base de donnees videe")
        messagebox.showinfo("Termine", msg)

    # ==================== COPIER-COLLER ====================

    def _create_context_menu(self):
        """Cree le menu contextuel pour le tableau"""
        self.context_menu = tk.Menu(self.root, tearoff=0,
                                    bg=Theme.COLORS['bg_alt'],
                                    fg=Theme.COLORS['text'],
                                    activebackground=Theme.COLORS['primary'],
                                    activeforeground=Theme.COLORS['white'],
                                    bd=1, relief='solid')

        self.context_menu.add_command(label="Copier la designation", command=self._copy_designation)
        self.context_menu.add_command(label="Copier le prix achat", command=self._copy_prix_achat)
        self.context_menu.add_command(label="Copier le prix vente", command=self._copy_prix_vente)
        self.context_menu.add_command(label="Copier la reference", command=self._copy_reference)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Copier toute la ligne", command=lambda: self._copy_row(None))
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Modifier", command=self.on_edit)
        self.context_menu.add_command(label="Supprimer", command=self.on_delete)

    def _show_context_menu(self, event):
        """Affiche le menu contextuel"""
        # Selectionner l'item sous le curseur
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            try:
                self.context_menu.tk_popup(event.x_root, event.y_root)
            finally:
                self.context_menu.grab_release()

    def _copy_to_clipboard(self, text):
        """Copie du texte dans le presse-papiers"""
        self.root.clipboard_clear()
        self.root.clipboard_append(text)
        self.root.update()
        self.set_status(f"Copie: {text[:50]}..." if len(text) > 50 else f"Copie: {text}")

    def _copy_designation(self):
        """Copie la designation du produit selectionne"""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])['values']
        if len(values) > 3:
            self._copy_to_clipboard(str(values[3]))  # designation

    def _copy_prix_achat(self):
        """Copie le prix achat du produit selectionne"""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])['values']
        if len(values) > 6:
            prix = str(values[6]).replace(' EUR', '').replace(',', '.')
            self._copy_to_clipboard(prix)

    def _copy_prix_vente(self):
        """Copie le prix vente du produit selectionne"""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])['values']
        if len(values) > 7:
            prix = str(values[7]).replace(' EUR', '').replace(',', '.')
            self._copy_to_clipboard(prix)

    def _copy_reference(self):
        """Copie la reference du produit selectionne"""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])['values']
        if len(values) > 8:
            self._copy_to_clipboard(str(values[8]))  # reference

    def _copy_row(self, event):
        """Copie toute la ligne au format tabule (pour Excel)"""
        selection = self.tree.selection()
        if not selection:
            return
        values = self.tree.item(selection[0])['values']
        # Exclure les colonnes pdf et devis (vides) - indices 9 et 10
        row_data = [str(v) for v in values[:9]]
        row_text = '\t'.join(row_data)
        self._copy_to_clipboard(row_text)

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
        """Nettoie toutes les icônes affichées (PDF, Devis et Devis rapide)"""
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

        for label in self.cart_labels:
            try:
                label.place_forget()
                label.destroy()
            except:
                pass
        self.cart_labels.clear()

    def _update_all_icons(self):
        """Met à jour toutes les icônes (PDF, Devis et Devis rapide)"""
        # Nettoyer toutes les icônes une seule fois au début
        self._clear_pdf_icons()
        # Recréer toutes les icônes
        self._update_pdf_icons()
        self._update_devis_icons()
        self._update_cart_icons()

    def _update_pdf_icons(self):
        """Met à jour les positions des icônes PDF avec des Labels overlay"""
        if not self.pdf_icon:
            return

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

                    # Vérifier si l'item a le tag 'has_pdf'
                    tags = self.tree.item(item)['tags']
                    if 'has_pdf' in tags:  # A un PDF
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

                    # Vérifier si l'item a le tag 'has_devis'
                    tags = self.tree.item(item)['tags']
                    if 'has_devis' in tags:  # A un devis
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

    # ==================== GESTION DU PANIER ====================

    def _update_cart_icons(self):
        """Met a jour les positions des icones Devis rapide avec des Labels overlay"""
        try:
            tree_height = self.tree.winfo_height()
            tree_width = self.tree.winfo_width()
        except:
            return

        try:
            for item in self.tree.get_children():
                bbox = self.tree.bbox(item, 'cart')
                if bbox:
                    if bbox[1] < 0 or bbox[1] + bbox[3] > tree_height:
                        continue
                    if bbox[0] < 0 or bbox[0] + bbox[2] > tree_width:
                        continue

                    values = self.tree.item(item)['values']
                    product_id = values[0]
                    in_cart = self.cart_manager.is_in_cart(product_id)

                    x = bbox[0] + (bbox[2] - 24) // 2
                    y = bbox[1] + (bbox[3] - 24) // 2 + 1

                    emoji = "\u2713" if in_cart else "+"  # ✓ ou +
                    color = Theme.COLORS['success'] if in_cart else Theme.COLORS['secondary']

                    label = tk.Label(self.tree.master, text=emoji,
                                    font=('Segoe UI', 12, 'bold'),
                                    bg='white', fg=color,
                                    cursor='hand2', bd=0, relief='flat')
                    label.place(x=x, y=y, width=24, height=24)

                    label.bind('<Button-1>', lambda e, i=item: self._on_cart_icon_click(i))

                    self.cart_labels.append(label)

        except Exception as e:
            pass

    def _on_cart_icon_click(self, item):
        """Gere le clic sur une icone Devis rapide"""
        values = self.tree.item(item)['values']
        product_id = values[0]

        produits = self.db.search_produits()
        product = next((p for p in produits if p['id'] == product_id), None)

        if not product:
            return

        if self.cart_manager.is_in_cart(product_id):
            self.cart_manager.remove_from_cart(product_id)
            self.set_status(f"Article retire du devis: {product['designation']}")
        else:
            self.cart_manager.add_to_cart(product)
            self.set_status(f"Article ajoute au devis: {product['designation']}")

        self._update_cart_button()
        self._update_all_icons()

    def _update_cart_button(self):
        """Met a jour le compteur du bouton devis rapide"""
        count = self.cart_manager.get_cart_count()
        self.cart_btn.config(text=f"\U0001F4CB Devis rapide ({count})")

    def _show_cart_panel(self):
        """Affiche le panneau du devis rapide"""
        CartPanel(self.root, self.cart_manager, self.db,
                 on_export_callback=self._on_export_cart)

    def _on_export_cart(self):
        """Lance l'export du devis rapide"""
        dialog = CartExportDialog(self.root, self.cart_manager, self.db)
        self.root.wait_window(dialog)

        if dialog.result:
            response = messagebox.askyesno(
                "Vider le devis",
                "Export termine avec succes!\n\nVoulez-vous vider le devis?"
            )
            if response:
                self.cart_manager.clear_cart()
                self._update_cart_button()
                self.on_search()

    # ==================== FERMETURE ====================

    def on_closing(self):
        """Ferme l'application"""
        # Nettoyer les icônes PDF
        self._clear_pdf_icons()

        self.db.close()
        self.root.destroy()
