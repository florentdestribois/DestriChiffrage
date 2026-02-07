"""
DestriChiffrage - Dialogues de mise à jour
==========================================
Interfaces pour la vérification et l'installation des mises à jour
"""

import tkinter as tk
from tkinter import ttk, messagebox
import threading
import sys
import os

# Ajouter le dossier parent au path
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from ui.theme import Theme
from updater import Updater


class UpdateDialog(tk.Toplevel):
    """Dialogue de notification de mise à jour disponible"""

    def __init__(self, parent, update_info):
        """
        Initialise le dialogue de mise à jour

        Args:
            parent: Fenêtre parente
            update_info: Dict avec les informations de mise à jour
        """
        super().__init__(parent)

        self.parent = parent
        self.update_info = update_info
        self.updater = Updater()

        self.title("Mise à jour disponible")
        self.geometry("500x500")
        self.minsize(480, 480)
        self.transient(parent)
        self.grab_set()
        self.resizable(True, True)

        self._create_widgets()

        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal
        main_frame = tk.Frame(self, bg=Theme.COLORS['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Icône et titre
        header_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        header_frame.pack(fill=tk.X, pady=(0, 15))

        tk.Label(header_frame, text="🔄", font=('Segoe UI', 32),
                bg=Theme.COLORS['bg']).pack(side=tk.LEFT, padx=(0, 15))

        title_frame = tk.Frame(header_frame, bg=Theme.COLORS['bg'])
        title_frame.pack(side=tk.LEFT, fill=tk.X, expand=True)

        tk.Label(title_frame, text="Mise à jour disponible",
                font=Theme.FONTS['title'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['primary']).pack(anchor='w')

        # Informations de version
        version_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'],
                                padx=15, pady=15,
                                highlightbackground=Theme.COLORS['border'],
                                highlightthickness=1)
        version_frame.pack(fill=tk.X, pady=(0, 15))

        # Version actuelle
        tk.Label(version_frame, text="Version actuelle :",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_light']).grid(row=0, column=0, sticky='w', pady=(0, 5))

        tk.Label(version_frame, text=self.update_info['current_version'],
                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).grid(row=0, column=1, sticky='w', pady=(0, 5))

        # Nouvelle version
        tk.Label(version_frame, text="Nouvelle version :",
                font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_light']).grid(row=1, column=0, sticky='w')

        tk.Label(version_frame, text=self.update_info['latest_version'],
                font=Theme.FONTS['heading'], bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).grid(row=1, column=1, sticky='w')

        # Notes de version
        notes_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        notes_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        tk.Label(notes_frame, text="Nouveautés :",
                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['text']).pack(anchor='w', pady=(0, 5))

        # Zone de texte avec scrollbar
        text_frame = tk.Frame(notes_frame, bg=Theme.COLORS['bg_alt'],
                             highlightbackground=Theme.COLORS['border'],
                             highlightthickness=1)
        text_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(text_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.notes_text = tk.Text(text_frame, wrap=tk.WORD, height=6,
                                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg_alt'],
                                 fg=Theme.COLORS['text'], bd=0, padx=10, pady=10,
                                 yscrollcommand=scrollbar.set)
        self.notes_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.notes_text.yview)

        # Insérer les notes
        release_notes = self.update_info.get('release_notes', 'Aucune note de version disponible.')
        self.notes_text.insert('1.0', release_notes)
        self.notes_text.config(state='disabled')

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        btn_frame.pack(fill=tk.X, pady=(10, 0))

        btn_later = tk.Button(btn_frame, text="Plus tard",
                              font=Theme.FONTS['body'], bg=Theme.COLORS['bg_dark'],
                              fg=Theme.COLORS['text'], bd=0, padx=20, pady=8,
                              cursor='hand2', command=self.on_later)
        btn_later.pack(side=tk.LEFT)

        btn_install = tk.Button(btn_frame, text="Télécharger et installer",
                                font=Theme.FONTS['body_bold'], bg=Theme.COLORS['accent'],
                                fg=Theme.COLORS['white'], bd=0, padx=20, pady=8,
                                cursor='hand2', command=self.on_install)
        btn_install.pack(side=tk.RIGHT)

    def on_later(self):
        """Ferme le dialogue sans installer"""
        self.destroy()

    def on_install(self):
        """Lance le téléchargement et l'installation"""
        download_url = self.update_info.get('download_url')

        if not download_url:
            messagebox.showerror("Erreur",
                               "URL de téléchargement non disponible.",
                               parent=self)
            return

        # Fermer ce dialogue
        self.destroy()

        # Ouvrir le dialogue de progression
        progress_dialog = DownloadProgressDialog(self.parent, self.updater, download_url)


class DownloadProgressDialog(tk.Toplevel):
    """Dialogue de progression du téléchargement"""

    def __init__(self, parent, updater, download_url):
        """
        Initialise le dialogue de progression

        Args:
            parent: Fenêtre parente
            updater: Instance de Updater
            download_url: URL de téléchargement
        """
        super().__init__(parent)

        self.parent = parent
        self.updater = updater
        self.download_url = download_url
        self.installer_path = None

        self.title("Téléchargement en cours")
        self.geometry("450x200")
        self.minsize(430, 180)
        self.transient(parent)
        self.grab_set()
        self.resizable(False, False)

        # Empêcher la fermeture pendant le téléchargement
        self.protocol("WM_DELETE_WINDOW", lambda: None)

        self._create_widgets()

        # Centrer la fenêtre
        self.update_idletasks()
        x = (self.winfo_screenwidth() // 2) - (self.winfo_width() // 2)
        y = (self.winfo_screenheight() // 2) - (self.winfo_height() // 2)
        self.geometry(f"+{x}+{y}")

        # Lancer le téléchargement dans un thread
        self.download_thread = threading.Thread(target=self._download)
        self.download_thread.daemon = True
        self.download_thread.start()

    def _create_widgets(self):
        """Crée les widgets de l'interface"""
        # Frame principal
        main_frame = tk.Frame(self, bg=Theme.COLORS['bg'], padx=20, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Titre
        tk.Label(main_frame, text="Téléchargement de la mise à jour",
                font=Theme.FONTS['heading'], bg=Theme.COLORS['bg'],
                fg=Theme.COLORS['primary']).pack(pady=(0, 20))

        # Label de statut
        self.status_label = tk.Label(main_frame, text="Connexion au serveur...",
                                     font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                     fg=Theme.COLORS['text'])
        self.status_label.pack(pady=(0, 10))

        # Barre de progression
        self.progress_bar = ttk.Progressbar(main_frame, mode='determinate',
                                           length=400)
        self.progress_bar.pack(pady=(0, 10))

        # Label de pourcentage
        self.percent_label = tk.Label(main_frame, text="0%",
                                      font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                      fg=Theme.COLORS['text_light'])
        self.percent_label.pack()

    def _download(self):
        """Télécharge l'installateur (dans un thread)"""
        try:
            def progress_callback(downloaded, total):
                # Mettre à jour la barre de progression
                if total > 0:
                    percent = (downloaded / total) * 100
                    self.after(0, self._update_progress, percent, downloaded, total)

            # Télécharger
            self.after(0, self.status_label.config, {'text': 'Téléchargement en cours...'})
            self.installer_path = self.updater.download_update(
                self.download_url,
                progress_callback=progress_callback
            )

            # Succès
            if self.installer_path:
                self.after(0, self._download_complete)
            else:
                self.after(0, self._download_error, "Échec du téléchargement")

        except Exception as e:
            self.after(0, self._download_error, str(e))

    def _update_progress(self, percent, downloaded, total):
        """Met à jour la barre de progression"""
        self.progress_bar['value'] = percent
        self.percent_label.config(text=f"{percent:.1f}%")

        # Afficher taille téléchargée
        mb_downloaded = downloaded / (1024 * 1024)
        mb_total = total / (1024 * 1024)
        self.status_label.config(text=f"Téléchargement: {mb_downloaded:.1f} MB / {mb_total:.1f} MB")

    def _download_complete(self):
        """Appelé quand le téléchargement est terminé"""
        self.status_label.config(text="Téléchargement terminé !")
        self.percent_label.config(text="100%")

        # Proposer d'installer
        response = messagebox.askyesno(
            "Téléchargement terminé",
            "Le téléchargement est terminé.\n\n"
            "Voulez-vous installer maintenant ?\n"
            "(L'application va se fermer)",
            parent=self
        )

        if response:
            # Lancer l'installation
            try:
                self.updater.install_update(self.installer_path, silent=False)
            except Exception as e:
                messagebox.showerror("Erreur",
                                   f"Erreur lors de l'installation:\n{str(e)}",
                                   parent=self)
                self.destroy()
        else:
            # Fermer le dialogue
            self.destroy()

    def _download_error(self, error_message):
        """Appelé en cas d'erreur"""
        messagebox.showerror("Erreur de téléchargement",
                           f"Impossible de télécharger la mise à jour:\n\n{error_message}",
                           parent=self)
        self.destroy()


def show_no_update_dialog(parent):
    """Affiche un message quand aucune mise à jour n'est disponible"""
    messagebox.showinfo(
        "Aucune mise à jour",
        "Vous utilisez déjà la dernière version de DestriChiffrage.",
        parent=parent
    )


def show_check_error_dialog(parent, error_message):
    """Affiche un message d'erreur lors de la vérification"""
    messagebox.showerror(
        "Erreur de vérification",
        f"Impossible de vérifier les mises à jour:\n\n{error_message}",
        parent=parent
    )
