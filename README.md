# DestriChiffrage

Application de gestion de catalogue et de chiffrage de portes.

## Fonctionnalites

- **Recherche instantanee** : Recherche par mot-cle dans les designations, dimensions, references
- **Filtrage avance** : Par categorie, sous-categorie (3 niveaux), hauteur et largeur
- **Calcul automatique des prix de vente** : Marge personnalisable (defaut 20%)
- **Gestion des produits** : Ajout, modification, suppression avec formulaires intuitifs
- **Panier d'export** 🛒 : Selection multiple d'articles pour export groupe avec PDFs
- **Import/Export CSV** : Compatible avec Excel, encodage UTF-8 avec BOM
- **Gestion des documents** : Association de fiches techniques et devis fournisseur (PDF)
- **Copier-coller** : Copie rapide des designations, prix et references
- **Base de donnees locale** : SQLite (pas de serveur requis)

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
│       └── cart_export_dialog.py  # Dialogue d'export panier
├── data/
│   ├── catalogue.db           # Base de donnees (creee automatiquement)
│   ├── Fiches_techniques/     # PDFs fiches techniques
│   └── Devis_fournisseur/     # PDFs devis
├── assets/
│   ├── icon.ico               # Icone application
│   ├── logo.png               # Logo (optionnel)
│   └── pdf.png                # Icone PDF
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
   - CATEGORIE, SOUS-CATEGORIE, DESIGNATION, DIMENSIONS, PRIX_UNITAIRE_HT, ARTICLE, CHANTIER

### Rechercher un produit
1. Taper dans le champ "Rechercher"
2. Ou selectionner une categorie dans la liste deroulante
3. Les resultats s'affichent instantanement

### Modifier la marge
1. Modifier la valeur dans le champ "Marge" en haut a droite
2. Cliquer sur "Appliquer"
3. Tous les prix de vente sont recalcules

### Utiliser le panier d'export 🛒
1. Cliquer sur l'icone "+" dans la colonne Panier pour ajouter un article
2. L'icone devient "✓" et le compteur du bouton Panier s'incremente
3. Cliquer sur le bouton "🛒 Panier (X)" pour voir les articles selectionnes
4. Dans le panneau panier :
   - Double-clic sur un article pour le retirer
   - "Vider le panier" pour tout supprimer
   - "Exporter" pour lancer l'export groupe

### Exporter le panier
1. Depuis le panneau panier, cliquer sur "Exporter"
2. Choisir le fichier CSV de destination
3. Choisir le dossier pour les PDFs (optionnel)
4. Cocher les options :
   - ☑ Inclure les fiches techniques
   - ☑ Inclure les devis fournisseur
5. Les fichiers PDF seront copies dans des sous-dossiers :
   - `Fiches_techniques/`
   - `Devis_fournisseur/`

### Exporter tout / selection
- **Exporter tout** : Exporte tous les produits du catalogue
- **Exporter selection** : Exporte uniquement les produits affiches (apres filtre/recherche)

## Creation d'un executable

```bash
pip install pyinstaller
pyinstaller --onefile --windowed --name DestriChiffrage src/main.py
```

L'executable sera dans le dossier `dist/`.

## Documentation

📚 **Documentation complete disponible dans le dossier [`docs/`](docs/)**

### Guides Disponibles

- **[Guide de Build](docs/BUILD.md)** - Compilation et creation de l'installateur
- **[Systeme de Mise a Jour](docs/AUTO_UPDATE.md)** - Auto-updater et publication de versions
- **[Implementation Panier](docs/IMPLEMENTATION_PANIER.md)** - Architecture du systeme de panier
- **[Implementation Installateur](docs/IMPLEMENTATION_EXE.md)** - Infrastructure de build .exe
- **[Rapport de Tests](docs/RAPPORT_TESTS_BUILD.md)** - Resultats des tests de build

Voir l'[index complet de la documentation](docs/README.md) pour plus de details.

## Licence

Projet prive - Tous droits reserves
