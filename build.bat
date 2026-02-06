@echo off
REM Build script for DestriChiffrage
REM Compile l'application en .exe avec PyInstaller

echo ========================================
echo Build DestriChiffrage avec PyInstaller
echo ========================================
echo.

REM Nettoyage des anciens builds
echo Nettoyage des anciens builds...
if exist "dist" rmdir /s /q "dist"
if exist "build" rmdir /s /q "build"

REM Build avec PyInstaller
echo.
echo Compilation avec PyInstaller...
pyinstaller DestriChiffrage.spec

REM Vérification
if exist "dist\DestriChiffrage.exe" (
    echo.
    echo ========================================
    echo Build reussi !
    echo Executable : dist\DestriChiffrage.exe
    echo ========================================
    echo.
    echo Creation du dossier data...
    if not exist "dist\data" mkdir "dist\data"
    if not exist "dist\data\Fiches_techniques" mkdir "dist\data\Fiches_techniques"
    if not exist "dist\data\Devis_fournisseur" mkdir "dist\data\Devis_fournisseur"
    echo.
    echo L'executable est pret dans le dossier dist\
) else (
    echo.
    echo ========================================
    echo ERREUR : Build echoue
    echo ========================================
)

pause
