"""
Panneau d'affichage et de gestion du panier

Ce module fournit l'interface pour visualiser et gerer le panier d'articles.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import TYPE_CHECKING
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

if TYPE_CHECKING:
    from cart_manager import CartManager
    from database import Database

from ui.theme import Theme


class CartPanel(tk.Toplevel):
    """Fenetre de gestion du panier d'articles"""

    def __init__(self, parent, cart_manager: 'CartManager', db: 'Database', on_export_callback=None):
        """
        Initialise le panneau du panier

        Args:
            parent: Fenetre parente
            cart_manager: Instance du gestionnaire de panier
            db: Instance de la base de donnees
            on_export_callback: Fonction appelee lors de l'export (optionnel)
        """
        super().__init__(parent)

        self.cart_manager = cart_manager
        self.db = db
        self.on_export_callback = on_export_callback

        self.title("Panier d'articles")
        self.geometry("700x500")
        self.transient(parent)
        self.resizable(True, True)

        # Creer les widgets d'abord
        self._create_widgets()
        self._refresh_cart()

        # Forcer la mise a jour et centrer la fenetre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Cree les widgets de l'interface"""
        # Frame principal
        main_frame = tk.Frame(self, bg=Theme.COLORS['bg'], padx=15, pady=15)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Header
        header_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(header_frame, text="\U0001F6D2 Panier d'articles",  # 🛒
                font=Theme.FONTS['title'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['primary']).pack(side=tk.LEFT)

        self.count_label = tk.Label(header_frame, text="",
                                    font=Theme.FONTS['body'],
                                    bg=Theme.COLORS['bg'],
                                    fg=Theme.COLORS['text'])
        self.count_label.pack(side=tk.LEFT, padx=(10, 0))

        # Liste des articles
        list_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                             highlightbackground=Theme.COLORS['border'],
                             highlightthickness=1)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Treeview
        columns = ('id', 'designation', 'prix', 'actions')
        self.tree = ttk.Treeview(list_frame, columns=columns, show='headings',
                                selectmode='browse', height=6)

        # Configuration des colonnes
        self.tree.heading('id', text='ID')
        self.tree.heading('designation', text='Designation')
        self.tree.heading('prix', text='Prix HT')
        self.tree.heading('actions', text='')

        self.tree.column('id', width=50, anchor='center')
        self.tree.column('designation', width=400, anchor='w')
        self.tree.column('prix', width=100, anchor='e')
        self.tree.column('actions', width=80, anchor='center')

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bindings
        self.tree.bind('<Double-1>', self._on_double_click)
        self.tree.bind('<Button-3>', self._on_right_click)

        # Frame total
        total_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                              padx=15, pady=10,
                              highlightbackground=Theme.COLORS['border'],
                              highlightthickness=1)
        total_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(total_frame, text="Total HT :", font=Theme.FONTS['body_bold'],
                bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.total_label = tk.Label(total_frame, text="0.00 EUR",
                                    font=Theme.FONTS['heading'],
                                    bg=Theme.COLORS['bg_alt'],
                                    fg=Theme.COLORS['secondary'])
        self.total_label.pack(side=tk.RIGHT)

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        btn_frame.pack(fill=tk.X)

        tk.Button(btn_frame, text="Vider le panier",
                 font=Theme.FONTS['body'], bg=Theme.COLORS['danger'],
                 fg=Theme.COLORS['white'], bd=0, padx=15, pady=8,
                 cursor='hand2', command=self._on_clear_cart).pack(side=tk.LEFT, padx=(0, 10))

        tk.Button(btn_frame, text="Fermer",
                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg_dark'],
                 fg=Theme.COLORS['text'], bd=0, padx=15, pady=8,
                 cursor='hand2', command=self.destroy).pack(side=tk.RIGHT)

        tk.Button(btn_frame, text="Exporter",
                 font=Theme.FONTS['body_bold'], bg=Theme.COLORS['accent'],
                 fg=Theme.COLORS['white'], bd=0, padx=20, pady=8,
                 cursor='hand2', command=self._on_export).pack(side=tk.RIGHT, padx=(0, 10))

    def _refresh_cart(self):
        """Rafraichit l'affichage du panier"""
        # Vider le tree
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Recuperer les articles
        items = self.cart_manager.get_cart_items()

        # Remplir le tree
        for product in items:
            prix = product.get('prix_achat', 0)
            self.tree.insert('', tk.END, values=(
                product['id'],
                product['designation'],
                f"{prix:.2f} EUR",
                "Retirer"
            ))

        # Mettre a jour le compteur
        count = self.cart_manager.get_cart_count()
        self.count_label.config(text=f"({count} article{'s' if count > 1 else ''})")

        # Mettre a jour le total
        total = self.cart_manager.get_total_ht()
        self.total_label.config(text=f"{total:.2f} EUR")

    def _on_double_click(self, event):
        """Retire un article au double-clic"""
        selection = self.tree.selection()
        if not selection:
            return

        item = self.tree.item(selection[0])
        product_id = item['values'][0]
        designation = item['values'][1]

        response = messagebox.askyesno(
            "Retirer du panier",
            f"Retirer cet article du panier ?\n\n{designation}"
        )

        if response:
            self.cart_manager.remove_from_cart(product_id)
            self._refresh_cart()

    def _on_right_click(self, event):
        """Menu contextuel au clic droit"""
        # Selectionner l'item sous le curseur
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self._on_double_click(None)

    def _on_clear_cart(self):
        """Vide completement le panier"""
        if self.cart_manager.get_cart_count() == 0:
            messagebox.showinfo("Panier vide", "Le panier est deja vide.")
            return

        response = messagebox.askyesno(
            "Vider le panier",
            f"Voulez-vous vraiment vider le panier ?\n\n"
            f"{self.cart_manager.get_cart_count()} article(s) seront retires."
        )

        if response:
            self.cart_manager.clear_cart()
            self._refresh_cart()

    def _on_export(self):
        """Lance l'export du panier"""
        if self.cart_manager.get_cart_count() == 0:
            messagebox.showwarning("Panier vide",
                                  "Le panier est vide. Ajoutez des articles avant d'exporter.")
            return

        # Fermer cette fenetre et appeler le callback d'export
        self.destroy()

        if self.on_export_callback:
            self.on_export_callback()
