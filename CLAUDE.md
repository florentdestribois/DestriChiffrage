# DestriChiffrage - Agent Claude Specialise
# ==========================================
# Application de chiffrage et approvisionnement Destribois
# Integration SolidWorks / SWOOD / Optiplanning

## Identite et Contexte

Tu es un agent Claude specialise dans le developpement de **DestriChiffrage**, une application desktop Python/Tkinter de chiffrage et gestion d'approvisionnement pour l'entreprise **Destribois** (menuiserie/agencement). Tu maitrises parfaitement l'architecture existante et tu travailles sur l'integration avec le pipeline SolidWorks/SWOOD.

## Architecture du Projet

```
DestriChiffrage/
├── src/
│   ├── main.py              # Point d'entree Tkinter
│   ├── config.py             # Config globale (Singleton, settings.ini)
│   ├── database.py           # Coeur BDD SQLite (~2600 lignes)
│   ├── cart_manager.py       # Gestionnaire devis rapide (Singleton)
│   ├── version.py            # Version actuelle: 1.8.3
│   └── ui/
│       ├── theme.py          # Theme Destribois (couleurs, polices, widgets)
│       ├── main_window.py    # Fenetre principale (~1200 lignes)
│       ├── dialogs.py        # Dialogues produit/categorie
│       ├── product_search_dialog.py  # Recherche produits
│       ├── import_dialog.py  # Import CSV avec mapping
│       ├── chantier_dialog.py       # Gestion chantiers/marches
│       ├── dpgf_dialog.py           # Module DPGF complet
│       └── ...
├── data/
│   ├── catalogue.db          # Base SQLite principale
│   ├── Fiches_techniques/    # PDFs fiches techniques par categorie
│   └── Devis_fournisseur/    # PDFs devis fournisseurs
├── config/
│   └── settings.ini          # Configuration persistante
├── assets/
│   ├── icon.ico
│   └── fonts/                # Abhaya Libre, Roboto (TTF)
├── docs/                     # Documentation
├── tests/                    # Tests pytest
├── requirements.txt          # Dependances (Pillow, openpyxl, requests, pyinstaller)
└── installer_simple.iss      # Script InnoSetup
```

## Schema Base de Donnees (SQLite)

### Table `produits` - Catalogue principal
```sql
CREATE TABLE produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    categorie TEXT NOT NULL,
    sous_categorie TEXT,
    designation TEXT NOT NULL,
    dimensions TEXT,
    hauteur INTEGER,
    largeur INTEGER,
    prix_achat REAL DEFAULT 0,
    reference TEXT,
    fournisseur TEXT,
    marque TEXT,
    chantier TEXT,
    notes TEXT,
    fiche_technique TEXT,    -- Chemin relatif PDF
    devis_fournisseur TEXT,  -- Chemin relatif PDF
    actif INTEGER DEFAULT 1,
    date_ajout TEXT DEFAULT CURRENT_TIMESTAMP,
    date_modification TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Table `categories` - Arborescence produits
```sql
CREATE TABLE categories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT UNIQUE NOT NULL,
    description TEXT,
    couleur TEXT DEFAULT '#1F4E79',
    ordre INTEGER DEFAULT 0
);
```

### Table `chantiers` - Gestion des marches
```sql
CREATE TABLE chantiers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    nom TEXT NOT NULL,
    nom_client TEXT,
    type_marche TEXT DEFAULT 'PUBLIC',  -- PUBLIC / PRIVE
    lieu TEXT,
    type_projet TEXT,
    lot TEXT,
    montant_ht REAL DEFAULT 0,
    marge_projet REAL,
    resultat TEXT DEFAULT 'EN_COURS',  -- EN_COURS / GAGNE / PERDU
    concurrent TEXT,
    montant_concurrent REAL,
    notes TEXT,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    date_modification TEXT DEFAULT CURRENT_TIMESTAMP
);
```

### Table `prix_marche` - Articles DPGF (26 colonnes)
```sql
CREATE TABLE prix_marche (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    chantier_id INTEGER NOT NULL,
    code TEXT,
    niveau INTEGER DEFAULT 4,
    designation TEXT NOT NULL,
    description TEXT,
    presentation TEXT,
    categorie TEXT,
    largeur_mm INTEGER,
    hauteur_mm INTEGER,
    caracteristiques TEXT,
    unite TEXT DEFAULT 'U',
    quantite REAL DEFAULT 1,
    localisation TEXT,
    notes TEXT,
    temps_conception REAL DEFAULT 0,
    temps_fabrication REAL DEFAULT 0,
    temps_pose REAL DEFAULT 0,
    cout_materiaux REAL DEFAULT 0,
    cout_mo_total REAL DEFAULT 0,
    cout_revient REAL DEFAULT 0,
    marge_pct REAL DEFAULT 20,
    taux_tva REAL DEFAULT 20,
    prix_unitaire_ht REAL DEFAULT 0,
    prix_total_ht REAL DEFAULT 0,
    date_creation TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (chantier_id) REFERENCES chantiers(id)
);
```

### Table `article_produits` - Liaison articles <-> produits
```sql
CREATE TABLE article_produits (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    prix_marche_id INTEGER NOT NULL,
    produit_id INTEGER NOT NULL,
    quantite REAL DEFAULT 1,
    prix_unitaire REAL DEFAULT 0,
    FOREIGN KEY (prix_marche_id) REFERENCES prix_marche(id),
    FOREIGN KEY (produit_id) REFERENCES produits(id)
);
```

### Tables auxiliaires
- `parametres` (cle/valeur) : marge globale, taux horaires, config
- `historique_prix` : suivi des changements de prix
- `dpgf_structure` : structure hierarchique DPGF (lots, sous-lots)

## API Database.py - Methodes Cles

### Import/Export CSV
```python
import_csv(filepath, mapping=None, progress_callback=None) -> int
# Import CSV ; delimiter ';' ; encoding UTF-8-sig
# Mapping colonnes: CATEGORIE, SOUS_CATEGORIE, DESIGNATION, DIMENSIONS,
#   HAUTEUR, LARGEUR, PRIX_ACHAT, REFERENCE, FOURNISSEUR, MARQUE, NOTES
# Retourne nombre de produits importes

export_csv(filepath, produits=None, marge=None, include_prix_vente=True, delimiter=';') -> int
# Export CSV complet catalogue ou selection

export_cart_to_csv(product_ids, filepath, marge=None, ...) -> int
# Export devis rapide vers CSV avec copie PDFs optionnelle

create_import_template(filepath, delimiter=';')
# Genere template CSV vierge avec en-tetes
```

### DPGF (Decomposition du Prix Global Forfaitaire)
```python
import_dpgf_csv(chantier_id, filepath) -> int
export_dpgf_csv(chantier_id, filepath, version_client=False) -> int
export_dpgf_files(chantier_id, export_dir, include_fiches=True, include_devis=True, naming_options=None) -> tuple
export_dpgf_odoo(chantier_id, filepath) -> int  # Export format ERP Odoo
create_dpgf_template(filepath)
```

### CRUD Produits
```python
add_produit(data: Dict) -> int
update_produit(id: int, data: Dict)
delete_produit(id: int, permanent=False)
search_produits(terme="", categorie="", actif_only=True, ...) -> List[Dict]
get_produit(id: int) -> Optional[Dict]
```

### Gestion Chantiers
```python
add_chantier(data) -> int
update_chantier(chantier_id, data)
delete_chantier(chantier_id)
get_chantier_recap(chantier_id) -> Dict
set_chantier_marge_projet(chantier_id, marge)
```

## Theme Destribois (ui/theme.py)

```python
# Palette couleurs
PRIMARY = '#2E3544'       # Bleu-gris fonce (headers, nav)
SECONDARY = '#AE9367'     # Or/dore (accents, boutons principaux)
ACCENT = '#3B7A57'        # Vert foret (success, validation)
BG = '#F7F5F2'            # Beige clair (fond)
CARD_BG = '#FFFFFF'       # Blanc (cartes)
TEXT = '#2C3E50'          # Texte principal
TEXT_LIGHT = '#95A5A6'    # Texte secondaire
DANGER = '#B4503C'        # Rouge brique (suppression, erreurs)

# Polices
TITLE_FONT = 'Abhaya Libre'  # Titres (serif elegant)
BODY_FONT = 'Roboto'         # Corps de texte (sans-serif)
MONO_FONT = 'Consolas'       # Code mono

# Methodes factory dans Theme:
# Theme.apply(root)           -> Applique le theme global
# Theme.create_button(parent, text, command, style)
# Theme.create_card(parent)
# Theme.create_header(parent, text)
# Theme.create_gold_button(parent, text, command)
# Theme.create_danger_button(parent, text, command)
```

## Pipeline SolidWorks / SWOOD / Optiplanning

### Flux de donnees actuel
```
SolidWorks/SWOOD Design
    |
    v
Outil_Material_Import.xlsm (macro Excel)
    |
    v
step9_export_optiplanning.py (Python)
    |
    v
Export TXT (8 colonnes, tab-delimited)
    |
    v
Optiplanning (logiciel d'optimisation de debit)
```

### Format TXT Optiplanning (8 colonnes)
```
SawReference | BOARDL | BOARDW | Thickness | FiberMaterial | Cost | Parametres | Ref Fournisseur
```

**Mapping XLSM -> TXT :**
| Colonne XLSM        | Colonne TXT     | Description                    |
|---------------------|-----------------|--------------------------------|
| SawReference (A)    | SawReference    | Reference piece/panneau        |
| BOARDL (B)          | BOARDL          | Longueur panneau (mm)          |
| BOARDW (C)          | BOARDW          | Largeur panneau (mm)           |
| Thickness (D)       | Thickness       | Epaisseur (mm)                 |
| FiberMaterial (E)   | FiberMaterial   | Materiau + sens fibre          |
| Cost (F)            | Cost            | Cout unitaire                  |
| Parametres (G)      | Parametres      | Params complementaires         |
| Ref Fournisseur (H) | Ref Fournisseur | Reference fournisseur materiau |

### Script step9_export_optiplanning.py
- Lit le fichier XLSM (openpyxl)
- Extraction colonnes A-H de la feuille "BDD"
- Nettoyage donnees (formatage numerique, trim)
- Ecriture TXT tab-delimited
- Encodage: UTF-8

## Objectifs d'Integration SolidWorks <-> DestriChiffrage

### 1. Import Materiaux SolidWorks
Creer un module d'import dans DestriChiffrage capable de :
- Lire les fichiers CSV/TXT generes par le pipeline SWOOD
- Mapper les colonnes SolidWorks vers la table `produits` :
  ```
  FiberMaterial  -> designation (ou sous_categorie)
  BOARDL/BOARDW  -> dimensions (format "LxW")
  Thickness      -> hauteur (ou champ dedie)
  Cost           -> prix_achat
  Ref Fournisseur -> reference + fournisseur
  SawReference   -> notes (ou reference interne)
  ```
- Categoriser automatiquement (categorie "Panneaux SWOOD" ou detection auto)
- Gerer les doublons (mise a jour prix si materiau existant)

### 2. Export Materiaux vers SolidWorks
Creer un export depuis le catalogue DestriChiffrage vers le format attendu par SWOOD :
- Generer le fichier CSV compatible Outil_Material_Import.xlsm
- Permettre la selection de produits a exporter (par categorie, filtre)
- Mapper les champs DestriChiffrage -> colonnes SolidWorks

### 3. Synchronisation Base de Donnees
- Synchronisation bidirectionnelle materiaux/prix
- Historique des imports/exports SolidWorks dans `historique_prix`
- Detection de conflits (prix different entre sources)

### 4. Interface UI
- Nouvel onglet ou section dans main_window.py
- Boutons Import/Export SolidWorks dans la toolbar
- Preview des donnees avant import
- Log des operations effectuees
- Respecter le theme Destribois existant (Theme.create_*)

## Conventions de Code

- **Langue** : Code en anglais, commentaires/docstrings en francais sans accents dans les identifiants
- **Encodage** : UTF-8 partout, CSV en UTF-8-sig avec delimiter ';'
- **Typage** : Type hints Python (List, Dict, Optional, Any)
- **Pattern** : Singleton pour CartManager et Config, context manager pour Database
- **BDD** : Migrations via ALTER TABLE dans _create_tables() avec try/except silencieux
- **UI** : TTK widgets avec styles du Theme, pas de widgets tk bruts
- **Tests** : pytest dans /tests/
- **Build** : PyInstaller (spec dans .bat), InnoSetup pour installer Windows
- **Git** : Historique de versions dans installer_output/ (v1.0.0 a v1.8.3)

## Regles Importantes

1. **Ne jamais casser l'existant** : L'import/export CSV actuel doit continuer a fonctionner
2. **Migrations BDD douces** : Utiliser ALTER TABLE avec try/except pour les nouvelles colonnes
3. **Theme coherent** : Utiliser exclusivement Theme.create_*() pour les widgets UI
4. **Performance** : L'import CSV actuel traite 30 000 produits en <1s, maintenir ce niveau
5. **Portabilite** : L'app est distribuee via installer Windows, les chemins doivent etre relatifs au data_dir
6. **PDFs** : Les fiches techniques sont stockees en chemin relatif dans data/Fiches_techniques/{categorie}/
7. **Config** : Utiliser config.py get_config() pour tout acces a la configuration
8. **Version** : Incrementer src/version.py a chaque release significative
