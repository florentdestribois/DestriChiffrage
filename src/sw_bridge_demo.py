# -*- coding: utf-8 -*-
"""
DestriChiffrage - Demo Bridge SolidWorks
=========================================
Script de demonstration du module sw_bridge.py

Ce script montre les differents cas d'usage du pont
SolidWorks <-> DestriChiffrage sans necessiter SolidWorks ouvert.

Il simule des donnees de quincailleries typiques d'un projet SWOOD
et les synchronise avec catalogue.db.

Usage:
    python sw_bridge_demo.py
"""

import os
import sys
import json
from datetime import datetime

# Ajouter le dossier src au path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from database import Database
from sw_bridge import SolidWorksBridge, DEFAULT_HARDWARE_CATEGORY


def print_header(title: str):
    """Affiche un titre formate."""
    print(f"\n{'='*60}")
    print(f"  {title}")
    print(f"{'='*60}")


def print_section(title: str):
    """Affiche un sous-titre."""
    print(f"\n--- {title} ---")


def demo_data():
    """Retourne des donnees de quincailleries simulees (typiques projet SWOOD)."""
    return [
        {
            'name': 'Charniere_Blum_110-1',
            'path': 'C:/SWOOD/Hardwares/Charniere_Blum_110.SLDPRT',
            'is_hardware': True,
            'swood_type': 'HARDWARE',
            'depth': 2,
            'properties': {
                'Code': 'BLUM-71B3550',
                'Supplier': 'BLUM',
                'Supplier_Reference': '71B3550',
                'Cost': '2.85',
                'FOURNISSEUR': 'BLUM',
                'DESCRIPTION': 'Charniere CLIP top 110 degrés',
                'SWOOD_TYPE': 'HARDWARE',
                'FINISH': 'Nickelé',
            },
            'code': 'BLUM-71B3550',
            'supplier': 'BLUM',
            'supplier_reference': '71B3550',
            'cost': 2.85,
            'description': 'Charniere CLIP top 110 degrés',
            'finish': 'Nickele',
            'quantity': 4,
        },
        {
            'name': 'Coulisse_Blum_Tandem-1',
            'path': 'C:/SWOOD/Hardwares/Coulisse_Blum_Tandem_550.SLDPRT',
            'is_hardware': True,
            'swood_type': 'HARDWARE',
            'depth': 2,
            'properties': {
                'Code': 'BLUM-560H5500B',
                'Supplier': 'BLUM',
                'Supplier_Reference': '560H5500B',
                'Cost': '18.50',
                'FOURNISSEUR': 'BLUM',
                'DESCRIPTION': 'Coulisse TANDEM 550mm charge 30kg',
                'SWOOD_TYPE': 'HARDWARE',
            },
            'code': 'BLUM-560H5500B',
            'supplier': 'BLUM',
            'supplier_reference': '560H5500B',
            'cost': 18.50,
            'description': 'Coulisse TANDEM 550mm charge 30kg',
            'finish': '',
            'quantity': 2,
        },
        {
            'name': 'Poignee_Hettich_ProDecor-1',
            'path': 'C:/SWOOD/Hardwares/Poignee_ProDecor.SLDPRT',
            'is_hardware': True,
            'swood_type': 'HARDWARE',
            'depth': 2,
            'properties': {
                'Code': 'HETT-9103362',
                'Supplier': 'HETTICH',
                'Supplier_Reference': '9103362',
                'Cost': '5.20',
                'FOURNISSEUR': 'HETTICH',
                'DESCRIPTION': 'Poignee ProDecor 128mm Inox',
                'SWOOD_TYPE': 'HARDWARE',
                'FINISH': 'Inox brosse',
            },
            'code': 'HETT-9103362',
            'supplier': 'HETTICH',
            'supplier_reference': '9103362',
            'cost': 5.20,
            'description': 'Poignee ProDecor 128mm Inox',
            'finish': 'Inox brosse',
            'quantity': 3,
        },
        {
            'name': 'Vis_Spax_4x30-1',
            'path': 'C:/SWOOD/Hardwares/Vis_Spax_4x30.SLDPRT',
            'is_hardware': True,
            'swood_type': 'HARDWARE',
            'depth': 3,
            'properties': {
                'Code': 'SPAX-0251010400305',
                'Supplier': 'SPAX',
                'Cost': '0.03',
                'DESCRIPTION': 'Vis SPAX 4x30mm tete fraisee',
                'SWOOD_TYPE': 'HARDWARE',
            },
            'code': 'SPAX-0251010400305',
            'supplier': 'SPAX',
            'supplier_reference': '',
            'cost': 0.03,
            'description': 'Vis SPAX 4x30mm tete fraisee',
            'finish': '',
            'quantity': 48,
        },
        {
            'name': 'Tourillon_8x35-1',
            'path': 'C:/SWOOD/Hardwares/Tourillon_8x35.SLDPRT',
            'is_hardware': True,
            'swood_type': 'HARDWARE',
            'depth': 3,
            'properties': {
                'Code': 'DIVERS-TOUR0835',
                'Supplier': 'DIVERS',
                'Cost': '0.02',
                'DESCRIPTION': 'Tourillon bois 8x35mm',
                'SWOOD_TYPE': 'HARDWARE',
            },
            'code': 'DIVERS-TOUR0835',
            'supplier': 'DIVERS',
            'supplier_reference': '',
            'cost': 0.02,
            'description': 'Tourillon bois 8x35mm',
            'finish': '',
            'quantity': 24,
        },
        {
            'name': 'Amortisseur_Blum_Blumotion-1',
            'path': 'C:/SWOOD/Hardwares/Amortisseur_Blumotion.SLDPRT',
            'is_hardware': True,
            'swood_type': 'HARDWARE',
            'depth': 2,
            'properties': {
                'Code': 'BLUM-973A0500',
                'Supplier': 'BLUM',
                'Cost': '3.40',
                'DESCRIPTION': 'Amortisseur BLUMOTION pour charniere',
                'SWOOD_TYPE': 'HARDWARE',
            },
            'code': 'BLUM-973A0500',
            'supplier': 'BLUM',
            'supplier_reference': '973A0500',
            'cost': 3.40,
            'description': 'Amortisseur BLUMOTION pour charniere',
            'finish': '',
            'quantity': 4,
        },
    ]


def demo_1_sync_to_db(bridge, db):
    """Demo 1: Synchroniser les quincailleries SolidWorks vers la BDD."""
    print_header("DEMO 1: Synchronisation SolidWorks -> catalogue.db")
    print("Scenario: Un assemblage SWOOD contient 6 quincailleries.")
    print("Le bridge les lit et les cree/met a jour dans la BDD.\n")

    components = demo_data()
    print(f"Composants detectes dans l'assemblage: {len(components)}")
    for c in components:
        print(f"  [{c['code']}] {c['description']} x{c['quantity']} - {c['cost']:.2f} EUR")

    print_section("Execution de la synchronisation")
    stats = bridge.sync_hardware_to_db(
        components=components,
        create_if_missing=True,
        update_prices=True
    )

    print(f"\nResultats:")
    print(f"  Crees:       {stats['created']}")
    print(f"  Mis a jour:  {stats['updated']}")
    print(f"  Ignores:     {stats['skipped']}")
    print(f"  Erreurs:     {stats['errors']}")

    # Verifier en BDD
    print_section("Verification dans la BDD")
    produits = db.search_produits(categorie=DEFAULT_HARDWARE_CATEGORY, actif_only=True, limit=0)
    print(f"Produits en categorie '{DEFAULT_HARDWARE_CATEGORY}': {len(produits)}")
    for p in produits:
        print(f"  ID:{p['id']:3d} | {p['reference']:25s} | {p['designation']:40s} | {p['prix_achat']:8.2f} EUR | {p['fournisseur']}")


def demo_2_db_to_solidworks(bridge, db):
    """Demo 2: Recuperer les donnees BDD pour les injecter dans SolidWorks."""
    print_header("DEMO 2: catalogue.db -> Proprietes SolidWorks")
    print("Scenario: Les prix ont ete mis a jour dans DestriChiffrage.")
    print("On veut repercuter les nouveaux prix dans les proprietes SW.\n")

    # Simuler une mise a jour de prix dans la BDD
    produits = db.search_produits(categorie=DEFAULT_HARDWARE_CATEGORY, actif_only=True, limit=0)
    updated_count = 0
    for p in produits:
        if p.get('reference', '').startswith('BLUM-71B3550'):
            # Simuler une hausse de prix
            new_price = p['prix_achat'] * 1.05  # +5%
            db.update_produit(p['id'], {
                **{k: p.get(k, '') for k in ['categorie', 'sous_categorie', 'sous_categorie_2',
                                               'sous_categorie_3', 'designation', 'description',
                                               'dimensions', 'hauteur', 'largeur', 'reference',
                                               'fournisseur', 'marque', 'chantier', 'notes',
                                               'fiche_technique', 'devis_fournisseur']},
                'prix_achat': new_price,
            })
            print(f"  Prix mis a jour dans BDD: {p['reference']} -> {new_price:.2f} EUR (+5%)")
            updated_count += 1

    print(f"\n{updated_count} prix mis a jour dans la BDD.")
    print("\nEn mode reel, le bridge ecrirait ces proprietes dans SolidWorks:")
    print("  cpm.Add3('Cost', 3, '2.99', 1)  # Nouveau prix")
    print("  cpm.Add3('Supplier', 30, 'BLUM', 1)")
    print("  cpm.Add3('Supplier_Reference', 30, '71B3550', 1)")

    # Montrer les proprietes qui seraient ecrites
    components = demo_data()
    print_section("Proprietes a ecrire dans SolidWorks")
    for comp in components:
        code = comp.get('code', '').strip()
        prods = db.search_produits(terme=code, actif_only=True, limit=5)
        for prod in prods:
            if prod.get('reference', '').strip().upper() == code.upper():
                print(f"\n  Composant: {comp['name']}")
                print(f"    Code             = {prod['reference']}")
                print(f"    Supplier         = {prod['fournisseur']}")
                print(f"    Cost             = {prod['prix_achat']:.2f}")
                print(f"    DESCRIPTION      = {prod['designation']}")
                break


def demo_3_supplier_order(bridge):
    """Demo 3: Generer une commande fournisseur."""
    print_header("DEMO 3: Generation commande fournisseur")
    print("Scenario: Depuis l'assemblage, generer un CSV de commande")
    print("regroupe par fournisseur avec quantites cumulees.\n")

    components = demo_data()

    # Generer dans un dossier temporaire
    output_dir = os.path.join(os.path.expanduser('~'), 'Documents')
    os.makedirs(output_dir, exist_ok=True)
    output_path = os.path.join(output_dir, 'demo_commande_fournisseur.csv')

    path = bridge.generate_supplier_order(
        components=components,
        output_path=output_path,
        group_by_supplier=True
    )

    if path:
        print(f"Fichier genere: {path}")
        print_section("Apercu du fichier")
        with open(path, 'r', encoding='utf-8-sig') as f:
            for line in f.readlines():
                print(f"  {line.rstrip()}")


def demo_4_csv_import(bridge, db):
    """Demo 4: Import depuis un CSV de Report SWOOD."""
    print_header("DEMO 4: Import CSV Report SWOOD (mode hors-ligne)")
    print("Scenario: Le Report SWOOD a genere un CSV des quincailleries.")
    print("On l'importe dans catalogue.db sans SolidWorks.\n")

    # Creer un fichier CSV de demonstration
    csv_path = os.path.join(os.path.expanduser('~'), 'Documents', 'demo_report_swood.csv')

    import csv
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f, delimiter=';')
        writer.writerow(['Code', 'Supplier', 'Supplier_Reference', 'Cost',
                         'FOURNISSEUR', 'Description', 'Quantity'])
        writer.writerow(['GRASS-4552', 'GRASS', 'Nova Pro Scala 550', '24.50',
                         'GRASS', 'Coulisse Nova Pro Scala 550mm', '4'])
        writer.writerow(['HAFELE-361.55.250', 'HAFELE', '361.55.250', '12.80',
                         'HAFELE', 'Pied reglable 100-135mm inox', '8'])
        writer.writerow(['HETT-1076696', 'HETTICH', '1076696', '7.60',
                         'HETTICH', 'Push to Open Silent 40N', '6'])

    print(f"CSV de demo cree: {csv_path}")

    # Importer
    components = bridge.import_from_report_csv(csv_path)
    print(f"Composants lus: {len(components)}")
    for c in components:
        print(f"  [{c['code']}] {c['description']} x{c['quantity']} - {c['cost']:.2f} EUR ({c['supplier']})")

    # Synchroniser
    print_section("Synchronisation vers la BDD")
    stats = bridge.sync_hardware_to_db(components, create_if_missing=True)
    print(f"  Crees: {stats['created']}, Mis a jour: {stats['updated']}, Erreurs: {stats['errors']}")

    # Nettoyage
    os.remove(csv_path)


def demo_5_export_for_swood(bridge, db):
    """Demo 5: Exporter la BDD vers un format SWOOD."""
    print_header("DEMO 5: Export BDD -> Format SWOOD")
    print("Scenario: Exporter les quincailleries du catalogue en CSV/JSON")
    print("pour alimenter les proprietes personnalisees SolidWorks.\n")

    # Export CSV
    csv_path = bridge.export_db_for_swood(format_type='csv')
    if csv_path:
        print(f"CSV genere: {csv_path}")
        with open(csv_path, 'r', encoding='utf-8-sig') as f:
            lines = f.readlines()
            for line in lines[:10]:  # Apercu des 10 premieres lignes
                print(f"  {line.rstrip()}")
            if len(lines) > 10:
                print(f"  ... ({len(lines)-1} lignes au total)")

    # Export JSON
    print()
    json_path = bridge.export_db_for_swood(format_type='json')
    if json_path:
        print(f"JSON genere: {json_path}")
        with open(json_path, 'r', encoding='utf-8') as f:
            data = json.load(f)
            print(f"  {len(data)} produits exportes")
            if data:
                print(f"  Exemple: {json.dumps(data[0], ensure_ascii=False, indent=4)}")


def demo_6_mapping_report_cfg():
    """Demo 6: Montrer le mapping Report.cfg <-> catalogue.db."""
    print_header("DEMO 6: Mapping Report de travail.Cfg <-> catalogue.db")
    print("Comment les variables SWOOD Report correspondent aux champs BDD.\n")

    mapping = [
        ("Report.cfg Variable", "Propriete SW (SWCP)", "Champ catalogue.db", "Direction"),
        ("-" * 25, "-" * 25, "-" * 25, "-" * 15),
        ("TO_Q_CODE", "Code", "reference", "SW -> BDD"),
        ("TO_Q_F", "Supplier", "fournisseur", "SW <-> BDD"),
        ("TO_Q_R", "Supplier_Reference", "reference", "SW <-> BDD"),
        ("TO_Q_UC", "Cost", "prix_achat", "BDD -> SW"),
        ("TO_Q_FOURNISSEUR", "FOURNISSEUR", "fournisseur", "BDD -> SW"),
        ("PRODUCT_DESC", "PRODUCT_DESC", "designation", "SW <-> BDD"),
        ("Width", "Width", "largeur", "SW -> BDD"),
        ("Height", "Height", "hauteur", "SW -> BDD"),
        ("FINISH", "FINISH", "notes/sous_cat", "SW -> BDD"),
        ("NUM_PRODUCT_EXT", "NUM_PRODUCT_EXT", "(auto-numero)", "SW -> Report"),
        ("NUM_PANEL_EXT", "NUM_PANEL_EXT", "(auto-numero)", "SW -> Report"),
        ("REPORT_CAM", "REPORT_CAM", "(controle FAO)", "BDD -> SW"),
    ]

    for row in mapping:
        print(f"  {row[0]:25s} | {row[1]:25s} | {row[2]:25s} | {row[3]}")

    print("\n  LEGENDE:")
    print("  SW -> BDD  : La donnee est lue dans SolidWorks et ecrite dans catalogue.db")
    print("  BDD -> SW  : La donnee est lue dans catalogue.db et ecrite dans SolidWorks")
    print("  SW <-> BDD : Synchronisation bidirectionnelle")

    print("\n  FLUX DE SYNCHRONISATION:")
    print("  1. Ouverture assemblage SWOOD")
    print("     -> sw_bridge.traverse_assembly() lit les proprietes des composants")
    print("  2. Pour chaque quincaillerie (TypedObject HA):")
    print("     -> Lecture <SWCP.Code> pour identifier le produit")
    print("     -> Recherche dans catalogue.db par reference")
    print("  3. Synchronisation:")
    print("     -> Si prix BDD plus recent: Ecriture <SWCP.Cost> dans SolidWorks")
    print("     -> Si nouveau composant: Creation dans catalogue.db")
    print("  4. Generation commande fournisseur:")
    print("     -> Regroupement par <SWCP.Supplier>/<SWCP.FOURNISSEUR>")
    print("     -> Cumul des quantites depuis l'assemblage")
    print("     -> Export CSV avec prix depuis catalogue.db")


def main():
    """Point d'entree principal de la demo."""
    print_header("DEMONSTRATION sw_bridge.py")
    print("Pont SolidWorks / SWOOD <-> DestriChiffrage")
    print(f"Date: {datetime.now().strftime('%d/%m/%Y %H:%M')}")
    print(f"Mode: Simulation (sans SolidWorks)")

    # Initialiser la BDD (en memoire pour la demo, ou vraie BDD si disponible)
    import tempfile
    demo_db_path = os.path.join(tempfile.gettempdir(), 'demo_sw_bridge.db')
    demo_data_dir = tempfile.gettempdir()

    print(f"\nBDD de demo: {demo_db_path}")

    db = Database(db_path=demo_db_path, data_dir=demo_data_dir)
    bridge = SolidWorksBridge(database=db)

    # Executer les demos
    try:
        demo_1_sync_to_db(bridge, db)
        demo_2_db_to_solidworks(bridge, db)
        demo_3_supplier_order(bridge)
        demo_4_csv_import(bridge, db)
        demo_5_export_for_swood(bridge, db)
        demo_6_mapping_report_cfg()

        # Afficher le journal complet
        print_header("JOURNAL DES OPERATIONS")
        for entry in bridge.get_log():
            print(f"  {entry}")

        print_header("RESUME")
        total_prods = db.count_produits(DEFAULT_HARDWARE_CATEGORY)
        print(f"Produits '{DEFAULT_HARDWARE_CATEGORY}' en BDD: {total_prods}")
        print(f"Operations logguees: {len(bridge.get_log())}")
        print(f"\nLe module sw_bridge.py est pret pour l'integration!")
        print(f"Prochaine etape: Connecter a SolidWorks avec bridge.connect_solidworks()")

    finally:
        # Nettoyage
        db.conn.close()
        if os.path.exists(demo_db_path):
            os.remove(demo_db_path)
            print(f"\nBDD de demo nettoyee.")


if __name__ == '__main__':
    main()
