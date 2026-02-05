# -*- coding: utf-8 -*-
"""
Script pour afficher tous les paramètres de l'application
"""

import sys
import os

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database

def show_parameters():
    """Affiche tous les paramètres stockés en base"""

    print("=" * 80)
    print("PARAMETRES DE L'APPLICATION DestriChiffrage")
    print("=" * 80)
    print()

    db = Database()

    # Récupérer tous les paramètres
    cursor = db.conn.cursor()
    cursor.execute("SELECT cle, valeur, description FROM parametres ORDER BY cle")
    params = cursor.fetchall()

    if not params:
        print("Aucun paramètre trouvé.")
    else:
        print(f"Nombre de paramètres: {len(params)}")
        print()

        # Largeur des colonnes
        max_key = max(len(row['cle']) for row in params)
        max_val = max(len(str(row['valeur'])) for row in params) if params else 0

        # En-tête
        print(f"{'Clé':<{max_key}}  {'Valeur':<{max_val}}  Description")
        print("-" * 80)

        # Données
        for row in params:
            cle = row['cle']
            valeur = str(row['valeur']) if row['valeur'] else '(vide)'
            desc = row['description'] if row['description'] else '(pas de description)'

            # Tronquer la valeur si trop longue
            if len(valeur) > 50:
                valeur = valeur[:47] + '...'

            print(f"{cle:<{max_key}}  {valeur:<50}  {desc}")

    print()
    print("=" * 80)
    print("Emplacement de la base de données:")
    print(f"  {db.db_path}")
    print()
    print("Dossier data configuré:")
    print(f"  {db.data_dir}")
    print("=" * 80)

    db.close()

if __name__ == '__main__':
    show_parameters()
