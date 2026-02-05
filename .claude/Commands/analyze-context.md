#!/bin/bash

# Commande Claude pour analyser le contexte de l'application et gérer les modifications
# Usage: sh .claude/Commands/analyze-context

echo "📚 Analyse du contexte de l'application DestriBoard..."
echo "================================================"
echo ""

# Fonction pour afficher le contenu d'un fichier avec formatage
show_file_content() {
    local file=$1
    local title=$2
    
    if [ -f "$file" ]; then
        echo "📄 $title"
        echo "----------------------------------------"
        # Affiche les 50 premières lignes pour avoir un aperçu
        head -n 50 "$file"
        echo ""
        echo "[... Fichier tronqué pour l'aperçu ...]"
        echo ""
    else
        echo "⚠️  $title - Fichier non trouvé: $file"
        echo ""
    fi
}

# 1. Analyse de CLAUDE.md
echo "1️⃣  ANALYSE DE CLAUDE.md (Instructions pour Claude Code)"
echo "=========================================="
show_file_content "CLAUDE.md" "Instructions et configuration du projet"

# 2. Analyse de README.md
echo "2️⃣  ANALYSE DE README.md (Documentation utilisateur)"
echo "=========================================="
show_file_content "README.md" "Documentation générale du projet"

# 3. Analyse du dossier docs/
echo "3️⃣  ANALYSE DU DOSSIER docs/"
echo "=========================================="
if [ -d "docs" ]; then
    echo "📁 Contenu du dossier docs/:"
    ls -la docs/ 2>/dev/null || echo "Le dossier docs/ est vide ou inaccessible"
    echo ""
    
    # Parcours des fichiers .md dans docs/
    for doc in docs/*.md; do
        if [ -f "$doc" ]; then
            filename=$(basename "$doc")
            echo "📝 Documentation: $filename"
            echo "----------------------------------------"
            head -n 30 "$doc"
            echo "[... Suite du fichier $filename ...]"
            echo ""
        fi
    done
else
    echo "ℹ️  Le dossier docs/ n'existe pas encore"
    echo ""
fi

# 4. Résumé du contexte
echo "4️⃣  RÉSUMÉ DU CONTEXTE"
echo "=========================================="
echo ""
echo "📊 Version actuelle de l'application:"
grep -E "version|Version|VERSION" package.json 2>/dev/null || echo "Version non trouvée"
echo ""

echo "🏗️  Architecture principale:"
echo "  - Framework: Next.js 15 avec TypeScript"
echo "  - Base de données: Firebase Firestore"
echo "  - Authentification: Firebase Auth"
echo "  - UI: shadcn/ui avec Tailwind CSS"
echo "  - Email: Nodemailer"
echo "  - Déploiement: Vercel"
echo ""

echo "📋 Collections Firestore principales:"
echo "  - users (employés et administrateurs)"
echo "  - dailyEntries (entrées quotidiennes)"
echo "  - vacationRequests (demandes de congés)"
echo "  - overtimeRequests (heures supplémentaires)"
echo "  - settings (configuration globale)"
echo ""

# 5. Instructions pour les modifications
echo "5️⃣  INSTRUCTIONS POUR LES MODIFICATIONS"
echo "=========================================="
echo ""
echo "⚠️  RAPPEL IMPORTANT:"
echo "  Pour TOUTE modification du code, vous devez:"
echo ""
echo "  1. 📖 Lire et comprendre le contexte via CLAUDE.md et README.md"
echo "  2. 🔍 Vérifier les patterns existants dans le code"
echo "  3. ✏️  Effectuer les modifications nécessaires"
echo "  4. 📝 Mettre à jour la documentation:"
echo "     - README.md : Section 'Historique des versions' (en français)"
echo "     - CLAUDE.md : Section 'Recent Updates' (en anglais)"
echo "     - docs/ : Si la modification impacte une fonctionnalité documentée"
echo "  5. 🧪 Vérifier que les tests passent: npm test"
echo "  6. 🔨 Vérifier le build: npm run build"
echo ""

echo "📌 Points d'attention spécifiques:"
echo "  - Utiliser les classes CSS personnalisées de globals.css"
echo "  - Respecter les conventions de nommage existantes"
echo "  - Maintenir la cohérence avec le design system Destribois"
echo "  - Suivre les patterns d'API existants (éviter la duplication)"
echo ""

# 6. État actuel de git
echo "6️⃣  ÉTAT ACTUEL DU REPOSITORY"
echo "=========================================="
echo ""
echo "📦 Branche actuelle:"
git branch --show-current 2>/dev/null || echo "Impossible de déterminer la branche"
echo ""

echo "📊 Statut Git:"
git status --short 2>/dev/null || echo "Impossible d'obtenir le statut git"
echo ""

echo "📅 Derniers commits:"
git log --oneline -5 2>/dev/null || echo "Impossible d'obtenir l'historique des commits"
echo ""

# 7. Prochaines étapes suggérées
echo "7️⃣  PROCHAINES ÉTAPES SUGGÉRÉES"
echo "=========================================="
echo ""
echo "Pour commencer à travailler sur une modification:"
echo ""
echo "1. Identifiez clairement la fonctionnalité à modifier"
echo "2. Recherchez les fichiers concernés avec:"
echo "   - grep -r 'terme_recherché' --include='*.tsx' --include='*.ts'"
echo "3. Lisez le code existant pour comprendre les patterns"
echo "4. Créez une liste de tâches avec TodoWrite"
echo "5. Effectuez les modifications en suivant les conventions"
echo "6. Mettez à jour la documentation immédiatement après"
echo ""

echo "✅ Analyse du contexte terminée!"
echo ""
echo "💡 Conseil: Utilisez cette commande avant chaque session de développement"
echo "   pour vous assurer d'avoir le contexte complet de l'application."