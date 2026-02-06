# Documentation DestriChiffrage

Documentation complète du projet DestriChiffrage.

## 📖 Table des Matières

### 🚀 Guides Utilisateur

- **[README.md](../README.md)** - Guide utilisateur principal (à la racine)

### 🔨 Guides Développeur

#### Build et Compilation

- **[BUILD.md](BUILD.md)** - Guide de build complet
  - Prérequis (Python, Inno Setup)
  - Compilation PyInstaller
  - Création de l'installateur
  - Dépannage

#### Système de Mise à Jour

- **[AUTO_UPDATE.md](AUTO_UPDATE.md)** - Système d'auto-update
  - Guide utilisateur
  - Architecture technique
  - Publication de releases
  - Dépannage

### 📋 Rapports d'Implémentation

#### Fonctionnalité Panier

- **[IMPLEMENTATION_PANIER.md](IMPLEMENTATION_PANIER.md)** - Implémentation du panier
  - Architecture
  - Fichiers créés
  - Intégration

- **[RAPPORT_IMPLEMENTATION_PANIER.md](RAPPORT_IMPLEMENTATION_PANIER.md)** - Rapport détaillé
  - Session de travail
  - Bugs corrigés
  - Tests effectués

#### Installateur .exe

- **[IMPLEMENTATION_EXE.md](IMPLEMENTATION_EXE.md)** - Implémentation installateur
  - Infrastructure de build
  - Phases d'implémentation
  - Fichiers modifiés
  - Statistiques

- **[RAPPORT_TESTS_BUILD.md](RAPPORT_TESTS_BUILD.md)** - Tests de build
  - Tests effectués
  - Résultats
  - Problèmes rencontrés

#### Auto-Updater

- **[IMPLEMENTATION_AUTO_UPDATE.md](IMPLEMENTATION_AUTO_UPDATE.md)** - Implémentation auto-update
  - Architecture technique
  - Workflow complet
  - Tests
  - Utilisation

## 📁 Organisation des Documents

```
docs/
├── README.md                          # Ce fichier (index)
│
├── Guides de Build
│   ├── BUILD.md                       # Guide de compilation
│   └── AUTO_UPDATE.md                 # Guide auto-update
│
├── Rapports - Panier
│   ├── IMPLEMENTATION_PANIER.md       # Implémentation
│   └── RAPPORT_IMPLEMENTATION_PANIER.md  # Rapport détaillé
│
├── Rapports - Installateur
│   ├── IMPLEMENTATION_EXE.md          # Implémentation
│   └── RAPPORT_TESTS_BUILD.md         # Tests de build
│
└── Rapports - Auto-Update
    └── IMPLEMENTATION_AUTO_UPDATE.md  # Implémentation complète
```

## 🎯 Liens Rapides

### Je veux...

- **Compiler l'application** → [BUILD.md](BUILD.md)
- **Publier une nouvelle version** → [AUTO_UPDATE.md](AUTO_UPDATE.md) (section "Publier")
- **Comprendre le système de panier** → [IMPLEMENTATION_PANIER.md](IMPLEMENTATION_PANIER.md)
- **Voir les résultats des tests** → [RAPPORT_TESTS_BUILD.md](RAPPORT_TESTS_BUILD.md)
- **Comprendre l'auto-updater** → [IMPLEMENTATION_AUTO_UPDATE.md](IMPLEMENTATION_AUTO_UPDATE.md)

## 📊 Vue d'Ensemble du Projet

### Fonctionnalités Principales

1. **Catalogue de Produits**
   - Gestion complète (CRUD)
   - Import/Export CSV
   - Catégories et sous-catégories

2. **Système de Panier** 🛒
   - Ajout d'articles
   - Visualisation
   - Export CSV avec PDFs

3. **Build et Distribution** 📦
   - Exécutable Windows standalone
   - Installateur professionnel (Inno Setup)
   - Pas de dépendances Python requises

4. **Mises à Jour Automatiques** 🔄
   - Vérification depuis GitHub Releases
   - Téléchargement automatique
   - Installation en un clic

### Technologies Utilisées

- **Backend** : Python 3.8+, SQLite
- **UI** : Tkinter, PIL/Pillow
- **Build** : PyInstaller 6.18+
- **Installateur** : Inno Setup 6
- **Updates** : GitHub API, requests

### Structure du Projet

```
DestriChiffrage/
├── src/                      # Code source
│   ├── main.py              # Point d'entrée
│   ├── database.py          # Gestion BDD
│   ├── config.py            # Configuration
│   ├── updater.py           # Auto-updater
│   ├── cart_manager.py      # Gestionnaire panier
│   ├── utils.py             # Utilitaires
│   ├── version.py           # Version
│   └── ui/                  # Interfaces
│       ├── main_window.py
│       ├── dialogs.py
│       ├── cart_panel.py
│       ├── cart_export_dialog.py
│       ├── update_dialog.py
│       └── theme.py
│
├── data/                     # Données utilisateur
│   ├── catalogue.db
│   ├── Fiches_techniques/
│   └── Devis_fournisseur/
│
├── assets/                   # Ressources
│   └── icon.ico
│
├── docs/                     # Documentation (ce dossier)
│
├── build.bat                 # Script build PyInstaller
├── build_installer.bat       # Script build Inno Setup
├── DestriChiffrage.spec      # Config PyInstaller
├── installer.iss             # Config Inno Setup
└── README.md                 # Guide utilisateur principal
```

## 📚 Ordre de Lecture Recommandé

### Pour Nouveau Développeur

1. **[../README.md](../README.md)** - Comprendre l'application
2. **[IMPLEMENTATION_PANIER.md](IMPLEMENTATION_PANIER.md)** - Architecture du panier
3. **[IMPLEMENTATION_EXE.md](IMPLEMENTATION_EXE.md)** - Infrastructure de build
4. **[BUILD.md](BUILD.md)** - Guide pratique de compilation

### Pour Maintenance

1. **[BUILD.md](BUILD.md)** - Compiler et tester
2. **[AUTO_UPDATE.md](AUTO_UPDATE.md)** - Publier des mises à jour
3. **[RAPPORT_TESTS_BUILD.md](RAPPORT_TESTS_BUILD.md)** - Référence des tests

### Pour Comprendre l'Historique

1. **[RAPPORT_IMPLEMENTATION_PANIER.md](RAPPORT_IMPLEMENTATION_PANIER.md)** - Session panier
2. **[IMPLEMENTATION_EXE.md](IMPLEMENTATION_EXE.md)** - Session build
3. **[IMPLEMENTATION_AUTO_UPDATE.md](IMPLEMENTATION_AUTO_UPDATE.md)** - Session auto-update

## 🔧 Commandes Rapides

### Build

```bash
# Compiler l'exécutable
build.bat

# Créer l'installateur (nécessite Inno Setup)
build_installer.bat

# Build complet
build.bat && build_installer.bat
```

### Tests

```bash
# Lancer l'application en mode dev
python src/main.py

# Tester l'exécutable
dist\DestriChiffrage.exe

# Vérifier les imports
python -c "from src.updater import Updater; print('OK')"
```

### Commandes Claude

```
/build                 # Build PyInstaller
/build-installer       # Build installateur
/build-all            # Build complet
```

## 📈 Statistiques Projet

**Code Source** :
- Python : ~3500 lignes
- Scripts : ~200 lignes

**Documentation** :
- Total : ~3000 lignes
- Fichiers : 8 documents

**Fonctionnalités** :
- Catalogue produits : ✅
- Système panier : ✅
- Build .exe : ✅
- Auto-updater : ✅
- CI/CD : 🔶 (à faire)

## 🤝 Contribution

Pour contribuer au projet :

1. Lire la documentation pertinente
2. Suivre les conventions de code existantes
3. Tester avec `build.bat` avant de commit
4. Mettre à jour la documentation si nécessaire

## 📞 Support

- **Issues** : https://github.com/florentdestribois/DestriChiffrage/issues
- **Releases** : https://github.com/florentdestribois/DestriChiffrage/releases
- **Documentation** : Ce dossier `docs/`

---

**Dernière mise à jour** : 2026-02-06
**Version** : 1.0.0
