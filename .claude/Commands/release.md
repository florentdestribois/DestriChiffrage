# Release DestriChiffrage

Automatise la création complète d'une release : compilation, installateur et publication GitHub.

## Arguments

- `version` (optionnel) : Numéro de version (ex: "1.0.2"). Si non spécifié, incrémente automatiquement la version patch.
- `--notes` (optionnel) : Notes de version personnalisées

## Instructions

Tu vas créer une release complète de DestriChiffrage en suivant ces étapes :

### 1. Déterminer la version

Si une version est fournie en argument, utilise-la. Sinon :
1. Lire la version actuelle dans `src/version.py`
2. Incrémenter la version patch (ex: 1.0.1 → 1.0.2)
3. Afficher la nouvelle version à l'utilisateur

### 2. Mettre à jour le numéro de version

1. Mettre à jour `src/version.py` avec la nouvelle version
2. Mettre à jour `installer_simple.iss` :
   - `AppVersion=X.Y.Z`
   - `OutputBaseFilename=DestriChiffrage-Setup-X.Y.Z`

**Note** : La boîte de dialogue "À propos" (`AboutDialog` dans `src/ui/dialogs.py`) importe automatiquement `__version__` depuis `src/version.py`, donc pas besoin de la modifier manuellement.

### 3. Compiler l'application

```bash
cd "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
python -m PyInstaller DestriChiffrage.spec --clean --noconfirm
```

Vérifier que `dist/DestriChiffrage.exe` a été créé.

### 4. Créer l'installateur

```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_simple.iss
```

Vérifier que `installer_output/DestriChiffrage-Setup-X.Y.Z.exe` a été créé.

### 5. Créer la release GitHub

Si des notes personnalisées sont fournies, les utiliser. Sinon, utiliser les notes par défaut :

```markdown
# Version X.Y.Z

## 📦 Installation

1. Télécharger DestriChiffrage-Setup-X.Y.Z.exe
2. Double-cliquer (accepter les droits administrateur)
3. Suivre l'assistant d'installation
4. L'application est installée !

## 🔄 Mise à Jour

L'auto-updater détectera automatiquement cette version depuis l'application.

---

**Taille**: ~27 MB
**Plateforme**: Windows 10/11 64-bit
**Droits admin**: Requis pour l'installation
```

Créer la release :
```bash
gh release create vX.Y.Z --title "Version X.Y.Z" --notes "[notes]"
```

### 6. Uploader l'installateur

```bash
gh release upload vX.Y.Z "installer_output/DestriChiffrage-Setup-X.Y.Z.exe" --clobber
```

### 7. Vérification finale

1. Vérifier que la release est visible : `gh release view vX.Y.Z`
2. Afficher l'URL de la release : `https://github.com/florentdestribois/DestriChiffrage/releases/tag/vX.Y.Z`
3. Confirmer que l'asset est attaché

### 8. Résumé

Afficher un résumé avec :
- ✅ Version publiée : X.Y.Z
- ✅ Fichier exe : [taille] MB
- ✅ Installateur : [taille] MB
- ✅ URL release : [url]
- ✅ L'auto-updater peut maintenant détecter cette version

## Important

- Toujours compiler AVANT de créer l'installateur
- Vérifier que chaque étape réussit avant de passer à la suivante
- En cas d'erreur, s'arrêter et informer l'utilisateur
- Ne pas créer la release GitHub si la compilation ou l'installateur échoue
