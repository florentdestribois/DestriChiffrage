# -*- coding: utf-8 -*-
"""
DestriChiffrage - Configuration
================================
Gestion de la configuration globale de l'application
"""

import os
import sys
import configparser


def _get_default_data_dir() -> str:
    """
    Détermine le dossier data par défaut.

    En mode PyInstaller : dossier data à côté de l'exécutable
    En mode développement : dossier data du projet
    """
    try:
        # PyInstaller : dossier data à côté de l'exécutable
        if getattr(sys, 'frozen', False):
            base_path = os.path.dirname(sys.executable)
        else:
            # Mode développement
            base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    except:
        # Fallback
        base_path = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

    data_dir = os.path.join(base_path, 'data')

    # Créer le dossier et sous-dossiers s'ils n'existent pas
    os.makedirs(data_dir, exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'Fiches_techniques'), exist_ok=True)
    os.makedirs(os.path.join(data_dir, 'Devis_fournisseur'), exist_ok=True)

    return os.path.normpath(os.path.abspath(data_dir))


class Config:
    """Gestion de la configuration globale"""

    def __init__(self):
        """Initialise la configuration"""
        # Fichier de configuration
        if getattr(sys, 'frozen', False):
            # Mode PyInstaller : utiliser %APPDATA% pour eviter les problemes de permissions
            appdata = os.environ.get('APPDATA', os.path.expanduser('~'))
            self.config_dir = os.path.join(appdata, "DestriChiffrage")

            # Migration: si config existe dans l'ancien emplacement, la copier
            old_config_dir = os.path.join(os.path.dirname(sys.executable), "config")
            old_config_file = os.path.join(old_config_dir, "settings.ini")
            new_config_file = os.path.join(self.config_dir, "settings.ini")

            if os.path.exists(old_config_file) and not os.path.exists(new_config_file):
                try:
                    os.makedirs(self.config_dir, exist_ok=True)
                    import shutil
                    shutil.copy2(old_config_file, new_config_file)
                except:
                    pass  # Ignorer les erreurs de migration
        else:
            # Mode développement
            self.config_dir = os.path.join(os.path.dirname(__file__), "..", "config")

        self.config_file = os.path.join(self.config_dir, "settings.ini")

        # Créer le dossier de config si nécessaire
        os.makedirs(self.config_dir, exist_ok=True)

        # Parser de configuration
        self.parser = configparser.ConfigParser()

        # Charger la configuration existante ou créer par défaut
        if os.path.exists(self.config_file):
            self.parser.read(self.config_file, encoding='utf-8')
        else:
            self._create_default_config()

    def _create_default_config(self):
        """Crée une configuration par défaut"""
        default_data_dir = _get_default_data_dir()

        self.parser['Application'] = {
            'data_dir': default_data_dir,
            'last_opened': ''
        }

        self.save()

    def get_data_dir(self) -> str:
        """Récupère le dossier data actuel"""
        if not self.parser.has_section('Application'):
            self._create_default_config()

        data_dir = self.parser.get('Application', 'data_dir', fallback=None)

        if not data_dir:
            # Valeur par défaut
            data_dir = _get_default_data_dir()

        return data_dir

    def set_data_dir(self, data_dir: str):
        """Définit le dossier data actuel"""
        if not self.parser.has_section('Application'):
            self.parser.add_section('Application')

        # Normaliser le chemin
        data_dir = os.path.normpath(os.path.abspath(data_dir))

        self.parser.set('Application', 'data_dir', data_dir)
        self.parser.set('Application', 'last_opened', data_dir)

        self.save()

    def save(self):
        """Sauvegarde la configuration"""
        try:
            os.makedirs(self.config_dir, exist_ok=True)
            with open(self.config_file, 'w', encoding='utf-8') as f:
                self.parser.write(f)
        except PermissionError as e:
            print(f"Erreur de permission lors de la sauvegarde de la config: {e}")
            raise
        except Exception as e:
            print(f"Erreur lors de la sauvegarde de la config: {e}")
            raise

    def get_db_path(self) -> str:
        """Retourne le chemin de la base de données dans le data_dir actuel"""
        data_dir = self.get_data_dir()
        return os.path.join(data_dir, "catalogue.db")

# Instance globale
_config = None

def get_config() -> Config:
    """Retourne l'instance globale de configuration"""
    global _config
    if _config is None:
        _config = Config()
    return _config
