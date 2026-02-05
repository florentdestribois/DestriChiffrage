# -*- coding: utf-8 -*-
"""
Script pour associer TOUS les produits à leur PDF (par désignation exacte)
"""

import sys
import os
import csv

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))
from database import Database

def main():
    data_dir = r"C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage\data"
    csv_import = os.path.join(data_dir, "Import.csv")

    print("=" * 80)
    print("ASSOCIATION DE TOUS LES PRODUITS A LEURS PDF")
    print("=" * 80)
    print()

    # 1. Lire le CSV avec les associations
    print("1. Lecture du fichier Import.csv...")
    csv_data = []

    with open(csv_import, 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            if row.get('FICHIER_PDF') and row['FICHIER_PDF'].strip():
                csv_data.append({
                    'designation': row['DESIGNATION'].strip(),
                    'pdf': row['FICHIER_PDF'].strip()
                })

    print(f"   {len(csv_data)} lignes avec PDF dans le CSV")
    print()

    # 2. Mettre à jour tous les produits correspondants dans la base
    print("2. Mise a jour de la base de donnees...")
    db = Database()
    cursor = db.conn.cursor()

    updated_count = 0

    for item in csv_data:
        designation = item['designation']
        pdf_path = item['pdf']

        # Trouver TOUS les produits avec cette désignation
        cursor.execute("SELECT id, designation FROM produits WHERE designation = ?", (designation,))
        products = cursor.fetchall()

        for product in products:
            cursor.execute(
                "UPDATE produits SET devis_fournisseur = ? WHERE id = ?",
                (pdf_path, product['id'])
            )
            updated_count += 1
            print(f"   [OK] ID {product['id']}: {designation[:60]}... -> {pdf_path}")

    db.conn.commit()

    # 3. Vérifier le résultat
    print()
    print("3. Verification...")
    cursor.execute("SELECT COUNT(*) as total FROM produits")
    total = cursor.fetchone()['total']

    cursor.execute("SELECT COUNT(*) as with_pdf FROM produits WHERE devis_fournisseur IS NOT NULL AND devis_fournisseur != ''")
    with_pdf = cursor.fetchone()['with_pdf']

    without_pdf = total - with_pdf

    db.close()

    print(f"   Total produits: {total}")
    print(f"   - Avec PDF: {with_pdf}")
    print(f"   - Sans PDF: {without_pdf}")
    print()

    print("=" * 80)
    print(f"TERMINE! {updated_count} produits mis a jour")
    print("=" * 80)

if __name__ == '__main__':
    main()
