# -*- coding: utf-8 -*-
"""
DestriChiffrage - Dialogue d'analyse PDF avec OCR
==================================================
Permet d'analyser des PDFs et de générer un fichier CSV avec les associations
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import os
import sys
import threading

sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))
from ui.theme import Theme


class PdfAnalyzerDialog:
    """Dialogue pour analyser les PDFs et générer un CSV"""

    def __init__(self, parent):
        self.parent = parent
        self.result = False

        self.dialog = tk.Toplevel(parent)
        self.dialog.title("Analyser les PDFs et generer CSV")
        self.dialog.geometry("700x600")
        self.dialog.minsize(700, 600)
        self.dialog.transient(parent)
        self.dialog.grab_set()
        self.dialog.configure(bg=Theme.COLORS['bg'])

        # Centrer
        self.dialog.update_idletasks()
        x = parent.winfo_x() + (parent.winfo_width() - 700) // 2
        y = parent.winfo_y() + (parent.winfo_height() - 600) // 2
        self.dialog.geometry(f"+{x}+{y}")

        # Variables
        self.pdf_folder = tk.StringVar()
        self.csv_output = tk.StringVar()
        self.is_running = False

        self._create_widgets()
        self.dialog.wait_window()

    def _create_widgets(self):
        """Crée les widgets"""
        # Header
        header = tk.Frame(self.dialog, bg=Theme.COLORS['primary'], height=60)
        header.pack(fill=tk.X)
        header.pack_propagate(False)

        tk.Label(header, text="Analyser les PDFs avec OCR",
                font=Theme.FONTS['heading'], bg=Theme.COLORS['primary'],
                fg=Theme.COLORS['white']).pack(side=tk.LEFT, padx=20, pady=15)

        # Main content
        main_frame = tk.Frame(self.dialog, bg=Theme.COLORS['bg'], padx=30, pady=20)
        main_frame.pack(fill=tk.X)

        # Description
        desc_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg_alt'], bd=1, relief='solid')
        desc_frame.pack(fill=tk.X, pady=(0, 20))

        desc_text = tk.Label(desc_frame,
                            text="Cet outil analyse automatiquement les PDFs de devis fournisseur\n"
                                 "avec OCR et genere un fichier CSV avec les associations\n"
                                 "entre les articles et les PDFs.",
                            font=Theme.FONTS['small'], bg=Theme.COLORS['bg_alt'],
                            fg=Theme.COLORS['text'], justify='left', anchor='w')
        desc_text.pack(padx=15, pady=15, fill=tk.X)

        # Sélection du dossier PDF
        pdf_frame = tk.LabelFrame(main_frame, text="Dossier des devis PDF",
                                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                 fg=Theme.COLORS['text'], padx=15, pady=15)
        pdf_frame.pack(fill=tk.X, pady=(0, 15))

        input_frame = tk.Frame(pdf_frame, bg=Theme.COLORS['bg'])
        input_frame.pack(fill=tk.X)

        self.pdf_entry = tk.Entry(input_frame, textvariable=self.pdf_folder,
                                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                 fg=Theme.COLORS['text'], bd=1, relief='solid', state='readonly')
        self.pdf_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Button(input_frame, text="Parcourir...", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white'],
                 bd=0, padx=15, pady=8, cursor='hand2',
                 command=self._browse_pdf_folder).pack(side=tk.RIGHT)

        # Sélection du fichier CSV de sortie
        csv_frame = tk.LabelFrame(main_frame, text="Fichier CSV de sortie",
                                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                 fg=Theme.COLORS['text'], padx=15, pady=15)
        csv_frame.pack(fill=tk.X, pady=(0, 15))

        output_frame = tk.Frame(csv_frame, bg=Theme.COLORS['bg'])
        output_frame.pack(fill=tk.X)

        self.csv_entry = tk.Entry(output_frame, textvariable=self.csv_output,
                                 font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                 fg=Theme.COLORS['text'], bd=1, relief='solid', state='readonly')
        self.csv_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 10))

        tk.Button(output_frame, text="Parcourir...", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['secondary'], fg=Theme.COLORS['white'],
                 bd=0, padx=15, pady=8, cursor='hand2',
                 command=self._browse_csv_output).pack(side=tk.RIGHT)

        # Zone de progression
        self.progress_frame = tk.LabelFrame(main_frame, text="Progression",
                                           font=Theme.FONTS['body'], bg=Theme.COLORS['bg'],
                                           fg=Theme.COLORS['text'], padx=15, pady=15)
        self.progress_frame.pack(fill=tk.X, pady=(0, 15))

        # Text widget pour afficher les logs
        log_scroll_frame = tk.Frame(self.progress_frame, bg=Theme.COLORS['bg'])
        log_scroll_frame.pack(fill=tk.BOTH, expand=True)

        scrollbar = tk.Scrollbar(log_scroll_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        self.log_text = tk.Text(log_scroll_frame, height=10, font=Theme.FONTS['small'],
                               bg=Theme.COLORS['bg_dark'], fg=Theme.COLORS['text'],
                               bd=1, relief='solid', yscrollcommand=scrollbar.set)
        self.log_text.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.log_text.yview)

        # Barre de progression
        self.progress_bar = ttk.Progressbar(self.progress_frame, mode='indeterminate')
        self.progress_bar.pack(fill=tk.X, pady=(10, 0))

        # Boutons
        button_frame = tk.Frame(main_frame, bg=Theme.COLORS['bg'])
        button_frame.pack(fill=tk.X, pady=(20, 0))

        self.analyze_btn = tk.Button(button_frame, text="Lancer l'analyse",
                                     font=Theme.FONTS['body'], bg=Theme.COLORS['success'],
                                     fg=Theme.COLORS['white'], bd=0, padx=30, pady=12,
                                     cursor='hand2', command=self._start_analysis)
        self.analyze_btn.pack(side=tk.RIGHT, padx=(10, 0))

        tk.Button(button_frame, text="Fermer", font=Theme.FONTS['body'],
                 bg=Theme.COLORS['bg_alt'], fg=Theme.COLORS['text'],
                 bd=0, padx=30, pady=12, cursor='hand2',
                 command=self.dialog.destroy).pack(side=tk.RIGHT)

    def _browse_pdf_folder(self):
        """Ouvre un dialogue pour sélectionner le dossier PDF"""
        folder = filedialog.askdirectory(
            title="Selectionner le dossier des devis PDF",
            initialdir=self.pdf_folder.get() or os.path.expanduser("~")
        )
        if folder:
            self.pdf_folder.set(folder)

    def _browse_csv_output(self):
        """Ouvre un dialogue pour sélectionner le fichier CSV de sortie"""
        filepath = filedialog.asksaveasfilename(
            title="Enregistrer le fichier CSV",
            defaultextension=".csv",
            filetypes=[("Fichiers CSV", "*.csv"), ("Tous les fichiers", "*.*")],
            initialdir=os.path.dirname(self.csv_output.get()) if self.csv_output.get() else os.path.expanduser("~")
        )
        if filepath:
            self.csv_output.set(filepath)

    def _log(self, message):
        """Ajoute un message au log"""
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.log_text.update()

    def _start_analysis(self):
        """Lance l'analyse OCR des PDFs"""
        if not self.pdf_folder.get():
            messagebox.showerror("Erreur", "Veuillez selectionner un dossier de PDFs")
            return

        if not self.csv_output.get():
            messagebox.showerror("Erreur", "Veuillez specifier un fichier CSV de sortie")
            return

        if self.is_running:
            messagebox.showwarning("Attention", "Une analyse est deja en cours")
            return

        # Vérifier que le dossier existe
        if not os.path.exists(self.pdf_folder.get()):
            messagebox.showerror("Erreur", f"Le dossier n'existe pas:\n{self.pdf_folder.get()}")
            return

        # Désactiver le bouton et démarrer la progression
        self.is_running = True
        self.analyze_btn.config(state='disabled')
        self.progress_bar.start(10)
        self.log_text.delete('1.0', tk.END)

        # Lancer l'analyse dans un thread séparé
        thread = threading.Thread(target=self._run_analysis)
        thread.daemon = True
        thread.start()

    def _run_analysis(self):
        """Exécute l'analyse OCR (dans un thread séparé)"""
        try:
            self._log("Demarrage de l'analyse OCR...")
            self._log(f"Dossier PDF: {self.pdf_folder.get()}")
            self._log(f"Fichier CSV: {self.csv_output.get()}")
            self._log("")

            # Importer les modules nécessaires
            sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', '..', 'scripts'))

            # Importer le script d'analyse
            from pdf2image import convert_from_path
            import pytesseract
            import csv
            import re

            # Configurer Tesseract et Poppler
            pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'
            poppler_path = r"C:\Users\tt\AppData\Local\poppler\poppler-24.08.0\Library\bin"
            if os.path.exists(poppler_path):
                os.environ['PATH'] = poppler_path + os.pathsep + os.environ['PATH']

            def normalize_text(text):
                text = text.upper()
                text = re.sub(r'[^\w\s]', ' ', text)
                text = re.sub(r'\s+', ' ', text)
                return text.strip()

            # Analyser les PDFs
            pdf_folder = self.pdf_folder.get()
            all_articles = []  # Liste de tous les articles trouvés
            seen_designations = set()  # Pour éviter les doublons

            pdf_files = []
            for root, dirs, files in os.walk(pdf_folder):
                for file in files:
                    if file.lower().endswith('.pdf'):
                        pdf_files.append(os.path.join(root, file))

            self._log(f"Trouve {len(pdf_files)} fichiers PDF")
            self._log("")

            for idx, pdf_path in enumerate(pdf_files, 1):
                filename = os.path.basename(pdf_path)
                rel_path = os.path.relpath(pdf_path, os.path.dirname(pdf_folder))

                self._log(f"[{idx}/{len(pdf_files)}] Analyse: {filename}")

                try:
                    # Convertir en images
                    images = convert_from_path(pdf_path, first_page=1, last_page=10, dpi=200)

                    # OCR
                    all_text = ""
                    for i, image in enumerate(images):
                        try:
                            text = pytesseract.image_to_string(image, lang='fra')
                        except:
                            text = pytesseract.image_to_string(image, lang='eng')
                        all_text += text + "\n"

                    # Extraire les articles du texte
                    lines = all_text.split('\n')
                    articles_found = 0

                    for line in lines:
                        line = line.strip()
                        # Identifier les lignes qui ressemblent à des désignations d'articles
                        # (contiennent des mots-clés et font au moins 30 caractères)
                        keywords = ['PORTE', 'BLOC', 'CHASSIS', 'HUISSERIE', 'FERME',
                                   'DOOR', 'FRAME', 'WINDOW']

                        if (len(line) >= 30 and
                            any(keyword in line.upper() for keyword in keywords)):

                            # Normaliser pour détecter les doublons
                            normalized = normalize_text(line)

                            # Éviter les doublons
                            if normalized not in seen_designations:
                                seen_designations.add(normalized)

                                all_articles.append({
                                    'designation': line[:200],  # Limiter à 200 caractères
                                    'fichier_pdf': rel_path
                                })

                                articles_found += 1

                    self._log(f"     -> {len(all_text)} caracteres extraits, {articles_found} articles trouves")

                except Exception as e:
                    self._log(f"     -> Erreur: {e}")

            self._log("")
            self._log("Ecriture du fichier CSV...")

            # Écrire le CSV au format Import.csv
            csv_output = self.csv_output.get()

            # Format du CSV d'import (compatible avec DestriChiffrage)
            fieldnames = [
                'CATEGORIE', 'SOUS-CATEGORIE', 'SOUS-CATEGORIE 2', 'ARTICLE',
                'DESIGNATION', 'HAUTEUR', 'LARGEUR', 'QUANTITE',
                'PRIX_UNITAIRE_HT', 'MONTANT_TOTAL_HT', 'DEVIS', 'FOURNISSEUR',
                'CHANTIER', 'FICHE_TECHNIQUE', 'FICHIER_PDF'
            ]

            csv_rows = []
            for article in all_articles:
                # Pour chaque article trouvé, créer une ligne CSV
                # L'utilisateur devra compléter les autres champs manuellement
                csv_rows.append({
                    'CATEGORIE': '',
                    'SOUS-CATEGORIE': '',
                    'SOUS-CATEGORIE 2': '',
                    'ARTICLE': '',
                    'DESIGNATION': article['designation'],
                    'HAUTEUR': '',
                    'LARGEUR': '',
                    'QUANTITE': '1',
                    'PRIX_UNITAIRE_HT': '',
                    'MONTANT_TOTAL_HT': '',
                    'DEVIS': '',
                    'FOURNISSEUR': '',
                    'CHANTIER': '',
                    'FICHE_TECHNIQUE': '',
                    'FICHIER_PDF': article['fichier_pdf']
                })

            with open(csv_output, 'w', encoding='cp1252', newline='') as f:
                writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
                writer.writeheader()
                writer.writerows(csv_rows)

            self._log(f"Fichier CSV cree: {csv_output}")
            self._log(f"{len(all_articles)} articles uniques trouves")
            self._log(f"{len(csv_rows)} lignes CSV generees")
            self._log("Format compatible pour import dans DestriChiffrage")
            self._log("")
            self._log("=== ANALYSE TERMINEE ===")

            # Afficher un message de succès dans le thread principal
            self.dialog.after(0, lambda: messagebox.showinfo(
                "Success",
                f"Analyse terminee!\n\n"
                f"{len(pdf_files)} PDFs analyses\n"
                f"{len(all_articles)} articles trouves\n"
                f"Fichier CSV: {csv_output}"
            ))

        except Exception as e:
            self._log(f"ERREUR: {e}")
            self.dialog.after(0, lambda: messagebox.showerror("Erreur", f"Erreur lors de l'analyse:\n{e}"))

        finally:
            # Réactiver le bouton dans le thread principal
            self.dialog.after(0, self._analysis_complete)

    def _analysis_complete(self):
        """Appelé quand l'analyse est terminée"""
        self.is_running = False
        self.analyze_btn.config(state='normal')
        self.progress_bar.stop()
        self.result = True
