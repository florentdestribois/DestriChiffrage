#!/bin/bash
# Commande pour générer un message d'information formaté pour DestriBoard
# Usage: /message_info <ton> <idée du message>

# Cette commande demande à Claude de :
# 1. Rédiger un message professionnel et bien formulé à partir de l'idée fournie
# 2. Appliquer le ton demandé (informatif, urgent, positif, rappel, nouveaute, heureux)
# 3. Générer le HTML avec les styles Destribois (structure complète)
# 4. Sauvegarder dans .claude/message_informations/

echo "📝 Génération d'un message d'information pour DestriBoard"
echo ""
echo "Instruction pour Claude :"
echo "========================"
echo ""
echo "Génère un message d'information HTML pour le tableau de bord des employés DestriBoard."
echo ""
echo "Ton demandé : $1"
echo "Idée du message : ${@:2}"
echo ""
echo "Instructions :"
echo "1. Rédige un message professionnel et bien formulé à partir de l'idée fournie"
echo "2. Utilise un français correct et adapté au contexte professionnel"
echo "3. Applique le ton demandé parmi : informatif, urgent, positif, rappel, nouveaute, heureux"
echo "4. Formate le HTML avec la structure complète Destribois (voir template ci-dessous)"
echo "5. Mets en évidence les dates, heures, montants et pourcentages"
echo "6. Sauvegarde le résultat dans .claude/message_informations/latest.html"
echo ""
echo "========================"
echo ""
echo "TEMPLATE HTML À UTILISER (structure complète) :"
echo ""
cat << 'EOF'
<!DOCTYPE html>
<html lang="fr">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Nouvelles améliorations - [DATE]</title>
</head>
<body style="font-family: 'Roboto', 'Arial', sans-serif; max-width: 800px; margin: 0 auto; padding: 20px; background-color: #EDE6DC;">
    <!-- En-tête principal -->
    <div style="background: #2E3544; padding: 30px; border-radius: 12px 12px 0 0; text-align: center; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">
        <h1 style="color: #EDE6DC; margin: 0; font-family: 'Rubik', sans-serif; font-size: 28px; font-weight: 500;">
            [TITRE PRINCIPAL]
        </h1>
        <p style="color: #AE9367; margin-top: 10px; font-size: 14px; text-transform: uppercase; letter-spacing: 1px;">
            [DATE] - Version [X.X.X]
        </p>
    </div>

    <!-- Contenu principal -->
    <div style="background: white; padding: 30px; border-radius: 0 0 12px 12px; box-shadow: 0 4px 6px rgba(0,0,0,0.1);">

        <!-- Section 1 -->
        <div style="background: #2E3544; padding: 12px 20px; border-radius: 8px; margin-bottom: 20px;">
            <h2 style="margin: 0; font-family: 'Rubik', sans-serif; font-size: 18px; font-weight: 500; color: #EDE6DC;">
                [ICÔNE] [TITRE SECTION]
            </h2>
        </div>

        <div style="background: #EDE6DC; padding: 20px; border-radius: 8px; margin-bottom: 25px; border-left: 4px solid #AE9367;">
            <h3 style="color: #2E3544; margin-top: 0; font-family: 'Rubik', sans-serif; font-size: 16px;">
                [SOUS-TITRE]
            </h3>
            <p style="color: #2E3544; line-height: 1.6; margin: 10px 0;">
                [CONTENU TEXTE] avec <strong style="color: #AE9367;">mise en évidence</strong>
            </p>
            <ul style="color: #2E3544; line-height: 1.8; padding-left: 20px;">
                <li style="margin-bottom: 8px;">
                    <strong>[Point clé]</strong><br>
                    <span style="font-size: 14px; color: #666;">[Description]</span>
                </li>
            </ul>
            <!-- Encadré d'exemple ou note importante -->
            <div style="background: white; padding: 15px; border-radius: 6px; margin-top: 15px; border: 1px solid #AE9367;">
                <p style="color: #2E3544; margin: 0; font-size: 14px;">
                    <strong style="color: #AE9367;">[Label] :</strong> [Exemple ou note]
                </p>
            </div>
        </div>

        <!-- Répéter les sections selon les besoins -->

        <!-- Footer -->
        <div style="text-align: center; margin-top: 30px; padding-top: 20px; border-top: 2px solid #EDE6DC;">
            <p style="color: #666; font-size: 14px; margin: 0;">
                [Message de conclusion]
            </p>
            <p style="color: #666; font-size: 14px; margin: 10px 0;">
                Pour toute question, contactez votre responsable.
            </p>
            <div style="margin-top: 20px;">
                <span style="background: #AE9367; color: white; padding: 8px 20px; border-radius: 20px; font-size: 12px; font-weight: bold; text-transform: uppercase; letter-spacing: 1px;">
                    DestriBoard v[X.X.X]
                </span>
            </div>
        </div>
    </div>
</body>
</html>
EOF

echo ""
echo "========================"
echo ""
echo "COULEURS DESTRIBOIS À UTILISER :"
echo "- Fond principal : #EDE6DC (crème)"
echo "- Titres/en-têtes : #2E3544 (bleu foncé)"
echo "- Accents/highlights : #AE9367 (beige/or)"
echo "- Texte standard : #2E3544"
echo "- Texte secondaire : #666"
echo ""
echo "ICÔNES RECOMMANDÉES SELON LE TON :"
echo "- informatif : ℹ️ 📋"
echo "- urgent : ⚠️ 🚨"
echo "- positif : ✅ 👍"
echo "- rappel : 📅 ⏰"
echo "- nouveaute : ✨ 🎉"
echo "- heureux : 🎊 😊"
echo ""
echo "STRUCTURE HTML :"
echo "- Document HTML5 complet avec <head> et <body>"
echo "- Responsive avec max-width: 800px"
echo "- En-tête avec background #2E3544"
echo "- Sections avec titres sur fond #2E3544"
echo "- Contenu dans blocs #EDE6DC avec bordure gauche #AE9367"
echo "- Footer avec badge de version"
echo ""
echo "========================"
