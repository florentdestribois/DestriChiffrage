"""
Convertit icon_dc.svg en icon.ico
"""
import cairosvg
from PIL import Image
import os

# Convertir SVG en PNG (haute résolution)
print("Conversion SVG -> PNG...")
cairosvg.svg2png(
    url='assets/icon_dc.svg',
    write_to='assets/icon_dc_temp.png',
    output_width=512,
    output_height=512
)

# Ouvrir le PNG avec PIL
print("Création de l'icône multi-tailles...")
img = Image.open('assets/icon_dc_temp.png')

# Créer des versions à différentes tailles
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]

# Sauvegarder en ICO
img.save(
    'assets/icon.ico',
    format='ICO',
    sizes=sizes
)

# Nettoyer le fichier temporaire
os.remove('assets/icon_dc_temp.png')

print("✓ Icône créée avec succès : assets/icon.ico")
print(f"  Tailles incluses : {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
