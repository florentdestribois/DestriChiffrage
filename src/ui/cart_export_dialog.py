"""
Dialogue d'export du panier

Ce module fournit l'interface pour exporter le panier avec options.
"""

import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import os
from typing import TYPE_CHECKING
import sys

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

if TYPE_CHECKING:
    from cart_manager import CartManager
    from database import Database

from ui.theme import Theme


class CartExportDialog(tk.Toplevel):
    """Dialogue d'export du panier avec options"""

    def __init__(self, parent, cart_manager: 'CartManager', db: 'Database'):
        """
        Initialise le dialogue d'export

        Args:
            parent: Fenetre parente
            cart_manager: Instance du gestionnaire de panier
            db: Instance de la base de donnees
        """
        super().__init__(parent)

        self.cart_manager = cart_manager
        self.db = db
        self.result = None

        self.title("Exporter le panier")
        self.geometry("550x450")
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # Variables
        self.csv_path_var = tk.StringVar()
        self.export_dir_var = tk.StringVar()
        self.include_fiches_var = tk.BooleanVar(value=False)
        self.include_devis_var = tk.BooleanVar(value=False)
        self.progress_var = tk.IntVar(value=0)

        # Creer les widgets d'abord
        self._create_widgets()

        # Forcer la mise a jour et centrer la fenetre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Cree les widgets de l'interface"""
        # Frame principal
        main_frame = tk.Frame(self, bg=Theme.COLORS['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 20))

        tk.Label(header_frame, text="\U0001F4E4 Exporter le panier",  # 📤
                font=Theme.FONTS['title'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['primary']).pack(side=tk.LEFT)

        count = self.cart_manager.get_cart_count()
        tk.Label(header_frame, text=f"({count} articles)",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT, padx=(10, 0))

        # Section fichier CSV
        csv_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        csv_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(csv_frame, text="Fichier CSV :",
                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 5))

        csv_input_frame = tk.Frame(csv_frame, bg=Theme.COLORS['bg'])
        csv_input_frame.pack(fill=tk.X)

        tk.Entry(csv_input_frame, textvariable=self.csv_path_var,
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text'], bd=1, relief='solid',
                state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(csv_input_frame, text="Parcourir",
                 font=Theme.FONTS['small'], bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'], bd=0, padx=10, pady=5,
                 cursor='hand2', command=self._browse_csv).pack(side=tk.LEFT, padx=(5, 0))

        # Section dossier destination PDFs
        pdf_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        pdf_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(pdf_frame, text="Dossier destination PDFs :",
                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 5))

        pdf_input_frame = tk.Frame(pdf_frame, bg=Theme.COLORS['bg'])
        pdf_input_frame.pack(fill=tk.X)

        tk.Entry(pdf_input_frame, textvariable=self.export_dir_var,
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text'], bd=1, relief='solid',
                state='readonly').pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Button(pdf_input_frame, text="Parcourir",
                 font=Theme.FONTS['small'], bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'], bd=0, padx=10, pady=5,
                 cursor='hand2', command=self._browse_dir).pack(side=tk.LEFT, padx=(5, 0))

        # Section options
        options_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                                padx=15, pady=15,
                                highlightbackground=Theme.COLORS['border'],
                                highlightthickness=1)
        options_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(options_frame, text="Options de copie :",
                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 10))

        tk.Checkbutton(options_frame, text="Inclure les fiches techniques",
                      variable=self.include_fiches_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2').pack(anchor='w', pady=(0, 5))

        tk.Checkbutton(options_frame, text="Inclure les devis fournisseur",
                      variable=self.include_devis_var, font=Theme.FONTS['body'],
                      bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                      selectcolor=Theme.COLORS['bg'], activebackground=Theme.COLORS['bg_alt'],
                      cursor='hand2').pack(anchor='w')

        # Barre de progression (cachee par defaut)
        self.progress_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))
        self.progress_frame.pack_forget()  # Masquer initialement

        tk.Label(self.progress_frame, text="Export en cours...",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 5))

        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X)

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Annuler",
                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'], bd=0, padx=20, pady=8,
                 cursor='hand2', command=self._on_cancel).pack(side=tk.LEFT)

        tk.Button(btn_frame, text="Exporter",
                 font=Theme.FONTS['body_bold'], bg=Theme.COLORS['accent'],
                 fg=Theme.COLORS['white'], bd=0, padx=30, pady=8,
                 cursor='hand2', command=self._on_export).pack(side=tk.RIGHT)

    def _browse_csv(self):
        """Ouvre le dialogue de selection du fichier CSV"""
        filepath = filedialog.asksaveasfilename(
            title="Enregistrer le fichier CSV",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")]
        )
        if filepath:
            self.csv_path_var.set(filepath)
            # Proposer le meme dossier pour les PDFs si pas encore defini
            if not self.export_dir_var.get():
                self.export_dir_var.set(os.path.dirname(filepath))

    def _browse_dir(self):
        """Ouvre le dialogue de selection du dossier"""
        directory = filedialog.askdirectory(
            title="Selectionner le dossier de destination"
        )
        if directory:
            self.export_dir_var.set(directory)

    def _on_cancel(self):
        """Annule l'export"""
        self.result = None
        self.destroy()

    def _on_export(self):
        """Lance l'export"""
        # Validation
        csv_path = self.csv_path_var.get()
        if not csv_path:
            messagebox.showwarning("Fichier manquant",
                                  "Veuillez selectionner un fichier CSV de destination.")
            return

        export_dir = self.export_dir_var.get()
        include_fiches = self.include_fiches_var.get()
        include_devis = self.include_devis_var.get()

        if (include_fiches or include_devis) and not export_dir:
            messagebox.showwarning("Dossier manquant",
                                  "Veuillez selectionner un dossier de destination pour les PDFs.")
            return

        # Afficher la barre de progression
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))
        self.progress_bar.start(10)
        self.update()

        try:
            # Recuperer les IDs des produits du panier
            product_ids = self.cart_manager.get_product_ids()

            # Exporter
            stats = self.db.export_cart_to_csv(
                product_ids=product_ids,
                filepath=csv_path,
                export_dir=export_dir if (include_fiches or include_devis) else None,
                include_fiches=include_fiches,
                include_devis=include_devis
            )

            # Arreter la barre de progression
            self.progress_bar.stop()
            self.progress_frame.pack_forget()

            # Afficher le rapport
            message = f"Export termine avec succes !\n\n"
            message += f"Articles exportes : {stats['nb_articles']}\n"
            if include_fiches:
                message += f"Fiches techniques copiees : {stats['nb_fiches']}\n"
            if include_devis:
                message += f"Devis fournisseur copies : {stats['nb_devis']}\n"

            messagebox.showinfo("Export reussi", message)

            self.result = stats
            self.destroy()

        except Exception as e:
            self.progress_bar.stop()
            self.progress_frame.pack_forget()
            messagebox.showerror("Erreur d'export",
                                f"Une erreur est survenue lors de l'export :\n\n{str(e)}")
