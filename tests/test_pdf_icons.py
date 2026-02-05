"""
Test des icônes PDF - Crash Test d'utilisation
==============================================
Scénarios de test pour vérifier le bon fonctionnement des icônes PDF
"""

import sys
import os

# Ajouter le chemin src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database


def create_test_data():
    """Crée des données de test avec et sans fiches techniques"""
    db = Database()

    print("=== CRASH TEST: Création de données de test ===\n")

    # Produits de test
    test_products = [
        {
            'categorie': 'COUPE-FEU',
            'sous_categorie': 'EI30',
            'designation': 'Porte CF 1/2h avec fiche',
            'hauteur': 2040,
            'largeur': 930,
            'prix_achat': 350.00,
            'reference': 'CF30-TEST',
            'fournisseur': 'Dispano',
            'chantier': 'Test',
            'fiche_technique': 'test_fiche.pdf',  # Avec fiche (même si fichier n'existe pas)
            'notes': 'Produit avec fiche technique PDF'
        },
        {
            'categorie': 'STANDARD',
            'sous_categorie': 'Pleine',
            'designation': 'Porte standard sans fiche',
            'hauteur': 2040,
            'largeur': 830,
            'prix_achat': 125.00,
            'reference': 'STD-TEST',
            'fournisseur': 'Dispano',
            'chantier': 'Test',
            'fiche_technique': '',  # Sans fiche
            'notes': 'Produit sans fiche technique'
        },
        {
            'categorie': 'VITREE',
            'sous_categorie': 'Demi-vitrée',
            'designation': 'Porte vitrée avec fiche',
            'hauteur': 2040,
            'largeur': 830,
            'prix_achat': 280.00,
            'reference': 'VIT-TEST',
            'fournisseur': 'Dispano',
            'chantier': 'Test',
            'fiche_technique': 'test_vitree.pdf',  # Avec fiche
            'notes': 'Porte vitrée de test'
        },
        {
            'categorie': 'ACOUSTIQUE',
            'sous_categorie': 'RA 35dB',
            'designation': 'Porte acoustique sans fiche',
            'hauteur': 2040,
            'largeur': 930,
            'prix_achat': 320.00,
            'reference': 'ACO-TEST',
            'fournisseur': 'Dispano',
            'chantier': 'Test',
            'fiche_technique': None,  # Sans fiche
            'notes': 'Test acoustique'
        },
    ]

    # Ajouter les produits
    for i, product in enumerate(test_products, 1):
        product_id = db.add_produit(product)
        has_pdf = "OUI" if product.get('fiche_technique') else "NON"
        print(f"{i}. {product['designation']}")
        print(f"   ID: {product_id}")
        print(f"   Fiche PDF: {has_pdf}")
        print(f"   Categorie: {product['categorie']}")
        print()

    db.close()
    print(f"[OK] {len(test_products)} produits de test crees avec succes!")
    print("\n=== TESTS A EFFECTUER MANUELLEMENT ===")
    print("1. Lancer l'application: python src/main.py")
    print("2. Verifier que les icones PDF apparaissent uniquement sur les lignes 1 et 3")
    print("3. Tester le clic sur les icones PDF")
    print("4. Tester le scroll vertical et horizontal")
    print("5. Tester le redimensionnement de la fenetre")
    print("6. Tester le filtrage par categorie")
    print("7. Tester la recherche")
    print("8. Verifier que les icones se repositionnent correctement")
    print("\n=== SCENARIOS DE CRASH TEST ===")
    print("[X] Test 1: Scroll rapide -> Les icones doivent suivre")
    print("[X] Test 2: Redimensionnement brutal -> Pas de crash")
    print("[X] Test 3: Clic rapide sur icone -> Ouvre le PDF une seule fois")
    print("[X] Test 4: Filtrage -> Les icones disparaissent/apparaissent correctement")
    print("[X] Test 5: Tri par colonne -> Les icones suivent les lignes")


if __name__ == '__main__':
    create_test_data()
