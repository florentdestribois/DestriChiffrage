"""
Tests pour le module database
"""

import pytest
import os
import sys
import tempfile

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from database import Database


class TestDatabase:
    """Tests de la classe Database"""

    @pytest.fixture
    def db(self):
        """Cree une base de donnees temporaire pour les tests"""
        with tempfile.NamedTemporaryFile(suffix='.db', delete=False) as f:
            db_path = f.name

        db = Database(db_path)
        yield db
        db.close()
        os.unlink(db_path)

    def test_create_database(self, db):
        """Test de creation de la base"""
        assert db is not None
        assert os.path.exists(db.db_path)

    def test_default_marge(self, db):
        """Test de la marge par defaut"""
        marge = db.get_marge()
        assert marge == 20.0

    def test_set_marge(self, db):
        """Test de modification de la marge"""
        db.set_marge(25)
        assert db.get_marge() == 25.0

    def test_add_produit(self, db):
        """Test d'ajout de produit"""
        data = {
            'categorie': 'TEST',
            'sous_categorie': 'Sous-test',
            'designation': 'Produit de test',
            'dimensions': '100x200',
            'prix_achat': 150.50,
            'reference': 'REF001',
            'fournisseur': 'Fournisseur Test'
        }
        product_id = db.add_produit(data)
        assert product_id > 0

        # Verifier que le produit existe
        produit = db.get_produit(product_id)
        assert produit is not None
        assert produit['designation'] == 'Produit de test'
        assert produit['prix_achat'] == 150.50

    def test_search_produits(self, db):
        """Test de recherche de produits"""
        # Ajouter quelques produits
        db.add_produit({'categorie': 'CAT1', 'designation': 'Porte EI30', 'prix_achat': 100})
        db.add_produit({'categorie': 'CAT1', 'designation': 'Porte EI60', 'prix_achat': 200})
        db.add_produit({'categorie': 'CAT2', 'designation': 'Porte acoustique', 'prix_achat': 300})

        # Recherche par terme
        results = db.search_produits(terme='EI30')
        assert len(results) == 1

        # Recherche par categorie
        results = db.search_produits(categorie='CAT1')
        assert len(results) == 2

        # Recherche combinee
        results = db.search_produits(terme='Porte', categorie='CAT2')
        assert len(results) == 1

    def test_update_produit(self, db):
        """Test de mise a jour de produit"""
        product_id = db.add_produit({
            'categorie': 'TEST',
            'designation': 'Original',
            'prix_achat': 100
        })

        db.update_produit(product_id, {
            'categorie': 'TEST',
            'designation': 'Modifie',
            'prix_achat': 150
        })

        produit = db.get_produit(product_id)
        assert produit['designation'] == 'Modifie'
        assert produit['prix_achat'] == 150

    def test_delete_produit(self, db):
        """Test de suppression de produit"""
        product_id = db.add_produit({
            'categorie': 'TEST',
            'designation': 'A supprimer',
            'prix_achat': 100
        })

        # Suppression douce (desactivation)
        db.delete_produit(product_id, permanent=False)
        results = db.search_produits(actif_only=True)
        assert len(results) == 0

        # Le produit existe toujours
        produit = db.get_produit(product_id)
        assert produit is not None
        assert produit['actif'] == 0

    def test_get_categories(self, db):
        """Test de recuperation des categories"""
        categories = db.get_categories()
        assert len(categories) > 0
        assert any(c['nom'] == 'COUPE-FEU' for c in categories)

    def test_count_produits(self, db):
        """Test du comptage de produits"""
        db.add_produit({'categorie': 'CAT1', 'designation': 'Prod1', 'prix_achat': 100})
        db.add_produit({'categorie': 'CAT1', 'designation': 'Prod2', 'prix_achat': 200})
        db.add_produit({'categorie': 'CAT2', 'designation': 'Prod3', 'prix_achat': 300})

        assert db.count_produits() == 3
        assert db.count_produits('CAT1') == 2

    def test_get_stats(self, db):
        """Test des statistiques"""
        db.add_produit({'categorie': 'CAT1', 'designation': 'Prod1', 'prix_achat': 100})
        db.add_produit({'categorie': 'CAT1', 'designation': 'Prod2', 'prix_achat': 200})

        stats = db.get_stats()
        assert stats['total_produits'] == 2
        assert stats['prix_moyen'] == 150
        assert stats['prix_min'] == 100
        assert stats['prix_max'] == 200


if __name__ == '__main__':
    pytest.main([__file__, '-v'])
