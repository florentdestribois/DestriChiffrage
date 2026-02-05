---
description: Mettre à jour le numéro de version dans tous les fichiers de l'application
---

# Mise à jour du numéro de version

Cette commande met à jour le numéro de version dans tous les fichiers pertinents de l'application DestriBoard.

## Fichiers à modifier

Les fichiers suivants contiennent le numéro de version et doivent être mis à jour :

1. **package.json** - Version npm du projet
2. **components/admin/admin-dashboard.tsx** - Affichage dans le header admin
3. **components/dashboard/employee-dashboard.tsx** - Affichage dans le header employé
4. **README.md** - Titre principal du README
5. **login-form.tsx** - Accès DestriBoard <span className="app-version app-version-dark">v1.1.3</span>

## Instructions

Pour mettre à jour la version, suivez ces étapes :

### 1. Demander la nouvelle version
Demandez d'abord quelle est la nouvelle version souhaitée (format : v1.X.X)

### 2. Mettre à jour package.json
```bash
# Rechercher la version actuelle
grep '"version"' package.json

# Modifier la version
Edit package.json et remplacer la version
```

### 3. Mettre à jour les dashboards
```bash
# Pour admin-dashboard.tsx
grep 'app-version' components/admin/admin-dashboard.tsx
# Utiliser Edit avec replace_all=true pour remplacer toutes les occurrences

# Pour employee-dashboard.tsx  
grep 'app-version' components/dashboard/employee-dashboard.tsx
# Utiliser Edit avec replace_all=true pour remplacer toutes les occurrences

# Pour login-form.tsx 
grep 'app-version' components/auth/login-form.tsx
```

### 4. Mettre à jour le README
```bash
# Rechercher le titre
head -1 README.md
# Modifier le titre avec la nouvelle version
```
Indiquer les modification réaliser dans le fichier Readme et claude.md

### 5. Vérifier et committer
```bash
# Vérifier que le build fonctionne
npm run build

# Créer le commit
git add -A
git commit -m "chore: Mise à jour du numéro de version vX.X.X

- Mise à jour dans package.json
- Mise à jour dans admin-dashboard.tsx  
- Mise à jour dans employee-dashboard.tsx
- Mise à jour dans README.md"

# Pousser sur GitHub
git push origin main
```

## Exemple d'utilisation

Pour passer de v1.1.9 à v1.2.0 :

1. Modifier package.json : `"version": "1.1.9"` → `"version": "1.2.0"`
2. Modifier admin-dashboard.tsx : `v1.1.9` → `v1.2.0` (toutes les occurrences)
3. Modifier employee-dashboard.tsx : `v1.1.9` → `v1.2.0` (toutes les occurrences)
4. Modifier README.md : `# DestriBoard v1.1.9` → `# DestriBoard v1.2.0`

## Notes importantes

- Toujours vérifier que le build fonctionne après les modifications
- Le format de version suit le semantic versioning : MAJOR.MINOR.PATCH
- Documenter les changements dans la section "Historique des versions" du README
