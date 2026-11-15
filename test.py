#!/usr/bin/env python3
"""
Rekurzivně opraví PNG soubory, které pygame / pygbag nedokáže načíst.

- Podle hlaviček souboru zjistí skutečný formát (ne podle přípony).
- Soubory, které jsou ve skutečnosti JPEG, WebP, GIF nebo BMP, převede na PNG.
- Každý PNG přepíše jako standardní 8bitové RGBA PNG (odstraní neobvyklé varianty,
  např. 16bit, CMYK, paletu s poškozenou transparencí).
- Nečitelné soubory pouze vypíše.
- Původní soubory zálohuje do složky <nazev_slozky>_backup vedle cílové složky.

Použití:
    pip install pillow
    python fix_pngs.py <složka> [--dry-run] [--no-backup]
"""

import argparse
import os
import shutil
import sys
from collections import Counter
from pathlib import Path

from PIL import Image

PNG_MAGIC = b"\x89PNG\r\n\x1a\n"


def sniff(path: Path) -> str | None:
    """Vrátí skutečný formát souboru podle prvních bajtů, nebo None."""
    with open(path, "rb") as f:
        head = f.read(16)
    if head.startswith(PNG_MAGIC):
        return "png"
    if head.startswith(b"\xff\xd8\xff"):
        return "jpeg"
    if head[:4] == b"RIFF" and head[8:12] == b"WEBP":
        return "webp"
    if head[:6] in (b"GIF87a", b"GIF89a"):
        return "gif"
    if head[:2] == b"BM":
        return "bmp"
    return None


def fix_file(path: Path, root: Path, backup_dir: Path | None, dry_run: bool) -> str:
    kind = sniff(path)
    if kind is None:
        return "NEZNÁMÝ FORMÁT (hlavička nepatří k žádnému podporovanému obrázku)"

    try:
        with Image.open(path) as im:
            im.load()
            fixed = im.convert("RGBA")
    except Exception as e:
        return f"NEČITELNÝ, přeskočeno: {e}"

    note = "přepsáno jako standardní PNG" if kind == "png" else f"převedeno z {kind} na PNG"
    if dry_run:
        return f"[dry-run] {note}"

    if backup_dir is not None:
        dest = backup_dir / path.relative_to(root)
        dest.parent.mkdir(parents=True, exist_ok=True)
        if not dest.exists():
            shutil.copy2(path, dest)

    # Zápis do dočasného souboru a pak atomické nahrazení, aby nevznikl poloviční soubor.
    tmp = path.with_name(path.name + ".tmp")
    fixed.save(tmp, format="PNG")
    os.replace(tmp, path)
    return note


def main() -> None:
    ap = argparse.ArgumentParser(description="Opraví PNG soubory rekurzivně.")
    ap.add_argument("folder", help="složka, která se má projít")
    ap.add_argument("--dry-run", action="store_true", help="jen vypíše, co by se stalo")
    ap.add_argument("--no-backup", action="store_true", help="nezálohovat původní soubory")
    args = ap.parse_args()

    root = Path(args.folder).resolve()
    if not root.is_dir():
        sys.exit(f"Složka neexistuje: {root}")

    backup_dir = None
    if not args.no_backup and not args.dry_run:
        backup_dir = root.parent / (root.name + "_backup")

    files = sorted(
        p for p in root.rglob("*")
        if p.is_file() and p.suffix.lower() == ".png" and not p.name.endswith(".tmp")
    )
    print(f"Nalezeno PNG souborů: {len(files)}\n")

    stats = Counter()
    for path in files:
        result = fix_file(path, root, backup_dir, args.dry_run)
        rel = path.relative_to(root)
        status = "OK" if not result.startswith(("NEZNÁMÝ", "NEČITELNÝ")) else "CHYBA"
        stats[status] += 1
        print(f"[{status}] {rel}: {result}")

    print(f"\nHotovo. OK: {stats['OK']}, chyby: {stats['CHYBA']}")
    if backup_dir is not None and stats["OK"]:
        print(f"Originály jsou zálohované v: {backup_dir}")


if __name__ == "__main__":
    main()