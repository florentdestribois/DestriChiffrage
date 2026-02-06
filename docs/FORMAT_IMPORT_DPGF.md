# Format d'import DPGF - Proposition

> **Date :** 06/02/2026
> **Version :** 1.0
> **Basé sur :** Analyse de 7 fichiers DPGF réels (4 formats différents)

---

## 1. Contexte et objectif

### Problème
Les DPGF reçus lors des appels d'offres proviennent de sources très variées :

| Source | Format | Complexité | Exemples |
|--------|--------|------------|----------|
| **Format A** - Manuel | Excel simple, colonnes plates | Faible | Stabilo, Drusenheim |
| **Format B** - DVS/DeViSor | Excel structuré, codes NIV | Forte | Batzendorf, Berstheim, Scharrachbergheim |
| **Format C** - OTE Ingénierie | Excel multi-bâtiments | Moyenne | Lingolsheim |
| **Format D** - SBM/Mayker | Excel semi-structuré | Moyenne | Mutzig |

### Colonnes universelles identifiées

Malgré la diversité des formats, **6 colonnes sont présentes dans 100% des DPGF** analysés :

| Donnée | Format A | Format B (DVS) | Format C (OTE) | Format D (SBM) |
|--------|----------|----------------|-----------------|-----------------|
| N° article | Col A (`1.1`) | Col B (`16.4.1.1`) | Col A (`C.1.1.1`) | Col B (`05.3.2`) |
| Désignation | Col B | Col C (TITRE1) | Col B | Col C |
| Unité | Col D | Col F (U) | Col C | Col D |
| Quantité | Col E | Col G (QTE) | Col D (par bât.) | Col E |
| PU HT | Col F | Col I (CRM) | Col E (par bât.) | Col F |
| PT HT | Col G | Col J (CRT) | Col F (par bât.) | Col G |

### Objectif
Proposer un **format CSV unique, simple et plat** que l'utilisateur remplit manuellement à partir du DPGF Excel reçu. Ce format doit :
- Être utilisable comme **template téléchargeable** (vide)
- Permettre de capturer **la hiérarchie** (lot/chapitre/article) sans complexité
- Être compatible avec le flux d'import existant de DestriChiffrage (`;` + UTF-8 BOM)
- Servir aussi de **format d'export** (enrichi des colonnes de prix calculés)

---

## 2. Format proposé : CSV DPGF DestriChiffrage

### 2.1 Choix de conception

| Décision | Choix | Justification |
|----------|-------|---------------|
| **Hiérarchie** | Colonne `NIVEAU` (1-4) + `CODE` numéroté | Plus simple qu'un arbre, préserve la structure |
| **Catégorisation** | Colonne `CATEGORIE` libre | Permet PORTES, AGENCEMENT, DIVERS ou autre |
| **Dimensions** | Colonnes `LARGEUR` + `HAUTEUR` séparées (en mm) | Compatible avec le catalogue DestriChiffrage |
| **Caractéristiques** | Colonne texte libre | Capture EI30, RA=35dB, finition, etc. |
| **Localisation** | Colonne `LOCALISATION` | Fréquent dans les DPGF (RDC, R+1, salle X...) |
| **Prix** | `PU_HT` et `PT_HT` optionnels à l'import | Remplis par l'application lors du chiffrage |

### 2.2 Colonnes du template d'import

```
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES
```

**11 colonnes**, détaillées ci-dessous :

| # | Colonne | Type | Obligatoire | Description | Exemple |
|---|---------|------|-------------|-------------|---------|
| 1 | `CODE` | Texte | **Oui** | Code article du DPGF original | `1.1`, `16.4.1.1`, `C.1.1` |
| 2 | `NIVEAU` | Entier | **Oui** | Niveau hiérarchique : **1**=Lot, **2**=Chapitre, **3**=Sous-chapitre, **4**=Article chiffrable | `4` |
| 3 | `DESIGNATION` | Texte | **Oui** | Libellé de l'article ou du chapitre | `BP âme pleine EI30 stratifié` |
| 4 | `CATEGORIE` | Texte | Non | Catégorie produit (aide au matching) | `PORTES`, `AGENCEMENT`, `DIVERS` |
| 5 | `LARGEUR_MM` | Entier | Non | Largeur en mm (si applicable) | `930` |
| 6 | `HAUTEUR_MM` | Entier | Non | Hauteur en mm (si applicable) | `2040` |
| 7 | `CARACTERISTIQUES` | Texte | Non | Caractéristiques techniques (EI, acoustique, finition...) | `EI30, RA=35dB, stratifié chêne` |
| 8 | `UNITE` | Texte | **Oui** (si NIVEAU=4) | Unité de mesure | `U`, `ENS`, `ML`, `M2`, `FT` |
| 9 | `QUANTITE` | Nombre | **Oui** (si NIVEAU=4) | Quantité du DPGF | `5`, `12.5` |
| 10 | `LOCALISATION` | Texte | Non | Emplacement dans le bâtiment | `RDC salle 103`, `R+1 couloir` |
| 11 | `NOTES` | Texte | Non | Remarques, précisions | `Voir plan 2.3`, `Avec oculus` |

### 2.3 Règles de remplissage

#### Niveaux hiérarchiques

| NIVEAU | Rôle | Champs requis | PU/PT |
|--------|------|---------------|-------|
| **1** | Lot / Titre principal | CODE + DESIGNATION | Non |
| **2** | Chapitre (ex: "BLOCS-PORTES") | CODE + DESIGNATION | Non |
| **3** | Sous-chapitre (optionnel) | CODE + DESIGNATION | Non |
| **4** | Article chiffrable | CODE + DESIGNATION + UNITE + QUANTITE | Oui (rempli par l'app) |

- Seuls les articles de **NIVEAU 4** sont importés dans `prix_marche` comme articles chiffrables.
- Les niveaux 1, 2, 3 sont conservés pour l'affichage et l'export mais ne génèrent pas d'entrées `prix_marche`.
- Un DPGF simple peut n'avoir que des niveaux 2 et 4 (chapitre + articles).

#### Catégorie
- Si la colonne `CATEGORIE` est vide, l'utilisateur choisit une catégorie par défaut dans le dialogue d'import.
- Les catégories standards sont : `PORTES`, `AGENCEMENT`, `DIVERS`, `VESTIAIRES`, `MOBILIER`.
- Possibilité de spécifier une catégorie différente par ligne (utile pour les DPGF mixtes).

#### Dimensions
- En **millimètres** (compatibilité catalogue DestriChiffrage qui stocke en mm).
- Si le DPGF donne `0,93 x 2,04 m` → remplir `930` et `2040`.
- Si non applicable (ex: ensemble, forfait) → laisser vide.

#### Caractéristiques
- Texte libre, mais il est recommandé de suivre un format structuré :
  - Performance feu : `EI30`, `EI60`
  - Acoustique : `RA=35dB`, `RW=44dB`
  - Finition : `stratifié`, `à peindre`, `placage chêne`
  - Séparateur recommandé : `, ` (virgule + espace)

---

## 3. Exemple concret

### 3.1 Extrait d'un DPGF Stabilo (Format A original)

```
n° | Désignation                        | u  | Q  | PU  | PT
1. | BLOCS-PORTES                       |    |    |     |
1.1| BP âme pleine standard 0,80x2,03  | U  | 15 |     |
1.2| BP âme pleine standard 0,90x2,03  | U  | 8  |     |
1.3| BP acoustique 30 dB 0,80x2,03     | U  | 3  |     |
2. | AGENCEMENT                         |    |    |     |
2.1| Kitchenette type A                 | ENS| 2  |     |
```

### 3.2 Même DPGF au format d'import DestriChiffrage

```csv
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES
1.;2;BLOCS-PORTES;PORTES;;;;;;;
1.1;4;BP âme pleine standard;PORTES;800;2030;Stratifié;U;15;;
1.2;4;BP âme pleine standard;PORTES;900;2030;Stratifié;U;8;;
1.3;4;BP acoustique 30 dB;PORTES;800;2030;RA=30dB, Stratifié acoustique;U;3;;
2.;2;AGENCEMENT;AGENCEMENT;;;;;;;
2.1;4;Kitchenette type A;AGENCEMENT;;;;ENS;2;;
```

### 3.3 Extrait d'un DPGF DVS/Batzendorf (Format B original)

```
NIV | CODE      | Désignation                          | U   | Qte | PU HT | PT HT
2   | 16        | MENUISERIE INTERIEURE BOIS           |     |     |       |
3   | 16.4      | BLOC PORTE INTERIEUR BOIS            |     |     |       |
5   | 16.4.1    | Blocs-portes âme pleine              |     |     |       |
9   | 16.4.1.1  | BP prépeint 83x204 EI30              | U   | 12  |       |
9   | 16.4.1.2  | BP prépeint 93x204 EI30              | U   | 5   |       |
9   | 16.4.2.1  | BP acoustique RA=35dB 93x204         | U   | 3   |       |
```

### 3.4 Même DPGF DVS au format d'import DestriChiffrage

```csv
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES
16;1;MENUISERIE INTERIEURE BOIS;;;;;;;;
16.4;2;BLOC PORTE INTERIEUR BOIS;PORTES;;;;;;;
16.4.1;3;Blocs-portes âme pleine;PORTES;;;;;;;
16.4.1.1;4;BP prépeint EI30;PORTES;830;2040;EI30, à peindre;U;12;;
16.4.1.2;4;BP prépeint EI30;PORTES;930;2040;EI30, à peindre;U;5;;
16.4.2.1;4;BP acoustique RA=35dB;PORTES;930;2040;EI30, RA=35dB;U;3;;
```

---

## 4. Correspondance avec le modèle de données

### 4.1 Import : CSV → table `prix_marche`

| Colonne CSV | Champ `prix_marche` | Transformation |
|-------------|---------------------|----------------|
| `CODE` | `id_prix` | Préfixe auto : `PM-{CODE}` |
| `DESIGNATION` | `designation` | Direct |
| `CATEGORIE` | `categorie` | Direct ou défaut dialogue |
| `LARGEUR_MM` + `HAUTEUR_MM` | `dimensions` | Format `L x H mm` |
| `CARACTERISTIQUES` | `caracteristiques` | Direct |
| `UNITE` | `unite` | Direct |
| `QUANTITE` | `quantite` | Direct |
| `LOCALISATION` | `notes` | Concaténé avec NOTES |
| `NOTES` | `notes` | Concaténé avec LOCALISATION |

> **Seules les lignes NIVEAU=4 sont importées dans `prix_marche`.**
> Les lignes NIVEAU 1-3 sont stockées dans une structure annexe pour l'affichage et l'export.

### 4.2 Export : table `prix_marche` → CSV enrichi

À l'export, le CSV contient les mêmes colonnes + les colonnes de chiffrage :

```
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES;PU_HT;PT_HT
```

Les colonnes `PU_HT` et `PT_HT` sont remplies par l'application.
Un export "client" ne contient que ces colonnes (sans coûts internes).

---

## 5. Détection automatique du format source (Phase 2+)

Pour une future fonctionnalité d'**import direct depuis un DPGF Excel** (sans conversion manuelle en CSV), voici les heuristiques de détection identifiées :

### 5.1 Arbre de décision

```
                    ┌─ Fichier Excel (.xlsx/.xls) ─┐
                    │                                │
            ┌───────┴───────┐                        │
            │ Feuille       │                        │
            │ "Version"     │                        │
            │ existe ?      │                        │
            ├── OUI ────────┤                        │
            │  SRC=DVS_APP  │                        │
            │  → FORMAT B   │                        │
            │  (DVS parser) │                        │
            ├── NON ────────┤                        │
            │               │                        │
      ┌─────┴─────┐                                  │
      │ Colonnes  │                                  │
      │ QTE/PU/PT │                                  │
      │ répétées? │                                  │
      ├── OUI ────┤                                  │
      │ → FORMAT C│                                  │
      │ (multi-bât│                                  │
      │  parser)  │                                  │
      ├── NON ────┤                                  │
      │           │                                  │
      │ Chercher  │                                  │
      │ ligne     │                                  │
      │ en-tête : │                                  │
      │ designat° │                                  │
      │ + u + Q   │                                  │
      │ + PU + PT │                                  │
      │ → FORMAT A│                                  │
      │ (simple   │                                  │
      │  parser)  │                                  │
      └───────────┘                                  │
                    └────────────────────────────────┘
```

### 5.2 Parsers spécifiques

| Format | Détection | Ligne en-tête | Articles | Hiérarchie |
|--------|-----------|---------------|----------|------------|
| **A** | Keywords dans une ligne | Scan rows 1-20 | Lignes avec unité+qté non vides | Numérotation dans col Code |
| **B** | Feuille "Version" + SRC=DVS_APP | Row 1 (interne) ou Row 3 (affichage) | NIV = `9` | NIV = 2/3/4/5 |
| **C** | Groupes QTE/PU/PT répétés | Row 2-3 | Lignes avec unité+qté non vides | Codes lettrés (C.1.1) |
| **D** | Ni B ni C, keywords trouvés | Scan rows 1-10 | Lignes avec unité+qté non vides | Codes numériques (05.3.2) |

> **Note :** L'import direct Excel est prévu pour une version ultérieure (Phase 2+).
> La v1.1.0 ne supporte que l'import CSV template.

---

## 6. Workflow utilisateur recommandé

```
1. Réception du DPGF Excel par email / plateforme marchés
   │
2. Ouverture dans Excel, identification du format
   │
3. Téléchargement du template CSV depuis DestriChiffrage
   │    Menu : Fichier → Télécharger template DPGF
   │
4. Recopie manuelle des articles du DPGF dans le template CSV
   │    - Structurer avec les NIVEAUX (1-4)
   │    - Extraire les dimensions séparément (L x H en mm)
   │    - Reporter les caractéristiques techniques
   │    - Seuls les articles chiffrables en NIVEAU 4
   │
5. Import du CSV dans DestriChiffrage
   │    Menu : Fichier → Importer DPGF
   │    - Création du chantier (nom, lieu, année, lot...)
   │    - Sélection du fichier CSV
   │    - Matching automatique avec le catalogue produits
   │
6. Chiffrage dans l'application
   │    - Lier/créer les produits
   │    - Saisir les temps de MO
   │    - Ajuster les marges
   │
7. Export du DPGF chiffré
       - CSV client (CODE + DESIGNATION + UNITE + QTE + PU + PT)
       - Sauvegarde en BDD
```

---

## 7. Template CSV vide (contenu du fichier téléchargeable)

Le template contiendra un en-tête + 2 lignes d'exemple commentées :

```csv
CODE;NIVEAU;DESIGNATION;CATEGORIE;LARGEUR_MM;HAUTEUR_MM;CARACTERISTIQUES;UNITE;QUANTITE;LOCALISATION;NOTES
#;#;--- INSTRUCTIONS ---;#;#;#;#;#;#;#;--- Remplir les articles du DPGF ci-dessous. Supprimer ces 2 lignes d'exemple. ---
1.;2;BLOCS-PORTES (exemple chapitre);PORTES;;;;;;;
1.1;4;BP âme pleine EI30 (exemple article);PORTES;930;2040;EI30, à peindre;U;5;RDC Hall;Voir CCTP p.15
```

> **Encodage :** UTF-8 avec BOM
> **Délimiteur :** `;` (point-virgule)
> **Décimale :** `,` (virgule) pour les quantités décimales

---

## 8. Avantages de cette approche

| Critère | Évaluation |
|---------|------------|
| **Simplicité** | 11 colonnes seulement, remplissage intuitif |
| **Universalité** | Couvre les 4 formats de DPGF analysés |
| **Compatibilité** | Même convention que l'import catalogue existant (`;` + UTF-8 BOM) |
| **Extensibilité** | Facile d'ajouter des colonnes (ex: TVA, variante) |
| **Matching produit** | Dimensions séparées (mm) + caractéristiques = matching efficace |
| **Hiérarchie** | Colonne NIVEAU simple (1-4) préserve la structure pour l'export |
| **Export** | Même format + colonnes PU/PT = réutilisable tel quel |
| **Évolutivité** | Import direct Excel préparé (heuristiques documentées) |
