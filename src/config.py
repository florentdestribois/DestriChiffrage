# -*- coding: utf-8 -*-
"""
DestriChiffrage - Configuration
================================
Gestion de la configuration globale de l'application
"""

import os
import configparser

class Config:
    """Gestion de la configuration globale"""

    def __init__(self):
        """Initialise la configuration"""
        # Fichier de configuration dans le dossier de l'application
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
        default_data_dir = os.path.normpath(os.path.abspath(
            os.path.join(os.path.dirname(__file__), "..", "data")
        ))

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
            data_dir = os.path.normpath(os.path.abspath(
                os.path.join(os.path.dirname(__file__), "..", "data")
            ))

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
        with open(self.config_file, 'w', encoding='utf-8') as f:
            self.parser.write(f)

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
