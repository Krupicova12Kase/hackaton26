

from pathlib import Path
from PIL import Image, UnidentifiedImageError

for p in Path(".").glob("*.png"):
    try:
        img = Image.open(p).convert("RGBA")
        img.save(p, "PNG")
        print("OK:", p)
    except UnidentifiedImageError:
        print("POŠKOZENO:", p)