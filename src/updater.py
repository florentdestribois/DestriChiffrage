"""
DestriChiffrage - Module de mise à jour automatique
====================================================
Gère la vérification et l'installation des mises à jour depuis GitHub Releases
"""

import requests
import os
import sys
import subprocess
import tempfile
from typing import Optional, Dict, Any

# Importer la version depuis le bon chemin
try:
    from version import __version__
except ImportError:
    # Si l'import direct échoue, essayer avec le chemin absolu
    import importlib.util
    version_path = os.path.join(os.path.dirname(__file__), 'version.py')
    spec = importlib.util.spec_from_file_location("version", version_path)
    version_module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(version_module)
    __version__ = version_module.__version__


class Updater:
    """Gestionnaire de mises à jour automatiques"""

    # Configuration GitHub
    GITHUB_OWNER = "florentdestribois"
    GITHUB_REPO = "DestriChiffrage"
    GITHUB_API_URL = f"https://api.github.com/repos/{GITHUB_OWNER}/{GITHUB_REPO}/releases/latest"

    def __init__(self):
        """Initialise le gestionnaire de mises à jour"""
        self.current_version = __version__
        self.latest_release = None

    def check_for_updates(self) -> Dict[str, Any]:
        """
        Vérifie si une mise à jour est disponible sur GitHub Releases

        Returns:
            Dict contenant:
            - 'available': bool - True si mise à jour disponible
            - 'current_version': str - Version actuelle
            - 'latest_version': str - Dernière version disponible
            - 'download_url': str - URL de téléchargement
            - 'release_notes': str - Notes de version
            - 'error': str - Message d'erreur si échec
        """
        try:
            # Requête à l'API GitHub
            response = requests.get(
                self.GITHUB_API_URL,
                timeout=10,
                headers={'Accept': 'application/vnd.github.v3+json'}
            )

            if response.status_code != 200:
                return {
                    'available': False,
                    'error': f"Erreur API GitHub: {response.status_code}"
                }

            release_data = response.json()

            # Extraire les informations
            latest_version = release_data.get('tag_name', '').lstrip('v')
            release_notes = release_data.get('body', 'Aucune note de version disponible.')

            # Trouver l'asset de l'installateur
            download_url = None
            for asset in release_data.get('assets', []):
                if asset['name'].endswith('.exe') and 'Setup' in asset['name']:
                    download_url = asset['browser_download_url']
                    break

            # Comparer les versions
            update_available = self._is_newer_version(latest_version, self.current_version)

            return {
                'available': update_available,
                'current_version': self.current_version,
                'latest_version': latest_version,
                'download_url': download_url,
                'release_notes': release_notes,
                'error': None
            }

        except requests.exceptions.RequestException as e:
            return {
                'available': False,
                'error': f"Erreur de connexion: {str(e)}"
            }
        except Exception as e:
            return {
                'available': False,
                'error': f"Erreur inattendue: {str(e)}"
            }

    def _is_newer_version(self, latest: str, current: str) -> bool:
        """
        Compare deux versions (format: X.Y.Z)

        Args:
            latest: Version la plus récente
            current: Version actuelle

        Returns:
            True si latest > current
        """
        try:
            latest_parts = [int(x) for x in latest.split('.')]
            current_parts = [int(x) for x in current.split('.')]

            # Comparer majeur.mineur.patch
            for l, c in zip(latest_parts, current_parts):
                if l > c:
                    return True
                elif l < c:
                    return False

            # Si toutes les parties sont égales
            return False

        except (ValueError, AttributeError):
            # En cas d'erreur de parsing, considérer comme pas de mise à jour
            return False

    def download_update(self, download_url: str, progress_callback=None) -> Optional[str]:
        """
        Télécharge l'installateur de mise à jour

        Args:
            download_url: URL de téléchargement de l'installateur
            progress_callback: Fonction appelée avec (bytes_downloaded, total_bytes)

        Returns:
            Chemin du fichier téléchargé, ou None en cas d'erreur
        """
        try:
            # Créer un fichier temporaire
            temp_dir = tempfile.gettempdir()
            installer_filename = os.path.basename(download_url)
            installer_path = os.path.join(temp_dir, installer_filename)

            # Télécharger avec streaming pour la progression
            response = requests.get(download_url, stream=True, timeout=30)
            response.raise_for_status()

            total_size = int(response.headers.get('content-length', 0))
            downloaded_size = 0

            with open(installer_path, 'wb') as f:
                for chunk in response.iter_content(chunk_size=8192):
                    if chunk:
                        f.write(chunk)
                        downloaded_size += len(chunk)

                        # Callback de progression
                        if progress_callback and total_size > 0:
                            progress_callback(downloaded_size, total_size)

            return installer_path

        except Exception as e:
            print(f"Erreur lors du téléchargement: {e}")
            return None

    def install_update(self, installer_path: str, silent: bool = False):
        """
        Lance l'installateur et ferme l'application actuelle

        Args:
            installer_path: Chemin vers l'installateur téléchargé
            silent: Si True, installation silencieuse
        """
        try:
            # Préparer la commande
            if silent:
                # Installation silencieuse avec Inno Setup
                cmd = [installer_path, '/SILENT', '/CLOSEAPPLICATIONS', '/RESTARTAPPLICATIONS']
            else:
                # Installation normale
                cmd = [installer_path]

            # Lancer l'installateur
            subprocess.Popen(cmd, shell=True)

            # Fermer l'application actuelle
            # L'installateur va remplacer l'exe
            sys.exit(0)

        except Exception as e:
            print(f"Erreur lors du lancement de l'installateur: {e}")
            raise


def check_updates_sync() -> Dict[str, Any]:
    """
    Fonction helper pour vérifier les mises à jour de manière synchrone

    Returns:
        Dict avec les informations de mise à jour
    """
    updater = Updater()
    return updater.check_for_updates()
