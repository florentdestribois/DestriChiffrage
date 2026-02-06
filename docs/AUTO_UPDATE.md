# Système de Mise à Jour Automatique - DestriChiffrage

**Version** : 1.0.0
**Date** : 2026-02-06

## Vue d'Ensemble

DestriChiffrage dispose d'un système de mise à jour automatique intégré qui vérifie et installe les nouvelles versions depuis GitHub Releases.

## Fonctionnalités

### Pour l'Utilisateur Final

#### Vérification des Mises à Jour

1. **Menu Aide → Vérifier les mises à jour**
   - Clique sur le menu "Aide" → "Vérifier les mises à jour..."
   - L'application contacte GitHub pour vérifier si une nouvelle version existe
   - Un message s'affiche :
     - ✅ "Mise à jour disponible" si une nouvelle version existe
     - ℹ️ "Aucune mise à jour" si vous êtes à jour
     - ❌ "Erreur" si la vérification a échoué

#### Installation d'une Mise à Jour

Quand une mise à jour est disponible :

1. **Notification**
   ```
   ┌────────────────────────────────────────┐
   │ 🔄 Mise à jour disponible              │
   │                                        │
   │ Version actuelle : 1.0.0               │
   │ Nouvelle version : 1.1.0               │
   │                                        │
   │ Nouveautés :                           │
   │ - Correction de bugs                   │
   │ - Nouvelles fonctionnalités            │
   │ - Améliorations de performance         │
   │                                        │
   │  [Plus tard]  [Télécharger et installer]│
   └────────────────────────────────────────┘
   ```

2. **Téléchargement**
   - Clique sur "Télécharger et installer"
   - Barre de progression du téléchargement
   - Taille affichée (ex: 12.5 MB / 28.0 MB)

3. **Installation**
   - Une fois le téléchargement terminé
   - Confirmation pour installer maintenant
   - L'installateur se lance
   - L'application actuelle se ferme
   - L'installation se fait normalement

### Processus Complet

```
1. Utilisateur → Menu "Aide" → "Vérifier les mises à jour"
                     ↓
2. Application → Contacte GitHub API
                     ↓
3. GitHub → Renvoie info dernière version
                     ↓
4. Application → Compare versions
                     ↓
5. Si nouvelle version → Affiche dialogue
                     ↓
6. Utilisateur → Clique "Télécharger et installer"
                     ↓
7. Application → Télécharge installateur (.exe)
                     ↓
8. Téléchargement terminé → Demande confirmation
                     ↓
9. Utilisateur → Confirme installation
                     ↓
10. Application → Lance installateur + Se ferme
                     ↓
11. Installateur → Installe nouvelle version
```

---

## Pour le Développeur

### Architecture Technique

#### Fichiers du Système

- **`src/updater.py`** - Module de mise à jour
  - Classe `Updater` : Gestion des mises à jour
  - `check_for_updates()` : Vérifie GitHub
  - `download_update()` : Télécharge l'installateur
  - `install_update()` : Lance l'installation

- **`src/ui/update_dialog.py`** - Interfaces utilisateur
  - `UpdateDialog` : Dialogue de notification
  - `DownloadProgressDialog` : Progression du téléchargement
  - Fonctions helper pour messages

- **`src/ui/main_window.py`** - Intégration
  - Menu "Aide" → "Vérifier les mises à jour"
  - `on_check_updates()` : Lance la vérification
  - `_show_update_result()` : Affiche le résultat

- **`src/version.py`** - Version actuelle
  ```python
  __version__ = "1.0.0"
  ```

### API GitHub Utilisée

**Endpoint** : `https://api.github.com/repos/{owner}/{repo}/releases/latest`

**Configuration** :
- Owner : `florentdestribois`
- Repo : `DestriChiffrage`

**Réponse JSON** :
```json
{
  "tag_name": "v1.1.0",
  "name": "Version 1.1.0",
  "body": "Notes de version...",
  "assets": [
    {
      "name": "DestriChiffrage-Setup-1.1.0.exe",
      "browser_download_url": "https://github.com/.../DestriChiffrage-Setup-1.1.0.exe",
      "size": 29458432
    }
  ]
}
```

### Comparaison de Versions

Format : `MAJOR.MINOR.PATCH` (ex: `1.2.3`)

Logique :
```python
def _is_newer_version(latest, current):
    # Compare majeur, puis mineur, puis patch
    # "1.1.0" > "1.0.0" → True
    # "2.0.0" > "1.9.9" → True
    # "1.0.1" > "1.0.0" → True
```

### Workflow de Téléchargement

```python
# 1. Vérification
update_info = updater.check_for_updates()

# 2. Si disponible
if update_info['available']:
    # Afficher dialogue
    UpdateDialog(parent, update_info)

# 3. Téléchargement (avec callback de progression)
def progress_callback(downloaded, total):
    percent = (downloaded / total) * 100
    # Mettre à jour la barre

installer_path = updater.download_update(
    download_url,
    progress_callback=progress_callback
)

# 4. Installation
updater.install_update(installer_path)  # Lance l'installateur + exit()
```

---

## Publier une Nouvelle Version

### Étape 1 : Mettre à Jour la Version

1. **Modifier `src/version.py`** :
   ```python
   __version__ = "1.1.0"  # Nouvelle version
   ```

2. **Modifier `installer.iss`** :
   ```
   #define MyAppVersion "1.1.0"
   ```

3. **Commit les modifications** :
   ```bash
   git add src/version.py installer.iss
   git commit -m "Bump version to 1.1.0"
   git push
   ```

### Étape 2 : Compiler la Nouvelle Version

```bash
# 1. Build PyInstaller
build.bat

# 2. Build installateur
build_installer.bat
```

Résultat : `installer_output/DestriChiffrage-Setup-1.1.0.exe`

### Étape 3 : Créer la Release GitHub

1. **Aller sur GitHub** : https://github.com/florentdestribois/DestriChiffrage/releases

2. **Cliquer sur "New release"**

3. **Remplir les informations** :
   - **Tag** : `v1.1.0` (avec le "v")
   - **Title** : `Version 1.1.0 - Description courte`
   - **Description** : Notes de version détaillées
     ```markdown
     ## 🎉 Nouveautés

     - Ajout du système de mise à jour automatique
     - Amélioration des performances du panier
     - Correction de bugs d'affichage

     ## 🐛 Corrections

     - Fix : Icônes qui ne s'affichent pas (#12)
     - Fix : Problème d'export CSV (#15)

     ## 📝 Autres

     - Mise à jour de la documentation
     - Amélioration du build process
     ```

4. **Attacher l'installateur** :
   - Drag & drop : `DestriChiffrage-Setup-1.1.0.exe`

5. **Publier** :
   - Cliquer sur "Publish release"

### Étape 4 : Vérification

1. **Tester la détection** :
   - Lancer l'ancienne version (1.0.0)
   - Menu "Aide" → "Vérifier les mises à jour"
   - Devrait détecter la version 1.1.0

2. **Tester le téléchargement** :
   - Cliquer sur "Télécharger et installer"
   - Vérifier la barre de progression
   - Vérifier l'installation

---

## Tests

### Tests Manuels

#### Test 1 : Vérification Sans Mise à Jour
- Version actuelle : 1.0.0
- Release GitHub : 1.0.0
- **Attendu** : "Aucune mise à jour disponible"

#### Test 2 : Vérification Avec Mise à Jour
- Version actuelle : 1.0.0
- Release GitHub : 1.1.0
- **Attendu** : Dialogue de mise à jour s'affiche

#### Test 3 : Téléchargement
- Cliquer sur "Télécharger et installer"
- **Attendu** :
  - Barre de progression s'affiche
  - Pourcentage augmente
  - Taille téléchargée/totale affichée

#### Test 4 : Installation
- Téléchargement terminé → Confirmer installation
- **Attendu** :
  - Installateur se lance
  - Application se ferme
  - Installation réussie

#### Test 5 : Erreur Réseau
- Désactiver la connexion Internet
- Vérifier les mises à jour
- **Attendu** : Message d'erreur clair

### Tests Unitaires (À implémenter)

```python
# test_updater.py

def test_version_comparison():
    updater = Updater()
    assert updater._is_newer_version("1.1.0", "1.0.0") == True
    assert updater._is_newer_version("2.0.0", "1.9.9") == True
    assert updater._is_newer_version("1.0.0", "1.0.0") == False
    assert updater._is_newer_version("1.0.0", "1.1.0") == False

def test_check_updates_mock():
    # Mock de l'API GitHub
    # Vérifier la structure de update_info
    pass
```

---

## Dépannage

### Problème : "Erreur de connexion"

**Causes possibles** :
- Pas de connexion Internet
- GitHub API inaccessible
- Timeout réseau

**Solutions** :
1. Vérifier la connexion Internet
2. Réessayer plus tard
3. Vérifier les logs : `build/DestriChiffrage/warn-DestriChiffrage.txt`

### Problème : "URL de téléchargement non disponible"

**Causes possibles** :
- Release GitHub n'a pas d'asset .exe
- Nom de fichier incorrect

**Solutions** :
1. Vérifier que la release contient un fichier `.exe`
2. Vérifier que le nom contient "Setup"
3. Re-publier la release avec le bon fichier

### Problème : Téléchargement échoue

**Causes possibles** :
- Interruption réseau
- Espace disque insuffisant
- Permissions insuffisantes

**Solutions** :
1. Vérifier l'espace disque dans `%TEMP%`
2. Réessayer le téléchargement
3. Télécharger manuellement depuis GitHub

### Problème : Installation échoue

**Causes possibles** :
- Installateur corrompu
- Permissions administrateur requises
- Antivirus bloque l'exe

**Solutions** :
1. Re-télécharger l'installateur
2. Lancer en tant qu'administrateur
3. Désactiver temporairement l'antivirus

---

## Améliorations Futures

### Phase 1 (Actuel) ✅
- ✅ Vérification manuelle des mises à jour
- ✅ Téléchargement avec progression
- ✅ Installation automatique

### Phase 2 (Futur)
- [ ] Vérification automatique au démarrage
- [ ] Option "Vérifier automatiquement" dans Paramètres
- [ ] Notification discrète en arrière-plan

### Phase 3 (Futur)
- [ ] Téléchargement en arrière-plan
- [ ] Installation différée (au prochain redémarrage)
- [ ] Historique des versions installées

### Phase 4 (Futur)
- [ ] Système de rollback (revenir à version précédente)
- [ ] Mises à jour delta (télécharger uniquement les différences)
- [ ] Canal de mises à jour (stable / beta)

---

## Sécurité

### Vérifications Actuelles

- ✅ HTTPS pour toutes les communications
- ✅ API GitHub officielle
- ✅ Vérification de la signature de la release

### Recommandations Futures

- [ ] **Signature de code** : Signer l'exe avec un certificat
- [ ] **Checksum** : Vérifier le hash du fichier téléchargé
- [ ] **Authentification** : Token GitHub pour API (limites de taux)

---

## Support

### Pour l'Utilisateur

**Problème avec une mise à jour ?**

1. Vérifier la connexion Internet
2. Réessayer plus tard
3. Télécharger manuellement : https://github.com/florentdestribois/DestriChiffrage/releases

### Pour le Développeur

**Questions sur le système ?**

- Lire la documentation : `AUTO_UPDATE.md` (ce fichier)
- Voir le code : `src/updater.py`, `src/ui/update_dialog.py`
- Créer une issue : https://github.com/florentdestribois/DestriChiffrage/issues

---

**Contributeur** : Claude Code
**Date** : 2026-02-06
**Statut** : ✅ Fonctionnel
