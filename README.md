# DestriChiffrage

**Version 1.3.4**

Application de gestion de catalogue et de chiffrage de portes avec module Marches Publics.

## Fonctionnalites

### Catalogue de produits
- **Recherche instantanee** : Recherche par mot-cle dans les designations, dimensions, references
- **Filtrage avance en cascade** : Par categorie et 3 niveaux de sous-categories, hauteur et largeur
  - Les filtres de sous-categories sont mis a jour automatiquement selon les selections precedentes
  - La selection est preservee lors du rafraichissement si elle existe toujours
- **Calcul automatique des prix de vente** : Marge personnalisable (defaut 20%)
- **Gestion des produits** : Ajout, modification, suppression avec formulaires intuitifs
- **Panier d'export** : Selection multiple d'articles pour export groupe avec PDFs
- **Import/Export CSV** : Compatible avec Excel, encodage UTF-8 avec BOM
- **Gestion des documents** : Association de fiches techniques et devis fournisseur (PDF)
- **Copier-coller** : Copie rapide des designations, prix et references
- **Base de donnees locale** : SQLite (pas de serveur requis)

### Module Marches Publics
- **Gestion des chantiers** : Creation et suivi des appels d'offres
- **Types de marche (v1.3.0)** : Marche public, Particulier avec DPGF, Export Odoo
- **Filtrage par type (v1.3.0)** : Filtre par type de marche dans l'analyse
- **Nom du client (v1.3.0)** : Champ client pour l'export Odoo
- **Import DPGF** : Import de fichiers DPGF au format CSV avec colonnes DESCRIPTION et TVA
- **Import DPGF dans vue chiffrage (v1.3.3)** : Bouton pour importer un fichier DPGF dans le chantier courant
- **Import article depuis catalogue (v1.3.3)** : Creation rapide d'un article DPGF a partir d'un produit du catalogue avec liaison automatique
- **Chiffrage multi-produits** : Associer plusieurs produits du catalogue a chaque article DPGF
- **Description article (v1.3.0)** : Description detaillee pour chaque article DPGF
- **TVA par article (v1.3.0)** : Taux de TVA configurable (0%, 5.5%, 10%, 20%)
- **Calcul des couts detailles (v1.2.0)** :
  - Cout entreprise et Prix de vente separes pour la main d'oeuvre
  - Marge MO calculee automatiquement (non modifiable)
  - Marge materiaux configurable separement
  - Formule: Prix = (Materiaux x (1+marge)) + MO_vente
- **Menu contextuel produits (v1.2.0)** : Clic droit pour copier infos, ouvrir fiche technique ou devis
- **Export DPGF (v1.3.0)** :
  - Version client (simplifiee)
  - Version interne (complete)
  - Version Odoo (format ERP compatible)
  - Option d'export des fiches techniques et devis fournisseur
- **Suivi des resultats** : Gagne/Perdu/En cours avec infos concurrent
- **Analyse des marches** : Statistiques et taux de reussite avec filtre par type

## Structure du projet

```
DestriChiffrage/
├── src/
│   ├── main.py                # Point d'entree
│   ├── database.py            # Gestion base de donnees & exports
│   ├── cart_manager.py        # Gestionnaire de panier
│   ├── config.py              # Configuration
│   └── ui/
│       ├── __init__.py
│       ├── theme.py           # Styles et couleurs
│       ├── main_window.py     # Fenetre principale
│       ├── dialogs.py         # Boites de dialogue
│       ├── cart_panel.py      # Interface panier
│       ├── cart_export_dialog.py  # Dialogue d'export panier
│       ├── dpgf_import_dialog.py     # Import DPGF (v1.3.0)
│       ├── dpgf_chiffrage_view.py    # Vue chiffrage DPGF (v1.3.0)
│       ├── dpgf_export_dialog.py     # Export DPGF (v1.3.0)
│       ├── product_search_dialog.py  # Recherche produit (v1.1.0)
│       ├── resultat_marche_dialog.py # Resultat marche (v1.1.0)
│       └── marches_analyse_view.py   # Analyse marches (v1.3.0)
├── data/
│   ├── catalogue.db           # Base de donnees (creee automatiquement)
│   ├── Fiches_techniques/     # PDFs fiches techniques
│   ├── Devis_fournisseur/     # PDFs devis
│   └── Modele export Odoo.xlsx # Modele de reference Odoo
├── assets/
│   ├── icon.ico               # Icone application
│   ├── logo.png               # Logo (optionnel)
│   └── pdf.png                # Icone PDF
├── tests/
│   └── test_marches_complet.py  # Tests module Marches Publics
├── requirements.txt
├── README.md
└── run.bat                    # Lanceur Windows
```

## Installation

### Prerequis
- Python 3.8 ou superieur
- Tkinter (inclus avec Python sur Windows)

### Lancement

```bash
# Cloner ou telecharger le projet
cd DestriChiffrage

# Installer les dependances (optionnel)
pip install -r requirements.txt

# Lancer l'application
python src/main.py

# Ou double-cliquer sur run.bat
```

## Utilisation

### Importer des donnees existantes
1. Cliquer sur "Importer CSV"
2. Selectionner un fichier CSV avec les colonnes:
   - CATEGORIE, SOUS-CATEGORIE, SOUS-CATEGORIE 2, SOUS-CATEGORIE 3, DESIGNATION, HAUTEUR, LARGEUR, PRIX_UNITAIRE_HT, ARTICLE, FOURNISSEUR, CHANTIER, FICHE_TECHNIQUE, FICHIER_PDF

### Rechercher un produit
1. Taper dans le champ "Rechercher"
2. Ou selectionner une categorie dans la liste deroulante
3. Les resultats s'affichent instantanement

### Modifier la marge
1. Modifier la valeur dans le champ "Marge" en haut a droite
2. Cliquer sur "Appliquer"
3. Tous les prix de vente sont recalcules

### Utiliser le panier d'export
1. Cliquer sur l'icone "+" dans la colonne Panier pour ajouter un article
2. L'icone devient un checkmark et le compteur du bouton Panier s'incremente
3. Cliquer sur le bouton "Panier (X)" pour voir les articles selectionnes
4. Dans le panneau panier :
   - Double-clic sur un article pour le retirer
   - "Vider le panier" pour tout supprimer
   - "Exporter" pour lancer l'export groupe

### Exporter le panier
1. Depuis le panneau panier, cliquer sur "Exporter"
2. Choisir le fichier CSV de destination
3. Choisir le dossier pour les PDFs (optionnel)
4. Cocher les options :
   - Inclure les fiches techniques
   - Inclure les devis fournisseur
5. Les fichiers PDF seront copies dans des sous-dossiers :
   - `Fiches_techniques/`
   - `Devis_fournisseur/`

### Exporter tout / selection
- **Exporter tout** : Exporte tous les produits du catalogue
- **Exporter selection** : Exporte uniquement les produits affiches (apres filtre/recherche)

### Utiliser le module Marches Publics

#### Creer un nouveau chantier (v1.3.0)
1. Menu "Marches" > "Nouveau chantier / DPGF..." (ou Ctrl+Shift+N)
2. Renseigner les informations du chantier :
   - Nom du chantier (obligatoire)
   - **Nom du client** (obligatoire pour export Odoo)
   - **Type de marche** : Marche public / Particulier avec DPGF / Export Odoo
   - Lieu, type de projet, lot
3. Optionnel: Importer un fichier DPGF CSV
4. Cliquer sur "Creer le chantier"

#### Format CSV DPGF (v1.3.0)
Le fichier DPGF peut contenir les colonnes suivantes :
```
CODE;NIVEAU;DESIGNATION;DESCRIPTION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES;TVA
```

#### Chiffrer un article DPGF (v1.3.0)
1. Dans la vue de chiffrage, selectionner un article dans la liste
2. Dans le panneau de droite :
   - Renseigner la **Description** de l'article (pour export Odoo)
   - Cliquer sur "+ Ajouter" pour lier un ou plusieurs produits du catalogue
   - **Clic droit** sur un produit pour copier ses infos ou ouvrir ses documents
   - Saisir les temps de main d'oeuvre (conception, fabrication, pose)
   - Ajuster la marge materiaux si necessaire
   - Selectionner le **taux de TVA** (0%, 5.5%, 10%, 20%)
3. Les couts sont calcules automatiquement :
   - Materiaux = somme(prix_produit x quantite) x (1 + marge%)
   - MO = temps x prix_vente_horaire (marge MO integree dans les taux)
   - Prix vente = Materiaux + MO

#### Configurer les taux horaires (v1.2.0)
1. Menu "Parametres" > onglet "Chiffrage marches"
2. Pour chaque type (Conception, Fabrication, Pose) :
   - **Cout entreprise** : Le cout reel pour votre entreprise
   - **Prix de vente** : Le prix facture au client
   - **Marge** : Calculee automatiquement (lecture seule)
3. La marge materiaux s'applique sur le prix d'achat des produits

#### Exporter le DPGF (v1.3.0)
1. Cliquer sur "Exporter DPGF" dans la vue de chiffrage
2. Choisir la version :
   - **Client** : Uniquement code, designation, quantite, prix
   - **Interne** : Detail complet avec couts, temps MO, produits lies
   - **Odoo** : Format compatible ERP (Client, Articles, Description, Quantite, Prix, TVA)
3. Pour toutes les versions (Client, Interne, Odoo) :
   - Optionnel: Exporter les documents PDF des produits lies
   - Selectionner un dossier de destination
   - Cocher "Inclure les fiches techniques" et/ou "Inclure les devis fournisseur"
4. Enregistrer le fichier CSV

#### Format export Odoo
Le fichier CSV Odoo genere suit le format :
```
Customer*;Order Lines/Products*;order_line/name;Order Lines/Quantity;Order Lines/Unit Price;Order Lines/Taxes;Customer Reference
Nom du client;Article 1; ;12;70.00;20% Ser;REF123
;;Description de l'article 1;;;;
;Article 2; ;8;110.00;20% Ser;
;;Description de l'article 2;;;;
```

**Note (v1.3.4)** : La colonne `order_line/name` contient un espace sur les lignes produit pour permettre a Odoo de differencier les lignes produit des lignes description.

#### Analyser les marches (v1.3.0)
1. Menu "Marches" > "Analyse des marches"
2. Filtrer par :
   - **Resultat** : Tous, Gagne, Perdu, En cours...
   - **Type de marche** : Tous, Marche public, Particulier, Export Odoo
3. Visualiser les statistiques : total, gagnes, perdus, taux de reussite, CA

#### Suivre les resultats
1. Cliquer sur "Resultat marche" dans la vue de chiffrage
2. Selectionner le resultat (Gagne, Perdu, En cours...)
3. Optionnel: Renseigner le concurrent et son montant

## Tests

### Lancer les tests du module Marches Publics

```bash
# Tests complets (61 tests)
python tests/test_marches_complet.py

# Tests approfondis v1.3.0 (69 tests)
python tests/test_v130_approfondis.py
```

### Tests complets (test_marches_complet.py)
- Configuration des taux horaires et marge
- CRUD chantiers et articles DPGF
- Liaison multi-produits
- Calcul des couts (materiaux, MO, prix de vente)
- Import/Export DPGF CSV
- Statistiques des marches
- Suppression en cascade
- Imports modules UI

### Tests approfondis v1.3.0 (test_v130_approfondis.py)
- **Champs chantiers** : nom_client, type_marche (PUBLIC/PARTICULIER/ODOO)
- **Champs articles** : description, taux_tva (0%, 5.5%, 10%, 20%)
- **Export Odoo CSV** : format compatible ERP, alternance article/description
- **Import DPGF** : colonnes DESCRIPTION et TVA
- **Filtres** : par type de marche, combinaison avec resultat
- **Liaisons** : chantier-articles, article-produits, cascade
- **Workflow complet** : creation -> chiffrage -> export Odoo

## Creation d'un executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DestriChiffrage src/main.py
```

L'executable sera dans le dossier `dist/`.

## Documentation

Documentation complete disponible dans le dossier [`docs/`](docs/)

### Guides Disponibles

- **[Guide de Build](docs/BUILD.md)** - Compilation et creation de l'installateur
- **[Systeme de Mise a Jour](docs/AUTO_UPDATE.md)** - Auto-updater et publication de versions
- **[Implementation Panier](docs/IMPLEMENTATION_PANIER.md)** - Architecture du systeme de panier
- **[Implementation Installateur](docs/IMPLEMENTATION_EXE.md)** - Infrastructure de build .exe
- **[Rapport de Tests](docs/RAPPORT_TESTS_BUILD.md)** - Resultats des tests de build

Voir l'[index complet de la documentation](docs/README.md) pour plus de details.

## Conventions UI

### Tailles minimales des fenetres (v1.3.1)

Toutes les fenetres Toplevel disposent d'une taille minimale (`minsize`) pour garantir l'affichage complet des boutons et elements d'interface.

| Type de fenetre | Taille par defaut | Taille minimale |
|-----------------|-------------------|-----------------|
| Dialogues simples (quantite, confirmation) | 380x200 | 350x180 |
| Dialogues moyens (export, parametres) | 550x450 | 530x430 |
| Dialogues complexes (produit, fournisseur) | 680x860 | 660x840 |
| Vues principales (chiffrage, analyse) | 1200x700 | 1100x650 |

## Licence

Projet prive - Tous droits reserves
