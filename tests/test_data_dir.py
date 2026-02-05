# -*- coding: utf-8 -*-
"""
Test de la configuration du dossier data
"""

import sys
import os

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database

def test_data_dir():
    """Test de la configuration du dossier data"""

    print("=== Test de Configuration du Dossier Data ===\n")

    # Créer une instance de la base de données
    db = Database()

    # 1. Vérifier le data_dir par défaut
    print(f"1. Dossier data par défaut: {db.data_dir}")
    assert db.data_dir, "data_dir ne devrait pas être vide"
    assert os.path.isabs(db.data_dir), "data_dir devrait être un chemin absolu"
    print("   [OK] data_dir est defini et absolu\n")

    # 2. Vérifier que le paramètre est bien stocké en base
    stored_data_dir = db.get_parametre('data_dir')
    print(f"2. Dossier data stocke en base: {stored_data_dir}")
    assert stored_data_dir, "data_dir devrait être stocké en base"
    print("   [OK] data_dir est stocke en base\n")

    # 3. Tester resolve_fiche_path
    rel_path = "Fiches_techniques/test.pdf"
    abs_path = db.resolve_fiche_path(rel_path)
    print(f"3. Resolution de chemin relatif:")
    print(f"   Entree:  {rel_path}")
    print(f"   Sortie:  {abs_path}")
    assert os.path.isabs(abs_path), "Le chemin résolu devrait être absolu"
    assert "test.pdf" in abs_path, "Le nom du fichier devrait être présent"
    print("   [OK] resolve_fiche_path fonctionne\n")

    # 4. Tester make_fiche_path_relative
    test_abs_path = os.path.join(db.data_dir, "Devis_fournisseur", "test_devis.pdf")
    rel_path = db.make_fiche_path_relative(test_abs_path)
    print(f"4. Conversion en chemin relatif:")
    print(f"   Entree:  {test_abs_path}")
    print(f"   Sortie:  {rel_path}")
    assert not os.path.isabs(rel_path), "Le chemin devrait être relatif"
    assert "test_devis.pdf" in rel_path, "Le nom du fichier devrait être présent"
    print("   [OK] make_fiche_path_relative fonctionne\n")

    # 5. Tester le changement de data_dir
    new_data_dir = os.path.join(os.path.dirname(__file__), '..', 'test_data')
    new_data_dir = os.path.normpath(os.path.abspath(new_data_dir))

    print(f"5. Test de changement de dossier data:")
    print(f"   Ancien: {db.data_dir}")
    print(f"   Nouveau: {new_data_dir}")

    db.set_parametre('data_dir', new_data_dir)
    db.data_dir = new_data_dir

    assert db.data_dir == new_data_dir, "data_dir devrait être mis à jour"
    assert db.get_parametre('data_dir') == new_data_dir, "Devrait être persisté en base"
    print("   [OK] Le changement de data_dir fonctionne\n")

    # 6. Restaurer le dossier par défaut
    default_data_dir = os.path.normpath(os.path.abspath(
        os.path.join(os.path.dirname(__file__), '..', 'data')
    ))
    db.set_parametre('data_dir', default_data_dir)
    db.data_dir = default_data_dir
    print(f"6. Restauration du dossier par defaut: {db.data_dir}")
    print("   [OK] Dossier par defaut restaure\n")

    db.close()

    print("=== [OK] TOUS LES TESTS PASSENT ===\n")

    print("Test manuel a effectuer:")
    print("1. Lancer l'application: python src/main.py")
    print("2. Ouvrir Edition -> Parametres")
    print("3. Verifier que 'Dossier des donnees' est affiche avec le bouton '...'")
    print("4. Cliquer sur '...' pour selectionner un nouveau dossier")
    print("5. Enregistrer et verifier que les fichiers sont cherches au bon endroit")

if __name__ == '__main__':
    test_data_dir()
