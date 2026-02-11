"""
DestriChiffrage - Vue CAO (SolidWorks / SWOOD)
==============================================
Interface pour l'import/export de materiaux SWOOD et Optiplanning
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
from datetime import datetime
from typing import Optional, Callable

# Import du theme
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme

# Import des fonctions d'export depuis le plug-in
HAS_EXPORT_MODULE = False
IMPORT_ERROR = ""

# Methode 1: Import direct (fonctionne si PyInstaller a inclus le module)
try:
    from export_optiplanning import (
        export_optiplanning_txt,
        export_xml_boards_nesting,
        export_xml_materials,
        export_xml_edgebands
    )
    HAS_EXPORT_MODULE = True
except ImportError:
    pass

# Methode 2: Import via chemin (mode developpement)
if not HAS_EXPORT_MODULE:
    try:
        # Determiner le chemin de base
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        plugin_path = os.path.join(base_path, 'Plug-in', 'Export optiplanning')
        if plugin_path not in sys.path:
            sys.path.insert(0, plugin_path)

        from export_optiplanning import (
            export_optiplanning_txt,
            export_xml_boards_nesting,
            export_xml_materials,
            export_xml_edgebands
        )
        HAS_EXPORT_MODULE = True
    except ImportError as e:
        IMPORT_ERROR = str(e)


class CAOView:
    """Vue principale CAO - Integration SolidWorks / SWOOD"""

    def __init__(self, parent, db, on_close_callback: Optional[Callable] = None):
        self.db = db
        self.parent = parent
        self.on_close_callback = on_close_callback

        # Creer la fenetre Toplevel
        self.window = tk.Toplevel(parent)
        self.window.title("CAO - Import/Export SolidWorks & SWOOD")
        self.window.geometry("950x920")
        self.window.minsize(900, 900)
        self.window.configure(bg=Theme.COLORS['bg'])

        # Centrer la fenetre
        self.window.update_idletasks()
        x = (self.window.winfo_screenwidth() - 850) // 2
        y = (self.window.winfo_screenheight() - 700) // 2
        self.window.geometry(f"+{x}+{y}")

        # Gerer la fermeture
        self.window.protocol("WM_DELETE_WINDOW", self._on_close)

        # Variables
        self.xlsm_path_var = tk.StringVar()
        self.output_dir_var = tk.StringVar()

        # Construction de l'interface
        self._create_widgets()

        # Rechercher le fichier XLSM par defaut
        self._find_default_xlsm()

    def _create_widgets(self):
        """Cree les widgets de la vue"""
        # Header
        self._create_header()

        # Separateur or
        tk.Frame(self.window, bg=Theme.COLORS['secondary'], height=3).pack(fill=tk.X)

        # Contenu principal avec notebook (onglets)
        self._create_main_content()

        # Barre de statut
        self._create_status_bar()

    def _create_header(self):
        """Cree le header de la fenetre"""
        header = tk.Frame(self.window, bg=Theme.COLORS['primary'], height=70)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        header_content = tk.Frame(header, bg=Theme.COLORS['primary'])
        header_content.pack(fill=tk.BOTH, expand=True, padx=24, pady=12)

        # Icone CAO
        icon_label = tk.Label(header_content, text="",
                             font=('Segoe UI', 28),
                             fg=Theme.COLORS['secondary'],
                             bg=Theme.COLORS['primary'])
        icon_label.pack(side=tk.LEFT, padx=(0, 12))

        # Titre
        title_frame = tk.Frame(header_content, bg=Theme.COLORS['primary'])
        title_frame.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(title_frame, text="CAO - SolidWorks & SWOOD",
                font=Theme.FONTS['heading'],
                fg=Theme.COLORS['white'],
                bg=Theme.COLORS['primary']).pack(anchor=tk.W)

        tk.Label(title_frame, text="Import/Export de materiaux pour Optiplanning et SWOOD",
                font=Theme.FONTS['small'],
                fg=Theme.COLORS['text_muted'],
                bg=Theme.COLORS['primary']).pack(anchor=tk.W)

        # Bouton fermer a droite
        close_btn = tk.Button(header_content, text="Fermer",
                             font=Theme.FONTS['body'],
                             fg=Theme.COLORS['white'],
                             bg=Theme.COLORS['primary_light'],
                             activebackground=Theme.COLORS['primary_dark'],
                             activeforeground=Theme.COLORS['white'],
                             bd=0, padx=16, pady=6, cursor="hand2",
                             command=self._on_close)
        close_btn.pack(side=tk.RIGHT)

    def _create_main_content(self):
        """Cree le contenu principal avec onglets"""
        main_frame = tk.Frame(self.window, bg=Theme.COLORS['bg'])
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=12)

        # Notebook pour les onglets
        style = ttk.Style()
        style.configure('CAO.TNotebook', background=Theme.COLORS['bg'])
        style.configure('CAO.TNotebook.Tab',
                       font=Theme.FONTS['body_bold'],
                       padding=(16, 8))

        self.notebook = ttk.Notebook(main_frame, style='CAO.TNotebook')
        self.notebook.pack(fill=tk.BOTH, expand=True)

        # Onglet Export SWOOD
        self._create_export_tab()

        # Onglet Import Materiaux (futur)
        self._create_import_tab()

    def _create_export_tab(self):
        """Cree l'onglet d'export SWOOD/Optiplanning"""
        export_frame = tk.Frame(self.notebook, bg=Theme.COLORS['bg'])
        self.notebook.add(export_frame, text="  Export SWOOD  ")

        # Verifier si le module d'export est disponible
        if not HAS_EXPORT_MODULE:
            error_frame = tk.Frame(export_frame, bg=Theme.COLORS['bg'])
            error_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=40)

            tk.Label(error_frame, text="Module d'export non disponible",
                    font=Theme.FONTS['heading'],
                    fg=Theme.COLORS['danger'],
                    bg=Theme.COLORS['bg']).pack()

            tk.Label(error_frame, text=f"Erreur: {IMPORT_ERROR}",
                    font=Theme.FONTS['body'],
                    fg=Theme.COLORS['text_muted'],
                    bg=Theme.COLORS['bg']).pack(pady=10)

            tk.Label(error_frame, text="Verifiez que le plug-in DestriImport est present dans le dossier Plug-in/",
                    font=Theme.FONTS['small'],
                    fg=Theme.COLORS['text_light'],
                    bg=Theme.COLORS['bg']).pack()
            return

        # Card: Fichier source XLSM
        src_card = self._create_card(export_frame, "Fichier source XLSM")

        src_path_frame = tk.Frame(src_card, bg=Theme.COLORS['bg_alt'])
        src_path_frame.pack(fill=tk.X, pady=(8, 0))

        self.xlsm_entry = tk.Entry(src_path_frame, textvariable=self.xlsm_path_var,
                                   font=Theme.FONTS['small'],
                                   bg=Theme.COLORS['bg_alt'],
                                   fg=Theme.COLORS['text'],
                                   bd=1, relief="solid",
                                   highlightbackground=Theme.COLORS['border'],
                                   highlightcolor=Theme.COLORS['accent'],
                                   highlightthickness=1)
        self.xlsm_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        browse_src_btn = tk.Button(src_path_frame, text="Parcourir",
                                   font=Theme.FONTS['small'],
                                   bg=Theme.COLORS['bg_dark'],
                                   fg=Theme.COLORS['text'],
                                   activebackground=Theme.COLORS['border'],
                                   bd=0, padx=12, pady=6, cursor="hand2",
                                   command=self._browse_xlsm)
        browse_src_btn.pack(side=tk.RIGHT, padx=(8, 0))

        # Card: Dossier de destination
        dst_card = self._create_card(export_frame, "Dossier de destination")

        dst_path_frame = tk.Frame(dst_card, bg=Theme.COLORS['bg_alt'])
        dst_path_frame.pack(fill=tk.X, pady=(8, 0))

        self.output_entry = tk.Entry(dst_path_frame, textvariable=self.output_dir_var,
                                     font=Theme.FONTS['small'],
                                     bg=Theme.COLORS['bg_alt'],
                                     fg=Theme.COLORS['text'],
                                     bd=1, relief="solid",
                                     highlightbackground=Theme.COLORS['border'],
                                     highlightcolor=Theme.COLORS['accent'],
                                     highlightthickness=1)
        self.output_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)

        browse_dst_btn = tk.Button(dst_path_frame, text="Parcourir",
                                   font=Theme.FONTS['small'],
                                   bg=Theme.COLORS['bg_dark'],
                                   fg=Theme.COLORS['text'],
                                   activebackground=Theme.COLORS['border'],
                                   bd=0, padx=12, pady=6, cursor="hand2",
                                   command=self._browse_output)
        browse_dst_btn.pack(side=tk.RIGHT, padx=(8, 0))

        tk.Label(dst_card, text="(vide = meme dossier que le fichier XLSM)",
                font=Theme.FONTS['tiny'],
                fg=Theme.COLORS['text_muted'],
                bg=Theme.COLORS['bg_alt']).pack(anchor=tk.W, pady=(4, 0))

        # Card: Exports disponibles
        export_card = self._create_card(export_frame, "Exports disponibles")

        # Stocker les boutons pour les activer/desactiver
        self.export_buttons = []

        # Bouton 1: TXT Optiplanning
        self.export_buttons.append(
            self._create_export_button(export_card,
                "Export TXT Optiplanning",
                "8 colonnes tab-delimited - Page Materials",
                Theme.COLORS['accent'],
                Theme.COLORS['accent_light'],
                self._do_export_txt)
        )

        # Bouton 2: XML Plaques Nesting
        self.export_buttons.append(
            self._create_export_button(export_card,
                "Export XML Plaques Nesting",
                "Boards pour SWOOD Nesting - Page Materials",
                Theme.COLORS['secondary'],
                Theme.COLORS['secondary_light'],
                self._do_export_nesting)
        )

        # Bouton 3: XML Materiaux SWOOD
        self.export_buttons.append(
            self._create_export_button(export_card,
                "Export XML Materiaux SWOOD",
                "Materiaux complets 49 colonnes - Page Materials",
                Theme.COLORS['primary'],
                Theme.COLORS['primary_light'],
                self._do_export_materials)
        )

        # Bouton 4: XML Chants
        self.export_buttons.append(
            self._create_export_button(export_card,
                "Export XML Chants (EdgeBands)",
                "Chants pour SWOOD - Page EdgeBands",
                Theme.COLORS['secondary_dark'],
                '#A08B66',
                self._do_export_edgebands)
        )

        # Card: Journal
        log_card = self._create_card(export_frame, "Journal", expand=True)

        self.log_text = tk.Text(log_card, font=Theme.FONTS['mono'], height=8,
                               bg=Theme.COLORS['bg'],
                               fg=Theme.COLORS['text'],
                               relief="solid", borderwidth=1,
                               highlightbackground=Theme.COLORS['border'],
                               highlightthickness=0,
                               insertbackground=Theme.COLORS['text'],
                               selectbackground=Theme.COLORS['accent'],
                               selectforeground=Theme.COLORS['white'])
        self.log_text.pack(fill=tk.BOTH, expand=True, pady=(8, 0))

        self._log("Pret. Selectionnez un fichier XLSM et choisissez un export.")

    def _create_import_tab(self):
        """Cree l'onglet d'import materiaux (futur)"""
        import_frame = tk.Frame(self.notebook, bg=Theme.COLORS['bg'])
        self.notebook.add(import_frame, text="  Import Materiaux  ")

        # Message placeholder pour la future fonctionnalite
        placeholder_frame = tk.Frame(import_frame, bg=Theme.COLORS['bg'])
        placeholder_frame.pack(fill=tk.BOTH, expand=True, padx=40, pady=60)

        tk.Label(placeholder_frame, text="Import Materiaux",
                font=Theme.FONTS['heading'],
                fg=Theme.COLORS['primary'],
                bg=Theme.COLORS['bg']).pack()

        tk.Label(placeholder_frame, text="Fonctionnalite a venir",
                font=Theme.FONTS['subheading'],
                fg=Theme.COLORS['text_muted'],
                bg=Theme.COLORS['bg']).pack(pady=(8, 20))

        info_text = """Cette fonctionnalite permettra de :

- Importer des materiaux depuis les fichiers SWOOD/Optiplanning
- Synchroniser les materiaux avec le catalogue DestriChiffrage
- Mettre a jour automatiquement les prix depuis SolidWorks
- Creer des liaisons entre les produits CAO et la base de donnees

Un lien sera etabli entre le plug-in DestriImport et la base de donnees
catalogue.db pour une gestion integree des materiaux."""

        tk.Label(placeholder_frame, text=info_text,
                font=Theme.FONTS['body'],
                fg=Theme.COLORS['text_light'],
                bg=Theme.COLORS['bg'],
                justify=tk.LEFT).pack(pady=10)

        # Badge "A venir"
        badge_frame = tk.Frame(placeholder_frame, bg=Theme.COLORS['warning_light'],
                              padx=12, pady=6)
        badge_frame.pack(pady=20)

        tk.Label(badge_frame, text="Developpement prevu - Phase 2",
                font=Theme.FONTS['small_bold'],
                fg=Theme.COLORS['warning'],
                bg=Theme.COLORS['warning_light']).pack()

    def _create_card(self, parent, title: str, expand: bool = False) -> tk.Frame:
        """Cree une card avec titre"""
        card = tk.Frame(parent, bg=Theme.COLORS['bg_alt'], padx=16, pady=12,
                       highlightbackground=Theme.COLORS['border'],
                       highlightthickness=1)
        if expand:
            card.pack(fill=tk.BOTH, expand=True, pady=(0, 8))
        else:
            card.pack(fill=tk.X, pady=(0, 8))

        tk.Label(card, text=title,
                font=Theme.FONTS['body_bold'],
                fg=Theme.COLORS['text'],
                bg=Theme.COLORS['bg_alt']).pack(anchor=tk.W)

        return card

    def _create_export_button(self, parent, text: str, subtitle: str,
                              bg_color: str, hover_color: str,
                              command: Callable) -> tk.Button:
        """Cree un bouton d'export avec sous-titre"""
        frame = tk.Frame(parent, bg=Theme.COLORS['bg_alt'])
        frame.pack(fill=tk.X, pady=3)

        btn = tk.Button(frame, text=text, command=command,
                       font=Theme.FONTS['body_bold'],
                       bg=bg_color,
                       fg=Theme.COLORS['white'],
                       activebackground=hover_color,
                       activeforeground=Theme.COLORS['white'],
                       bd=0, padx=16, pady=10, cursor="hand2",
                       anchor=tk.W)
        btn.pack(side=tk.LEFT, fill=tk.X, expand=True)

        lbl = tk.Label(frame, text=subtitle,
                      font=Theme.FONTS['tiny'],
                      fg=Theme.COLORS['text_muted'],
                      bg=Theme.COLORS['bg_alt'])
        lbl.pack(side=tk.RIGHT, padx=(8, 0))

        # Hover effect
        def on_enter(e):
            btn.configure(bg=hover_color)
        def on_leave(e):
            btn.configure(bg=bg_color)
        btn.bind('<Enter>', on_enter)
        btn.bind('<Leave>', on_leave)

        return btn

    def _create_status_bar(self):
        """Cree la barre de statut"""
        self.status_bar = tk.Frame(self.window, bg=Theme.COLORS['primary'], height=32)
        self.status_bar.pack(fill=tk.X, side=tk.BOTTOM)
        self.status_bar.pack_propagate(False)

        self.status_var = tk.StringVar(value="Pret")
        self.status_label = tk.Label(self.status_bar, textvariable=self.status_var,
                                    font=Theme.FONTS['small'],
                                    fg=Theme.COLORS['white'],
                                    bg=Theme.COLORS['primary'],
                                    anchor=tk.W, padx=16)
        self.status_label.pack(fill=tk.BOTH, expand=True)

    def _find_default_xlsm(self):
        """Recherche le fichier XLSM par defaut"""
        # Determiner le chemin de base (exe compile ou mode dev)
        if getattr(sys, 'frozen', False):
            base_path = sys._MEIPASS
        else:
            base_path = os.path.dirname(os.path.dirname(os.path.dirname(__file__)))

        # Chercher dans le dossier du plug-in
        plugin_path = os.path.join(base_path, 'Plug-in', 'Export optiplanning')

        candidate = os.path.join(plugin_path, "Liste_panneaux_et_chants.xlsm")
        if os.path.exists(candidate):
            self.xlsm_path_var.set(candidate)
            return

        # Chercher dans le dossier courant
        for root_dir in [plugin_path, os.getcwd()]:
            if os.path.exists(root_dir):
                try:
                    for f in os.listdir(root_dir):
                        if f.endswith(".xlsm") and "backup" not in f.lower() and "copie" not in f.lower():
                            self.xlsm_path_var.set(os.path.join(root_dir, f))
                            return
                except OSError:
                    pass

    def _browse_xlsm(self):
        """Ouvre le dialogue de selection du fichier XLSM"""
        path = filedialog.askopenfilename(
            parent=self.window,
            title="Selectionner le fichier XLSM",
            filetypes=[("Fichiers Excel Macro", "*.xlsm"), ("Tous les fichiers", "*.*")]
        )
        if path:
            self.xlsm_path_var.set(path)

    def _browse_output(self):
        """Ouvre le dialogue de selection du dossier de destination"""
        folder = filedialog.askdirectory(
            parent=self.window,
            title="Selectionner le dossier de destination"
        )
        if folder:
            self.output_dir_var.set(folder)

    def _log(self, msg: str):
        """Ajoute un message au journal"""
        self.log_text.insert(tk.END, msg + "\n")
        self.log_text.see(tk.END)
        self.window.update_idletasks()

    def _set_status(self, msg: str, color: Optional[str] = None):
        """Met a jour la barre de statut"""
        if color is None:
            color = Theme.COLORS['white']
        self.status_var.set(msg)
        self.status_label.configure(fg=color)

    def _get_xlsm_path(self) -> Optional[str]:
        """Valide et retourne le chemin XLSM"""
        xlsm = self.xlsm_path_var.get().strip()
        if not xlsm:
            self._set_status("Selectionnez un fichier XLSM.", Theme.COLORS['secondary'])
            return None
        if not os.path.exists(xlsm):
            self._set_status(f"Fichier introuvable: {xlsm}", Theme.COLORS['danger'])
            return None
        return xlsm

    def _get_output_dir(self) -> Optional[str]:
        """Retourne le dossier de destination"""
        out = self.output_dir_var.get().strip()
        if out and os.path.isdir(out):
            return out
        return None

    def _disable_buttons(self):
        """Desactive les boutons pendant l'export"""
        for btn in self.export_buttons:
            btn.config(state="disabled")

    def _enable_buttons(self):
        """Reactive les boutons apres l'export"""
        for btn in self.export_buttons:
            btn.config(state="normal")

    def _run_export(self, export_func: Callable, export_name: str):
        """Execute un export"""
        xlsm = self._get_xlsm_path()
        if not xlsm:
            return

        output_dir = self._get_output_dir()

        self._disable_buttons()
        self._set_status(f"Export en cours: {export_name}...", Theme.COLORS['secondary'])
        self.log_text.delete("1.0", tk.END)
        self._log(f"=== {export_name} ===")
        self._log(f"Source: {os.path.basename(xlsm)}")
        if output_dir:
            self._log(f"Destination: {output_dir}")
        else:
            self._log(f"Destination: {os.path.dirname(os.path.abspath(xlsm))}")
        self._log("")

        try:
            result = export_func(xlsm, output_dir=output_dir, log_func=self._log)
            if result:
                self._log("")
                self._log("Export termine avec succes !")
                self._log(f"Fichier: {result}")
                self._set_status(f"Export reussi: {os.path.basename(result)}",
                               Theme.COLORS['accent'])
            else:
                self._log("ERREUR: L'export a echoue.")
                self._set_status("Echec de l'export. Voir le journal.",
                               Theme.COLORS['danger'])
        except PermissionError:
            self._log("ERREUR: Fichier verrouille. Fermez Excel et reessayez.")
            self._set_status("Erreur: fichier verrouille. Fermez Excel.",
                           Theme.COLORS['danger'])
        except Exception as e:
            self._log(f"ERREUR: {e}")
            import traceback
            self._log(traceback.format_exc())
            self._set_status(f"Erreur: {e}", Theme.COLORS['danger'])
        finally:
            self._enable_buttons()

    def _do_export_txt(self):
        """Export TXT Optiplanning"""
        self._run_export(export_optiplanning_txt, "Export TXT Optiplanning")

    def _do_export_nesting(self):
        """Export XML Plaques Nesting"""
        self._run_export(export_xml_boards_nesting, "Export XML Plaques Nesting")

    def _do_export_materials(self):
        """Export XML Materiaux SWOOD"""
        self._run_export(export_xml_materials, "Export XML Materiaux SWOOD")

    def _do_export_edgebands(self):
        """Export XML Chants"""
        self._run_export(export_xml_edgebands, "Export XML Chants (EdgeBands)")

    def _on_close(self):
        """Gere la fermeture de la fenetre"""
        if self.on_close_callback:
            self.on_close_callback()
        self.window.destroy()
