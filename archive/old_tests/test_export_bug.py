"""
Test des fonctions d'export et de génération de template
"""
import sys
import os

# Ajouter src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "src"))

from database import Database

def test_create_import_template():
    """Test de la fonction create_import_template"""
    print("=" * 60)
    print("TEST 1: Création du modèle d'import")
    print("=" * 60)

    try:
        db = Database()
        output_file = os.path.join(os.path.dirname(__file__), "test_template.csv")
        print(f"Fichier de sortie: {output_file}")

        db.create_import_template(output_file)

        if os.path.exists(output_file):
            print("[OK] SUCCESS: Le fichier template a ete cree")
            with open(output_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                print(f"\nContenu du fichier ({len(content)} caracteres):")
                print(content[:500])  # Premiers 500 caracteres
            return True
        else:
            print("[FAIL] Le fichier n'a pas ete cree")
            return False

    except Exception as e:
        print(f"[ERROR] {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_export_csv():
    """Test de la fonction export_csv"""
    print("\n" + "=" * 60)
    print("TEST 2: Export de la base de données")
    print("=" * 60)

    try:
        db = Database()
        output_file = os.path.join(os.path.dirname(__file__), "test_export.csv")
        print(f"Fichier de sortie: {output_file}")

        # Obtenir le nombre de produits dans la base
        produits = db.search_produits()
        print(f"Nombre de produits dans la base: {len(produits)}")

        count = db.export_csv(output_file)

        if os.path.exists(output_file):
            print(f"[OK] SUCCESS: {count} produit(s) exporté(s)")
            with open(output_file, 'r', encoding='utf-8-sig') as f:
                content = f.read()
                lines = content.split('\n')
                print(f"\nNombre de lignes dans le fichier: {len(lines)}")
                print(f"Premières lignes:")
                for i, line in enumerate(lines[:5]):
                    print(f"  {i+1}: {line[:100]}")
            return True
        else:
            print("[FAIL] FAIL: Le fichier n'a pas été créé")
            return False

    except Exception as e:
        print(f"[FAIL] ERROR: {type(e).__name__}: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Tests des fonctions d'export\n")

    result1 = test_create_import_template()
    result2 = test_export_csv()

    print("\n" + "=" * 60)
    print("RÉSUMÉ")
    print("=" * 60)
    print(f"Test 1 (create_import_template): {'[OK] PASS' if result1 else '[FAIL] FAIL'}")
    print(f"Test 2 (export_csv): {'[OK] PASS' if result2 else '[FAIL] FAIL'}")

    if result1 and result2:
        print("\n[SUCCESS] Tous les tests sont passés!")
        print("Le problème n'est PAS dans database.py")
        print("Le problème doit être dans main_window.py ou dans l'interface")
    else:
        print("\n[WARNING] Certains tests ont échoué")
        print("Le problème est dans database.py")
