# Guide de Création de la Release v1.0.0

**Date** : 2026-02-06
**Version** : 1.0.0
**Statut** : Build PyInstaller ✅ | Installateur 🔶

## ✅ Build PyInstaller Terminé

L'exécutable a été créé avec succès :
- **Fichier** : `dist/DestriChiffrage.exe`
- **Taille** : 26 MB
- **Version** : 1.0.0
- **Dossiers data** : Créés ✅

---

## 🔶 Étapes Suivantes

### Option A : Créer Release avec Exe Seul (Rapide - 2 minutes)

Tu peux créer une release GitHub maintenant avec **juste l'exe portable**.

**Avantages** :
- ✅ Rapide
- ✅ Permet de tester l'auto-updater
- ✅ Distribution possible

**Inconvénients** :
- ❌ Pas d'installateur professionnel
- ❌ Utilisateur doit gérer les dossiers manuellement

**Comment faire** :

1. **Créer un ZIP** :
   ```bash
   cd "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
   # Créer DestriChiffrage-v1.0.0-portable.zip contenant:
   # - DestriChiffrage.exe
   # - data/
   ```

2. **Créer la release GitHub** :
   - Aller sur : https://github.com/florentdestribois/DestriChiffrage/releases/new
   - Tag : `v1.0.0`
   - Title : `Version 1.0.0 - Première release`
   - Body : Notes de version (voir ci-dessous)
   - Attacher : `DestriChiffrage-v1.0.0-portable.zip`

---

### Option B : Installer Inno Setup et Créer Installateur (Complet - 10 minutes)

Pour une release professionnelle avec installateur Windows.

#### Étape 1 : Installer Inno Setup

1. **Télécharger Inno Setup 6** :
   - URL : https://jrsoftware.org/isdl.php
   - Fichier : `innosetup-6.x.x.exe`

2. **Installer** :
   - Double-cliquer sur l'installateur
   - Suivre l'assistant (options par défaut)
   - Installation dans : `C:\Program Files (x86)\Inno Setup 6\`

#### Étape 2 : Compiler l'Installateur

```bash
cd "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
build_installer.bat
```

Ou manuellement :
```bash
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer.iss
```

**Résultat** : `installer_output/DestriChiffrage-Setup-1.0.0.exe`

#### Étape 3 : Créer la Release GitHub

- Aller sur : https://github.com/florentdestribois/DestriChiffrage/releases/new
- Tag : `v1.0.0`
- Title : `Version 1.0.0 - Première release`
- Body : Notes de version (voir ci-dessous)
- Attacher : **`DestriChiffrage-Setup-1.0.0.exe`**

---

## 📝 Notes de Version Suggérées

Copie/colle ceci dans la description de la release GitHub :

```markdown
# Version 1.0.0 - Première Release Officielle

## 🎉 Fonctionnalités Principales

### Gestion de Catalogue
- ✅ Gestion complète des produits (CRUD)
- ✅ Import/Export CSV
- ✅ Recherche et filtrage avancés
- ✅ Support de 3 niveaux de sous-catégories

### Système de Panier 🛒
- ✅ Ajout d'articles au panier depuis l'interface
- ✅ Visualisation et gestion du panier
- ✅ Export CSV multi-articles
- ✅ Copie optionnelle des PDFs (fiches techniques + devis)

### Gestion des Documents
- ✅ Association de fiches techniques (PDF)
- ✅ Association de devis fournisseurs (PDF)
- ✅ Ouverture directe des documents depuis l'interface

### Mise à Jour Automatique 🔄
- ✅ Vérification des mises à jour depuis GitHub
- ✅ Téléchargement automatique
- ✅ Installation en un clic

## 💻 Installation

### Option 1 : Installateur Windows (Recommandé)
1. Télécharger `DestriChiffrage-Setup-1.0.0.exe`
2. Double-cliquer pour lancer l'installation
3. Suivre l'assistant d'installation
4. L'application est prête !

### Option 2 : Exécutable Portable
1. Télécharger `DestriChiffrage-v1.0.0-portable.zip`
2. Extraire dans un dossier
3. Lancer `DestriChiffrage.exe`

## 📋 Prérequis

**Aucun !** 🎉

L'application est standalone et n'a pas besoin de Python ou d'autres dépendances installées.

## 🐛 Bugs Corrigés

- Fix : Icônes du panier qui ne s'affichent pas sans redimensionner
- Fix : Boutons invisibles dans les dialogues de panier
- Fix : KeyError Theme.COLORS['error']

## 📚 Documentation

La documentation complète est disponible dans le dossier `docs/` :
- [Guide de Build](docs/BUILD.md)
- [Système d'Auto-Update](docs/AUTO_UPDATE.md)
- [Architecture du Panier](docs/IMPLEMENTATION_PANIER.md)

## 🆕 Nouveautés Futures

- [ ] CI/CD avec GitHub Actions
- [ ] Vérification automatique des mises à jour au démarrage
- [ ] Export Excel avancé
- [ ] Thèmes personnalisables

## 💬 Support

- **Issues** : https://github.com/florentdestribois/DestriChiffrage/issues
- **Documentation** : Dossier `docs/` du projet

---

**Taille** : ~26 MB (exe) | ~30 MB (installateur)
**Plateforme** : Windows 10/11 64-bit
**Licence** : Privé - Tous droits réservés

Développé avec ❤️ par Destribois
```

---

## 🧪 Test de l'Auto-Updater

Une fois la release créée, tu pourras tester le système complet :

### Test 1 : Avec Version 0.9.0

1. **Modifier la version** :
   ```python
   # src/version.py
   __version__ = "0.9.0"
   ```

2. **Lancer l'application** :
   ```bash
   python src/main.py
   ```

3. **Menu "Aide" → "Vérifier les mises à jour"**
   - Devrait détecter la version 1.0.0 ✅
   - Proposer de télécharger
   - Afficher les notes de version

### Test 2 : Téléchargement Complet

1. Cliquer "Télécharger et installer"
2. Observer la progression
3. Confirmer l'installation
4. Vérifier que la nouvelle version est installée

---

## 📊 Résumé Build

| Étape | Statut | Fichier |
|-------|--------|---------|
| Nettoyage | ✅ | - |
| Build PyInstaller | ✅ | `dist/DestriChiffrage.exe` |
| Dossiers data | ✅ | `dist/data/` |
| **Installateur Inno Setup** | **🔶** | **Inno Setup non installé** |
| Release GitHub | 🔶 | À créer |

---

## 🎯 Recommandation

**Pour une release professionnelle** :

1. ✅ Installer Inno Setup (5 minutes)
2. ✅ Compiler l'installateur (30 secondes)
3. ✅ Créer release GitHub avec l'installateur
4. ✅ Tester l'auto-updater

**Pour tester rapidement** :

1. ✅ Créer release GitHub avec l'exe portable
2. ✅ Tester l'auto-updater
3. 🔶 Ajouter l'installateur plus tard

---

## 📞 Aide

Tu veux que je :
- **A)** T'aide à créer une release avec l'exe portable ?
- **B)** Te guide pour installer Inno Setup et compiler l'installateur ?
- **C)** Crée un script d'aide pour la release GitHub ?

---

**Créé par** : Claude Code
**Date** : 2026-02-06
**Status** : Build PyInstaller ✅ | Prêt pour release
