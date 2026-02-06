@echo off
REM Build script for DestriChiffrage Installer
REM Compile l'installateur Windows avec Inno Setup

echo ========================================
echo Build DestriChiffrage Installer
echo ========================================
echo.

REM Vérifier que le build PyInstaller existe
if not exist "dist\DestriChiffrage.exe" (
    echo ERREUR : L'executable n'existe pas.
    echo Veuillez d'abord executer build.bat
    pause
    exit /b 1
)

REM Vérifier qu'Inno Setup est installé
set ISCC="C:\Program Files (x86)\Inno Setup 6\ISCC.exe"
if not exist %ISCC% (
    echo ERREUR : Inno Setup n'est pas installe.
    echo Telechargez-le depuis : https://jrsoftware.org/isdl.php
    pause
    exit /b 1
)

REM Compilation avec Inno Setup
echo.
echo Compilation de l'installateur...
%ISCC% installer.iss

REM Vérification
if exist "installer_output\DestriChiffrage-Setup-1.0.0.exe" (
    echo.
    echo ========================================
    echo Installateur cree avec succes !
    echo Fichier : installer_output\DestriChiffrage-Setup-1.0.0.exe
    echo ========================================
    echo.
    echo Vous pouvez maintenant distribuer cet installateur.
) else (
    echo.
    echo ========================================
    echo ERREUR : Creation de l'installateur echouee
    echo ========================================
)

pause
