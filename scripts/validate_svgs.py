#!/usr/bin/env python3
"""Validate MOKO AI SVG masters using only Python's standard library."""

from __future__ import annotations

import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_ROOT = ROOT / "assets" / "svg"
MANIFEST = ROOT / "manifest.json"

ALLOWED_COLORS = {
    "#d64545", "#b93636", "#050505", "#0a0a0a", "#6b7177", "#9ca3af",
    "#ffffff", "#34383c", "#f3f3f1", "#b8bdc2", "#4caf7d", "#e0a33e",
    "#4a7fb5",
}
FORBIDDEN_TAGS = {"image", "script", "foreignObject", "linearGradient", "radialGradient", "filter"}
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)$")

OFFICIAL_PATHS = {
    "M160 4.27406L271 154.274L176 192.274L160 4.27406Z",
    "M94.8938 0L127.894 44L101.894 82L94.8938 0Z",
    "M160 4.27406L176 192.274L53 163.274L160 4.27406Z",
    "M93.5 2.27405L58 147.274L0 132.274L93.5 2.27405Z",
    "M95 0.274048L102 81.774L58 147.274L0 132.274L95 0.274048Z",
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def validate_file(path: Path, errors: list[str], warnings: list[str]) -> None:
    try:
        tree = ET.parse(path)
    except ET.ParseError as exc:
        error(errors, path, f"invalid XML: {exc}")
        return

    root = tree.getroot()
    if local_name(root.tag) != "svg":
        error(errors, path, "root element must be <svg>")
        return

    view_box = root.attrib.get("viewBox")
    if not view_box:
        error(errors, path, "missing viewBox")
    else:
        values = view_box.replace(",", " ").split()
        if len(values) != 4 or not all(NUMBER.match(v) for v in values):
            error(errors, path, f"invalid viewBox: {view_box!r}")
        elif float(values[2]) <= 0 or float(values[3]) <= 0:
            error(errors, path, "viewBox width and height must be positive")

    names = [local_name(el.tag) for el in root.iter()]
    if "title" not in names:
        error(errors, path, "missing accessible <title>")
    if "desc" not in names:
        error(errors, path, "missing accessible <desc>")

    for el in root.iter():
        name = local_name(el.tag)
        if name in FORBIDDEN_TAGS:
            error(errors, path, f"forbidden <{name}> element")
        for key, value in el.attrib.items():
            if local_name(key) == "href" and ("://" in value or value.startswith("data:")):
                error(errors, path, f"external or embedded href is forbidden: {value[:80]}")
            for color in HEX_COLOR.findall(value):
                if color.lower() not in ALLOWED_COLORS:
                    error(errors, path, f"unapproved color {color}")

    # Avatars must not rely on fonts or live text.
    if "avatars" in path.parts and "text" in names:
        error(errors, path, "avatars must use paths, not live <text>")

    # Every avatar must embed the exact official geometry.
    if "avatars" in path.parts:
        ds = {el.attrib.get("d") for el in root.iter() if local_name(el.tag) == "path"}
        missing = OFFICIAL_PATHS - ds
        if missing:
            error(errors, path, f"official MOKO path geometry missing ({len(missing)} path(s))")

    if "templates" in path.parts and "text" in names:
        warnings.append(f"{path.relative_to(ROOT)}: live text is intentional; outline only in an export copy")


def validate_manifest(errors: list[str]) -> None:
    try:
        data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"manifest.json: cannot read: {exc}")
        return

    listed: set[Path] = set()
    ids: set[str] = set()
    for item in data.get("assets", []):
        asset_id = item.get("id")
        raw_path = item.get("path")
        if not asset_id or not raw_path:
            errors.append("manifest.json: every asset needs id and path")
            continue
        if asset_id in ids:
            errors.append(f"manifest.json: duplicate id {asset_id}")
        ids.add(asset_id)
        asset_path = ROOT / raw_path
        listed.add(asset_path.resolve())
        if not asset_path.exists():
            errors.append(f"manifest.json: missing file {raw_path}")

    actual = {p.resolve() for p in SVG_ROOT.rglob("*.svg")}
    for path in sorted(actual - listed):
        errors.append(f"manifest.json: unlisted SVG {path.relative_to(ROOT)}")
    for path in sorted(listed - actual):
        if path.suffix.lower() == ".svg":
            errors.append(f"manifest.json: listed SVG not found under assets/svg: {path}")


def main() -> int:
    errors: list[str] = []
    warnings: list[str] = []
    files = sorted(SVG_ROOT.rglob("*.svg"))
    if not files:
        print("ERROR: no SVG files found", file=sys.stderr)
        return 1

    for path in files:
        validate_file(path, errors, warnings)
    validate_manifest(errors)

    for item in warnings:
        print(f"WARN  {item}")
    if errors:
        for item in errors:
            print(f"ERROR {item}", file=sys.stderr)
        print(f"\nFAILED: {len(errors)} error(s), {len(warnings)} warning(s)", file=sys.stderr)
        return 1

    print(f"OK: {len(files)} SVG files validated; {len(warnings)} informational warning(s)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
