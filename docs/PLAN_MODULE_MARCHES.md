# Plan d'implémentation - Module Marchés Publics DestriChiffrage

> **Version cible :** v1.1.0
> **Date :** 06/02/2026
> **Statut :** En attente de validation

---

## Table des matières

1. [Vue d'ensemble](#1-vue-densemble)
2. [Architecture base de données](#2-architecture-base-de-données)
3. [Paramètres de chiffrage](#3-paramètres-de-chiffrage)
4. [Module import DPGF](#4-module-import-dpgf)
5. [Module chiffrage DPGF](#5-module-chiffrage-dpgf)
6. [Module analyse marchés](#6-module-analyse-marchés)
7. [Module résultat marché](#7-module-résultat-marché)
8. [Export DPGF](#8-export-dpgf)
9. [Interface utilisateur](#9-interface-utilisateur)
10. [Fichiers impactés](#10-fichiers-impactés)
11. [Phases de développement](#11-phases-de-développement)

---

## 1. Vue d'ensemble

### Objectif
Ajouter un module complet de gestion des marchés publics dans DestriChiffrage permettant de :
- **Importer** un DPGF vierge (CSV) et le compléter dans l'application
- **Chiffrer** chaque article en liant un produit catalogue + temps de MO
- **Exporter** le DPGF complété au même format
- **Analyser** l'historique des marchés et prix de référence
- **Enregistrer** les résultats (gagné/perdu) et prix des concurrents

### Flux utilisateur

```
┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────────┐
│  Import     │────>│  Chiffrage   │────>│  Export      │────>│  Résultat    │
│  DPGF CSV   │     │  articles    │     │  DPGF CSV    │     │  gagné/perdu │
│  + création │     │  + produits  │     │  + sauvegarde│     │  + concurrent│
│  chantier   │     │  + temps MO  │     │  en BDD      │     │  + montant   │
└─────────────┘     └──────────────┘     └──────────────┘     └──────────────┘
```

---

## 2. Architecture base de données

### 2.1 Nouvelle table `chantiers`

```sql
CREATE TABLE IF NOT EXISTS chantiers (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    id_chantier     TEXT UNIQUE NOT NULL,      -- Ex: CHT-2025-HOENHEIM
    nom             TEXT NOT NULL,
    lieu            TEXT,
    type_projet     TEXT,
    lot             TEXT,
    annee           INTEGER,
    montant_ht      REAL,                      -- Montant total soumis HT
    montant_ttc     REAL,
    resultat        TEXT,                      -- GAGNE|PERDU|PERTE|TROP_CHER|EN_COURS|INCONNU
    rentabilite     TEXT,
    retour_experience TEXT,
    architecte      TEXT,
    concurrent_nom       TEXT,                 -- Nom du concurrent retenu
    concurrent_montant_ht REAL,                -- Montant global HT concurrent
    lien_cctp       TEXT,                      -- Chemin relatif vers PDF CCTP
    date_ajout      TEXT DEFAULT CURRENT_TIMESTAMP,
    date_modification TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### 2.2 Nouvelle table `prix_marche`

```sql
CREATE TABLE IF NOT EXISTS prix_marche (
    id                  INTEGER PRIMARY KEY AUTOINCREMENT,
    id_prix             TEXT UNIQUE NOT NULL,   -- Ex: PM-PRT-001
    chantier_id         INTEGER NOT NULL,       -- FK -> chantiers.id
    produit_id          INTEGER,                -- FK -> produits.id (nullable)
    categorie           TEXT NOT NULL,           -- PORTES|AGENCEMENT|DIVERS
    sous_categorie      TEXT,
    designation         TEXT NOT NULL,
    dimensions          TEXT,
    caracteristiques    TEXT,
    unite               TEXT DEFAULT 'U',       -- U|ENS|ML|M2|FT
    quantite            REAL DEFAULT 1,
    -- Prix
    prix_unitaire_ht    REAL DEFAULT 0,         -- Prix de vente unitaire soumis
    prix_total_ht       REAL DEFAULT 0,         -- = prix_unitaire_ht * quantite
    -- Coût de revient
    cout_achat          REAL DEFAULT 0,         -- Prix d'achat produit (auto si produit_id)
    temps_conception_h  REAL DEFAULT 0,         -- Heures de conception/étude
    temps_fabrication_h REAL DEFAULT 0,         -- Heures de fabrication
    temps_pose_h        REAL DEFAULT 0,         -- Heures d'installation
    cout_mo_total       REAL DEFAULT 0,         -- Coût MO calculé
    cout_revient        REAL DEFAULT 0,         -- cout_achat + cout_mo_total
    marge_pct           REAL DEFAULT 0,         -- Marge réelle calculée
    -- Métadonnées
    resultat_marche     TEXT,                   -- Hérité du chantier ou spécifique
    fiabilite           TEXT,                   -- REFERENCE|PLAFOND|PLANCHER_DANGER|A_VALIDER
    match_confiance     TEXT,                   -- FORT|MOYEN|FAIBLE (matching auto)
    notes               TEXT,
    lien_cctp           TEXT,
    page_cctp           TEXT,
    date_ajout          TEXT DEFAULT CURRENT_TIMESTAMP,
    date_modification   TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chantier_id) REFERENCES chantiers(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);
```

### 2.3 Nouvelle table `dpgf_structure` (hiérarchie DPGF)

```sql
CREATE TABLE IF NOT EXISTS dpgf_structure (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    chantier_id     INTEGER NOT NULL,       -- FK -> chantiers.id
    code            TEXT NOT NULL,           -- Code article DPGF (1., 1.1, 16.4.1)
    niveau          INTEGER NOT NULL,        -- 1=Lot, 2=Chapitre, 3=Sous-chapitre
    designation     TEXT NOT NULL,           -- Libellé du chapitre/sous-chapitre
    categorie       TEXT,                    -- PORTES|AGENCEMENT|DIVERS
    ordre           INTEGER NOT NULL,        -- Ordre d'affichage (numéro de ligne)
    FOREIGN KEY (chantier_id) REFERENCES chantiers(id)
);
```

> Cette table stocke les lignes de NIVEAU 1-3 du CSV pour reconstituer la hiérarchie lors de l'affichage et de l'export. Les articles chiffrables (NIVEAU 4) sont dans `prix_marche`.

### 2.4 Index pour performances

```sql
CREATE INDEX IF NOT EXISTS idx_prix_marche_chantier ON prix_marche(chantier_id);
CREATE INDEX IF NOT EXISTS idx_prix_marche_produit ON prix_marche(produit_id);
CREATE INDEX IF NOT EXISTS idx_prix_marche_categorie ON prix_marche(categorie);
CREATE INDEX IF NOT EXISTS idx_chantiers_resultat ON chantiers(resultat);
CREATE INDEX IF NOT EXISTS idx_chantiers_annee ON chantiers(annee);
```

---

## 3. Paramètres de chiffrage

### 3.1 Nouveaux paramètres dans la table `parametres`

| Clé | Valeur par défaut | Description |
|-----|-------------------|-------------|
| `taux_horaire_conception` | `45.0` | Taux horaire conception/étude (€/h) |
| `taux_horaire_fabrication` | `38.0` | Taux horaire fabrication atelier (€/h) |
| `taux_horaire_pose` | `42.0` | Taux horaire pose/installation (€/h) |
| `marge_marche_defaut` | `20.0` | Marge par défaut sur marchés publics (%) |

### 3.2 Formule de calcul du prix de vente

```
cout_achat          = produit.prix_achat (si produit lié) ou saisie manuelle
cout_mo_conception  = temps_conception_h × taux_horaire_conception
cout_mo_fabrication = temps_fabrication_h × taux_horaire_fabrication
cout_mo_pose        = temps_pose_h × taux_horaire_pose
cout_mo_total       = cout_mo_conception + cout_mo_fabrication + cout_mo_pose
cout_revient        = cout_achat + cout_mo_total
prix_unitaire_ht    = cout_revient × (1 + marge / 100)
prix_total_ht       = prix_unitaire_ht × quantite
marge_pct           = ((prix_unitaire_ht - cout_revient) / cout_revient) × 100
```

### 3.3 Modification SettingsDialog

Ajouter un onglet **"Chiffrage marchés"** dans `SettingsDialog` avec :
- Taux horaire conception (€/h)
- Taux horaire fabrication (€/h)
- Taux horaire pose (€/h)
- Marge marchés par défaut (%)

---

## 4. Module import DPGF

> **Voir document détaillé :** `docs/FORMAT_IMPORT_DPGF.md`

### 4.1 Format du template DPGF d'import

Fichier CSV téléchargeable depuis l'application. Délimiteur `;`, encodage UTF-8 BOM.

**Colonnes du template (11 colonnes) :**

```
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES
```

| Colonne | Type | Obligatoire | Description |
|---------|------|-------------|-------------|
| `CODE` | Texte | Oui | Code article du DPGF original (ex: `1.1`, `16.4.1.1`) |
| `NIVEAU` | Entier | Oui | 1=Lot, 2=Chapitre, 3=Sous-chapitre, **4=Article chiffrable** |
| `DESIGNATION` | Texte | Oui | Libellé de l'article |
| `CATEGORIE` | Texte | Non | `PORTES`, `AGENCEMENT`, `DIVERS`, `MOBILIER`... |
| `LARGEUR_MM` | Entier | Non | Largeur en mm |
| `HAUTEUR_MM` | Entier | Non | Hauteur en mm |
| `CARACTERISTIQUES` | Texte | Non | EI30, RA=35dB, finition... |
| `UNITE` | Texte | Oui (niv.4) | U, ENS, ML, M2, FT |
| `QUANTITE` | Nombre | Oui (niv.4) | Quantité du DPGF |
| `LOCALISATION` | Texte | Non | Emplacement (RDC, R+1, salle X) |
| `NOTES` | Texte | Non | Remarques, réf. CCTP |

**Règle clé :** Seuls les articles de **NIVEAU 4** sont importés dans `prix_marche`. Les niveaux 1-3 sont conservés pour l'affichage hiérarchique et l'export.

L'utilisateur remplit ce CSV avec les articles du DPGF qu'il a reçu, puis l'importe dans l'application.

### 4.2 Dialogue d'import DPGF : `DPGFImportDialog`

**Étape 1 : Créer ou sélectionner le chantier**
- Nom du chantier (obligatoire)
- Lieu
- Type de projet
- Lot
- Année
- Architecte / MOE
- Parcourir → fichier CCTP (PDF)

**Étape 2 : Sélectionner le fichier CSV**
- Parcourir → fichier CSV DPGF
- Aperçu des 5 premières lignes
- Choix catégorie par défaut (PORTES / AGENCEMENT / DIVERS)

**Étape 3 : Validation et import**
- Création du chantier en BDD
- Import des articles dans `prix_marche` avec statut `EN_COURS`
- Lancement automatique du matching semi-auto avec le catalogue
- Ouverture de la vue chiffrage

### 4.3 Méthodes database.py

```python
def import_dpgf_csv(self, filepath, chantier_id, categorie_defaut="PORTES"):
    """Importe un DPGF CSV dans prix_marche.
    - Lit le CSV (délimiteur ;, UTF-8 BOM)
    - Filtre les lignes NIVEAU=4 (articles chiffrables)
    - Génère id_prix auto : PM-{CODE}
    - Formate dimensions : LARGEUR_MM x HAUTEUR_MM mm
    - Concatène LOCALISATION + NOTES dans le champ notes
    - Applique categorie_defaut si CATEGORIE vide
    - Retourne : (nb_articles_importés, nb_lignes_structure)
    """

def import_dpgf_structure(self, filepath, chantier_id):
    """Importe la structure hiérarchique (NIVEAU 1-3) pour l'affichage.
    Stockée dans une table auxiliaire dpgf_structure."""

def create_dpgf_template(self, filepath):
    """Génère le template CSV DPGF vide téléchargeable.
    Inclut l'en-tête + 2 lignes d'exemple commentées."""

def add_chantier(self, data):
    """Crée un nouveau chantier. Retourne l'ID."""

def update_chantier(self, chantier_id, data):
    """Met à jour un chantier existant."""

def get_chantier(self, chantier_id):
    """Retourne un chantier par ID."""

def get_chantiers(self, resultat=None, annee=None):
    """Liste les chantiers avec filtres optionnels."""

def delete_chantier(self, chantier_id, permanent=False):
    """Supprime un chantier et ses prix_marche associés."""
```

---

## 5. Module chiffrage DPGF

### 5.1 Vue chiffrage : `DPGFChiffrageView`

Vue principale affichée après import ou en ouvrant un chantier existant.

**Layout :**

```
┌─────────────────────────────────────────────────────────┐
│  EN-TÊTE CHANTIER                                       │
│  Nom | Lieu | Lot | Année | Architecte      [Modifier]  │
├─────────────────────────────────────────────────────────┤
│  TABLEAU DES ARTICLES DPGF                              │
│  ┌─────┬─────────────┬──────┬───┬────┬──────┬─────────┐ │
│  │ N°  │ Désignation │ Unité│Qté│ PU │ PT   │Produit  │ │
│  ├─────┼─────────────┼──────┼───┼────┼──────┼─────────┤ │
│  │ 001 │ BP EI30     │  U   │ 5 │562 │2810  │ #599 ✓  │ │
│  │ 002 │ BP acous.   │  U   │ 3 │875 │2625  │ #620 ?  │ │
│  │ 003 │ Kitchenette │  ENS │ 1 │    │      │ --      │ │
│  └─────┴─────────────┴──────┴───┴────┴──────┴─────────┘ │
│  [Ajouter article] [Supprimer] [Importer articles]      │
├─────────────────────────────────────────────────────────┤
│  PANNEAU DE CHIFFRAGE (article sélectionné)             │
│  ┌─────────────────────┬───────────────────────────┐    │
│  │ Produit lié: #599   │  Coût achat: 297.04 €    │    │
│  │ [Chercher] [Créer]  │                            │    │
│  ├─────────────────────┼───────────────────────────┤    │
│  │ Conception:  0.5 h  │  = 22.50 €               │    │
│  │ Fabrication: 1.0 h  │  = 38.00 €               │    │
│  │ Pose:        1.5 h  │  = 63.00 €               │    │
│  ├─────────────────────┼───────────────────────────┤    │
│  │ Coût MO total:      │  123.50 €                │    │
│  │ Coût de revient:    │  420.54 €                │    │
│  │ Marge (20%):        │  84.11 €                 │    │
│  │ PU HT proposé:      │  504.65 €                │    │
│  │ PT HT (x5):         │  2523.25 €               │    │
│  └─────────────────────┴───────────────────────────┘    │
├─────────────────────────────────────────────────────────┤
│  BARRE TOTAUX                                           │
│  Total HT: 7 958.25 €  |  Marge moy: 18.2%            │
│  [Exporter DPGF]  [Enregistrer]                         │
└─────────────────────────────────────────────────────────┘
```

### 5.2 Dialogue recherche produit : `ProductSearchDialog`

Lorsqu'on clique "Chercher" pour lier un produit à un article DPGF :
- Barre de recherche avec filtres identiques au catalogue
- Treeview affichant les résultats avec prix achat
- Double-clic → sélectionne le produit et retourne l'ID
- Bouton "Créer nouveau" → ouvre `ProductDialog`, retourne l'ID du nouveau produit

### 5.3 Calcul en temps réel

À chaque modification d'un champ (produit, temps, marge) :
1. Recalculer coût MO via les taux horaires des paramètres
2. Recalculer coût de revient = achat + MO
3. Recalculer PU HT = revient × (1 + marge%)
4. Recalculer PT HT = PU × quantité
5. Recalculer le total chantier
6. Mettre à jour la marge moyenne

### 5.4 Méthodes database.py

```python
def get_prix_marche_by_chantier(self, chantier_id):
    """Retourne tous les articles d'un chantier."""

def get_prix_marche(self, prix_id):
    """Retourne un article prix_marche par ID."""

def add_prix_marche(self, data):
    """Ajoute un article dans prix_marche."""

def update_prix_marche(self, prix_id, data):
    """Met à jour un article prix_marche."""

def delete_prix_marche(self, prix_id):
    """Supprime un article prix_marche."""

def link_produit_to_prix(self, prix_id, produit_id):
    """Lie un produit catalogue à un article DPGF.
    Met à jour automatiquement cout_achat depuis produit.prix_achat."""

def recalculate_prix(self, prix_id):
    """Recalcule tous les coûts d'un article DPGF."""

def recalculate_chantier_total(self, chantier_id):
    """Recalcule le montant_ht total du chantier."""
```

---

## 6. Module analyse marchés

### 6.1 Vue analyse : `MarchesAnalyseView`

Accessible via le menu principal ou un onglet/bouton dédié.

**Layout :**

```
┌───────────────────────────────────────────────────────┐
│  FILTRES                                              │
│  Année: [Toutes ▼]  Résultat: [Tous ▼]  Catégorie: [▼]│
├───────────────────────────────────────────────────────┤
│  LISTE DES CHANTIERS                                  │
│  ┌──────────────────┬──────┬──────────┬───────┬──────┐│
│  │ Chantier         │Année │Montant HT│Résult.│Écart ││
│  ├──────────────────┼──────┼──────────┼───────┼──────┤│
│  │ ● APEDI          │ 2023 │82 157 €  │GAGNÉ  │  --  ││
│  │ ● Stabilo        │ 2024 │90 550 €  │T.CHER │+12%  ││
│  │ ● Thal-Marmoutier│ 2023 │119 899 € │PERTE  │-25%  ││
│  └──────────────────┴──────┴──────────┴───────┴──────┘│
├───────────────────────────────────────────────────────┤
│  DÉTAIL CHANTIER SÉLECTIONNÉ                          │
│  Articles du DPGF avec prix soumis + produit lié      │
│  Colonne "Prix catalogue" si produit lié              │
│  Colonne "Écart" = (vente - revient) / revient        │
├───────────────────────────────────────────────────────┤
│  STATISTIQUES                                         │
│  Taux de réussite: 4/8 (50%)                          │
│  Marge moy. gagnés: 18.5%  |  Marge moy. perdus: 28% │
│  Nb articles avec produit lié: 28/152                 │
│  [Ouvrir chantier]  [Modifier résultat]               │
└───────────────────────────────────────────────────────┘
```

### 6.2 Code couleur

| Résultat | Couleur fond | Couleur texte |
|----------|-------------|---------------|
| GAGNE | `#C6EFCE` (vert clair) | `#006100` |
| PERDU | `#FFC7CE` (rose) | `#9C0006` |
| PERTE | `#FF6347` (rouge vif) | `#FFFFFF` |
| TROP_CHER | `#FFEB9C` (jaune) | `#9C6500` |
| EN_COURS | `#D6E4F0` (bleu clair) | `#1E293B` |
| INCONNU | `#F1F5F9` (gris) | `#64748B` |

### 6.3 Analyse par produit

Quand un produit du catalogue est sélectionné dans la vue principale, afficher dans un panneau ou infobulle :
- Historique des prix soumis pour ce produit (via `produit_id`)
- Prix min / max / moyen soumis
- Résultat de chaque soumission
- **Fourchette recommandée** : entre le prix gagné le plus bas et le prix perdu le plus bas

### 6.4 Méthodes database.py

```python
def get_prix_marche_by_produit(self, produit_id):
    """Tous les prix marché liés à un produit du catalogue."""

def get_stats_marches(self, annee=None):
    """Statistiques globales: taux réussite, marges moyennes, etc."""

def get_fourchette_prix(self, produit_id):
    """Retourne min/max/moyenne des prix soumis pour un produit,
    séparés par résultat (gagné vs perdu)."""

def search_prix_marche(self, terme=None, categorie=None,
                       resultat=None, fiabilite=None, chantier_id=None):
    """Recherche multi-critères dans prix_marche."""
```

---

## 7. Module résultat marché

### 7.1 Dialogue résultat : `ResultatMarcheDialog`

Accessible depuis la vue analyse ou la vue chiffrage. S'ouvre quand l'utilisateur veut enregistrer le résultat d'un appel d'offres.

**Champs :**
- **Résultat** : GAGNE / PERDU / TROP_CHER / PERTE (combobox)
- **Concurrent retenu** : Nom de l'entreprise (texte, affiché si PERDU)
- **Montant concurrent HT** : Montant global HT (numérique, affiché si PERDU)
- **Rentabilité** : Texte libre (affiché si GAGNE ou PERTE)
- **Retour d'expérience** : Zone de texte multiligne

### 7.2 Logique

À la sauvegarde :
1. Met à jour `chantiers.resultat`, `concurrent_nom`, `concurrent_montant_ht`
2. Recalcule `chantiers.montant_ht` depuis la somme des `prix_marche.prix_total_ht`
3. Met à jour `prix_marche.resultat_marche` et `prix_marche.fiabilite` pour tous les articles du chantier
4. Calcul de l'écart avec le concurrent : `ecart_pct = (montant_destribois - concurrent) / concurrent × 100`

### 7.3 Méthodes database.py

```python
def set_resultat_marche(self, chantier_id, resultat, concurrent_nom=None,
                        concurrent_montant_ht=None, rentabilite=None,
                        retour_experience=None):
    """Enregistre le résultat d'un marché et cascade la fiabilité."""

def get_ecart_concurrent(self, chantier_id):
    """Calcule l'écart entre notre montant et celui du concurrent."""
```

---

## 8. Export DPGF

### 8.1 Format d'export

Même format CSV que l'import, enrichi des colonnes de prix. Délimiteur `;`, UTF-8 BOM.

**Export client (DPGF réponse) :**
```
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES;PU_HT;PT_HT
```

**Export interne (avec coûts) :**
```
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES;PU_HT;PT_HT;PRODUIT_ID;COUT_ACHAT;TEMPS_CONCEPTION_H;TEMPS_FABRICATION_H;TEMPS_POSE_H;COUT_MO_TOTAL;COUT_REVIENT;MARGE_PCT
```

### 8.2 Dialogue export : `DPGFExportDialog`

- Sélection du chantier à exporter (si pas déjà dans la vue)
- Choix du fichier de destination
- Option : inclure les colonnes de coût de revient (interne) ou seulement le DPGF client (sans coûts)
- Option : copier le CCTP dans le dossier d'export
- Bouton "Exporter"

### 8.3 Méthodes database.py

```python
def export_dpgf_csv(self, chantier_id, filepath, include_costs=False):
    """Exporte le DPGF d'un chantier au format CSV."""

def export_dpgf_client_csv(self, chantier_id, filepath):
    """Exporte le DPGF version client (sans coûts internes)."""
```

---

## 9. Interface utilisateur

### 9.1 Modifications du menu principal

```
Fichier
  ├── Import catalogue CSV        (existant)
  ├── Export catalogue CSV         (existant)
  ├── Télécharger template CSV     (existant)
  ├── ─────────────────
  ├── Nouveau chantier / DPGF     (NOUVEAU)
  ├── Importer DPGF               (NOUVEAU)
  ├── ─────────────────
  └── Quitter

Edition
  ├── Nouveau produit              (existant)
  ├── Modifier                     (existant)
  ├── Supprimer                    (existant)
  ├── ─────────────────
  ├── Gérer les catégories         (existant)
  ├── Paramètres                   (existant)
  └── Vider la base                (existant)

Marchés                             (NOUVEAU MENU)
  ├── Analyse des marchés          → ouvre MarchesAnalyseView
  ├── Historique des chantiers     → ouvre liste chantiers
  ├── ─────────────────
  └── Importer historique CSV      → import IMPORT_CHANTIERS.csv + IMPORT_PRIX_MARCHE.csv

Affichage
  ├── Actualiser                   (existant)
  └── Statistiques                 (existant + enrichi marchés)

Aide
  ├── Vérifier les MAJ             (existant)
  └── À propos                     (existant)
```

### 9.2 Bouton d'accès rapide

Ajouter un bouton **"Marchés"** dans le header (à côté du panier) avec un badge affichant le nombre de chantiers EN_COURS.

### 9.3 Panneau d'info produit (vue catalogue)

Quand un produit est sélectionné dans le Treeview principal, afficher en bas ou dans un panneau latéral :
- Nombre de fois soumis en marché
- Fourchette de prix soumis (min - max)
- Dernier résultat (gagné/perdu)

---

## 10. Fichiers impactés

### Fichiers à MODIFIER

| Fichier | Modifications |
|---------|---------------|
| `src/database.py` | +tables chantiers/prix_marche, +méthodes CRUD, +import/export DPGF, +paramètres MO |
| `src/ui/main_window.py` | +menu Marchés, +bouton header, +panneau info produit |
| `src/ui/dialogs.py` | +onglet Chiffrage dans SettingsDialog |
| `src/version.py` | Version → 1.1.0 |

### Fichiers à CRÉER

| Fichier | Rôle |
|---------|------|
| `src/ui/dpgf_import_dialog.py` | Dialogue d'import DPGF (création chantier + import CSV) |
| `src/ui/dpgf_chiffrage_view.py` | Vue principale de chiffrage d'un DPGF |
| `src/ui/dpgf_export_dialog.py` | Dialogue d'export DPGF |
| `src/ui/marches_analyse_view.py` | Vue d'analyse globale des marchés |
| `src/ui/resultat_marche_dialog.py` | Dialogue de saisie résultat (gagné/perdu + concurrent) |
| `src/ui/product_search_dialog.py` | Dialogue de recherche/sélection produit pour lier à un article |

### Fichiers inchangés

| Fichier | Raison |
|---------|--------|
| `src/ui/theme.py` | Réutilisation du thème existant + nouvelles couleurs marchés |
| `src/ui/cart_panel.py` | Pas impacté |
| `src/ui/cart_export_dialog.py` | Pas impacté |
| `src/config.py` | Pas impacté (les paramètres marchés sont en BDD) |
| `src/cart_manager.py` | Pas impacté |
| `src/updater.py` | Pas impacté |

---

## 11. Phases de développement

### Phase 1 : Base de données et paramètres
**Fichiers :** `database.py`, `dialogs.py`
1. Créer tables `chantiers` et `prix_marche` avec migrations
2. Ajouter les paramètres de taux horaires
3. Implémenter toutes les méthodes CRUD chantiers et prix_marche
4. Ajouter l'onglet "Chiffrage marchés" dans SettingsDialog
5. Implémenter `import_chantiers_csv()` et `import_prix_marche_csv()` pour l'import initial de l'historique

### Phase 2 : Import DPGF
**Fichiers :** `dpgf_import_dialog.py`, `database.py`
1. Créer `create_dpgf_template()` pour générer le template CSV
2. Créer `DPGFImportDialog` (création chantier + import CSV)
3. Intégrer le matching semi-auto des produits
4. Ajouter les entrées menu dans `main_window.py`

### Phase 3 : Vue chiffrage
**Fichiers :** `dpgf_chiffrage_view.py`, `product_search_dialog.py`, `database.py`
1. Créer `DPGFChiffrageView` avec tableau articles + panneau de chiffrage
2. Créer `ProductSearchDialog` pour la recherche/sélection de produit
3. Implémenter le calcul en temps réel (coûts, marges, totaux)
4. Permettre l'ajout/suppression d'articles dans le DPGF
5. Permettre la création de produit à la volée depuis la vue chiffrage

### Phase 4 : Export DPGF
**Fichiers :** `dpgf_export_dialog.py`, `database.py`
1. Créer `DPGFExportDialog`
2. Implémenter `export_dpgf_csv()` (version interne + version client)
3. Sauvegarde automatique en BDD

### Phase 5 : Résultat marché et analyse
**Fichiers :** `resultat_marche_dialog.py`, `marches_analyse_view.py`, `main_window.py`
1. Créer `ResultatMarcheDialog` (gagné/perdu + concurrent)
2. Créer `MarchesAnalyseView` avec liste chantiers + détail + stats
3. Ajouter le panneau d'info produit dans la vue catalogue
4. Implémenter le code couleur et les statistiques

### Phase 6 : Import historique et finalisation
**Fichiers :** `main_window.py`, `database.py`
1. Import des CSV existants (`IMPORT_CHANTIERS.csv` + `IMPORT_PRIX_MARCHE.csv`)
2. Tests complets du flux import → chiffrage → export → résultat
3. Bump version → 1.1.0
