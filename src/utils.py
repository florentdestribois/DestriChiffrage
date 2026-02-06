"""
DestriChiffrage - Utilitaires
Fonctions helper pour l'application
"""

import os
import sys


def get_resource_path(relative_path):
    """
    Obtient le chemin absolu vers une ressource.

    Fonctionne à la fois en mode développement et avec PyInstaller.
    PyInstaller crée un dossier temporaire _MEIPASS pour les ressources.

    Args:
        relative_path: Chemin relatif depuis la racine du projet

    Returns:
        Chemin absolu vers la ressource

    Example:
        >>> icon_path = get_resource_path('assets/icon.ico')
        >>> logo_path = get_resource_path('assets/logo.png')
    """
    try:
        # PyInstaller crée un dossier temporaire et stocke le chemin dans _MEIPASS
        base_path = sys._MEIPASS
    except AttributeError:
        # Mode développement : utiliser le dossier parent de src/
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    return os.path.join(base_path, relative_path)


def get_data_dir():
    """
    Obtient le chemin vers le dossier data.

    En mode PyInstaller, utilise un dossier à côté de l'exécutable.
    En mode développement, utilise le dossier data du projet.

    Returns:
        Chemin absolu vers le dossier data
    """
    try:
        # PyInstaller : dossier data à côté de l'exécutable
        base_path = os.path.dirname(sys.executable)
    except:
        # Mode développement : dossier data du projet
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    data_dir = os.path.join(base_path, 'data')

    # Créer le dossier s'il n'existe pas
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'Fiches_techniques'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'Devis_fournisseur'), exist_ok=True)

    return data_dir
