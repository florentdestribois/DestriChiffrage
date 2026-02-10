#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Test de performance d'import CSV
Executez ce script pour mesurer la vitesse d'import
"""

import sys
import os
import time

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from database import Database
import tempfile

def test_import(csv_filepath):
    """Teste l'import d'un fichier CSV et mesure les performances"""

    print("=" * 60)
    print("TEST DE PERFORMANCE D'IMPORT CSV")
    print("=" * 60)
    print()

    # Verifier que le fichier existe
    if not os.path.exists(csv_filepath):
        print(f"ERREUR: Le fichier n'existe pas: {csv_filepath}")
        return

    # Info fichier
    file_size = os.path.getsize(csv_filepath) / 1024 / 1024  # Mo
    print(f"Fichier: {csv_filepath}")
    print(f"Taille: {file_size:.2f} Mo")

    # Compter les lignes
    print("Comptage des lignes...")
    with open(csv_filepath, 'r', encoding='utf-8-sig', errors='ignore') as f:
        line_count = sum(1 for _ in f)
    print(f"Nombre de lignes: {line_count:,}")
    print()

    # Creer une base temporaire
    with tempfile.TemporaryDirectory() as tmpdir:
        db = Database(data_dir=tmpdir)

        # Callback simple pour mesurer
        callback_count = 0
        last_print = 0

        def progress_callback(current, total):
            nonlocal callback_count, last_print
            callback_count += 1
            now = time.time()
            if now - last_print >= 1.0:  # Afficher toutes les secondes
                elapsed = now - start_time
                speed = current / elapsed if elapsed > 0 else 0
                remaining = (total - current) / speed if speed > 0 else 0
                print(f"  Progression: {current:,}/{total:,} ({current*100/total:.1f}%) - {speed:,.0f}/sec - ~{remaining:.0f}s restant")
                last_print = now

        print("Demarrage de l'import...")
        print()

        start_time = time.time()

        try:
            count = db.import_csv(csv_filepath, progress_callback=progress_callback)
            elapsed = time.time() - start_time

            print()
            print("=" * 60)
            print("RESULTATS")
            print("=" * 60)
            print(f"Produits importes: {count:,}")
            print(f"Temps total: {elapsed:.2f} secondes")
            print(f"Vitesse: {count/elapsed:,.0f} produits/seconde")
            print(f"Callbacks appeles: {callback_count}")
            print()

            if elapsed > 10:
                print("ATTENTION: L'import est lent!")
                print("Causes possibles:")
                print("  - Antivirus qui scanne les ecritures")
                print("  - Disque dur lent (HDD vs SSD)")
                print("  - Fichier CSV avec beaucoup de colonnes")
            else:
                print("Performance OK!")

        except Exception as e:
            print(f"ERREUR: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python test_import_performance.py <chemin_fichier.csv>")
        print()
        print("Exemple:")
        print("  python test_import_performance.py data/mon_catalogue.csv")
    else:
        test_import(sys.argv[1])
