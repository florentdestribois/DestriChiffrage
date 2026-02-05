# DestriChiffrage

Application de gestion de catalogue et de chiffrage de portes.

## Fonctionnalites

- **Recherche instantanee** : Recherche par mot-cle dans les designations, dimensions, references
- **Filtrage par categorie** : COUPE-FEU, ACOUSTIQUE, VITREE, STANDARD, MATERNELLE, ACCESSOIRE
- **Calcul automatique des prix de vente** : Marge personnalisable (defaut 20%)
- **Gestion des produits** : Ajout, modification, suppression
- **Import/Export CSV** : Compatible avec Excel
- **Base de donnees locale** : SQLite (pas de serveur requis)

## Structure du projet

```
DestriChiffrage/
├── src/
│   ├── main.py              # Point d'entree
│   ├── database.py          # Gestion base de donnees
│   └── ui/
│       ├── __init__.py
│       ├── theme.py         # Styles et couleurs
│       ├── main_window.py   # Fenetre principale
│       └── dialogs.py       # Boites de dialogue
├── data/
│   └── catalogue.db         # Base de donnees (creee automatiquement)
├── assets/
│   └── icon.ico             # Icone (optionnel)
├── tests/
├── requirements.txt
├── README.md
└── run.bat                  # Lanceur Windows
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
   - CATEGORIE, SOUS-CATEGORIE, DESIGNATION, DIMENSIONS, PRIX_UNITAIRE_HT, ARTICLE, CHANTIER

### Rechercher un produit
1. Taper dans le champ "Rechercher"
2. Ou selectionner une categorie dans la liste deroulante
3. Les resultats s'affichent instantanement

### Modifier la marge
1. Modifier la valeur dans le champ "Marge" en haut a droite
2. Cliquer sur "Appliquer"
3. Tous les prix de vente sont recalcules

### Exporter
- **Exporter tout** : Exporte tous les produits
- **Exporter selection** : Exporte uniquement les produits affiches (apres filtre/recherche)

## Creation d'un executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DestriChiffrage src/main.py
```

L'executable sera dans le dossier `dist/`.

## Licence

Projet prive - Tous droits reserves
