# -*- coding: utf-8 -*-
"""
Script pour associer automatiquement les articles aux PDFs de devis fournisseur
Utilise le fichier correspondance_devis_pdf.csv
"""

import sys
import os
import csv

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database

def main():
    data_dir = r"C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage\data"
    csv_import = os.path.join(data_dir, "Import.csv")
    csv_correspondance = os.path.join(data_dir, "correspondance_devis_pdf.csv")

    print("=" * 80)
    print("ASSOCIATION AUTOMATIQUE ARTICLES <-> DEVIS PDF")
    print("=" * 80)
    print()

    # 1. Lire le fichier de correspondance
    print("1. Lecture du fichier de correspondance...")
    mapping = {}  # {devis_ref: pdf_path}

    with open(csv_correspondance, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row['FICHIER_PDF'] and row['FICHIER_PDF'].strip():
                mapping[row['REFERENCE_DEVIS']] = row['FICHIER_PDF'].strip()

    print(f"   {len(mapping)} correspondances trouvees:")
    for devis_ref in sorted(mapping.keys()):
        print(f"   - {devis_ref} -> {mapping[devis_ref]}")
    print()

    # 2. Lire le fichier Import.csv et compter les articles par devis
    print("2. Analyse du fichier Import.csv...")
    articles_par_devis = {}  # {devis_ref: nombre d'articles}

    with open(csv_import, 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            devis_ref = row.get('DEVIS', '').strip()
            if devis_ref:
                articles_par_devis[devis_ref] = articles_par_devis.get(devis_ref, 0) + 1

    print(f"   {sum(articles_par_devis.values())} articles repartis sur {len(articles_par_devis)} devis")
    for devis_ref in sorted(articles_par_devis.keys()):
        pdf_info = f"-> {mapping[devis_ref]}" if devis_ref in mapping else "-> PAS DE PDF!"
        print(f"   - {devis_ref}: {articles_par_devis[devis_ref]} articles {pdf_info}")
    print()

    # 3. Mettre à jour la base de données
    print("3. Mise a jour de la base de donnees...")
    db = Database()
    cursor = db.conn.cursor()

    updated_count = 0
    skipped_count = 0

    with open(csv_import, 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            article_ref = row.get('ARTICLE', '').strip()
            devis_ref = row.get('DEVIS', '').strip()

            if not article_ref or not devis_ref:
                continue

            if devis_ref not in mapping:
                print(f"   [SKIP] Article {article_ref}: Pas de PDF pour {devis_ref}")
                skipped_count += 1
                continue

            pdf_path = mapping[devis_ref]

            # Trouver le produit par sa référence
            cursor.execute("SELECT id, designation FROM produits WHERE reference = ?", (article_ref,))
            result = cursor.fetchone()

            if result:
                product_id = result['id']
                cursor.execute(
                    "UPDATE produits SET devis_fournisseur = ? WHERE id = ?",
                    (pdf_path, product_id)
                )
                updated_count += 1
                print(f"   [OK] {article_ref} ({result['designation'][:40]}...) -> {pdf_path}")
            else:
                print(f"   [WARN] Article {article_ref} non trouve dans la base")
                skipped_count += 1

    db.conn.commit()
    db.close()

    print()
    print("=" * 80)
    print(f"RESULTATS:")
    print(f"  - {updated_count} produits mis a jour")
    print(f"  - {skipped_count} produits ignores")
    print("=" * 80)

if __name__ == '__main__':
    main()
