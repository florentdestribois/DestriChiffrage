# Guide de Build - DestriChiffrage

Ce document explique comment compiler DestriChiffrage en un exécutable Windows standalone et créer un installateur.

## Prérequis

### 1. Python 3.8 ou supérieur
Télécharger depuis : https://www.python.org/downloads/

### 2. Inno Setup 6
Télécharger depuis : https://jrsoftware.org/isdl.php

Installer avec les options par défaut (chemin : `C:\Program Files (x86)\Inno Setup 6\`)

### 3. Dépendances Python
```bash
pip install -r requirements.txt
```

Les dépendances principales sont :
- `pyinstaller>=5.0` - Pour créer l'exécutable
- `Pillow>=10.0` - Pour le traitement d'images
- `openpyxl>=3.0` - Pour l'export Excel
- `requests>=2.31` - Pour l'auto-updater

## Étapes de Build

### Étape 1 : Compiler l'exécutable avec PyInstaller

Exécuter le script de build :

```bash
build.bat
```

Ce script va :
1. Nettoyer les anciens builds (`dist/`, `build/`)
2. Compiler l'application avec PyInstaller selon `DestriChiffrage.spec`
3. Créer le dossier `dist/` contenant `DestriChiffrage.exe`
4. Créer les dossiers data nécessaires

**Résultat** : L'exécutable se trouve dans `dist/DestriChiffrage.exe`

#### Build manuel (optionnel)

Si vous préférez compiler manuellement :

```bash
pyinstaller DestriChiffrage.spec
```

### Étape 2 : Créer l'installateur Windows

Exécuter le script de création de l'installateur :

```bash
build_installer.bat
```

Ce script va :
1. Vérifier que `dist/DestriChiffrage.exe` existe
2. Vérifier qu'Inno Setup est installé
3. Compiler l'installateur selon `installer.iss`
4. Créer le fichier dans `installer_output/DestriChiffrage-Setup-1.0.0.exe`

**Résultat** : L'installateur se trouve dans `installer_output/DestriChiffrage-Setup-1.0.0.exe`

#### Build manuel (optionnel)

Si vous préférez compiler manuellement :

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

## Structure du Build

### Fichiers de configuration

- **`DestriChiffrage.spec`** : Configuration PyInstaller
  - Définit les fichiers à inclure
  - Configure les options de compilation
  - Spécifie l'icône de l'application

- **`installer.iss`** : Script Inno Setup
  - Définit la structure de l'installateur
  - Configure les dossiers d'installation
  - Crée les raccourcis
  - Gère la désinstallation

### Fichiers générés

```
DestriChiffrage/
├── dist/                          # Build PyInstaller
│   ├── DestriChiffrage.exe        # Exécutable principal
│   ├── data/                      # Dossier de données (vide)
│   │   ├── Fiches_techniques/
│   │   └── Devis_fournisseur/
│   └── config/                    # Configuration (créé au runtime)
│
└── installer_output/              # Build Inno Setup
    └── DestriChiffrage-Setup-1.0.0.exe  # Installateur Windows
```

## Gestion des Ressources

### Assets inclus dans l'exécutable

Les ressources suivantes sont empaquetées dans l'exécutable :

- `src/assets/logo.png` - Logo de l'application
- `src/assets/pdf.png` - Icône PDF
- `assets/icon.ico` - Icône de l'application

Ces fichiers sont accessibles via la fonction `get_resource_path()` dans `src/utils.py`.

### Données utilisateur

Les données suivantes sont créées à l'installation et restent modifiables :

- `data/` - Dossier principal des données
  - `catalogue.db` - Base de données SQLite
  - `Fiches_techniques/` - PDFs des fiches techniques
  - `Devis_fournisseur/` - PDFs des devis fournisseurs

- `config/` - Configuration utilisateur
  - `settings.ini` - Paramètres de l'application

## Mise à Jour de la Version

Pour créer une nouvelle version :

1. Modifier la version dans `src/version.py` :
   ```python
   __version__ = "1.1.0"
   ```

2. Modifier la version dans `installer.iss` :
   ```
   #define MyAppVersion "1.1.0"
   ```

3. Recompiler avec les scripts `build.bat` et `build_installer.bat`

## Dépannage

### Erreur : "Module not found"

**Cause** : Une dépendance n'est pas installée ou n'est pas détectée par PyInstaller.

**Solution** :
1. Installer la dépendance : `pip install <module>`
2. Ajouter à `hiddenimports` dans `DestriChiffrage.spec`

### Erreur : "Failed to execute script"

**Cause** : Erreur au runtime, souvent liée aux chemins de fichiers.

**Solution** :
1. Vérifier les logs dans `dist/DestriChiffrage.exe.log`
2. Tester en mode développement : `python src/main.py`
3. Vérifier que les ressources sont bien incluses dans `datas` du .spec

### Erreur : "Inno Setup not found"

**Cause** : Inno Setup n'est pas installé ou pas dans le chemin par défaut.

**Solution** :
1. Installer Inno Setup depuis https://jrsoftware.org/isdl.php
2. Ou modifier le chemin dans `build_installer.bat`

### L'exécutable est trop volumineux

**Cause** : PyInstaller inclut toutes les dépendances, y compris celles non utilisées.

**Solution** :
1. Ajouter les modules inutiles à `excludes` dans le .spec
2. Utiliser UPX pour compresser (déjà activé avec `upx=True`)

## Distribution

### Fichiers à distribuer

**Option 1 - Installateur (recommandé)** :
- Distribuer uniquement `DestriChiffrage-Setup-1.0.0.exe`
- L'utilisateur double-clique pour installer
- L'application est installée dans `C:\Program Files\DestriChiffrage\`

**Option 2 - Exécutable portable** :
- Distribuer le dossier `dist/` complet en archive ZIP
- L'utilisateur décompresse où il veut
- L'application est portable (pas d'installation)

### Taille des fichiers

- Exécutable seul : ~20-30 MB
- Installateur : ~25-35 MB
- Avec données utilisateur : Variable selon les PDFs

## Build Automatisé (CI/CD)

Pour automatiser le build avec GitHub Actions, voir la configuration dans `.github/workflows/build.yml` (à créer).

Le workflow automatique permet de :
- Compiler automatiquement à chaque release
- Publier l'installateur sur GitHub Releases
- Gérer les mises à jour automatiques

## Support

Pour toute question ou problème de build :
- Créer une issue sur GitHub : https://github.com/florentdestribois/DestriChiffrage/issues
- Vérifier les logs de compilation
- Tester en mode développement avant de compiler
