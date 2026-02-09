@echo off
cd /d "C:\Users\tt\Documents\Developpement logiciel\DestriChiffrage"
echo.
echo ========================================
echo RELEASE DestriChiffrage v1.7.11
echo ========================================
echo.
echo [1/2] Compilation PyInstaller...
py -m PyInstaller DestriChiffrage.spec --clean --noconfirm
if not exist "dist\DestriChiffrage.exe" (
    echo ERREUR: Compilation echouee!
    pause
    exit /b 1
)
echo OK: dist\DestriChiffrage.exe cree
echo.
echo [2/2] Creation installateur Inno Setup...
"C:\Program Files (x86)\Inno Setup 6\ISCC.exe" installer_simple.iss
if not exist "installer_output\DestriChiffrage-Setup-1.7.11.exe" (
    echo ERREUR: Installateur non cree!
    pause
    exit /b 1
)
echo OK: installer_output\DestriChiffrage-Setup-1.7.11.exe cree
echo.
echo ========================================
echo BUILD TERMINE AVEC SUCCES
echo ========================================
dir dist\DestriChiffrage.exe
dir installer_output\DestriChiffrage-Setup-1.7.11.exe
echo.
pause
