"""
DestriChiffrage - Dialogue resultat marche
===========================================
Saisie du resultat d'un marche (gagne/perdu/etc.)
"""

import tkinter as tk
from tkinter import ttk, messagebox
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme


# Resultats possibles avec couleurs
RESULTATS = {
    'EN_COURS': {'label': 'En cours', 'color': '#3B82F6', 'bg': '#DBEAFE'},
    'GAGNE': {'label': 'Gagne', 'color': '#059669', 'bg': '#D1FAE5'},
    'PERDU': {'label': 'Perdu', 'color': '#DB2777', 'bg': '#FCE7F3'},
    'PERTE': {'label': 'Perte (deficit)', 'color': '#DC2626', 'bg': '#FEE2E2'},
    'TROP_CHER': {'label': 'Trop cher', 'color': '#D97706', 'bg': '#FEF3C7'},
    'INCONNU': {'label': 'Inconnu', 'color': '#6B7280', 'bg': '#F3F4F6'},
}


class ResultatMarcheDialog:
    """Dialogue de saisie du resultat d'un marche"""

    def __init__(self, parent, db, chantier_id):
        self.db = db
        self.parent = parent
        self.chantier_id = chantier_id
        self.result = False

        # Charger les donnees
        self.chantier = self.db.get_chantier(chantier_id) or {}

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Resultat du marche")
        self.dialog.geometry("550x480")
        self.dialog.minsize(530, 460)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 550) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 480) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Variable resultat
        self.resultat_var = tk.StringVar(value=self.chantier.get('resultat', 'EN_COURS'))

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Cree les widgets"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Resultat du marche",
                font=Theme.FONTS['heading'],
                bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=24, pady=16)

        # Main frame
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=24, pady=20)
        main_frame.pack(fill=tk.BOTH, expand=True)

        # Info chantier
        info_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=16, pady=12,
                            highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        info_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(info_card, text=self.chantier.get('nom', ''),
                font=Theme.FONTS['body_bold'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(anchor='w')

        tk.Label(info_card,
                text=f"Montant soumis: {self.chantier.get('montant_ht', 0):.2f} EUR HT",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(anchor='w')

        # Selection resultat
        resultat_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                                highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        resultat_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(resultat_card, text="RESULTAT",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Boutons radio pour chaque resultat
        for key, info in RESULTATS.items():
            frame = tk.Frame(resultat_card, bg=Theme.COLORS['bg_alt'])
            frame.pack(fill=tk.X, pady=2)

            rb = tk.Radiobutton(frame, text=info['label'],
                              variable=self.resultat_var, value=key,
                              font=Theme.FONTS['body'],
                              bg=Theme.COLORS['bg_alt'],
                              fg=info['color'],
                              selectcolor=Theme.COLORS['bg'],
                              activebackground=Theme.COLORS['bg_alt'])
            rb.pack(side=tk.LEFT)

        # Infos concurrent
        concurrent_card = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], padx=20, pady=16,
                                  highlightbackground=Theme.COLORS['border'], highlightthickness=1)
        concurrent_card.pack(fill=tk.X, pady=(0, 16))

        tk.Label(concurrent_card, text="INFORMATIONS CONCURRENT (optionnel)",
                font=Theme.FONTS['subheading'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['secondary']).pack(anchor='w', pady=(0, 12))

        # Nom concurrent
        row1 = tk.Frame(concurrent_card, bg=Theme.COLORS['bg_alt'])
        row1.pack(fill=tk.X, pady=4)

        tk.Label(row1, text="Concurrent gagnant:",
                font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.concurrent_entry = tk.Entry(row1, width=25, font=Theme.FONTS['body'],
                                        bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                        bd=1, relief='solid')
        self.concurrent_entry.insert(0, self.chantier.get('concurrent', '') or '')
        self.concurrent_entry.pack(side=tk.LEFT, padx=(8, 0))

        # Montant concurrent
        row2 = tk.Frame(concurrent_card, bg=Theme.COLORS['bg_alt'])
        row2.pack(fill=tk.X, pady=4)

        tk.Label(row2, text="Montant concurrent:",
                font=Theme.FONTS['body'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text']).pack(side=tk.LEFT)

        self.montant_entry = tk.Entry(row2, width=15, font=Theme.FONTS['body'],
                                     bg=Theme.COLORS['bg'], fg=Theme.COLORS['text'],
                                     bd=1, relief='solid', justify='right')
        montant = self.chantier.get('montant_concurrent')
        if montant:
            self.montant_entry.insert(0, f"{montant:.2f}")
        self.montant_entry.pack(side=tk.LEFT, padx=(8, 0))

        tk.Label(row2, text="EUR HT",
                font=Theme.FONTS['small'],
                bg=Theme.COLORS['bg_alt'],
                fg=Theme.COLORS['text_muted']).pack(side=tk.LEFT, padx=(4, 0))

        # Boutons
        btn_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'], height=50)
        btn_frame.pack(fill=tk.X, pady=(16, 0))

        tk.Button(btn_frame, text="Annuler", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT, padx=(8, 0))

        tk.Button(btn_frame, text="Enregistrer", font=Theme.FONTS['body_bold'],
                 bg=Theme.COLORS['accent'], fg=Theme.COLORS['white'],
                 bd=0, padx=24, pady=10, cursor='hand2',
                 command=self._save).pack(side=tk.RIGHT)

    def _save(self):
        """Enregistre le resultat"""
        resultat = self.resultat_var.get()
        concurrent = self.concurrent_entry.get().strip()

        montant_concurrent = None
        montant_str = self.montant_entry.get().strip()
        if montant_str:
            try:
                montant_concurrent = float(montant_str.replace(',', '.'))
            except:
                messagebox.showerror("Erreur", "Montant concurrent invalide")
                return

        data = {
            'nom': self.chantier.get('nom', ''),
            'lieu': self.chantier.get('lieu', ''),
            'type_projet': self.chantier.get('type_projet', ''),
            'lot': self.chantier.get('lot', ''),
            'montant_ht': self.chantier.get('montant_ht', 0),
            'resultat': resultat,
            'concurrent': concurrent,
            'montant_concurrent': montant_concurrent,
            'notes': self.chantier.get('notes', ''),
        }

        try:
            self.db.update_chantier(self.chantier_id, data)
            self.result = True
            self.dialog.destroy()
        except Exception as e:
            messagebox.showerror("Erreur", f"Erreur: {e}")


def get_resultat_color(resultat: str) -> tuple:
    """Retourne (couleur_texte, couleur_fond) pour un resultat"""
    info = RESULTATS.get(resultat, RESULTATS['INCONNU'])
    return info['color'], info['bg']


def get_resultat_label(resultat: str) -> str:
    """Retourne le libelle d'un resultat"""
    info = RESULTATS.get(resultat, RESULTATS['INCONNU'])
    return info['label']
