@echo off
cd /d "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
echo.
echo ========================================
echo PUBLICATION GitHub Release v1.7.7
echo ========================================
echo.
echo [1/2] Creation de la release...
gh release create v1.7.7 --title "Version 1.7.7" --notes "## Nouveautes v1.7.7

### Verification automatique des mises a jour (#26)
- Verification automatique des mises a jour au demarrage de l'application
- Execution en arriere-plan (non bloquant)
- Notification uniquement si une mise a jour est disponible
- Gestion silencieuse des erreurs (pas de notification en cas d'echec)

### Ameliorations du chiffrage DPGF (#25) - v1.7.6
- Ajout d'un champ Fournitures additionnelles pour ajouter des couts supplementaires
- Ajout d'une option Prix manuel pour forcer un prix de vente specifique
- Remplacement des champs de saisie MO par des Spinbox (increments de 1h)
- Interface plus intuitive pour la saisie des temps de main d'oeuvre

## Installation
Telechargez et executez DestriChiffrage-Setup-1.7.7.exe pour installer l'application."
if errorlevel 1 (
    echo ERREUR: Creation de la release echouee!
    pause
    exit /b 1
)
echo.
echo [2/2] Upload de l'installateur...
gh release upload v1.7.7 "installer_output\DestriChiffrage-Setup-1.7.7.exe"
if errorlevel 1 (
    echo ERREUR: Upload echoue!
    pause
    exit /b 1
)
echo.
echo ========================================
echo PUBLICATION TERMINEE AVEC SUCCES
echo ========================================
echo.
echo La release v1.7.7 est maintenant disponible sur GitHub!
echo.
pause
