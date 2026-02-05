# -*- coding: utf-8 -*-
"""
Script pour analyser automatiquement les PDFs avec OCR et associer les articles par désignation
"""

import sys
import os
import csv
import re
from pdf2image import convert_from_path
import pytesseract
from difflib import SequenceMatcher

# Configurer Tesseract
pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

# Configurer Poppler - Ajouter au PATH
poppler_path = r"C:\Users\tt\AppData\Local\poppler\poppler-24.08.0\Library\bin"
if os.path.exists(poppler_path):
    os.environ['PATH'] = poppler_path + os.pathsep + os.environ['PATH']

# Ajouter le dossier src au path
project_root = r"C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
sys.path.insert(0, os.path.join(project_root, 'src'))

from database import Database

def normalize_text(text):
    """Normalise le texte pour la comparaison"""
    # Convertir en majuscules et retirer les accents
    text = text.upper()
    # Retirer les caractères spéciaux et espaces multiples
    text = re.sub(r'[^\w\s]', ' ', text)
    text = re.sub(r'\s+', ' ', text)
    return text.strip()

def extract_text_from_pdf(pdf_path):
    """Extrait tout le texte depuis un PDF scanné avec OCR"""
    try:
        print(f"      Conversion en images...")
        # Convertir toutes les pages en images (limité aux 5 premières pour la vitesse)
        images = convert_from_path(pdf_path, first_page=1, last_page=5, dpi=200)

        all_text = ""
        for i, image in enumerate(images):
            print(f"      OCR page {i+1}/{len(images)}...")
            # Essayer français d'abord, sinon anglais
            try:
                text = pytesseract.image_to_string(image, lang='fra')
            except:
                text = pytesseract.image_to_string(image, lang='eng')
            all_text += text + "\n"

        return normalize_text(all_text)

    except Exception as e:
        print(f"      --> Erreur: {e}")
        return ""

def find_designation_in_text(designation, pdf_text, threshold=0.7):
    """Cherche si une désignation apparaît dans le texte du PDF"""
    designation_norm = normalize_text(designation)

    # Diviser en mots significatifs (au moins 4 caractères)
    words = [w for w in designation_norm.split() if len(w) >= 4]

    if not words:
        return False

    # Compter combien de mots sont trouvés dans le texte
    found_words = sum(1 for word in words if word in pdf_text)

    # Si au moins 70% des mots sont trouvés, c'est une correspondance
    match_ratio = found_words / len(words) if words else 0

    return match_ratio >= threshold

def main():
    data_dir = r"C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage\data"
    csv_import = os.path.join(data_dir, "Import.csv")
    devis_dir = os.path.join(data_dir, "Devis_fournisseur")

    print("=" * 80)
    print("ANALYSE AUTOMATIQUE DES PDFs AVEC OCR - ASSOCIATION PAR DESIGNATION")
    print("=" * 80)
    print()

    # 1. Lire tous les articles du CSV
    print("1. Lecture du fichier Import.csv...")
    articles = []

    with open(csv_import, 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f, delimiter=';')
        for row in reader:
            articles.append({
                'ARTICLE': row.get('ARTICLE', '').strip(),
                'DESIGNATION': row.get('DESIGNATION', '').strip(),
                'DEVIS': row.get('DEVIS', '').strip(),
            })

    print(f"   {len(articles)} articles charges")
    print()

    # 2. Analyser tous les PDFs et extraire leur texte
    print("2. Analyse des PDFs et extraction OCR...")
    pdf_texts = {}  # {rel_pdf_path: texte_extrait}

    for root, dirs, files in os.walk(devis_dir):
        for file in files:
            if file.lower().endswith('.pdf'):
                pdf_path = os.path.join(root, file)
                rel_path = os.path.relpath(pdf_path, data_dir)

                print(f"\n   Analyse: {file}")
                text = extract_text_from_pdf(pdf_path)

                if text:
                    pdf_texts[rel_path] = text
                    print(f"      --> {len(text)} caracteres extraits")
                else:
                    print(f"      --> Echec extraction")

    print()
    print(f"   {len(pdf_texts)} PDFs analyses avec succes")
    print()

    # 3. Pour chaque article, trouver le PDF correspondant
    print("3. Association des articles aux PDFs...")
    article_pdf_mapping = {}  # {article_ref: pdf_path}
    match_count = 0
    no_match_count = 0

    for article in articles:
        article_ref = article['ARTICLE']
        designation = article['DESIGNATION']

        if not designation:
            no_match_count += 1
            continue

        print(f"\n   Article {article_ref}: {designation[:60]}...")

        # Chercher dans quel PDF cette désignation apparaît
        found = False
        for pdf_path, pdf_text in pdf_texts.items():
            if find_designation_in_text(designation, pdf_text):
                article_pdf_mapping[article_ref] = pdf_path
                print(f"      --> Trouve dans: {pdf_path}")
                match_count += 1
                found = True
                break

        if not found:
            print(f"      --> Non trouve dans aucun PDF")
            no_match_count += 1

    print()
    print(f"   Resultats: {match_count} articles associes, {no_match_count} non trouves")
    print()

    # 4. Mettre à jour la base de données
    print("4. Mise a jour de la base de donnees...")
    db = Database()
    cursor = db.conn.cursor()

    updated_count = 0
    for article_ref, pdf_path in article_pdf_mapping.items():
        cursor.execute("SELECT id FROM produits WHERE reference = ?", (article_ref,))
        result = cursor.fetchone()

        if result:
            cursor.execute(
                "UPDATE produits SET devis_fournisseur = ? WHERE id = ?",
                (pdf_path, result['id'])
            )
            updated_count += 1
            print(f"   [OK] {article_ref} -> {pdf_path}")

    db.conn.commit()
    db.close()

    print()
    print(f"   {updated_count} produits mis a jour dans la base")

    # 5. Optionnel : Mettre à jour Import.csv
    print()
    print("5. Mise a jour du fichier Import.csv...")

    rows = []
    with open(csv_import, 'r', encoding='cp1252') as f:
        reader = csv.DictReader(f, delimiter=';')
        fieldnames = reader.fieldnames

        if 'FICHIER_PDF' not in fieldnames:
            fieldnames = list(fieldnames) + ['FICHIER_PDF']

        for row in reader:
            article_ref = row.get('ARTICLE', '').strip()

            if article_ref and article_ref in article_pdf_mapping:
                row['FICHIER_PDF'] = article_pdf_mapping[article_ref]
            else:
                row['FICHIER_PDF'] = ''

            rows.append(row)

    # Backup
    backup_path = csv_import + '.backup'
    if os.path.exists(csv_import):
        if os.path.exists(backup_path):
            os.remove(backup_path)
        os.rename(csv_import, backup_path)
        print(f"   Backup cree: {backup_path}")

    # Écrire le nouveau CSV
    with open(csv_import, 'w', encoding='cp1252', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=fieldnames, delimiter=';')
        writer.writeheader()
        writer.writerows(rows)

    print(f"   Fichier Import.csv mis a jour")

    print()
    print("=" * 80)
    print("ANALYSE TERMINEE!")
    print(f"  - {match_count} articles associes a un PDF")
    print(f"  - {no_match_count} articles sans PDF")
    print(f"  - {updated_count} produits mis a jour dans la base")
    print("=" * 80)

if __name__ == '__main__':
    main()
