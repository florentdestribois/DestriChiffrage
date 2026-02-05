---
description: Créer une issue GitHub à partir d'un fichier
---

# Instructions

Analyse le fichier indiqué et crée une issue GitHub complète avec :

1. **Titre** : Un titre clair et concis basé sur le contenu du fichier
2. **Description** : Une description détaillée incluant :
   - Le contexte et le problème identifié
   - Les modifications proposées
   - L'impact attendu
3. **Labels** : Suggère des labels appropriés (bug, enhancement, documentation, etc.)
4. **Checklist** : Liste des tâches à accomplir
5. **Fichiers concernés** : Liste des fichiers impactés

## Format de l'issue

```markdown
## 📋 Description
[Description détaillée du problème ou de la fonctionnalité]

## 🎯 Objectif
[Ce que cette issue vise à accomplir]

## 📁 Fichiers concernés
- `[chemin/vers/fichier]`

## ✅ Tâches
- [ ] Tâche 1
- [ ] Tâche 2
- [ ] Tests
- [ ] Documentation mise à jour

## 🏷️ Labels suggérés
- `enhancement` / `bug` / `documentation`
- `priority: low/medium/high`

## 💡 Notes additionnelles
[Informations supplémentaires si nécessaire]
```

Utilise ensuite la commande `gh issue create` pour créer l'issue sur GitHub.