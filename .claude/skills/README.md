# Skills Claude pour DestriChiffrage

Ce dossier contient des commandes personnalisées (skills) pour automatiser les tâches courantes.

## Skills Disponibles

### `/release` - Créer une Release Complète

Automatise tout le processus de création d'une release :
- Compilation avec PyInstaller
- Création de l'installateur Inno Setup
- Publication sur GitHub Releases
- Upload de l'installateur

**Usage** :
```
/release
```
Incrémente automatiquement la version patch (ex: 1.0.1 → 1.0.2)

```
/release 1.1.0
```
Utilise la version spécifiée

```
/release 1.0.3 --notes "Correction bugs critiques"
```
Utilise des notes de version personnalisées

**Prérequis** :
- PyInstaller installé (`pip install pyinstaller`)
- Inno Setup installé dans `C:\Program Files (x86)\Inno Setup 6\`
- GitHub CLI configuré (`gh auth login`)

**Fichiers modifiés** :
- `src/version.py` - Version de l'application
- `installer_simple.iss` - Version de l'installateur

**Résultat** :
- `dist/DestriChiffrage.exe` - Application compilée
- `installer_output/DestriChiffrage-Setup-X.Y.Z.exe` - Installateur
- Release GitHub créée et publiée avec l'installateur attaché

---

## Créer un Nouveau Skill

Pour ajouter un nouveau skill :

1. Créer un fichier `.md` dans ce dossier
2. Utiliser le format :
   ```markdown
   # Nom du Skill

   Description courte du skill

   ## Arguments

   - `arg1` : Description

   ## Instructions

   Instructions détaillées pour Claude...
   ```

3. Le skill sera automatiquement disponible via `/nom-du-fichier`

---

**Note** : Les skills sont des instructions pour Claude Code, pas des scripts shell. Claude exécute les instructions étape par étape.
