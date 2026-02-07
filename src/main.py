"""
DestriChiffrage - Application principale
========================================
Application de chiffrage et approvisionnement professionnel
"""

import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import os
import sys

# Ajouter le chemin src au path
sys.path.insert(0, os.path.dirname(__file__))

from database import Database
from ui.main_window import MainWindow
from ui.theme import Theme
from utils import get_resource_path


def main():
    """Point d'entree de l'application"""
    # Creer la fenetre principale
    root = tk.Tk()

    # Configuration de base
    root.title("DestriChiffrage - Chiffrage et Approvisionnement")

    # Ouvrir en pleine hauteur d'ecran
    root.update_idletasks()
    screen_width = root.winfo_screenwidth()
    screen_height = root.winfo_screenheight()
    window_height = screen_height - 80  # Marge pour la barre des taches
    root.geometry(f"1280x{window_height}")
    root.minsize(1024, 700)

    # Icone (si disponible)
    icon_path = get_resource_path('assets/icon.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    # Centrer horizontalement, en haut de l'ecran
    x = (screen_width - 1280) // 2
    root.geometry(f"1280x{window_height}+{x}+10")

    # Appliquer le theme
    Theme.apply(root)

    # Creer l'application
    app = MainWindow(root)

    # Gestion de la fermeture
    root.protocol("WM_DELETE_WINDOW", app.on_closing)

    # Lancer la boucle principale
    root.mainloop()


if __name__ == "__main__":
    main()
