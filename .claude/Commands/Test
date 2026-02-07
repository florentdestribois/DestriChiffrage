# 🔍 COMMANDE DE TEST APPROFONDI — POST-MODIFICATION MAJEURE

> **Objectif** : Effectuer une batterie de tests exhaustive après une modification majeure de l'application, couvrant l'intégrité de la base de données, la cohérence des formulaires, la stabilité générale et les cas limites.

---

## 📋 INSTRUCTIONS GÉNÉRALES

Tu viens d'effectuer une modification majeure sur l'application. Avant de considérer le travail terminé, tu dois impérativement réaliser **tous les tests ci-dessous**, dans l'ordre. Ne passe à la section suivante que lorsque la précédente est entièrement validée. Si un test échoue, corrige le problème **immédiatement** avant de poursuivre.

**Règle absolue** : Ne me dis jamais "tout fonctionne" sans avoir réellement exécuté chaque test. Montre-moi les résultats concrets.

---

## 1. 🗄️ INTÉGRITÉ DE LA BASE DE DONNÉES

### 1.1 — Structure et schéma
- [ ] Vérifier que toutes les collections/tables existent et correspondent au schéma attendu
- [ ] Vérifier que tous les champs obligatoires sont bien définis avec leurs types corrects
- [ ] Vérifier qu'aucune collection/table n'a été supprimée ou renommée par erreur
- [ ] Contrôler les index : sont-ils toujours en place et pertinents ?

### 1.2 — Relations et références
- [ ] Vérifier **chaque référence entre documents/tables** (clés étrangères, IDs liés)
- [ ] Tester qu'aucune référence ne pointe vers un document/enregistrement inexistant (orphelins)
- [ ] Vérifier la cohérence bidirectionnelle des relations (si A référence B, B référence-t-il A quand nécessaire ?)
- [ ] Tester la cascade : que se passe-t-il quand on supprime un élément parent ? Les enfants sont-ils correctement gérés ?

### 1.3 — Données existantes
- [ ] Vérifier que les données existantes n'ont pas été corrompues par la migration/modification
- [ ] Contrôler qu'aucun champ n'a perdu sa valeur ou changé de type
- [ ] Vérifier la rétrocompatibilité : les anciennes données fonctionnent-elles avec le nouveau code ?

---

## 2. 📝 COHÉRENCE DES FORMULAIRES ET CHAMPS

### 2.1 — Champs de saisie
- [ ] Vérifier que **chaque formulaire** de l'application s'affiche correctement
- [ ] Contrôler que tous les champs obligatoires sont bien marqués comme tels
- [ ] Vérifier les types de champs : un champ date accepte-t-il bien une date ? Un champ numérique refuse-t-il du texte ?
- [ ] Tester les valeurs par défaut : sont-elles correctes et cohérentes ?
- [ ] Vérifier les listes déroulantes / selects : contiennent-ils les bonnes options ? Les options sont-elles à jour ?

### 2.2 — Validation des données
- [ ] Tester la soumission d'un formulaire **vide** → les erreurs de validation s'affichent-elles ?
- [ ] Tester avec des données **invalides** (texte dans un champ numérique, date impossible, email malformé, etc.)
- [ ] Tester avec des données **extrêmes** (chaînes très longues, nombres négatifs, caractères spéciaux, émojis, HTML/scripts)
- [ ] Vérifier que les messages d'erreur sont clairs, en français, et correctement positionnés
- [ ] Tester les champs conditionnels : les champs qui dépendent d'autres valeurs réagissent-ils correctement ?

### 2.3 — Soumission et enregistrement
- [ ] Vérifier que les données saisies arrivent **correctement** en base de données (bon format, bon champ, bonne collection)
- [ ] Tester la double soumission (clic rapide) → pas de doublon créé ?
- [ ] Vérifier les retours utilisateur : message de succès, redirection, mise à jour de l'affichage
- [ ] Tester la modification d'un enregistrement existant : les champs sont-ils pré-remplis correctement ?
- [ ] Tester la suppression : confirmation demandée ? Suppression effective ? Mise à jour de l'affichage ?

---

## 3. 🔗 NAVIGATION ET LIENS

### 3.1 — Routing
- [ ] Vérifier que **chaque route/page** de l'application est accessible
- [ ] Tester la navigation entre toutes les pages (liens du menu, boutons, breadcrumbs)
- [ ] Vérifier qu'aucune route ne retourne une erreur 404 ou une page blanche
- [ ] Tester l'accès direct par URL (copier-coller une URL dans le navigateur)
- [ ] Vérifier les redirections : sont-elles correctes après connexion, après soumission de formulaire ?

### 3.2 — Liens dynamiques
- [ ] Vérifier que les liens vers des éléments spécifiques (ex : fiche employé, détail d'un projet) fonctionnent avec des IDs valides
- [ ] Tester avec un ID invalide ou inexistant → message d'erreur approprié ?
- [ ] Vérifier les liens de retour ("Retour à la liste", bouton précédent)

---

## 4. 🛡️ STABILITÉ ET ROBUSTESSE

### 4.1 — Gestion des erreurs
- [ ] Vérifier qu'aucune erreur n'apparaît dans la console du navigateur (warnings acceptables, errors non)
- [ ] Tester le comportement en cas de perte de connexion réseau / base de données indisponible
- [ ] Vérifier la gestion des sessions : que se passe-t-il si le token expire en cours d'utilisation ?
- [ ] Tester les appels API : réponses correctes en cas de succès ET d'échec

### 4.2 — Performance
- [ ] Vérifier qu'aucune page ne met plus de 3 secondes à charger
- [ ] Contrôler qu'il n'y a pas de fuites mémoire (re-renders infinis, listeners non nettoyés)
- [ ] Vérifier que les requêtes à la base de données sont optimisées (pas de requêtes en boucle, pas de N+1)

### 4.3 — Cas limites
- [ ] Tester avec une base de données **vide** (premier lancement) → l'app gère-t-elle le cas "aucune donnée" ?
- [ ] Tester avec un **grand volume** de données → pagination, scroll, temps de chargement
- [ ] Tester les actions simultanées (deux onglets ouverts, modifications concurrentes)
- [ ] Vérifier le comportement sur différentes tailles d'écran (responsive)

---

## 5. 🔐 DROITS ET ACCÈS

- [ ] Vérifier que les pages protégées sont inaccessibles sans authentification
- [ ] Tester les différents rôles utilisateur : chaque rôle voit-il uniquement ce qu'il doit voir ?
- [ ] Vérifier qu'un utilisateur non autorisé ne peut pas accéder aux API protégées directement
- [ ] Tester la déconnexion : nettoyage correct de la session ?

---

## 6. 📊 RAPPORT DE TEST

À la fin de tous les tests, fournis-moi un **rapport structuré** au format suivant :

```
### ✅ TESTS RÉUSSIS
- [Section] Description du test

### ❌ TESTS ÉCHOUÉS (corrigés)
- [Section] Description du problème → Correction appliquée

### ⚠️ POINTS D'ATTENTION
- Observations, suggestions d'amélioration, dette technique identifiée

### 📈 BILAN
- Nombre total de tests exécutés : XX
- Réussis du premier coup : XX
- Corrigés en cours de route : XX
- Problèmes résiduels : XX
```

---

## ⚡ RAPPELS IMPORTANTS

1. **Ne saute aucun test**, même si tu penses que la modification ne l'affecte pas. Les effets de bord sont la première source de bugs.
2. **Corrige immédiatement** tout problème détecté, puis re-teste la correction.
3. **Documente chaque correction** dans le rapport final.
4. En cas de doute sur un comportement, **teste-le** plutôt que de supposer qu'il fonctionne.
5. **Vérifie le build** : l'application compile-t-elle sans erreur ni warning ?