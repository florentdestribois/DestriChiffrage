"""
DestriChiffrage - Theme Destribois Modern
==========================================
Style graphique moderne et professionnel
"""

import tkinter as tk
from tkinter import ttk


class Theme:
    """Gestionnaire de theme Destribois moderne"""

    # Palette de couleurs moderne Destribois
    COLORS = {
        # Couleurs principales
        'primary': '#1E293B',           # Slate 800 - Header sombre elegant
        'primary_light': '#334155',     # Slate 700
        'primary_dark': '#0F172A',      # Slate 900

        'secondary': '#B8860B',         # Or Destribois - DarkGoldenrod
        'secondary_light': '#DAA520',   # Goldenrod
        'secondary_dark': '#8B6914',    # Or fonce

        'accent': '#2563EB',            # Bleu moderne
        'accent_light': '#3B82F6',      # Bleu clair
        'accent_dark': '#1D4ED8',       # Bleu fonce

        # Couleurs de fond
        'bg': '#F8FAFC',                # Slate 50 - Fond principal clair
        'bg_alt': '#FFFFFF',            # Blanc pur - Cards
        'bg_dark': '#E2E8F0',           # Slate 200 - Fond secondaire
        'bg_header': '#1E293B',         # Header sombre

        # Couleurs de statut
        'success': '#059669',           # Emerald 600
        'success_light': '#D1FAE5',     # Emerald 100
        'warning': '#D97706',           # Amber 600
        'warning_light': '#FEF3C7',     # Amber 100
        'danger': '#DC2626',            # Red 600
        'danger_light': '#FEE2E2',      # Red 100

        # Couleurs de texte
        'text': '#1E293B',              # Slate 800
        'text_light': '#64748B',        # Slate 500
        'text_muted': '#94A3B8',        # Slate 400
        'white': '#FFFFFF',

        # Bordures
        'border': '#E2E8F0',            # Slate 200
        'border_light': '#F1F5F9',      # Slate 100
        'border_focus': '#2563EB',      # Bleu accent
    }

    # Polices modernes
    FONTS = {
        'title': ('Segoe UI', 22, 'bold'),
        'heading': ('Segoe UI', 14, 'bold'),
        'subheading': ('Segoe UI Semibold', 11),
        'body': ('Segoe UI', 10),
        'body_bold': ('Segoe UI Semibold', 10),
        'small': ('Segoe UI', 9),
        'small_bold': ('Segoe UI Semibold', 9),
        'tiny': ('Segoe UI', 8),
        'mono': ('Consolas', 10),
        'mono_bold': ('Consolas', 10, 'bold'),
        'data': ('Consolas', 11),
    }

    @classmethod
    def apply(cls, root: tk.Tk):
        """Applique le theme moderne"""
        style = ttk.Style()
        style.theme_use('clam')

        # Fond fenetre principale
        root.configure(bg=cls.COLORS['bg'])

        # Configuration generale
        style.configure('.', font=cls.FONTS['body'], background=cls.COLORS['bg'])

        # Frame
        style.configure('TFrame', background=cls.COLORS['bg'])
        style.configure('Card.TFrame', background=cls.COLORS['bg_alt'])
        style.configure('Header.TFrame', background=cls.COLORS['primary'])
        style.configure('Dark.TFrame', background=cls.COLORS['primary'])

        # Labels
        style.configure('TLabel',
                       background=cls.COLORS['bg'],
                       foreground=cls.COLORS['text'])

        style.configure('Title.TLabel',
                       font=cls.FONTS['title'],
                       foreground=cls.COLORS['primary'])

        style.configure('Heading.TLabel',
                       font=cls.FONTS['heading'],
                       foreground=cls.COLORS['primary'])

        style.configure('Subheading.TLabel',
                       font=cls.FONTS['subheading'],
                       foreground=cls.COLORS['text_light'])

        style.configure('Small.TLabel',
                       font=cls.FONTS['small'],
                       foreground=cls.COLORS['text_light'])

        style.configure('White.TLabel',
                       foreground=cls.COLORS['white'],
                       background=cls.COLORS['primary'])

        style.configure('Muted.TLabel',
                       foreground=cls.COLORS['text_muted'])

        # Boutons modernes
        style.configure('TButton',
                       font=cls.FONTS['body'],
                       padding=(16, 8),
                       background=cls.COLORS['bg_dark'],
                       foreground=cls.COLORS['text'])

        style.map('TButton',
                 background=[('active', cls.COLORS['border'])])

        # Bouton Primary (bleu)
        style.configure('Primary.TButton',
                       background=cls.COLORS['accent'],
                       foreground=cls.COLORS['white'],
                       font=cls.FONTS['body_bold'],
                       padding=(20, 10))
        style.map('Primary.TButton',
                 background=[('active', cls.COLORS['accent_light']),
                           ('pressed', cls.COLORS['accent_dark'])])

        # Bouton Secondary (or)
        style.configure('Secondary.TButton',
                       background=cls.COLORS['secondary'],
                       foreground=cls.COLORS['white'],
                       font=cls.FONTS['body_bold'])
        style.map('Secondary.TButton',
                 background=[('active', cls.COLORS['secondary_light']),
                           ('pressed', cls.COLORS['secondary_dark'])])

        # Bouton Success
        style.configure('Success.TButton',
                       background=cls.COLORS['success'],
                       foreground=cls.COLORS['white'],
                       font=cls.FONTS['body_bold'])
        style.map('Success.TButton',
                 background=[('active', '#10B981')])

        # Bouton Danger
        style.configure('Danger.TButton',
                       background=cls.COLORS['danger'],
                       foreground=cls.COLORS['white'])
        style.map('Danger.TButton',
                 background=[('active', '#EF4444')])

        # Bouton Ghost (transparent)
        style.configure('Ghost.TButton',
                       background=cls.COLORS['bg'],
                       foreground=cls.COLORS['text_light'])
        style.map('Ghost.TButton',
                 background=[('active', cls.COLORS['bg_dark'])])

        # Entry (champs de saisie)
        style.configure('TEntry',
                       padding=10,
                       fieldbackground=cls.COLORS['bg_alt'],
                       bordercolor=cls.COLORS['border'],
                       lightcolor=cls.COLORS['border'])

        style.map('TEntry',
                 bordercolor=[('focus', cls.COLORS['accent'])])

        # Combobox
        style.configure('TCombobox',
                       padding=10,
                       fieldbackground=cls.COLORS['bg_alt'],
                       bordercolor=cls.COLORS['border'])

        style.map('TCombobox',
                 fieldbackground=[('readonly', cls.COLORS['bg_alt'])],
                 bordercolor=[('focus', cls.COLORS['accent'])])

        # Treeview moderne
        style.configure('Treeview',
                       background=cls.COLORS['bg_alt'],
                       foreground=cls.COLORS['text'],
                       fieldbackground=cls.COLORS['bg_alt'],
                       rowheight=40,
                       font=cls.FONTS['body'],
                       borderwidth=0)

        style.configure('Treeview.Heading',
                       background=cls.COLORS['bg_dark'],
                       foreground=cls.COLORS['text'],
                       font=cls.FONTS['small_bold'],
                       padding=12,
                       borderwidth=0)

        style.map('Treeview.Heading',
                 background=[('active', cls.COLORS['border'])])

        style.map('Treeview',
                 background=[('selected', cls.COLORS['accent'])],
                 foreground=[('selected', cls.COLORS['white'])])

        # LabelFrame
        style.configure('TLabelframe',
                       background=cls.COLORS['bg_alt'],
                       bordercolor=cls.COLORS['border'])

        style.configure('TLabelframe.Label',
                       font=cls.FONTS['subheading'],
                       foreground=cls.COLORS['text_light'],
                       background=cls.COLORS['bg_alt'])

        # Notebook (onglets)
        style.configure('TNotebook',
                       background=cls.COLORS['bg'],
                       borderwidth=0,
                       tabmargins=[0, 0, 0, 0])

        style.configure('TNotebook.Tab',
                       padding=(20, 10),
                       font=cls.FONTS['body'],
                       background=cls.COLORS['bg'],
                       foreground=cls.COLORS['text_light'])

        style.map('TNotebook.Tab',
                 background=[('selected', cls.COLORS['bg_alt'])],
                 foreground=[('selected', cls.COLORS['text'])])

        # Scrollbar moderne
        style.configure('Vertical.TScrollbar',
                       background=cls.COLORS['border'],
                       troughcolor=cls.COLORS['bg_alt'],
                       arrowcolor=cls.COLORS['text_muted'],
                       borderwidth=0,
                       width=10)

        style.configure('Horizontal.TScrollbar',
                       background=cls.COLORS['border'],
                       troughcolor=cls.COLORS['bg_alt'],
                       borderwidth=0,
                       width=10)

        # Progressbar
        style.configure('TProgressbar',
                       background=cls.COLORS['accent'],
                       troughcolor=cls.COLORS['bg_dark'])

        # Separator
        style.configure('TSeparator',
                       background=cls.COLORS['border'])

        # Checkbutton / Radiobutton
        style.configure('TCheckbutton',
                       background=cls.COLORS['bg'],
                       foreground=cls.COLORS['text'])

        style.configure('TRadiobutton',
                       background=cls.COLORS['bg'],
                       foreground=cls.COLORS['text'])

        return style

    @classmethod
    def get_color(cls, name: str) -> str:
        """Recupere une couleur par son nom"""
        return cls.COLORS.get(name, cls.COLORS['text'])

    @classmethod
    def get_font(cls, name: str) -> tuple:
        """Recupere une police par son nom"""
        return cls.FONTS.get(name, cls.FONTS['body'])

    # =========================================================================
    # FACTORY METHODS - Composants réutilisables
    # =========================================================================

    @classmethod
    def create_header(cls, parent, title: str, height: int = 60,
                      icon: str = None, subtitle: str = None) -> tk.Frame:
        """
        Crée un header de fenêtre stylisé.

        Args:
            parent: Widget parent
            title: Titre principal
            height: Hauteur du header (défaut: 60)
            icon: Emoji/icône optionnel avant le titre
            subtitle: Sous-titre optionnel

        Returns:
            tk.Frame: Le frame header configuré
        """
        header = tk.Frame(parent, bg=cls.COLORS['primary'], height=height)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        # Container pour le contenu
        content = tk.Frame(header, bg=cls.COLORS['primary'])
        content.pack(fill=tk.BOTH, expand=True, padx=20)

        # Titre avec icône optionnelle
        title_text = f"{icon} {title}" if icon else title
        title_label = tk.Label(
            content,
            text=title_text,
            font=cls.FONTS['heading'],
            bg=cls.COLORS['primary'],
            fg=cls.COLORS['white']
        )
        title_label.pack(side=tk.LEFT, pady=10 if not subtitle else 5)

        # Sous-titre optionnel
        if subtitle:
            subtitle_label = tk.Label(
                content,
                text=subtitle,
                font=cls.FONTS['small'],
                bg=cls.COLORS['primary'],
                fg=cls.COLORS['text_muted']
            )
            subtitle_label.pack(side=tk.LEFT, padx=(10, 0), pady=5)

        return header

    @classmethod
    def create_card(cls, parent, padx: int = 20, pady: int = 16,
                    bg: str = None, border: bool = True) -> tk.Frame:
        """
        Crée une card avec bordure optionnelle.

        Args:
            parent: Widget parent
            padx: Padding horizontal interne (défaut: 20)
            pady: Padding vertical interne (défaut: 16)
            bg: Couleur de fond (défaut: bg_alt)
            border: Afficher la bordure (défaut: True)

        Returns:
            tk.Frame: Le frame card configuré
        """
        bg_color = bg or cls.COLORS['bg_alt']

        card = tk.Frame(
            parent,
            bg=bg_color,
            padx=padx,
            pady=pady,
            highlightbackground=cls.COLORS['border'] if border else bg_color,
            highlightthickness=1 if border else 0
        )

        return card

    @classmethod
    def create_button(cls, parent, text: str, command=None,
                      style: str = 'primary', icon: str = None,
                      padx: int = None, pady: int = None,
                      width: int = None) -> tk.Button:
        """
        Crée un bouton stylisé.

        Args:
            parent: Widget parent
            text: Texte du bouton
            command: Fonction à appeler au clic
            style: Style du bouton ('primary', 'secondary', 'success', 'danger', 'ghost')
            icon: Emoji/icône optionnel avant le texte
            padx: Padding horizontal (défaut selon style)
            pady: Padding vertical (défaut selon style)
            width: Largeur fixe optionnelle

        Returns:
            tk.Button: Le bouton configuré
        """
        # Configuration par style
        styles = {
            'primary': {
                'bg': cls.COLORS['accent'],
                'fg': cls.COLORS['white'],
                'active_bg': cls.COLORS['accent_light'],
                'font': cls.FONTS['body_bold'],
                'padx': 20,
                'pady': 10
            },
            'secondary': {
                'bg': cls.COLORS['secondary'],
                'fg': cls.COLORS['white'],
                'active_bg': cls.COLORS['secondary_light'],
                'font': cls.FONTS['body_bold'],
                'padx': 16,
                'pady': 8
            },
            'success': {
                'bg': cls.COLORS['success'],
                'fg': cls.COLORS['white'],
                'active_bg': '#10B981',
                'font': cls.FONTS['body_bold'],
                'padx': 16,
                'pady': 8
            },
            'danger': {
                'bg': cls.COLORS['danger'],
                'fg': cls.COLORS['white'],
                'active_bg': '#EF4444',
                'font': cls.FONTS['body'],
                'padx': 15,
                'pady': 8
            },
            'ghost': {
                'bg': cls.COLORS['bg'],
                'fg': cls.COLORS['text_light'],
                'active_bg': cls.COLORS['bg_dark'],
                'font': cls.FONTS['body'],
                'padx': 12,
                'pady': 6
            }
        }

        config = styles.get(style, styles['primary'])
        button_text = f"{icon} {text}" if icon else text

        btn = tk.Button(
            parent,
            text=button_text,
            command=command,
            font=config['font'],
            bg=config['bg'],
            fg=config['fg'],
            activebackground=config['active_bg'],
            activeforeground=config['fg'],
            bd=0,
            padx=padx or config['padx'],
            pady=pady or config['pady'],
            cursor='hand2',
            relief='flat'
        )

        if width:
            btn.configure(width=width)

        # Effet hover
        def on_enter(e):
            btn.configure(bg=config['active_bg'])

        def on_leave(e):
            btn.configure(bg=config['bg'])

        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    @classmethod
    def create_label(cls, parent, text: str, style: str = 'body',
                     bg: str = None, fg: str = None,
                     icon: str = None) -> tk.Label:
        """
        Crée un label stylisé.

        Args:
            parent: Widget parent
            text: Texte du label
            style: Style du label ('title', 'heading', 'subheading', 'body', 'small', 'muted')
            bg: Couleur de fond (défaut selon contexte)
            fg: Couleur du texte (défaut selon style)
            icon: Emoji/icône optionnel avant le texte

        Returns:
            tk.Label: Le label configuré
        """
        # Configuration par style
        styles = {
            'title': {
                'font': cls.FONTS['title'],
                'fg': cls.COLORS['primary']
            },
            'heading': {
                'font': cls.FONTS['heading'],
                'fg': cls.COLORS['primary']
            },
            'heading_white': {
                'font': cls.FONTS['heading'],
                'fg': cls.COLORS['white'],
                'bg': cls.COLORS['primary']
            },
            'subheading': {
                'font': cls.FONTS['subheading'],
                'fg': cls.COLORS['text_light']
            },
            'body': {
                'font': cls.FONTS['body'],
                'fg': cls.COLORS['text']
            },
            'body_bold': {
                'font': cls.FONTS['body_bold'],
                'fg': cls.COLORS['text']
            },
            'small': {
                'font': cls.FONTS['small'],
                'fg': cls.COLORS['text_light']
            },
            'muted': {
                'font': cls.FONTS['small'],
                'fg': cls.COLORS['text_muted']
            },
            'data': {
                'font': cls.FONTS['data'],
                'fg': cls.COLORS['text']
            }
        }

        config = styles.get(style, styles['body'])
        label_text = f"{icon} {text}" if icon else text

        label = tk.Label(
            parent,
            text=label_text,
            font=config['font'],
            bg=bg or config.get('bg', cls.COLORS['bg']),
            fg=fg or config['fg']
        )

        return label

    @classmethod
    def create_entry(cls, parent, textvariable=None, placeholder: str = None,
                     width: int = None, state: str = 'normal') -> tk.Entry:
        """
        Crée un champ de saisie stylisé.

        Args:
            parent: Widget parent
            textvariable: Variable Tkinter associée
            placeholder: Texte indicatif (non supporté nativement, simulé)
            width: Largeur en caractères
            state: État du champ ('normal', 'disabled', 'readonly')

        Returns:
            tk.Entry: Le champ de saisie configuré
        """
        entry = tk.Entry(
            parent,
            textvariable=textvariable,
            font=cls.FONTS['body'],
            bg=cls.COLORS['bg_alt'],
            fg=cls.COLORS['text'],
            disabledbackground=cls.COLORS['bg_dark'],
            disabledforeground=cls.COLORS['text_muted'],
            insertbackground=cls.COLORS['text'],
            selectbackground=cls.COLORS['accent'],
            selectforeground=cls.COLORS['white'],
            bd=1,
            relief='solid',
            highlightthickness=1,
            highlightbackground=cls.COLORS['border'],
            highlightcolor=cls.COLORS['accent'],
            state=state
        )

        if width:
            entry.configure(width=width)

        # Gestion du placeholder
        if placeholder and not textvariable:
            entry.insert(0, placeholder)
            entry.configure(fg=cls.COLORS['text_muted'])

            def on_focus_in(e):
                if entry.get() == placeholder:
                    entry.delete(0, tk.END)
                    entry.configure(fg=cls.COLORS['text'])

            def on_focus_out(e):
                if not entry.get():
                    entry.insert(0, placeholder)
                    entry.configure(fg=cls.COLORS['text_muted'])

            entry.bind('<FocusIn>', on_focus_in)
            entry.bind('<FocusOut>', on_focus_out)

        return entry

    @classmethod
    def create_treeview(cls, parent, columns: list, headings: dict = None,
                        show: str = 'headings', height: int = 10,
                        selectmode: str = 'browse',
                        with_scrollbar: bool = True) -> tuple:
        """
        Crée un Treeview stylisé avec scrollbar optionnelle.

        Args:
            parent: Widget parent
            columns: Liste des identifiants de colonnes
            headings: Dict {column_id: heading_text} pour les en-têtes
            show: Mode d'affichage ('headings', 'tree', 'tree headings')
            height: Nombre de lignes visibles
            selectmode: Mode de sélection ('browse', 'extended', 'none')
            with_scrollbar: Inclure une scrollbar verticale

        Returns:
            tuple: (container_frame, treeview, scrollbar ou None)
        """
        # Container
        container = tk.Frame(parent, bg=cls.COLORS['bg_alt'])

        # Treeview
        tree = ttk.Treeview(
            container,
            columns=columns,
            show=show,
            height=height,
            selectmode=selectmode
        )

        # Configuration des en-têtes
        if headings:
            for col_id, heading_text in headings.items():
                tree.heading(col_id, text=heading_text)

        scrollbar = None
        if with_scrollbar:
            scrollbar = ttk.Scrollbar(
                container,
                orient=tk.VERTICAL,
                command=tree.yview
            )
            tree.configure(yscrollcommand=scrollbar.set)

            tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        else:
            tree.pack(fill=tk.BOTH, expand=True)

        return container, tree, scrollbar

    @classmethod
    def create_separator(cls, parent, orient: str = 'horizontal',
                         color: str = None) -> tk.Frame:
        """
        Crée un séparateur visuel.

        Args:
            parent: Widget parent
            orient: Orientation ('horizontal' ou 'vertical')
            color: Couleur du séparateur (défaut: border)

        Returns:
            tk.Frame: Le séparateur
        """
        sep_color = color or cls.COLORS['border']

        if orient == 'horizontal':
            sep = tk.Frame(parent, bg=sep_color, height=1)
        else:
            sep = tk.Frame(parent, bg=sep_color, width=1)

        return sep

    @classmethod
    def create_status_badge(cls, parent, text: str,
                            status: str = 'info') -> tk.Label:
        """
        Crée un badge de statut coloré.

        Args:
            parent: Widget parent
            text: Texte du badge
            status: Type de statut ('success', 'warning', 'danger', 'info')

        Returns:
            tk.Label: Le badge configuré
        """
        status_config = {
            'success': {
                'bg': cls.COLORS['success_light'],
                'fg': cls.COLORS['success']
            },
            'warning': {
                'bg': cls.COLORS['warning_light'],
                'fg': cls.COLORS['warning']
            },
            'danger': {
                'bg': cls.COLORS['danger_light'],
                'fg': cls.COLORS['danger']
            },
            'info': {
                'bg': '#DBEAFE',
                'fg': cls.COLORS['accent']
            }
        }

        config = status_config.get(status, status_config['info'])

        badge = tk.Label(
            parent,
            text=f" {text} ",
            font=cls.FONTS['small_bold'],
            bg=config['bg'],
            fg=config['fg'],
            padx=8,
            pady=2
        )

        return badge

    @classmethod
    def create_tooltip(cls, widget, text: str, delay: int = 500):
        """
        Ajoute un tooltip à un widget.

        Args:
            widget: Widget auquel attacher le tooltip
            text: Texte du tooltip
            delay: Délai avant affichage en ms (défaut: 500)
        """
        tooltip = None
        after_id = None

        def show_tooltip(event):
            nonlocal tooltip, after_id

            def display():
                nonlocal tooltip
                x = widget.winfo_rootx() + 20
                y = widget.winfo_rooty() + widget.winfo_height() + 5

                tooltip = tk.Toplevel(widget)
                tooltip.wm_overrideredirect(True)
                tooltip.wm_geometry(f"+{x}+{y}")

                label = tk.Label(
                    tooltip,
                    text=text,
                    font=cls.FONTS['small'],
                    bg=cls.COLORS['primary_dark'],
                    fg=cls.COLORS['white'],
                    padx=8,
                    pady=4,
                    relief='solid',
                    borderwidth=1
                )
                label.pack()

            after_id = widget.after(delay, display)

        def hide_tooltip(event):
            nonlocal tooltip, after_id
            if after_id:
                widget.after_cancel(after_id)
                after_id = None
            if tooltip:
                tooltip.destroy()
                tooltip = None

        widget.bind('<Enter>', show_tooltip)
        widget.bind('<Leave>', hide_tooltip)
