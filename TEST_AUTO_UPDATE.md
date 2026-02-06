# Test de l'Auto-Updater - Guide Pratique

**Date** : 2026-02-06
**Version de test** : 0.9.0 (simulée)

## ✅ Étape 1 Réalisée

La version a été temporairement modifiée à **0.9.0** pour simuler une ancienne version.

L'application est lancée et prête pour les tests.

---

## 🧪 Tests à Effectuer Maintenant

### Test 1 : Vérifier les Mises à Jour (Sans Release GitHub)

**Ce qui va se passer** :
- Si aucune release n'existe sur GitHub → Message d'erreur ou "Aucune mise à jour"
- C'est **normal** si tu n'as pas encore publié de release

**Étapes** :
1. ✅ L'application est lancée (version 0.9.0)
2. 📋 Clique sur le menu **"Aide"**
3. 📋 Clique sur **"Vérifier les mises à jour..."**
4. 📋 Observer le résultat

**Résultats possibles** :

#### Cas A : Aucune release GitHub
```
❌ Erreur de vérification
"Erreur API GitHub: 404"
```
➜ **Normal** : Pas encore de release publiée

#### Cas B : Release existe mais version égale/inférieure
```
ℹ️ Aucune mise à jour
"Vous utilisez déjà la dernière version"
```
➜ **Normal** si release = 0.9.0 ou moins

#### Cas C : Release existe avec version supérieure (1.0.0+)
```
🔄 Mise à jour disponible !

Version actuelle : 0.9.0
Nouvelle version : 1.0.0 (ou supérieure)

Nouveautés :
- [Notes de la release GitHub]

[Plus tard]  [Télécharger et installer]
```
➜ **Succès** ! L'auto-updater fonctionne ✅

---

### Test 2 : Créer une Release GitHub pour Tester

Pour tester le workflow complet, tu dois créer une release GitHub.

#### Option A : Release de Test Minimale

1. **Aller sur GitHub** :
   ```
   https://github.com/florentdestribois/DestriChiffrage/releases/new
   ```

2. **Remplir les champs** :
   - **Tag** : `v1.0.0-test`
   - **Title** : `Version 1.0.0 - Test Auto-Updater`
   - **Description** :
     ```markdown
     ## 🧪 Release de Test

     Cette release sert à tester le système de mise à jour automatique.

     ### Nouveautés simulées
     - ✅ Système d'auto-update fonctionnel
     - ✅ Build PyInstaller
     - ✅ Interface de téléchargement
     ```

3. **Attacher un fichier** :
   - **Option 1** : Utiliser le vrai installateur
     ```
     dist/DestriChiffrage.exe
     ou
     installer_output/DestriChiffrage-Setup-1.0.0.exe
     ```
   - **Option 2** : Créer un fichier factice pour le test
     ```bash
     # Créer un fichier de test
     echo "Test installer" > DestriChiffrage-Setup-1.0.0-test.exe
     ```

4. **Publier** : Cliquer sur "Publish release"

5. **Retester** :
   - Retourner dans l'application (version 0.9.0)
   - Menu "Aide" → "Vérifier les mises à jour"
   - Devrait maintenant détecter la version 1.0.0-test ✅

#### Option B : Release Réelle Complète

Si tu veux créer une vraie release :

```bash
# 1. Remettre la vraie version
# src/version.py : __version__ = "1.0.0"

# 2. Compiler
build.bat
build_installer.bat

# 3. Créer release GitHub v1.0.0
# Attacher : installer_output/DestriChiffrage-Setup-1.0.0.exe

# 4. Retester depuis version 0.9.0
```

---

### Test 3 : Tester le Téléchargement

**Si une release existe avec version > 0.9.0 :**

1. ✅ Dialogue "Mise à jour disponible" affiché
2. 📋 Cliquer sur **"Télécharger et installer"**
3. 📋 Observer la progression :
   - Dialogue "Téléchargement en cours" s'affiche
   - Barre de progression augmente (0% → 100%)
   - Taille téléchargée affichée (ex: 12.5 MB / 28.0 MB)
4. 📋 Quand terminé :
   - Message "Téléchargement terminé"
   - Question "Voulez-vous installer maintenant ?"

**⚠️ Attention** : Si tu cliques "Oui", l'application va :
- Se fermer
- Lancer l'installateur
- Remplacer la version actuelle

**Pour tester sans installer** : Clique "Non" ou ferme le dialogue

---

### Test 4 : Tester les Erreurs

#### Test Erreur Réseau
1. 📋 Désactiver Wi-Fi/Ethernet
2. 📋 Menu "Aide" → "Vérifier les mises à jour"
3. 📋 **Attendu** : Message d'erreur clair
   ```
   ❌ Erreur de vérification
   "Erreur de connexion: ..."
   ```

#### Test Release Sans Fichier
1. Créer une release GitHub sans attacher de fichier .exe
2. Vérifier les mises à jour
3. **Attendu** : Mise à jour détectée mais téléchargement échoue

---

## 📊 Résultats Attendus

### Comportements Normaux ✅

| Situation | Résultat Attendu |
|-----------|------------------|
| Pas de release GitHub | ❌ Erreur API 404 |
| Release = 0.9.0 | ℹ️ Aucune mise à jour |
| Release > 0.9.0 | 🔄 Mise à jour disponible |
| Pas d'Internet | ❌ Erreur de connexion |
| Release sans .exe | ❌ URL de téléchargement non disponible |

### Workflow Complet ✅

```
1. Vérifier → Détecte nouvelle version
2. Cliquer "Télécharger" → Barre de progression
3. Téléchargement terminé → Confirmation
4. Cliquer "Oui" → Installation lance + App se ferme
5. Installation normale → Nouvelle version installée
```

---

## 🔄 Remettre la Version Normale

**Après les tests, remettre la vraie version :**

```python
# src/version.py
__version__ = "1.0.0"  # Enlever le commentaire de test
```

Ou simplement :

```bash
git checkout src/version.py
```

---

## 🐛 Problèmes Possibles

### Problème : "Erreur API GitHub: 404"

**Cause** : Pas de release publiée sur GitHub

**Solution** : Créer une release de test (voir Test 2 ci-dessus)

### Problème : "Aucune mise à jour"

**Causes** :
- Release GitHub = 0.9.0 ou moins
- Version locale mal lue

**Solution** : Vérifier la version de la release GitHub

### Problème : "URL de téléchargement non disponible"

**Cause** : La release n'a pas de fichier .exe attaché ou mal nommé

**Solution** :
- Vérifier que le fichier s'appelle `DestriChiffrage-Setup-X.X.X.exe`
- Vérifier que "Setup" est dans le nom

### Problème : Application ne démarre pas

**Cause** : Erreur dans le code de l'updater

**Solution** :
```bash
# Lancer en mode debug
python src/main.py

# Regarder les erreurs dans la console
```

---

## 📝 Notes de Test

### Test 1 : Vérification

Date : ___________
Résultat : ⬜ Succès  ⬜ Erreur
Notes : _______________________________________

### Test 2 : Téléchargement

Date : ___________
Résultat : ⬜ Succès  ⬜ Erreur
Notes : _______________________________________

### Test 3 : Installation

Date : ___________
Résultat : ⬜ Succès  ⬜ Erreur
Notes : _______________________________________

---

## 🎯 Résumé

**État actuel** :
- ✅ Version modifiée à 0.9.0
- ✅ Application lancée
- 📋 Prêt pour les tests

**Prochaines étapes** :
1. Tester la vérification (menu Aide)
2. Créer une release GitHub si nécessaire
3. Tester le téléchargement complet
4. Remettre la version à 1.0.0

**Durée estimée des tests** : 10-15 minutes

---

**Créé par** : Claude Code
**Date** : 2026-02-06
**Statut** : 🧪 En cours de test
