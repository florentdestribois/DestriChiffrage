# Fix Auto-Updater pour Repository Privé

**Date** : 2026-02-06
**Statut** : ⚠️ Action Requise
**Problème** : L'auto-updater ne peut pas détecter les releases car le repository est privé

---

## 🔍 Diagnostic

### Symptôme
L'application ne détecte pas la mise à jour v1.0.0 disponible sur GitHub.

### Cause Racine
Le repository `florentdestribois/DestriChiffrage` est **privé** (`isPrivate: true`).

L'API GitHub retourne **404 Not Found** pour les releases de repositories privés lorsqu'on fait des requêtes sans authentification :

```
GET https://api.github.com/repos/florentdestribois/DestriChiffrage/releases/latest
Status: 404 Not Found
```

### Vérification
```bash
gh repo view florentdestribois/DestriChiffrage --json isPrivate
# Résultat: {"isPrivate": true}

gh release list
# Résultat: La release v1.0.0 existe bien
```

---

## ✅ Solutions Disponibles

### Option A : Rendre le Repository Public (RECOMMANDÉ)

**✨ Avantages** :
- ✅ Solution la plus simple (30 secondes)
- ✅ Aucune modification de code nécessaire
- ✅ L'auto-updater fonctionne immédiatement
- ✅ Pas besoin de gérer des tokens
- ✅ Les utilisateurs peuvent voir le code source
- ✅ Facilite les contributions futures

**❌ Inconvénients** :
- Le code source devient visible publiquement

**📝 Comment faire** :

#### Via GitHub Web
1. Aller sur : https://github.com/florentdestribois/DestriChiffrage/settings
2. Scroller tout en bas jusqu'à **"Danger Zone"**
3. Cliquer sur **"Change repository visibility"**
4. Sélectionner **"Make public"**
5. Confirmer en tapant le nom du repository

#### Via GitHub CLI
```bash
gh repo edit florentdestribois/DestriChiffrage --visibility public
```

**⏱️ Temps estimé** : 30 secondes

---

### Option B : Implémenter l'Authentification GitHub Token

**✨ Avantages** :
- ✅ Garde le repository privé
- ✅ Contrôle total sur l'accès

**❌ Inconvénients** :
- Nécessite un Personal Access Token
- Code plus complexe
- Configuration supplémentaire pour l'utilisateur
- Token doit être stocké en sécurité

**📝 Comment faire** :

#### Étape 1 : Créer un Personal Access Token

1. Aller sur : https://github.com/settings/tokens
2. Cliquer **"Generate new token"** → **"Generate new token (classic)"**
3. **Note** : `DestriChiffrage Auto-Updater`
4. **Expiration** : Choisir une durée (ex: 90 days ou No expiration)
5. **Scopes** : Cocher uniquement `public_repo` (ou `repo` si vraiment privé)
6. Cliquer **"Generate token"**
7. **COPIER LE TOKEN** (il ne sera plus visible après)

Exemple de token : `ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx`

#### Étape 2 : Modifier le Code

**Fichier** : `src/updater.py`

Ajouter le support pour un token optionnel :

```python
class Updater:
    def __init__(self, github_token: Optional[str] = None):
        """
        Initialise l'updater

        Args:
            github_token: Token GitHub pour accéder aux repos privés (optionnel)
        """
        self.GITHUB_OWNER = "florentdestribois"
        self.GITHUB_REPO = "DestriChiffrage"
        self.GITHUB_API_URL = f"https://api.github.com/repos/{self.GITHUB_OWNER}/{self.GITHUB_REPO}/releases/latest"
        self.github_token = github_token

    def check_for_updates(self) -> Dict[str, Any]:
        """Vérifie si une mise à jour est disponible"""
        try:
            # Préparer les headers
            headers = {'Accept': 'application/vnd.github.v3+json'}

            # Ajouter l'authentification si token disponible
            if self.github_token:
                headers['Authorization'] = f'token {self.github_token}'

            response = requests.get(
                self.GITHUB_API_URL,
                timeout=10,
                headers=headers
            )

            # ... reste du code inchangé
```

#### Étape 3 : Stocker le Token

**Option 3A : Variable d'Environnement** (Recommandé)

Créer un fichier `config.env` (à ne PAS commit sur Git) :
```env
GITHUB_TOKEN=ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Ajouter dans `.gitignore` :
```
config.env
```

Charger dans le code :
```python
import os
from dotenv import load_dotenv

load_dotenv('config.env')
github_token = os.getenv('GITHUB_TOKEN')
updater = Updater(github_token=github_token)
```

**Option 3B : Fichier de Configuration**

Créer `config/github_token.txt` (à ne PAS commit) :
```
ghp_xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
```

Charger dans le code :
```python
import os

token_file = os.path.join('config', 'github_token.txt')
github_token = None
if os.path.exists(token_file):
    with open(token_file, 'r') as f:
        github_token = f.read().strip()

updater = Updater(github_token=github_token)
```

**Option 3C : Demander à l'Utilisateur**

Ajouter un champ dans les paramètres de l'application.

**⏱️ Temps estimé** : 10-15 minutes

---

## 🎯 Recommandation

### Pour DestriChiffrage

**JE RECOMMANDE L'OPTION A** : Rendre le repository public

**Raisons** :
1. ✅ **Simplicité** : Aucun code à modifier, fonctionne immédiatement
2. ✅ **Maintenance** : Pas de tokens à gérer ou renouveler
3. ✅ **Transparence** : Un outil de gestion de catalogue n'a pas besoin d'être privé
4. ✅ **Distribution** : Tu distribues déjà les binaires publiquement via les releases
5. ✅ **Open Source** : Peut devenir un projet de portfolio ou aider d'autres développeurs

**Note** : Si le repository contient des informations sensibles (clés API, mots de passe), retire-les d'abord avant de rendre public. Mais actuellement, le code semble propre pour être public.

---

## 📋 Checklist de Mise en Production

### Si Option A (Repository Public)
- [ ] Vérifier qu'aucune information sensible n'est dans le code
- [ ] Vérifier le fichier `.gitignore` (exclure `config/`, `*.env`, etc.)
- [ ] Rendre le repository public via GitHub settings
- [ ] Tester l'auto-updater avec `python src/main.py` (version 0.0.9)
- [ ] Vérifier que la mise à jour v1.0.0 est détectée
- [ ] Tester le téléchargement complet

### Si Option B (Token GitHub)
- [ ] Créer un Personal Access Token sur GitHub
- [ ] Modifier `src/updater.py` pour supporter le token
- [ ] Choisir une méthode de stockage du token
- [ ] Implémenter le chargement du token
- [ ] Ajouter le fichier de token au `.gitignore`
- [ ] Documenter le processus pour les utilisateurs
- [ ] Tester l'auto-updater avec le token
- [ ] Vérifier que la mise à jour v1.0.0 est détectée

---

## 🧪 Test Final

Une fois la solution appliquée :

```bash
# 1. Modifier la version à 0.0.9
# Éditer src/version.py : __version__ = "0.0.9"

# 2. Lancer l'application
python src/main.py

# 3. Menu "Aide" → "Vérifier les mises à jour..."

# 4. Résultat attendu :
# ✅ Détection de la version 1.0.0
# ✅ Affichage des notes de version
# ✅ Proposition de téléchargement
```

---

## 📊 Comparaison Finale

| Critère | Option A (Public) | Option B (Token) |
|---------|-------------------|------------------|
| Simplicité | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| Temps de mise en œuvre | 30 secondes | 15 minutes |
| Maintenance | Aucune | Tokens à renouveler |
| Sécurité du code | Public | Privé |
| Expérience utilisateur | Parfaite | Parfaite |
| Coût | Gratuit | Gratuit |
| **Recommandation** | **✅ OUI** | Seulement si vraiment nécessaire |

---

## 🚀 Action Immédiate

**Pour débloquer l'auto-updater maintenant** :

```bash
# Commande simple pour rendre le repo public
gh repo edit florentdestribois/DestriChiffrage --visibility public
```

Ensuite, tester immédiatement :
```bash
python src/main.py
# Menu "Aide" → "Vérifier les mises à jour..."
```

**Résultat attendu** : Détection automatique de v1.0.0 ✅

---

**Créé par** : Claude Code
**Date** : 2026-02-06
**Statut** : Solution documentée - Action requise
