# -*- mode: python ; coding: utf-8 -*-
"""
DestriChiffrage - PyInstaller Spec File
Génère un exécutable Windows standalone
"""

import os
from PyInstaller.utils.hooks import collect_data_files

block_cipher = None

# Collecte des fichiers de données
datas = [
    ('src/assets', 'src/assets'),  # logo.png, pdf.png
    ('assets/icon.ico', 'assets'),  # icon.ico
]

# Analyse des dépendances
a = Analysis(
    ['src/main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PIL._tkinter_finder',
        'openpyxl',
        'requests',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'matplotlib',
        'numpy',
        'pandas',
        'scipy',
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

# Création de l'archive Python
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

# Création de l'exécutable
exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='DestriChiffrage',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=False,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # Pas de console, interface graphique uniquement
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon='assets/icon.ico',
    version_file=None,
)
