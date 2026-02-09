@echo off
cd /d "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
echo.
echo === Verification Python ===
py --version
echo.
echo === Verification PyInstaller ===
py -m pip show pyinstaller
echo.
echo === Lancement du Build ===
echo.
py -m PyInstaller DestriChiffrage.spec --noconfirm
echo.
echo === Resultat ===
if exist "dist\DestriChiffrage.exe" (
    echo SUCCESS: dist\DestriChiffrage.exe cree!
    dir dist\DestriChiffrage.exe
) else (
    echo ECHEC: exe non trouve
)
echo.
pause
