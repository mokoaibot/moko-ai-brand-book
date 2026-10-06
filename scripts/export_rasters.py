#!/usr/bin/env python3
"""Export every SVG asset to downloadable PNG, JPG and WebP files.

SVG remains the source of truth. PNG and lossless WebP keep transparency.
JPG receives a light or dark background selected for the asset theme.
"""

from __future__ import annotations

import re
import shutil
import subprocess
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_ROOT = ROOT / "assets" / "svg"
EXPORT_ROOT = ROOT / "exports"

DARK_JPG = {
    "moko-ai-horus-horizontal-dark.svg",
    "moko-ai-horus-mark-mono.svg",
    "logo-horizontal-white.svg",
    "logo-mark-white.svg",
    "moko-ai-mono.svg",
}


def dimensions(path: Path) -> tuple[int, int]:
    root = ET.parse(path).getroot()
    values = [float(value) for value in root.attrib["viewBox"].replace(",", " ").split()]
    ratio = values[2] / values[3]
    if ratio >= 1.8:
        width = 2400
        height = round(width / ratio)
    elif ratio <= 0.55:
        height = 2048
        width = round(height * ratio)
    elif ratio >= 1:
        width = 2048
        height = round(width / ratio)
    else:
        height = 2048
        width = round(height * ratio)
    return width, height


def scaled_svg(source: Path, target: Path, width: int, height: int) -> None:
    content = source.read_text(encoding="utf-8")
    opening = re.search(r"<svg\b[^>]*>", content)
    if not opening:
        raise RuntimeError(f"Missing SVG root: {source}")
    tag = opening.group(0)
    if re.search(r'\bwidth="[^"]*"', tag):
        tag = re.sub(r'\bwidth="[^"]*"', f'width="{width}"', tag, count=1)
    else:
        tag = tag[:-1] + f' width="{width}">'
    if re.search(r'\bheight="[^"]*"', tag):
        tag = re.sub(r'\bheight="[^"]*"', f'height="{height}"', tag, count=1)
    else:
        tag = tag[:-1] + f' height="{height}">'
    target.write_text(content[: opening.start()] + tag + content[opening.end() :], encoding="utf-8")


def render(source: Path, png: Path, jpg: Path, webp: Path) -> None:
    width, height = dimensions(source)
    png.parent.mkdir(parents=True, exist_ok=True)
    jpg.parent.mkdir(parents=True, exist_ok=True)
    webp.parent.mkdir(parents=True, exist_ok=True)
    background = "#050505" if source.name in DARK_JPG else "#ffffff"

    with tempfile.TemporaryDirectory(prefix="moko-ai-export-") as directory:
        temporary_svg = Path(directory) / source.name
        scaled_svg(source, temporary_svg, width, height)
        subprocess.run([
            "magick", "-background", "none", str(temporary_svg),
            "-strip", f"PNG32:{png}",
        ], check=True)
        subprocess.run([
            "magick", "-background", background, str(temporary_svg),
            "-alpha", "remove", "-alpha", "off", "-quality", "92", "-strip", str(jpg),
        ], check=True)
        subprocess.run([
            "magick", "-background", "none", str(temporary_svg),
            "-define", "webp:lossless=true", "-quality", "100", "-strip", str(webp),
        ], check=True)


def main() -> None:
    if shutil.which("magick") is None:
        raise SystemExit("ImageMagick command 'magick' is required")

    files = sorted(SVG_ROOT.rglob("*.svg"))
    for source in files:
        relative = source.relative_to(SVG_ROOT)
        render(
            source,
            EXPORT_ROOT / "png" / relative.with_suffix(".png"),
            EXPORT_ROOT / "jpg" / relative.with_suffix(".jpg"),
            EXPORT_ROOT / "webp" / relative.with_suffix(".webp"),
        )
    print(f"Exported {len(files)} SVG assets to PNG, JPG and WebP ({len(files) * 3} files)")


if __name__ == "__main__":
    main()
