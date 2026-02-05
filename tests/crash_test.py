"""
DestriChiffrage - Crash Test Suite
==================================
Tests automatises pour detecter les bugs et crashs potentiels
"""

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database
import tempfile
import shutil

class CrashTester:
    """Suite de tests pour crash test"""

    def __init__(self):
        # Creer une base temporaire pour les tests
        self.temp_dir = tempfile.mkdtemp()
        self.db_path = os.path.join(self.temp_dir, 'test.db')
        self.db = Database(self.db_path)
        self.errors = []
        self.successes = []

    def cleanup(self):
        """Nettoie les fichiers temporaires"""
        self.db.close()
        shutil.rmtree(self.temp_dir)

    def log_error(self, test_name, error):
        """Enregistre une erreur"""
        self.errors.append((test_name, str(error)))
        print(f"  [ERREUR] {test_name}: {error}")

    def log_success(self, test_name):
        """Enregistre un succes"""
        self.successes.append(test_name)
        print(f"  [OK] {test_name}")

    def run_test(self, test_name, test_func):
        """Execute un test avec gestion d'erreur"""
        try:
            test_func()
            self.log_success(test_name)
        except Exception as e:
            self.log_error(test_name, e)

    # ==================== TESTS BASE DE DONNEES ====================

    def test_db_connection(self):
        """Test connexion DB"""
        assert self.db.conn is not None

    def test_default_params(self):
        """Test parametres par defaut"""
        marge = self.db.get_marge()
        assert marge == 20.0

    def test_set_marge_valid(self):
        """Test modification marge valide"""
        self.db.set_marge(25.5)
        assert self.db.get_marge() == 25.5
        self.db.set_marge(20)  # Reset

    def test_set_marge_zero(self):
        """Test marge a zero"""
        self.db.set_marge(0)
        assert self.db.get_marge() == 0
        self.db.set_marge(20)  # Reset

    def test_set_marge_negative(self):
        """Test marge negative (cas limite)"""
        self.db.set_marge(-10)
        assert self.db.get_marge() == -10
        self.db.set_marge(20)  # Reset

    def test_set_marge_large(self):
        """Test marge tres grande"""
        self.db.set_marge(999999.99)
        assert self.db.get_marge() == 999999.99
        self.db.set_marge(20)  # Reset

    # ==================== TESTS CATEGORIES ====================

    def test_get_categories_default(self):
        """Test categories par defaut"""
        cats = self.db.get_categories()
        assert len(cats) >= 6  # Au moins les 6 categories par defaut

    def test_add_category_simple(self):
        """Test ajout categorie simple"""
        self.db.add_categorie("TEST_CAT", "Description test")
        cats = self.db.get_categories_names()
        assert "TEST_CAT" in cats

    def test_add_category_empty_name(self):
        """Test ajout categorie avec nom vide"""
        # Doit echouer silencieusement (INSERT OR IGNORE)
        initial_count = len(self.db.get_categories())
        self.db.add_categorie("", "Test")
        # Verifier que ca n'a pas crash

    def test_add_category_special_chars(self):
        """Test ajout categorie avec caracteres speciaux"""
        self.db.add_categorie("TEST-SPECIAL_123", "Desc avec accents: eéèêë")
        cats = self.db.get_categories_names()
        assert "TEST-SPECIAL_123" in cats

    def test_add_category_duplicate(self):
        """Test ajout categorie en double"""
        self.db.add_categorie("DUPLICATE", "First")
        self.db.add_categorie("DUPLICATE", "Second")  # Doit ignorer
        # Pas de crash = succes

    def test_update_category(self):
        """Test modification categorie"""
        self.db.add_categorie("OLD_NAME", "Old desc")
        self.db.update_categorie("OLD_NAME", "NEW_NAME", "New desc")
        cats = self.db.get_categories_names()
        assert "NEW_NAME" in cats
        assert "OLD_NAME" not in cats

    def test_update_category_nonexistent(self):
        """Test modification categorie inexistante"""
        self.db.update_categorie("NONEXISTENT_123", "STILL_NONEXISTENT", "Test")
        # Pas de crash = succes

    def test_delete_category(self):
        """Test suppression categorie"""
        self.db.add_categorie("TO_DELETE", "Will be deleted")
        self.db.delete_categorie("TO_DELETE")
        cats = self.db.get_categories_names()
        assert "TO_DELETE" not in cats

    def test_delete_category_nonexistent(self):
        """Test suppression categorie inexistante"""
        self.db.delete_categorie("CATEGORY_THAT_DOES_NOT_EXIST_12345")
        # Pas de crash = succes

    def test_get_categorie_by_name(self):
        """Test recuperation categorie par nom"""
        cat = self.db.get_categorie("COUPE-FEU")
        assert cat is not None
        assert cat['nom'] == "COUPE-FEU"

    def test_get_categorie_nonexistent(self):
        """Test recuperation categorie inexistante"""
        cat = self.db.get_categorie("NONEXISTENT_999")
        assert cat is None

    # ==================== TESTS PRODUITS ====================

    def test_add_product_simple(self):
        """Test ajout produit simple"""
        data = {
            'categorie': 'STANDARD',
            'sous_categorie': 'Test',
            'designation': 'Produit Test',
            'dimensions': '100x200',
            'prix_achat': 150.50,
            'reference': 'REF001',
            'fournisseur': 'Fournisseur Test'
        }
        id = self.db.add_produit(data)
        assert id is not None and id > 0

    def test_add_product_minimal(self):
        """Test ajout produit avec donnees minimales"""
        data = {
            'designation': 'Minimal Product'
        }
        id = self.db.add_produit(data)
        assert id is not None

    def test_add_product_empty(self):
        """Test ajout produit vide"""
        data = {}
        id = self.db.add_produit(data)
        # Pas de crash = succes (meme si donnees vides)

    def test_add_product_special_chars(self):
        """Test ajout produit avec caracteres speciaux"""
        data = {
            'categorie': 'STANDARD',
            'designation': "Porte d'entrée \"spéciale\" avec <balises> & symboles",
            'notes': "Notes avec\nretours à la ligne\tet tabulations"
        }
        id = self.db.add_produit(data)
        produit = self.db.get_produit(id)
        assert "spéciale" in produit['designation']

    def test_add_product_unicode(self):
        """Test ajout produit avec unicode"""
        data = {
            'designation': '日本語 中文 العربية Ελληνικά'
        }
        id = self.db.add_produit(data)
        produit = self.db.get_produit(id)
        assert '日本語' in produit['designation']

    def test_add_product_very_long(self):
        """Test ajout produit avec texte tres long"""
        data = {
            'designation': 'A' * 10000,
            'notes': 'B' * 50000
        }
        id = self.db.add_produit(data)
        produit = self.db.get_produit(id)
        assert len(produit['designation']) == 10000

    def test_add_product_price_zero(self):
        """Test ajout produit prix zero"""
        data = {'designation': 'Free product', 'prix_achat': 0}
        id = self.db.add_produit(data)
        produit = self.db.get_produit(id)
        assert produit['prix_achat'] == 0

    def test_add_product_price_negative(self):
        """Test ajout produit prix negatif"""
        data = {'designation': 'Negative price', 'prix_achat': -100}
        id = self.db.add_produit(data)
        produit = self.db.get_produit(id)
        assert produit['prix_achat'] == -100

    def test_add_product_price_very_large(self):
        """Test ajout produit prix tres grand"""
        data = {'designation': 'Expensive', 'prix_achat': 9999999999.99}
        id = self.db.add_produit(data)
        produit = self.db.get_produit(id)
        assert produit['prix_achat'] == 9999999999.99

    def test_update_product(self):
        """Test modification produit"""
        data = {'designation': 'Original', 'prix_achat': 100}
        id = self.db.add_produit(data)
        data['designation'] = 'Modified'
        data['prix_achat'] = 200
        self.db.update_produit(id, data)
        produit = self.db.get_produit(id)
        assert produit['designation'] == 'Modified'
        assert produit['prix_achat'] == 200

    def test_update_product_nonexistent(self):
        """Test modification produit inexistant"""
        self.db.update_produit(999999, {'designation': 'Test'})
        # Pas de crash = succes

    def test_delete_product(self):
        """Test suppression produit (soft delete)"""
        data = {'designation': 'To delete'}
        id = self.db.add_produit(data)
        self.db.delete_produit(id)
        produit = self.db.get_produit(id)
        assert produit['actif'] == 0

    def test_delete_product_permanent(self):
        """Test suppression produit permanent"""
        data = {'designation': 'To delete permanently'}
        id = self.db.add_produit(data)
        self.db.delete_produit(id, permanent=True)
        produit = self.db.get_produit(id)
        assert produit is None

    def test_delete_product_nonexistent(self):
        """Test suppression produit inexistant"""
        self.db.delete_produit(999999)
        self.db.delete_produit(999999, permanent=True)
        # Pas de crash = succes

    # ==================== TESTS RECHERCHE ====================

    def test_search_empty(self):
        """Test recherche sans critere"""
        results = self.db.search_produits()
        assert isinstance(results, list)

    def test_search_by_term(self):
        """Test recherche par terme"""
        self.db.add_produit({'designation': 'UNIQUE_SEARCH_TERM_ABC123', 'categorie': 'STANDARD'})
        results = self.db.search_produits('UNIQUE_SEARCH_TERM')
        assert len(results) >= 1

    def test_search_by_category(self):
        """Test recherche par categorie"""
        results = self.db.search_produits(categorie='STANDARD')
        # Doit fonctionner sans crash

    def test_search_special_chars(self):
        """Test recherche avec caracteres speciaux"""
        results = self.db.search_produits("test'injection; DROP TABLE;")
        # Pas de crash = protection SQL injection OK

    def test_search_unicode(self):
        """Test recherche unicode"""
        results = self.db.search_produits("日本語")
        assert isinstance(results, list)

    def test_search_very_long_term(self):
        """Test recherche terme tres long"""
        results = self.db.search_produits("A" * 10000)
        assert isinstance(results, list)

    # ==================== TESTS CATEGORY + PRODUITS ====================

    def test_update_products_category(self):
        """Test reassignation produits"""
        self.db.add_categorie("CAT_A", "Category A")
        self.db.add_categorie("CAT_B", "Category B")
        self.db.add_produit({'designation': 'Product in A', 'categorie': 'CAT_A'})
        self.db.update_produits_category("CAT_A", "CAT_B")
        results = self.db.search_produits(categorie="CAT_B")
        assert any(p['designation'] == 'Product in A' for p in results)

    def test_delete_products_by_category(self):
        """Test suppression produits par categorie"""
        self.db.add_categorie("CAT_TO_CLEAR", "Will be cleared")
        self.db.add_produit({'designation': 'Product to delete', 'categorie': 'CAT_TO_CLEAR'})
        self.db.delete_produits_by_category("CAT_TO_CLEAR")
        count = self.db.count_produits("CAT_TO_CLEAR")
        assert count == 0

    def test_count_products(self):
        """Test comptage produits"""
        count = self.db.count_produits()
        assert count >= 0

    def test_count_products_by_category(self):
        """Test comptage produits par categorie"""
        count = self.db.count_produits("STANDARD")
        assert count >= 0

    def test_count_products_nonexistent_category(self):
        """Test comptage categorie inexistante"""
        count = self.db.count_produits("CATEGORY_DOES_NOT_EXIST_999")
        assert count == 0

    # ==================== TESTS STATISTIQUES ====================

    def test_stats(self):
        """Test recuperation statistiques"""
        stats = self.db.get_stats()
        assert 'total_produits' in stats
        assert 'par_categorie' in stats
        assert 'prix_moyen' in stats

    def test_stats_empty_db(self):
        """Test stats sur DB presque vide"""
        # La DB de test a deja des donnees, mais verifier que ca ne crash pas
        stats = self.db.get_stats()
        assert isinstance(stats['prix_moyen'], (int, float))

    # ==================== TESTS IMPORT/EXPORT ====================

    def test_export_csv(self):
        """Test export CSV"""
        csv_path = os.path.join(self.temp_dir, 'export_test.csv')
        count = self.db.export_csv(csv_path)
        assert os.path.exists(csv_path)

    def test_export_csv_with_selection(self):
        """Test export CSV avec selection"""
        csv_path = os.path.join(self.temp_dir, 'export_selection.csv')
        produits = self.db.search_produits()[:5]
        count = self.db.export_csv(csv_path, produits)
        assert count <= 5

    def test_import_csv_nonexistent(self):
        """Test import CSV fichier inexistant"""
        try:
            self.db.import_csv("nonexistent_file_12345.csv")
            assert False, "Devrait lever une exception"
        except FileNotFoundError:
            pass  # Expected

    # ==================== EXECUTION ====================

    def run_all_tests(self):
        """Execute tous les tests"""
        print("\n" + "="*60)
        print("CRASH TEST - DestriChiffrage")
        print("="*60 + "\n")

        # Liste de tous les tests
        tests = [
            # DB Connection
            ("Connexion DB", self.test_db_connection),
            ("Parametres par defaut", self.test_default_params),
            ("Marge valide", self.test_set_marge_valid),
            ("Marge zero", self.test_set_marge_zero),
            ("Marge negative", self.test_set_marge_negative),
            ("Marge tres grande", self.test_set_marge_large),

            # Categories
            ("Categories par defaut", self.test_get_categories_default),
            ("Ajout categorie simple", self.test_add_category_simple),
            ("Ajout categorie nom vide", self.test_add_category_empty_name),
            ("Ajout categorie chars speciaux", self.test_add_category_special_chars),
            ("Ajout categorie doublon", self.test_add_category_duplicate),
            ("Modification categorie", self.test_update_category),
            ("Modification categorie inexistante", self.test_update_category_nonexistent),
            ("Suppression categorie", self.test_delete_category),
            ("Suppression categorie inexistante", self.test_delete_category_nonexistent),
            ("Get categorie par nom", self.test_get_categorie_by_name),
            ("Get categorie inexistante", self.test_get_categorie_nonexistent),

            # Produits
            ("Ajout produit simple", self.test_add_product_simple),
            ("Ajout produit minimal", self.test_add_product_minimal),
            ("Ajout produit vide", self.test_add_product_empty),
            ("Ajout produit chars speciaux", self.test_add_product_special_chars),
            ("Ajout produit unicode", self.test_add_product_unicode),
            ("Ajout produit texte long", self.test_add_product_very_long),
            ("Ajout produit prix zero", self.test_add_product_price_zero),
            ("Ajout produit prix negatif", self.test_add_product_price_negative),
            ("Ajout produit prix enorme", self.test_add_product_price_very_large),
            ("Modification produit", self.test_update_product),
            ("Modification produit inexistant", self.test_update_product_nonexistent),
            ("Suppression produit soft", self.test_delete_product),
            ("Suppression produit permanent", self.test_delete_product_permanent),
            ("Suppression produit inexistant", self.test_delete_product_nonexistent),

            # Recherche
            ("Recherche vide", self.test_search_empty),
            ("Recherche par terme", self.test_search_by_term),
            ("Recherche par categorie", self.test_search_by_category),
            ("Recherche SQL injection", self.test_search_special_chars),
            ("Recherche unicode", self.test_search_unicode),
            ("Recherche terme tres long", self.test_search_very_long_term),

            # Category + Produits
            ("Reassignation produits", self.test_update_products_category),
            ("Suppression produits par categorie", self.test_delete_products_by_category),
            ("Comptage produits", self.test_count_products),
            ("Comptage par categorie", self.test_count_products_by_category),
            ("Comptage categorie inexistante", self.test_count_products_nonexistent_category),

            # Stats
            ("Statistiques", self.test_stats),
            ("Statistiques DB quasi-vide", self.test_stats_empty_db),

            # Import/Export
            ("Export CSV", self.test_export_csv),
            ("Export CSV selection", self.test_export_csv_with_selection),
            ("Import CSV inexistant", self.test_import_csv_nonexistent),
        ]

        for test_name, test_func in tests:
            self.run_test(test_name, test_func)

        # Resume
        print("\n" + "="*60)
        print("RESULTATS")
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
            print("\nTous les tests ont reussi!")

        return len(self.errors) == 0


if __name__ == "__main__":
    tester = CrashTester()
    try:
        success = tester.run_all_tests()
        sys.exit(0 if success else 1)
    finally:
        tester.cleanup()
