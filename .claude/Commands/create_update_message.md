# Créer un message de mise à jour pour les employés

Cette commande génère un message HTML dans le style Destribois pour informer les employés des nouvelles fonctionnalités et améliorations de l'application.

## Instructions pour Claude

### 1. Demander les informations nécessaires
Demandez à l'utilisateur :
- La date de la mise à jour
- Le numéro de version
- Les améliorations à communiquer (organisées par catégories)

### 2. Structure du message
Le message doit suivre cette structure :
```html
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouvelles améliorations - [DATE]</title>
</head>
<body style="font-family: 'Roboto', 'Arial', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #EDE6DC;">
    <!-- Header -->
    <div style="background: #2E3544; padding: 30px; border-radius: 12px 12px 0 0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: #EDE6DC; margin: 0; font-family: 'Rubik', sans-serif; font-size: 28px; font-weight: 500;">
            Nouvelles améliorations de l'application
        </h1>
        <p style="color: #AE9367; margin-top: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
            [DATE] - Version [VERSION]
        </p>
    </div>
    
    <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <!-- Sections des améliorations -->
        [CONTENU]
        
        <!-- Footer -->
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #EDE6DC;">
            <p style="color: #666; font-size: 14px; margin: 0;">
                Ces améliorations facilitent votre utilisation quotidienne.
            </p>
            <p style="color: #666; font-size: 14px; margin: 10px 0;">
                Pour toute question, contactez votre responsable.
            </p>
            <div style="margin-top: 20px;">
                <span style="background: #AE9367; color: white; padding: 8px 20px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">
                    DestriBoard v[VERSION]
                </span>
            </div>
        </div>
    </div>
</body>
</html>
```

### 3. Template pour chaque section d'amélioration

#### Section principale (titre avec fond sombre)
```html
<div style="background: #2E3544; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px;">
    <h2 style="margin: 0; font-family: 'Rubik', sans-serif; font-size: 18px; font-weight: 500; color: #EDE6DC;">
        [TITRE DE LA SECTION]
    </h2>
</div>
```

#### Contenu de la section (fond crème avec bordure)
```html
<div style="background: #EDE6DC; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #AE9367;">
    <h3 style="color: #2E3544; margin-top: 0; font-family: 'Rubik', sans-serif; font-size: 16px;">
        [SOUS-TITRE]
    </h3>
    <p style="color: #2E3544; line-height: 1.6; margin: 10px 0;">
        [DESCRIPTION]
    </p>
    <ul style="color: #2E3544; line-height: 1.8; padding-left: 20px;">
        <li style="margin-bottom: 8px;">
            <strong>[POINT CLÉ]</strong><br>
            <span style="font-size: 14px; color: #666;">[EXPLICATION DÉTAILLÉE]</span>
        </li>
    </ul>
</div>
```

#### Encadré d'exemple ou d'information importante
```html
<div style="background: white; padding: 15px; border-radius: 6px; margin-top: 15px; border: 1px solid #AE9367;">
    <p style="color: #2E3544; margin: 0; font-size: 14px;">
        <strong style="color: #AE9367;">Exemple :</strong> [EXEMPLE PRATIQUE]
    </p>
</div>
```

#### Section d'instructions (avec dégradé)
```html
<div style="background: linear-gradient(135deg, #AE9367 0%, #8B7453 100%); padding: 20px; border-radius: 8px; margin-top: 30px;">
    <h3 style="color: white; margin: 0 0 15px 0; font-family: 'Rubik', sans-serif; font-size: 16px;">
        Comment profiter de ces améliorations ?
    </h3>
    <div style="background: white; padding: 15px; border-radius: 6px;">
        <ol style="color: #2E3544; line-height: 1.8; margin: 10px 0; padding-left: 20px;">
            <li style="margin-bottom: 8px;">
                <strong>[ACTION]:</strong> [DESCRIPTION]
            </li>
        </ol>
    </div>
</div>
```

### 4. Palette de couleurs Destribois
- **Fond principal** : `#EDE6DC` (crème)
- **Headers/Titres** : `#2E3544` (dark)
- **Accents** : `#AE9367` (beige doré)
- **Texte principal** : `#2E3544`
- **Texte secondaire** : `#666`
- **Blanc** : `white` ou `#FFFFFF`

### 5. Règles de style
- **Pas d'emojis colorés** - Utilisez des descriptions textuelles
- **Police des titres** : `font-family: 'Rubik', sans-serif`
- **Police du texte** : `font-family: 'Roboto', 'Arial', sans-serif`
- **Largeur maximale** : `800px`
- **Arrondis** : `border-radius: 8px` pour les sections, `12px` pour le conteneur principal
- **Ombres** : `box-shadow: 0 4px 6px rgba(0,0,0,0.1)`

### 6. Processus de création
1. Créer le fichier dans `.claude/message_informations/message_nouveautes_[DATE].html`
2. Utiliser le format de date : `JJ_MM_AAAA` (ex: `01_09_2025`)
3. Organiser les améliorations par ordre d'importance pour les employés
4. Privilégier un langage simple et direct
5. Donner des exemples concrets d'utilisation
6. Terminer par des instructions claires si nécessaire

### 7. Exemples de sections types

#### Pour une amélioration de l'interface
```html
<div style="background: #2E3544; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px;">
    <h2 style="margin: 0; font-family: 'Rubik', sans-serif; font-size: 18px; font-weight: 500; color: #EDE6DC;">
        Amélioration de la saisie quotidienne
    </h2>
</div>

<div style="background: #EDE6DC; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #AE9367;">
    <h3 style="color: #2E3544; margin-top: 0; font-family: 'Rubik', sans-serif; font-size: 16px;">
        Interface simplifiée
    </h3>
    <p style="color: #2E3544; line-height: 1.6; margin: 10px 0;">
        La saisie de vos heures est maintenant <strong style="color: #AE9367;">plus rapide et intuitive</strong> :
    </p>
    <ul style="color: #2E3544; line-height: 1.8; padding-left: 20px;">
        <li style="margin-bottom: 8px;">
            <strong>Nouveau bouton rapide</strong><br>
            <span style="font-size: 14px; color: #666;">Cliquez sur "Journée normale" pour saisir automatiquement vos heures standard</span>
        </li>
    </ul>
</div>
```

#### Pour une nouvelle fonctionnalité
```html
<div style="background: #2E3544; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px;">
    <h2 style="margin: 0; font-family: 'Rubik', sans-serif; font-size: 18px; font-weight: 500; color: #EDE6DC;">
        Nouvelle fonctionnalité
    </h2>
</div>

<div style="background: #EDE6DC; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #AE9367;">
    <p style="color: #2E3544; line-height: 1.6; margin: 10px 0;">
        Vous pouvez maintenant <strong style="color: #AE9367;">[ACTION PRINCIPALE]</strong> directement depuis votre tableau de bord.
    </p>
    <!-- Détails de la fonctionnalité -->
</div>
```

### 8. Validation finale
Avant de sauvegarder le fichier :
1. Vérifier que toutes les balises HTML sont fermées
2. S'assurer que les couleurs correspondent au design system Destribois
3. Relire pour éviter les fautes d'orthographe
4. Tester l'affichage dans un navigateur si possible

## Exemple de commande
Pour créer un nouveau message de mise à jour :
1. Demandez : "Crée un message de mise à jour pour les employés"
2. Claude vous demandera les informations nécessaires
3. Le fichier sera créé dans `.claude/message_informations/`
4. Le message pourra être utilisé dans l'application via le système de messages d'information