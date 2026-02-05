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
