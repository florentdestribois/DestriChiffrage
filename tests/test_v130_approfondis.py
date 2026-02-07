"""
DestriChiffrage - Tests Approfondis v1.3.0
===========================================
Tests exhaustifs pour les nouvelles fonctionnalites v1.3.0:
- Champs nom_client et type_marche dans les chantiers
- Champs description et taux_tva dans les articles
- Export Odoo CSV
- Filtre par type de marche dans l'analyse
- Import DPGF avec description et TVA
- Liaisons inter-fonctions
"""

import os
import sys
import tempfile
import shutil
import csv

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database


class TestResults:
    """Classe pour collecter les resultats des tests"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []
        self.warnings = []

    def success(self, test_name):
        self.passed += 1
        print(f"  [OK] {test_name}")

    def fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  [FAIL] {test_name}: {error}")

    def warn(self, test_name, message):
        self.warnings.append((test_name, message))
        print(f"  [WARN] {test_name}: {message}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*70}")
        print(f"RESULTATS: {self.passed}/{total} tests reussis")
        if self.warnings:
            print(f"\nAvertissements ({len(self.warnings)}):")
            for name, msg in self.warnings:
                print(f"  - {name}: {msg}")
        if self.errors:
            print(f"\nErreurs ({len(self.errors)}):")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print(f"{'='*70}")
        return self.failed == 0


# ==============================================================================
# TESTS DES NOUVEAUX CHAMPS CHANTIERS (nom_client, type_marche)
# ==============================================================================

def test_chantier_nom_client(db, results):
    """Test du champ nom_client dans les chantiers"""
    print("\n[TEST] Champ nom_client dans les chantiers")

    try:
        # Test 1: Creation avec nom_client
        data = {
            'nom': 'Chantier Test Client',
            'nom_client': 'Entreprise ABC',
            'type_marche': 'PUBLIC'
        }
        chantier_id = db.add_chantier(data)
        chantier = db.get_chantier(chantier_id)

        if chantier['nom_client'] == 'Entreprise ABC':
            results.success("Creation chantier avec nom_client")
        else:
            results.fail("Creation nom_client", f"Attendu 'Entreprise ABC', obtenu '{chantier['nom_client']}'")

        # Test 2: Modification du nom_client
        update_data = {
            'nom': 'Chantier Test Client',
            'nom_client': 'Societe XYZ',
            'type_marche': 'PUBLIC'
        }
        db.update_chantier(chantier_id, update_data)
        chantier = db.get_chantier(chantier_id)

        if chantier['nom_client'] == 'Societe XYZ':
            results.success("Modification nom_client")
        else:
            results.fail("Modification nom_client", f"Non modifie: '{chantier['nom_client']}'")

        # Test 3: Chantier sans nom_client (valeur vide)
        data2 = {
            'nom': 'Chantier Sans Client',
            'type_marche': 'PUBLIC'
        }
        chantier_id2 = db.add_chantier(data2)
        chantier2 = db.get_chantier(chantier_id2)

        if chantier2['nom_client'] == '' or chantier2['nom_client'] is None:
            results.success("Chantier sans nom_client (valeur vide OK)")
        else:
            results.fail("Chantier sans nom_client", f"Valeur inattendue: '{chantier2['nom_client']}'")

        # Cleanup
        db.delete_chantier(chantier_id)
        db.delete_chantier(chantier_id2)

        return True

    except Exception as e:
        results.fail("Champ nom_client", str(e))
        return False


def test_chantier_type_marche(db, results):
    """Test du champ type_marche dans les chantiers"""
    print("\n[TEST] Champ type_marche dans les chantiers")

    types_valides = ['PUBLIC', 'PARTICULIER', 'ODOO']
    chantier_ids = []

    try:
        # Test 1: Creation avec chaque type de marche
        for type_m in types_valides:
            data = {
                'nom': f'Chantier {type_m}',
                'nom_client': 'Client Test' if type_m == 'ODOO' else '',
                'type_marche': type_m
            }
            chantier_id = db.add_chantier(data)
            chantier_ids.append(chantier_id)
            chantier = db.get_chantier(chantier_id)

            if chantier['type_marche'] == type_m:
                results.success(f"Creation chantier type={type_m}")
            else:
                results.fail(f"Type {type_m}", f"Attendu '{type_m}', obtenu '{chantier['type_marche']}'")

        # Test 2: Valeur par defaut (PUBLIC)
        data_defaut = {'nom': 'Chantier Defaut'}
        chantier_defaut_id = db.add_chantier(data_defaut)
        chantier_ids.append(chantier_defaut_id)
        chantier_defaut = db.get_chantier(chantier_defaut_id)

        if chantier_defaut['type_marche'] == 'PUBLIC':
            results.success("Type par defaut = PUBLIC")
        else:
            results.fail("Type par defaut", f"Attendu 'PUBLIC', obtenu '{chantier_defaut['type_marche']}'")

        # Test 3: Changement de type
        db.update_chantier(chantier_ids[0], {
            'nom': 'Chantier PUBLIC',
            'nom_client': 'Nouveau Client',
            'type_marche': 'ODOO'
        })
        chantier_modifie = db.get_chantier(chantier_ids[0])
        if chantier_modifie['type_marche'] == 'ODOO':
            results.success("Changement de type PUBLIC -> ODOO")
        else:
            results.fail("Changement type", f"Non modifie: '{chantier_modifie['type_marche']}'")

        # Cleanup
        for cid in chantier_ids:
            db.delete_chantier(cid)

        return True

    except Exception as e:
        results.fail("Champ type_marche", str(e))
        for cid in chantier_ids:
            try:
                db.delete_chantier(cid)
            except:
                pass
        return False


def test_filtre_type_marche(db, results):
    """Test du filtre par type_marche dans get_chantiers"""
    print("\n[TEST] Filtre par type_marche dans get_chantiers")

    chantier_ids = []

    try:
        # Creer des chantiers de chaque type
        for i, type_m in enumerate(['PUBLIC', 'PUBLIC', 'PARTICULIER', 'ODOO', 'ODOO']):
            data = {
                'nom': f'Chantier Filtre {i+1}',
                'nom_client': f'Client {i+1}' if type_m == 'ODOO' else '',
                'type_marche': type_m
            }
            chantier_ids.append(db.add_chantier(data))

        # Test filtres
        # Filtre PUBLIC (devrait retourner au moins 2)
        chantiers_public = db.get_chantiers(type_marche='PUBLIC')
        nb_public = len([c for c in chantiers_public if c['id'] in chantier_ids])
        if nb_public == 2:
            results.success(f"Filtre PUBLIC: {nb_public} chantiers")
        else:
            results.fail("Filtre PUBLIC", f"Attendu 2, obtenu {nb_public}")

        # Filtre PARTICULIER (devrait retourner 1)
        chantiers_part = db.get_chantiers(type_marche='PARTICULIER')
        nb_part = len([c for c in chantiers_part if c['id'] in chantier_ids])
        if nb_part == 1:
            results.success(f"Filtre PARTICULIER: {nb_part} chantier")
        else:
            results.fail("Filtre PARTICULIER", f"Attendu 1, obtenu {nb_part}")

        # Filtre ODOO (devrait retourner 2)
        chantiers_odoo = db.get_chantiers(type_marche='ODOO')
        nb_odoo = len([c for c in chantiers_odoo if c['id'] in chantier_ids])
        if nb_odoo == 2:
            results.success(f"Filtre ODOO: {nb_odoo} chantiers")
        else:
            results.fail("Filtre ODOO", f"Attendu 2, obtenu {nb_odoo}")

        # Sans filtre (tous)
        tous_chantiers = db.get_chantiers()
        nb_tous = len([c for c in tous_chantiers if c['id'] in chantier_ids])
        if nb_tous == 5:
            results.success(f"Sans filtre: {nb_tous} chantiers")
        else:
            results.fail("Sans filtre", f"Attendu 5, obtenu {nb_tous}")

        # Filtre combine (resultat + type_marche)
        # Modifier un chantier pour le test
        db.update_chantier(chantier_ids[0], {
            'nom': 'Chantier Filtre 1',
            'type_marche': 'PUBLIC',
            'resultat': 'GAGNE'
        })
        chantiers_gagne_public = db.get_chantiers(resultat='GAGNE', type_marche='PUBLIC')
        nb_gagne_public = len([c for c in chantiers_gagne_public if c['id'] in chantier_ids])
        if nb_gagne_public >= 1:
            results.success(f"Filtre combine GAGNE+PUBLIC: {nb_gagne_public} chantier(s)")
        else:
            results.fail("Filtre combine", f"Aucun resultat pour GAGNE+PUBLIC")

        # Cleanup
        for cid in chantier_ids:
            db.delete_chantier(cid)

        return True

    except Exception as e:
        results.fail("Filtre type_marche", str(e))
        for cid in chantier_ids:
            try:
                db.delete_chantier(cid)
            except:
                pass
        return False


# ==============================================================================
# TESTS DES NOUVEAUX CHAMPS ARTICLES (description, taux_tva)
# ==============================================================================

def test_article_description(db, results):
    """Test du champ description dans les articles DPGF"""
    print("\n[TEST] Champ description dans les articles DPGF")

    try:
        chantier_id = db.add_chantier({'nom': 'Test Description'})

        # Test 1: Creation avec description
        data = {
            'code': 'DESC-001',
            'designation': 'Porte avec description',
            'description': 'Porte coupe-feu EI60, finition blanc RAL9010, pose comprise',
            'unite': 'U',
            'quantite': 3
        }
        article_id = db.add_article_dpgf(chantier_id, data)
        article = db.get_article_dpgf(article_id)

        if article['description'] == data['description']:
            results.success("Creation article avec description longue")
        else:
            results.fail("Creation description", f"Description non enregistree")

        # Test 2: Modification de la description
        update_data = {
            'code': 'DESC-001',
            'designation': 'Porte avec description',
            'description': 'Description modifiee avec caracteres speciaux: e, a, etc.'
        }
        db.update_article_dpgf(article_id, update_data)
        article = db.get_article_dpgf(article_id)

        if 'modifiee' in article['description']:
            results.success("Modification description")
        else:
            results.fail("Modification description", "Non modifiee")

        # Test 3: Article sans description
        data2 = {
            'code': 'DESC-002',
            'designation': 'Porte sans description',
            'unite': 'U',
            'quantite': 1
        }
        article_id2 = db.add_article_dpgf(chantier_id, data2)
        article2 = db.get_article_dpgf(article_id2)

        if article2['description'] == '' or article2['description'] is None:
            results.success("Article sans description (valeur vide OK)")
        else:
            results.fail("Sans description", f"Valeur inattendue: '{article2['description']}'")

        # Test 4: Description avec retours a la ligne
        data3 = {
            'code': 'DESC-003',
            'designation': 'Porte description multiligne',
            'description': 'Ligne 1\nLigne 2\nLigne 3',
            'unite': 'U',
            'quantite': 1
        }
        article_id3 = db.add_article_dpgf(chantier_id, data3)
        article3 = db.get_article_dpgf(article_id3)

        if '\n' in article3['description']:
            results.success("Description multiligne preservee")
        else:
            results.fail("Description multiligne", "Retours a la ligne perdus")

        # Cleanup
        db.delete_chantier(chantier_id)

        return True

    except Exception as e:
        results.fail("Champ description", str(e))
        return False


def test_article_taux_tva(db, results):
    """Test du champ taux_tva dans les articles DPGF"""
    print("\n[TEST] Champ taux_tva dans les articles DPGF")

    taux_valides = [0, 5.5, 10, 20]

    try:
        chantier_id = db.add_chantier({'nom': 'Test TVA'})

        # Test 1: Creation avec chaque taux de TVA
        for taux in taux_valides:
            data = {
                'code': f'TVA-{int(taux*10):03d}',
                'designation': f'Article TVA {taux}%',
                'unite': 'U',
                'quantite': 1,
                'taux_tva': taux
            }
            article_id = db.add_article_dpgf(chantier_id, data)
            article = db.get_article_dpgf(article_id)

            if abs(article['taux_tva'] - taux) < 0.01:
                results.success(f"Creation article taux_tva={taux}%")
            else:
                results.fail(f"TVA {taux}%", f"Attendu {taux}, obtenu {article['taux_tva']}")

        # Test 2: Valeur par defaut (20%)
        data_defaut = {
            'code': 'TVA-DEF',
            'designation': 'Article TVA par defaut'
        }
        article_defaut_id = db.add_article_dpgf(chantier_id, data_defaut)
        article_defaut = db.get_article_dpgf(article_defaut_id)

        if article_defaut['taux_tva'] == 20:
            results.success("Taux TVA par defaut = 20%")
        else:
            results.fail("TVA par defaut", f"Attendu 20, obtenu {article_defaut['taux_tva']}")

        # Test 3: Modification du taux TVA
        db.update_article_dpgf(article_defaut_id, {
            'code': 'TVA-DEF',
            'designation': 'Article TVA modifie',
            'taux_tva': 5.5
        })
        article_modifie = db.get_article_dpgf(article_defaut_id)

        if abs(article_modifie['taux_tva'] - 5.5) < 0.01:
            results.success("Modification taux TVA 20% -> 5.5%")
        else:
            results.fail("Modif TVA", f"Non modifie: {article_modifie['taux_tva']}")

        # Cleanup
        db.delete_chantier(chantier_id)

        return True

    except Exception as e:
        results.fail("Champ taux_tva", str(e))
        return False


# ==============================================================================
# TESTS EXPORT ODOO CSV
# ==============================================================================

def test_export_odoo_format(db, results):
    """Test du format d'export Odoo CSV"""
    print("\n[TEST] Format export Odoo CSV")

    try:
        temp_dir = tempfile.mkdtemp()

        # Creer un chantier type Odoo
        chantier_id = db.add_chantier({
            'nom': 'Chantier Export Odoo',
            'nom_client': 'Client Odoo Test',
            'type_marche': 'ODOO',
            'lot': 'REF-2024-001'
        })

        # Ajouter des articles avec description et TVA
        articles_data = [
            {'code': 'A1', 'designation': 'Porte standard', 'description': 'Porte 83x204 blanc', 'quantite': 5, 'taux_tva': 20},
            {'code': 'A2', 'designation': 'Fenetre PVC', 'description': 'Fenetre double vitrage', 'quantite': 3, 'taux_tva': 10},
            {'code': 'A3', 'designation': 'Main oeuvre', 'description': 'Pose et finitions', 'quantite': 1, 'taux_tva': 5.5},
        ]

        for data in articles_data:
            article_id = db.add_article_dpgf(chantier_id, data)
            # Ajouter un produit pour avoir un prix
            produit_id = db.add_produit({'designation': 'Prod test', 'categorie': 'TEST', 'prix_achat': 100})
            db.add_produit_article(article_id, produit_id, 1)

        # Exporter
        export_file = os.path.join(temp_dir, 'export_odoo.csv')
        count = db.export_dpgf_odoo(chantier_id, export_file)

        if count == 3:
            results.success(f"Export Odoo: {count} articles exportes")
        else:
            results.fail("Nombre articles", f"Attendu 3, obtenu {count}")

        # Verifier le contenu du fichier
        with open(export_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

        # Test en-tetes
        headers = rows[0]
        expected_headers = ['Customer*', 'Order Lines/Products*', 'order_line/name',
                          'Order Lines/Quantity', 'Order Lines/Unit Price',
                          'Order Lines/Taxes', 'Customer Reference']

        if headers == expected_headers:
            results.success("En-tetes Odoo corrects")
        else:
            results.fail("En-tetes Odoo", f"Headers incorrects: {headers}")

        # Test premiere ligne (client + premier article)
        if rows[1][0] == 'Client Odoo Test':
            results.success("Nom client en premiere ligne")
        else:
            results.fail("Nom client", f"Attendu 'Client Odoo Test', obtenu '{rows[1][0]}'")

        # Test reference client
        if rows[1][6] == 'REF-2024-001':
            results.success("Reference client (lot) en premiere ligne")
        else:
            results.fail("Reference", f"Attendu 'REF-2024-001', obtenu '{rows[1][6]}'")

        # Test format TVA (doit etre "X% Ser")
        tva_values = [rows[1][5], rows[3][5], rows[5][5]]  # Lignes articles (1, 3, 5)
        if all('Ser' in tva for tva in tva_values):
            results.success("Format TVA Odoo 'X% Ser' correct")
        else:
            results.fail("Format TVA", f"Format incorrect: {tva_values}")

        # Test lignes description (doivent etre sur lignes separees)
        # Structure: Article 1 (ligne 1), Description 1 (ligne 2), Article 2 (ligne 3), etc.
        if rows[2][2] == 'Porte 83x204 blanc':
            results.success("Description sur ligne separee")
        else:
            results.fail("Description separee", f"Description incorrecte ligne 2: '{rows[2][2]}'")

        # Test que les lignes suivantes n'ont pas le client
        if rows[3][0] == '' and rows[5][0] == '':
            results.success("Client absent des lignes suivantes")
        else:
            results.fail("Client lignes suivantes", "Client present sur plusieurs lignes")

        # Cleanup
        db.delete_chantier(chantier_id)
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        results.fail("Export Odoo", str(e))
        return False


def test_export_odoo_sans_client(db, results):
    """Test export Odoo quand nom_client est vide (doit utiliser le nom du chantier)"""
    print("\n[TEST] Export Odoo sans nom_client (fallback sur nom chantier)")

    try:
        temp_dir = tempfile.mkdtemp()

        # Creer un chantier sans nom_client
        chantier_id = db.add_chantier({
            'nom': 'Chantier Fallback',
            'nom_client': '',  # Vide
            'type_marche': 'ODOO'
        })

        # Ajouter un article
        db.add_article_dpgf(chantier_id, {
            'code': 'FB-1',
            'designation': 'Article Fallback',
            'quantite': 1
        })

        # Exporter
        export_file = os.path.join(temp_dir, 'export_fallback.csv')
        db.export_dpgf_odoo(chantier_id, export_file)

        # Verifier
        with open(export_file, 'r', encoding='utf-8-sig') as f:
            reader = csv.reader(f, delimiter=';')
            rows = list(reader)

        # Le nom du chantier doit etre utilise si nom_client est vide
        if rows[1][0] == 'Chantier Fallback':
            results.success("Fallback sur nom chantier quand nom_client vide")
        else:
            results.fail("Fallback client", f"Attendu 'Chantier Fallback', obtenu '{rows[1][0]}'")

        # Cleanup
        db.delete_chantier(chantier_id)
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        results.fail("Export Odoo fallback", str(e))
        return False


# ==============================================================================
# TESTS IMPORT DPGF AVEC DESCRIPTION ET TVA
# ==============================================================================

def test_import_dpgf_description_tva(db, results):
    """Test import DPGF CSV avec colonnes DESCRIPTION et TVA"""
    print("\n[TEST] Import DPGF avec DESCRIPTION et TVA")

    try:
        temp_dir = tempfile.mkdtemp()
        dpgf_file = os.path.join(temp_dir, 'import_test.csv')

        # Creer un fichier DPGF avec DESCRIPTION et TVA
        with open(dpgf_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['CODE', 'NIVEAU', 'DESIGNATION', 'DESCRIPTION', 'UNITE', 'QUANTITE', 'TVA'])
            writer.writerow(['1', '1', 'LOT MENUISERIES', '', '', '', ''])
            writer.writerow(['1.1', '4', 'Porte simple', 'Porte isoplane 83x204', 'U', '10', '20'])
            writer.writerow(['1.2', '4', 'Porte CF', 'Porte coupe-feu EI60', 'U', '5', '10'])
            writer.writerow(['1.3', '4', 'Main oeuvre', 'Pose et finitions', 'H', '20', '5.5'])

        # Importer
        chantier_id = db.add_chantier({'nom': 'Import Test Desc TVA'})
        count = db.import_dpgf_csv(chantier_id, dpgf_file)

        if count == 3:
            results.success(f"Import: {count} articles importes")
        else:
            results.fail("Nombre import", f"Attendu 3, obtenu {count}")

        # Verifier les articles
        articles = db.get_articles_dpgf(chantier_id)

        # Trouver chaque article et verifier
        art_simple = next((a for a in articles if a['code'] == '1.1'), None)
        art_cf = next((a for a in articles if a['code'] == '1.2'), None)
        art_mo = next((a for a in articles if a['code'] == '1.3'), None)

        # Test descriptions
        if art_simple and 'isoplane' in art_simple['description']:
            results.success("Description article 1.1 importee")
        else:
            results.fail("Description 1.1", f"Description incorrecte: {art_simple}")

        if art_cf and 'EI60' in art_cf['description']:
            results.success("Description article 1.2 importee")
        else:
            results.fail("Description 1.2", f"Description incorrecte: {art_cf}")

        # Test TVA
        if art_simple and art_simple['taux_tva'] == 20:
            results.success("TVA 20% importee pour article 1.1")
        else:
            results.fail("TVA 1.1", f"TVA incorrecte: {art_simple.get('taux_tva') if art_simple else 'None'}")

        if art_cf and art_cf['taux_tva'] == 10:
            results.success("TVA 10% importee pour article 1.2")
        else:
            results.fail("TVA 1.2", f"TVA incorrecte: {art_cf.get('taux_tva') if art_cf else 'None'}")

        if art_mo and abs(art_mo['taux_tva'] - 5.5) < 0.01:
            results.success("TVA 5.5% importee pour article 1.3")
        else:
            results.fail("TVA 1.3", f"TVA incorrecte: {art_mo.get('taux_tva') if art_mo else 'None'}")

        # Cleanup
        db.delete_chantier(chantier_id)
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        results.fail("Import DPGF desc/tva", str(e))
        return False


def test_import_dpgf_sans_description_tva(db, results):
    """Test import DPGF CSV sans colonnes DESCRIPTION et TVA (valeurs par defaut)"""
    print("\n[TEST] Import DPGF sans DESCRIPTION/TVA (valeurs par defaut)")

    try:
        temp_dir = tempfile.mkdtemp()
        dpgf_file = os.path.join(temp_dir, 'import_minimal.csv')

        # Creer un fichier DPGF minimal (sans DESCRIPTION ni TVA)
        with open(dpgf_file, 'w', encoding='utf-8-sig', newline='') as f:
            writer = csv.writer(f, delimiter=';')
            writer.writerow(['CODE', 'NIVEAU', 'DESIGNATION', 'UNITE', 'QUANTITE'])
            writer.writerow(['A1', '4', 'Article minimal', 'U', '5'])

        # Importer
        chantier_id = db.add_chantier({'nom': 'Import Minimal'})
        count = db.import_dpgf_csv(chantier_id, dpgf_file)

        if count == 1:
            results.success("Import minimal: 1 article importe")
        else:
            results.fail("Import minimal", f"Attendu 1, obtenu {count}")

        # Verifier valeurs par defaut
        articles = db.get_articles_dpgf(chantier_id)
        if articles:
            art = articles[0]
            if art['description'] == '' or art['description'] is None:
                results.success("Description vide par defaut")
            else:
                results.fail("Desc defaut", f"Description non vide: '{art['description']}'")

            if art['taux_tva'] == 20:
                results.success("TVA 20% par defaut")
            else:
                results.fail("TVA defaut", f"TVA incorrecte: {art['taux_tva']}")
        else:
            results.fail("Articles", "Aucun article trouve")

        # Cleanup
        db.delete_chantier(chantier_id)
        shutil.rmtree(temp_dir)

        return True

    except Exception as e:
        results.fail("Import minimal", str(e))
        return False


# ==============================================================================
# TESTS LIAISONS INTER-FONCTIONS
# ==============================================================================

def test_liaison_chantier_articles(db, results):
    """Test liaison entre chantiers et articles (cascade, montant)"""
    print("\n[TEST] Liaison chantier <-> articles")

    try:
        # Creer chantier avec articles
        chantier_id = db.add_chantier({
            'nom': 'Liaison Test',
            'nom_client': 'Client Liaison',
            'type_marche': 'PARTICULIER'
        })

        article_ids = []
        for i in range(3):
            article_id = db.add_article_dpgf(chantier_id, {
                'code': f'LIA-{i+1}',
                'designation': f'Article liaison {i+1}',
                'description': f'Description {i+1}',
                'quantite': i + 1,
                'taux_tva': 20
            })
            article_ids.append(article_id)
            # Ajouter produit pour prix
            prod_id = db.add_produit({'designation': f'Prod {i}', 'categorie': 'TEST', 'prix_achat': 100 * (i+1)})
            db.add_produit_article(article_id, prod_id, 1)

        # Verifier que les articles sont lies au chantier
        articles = db.get_articles_dpgf(chantier_id)
        if len(articles) == 3:
            results.success("3 articles lies au chantier")
        else:
            results.fail("Articles lies", f"Attendu 3, obtenu {len(articles)}")

        # Mettre a jour le montant du chantier
        db.update_chantier_montant(chantier_id)
        chantier = db.get_chantier(chantier_id)
        if chantier['montant_ht'] > 0:
            results.success(f"Montant chantier calcule: {chantier['montant_ht']:.2f} EUR")
        else:
            results.fail("Montant chantier", "Montant nul")

        # Supprimer le chantier (cascade)
        db.delete_chantier(chantier_id)

        # Verifier que les articles sont supprimes
        for article_id in article_ids:
            article = db.get_article_dpgf(article_id)
            if article is None:
                pass  # OK, supprime
            else:
                results.fail("Cascade article", f"Article {article_id} non supprime")
                return False

        results.success("Suppression cascade articles OK")

        return True

    except Exception as e:
        results.fail("Liaison chantier-articles", str(e))
        return False


def test_liaison_article_produits(db, results):
    """Test liaison entre articles et produits du catalogue"""
    print("\n[TEST] Liaison article <-> produits catalogue")

    try:
        chantier_id = db.add_chantier({'nom': 'Liaison Produits'})

        article_id = db.add_article_dpgf(chantier_id, {
            'code': 'PROD-LIA',
            'designation': 'Article avec produits',
            'marge_pct': 25
        })

        # Creer des produits
        prod_ids = []
        for i, prix in enumerate([100, 200, 50]):
            prod_id = db.add_produit({
                'designation': f'Produit liaison {i+1}',
                'categorie': 'TEST',
                'prix_achat': prix
            })
            prod_ids.append(prod_id)
            db.add_produit_article(article_id, prod_id, i + 1)

        # Verifier les produits lies
        produits = db.get_produits_article(article_id)
        if len(produits) == 3:
            results.success("3 produits lies a l'article")
        else:
            results.fail("Produits lies", f"Attendu 3, obtenu {len(produits)}")

        # Recalculer et verifier le cout
        db.recalculer_article_dpgf(article_id)
        article = db.get_article_dpgf(article_id)

        # Cout = 100*1 + 200*2 + 50*3 = 650
        expected_cout = 100 * 1 + 200 * 2 + 50 * 3
        if abs(article['cout_materiaux'] - expected_cout) < 0.01:
            results.success(f"Cout materiaux calcule: {article['cout_materiaux']:.2f} EUR")
        else:
            results.fail("Cout materiaux", f"Attendu {expected_cout}, obtenu {article['cout_materiaux']}")

        # Supprimer un produit de l'article
        liaison = db.get_produits_article(article_id)[0]
        db.remove_produit_article(liaison['id'])
        produits_apres = db.get_produits_article(article_id)
        if len(produits_apres) == 2:
            results.success("Produit retire de l'article")
        else:
            results.fail("Retrait produit", f"Attendu 2, obtenu {len(produits_apres)}")

        # Cleanup
        db.delete_chantier(chantier_id)
        for prod_id in prod_ids:
            db.delete_produit(prod_id, permanent=True)

        return True

    except Exception as e:
        results.fail("Liaison article-produits", str(e))
        return False


def test_workflow_complet_odoo(db, results):
    """Test du workflow complet: creation chantier -> articles -> export Odoo"""
    print("\n[TEST] Workflow complet Odoo (creation -> chiffrage -> export)")

    try:
        temp_dir = tempfile.mkdtemp()

        # 1. Creer chantier type Odoo
        chantier_id = db.add_chantier({
            'nom': 'Workflow Odoo Complet',
            'nom_client': 'Client Workflow',
            'type_marche': 'ODOO',
            'lieu': 'Paris',
            'lot': 'LOT-WF-001'
        })
        results.success("1. Chantier Odoo cree")

        # 2. Creer des produits
        prod1 = db.add_produit({'designation': 'Porte standard', 'categorie': 'PORTES', 'prix_achat': 250})
        prod2 = db.add_produit({'designation': 'Serrure', 'categorie': 'QUINCAILLERIE', 'prix_achat': 80})
        results.success("2. Produits crees")

        # 3. Creer articles avec description et TVA
        art1 = db.add_article_dpgf(chantier_id, {
            'code': 'WF-001',
            'designation': 'Porte complete',
            'description': 'Porte isoplane blanc avec serrure 3 points',
            'quantite': 5,
            'taux_tva': 20,
            'temps_fabrication': 2,
            'temps_pose': 1,
            'marge_pct': 30
        })
        db.add_produit_article(art1, prod1, 1)
        db.add_produit_article(art1, prod2, 1)

        art2 = db.add_article_dpgf(chantier_id, {
            'code': 'WF-002',
            'designation': 'Main oeuvre supplementaire',
            'description': 'Travaux de finition',
            'quantite': 8,
            'taux_tva': 10,
            'temps_pose': 2
        })
        results.success("3. Articles DPGF crees avec produits lies")

        # 4. Recalculer
        db.recalculer_article_dpgf(art1)
        db.recalculer_article_dpgf(art2)
        db.update_chantier_montant(chantier_id)
        chantier = db.get_chantier(chantier_id)
        results.success(f"4. Montant chantier: {chantier['montant_ht']:.2f} EUR")

        # 5. Exporter Odoo
        export_file = os.path.join(temp_dir, 'workflow_odoo.csv')
        count = db.export_dpgf_odoo(chantier_id, export_file)
        if count == 2:
            results.success("5. Export Odoo: 2 articles")
        else:
            results.fail("Export Odoo", f"Attendu 2, obtenu {count}")

        # 6. Verifier le fichier export
        with open(export_file, 'r', encoding='utf-8-sig') as f:
            content = f.read()

        checks = [
            ('Client Workflow' in content, "Client present"),
            ('Porte complete' in content, "Designation article 1"),
            ('Main oeuvre supplementaire' in content, "Designation article 2"),
            ('isoplane' in content, "Description article 1"),
            ('finition' in content, "Description article 2"),
            ('20% Ser' in content, "TVA 20%"),
            ('10% Ser' in content, "TVA 10%"),
            ('LOT-WF-001' in content, "Reference lot"),
        ]

        all_ok = True
        for check, msg in checks:
            if check:
                results.success(f"6. {msg}")
            else:
                results.fail(f"6. {msg}", "Non trouve dans export")
                all_ok = False

        # Cleanup
        db.delete_chantier(chantier_id)
        db.delete_produit(prod1, permanent=True)
        db.delete_produit(prod2, permanent=True)
        shutil.rmtree(temp_dir)

        return all_ok

    except Exception as e:
        results.fail("Workflow Odoo", str(e))
        return False


def test_coherence_statistiques(db, results):
    """Test coherence des statistiques avec les nouveaux types"""
    print("\n[TEST] Coherence statistiques avec types de marche")

    chantier_ids = []

    try:
        # Creer chantiers de differents types avec resultats
        test_data = [
            {'type_marche': 'PUBLIC', 'resultat': 'GAGNE', 'montant_ht': 10000},
            {'type_marche': 'PUBLIC', 'resultat': 'PERDU', 'montant_ht': 15000},
            {'type_marche': 'PARTICULIER', 'resultat': 'GAGNE', 'montant_ht': 5000},
            {'type_marche': 'ODOO', 'resultat': 'GAGNE', 'montant_ht': 8000},
            {'type_marche': 'ODOO', 'resultat': 'EN_COURS', 'montant_ht': 12000},
        ]

        for i, data in enumerate(test_data):
            cid = db.add_chantier({
                'nom': f'Stat Test {i+1}',
                'nom_client': f'Client {i+1}' if data['type_marche'] == 'ODOO' else '',
                **data
            })
            chantier_ids.append(cid)

        # Statistiques globales
        stats = db.get_stats_marches()
        if stats['total_chantiers'] >= 5:
            results.success(f"Total chantiers: >= 5")
        else:
            results.fail("Total", f"< 5 chantiers")

        # Verifier gagnes (3)
        gagnes = stats['par_resultat'].get('GAGNE', 0)
        if gagnes >= 3:
            results.success(f"Chantiers gagnes: >= 3")
        else:
            results.fail("Gagnes", f"Attendu >= 3, obtenu {gagnes}")

        # Verifier montant gagne (10000 + 5000 + 8000 = 23000)
        if stats['montant_gagne'] >= 23000:
            results.success(f"Montant gagne: >= 23000 EUR")
        else:
            results.fail("Montant", f"Attendu >= 23000, obtenu {stats['montant_gagne']}")

        # Verifier filtrage par type ne casse pas les stats
        chantiers_public = db.get_chantiers(type_marche='PUBLIC')
        nb_public = len([c for c in chantiers_public if c['id'] in chantier_ids])
        if nb_public == 2:
            results.success("Filtre PUBLIC coherent: 2")
        else:
            results.warn("Filtre PUBLIC", f"Attendu 2, obtenu {nb_public}")

        # Cleanup
        for cid in chantier_ids:
            db.delete_chantier(cid)

        return True

    except Exception as e:
        results.fail("Statistiques", str(e))
        for cid in chantier_ids:
            try:
                db.delete_chantier(cid)
            except:
                pass
        return False


# ==============================================================================
# TESTS INTEGRATION UI
# ==============================================================================

def test_imports_ui_v130(results):
    """Test des imports UI v1.3.0"""
    print("\n[TEST] Imports modules UI v1.3.0")

    try:
        # Test TYPES_MARCHE
        from ui.dpgf_import_dialog import TYPES_MARCHE
        expected_types = {'PUBLIC', 'PARTICULIER', 'ODOO'}
        if set(TYPES_MARCHE.keys()) == expected_types:
            results.success(f"TYPES_MARCHE: {list(TYPES_MARCHE.keys())}")
        else:
            results.fail("TYPES_MARCHE", f"Types incorrects: {TYPES_MARCHE.keys()}")

        # Test classes importables
        from ui.dpgf_import_dialog import DPGFImportDialog, ChantierEditDialog
        results.success("Import DPGFImportDialog, ChantierEditDialog")

        from ui.dpgf_export_dialog import DPGFExportDialog
        results.success("Import DPGFExportDialog")

        from ui.dpgf_chiffrage_view import DPGFChiffrageView, ArticleDialog
        results.success("Import DPGFChiffrageView, ArticleDialog")

        from ui.marches_analyse_view import MarchesAnalyseView
        results.success("Import MarchesAnalyseView")

        return True

    except Exception as e:
        results.fail("Imports UI", str(e))
        return False


def test_version_130(results):
    """Test version 1.3.0"""
    print("\n[TEST] Version application")

    try:
        from version import __version__
        if __version__ >= "1.3.0":
            results.success(f"Version: {__version__}")
            return True
        else:
            results.fail("Version", f"Version minimum attendue 1.3.0, obtenu {__version__}")
            return False
    except Exception as e:
        results.fail("Version", str(e))
        return False


# ==============================================================================
# EXECUTION PRINCIPALE
# ==============================================================================

def run_all_tests():
    """Execute tous les tests approfondis v1.3.0"""
    print("="*70)
    print("TESTS APPROFONDIS v1.3.0 - DestriChiffrage")
    print("="*70)
    print("\nFonctionnalites testees:")
    print("  - Nouveaux champs chantiers (nom_client, type_marche)")
    print("  - Nouveaux champs articles (description, taux_tva)")
    print("  - Export Odoo CSV")
    print("  - Import DPGF avec description et TVA")
    print("  - Filtre par type de marche")
    print("  - Liaisons inter-fonctions")
    print("  - Workflow complet")

    results = TestResults()

    # Base de donnees temporaire
    temp_dir = tempfile.mkdtemp()

    try:
        db = Database(data_dir=temp_dir)
        print(f"\nBase de test: {temp_dir}")

        # Tests champs chantiers
        test_chantier_nom_client(db, results)
        test_chantier_type_marche(db, results)
        test_filtre_type_marche(db, results)

        # Tests champs articles
        test_article_description(db, results)
        test_article_taux_tva(db, results)

        # Tests export Odoo
        test_export_odoo_format(db, results)
        test_export_odoo_sans_client(db, results)

        # Tests import DPGF
        test_import_dpgf_description_tva(db, results)
        test_import_dpgf_sans_description_tva(db, results)

        # Tests liaisons
        test_liaison_chantier_articles(db, results)
        test_liaison_article_produits(db, results)
        test_workflow_complet_odoo(db, results)
        test_coherence_statistiques(db, results)

        # Tests UI
        test_imports_ui_v130(results)
        test_version_130(results)

    except Exception as e:
        results.fail("Execution tests", str(e))
    finally:
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    # Resume
    success = results.summary()
    return success


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
