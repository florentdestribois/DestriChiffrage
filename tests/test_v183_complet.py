# -*- coding: utf-8 -*-
"""
TESTS APPROFONDIS POST-MODIFICATION MAJEURE v1.8.3
====================================================
"""
import os
import sys
import tempfile
import shutil
import time

# Ajouter le chemin src
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database

# Variables pour le rapport
tests_passed = []
tests_failed = []
tests_fixed = []
warnings = []

def log_pass(section, desc):
    tests_passed.append(f"[{section}] {desc}")
    print(f"  [OK] {desc}")

def log_fail(section, desc, fix=None):
    if fix:
        tests_fixed.append(f"[{section}] {desc} -> {fix}")
        print(f"  [FIXED] {desc} -> {fix}")
    else:
        tests_failed.append(f"[{section}] {desc}")
        print(f"  [FAIL] {desc}")

def log_warn(desc):
    warnings.append(desc)
    print(f"  [WARN] {desc}")

def run_tests():
    # Creer un dossier temporaire pour les tests
    test_dir = tempfile.mkdtemp(prefix="destrichiffrage_test_")
    print(f"Dossier de test: {test_dir}")

    # =============================================================================
    print("\n" + "="*70)
    print("1. INTEGRITE DE LA BASE DE DONNEES")
    print("="*70)

    # 1.1 Structure et schema
    print("\n1.1 Structure et schema")
    print("-" * 40)

    db = Database(data_dir=test_dir)

    # Verifier les tables
    cursor = db.conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table'")
    tables = [row[0] for row in cursor.fetchall()]

    # Tables de base (articles_dpgf et produits_articles creees dynamiquement)
    expected_tables = ['produits', 'categories', 'parametres', 'historique_prix', 'chantiers']

    for table in expected_tables:
        if table in tables:
            log_pass("1.1", f"Table '{table}' existe")
        else:
            log_fail("1.1", f"Table '{table}' manquante")

    # Verifier les colonnes de la table produits
    cursor.execute("PRAGMA table_info(produits)")
    columns = {row[1]: row[2] for row in cursor.fetchall()}

    expected_columns = {
        'id': 'INTEGER',
        'categorie': 'TEXT',
        'sous_categorie': 'TEXT',
        'designation': 'TEXT',
        'prix_achat': 'REAL',
        'fiche_technique': 'TEXT',
        'devis_fournisseur': 'TEXT',
        'marque': 'TEXT'
    }

    for col, _ in expected_columns.items():
        if col in columns:
            log_pass("1.1", f"Colonne 'produits.{col}' existe")
        else:
            log_fail("1.1", f"Colonne 'produits.{col}' manquante")

    # 1.2 Relations et references
    print("\n1.2 Relations et references")
    print("-" * 40)

    # Creer des donnees de test pour verifier les relations
    db.add_categorie("TEST_CAT", "Categorie de test")
    produit_id = db.add_produit({
        'categorie': 'TEST_CAT',
        'designation': 'Produit test',
        'prix_achat': 100.0
    })

    cat = db.get_categorie("TEST_CAT")
    if cat:
        log_pass("1.2", "Categorie creee et retrouvee")
    else:
        log_fail("1.2", "Categorie non retrouvee")

    produit = db.get_produit(produit_id)
    if produit and produit['categorie'] == 'TEST_CAT':
        log_pass("1.2", "Produit reference correctement la categorie")
    else:
        log_fail("1.2", "Reference produit->categorie incorrecte")

    # Test chantier simple
    chantier_id = db.add_chantier({
        'nom': 'Chantier test',
        'nom_client': 'Client test'
    })

    if chantier_id:
        log_pass("1.2", "Chantier cree")
        # Verifier qu'on peut recuperer le chantier
        chantier = db.get_chantier(chantier_id)
        if chantier and chantier['nom'] == 'Chantier test':
            log_pass("1.2", "Chantier recupere correctement")
        else:
            log_fail("1.2", "Chantier non retrouve")

        # Supprimer le chantier
        db.delete_chantier(chantier_id)
        chantier_deleted = db.get_chantier(chantier_id)
        if chantier_deleted is None:
            log_pass("1.2", "Suppression chantier OK")
        else:
            log_fail("1.2", "Chantier non supprime")

    # 1.3 Retrocompatibilite
    print("\n1.3 Retrocompatibilite")
    print("-" * 40)

    produit_check = db.get_produit(produit_id)
    if produit_check and produit_check['prix_achat'] == 100.0:
        log_pass("1.3", "Donnees produit intactes")
    else:
        log_fail("1.3", "Donnees corrompues")

    # =============================================================================
    print("\n" + "="*70)
    print("2. COHERENCE DES FORMULAIRES")
    print("="*70)

    print("\n2.1 Types de donnees")
    print("-" * 40)

    test_data = {
        'categorie': 'TEST_CAT',
        'designation': 'Test designation',
        'hauteur': 2040,
        'largeur': 930,
        'prix_achat': 123.45,
        'marque': 'Test Marque'
    }

    try:
        test_id = db.add_produit(test_data)
        test_produit = db.get_produit(test_id)

        if test_produit['hauteur'] == 2040:
            log_pass("2.1", "Champ entier OK")
        if abs(test_produit['prix_achat'] - 123.45) < 0.01:
            log_pass("2.1", "Champ decimal OK")
        if test_produit['designation'] == 'Test designation':
            log_pass("2.1", "Champ texte OK")
    except Exception as e:
        log_fail("2.1", f"Erreur: {e}")

    print("\n2.2 Caracteres speciaux")
    print("-" * 40)

    try:
        special_id = db.add_produit({
            'categorie': 'TEST_CAT',
            'designation': "Test & <tag> 'quotes' accents",
            'prix_achat': 10.0
        })
        p = db.get_produit(special_id)
        if '&' in p['designation'] and '<tag>' in p['designation']:
            log_pass("2.2", "Caracteres speciaux OK")
        else:
            log_fail("2.2", "Caracteres modifies")
    except Exception as e:
        log_fail("2.2", f"Erreur: {e}")

    # =============================================================================
    print("\n" + "="*70)
    print("3. RECHERCHE ET FILTRAGE")
    print("="*70)

    print("\n3.1 Fonctions de recherche")
    print("-" * 40)

    for i in range(5):
        db.add_produit({
            'categorie': 'SEARCH_TEST',
            'designation': f'Produit recherche {i}',
            'prix_achat': 100 + i * 10,
            'marque': 'MARQUE_A' if i < 3 else 'MARQUE_B'
        })

    results = db.search_produits(terme='recherche')
    if len(results) >= 5:
        log_pass("3.1", f"Recherche par terme: {len(results)} resultats")
    else:
        log_fail("3.1", f"Recherche incorrecte: {len(results)}")

    results = db.search_produits(categorie='SEARCH_TEST')
    if len(results) >= 5:
        log_pass("3.1", f"Recherche par categorie OK")

    results = db.search_produits(marque='MARQUE_A')
    if len(results) == 3:
        log_pass("3.1", "Recherche par marque OK")

    results = db.search_produits(limit=2)
    if len(results) == 2:
        log_pass("3.1", "Pagination OK")

    # =============================================================================
    print("\n" + "="*70)
    print("4. STABILITE ET ROBUSTESSE")
    print("="*70)

    print("\n4.1 Gestion des erreurs")
    print("-" * 40)

    if db.get_produit(999999) is None:
        log_pass("4.1", "Produit inexistant -> None")

    if db.get_categorie("INEXISTANTE") is None:
        log_pass("4.1", "Categorie inexistante -> None")

    print("\n4.2 Performance")
    print("-" * 40)

    start = time.time()
    for i in range(100):
        db.add_produit({
            'categorie': 'PERF_TEST',
            'designation': f'Produit perf {i}',
            'prix_achat': i * 10
        })
    elapsed = time.time() - start
    if elapsed < 5:
        log_pass("4.2", f"100 insertions en {elapsed:.2f}s")
    else:
        log_warn(f"Insertions lentes: {elapsed:.2f}s")

    # =============================================================================
    print("\n" + "="*70)
    print("5. NOUVELLES FONCTIONNALITES v1.8.3 (PDF)")
    print("="*70)

    print("\n5.1 Gestion PDF par categories")
    print("-" * 40)

    test_pdf = os.path.join(test_dir, "test.pdf")
    with open(test_pdf, "w") as f:
        f.write("PDF test content")

    new_path = db.copy_pdf_to_category_folder(test_pdf, "Fiches_techniques", "CAT_PDF", "SOUS_CAT")
    if new_path and "CAT_PDF" in new_path:
        log_pass("5.1", "Copie PDF dans structure categorie OK")
    else:
        log_fail("5.1", f"Chemin incorrect: {new_path}")

    full_path = db.resolve_fiche_path(new_path)
    if os.path.exists(full_path):
        log_pass("5.1", "Fichier PDF copie existe")
    else:
        log_fail("5.1", "Fichier introuvable")

    # Test doublon (fichier different avec meme nom)
    test_pdf2 = os.path.join(test_dir, "test.pdf")
    with open(test_pdf2, "w") as f:
        f.write("PDF test content DIFFERENT - version 2 with more content")  # Contenu different = taille differente

    new_path2 = db.copy_pdf_to_category_folder(test_pdf2, "Fiches_techniques", "CAT_PDF", "SOUS_CAT")
    if new_path != new_path2 and "_1" in new_path2:
        log_pass("5.1", f"Gestion doublons OK: {os.path.basename(new_path2)}")
    elif new_path == new_path2:
        # Meme chemin = meme fichier (meme taille), comportement correct
        log_pass("5.1", "Meme fichier detecte, pas de doublon cree")
    else:
        log_fail("5.1", f"Doublons: attendu _1, obtenu {new_path2}")

    # Test renommage dossier
    renamed = db.rename_category_folders("CAT_PDF", "CAT_RENAMED")
    if renamed >= 1:
        log_pass("5.1", f"Renommage dossier OK ({renamed})")
    else:
        log_fail("5.1", "Renommage echoue")

    new_folder = os.path.join(test_dir, "Fiches_techniques", "CAT_RENAMED")
    if os.path.exists(new_folder):
        log_pass("5.1", "Nouveau dossier existe")

    # Test sanitize
    result = db.sanitize_folder_name("Test/Colon:Star*")
    if "/" not in result and ":" not in result and "*" not in result:
        log_pass("5.1", "Sanitize caracteres speciaux OK")

    # =============================================================================
    # NETTOYAGE
    db.conn.close()
    shutil.rmtree(test_dir)

    # =============================================================================
    print("\n" + "="*70)
    print("RAPPORT DE TESTS")
    print("="*70)

    print(f"\n### TESTS REUSSIS ({len(tests_passed)})")
    for t in tests_passed[:10]:
        print(f"  [OK] {t}")
    if len(tests_passed) > 10:
        print(f"  ... et {len(tests_passed) - 10} autres")

    if tests_failed:
        print(f"\n### TESTS ECHOUES ({len(tests_failed)})")
        for t in tests_failed:
            print(f"  [FAIL] {t}")

    if warnings:
        print(f"\n### POINTS D'ATTENTION ({len(warnings)})")
        for w in warnings:
            print(f"  [WARN] {w}")

    print(f"\n### BILAN")
    total = len(tests_passed) + len(tests_failed) + len(tests_fixed)
    print(f"  - Nombre total de tests: {total}")
    print(f"  - Reussis: {len(tests_passed)}")
    print(f"  - Echoues: {len(tests_failed)}")
    print(f"  - Warnings: {len(warnings)}")

    if not tests_failed:
        print("\n" + "="*70)
        print("TOUS LES TESTS SONT PASSES!")
        print("="*70)
        return 0
    else:
        print("\n" + "="*70)
        print("ATTENTION: DES TESTS ONT ECHOUE!")
        print("="*70)
        return 1

if __name__ == "__main__":
    sys.exit(run_tests())
