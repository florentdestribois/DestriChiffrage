"""
DestriChiffrage - UI Crash Test
===============================
Tests automatises de l'interface utilisateur
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

import tkinter as tk
from tkinter import ttk
import tempfile
import shutil

# Importer les composants
from database import Database
from ui.theme import Theme
from ui.main_window import MainWindow
from ui.dialogs import ProductDialog, CategoryDialog, SettingsDialog, AboutDialog


class UITester:
    """Tests UI automatises"""

    def __init__(self):
        # Creer une base temporaire
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test_ui.db')

        # Creer dossier data
        os.makedirs(os.path.join(self.temp_dir, 'data'), exist_ok=True)

        self.errors = []
        self.successes = []

    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        shutil.rmtree(self.temp_dir, ignore_errors=True)

    def log_error(self, test_name, error):
        self.errors.append((test_name, str(error)))
        print(f"  [ERREUR] {test_name}: {error}")

    def log_success(self, test_name):
        self.successes.append(test_name)
        print(f"  [OK] {test_name}")

    def run_test(self, test_name, test_func):
        try:
            test_func()
            self.log_success(test_name)
        except Exception as e:
            self.log_error(test_name, e)

    # ==================== TESTS THEME ====================

    def test_theme_colors(self):
        """Test toutes les couleurs du theme"""
        root = tk.Tk()
        root.withdraw()

        for name, color in Theme.COLORS.items():
            # Verifier que la couleur est valide
            try:
                frame = tk.Frame(root, bg=color)
                frame.destroy()
            except tk.TclError as e:
                raise Exception(f"Couleur invalide '{name}': {color} - {e}")

        root.destroy()

    def test_theme_fonts(self):
        """Test toutes les polices du theme"""
        root = tk.Tk()
        root.withdraw()

        for name, font in Theme.FONTS.items():
            try:
                label = tk.Label(root, font=font, text="Test")
                label.destroy()
            except tk.TclError as e:
                raise Exception(f"Police invalide '{name}': {font} - {e}")

        root.destroy()

    def test_theme_apply(self):
        """Test application du theme"""
        root = tk.Tk()
        root.withdraw()
        Theme.apply(root)
        root.destroy()

    # ==================== TESTS MAIN WINDOW ====================

    def test_main_window_creation(self):
        """Test creation fenetre principale"""
        root = tk.Tk()
        root.withdraw()

        # Utiliser DB temporaire
        db = Database(self.db_path)

        # Creer la fenetre
        app = MainWindow(root)
        app.db = db

        # Forcer le rafraichissement
        root.update()

        # Verifier les composants essentiels
        assert hasattr(app, 'tree'), "Treeview manquant"
        assert hasattr(app, 'search_var'), "Variable recherche manquante"
        assert hasattr(app, 'category_var'), "Variable categorie manquante"

        db.close()
        root.destroy()

    def test_main_window_search(self):
        """Test fonctionnalite recherche"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Ajouter un produit test
        db.add_produit({'designation': 'SEARCH_TEST_XYZ', 'categorie': 'STANDARD', 'prix_achat': 100})

        # Rechercher
        app.search_var.set('SEARCH_TEST')
        app.on_search()
        root.update()

        db.close()
        root.destroy()

    def test_main_window_category_filter(self):
        """Test filtre par categorie"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Changer de categorie
        app.category_var.set("STANDARD")
        app.on_category_change()
        root.update()

        # Revenir a toutes
        app.category_var.set("Toutes")
        app.on_category_change()
        root.update()

        db.close()
        root.destroy()

    def test_main_window_marge(self):
        """Test modification marge"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Modifier la marge
        app.marge_var.set("25")
        app.on_apply_marge()
        root.update()

        # Marge invalide
        app.marge_var.set("invalide")
        app.on_apply_marge()  # Doit gerer l'erreur sans crash
        root.update()

        db.close()
        root.destroy()

    def test_main_window_clear_search(self):
        """Test effacer recherche"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Remplir les filtres
        app.search_var.set("test")
        app.category_var.set("STANDARD")

        # Effacer
        app.clear_search()
        root.update()

        assert app.search_var.get() == ""
        assert app.category_var.get() == "Toutes"
        assert app.hauteur_var.get() == "Toutes"
        assert app.largeur_var.get() == "Toutes"

        db.close()
        root.destroy()

    def test_main_window_dimension_filters(self):
        """Test filtres hauteur/largeur"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        # Ajouter des produits avec dimensions
        db.add_produit({'designation': 'Porte A', 'categorie': 'STANDARD', 'prix_achat': 100, 'hauteur': 2040, 'largeur': 830})
        db.add_produit({'designation': 'Porte B', 'categorie': 'STANDARD', 'prix_achat': 120, 'hauteur': 2040, 'largeur': 930})
        db.add_produit({'designation': 'Porte C', 'categorie': 'STANDARD', 'prix_achat': 150, 'hauteur': 2140, 'largeur': 830})

        app = MainWindow(root)
        app.db = db
        root.update()

        # Test filtre hauteur
        app.hauteur_var.set("2040")
        app.on_hauteur_change()
        root.update()

        # Test filtre largeur
        app.largeur_var.set("830")
        app.on_search()
        root.update()

        db.close()
        root.destroy()

    def test_main_window_sort(self):
        """Test tri colonnes"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        db.add_produit({'designation': 'AAA', 'categorie': 'STANDARD', 'prix_achat': 300})
        db.add_produit({'designation': 'ZZZ', 'categorie': 'STANDARD', 'prix_achat': 100})

        app = MainWindow(root)
        app.db = db
        root.update()

        # Trier par designation
        app.sort_column('designation')
        root.update()

        # Trier par prix
        app.sort_column('prix_achat')
        root.update()

        db.close()
        root.destroy()

    def test_main_window_stats(self):
        """Test affichage statistiques"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Les stats sont affichees via messagebox, on verifie juste que ca ne crash pas
        stats = db.get_stats()
        assert 'total_produits' in stats

        db.close()
        root.destroy()

    # ==================== TESTS DIALOGS ====================

    def test_about_dialog(self):
        """Test dialogue A propos"""
        root = tk.Tk()
        root.withdraw()
        root.update()

        # Creer le dialogue et le fermer immediatement
        def close_dialog():
            for child in root.winfo_children():
                if isinstance(child, tk.Toplevel):
                    child.destroy()

        root.after(100, close_dialog)

        try:
            AboutDialog(root)
        except tk.TclError:
            pass  # Fenetre fermee par notre callback

        root.destroy()

    # ==================== TESTS EDGE CASES ====================

    def test_empty_database(self):
        """Test avec base vide"""
        root = tk.Tk()
        root.withdraw()

        # Nouvelle base vide
        empty_db_path = os.path.join(self.temp_dir, 'empty.db')
        db = Database(empty_db_path)

        app = MainWindow(root)
        app.db = db
        root.update()

        # Recherche sur base vide
        app.search_var.set("test")
        app.on_search()
        root.update()

        db.close()
        root.destroy()

    def test_rapid_search(self):
        """Test recherche rapide (simulation frappe clavier)"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Simuler une frappe rapide
        for char in "porte interieure":
            app.search_var.set(app.search_var.get() + char)
            root.update()

        # Effacer rapidement
        while app.search_var.get():
            app.search_var.set(app.search_var.get()[:-1])
            root.update()

        db.close()
        root.destroy()

    def test_category_change_rapid(self):
        """Test changement rapide de categorie"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Changer rapidement de categorie
        categories = ["Toutes", "STANDARD", "COUPE-FEU", "ACOUSTIQUE", "Toutes"]
        for cat in categories:
            app.category_var.set(cat)
            app.on_category_change()
            root.update()

        db.close()
        root.destroy()

    def test_refresh_multiple(self):
        """Test rafraichissements multiples"""
        root = tk.Tk()
        root.withdraw()

        db = Database(self.db_path)
        app = MainWindow(root)
        app.db = db
        root.update()

        # Rafraichir plusieurs fois
        for _ in range(10):
            app.refresh_data()
            root.update()

        db.close()
        root.destroy()

    # ==================== EXECUTION ====================

    def run_all_tests(self):
        """Execute tous les tests UI"""
        print("\n" + "="*60)
        print("UI CRASH TEST - DestriChiffrage")
        print("="*60 + "\n")

        tests = [
            # Theme
            ("Theme - Couleurs valides", self.test_theme_colors),
            ("Theme - Polices valides", self.test_theme_fonts),
            ("Theme - Application", self.test_theme_apply),

            # Main Window
            ("MainWindow - Creation", self.test_main_window_creation),
            ("MainWindow - Recherche", self.test_main_window_search),
            ("MainWindow - Filtre categorie", self.test_main_window_category_filter),
            ("MainWindow - Modification marge", self.test_main_window_marge),
            ("MainWindow - Effacer recherche", self.test_main_window_clear_search),
            ("MainWindow - Filtres dimensions", self.test_main_window_dimension_filters),
            ("MainWindow - Tri colonnes", self.test_main_window_sort),
            ("MainWindow - Stats", self.test_main_window_stats),

            # Dialogs
            ("AboutDialog - Ouverture", self.test_about_dialog),

            # Edge cases
            ("Edge - Base vide", self.test_empty_database),
            ("Edge - Recherche rapide", self.test_rapid_search),
            ("Edge - Changement categorie rapide", self.test_category_change_rapid),
            ("Edge - Rafraichissements multiples", self.test_refresh_multiple),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Resume
        print("\n" + "="*60)
        print("RESULTATS UI")
        print("="*60)
        print(f"\nTotal: {len(tests)} tests")
        print(f"Succes: {len(self.successes)}")
        print(f"Erreurs: {len(self.errors)}")

        if self.errors:
            print("\n--- ERREURS DETECTEES ---")
            for test_name, error in self.errors:
                print(f"\n{test_name}:")
                print(f"  {error}")
        else:
            print("\nTous les tests UI ont reussi!")

        return len(self.errors) == 0


if __name__ == "__main__":
    tester = UITester()
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        tester.cleanup()
