"""
DestriChiffrage - Tests complets du module Marches Publics
===========================================================
Tests unitaires et d'integration pour valider toutes les fonctionnalites
"""

import os
import sys
import tempfile
import shutil

# Ajouter le dossier src au path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

from database import Database

class TestResults:
    """Classe pour collecter les resultats des tests"""
    def __init__(self):
        self.passed = 0
        self.failed = 0
        self.errors = []

    def success(self, test_name):
        self.passed += 1
        print(f"  [OK] {test_name}")

    def fail(self, test_name, error):
        self.failed += 1
        self.errors.append((test_name, error))
        print(f"  [FAIL] {test_name}: {error}")

    def summary(self):
        total = self.passed + self.failed
        print(f"\n{'='*60}")
        print(f"RESULTATS: {self.passed}/{total} tests reussis")
        if self.errors:
            print(f"\nErreurs detectees:")
            for name, error in self.errors:
                print(f"  - {name}: {error}")
        print(f"{'='*60}")
        return self.failed == 0


def test_configuration_taux(db, results):
    """Test des taux horaires et marge (nouvelle structure cout/vente)"""
    print("\n[TEST] Configuration des taux horaires et marge")

    try:
        taux = db.get_taux_horaires()
        if 'conception' in taux and 'fabrication' in taux and 'pose' in taux:
            results.success("get_taux_horaires retourne les 3 types de taux")
        else:
            results.fail("get_taux_horaires", f"Taux incomplets: {taux}")

        # Verifier la nouvelle structure avec cout et vente
        if all('cout' in taux[k] and 'vente' in taux[k] for k in taux):
            results.success("Chaque taux contient 'cout' et 'vente'")
        else:
            results.fail("Structure taux", f"Structure invalide: {taux}")

        # Verifier que vente >= cout (marge positive)
        if all(taux[k]['vente'] >= taux[k]['cout'] for k in taux):
            results.success("Prix de vente >= Cout entreprise (marge positive)")
        else:
            results.fail("Marge taux", "Prix de vente < Cout (marge negative)")

        # Test get_taux_horaires_simples (compatibilite)
        taux_simples = db.get_taux_horaires_simples()
        if all(isinstance(v, (int, float)) and v > 0 for v in taux_simples.values()):
            results.success("get_taux_horaires_simples retourne les prix de vente")
        else:
            results.fail("Taux simples", f"Valeurs invalides: {taux_simples}")

        marge = db.get_marge_marche()
        if isinstance(marge, (int, float)) and marge >= 0:
            results.success(f"get_marge_marche retourne {marge}%")
        else:
            results.fail("get_marge_marche", f"Marge invalide: {marge}")

    except Exception as e:
        results.fail("Configuration taux", str(e))


def test_crud_chantier(db, results):
    """Test CRUD complet des chantiers"""
    print("\n[TEST] CRUD Chantiers")

    chantier_id = None
    try:
        # CREATE
        data = {
            'nom': 'Chantier Test Complet',
            'lieu': 'Paris 75001',
            'type_projet': 'Construction',
            'lot': 'Lot 5 - Menuiseries',
            'maitre_ouvrage': 'Mairie de Paris',
            'maitre_oeuvre': 'Cabinet Architecture',
            'date_remise': '2024-06-15',
            'notes': 'Chantier de test automatique'
        }
        chantier_id = db.add_chantier(data)
        if chantier_id and isinstance(chantier_id, int):
            results.success(f"add_chantier cree ID={chantier_id}")
        else:
            results.fail("add_chantier", f"ID invalide: {chantier_id}")
            return None

        # READ
        chantier = db.get_chantier(chantier_id)
        if chantier and chantier['nom'] == data['nom']:
            results.success("get_chantier retourne les bonnes donnees")
        else:
            results.fail("get_chantier", f"Donnees incorrectes: {chantier}")

        # READ ALL
        chantiers = db.get_chantiers()
        if any(c['id'] == chantier_id for c in chantiers):
            results.success("get_chantiers inclut le nouveau chantier")
        else:
            results.fail("get_chantiers", "Chantier non trouve dans la liste")

        # UPDATE
        update_data = {
            'nom': 'Chantier Test Modifie',
            'lieu': 'Lyon 69001',
            'resultat': 'EN_COURS'
        }
        db.update_chantier(chantier_id, update_data)
        chantier = db.get_chantier(chantier_id)
        if chantier['nom'] == update_data['nom'] and chantier['lieu'] == update_data['lieu']:
            results.success("update_chantier modifie correctement")
        else:
            results.fail("update_chantier", f"Modification non appliquee: {chantier}")

        # FILTRE PAR RESULTAT
        chantiers_filtre = db.get_chantiers('EN_COURS')
        if any(c['id'] == chantier_id for c in chantiers_filtre):
            results.success("get_chantiers filtre par resultat fonctionne")
        else:
            results.fail("get_chantiers filtre", "Filtre resultat ne fonctionne pas")

        return chantier_id

    except Exception as e:
        results.fail("CRUD Chantier", str(e))
        return chantier_id


def test_crud_article_dpgf(db, results, chantier_id):
    """Test CRUD des articles DPGF"""
    print("\n[TEST] CRUD Articles DPGF")

    if not chantier_id:
        results.fail("CRUD Articles", "Pas de chantier_id pour les tests")
        return None

    article_id = None
    try:
        # CREATE
        data = {
            'code': 'ART-001',
            'designation': 'Porte coupe-feu 1H',
            'unite': 'U',
            'quantite': 5,
            'temps_conception': 2.0,
            'temps_fabrication': 4.5,
            'temps_pose': 3.0,
            'marge_pct': 25.0
        }
        article_id = db.add_article_dpgf(chantier_id, data)
        if article_id and isinstance(article_id, int):
            results.success(f"add_article_dpgf cree ID={article_id}")
        else:
            results.fail("add_article_dpgf", f"ID invalide: {article_id}")
            return None

        # READ
        article = db.get_article_dpgf(article_id)
        if article and article['code'] == data['code']:
            results.success("get_article_dpgf retourne les bonnes donnees")
        else:
            results.fail("get_article_dpgf", f"Donnees incorrectes: {article}")

        # READ ALL
        articles = db.get_articles_dpgf(chantier_id)
        if any(a['id'] == article_id for a in articles):
            results.success("get_articles_dpgf inclut le nouvel article")
        else:
            results.fail("get_articles_dpgf", "Article non trouve dans la liste")

        # UPDATE - mise a jour avec code et designation obligatoires
        update_data = {
            'code': 'ART-001',
            'designation': 'Porte coupe-feu 2H modifiee',
            'quantite': 10,
            'temps_conception': 2.0,
            'temps_fabrication': 4.5,
            'temps_pose': 4.0
        }
        db.update_article_dpgf(article_id, update_data)
        article = db.get_article_dpgf(article_id)
        if article['designation'] == update_data['designation']:
            results.success("update_article_dpgf modifie correctement")
        else:
            results.fail("update_article_dpgf", f"Modification non appliquee: {article}")

        # TEST CALCUL COUTS (sans produits) - apres update
        # La nouvelle structure utilise les prix de vente pour cout_mo_total
        taux = db.get_taux_horaires()
        expected_mo_vente = (2.0 * taux['conception']['vente'] +
                            4.5 * taux['fabrication']['vente'] +
                            4.0 * taux['pose']['vente'])
        article = db.get_article_dpgf(article_id)
        if abs(article.get('cout_mo_total', 0) - expected_mo_vente) < 0.01:
            results.success(f"Calcul cout MO (vente) correct: {expected_mo_vente:.2f} EUR")
        else:
            results.fail("Calcul cout MO", f"Attendu {expected_mo_vente:.2f}, obtenu {article.get('cout_mo_total', 0)}")

        return article_id

    except Exception as e:
        results.fail("CRUD Article DPGF", str(e))
        return article_id


def test_produits_lies(db, results, article_id):
    """Test des produits lies aux articles"""
    print("\n[TEST] Produits lies aux articles DPGF")

    if not article_id:
        results.fail("Produits lies", "Pas d'article_id pour les tests")
        return

    try:
        # D'abord, on a besoin d'un produit dans le catalogue
        # Verifier s'il y a des produits
        products = db.search_produits()

        if not products:
            # Ajouter un produit de test
            produit_data = {
                'designation': 'Porte test pour marches',
                'categorie': 'TEST',
                'sous_categorie': 'Test',
                'prix_achat': 150.0,
                'hauteur': 2040,
                'largeur': 830
            }
            produit_id = db.add_produit(produit_data)
            results.success(f"Produit de test cree ID={produit_id}")
        else:
            produit_id = products[0]['id']
            results.success(f"Utilisation produit existant ID={produit_id}")

        # ADD PRODUIT ARTICLE
        liaison_id = db.add_produit_article(article_id, produit_id, 3)
        if liaison_id and isinstance(liaison_id, int):
            results.success(f"add_produit_article cree liaison ID={liaison_id}")
        else:
            results.fail("add_produit_article", f"ID invalide: {liaison_id}")
            return

        # GET PRODUITS ARTICLE
        produits = db.get_produits_article(article_id)
        if produits and len(produits) > 0:
            results.success(f"get_produits_article retourne {len(produits)} produit(s)")

            # Verifier que le prix est correct
            produit_lie = produits[0]
            if produit_lie['quantite'] == 3:
                results.success("Quantite produit lie correcte")
            else:
                results.fail("Quantite produit", f"Attendu 3, obtenu {produit_lie['quantite']}")
        else:
            results.fail("get_produits_article", "Aucun produit retourne")

        # UPDATE PRODUIT ARTICLE
        db.update_produit_article(liaison_id, 5, 200.0)
        produits = db.get_produits_article(article_id)
        if produits and produits[0]['quantite'] == 5:
            results.success("update_produit_article modifie correctement")
        else:
            results.fail("update_produit_article", "Modification non appliquee")

        # RECALCULER ARTICLE
        db.recalculer_article_dpgf(article_id)
        article = db.get_article_dpgf(article_id)
        cout_materiaux = article.get('cout_materiaux', 0)
        if cout_materiaux > 0:
            results.success(f"recalculer_article_dpgf: cout_materiaux = {cout_materiaux:.2f} EUR")
        else:
            results.fail("recalculer_article_dpgf", f"Cout materiaux nul: {article}")

        # VERIFIER PRIX DE VENTE
        prix_vente = article.get('prix_unitaire_ht', 0)
        if prix_vente > 0:
            results.success(f"Prix de vente calcule: {prix_vente:.2f} EUR")
        else:
            results.fail("Prix de vente", f"Prix nul: {article}")

        # REMOVE PRODUIT ARTICLE
        db.remove_produit_article(liaison_id)
        produits = db.get_produits_article(article_id)
        if len(produits) == 0:
            results.success("remove_produit_article supprime le lien")
        else:
            results.fail("remove_produit_article", f"Produit non supprime: {produits}")

        # Cleanup produit de test si cree
        if not products:
            db.delete_produit(produit_id, permanent=True)

    except Exception as e:
        results.fail("Produits lies", str(e))


def test_calcul_prix_multi_produits(db, results, chantier_id):
    """Test du calcul de prix avec plusieurs produits"""
    print("\n[TEST] Calcul prix multi-produits")

    if not chantier_id:
        results.fail("Multi-produits", "Pas de chantier_id")
        return

    try:
        # Creer un article
        data = {
            'code': 'MULTI-001',
            'designation': 'Ensemble porte avec accessoires',
            'unite': 'ENS',
            'quantite': 2,
            'temps_conception': 1.5,
            'temps_fabrication': 3.0,
            'temps_pose': 2.0,
            'marge_pct': 30.0
        }
        article_id = db.add_article_dpgf(chantier_id, data)
        results.success(f"Article multi-produits cree ID={article_id}")

        # Ajouter plusieurs produits de test
        produit1_data = {
            'designation': 'Porte principale',
            'categorie': 'TEST',
            'prix_achat': 250.0
        }
        produit1_id = db.add_produit(produit1_data)

        produit2_data = {
            'designation': 'Serrure haute securite',
            'categorie': 'TEST',
            'prix_achat': 80.0
        }
        produit2_id = db.add_produit(produit2_data)

        produit3_data = {
            'designation': 'Ferme-porte automatique',
            'categorie': 'TEST',
            'prix_achat': 45.0
        }
        produit3_id = db.add_produit(produit3_data)

        results.success("3 produits de test crees")

        # Lier les produits a l'article
        db.add_produit_article(article_id, produit1_id, 1)  # 250 EUR
        db.add_produit_article(article_id, produit2_id, 1)  # 80 EUR
        db.add_produit_article(article_id, produit3_id, 2)  # 90 EUR
        results.success("3 produits lies a l'article")

        # Recalculer
        db.recalculer_article_dpgf(article_id)
        article = db.get_article_dpgf(article_id)

        # Verifier cout materiaux = 250 + 80 + 45*2 = 420 EUR
        cout_materiaux = article.get('cout_materiaux', 0)
        expected_materiaux = 250 + 80 + 45*2  # 420
        if abs(cout_materiaux - expected_materiaux) < 0.01:
            results.success(f"Cout materiaux correct: {cout_materiaux:.2f} EUR (attendu {expected_materiaux})")
        else:
            results.fail("Cout materiaux multi", f"Attendu {expected_materiaux}, obtenu {cout_materiaux}")

        # Verifier cout MO (utilise les prix de vente maintenant)
        taux = db.get_taux_horaires()
        expected_mo_vente = (1.5 * taux['conception']['vente'] +
                            3.0 * taux['fabrication']['vente'] +
                            2.0 * taux['pose']['vente'])
        cout_mo = article.get('cout_mo_total', 0)
        if abs(cout_mo - expected_mo_vente) < 0.01:
            results.success(f"Cout MO (vente) correct: {cout_mo:.2f} EUR")
        else:
            results.fail("Cout MO multi", f"Attendu {expected_mo_vente}, obtenu {cout_mo}")

        # Verifier prix de vente = materiaux*(1+marge) + MO_vente
        # La marge s'applique seulement sur les materiaux
        marge = 30 / 100
        prix_materiaux_vente = cout_materiaux * (1 + marge)
        expected_prix = prix_materiaux_vente + expected_mo_vente
        prix_vente = article.get('prix_unitaire_ht', 0)
        if abs(prix_vente - expected_prix) < 0.01:
            results.success(f"Prix vente unitaire correct: {prix_vente:.2f} EUR")
        else:
            results.fail("Prix vente multi", f"Attendu {expected_prix:.2f}, obtenu {prix_vente}")

        # Verifier prix total = prix_unitaire * quantite
        prix_total = article.get('prix_total_ht', 0)
        expected_total = prix_vente * 2  # quantite = 2
        if abs(prix_total - expected_total) < 0.01:
            results.success(f"Prix vente total correct: {prix_total:.2f} EUR")
        else:
            results.fail("Prix total multi", f"Attendu {expected_total:.2f}, obtenu {prix_total}")

        # Cleanup
        db.delete_article_dpgf(article_id)
        db.delete_produit(produit1_id, permanent=True)
        db.delete_produit(produit2_id, permanent=True)
        db.delete_produit(produit3_id, permanent=True)
        results.success("Nettoyage produits de test")

    except Exception as e:
        results.fail("Calcul multi-produits", str(e))


def test_import_export_dpgf(db, results, chantier_id):
    """Test import/export DPGF CSV"""
    print("\n[TEST] Import/Export DPGF CSV")

    if not chantier_id:
        results.fail("Import/Export", "Pas de chantier_id")
        return

    try:
        # Creer un fichier DPGF temporaire
        temp_dir = tempfile.mkdtemp()
        dpgf_file = os.path.join(temp_dir, 'test_dpgf.csv')

        # Ecrire un fichier DPGF de test (niveau 4 = articles chiffrables)
        with open(dpgf_file, 'w', encoding='utf-8-sig') as f:
            f.write("CODE;NIVEAU;DESIGNATION;UNITE;QUANTITE\n")
            f.write("1;1;LOT 1 - MENUISERIES;;\n")
            f.write("1.1;2;Portes interieures;;\n")
            f.write("1.1.1;3;Portes simples;;\n")
            f.write("1.1.1.1;4;Porte simple 83x204;U;10\n")
            f.write("1.1.1.2;4;Porte double 146x204;U;5\n")
            f.write("1.2;2;Fenetres;;\n")
            f.write("1.2.1;3;Fenetres standard;;\n")
            f.write("1.2.1.1;4;Fenetre 100x120;U;8\n")

        results.success("Fichier DPGF de test cree")

        # Creer un nouveau chantier pour l'import
        import_chantier_id = db.add_chantier({'nom': 'Chantier Import Test'})

        # Importer
        count = db.import_dpgf_csv(import_chantier_id, dpgf_file)
        if count == 3:  # 3 articles de niveau 3
            results.success(f"import_dpgf_csv: {count} articles importes")
        else:
            results.fail("import_dpgf_csv", f"Attendu 3 articles, obtenu {count}")

        # Verifier les articles importes
        articles = db.get_articles_dpgf(import_chantier_id)
        if len(articles) == 3:
            results.success("Nombre d'articles correct apres import")
        else:
            results.fail("Verification import", f"Attendu 3 articles, obtenu {len(articles)}")

        # Verifier la structure (niveaux 1, 2, 3)
        structure = db.get_structure_dpgf(import_chantier_id)
        if len(structure) >= 5:  # 1 niveau 1 + 2 niveaux 2 + 2 niveaux 3
            results.success(f"Structure DPGF importee: {len(structure)} elements")
        else:
            results.fail("Structure DPGF", f"Structure incomplete: {len(structure)} elements")

        # Test export version client
        export_file_client = os.path.join(temp_dir, 'export_client.csv')
        count_export = db.export_dpgf_csv(import_chantier_id, export_file_client, version_client=True)
        if os.path.exists(export_file_client):
            results.success(f"export_dpgf_csv (client): {count_export} lignes")
        else:
            results.fail("export_dpgf_csv client", "Fichier non cree")

        # Test export version interne
        export_file_interne = os.path.join(temp_dir, 'export_interne.csv')
        count_export = db.export_dpgf_csv(import_chantier_id, export_file_interne, version_client=False)
        if os.path.exists(export_file_interne):
            results.success(f"export_dpgf_csv (interne): {count_export} lignes")
        else:
            results.fail("export_dpgf_csv interne", "Fichier non cree")

        # Test template
        template_file = os.path.join(temp_dir, 'template.csv')
        db.create_dpgf_template(template_file)
        if os.path.exists(template_file):
            results.success("create_dpgf_template fonctionne")
        else:
            results.fail("create_dpgf_template", "Template non cree")

        # Cleanup
        db.delete_chantier(import_chantier_id)
        shutil.rmtree(temp_dir)
        results.success("Nettoyage fichiers temporaires")

    except Exception as e:
        results.fail("Import/Export DPGF", str(e))


def test_statistiques_marches(db, results):
    """Test des statistiques des marches"""
    print("\n[TEST] Statistiques des marches")

    try:
        # Creer plusieurs chantiers avec differents resultats
        chantier1 = db.add_chantier({'nom': 'Stat Test 1', 'resultat': 'GAGNE', 'montant_ht': 50000})
        chantier2 = db.add_chantier({'nom': 'Stat Test 2', 'resultat': 'GAGNE', 'montant_ht': 30000})
        chantier3 = db.add_chantier({'nom': 'Stat Test 3', 'resultat': 'PERDU', 'montant_ht': 20000})
        chantier4 = db.add_chantier({'nom': 'Stat Test 4', 'resultat': 'EN_COURS', 'montant_ht': 15000})

        results.success("4 chantiers de test crees")

        # Obtenir les stats
        stats = db.get_stats_marches()

        if stats['total_chantiers'] >= 4:
            results.success(f"Total chantiers: {stats['total_chantiers']}")
        else:
            results.fail("Total chantiers", f"Attendu >= 4, obtenu {stats['total_chantiers']}")

        if stats['par_resultat'].get('GAGNE', 0) >= 2:
            results.success(f"Chantiers gagnes: {stats['par_resultat'].get('GAGNE', 0)}")
        else:
            results.fail("Chantiers gagnes", f"Attendu >= 2")

        if stats['montant_gagne'] >= 80000:
            results.success(f"Montant gagne: {stats['montant_gagne']:.0f} EUR")
        else:
            results.fail("Montant gagne", f"Attendu >= 80000, obtenu {stats['montant_gagne']}")

        # Taux de reussite = gagnes / (gagnes + perdus) * 100
        # Ici: 2 / (2 + 1) * 100 = 66.67%
        if stats['taux_reussite'] > 0:
            results.success(f"Taux reussite: {stats['taux_reussite']:.1f}%")
        else:
            results.fail("Taux reussite", "Taux nul ou negatif")

        # Cleanup
        db.delete_chantier(chantier1)
        db.delete_chantier(chantier2)
        db.delete_chantier(chantier3)
        db.delete_chantier(chantier4)
        results.success("Nettoyage chantiers de test")

    except Exception as e:
        results.fail("Statistiques", str(e))


def test_update_montant_chantier(db, results):
    """Test de la mise a jour automatique du montant chantier"""
    print("\n[TEST] Mise a jour automatique montant chantier")

    try:
        # Creer un chantier
        chantier_id = db.add_chantier({'nom': 'Test Montant Auto'})

        # Ajouter des articles avec prix
        art1 = db.add_article_dpgf(chantier_id, {
            'code': 'M1',
            'designation': 'Article 1',
            'unite': 'U',
            'quantite': 2,
            'temps_fabrication': 1.0,
            'marge_pct': 20
        })

        art2 = db.add_article_dpgf(chantier_id, {
            'code': 'M2',
            'designation': 'Article 2',
            'unite': 'U',
            'quantite': 3,
            'temps_fabrication': 2.0,
            'marge_pct': 20
        })

        # Ajouter des produits
        produit = db.add_produit({'designation': 'Produit montant', 'categorie': 'TEST', 'prix_achat': 100})
        db.add_produit_article(art1, produit, 1)
        db.add_produit_article(art2, produit, 2)

        # Les recalculs sont automatiques apres add_produit_article
        # Mettre a jour le montant du chantier
        db.update_chantier_montant(chantier_id)

        # Verifier
        chantier = db.get_chantier(chantier_id)
        if chantier['montant_ht'] > 0:
            results.success(f"Montant chantier mis a jour: {chantier['montant_ht']:.2f} EUR")
        else:
            results.fail("Montant chantier", "Montant nul")

        # Cleanup
        db.delete_chantier(chantier_id)
        db.delete_produit(produit, permanent=True)

    except Exception as e:
        results.fail("Montant chantier auto", str(e))


def test_suppression_cascade(db, results):
    """Test de la suppression en cascade"""
    print("\n[TEST] Suppression en cascade")

    try:
        # Creer chantier avec articles et produits lies
        chantier_id = db.add_chantier({'nom': 'Test Cascade'})
        article_id = db.add_article_dpgf(chantier_id, {'code': 'C1', 'designation': 'Art cascade'})
        produit_id = db.add_produit({'designation': 'Prod cascade', 'categorie': 'TEST', 'prix_achat': 50})
        liaison_id = db.add_produit_article(article_id, produit_id, 1)

        results.success("Chantier avec article et produit lie cree")

        # Supprimer le chantier
        db.delete_chantier(chantier_id)

        # Verifier que l'article n'existe plus
        article = db.get_article_dpgf(article_id)
        if article is None:
            results.success("Article supprime en cascade")
        else:
            results.fail("Cascade article", "Article non supprime")

        # Verifier que la liaison n'existe plus
        produits = db.get_produits_article(article_id)
        if len(produits) == 0:
            results.success("Liaison produit supprimee en cascade")
        else:
            results.fail("Cascade liaison", "Liaison non supprimee")

        # Verifier que le produit existe toujours (pas de cascade sur produits catalogue)
        prod = db.get_produit(produit_id)
        if prod:
            results.success("Produit catalogue preserve (pas de cascade)")
        else:
            results.fail("Produit catalogue", "Produit supprime par erreur")

        # Cleanup
        db.delete_produit(produit_id, permanent=True)

    except Exception as e:
        results.fail("Suppression cascade", str(e))


def test_interfaces_ui(results):
    """Test des imports et initialisations UI"""
    print("\n[TEST] Imports et initialisations UI")

    try:
        # Test imports
        from ui.dpgf_import_dialog import DPGFImportDialog, ChantierEditDialog
        results.success("Import dpgf_import_dialog OK")

        from ui.dpgf_chiffrage_view import DPGFChiffrageView, ArticleDialog
        results.success("Import dpgf_chiffrage_view OK")

        from ui.product_search_dialog import ProductSearchDialog, MultiProductSearchDialog
        results.success("Import product_search_dialog OK")

        from ui.dpgf_export_dialog import DPGFExportDialog
        results.success("Import dpgf_export_dialog OK")

        from ui.resultat_marche_dialog import ResultatMarcheDialog, get_resultat_color, get_resultat_label, RESULTATS
        results.success("Import resultat_marche_dialog OK")

        from ui.marches_analyse_view import MarchesAnalyseView
        results.success("Import marches_analyse_view OK")

        # Test constantes
        if len(RESULTATS) >= 5:
            results.success(f"RESULTATS contient {len(RESULTATS)} etats")
        else:
            results.fail("RESULTATS", f"Incomplet: {len(RESULTATS)} etats")

        # Test fonctions utilitaires
        color = get_resultat_color('GAGNE')
        if color and len(color) == 2:
            results.success("get_resultat_color fonctionne")
        else:
            results.fail("get_resultat_color", f"Retour invalide: {color}")

        label = get_resultat_label('PERDU')
        if label and isinstance(label, str):
            results.success(f"get_resultat_label: 'PERDU' -> '{label}'")
        else:
            results.fail("get_resultat_label", f"Retour invalide: {label}")

    except Exception as e:
        results.fail("Imports UI", str(e))


def test_version(results):
    """Test de la version"""
    print("\n[TEST] Version application")

    try:
        from version import __version__, __app_name__

        if __version__ == "1.2.1":
            results.success(f"Version: {__version__}")
        else:
            results.fail("Version", f"Attendu 1.2.1, obtenu {__version__}")

        if __app_name__ == "DestriChiffrage":
            results.success(f"App name: {__app_name__}")
        else:
            results.fail("App name", f"Nom incorrect: {__app_name__}")

    except Exception as e:
        results.fail("Version", str(e))


def run_all_tests():
    """Execute tous les tests"""
    print("="*60)
    print("TESTS COMPLETS - MODULE MARCHES PUBLICS")
    print("DestriChiffrage v1.1.0")
    print("="*60)

    results = TestResults()

    # Utiliser une base de donnees temporaire pour les tests
    temp_dir = tempfile.mkdtemp()
    temp_db_path = os.path.join(temp_dir, 'catalogue.db')

    try:
        # Creer la DB avec le data_dir temporaire
        db = Database(data_dir=temp_dir)
        print(f"\nBase de test: {temp_db_path}")

        # Tests de configuration
        test_configuration_taux(db, results)

        # Tests CRUD
        chantier_id = test_crud_chantier(db, results)
        article_id = test_crud_article_dpgf(db, results, chantier_id)
        test_produits_lies(db, results, article_id)

        # Tests calculs
        test_calcul_prix_multi_produits(db, results, chantier_id)

        # Tests import/export
        test_import_export_dpgf(db, results, chantier_id)

        # Tests statistiques
        test_statistiques_marches(db, results)

        # Tests montant auto
        test_update_montant_chantier(db, results)

        # Tests cascade
        test_suppression_cascade(db, results)

        # Cleanup chantier principal
        if chantier_id:
            db.delete_chantier(chantier_id)

        # Tests UI (sans Tk)
        test_interfaces_ui(results)

        # Test version
        test_version(results)

    except Exception as e:
        results.fail("Execution tests", str(e))
    finally:
        # Nettoyer
        try:
            shutil.rmtree(temp_dir)
        except:
            pass

    # Afficher le resume
    success = results.summary()

    return success


if __name__ == '__main__':
    success = run_all_tests()
    sys.exit(0 if success else 1)
