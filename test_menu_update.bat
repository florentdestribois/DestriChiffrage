@echo off
REM Script pour tester le menu de mise à jour avec logs

echo ========================================
echo Test Menu Mise a Jour - DestriChiffrage
echo ========================================
echo.
echo L'application va se lancer.
echo Les messages de debug apparaitront dans cette console.
echo.
echo Etapes :
echo 1. Attendre que l'application se lance
echo 2. Cliquer sur menu "Aide"
echo 3. Cliquer sur "Verifier les mises a jour..."
echo 4. Observer les messages [DEBUG] dans cette console
echo.
echo ========================================
echo.

cd /d "%~dp0"
python src\main.py

pause
