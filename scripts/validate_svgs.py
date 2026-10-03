#!/usr/bin/env python3
"""Validate the approved MOKO AI SVG system using the standard library."""

from __future__ import annotations

import hashlib
import json
import re
import sys
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SVG_ROOT = ROOT / "assets" / "svg"
MANIFEST = ROOT / "manifest.json"
REFERENCE = SVG_ROOT / "source" / "moko-ai-horus-reference.svg"
REFERENCE_SHA256 = "b353fee987999584dc9e8bf025da6dc02586b9f0163b6354f4aeb2ba70d4abbd"

ALLOWED_COLORS = {
    # Approved MOKO AI mark and neutrals.
    "#f56a6a", "#ec5959", "#e34d4d", "#d94343", "#d64545", "#ce3d3d",
    "#c03838", "#b93636", "#b13232", "#050505", "#0a0a0a", "#34383c", "#6b7177",
    "#9ca3af", "#b8bdc2", "#f3f3f1", "#ffffff",
    # State colors.
    "#4caf7d", "#e0a33e", "#4a7fb5",
}
FORBIDDEN_TAGS = {"image", "script", "foreignObject", "linearGradient", "radialGradient", "filter", "pattern"}
HEX_COLOR = re.compile(r"#[0-9a-fA-F]{6}\b")
NUMBER = re.compile(r"^-?(?:\d+(?:\.\d*)?|\.\d+)$")
AI_TRANSFORM = "translate(210 232) scale(0.081 -0.081)"

EXPECTED_FACETS = {
    "moko-ai-horus-reference.svg": 24,
    "moko-ai-horus-mark.svg": 24,
    "moko-ai-horus-ring.svg": 24,
    "moko-ai-horus-ring-ai.svg": 24,
    "moko-ai-horus-horizontal-dark.svg": 24,
    "moko-ai-horus-horizontal-light.svg": 24,
    "moko-ai-primary-dark.svg": 24,
    "moko-ai-primary-light.svg": 24,
    "moko-ai-transparent.svg": 24,
    "moko-ai-online.svg": 24,
    "moko-ai-thinking.svg": 24,
    "moko-ai-action.svg": 24,
    "moko-ai-horus-mark-mono.svg": 0,
    "moko-ai-mono.svg": 0,
    "moko-ai-small.svg": 0,
}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def error(errors: list[str], path: Path, message: str) -> None:
    errors.append(f"{path.relative_to(ROOT)}: {message}")


def validate_file(path: Path, errors: list[str]) -> None:
    try:
        root = ET.parse(path).getroot()
    except ET.ParseError as exc:
        error(errors, path, f"invalid XML: {exc}")
        return

    if local_name(root.tag) != "svg":
        error(errors, path, "root element must be <svg>")
        return

    view_box = root.attrib.get("viewBox")
    if not view_box:
        error(errors, path, "missing viewBox")
    else:
        values = view_box.replace(",", " ").split()
        if len(values) != 4 or not all(NUMBER.match(value) for value in values):
            error(errors, path, f"invalid viewBox: {view_box!r}")
        elif float(values[2]) <= 0 or float(values[3]) <= 0:
            error(errors, path, "viewBox width and height must be positive")

    elements = list(root.iter())
    names = [local_name(element.tag) for element in elements]
    ids = {element.attrib.get("id") for element in elements if element.attrib.get("id")}

    if "title" not in names:
        error(errors, path, "missing accessible <title>")
    if "desc" not in names:
        error(errors, path, "missing accessible <desc>")

    for element in elements:
        name = local_name(element.tag)
        if name in FORBIDDEN_TAGS:
            error(errors, path, f"forbidden <{name}> element")
        for key, value in element.attrib.items():
            if local_name(key) == "href" and ("://" in value or value.startswith("data:")):
                error(errors, path, f"external or embedded href is forbidden: {value[:80]}")
            for color in HEX_COLOR.findall(value):
                if color.lower() not in ALLOWED_COLORS:
                    error(errors, path, f"unapproved color {color}")

    if ("avatars" in path.parts or "logo" in path.parts) and "text" in names:
        error(errors, path, "logos and avatars must use outlined paths, not live <text>")

    expected = EXPECTED_FACETS.get(path.name)
    if expected is not None:
        actual = names.count("polygon")
        if actual != expected:
            error(errors, path, f"expected {expected} polygon facets, found {actual}")
        if expected == 24 and path.name != "moko-ai-horus-reference.svg" and "horus-lowpoly-mark" not in ids:
            error(errors, path, "missing horus-lowpoly-mark component")
        if expected == 0 and path.name not in {"moko-ai-horus-mark-mono.svg"} and "horus-silhouette-mark" not in ids:
            error(errors, path, "missing horus-silhouette-mark component")

    ring_assets = {
        "moko-ai-horus-ring.svg", "moko-ai-horus-ring-ai.svg",
        "moko-ai-primary-dark.svg", "moko-ai-primary-light.svg", "moko-ai-mono.svg",
        "moko-ai-small.svg", "moko-ai-transparent.svg", "moko-ai-online.svg",
        "moko-ai-thinking.svg", "moko-ai-action.svg",
    }
    if path.name in ring_assets and "moko-red-ring" not in ids:
        error(errors, path, "missing approved ring component")

    ai_assets = ring_assets - {"moko-ai-horus-ring.svg", "moko-ai-small.svg"}
    if path.name in ai_assets:
        ai = next((element for element in elements if element.attrib.get("id") == "ai-signature"), None)
        if ai is None:
            error(errors, path, "missing outlined AI signature")
        elif ai.attrib.get("transform") != AI_TRANSFORM:
            error(errors, path, f"unexpected AI transform {ai.attrib.get('transform')!r}")

    if path.name == "moko-ai-small.svg" and "ai-signature" in ids:
        error(errors, path, "compact avatar must omit AI below 64 px")


def validate_reference(errors: list[str]) -> None:
    try:
        digest = hashlib.sha256(REFERENCE.read_bytes()).hexdigest()
    except OSError as exc:
        errors.append(f"reference: cannot read approved source: {exc}")
        return
    if digest != REFERENCE_SHA256:
        errors.append(f"reference: approved source hash changed: {digest}")


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

    actual = {path.resolve() for path in SVG_ROOT.rglob("*.svg")}
    for path in sorted(actual - listed):
        errors.append(f"manifest.json: unlisted SVG {path.relative_to(ROOT)}")
    for path in sorted(listed - actual):
        if path.suffix.lower() == ".svg":
            errors.append(f"manifest.json: listed SVG not found under assets/svg: {path}")


def main() -> int:
    errors: list[str] = []
    files = sorted(SVG_ROOT.rglob("*.svg"))
    if not files:
        print("ERROR: no SVG files found", file=sys.stderr)
        return 1

    for path in files:
        validate_file(path, errors)
    validate_reference(errors)
    validate_manifest(errors)

    if errors:
        for item in errors:
            print(f"ERROR {item}", file=sys.stderr)
        print(f"\nFAILED: {len(errors)} error(s)", file=sys.stderr)
        return 1

    print(f"OK: {len(files)} SVG files validated; approved reference hash intact")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
