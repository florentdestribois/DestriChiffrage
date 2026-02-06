"""
DestriChiffrage - Application principale
========================================
Application de gestion de catalogue et chiffrage de portes
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
    root.title("DestriChiffrage - Catalogue Portes")
    root.geometry("1280x800")
    root.minsize(1024, 700)

    # Icone (si disponible)
    icon_path = get_resource_path('assets/icon.ico')
    if os.path.exists(icon_path):
        root.iconbitmap(icon_path)

    # Centrer la fenetre
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'+{x}+{y}')

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
