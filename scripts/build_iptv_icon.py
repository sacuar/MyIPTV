#!/usr/bin/env python3
"""Create a multi-size Windows icon from the approved BANG IPTV artwork.

Used by the Windows PyInstaller build. Requires Pillow (requirements-v4.txt).
"""
from pathlib import Path
from PIL import Image


def build(source=None, destination=None):
    root = Path(__file__).resolve().parents[1]
    source = Path(source) if source else root / "assets" / "iptv_icon.png"
    destination = Path(destination) if destination else root / "assets" / "iptv_icon.ico"
    destination.parent.mkdir(parents=True, exist_ok=True)
    with Image.open(source) as image:
        image = image.convert("RGBA").resize((256, 256), Image.Resampling.LANCZOS)
        image.save(
            destination, format="ICO",
            sizes=[(16, 16), (24, 24), (32, 32), (48, 48),
                   (64, 64), (128, 128), (256, 256)],
        )
    with Image.open(destination) as icon:
        if icon.format != "ICO" or icon.size != (256, 256):
            raise RuntimeError("Windows icon build failed")
    print(f"Created Windows icon: {destination}")
    return destination


if __name__ == "__main__":
    build()
