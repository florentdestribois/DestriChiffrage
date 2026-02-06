"""
Crée l'icône DC directement avec PIL/Pillow
"""
from PIL import Image, ImageDraw, ImageFont
import os

# Créer une image 512x512 avec fond dégradé
size = 512
img = Image.new('RGB', (size, size))
draw = ImageDraw.Draw(img)

# Créer un dégradé de #AE9367 à #2E3544
color_start = (174, 147, 103)  # #AE9367
color_end = (46, 53, 68)       # #2E3544

for y in range(size):
    # Interpolation linéaire entre les deux couleurs
    ratio = y / size
    r = int(color_start[0] * (1 - ratio) + color_end[0] * ratio)
    g = int(color_start[1] * (1 - ratio) + color_end[1] * ratio)
    b = int(color_start[2] * (1 - ratio) + color_end[2] * ratio)
    draw.rectangle([(0, y), (size, y+1)], fill=(r, g, b))

# Arrondir les coins (optionnel - créer un masque)
radius = 80
mask = Image.new('L', (size, size), 0)
mask_draw = ImageDraw.Draw(mask)
mask_draw.rounded_rectangle([(0, 0), (size, size)], radius=radius, fill=255)
img.putalpha(mask)

# Convertir en RGBA pour le texte
if img.mode != 'RGBA':
    img = img.convert('RGBA')

draw = ImageDraw.Draw(img)

# Charger une police (utiliser une police système)
try:
    # Essayer Arial Bold
    font_large = ImageFont.truetype("arial.ttf", 200)
    font_small = ImageFont.truetype("arial.ttf", 50)
except:
    # Fallback sur la police par défaut
    font_large = ImageFont.load_default()
    font_small = ImageFont.load_default()

# Dessiner "DC" au centre
text_dc = "DC"
bbox = draw.textbbox((0, 0), text_dc, font=font_large)
text_width = bbox[2] - bbox[0]
text_height = bbox[3] - bbox[1]
x = (size - text_width) // 2
y = (size - text_height) // 2 - 20

draw.text((x, y), text_dc, fill='white', font=font_large)

# Dessiner "CHIFFRAGE" en bas
text_chiffrage = "CHIFFRAGE"
bbox2 = draw.textbbox((0, 0), text_chiffrage, font=font_small)
text_width2 = bbox2[2] - bbox2[0]
x2 = (size - text_width2) // 2
y2 = y + text_height + 80

draw.text((x2, y2), text_chiffrage, fill=(255, 255, 255, 200), font=font_small)

# Sauvegarder en PNG d'abord
temp_png = 'assets/icon_temp.png'
img.save(temp_png, 'PNG')

# Convertir en ICO avec plusieurs tailles
print("Création de l'icône multi-résolutions...")
img_png = Image.open(temp_png)

# Créer l'ICO avec plusieurs tailles
sizes = [(256, 256), (128, 128), (64, 64), (48, 48), (32, 32), (16, 16)]
img_png.save(
    'assets/icon.ico',
    format='ICO',
    sizes=sizes
)

# Nettoyer
os.remove(temp_png)

print("✓ Icône créée avec succès : assets/icon.ico")
print(f"  Style: Dégradé #AE9367 -> #2E3544")
print(f"  Texte: DC + CHIFFRAGE")
print(f"  Tailles: {', '.join([f'{s[0]}x{s[1]}' for s in sizes])}")
