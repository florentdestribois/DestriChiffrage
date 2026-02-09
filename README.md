# DestriChiffrage

**Version 1.7.9**

Application de chiffrage et approvisionnement professionnel avec module Marches Publics.

## Fonctionnalites

### Filtres documents produits (v1.7.9)
- **Fix issue #27** : Filtres de recherche par presence de fiche technique et/ou devis fournisseur
  - Checkbox "Avec fiche technique" pour filtrer les produits documentes
  - Checkbox "Avec devis fournisseur" pour filtrer les produits avec tarification validee
  - Disponible dans la fenetre principale et les dialogues de recherche produit
  - Combinable avec tous les autres filtres existants (categorie, dimensions, fournisseur)

### Affichage hierarchique DPGF (v1.7.8)
- **Fix issue #24** : Les niveaux 1 a 3 (Lot, Chapitre, Sous-chapitre) sont maintenant affiches dans la vue de chiffrage DPGF
  - Structure hierarchique complete visible avec indentation visuelle
  - Distinction visuelle : fond colore et police en gras pour les titres
  - Les elements de structure ne sont pas selectionnables (reserve aux articles)
  - Export CSV respecte l'ordre hierarchique (structure et articles intercales)
  - Meilleure lisibilite et navigation dans les articles

### Verification automatique des mises a jour (v1.7.7)
- **Fix issue #26** : Verification automatique des mises a jour au demarrage
  - Verification en arriere-plan apres 3 secondes (non bloquante)
  - Notification uniquement si une mise a jour est disponible
  - Gestion silencieuse des erreurs reseau (pas de popup d'erreur)
  - L'utilisateur n'est pas derange si tout est a jour

### Chiffrage DPGF ameliore (v1.7.6)
- **Fix issue #25** : Amelioration de l'ergonomie du chiffrage DPGF
  - **Prix manuel** : Possibilite de saisir un prix HT manuellement qui remplace le calcul automatique
    - Checkbox "Prix manuel (override)" pour activer/desactiver
    - Le prix calcule automatiquement est initialise comme valeur par defaut
    - Indication visuelle "(manuel)" dans le resume des couts
  - **Fournitures additionnelles** : Nouveau champ pour ajouter des couts de fournitures hors catalogue
    - S'additionne au cout des produits lies
    - Spinbox avec increment de 10 EUR pour un ajustement rapide
  - **Spinbox pour les temps MO** : Les champs Conception, Fabrication et Pose utilisent maintenant des Spinbox
    - Increment de 1h pour un ajustement rapide
    - Boutons +/- integres pour faciliter l'ajustement
  - **Export ameliore** : Nouvelles colonnes FOURNITURES_ADD et PRIX_MANUEL dans l'export CSV interne

### Export PDF avec nommage personnalise (v1.7.5)
- **Fix issue #22** : Options de nommage des fichiers PDF lors de l'export DPGF
  - Prefixer les fichiers avec le code article DPGF (ex: `ART-001_42_Designation_fiche.pdf`)
  - Choix des elements a inclure dans le nom: code article, ID produit, designation
  - Apercu en temps reel du format de nommage dans le dialogue d'export
  - Facilite le classement et l'identification des documents par lot/article

### Correction bug affichage recapitulatif (v1.7.4)
- **Fix issue #23** : Le recapitulatif projet ne s'affiche plus involontairement lors de l'edition d'un article
  - Verification que le clic provient bien du widget treeview avant de deselectionner
  - Le recapitulatif s'affiche uniquement lors d'un clic intentionnel sur la zone vide du treeview
  - L'edition des champs (description, heures MO, TVA) ne provoque plus la perte du contexte

### Recapitulatif projet et marge personnalisee (v1.7.0)
- **Recapitulatif projet** : Affichage automatique quand aucun article n'est selectionne dans la vue chiffrage DPGF
  - Total des heures par type (conception, fabrication, pose)
  - Couts detailles (materiaux, main d'oeuvre, revient)
  - Prix total HT et marge globale calculee
- **Marge projet personnalisee** : Ajustement de la marge produits par projet
  - Appliquee a tous les articles du chantier en un clic
  - Sauvegardee uniquement pour le projet (non globale)
  - Recalcul automatique de tous les prix
- **Harmonisation des boutons** : Style minimaliste coherent dans toute l'application
  - Bouton principal : Or Destribois (secondary)
  - Boutons secondaires : Ghost (transparent)
  - Boutons supprimer : Danger-ghost (texte rouge discret)

### Refactorisation UI et composants reutilisables (v1.6.0)
- **Factory methods dans theme.py** : Composants reutilisables pour une UI coherente
  - `Theme.create_header()` : Headers de fenetres avec titre, icone et sous-titre
  - `Theme.create_card()` : Cards avec bordures et padding configurables
  - `Theme.create_button()` : Boutons stylises (primary, secondary, success, danger, ghost)
  - `Theme.create_label()` : Labels stylises (title, heading, body, muted, etc.)
  - `Theme.create_entry()` : Champs de saisie avec support placeholder
  - `Theme.create_treeview()` : Treeview avec scrollbar integree
  - `Theme.create_separator()` : Separateurs horizontaux/verticaux
  - `Theme.create_status_badge()` : Badges colores (success, warning, danger, info)
  - `Theme.create_tooltip()` : Tooltips attachables a tout widget
- **Code UI simplifie** : Reduction significative du code repetitif dans les dialogues
- **Maintenabilite amelioree** : Modifications de style globales facilitees

### Navigation rapide (v1.5.0)
- **Menu Vente dans le header** : Menu deroulant avec acces direct a l'analyse des ventes et la creation de chantiers
- **Ergonomie amelioree** : Reduction du nombre de clics pour acceder aux fonctionnalites principales

### Catalogue de produits
- **Recherche instantanee** : Recherche par mot-cle dans les designations, dimensions, references
- **Filtrage avance en cascade** : Par categorie et 3 niveaux de sous-categories, hauteur et largeur
  - Les filtres de sous-categories sont mis a jour automatiquement selon les selections precedentes
  - La selection est preservee lors du rafraichissement si elle existe toujours
- **Calcul automatique des prix de vente** : Marge personnalisable (defaut 20%)
- **Gestion des produits** : Ajout, modification, suppression avec formulaires intuitifs
- **Devis rapide** : Selection multiple d'articles pour export groupe avec PDFs
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
- **Presentation article (v1.4.0)** : Champ optionnel exporte sur ligne 2 dans Odoo
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
│   ├── cart_manager.py        # Gestionnaire de devis rapide
│   ├── config.py              # Configuration
│   └── ui/
│       ├── __init__.py
│       ├── theme.py           # Styles et couleurs
│       ├── main_window.py     # Fenetre principale
│       ├── dialogs.py         # Boites de dialogue
│       ├── cart_panel.py      # Interface devis rapide
│       ├── cart_export_dialog.py  # Dialogue d'export devis rapide
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
3. **Filtrer par sous-categories (v1.4.0)** : 3 niveaux de sous-categories en cascade
4. **Creer un produit (v1.4.0)** : Bouton pour creer un nouveau produit directement depuis la recherche
5. Les resultats s'affichent instantanement

### Modifier la marge
1. Modifier la valeur dans le champ "Marge" en haut a droite
2. Cliquer sur "Appliquer"
3. Tous les prix de vente sont recalcules

### Utiliser le devis rapide
1. Cliquer sur l'icone "+" dans la colonne Devis pour ajouter un article
2. L'icone devient un checkmark et le compteur du bouton Devis rapide s'incremente
3. Cliquer sur le bouton "Devis rapide (X)" pour voir les articles selectionnes
4. Dans le panneau devis rapide :
   - Double-clic sur un article pour le retirer
   - "Vider le devis" pour tout supprimer
   - "Exporter" pour lancer l'export groupe

### Exporter le devis rapide
1. Depuis le panneau devis rapide, cliquer sur "Exporter"
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

### Vider la base de donnees (v1.4.1)
1. Menu "Edition" > "Vider la base de donnees..."
2. Options disponibles :
   - **Supprimer les categories** : Optionnel, supprime aussi les categories
   - **Supprimer les chantiers** : Coche par defaut, supprime tous les chantiers et marches
3. Les IDs sont reinitialises (AUTOINCREMENT remis a zero)
4. **Les parametres sont conserves** : marge, taux horaires, etc.

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

**Note (v1.4.0)** :
- La description est maintenant sur la meme ligne que l'article (plus d'espace)
- Si un champ "Presentation" est renseigne dans l'article, il est exporte sur une seconde ligne

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
- **[Implementation Devis rapide](docs/IMPLEMENTATION_PANIER.md)** - Architecture du systeme de devis rapide
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
