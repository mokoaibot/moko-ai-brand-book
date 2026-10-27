#!/usr/bin/env python3
"""Verify the local PANTHEON snapshot against the 2026-10-27 Drive inventory."""

from __future__ import annotations

import csv
import hashlib
import mimetypes
from pathlib import Path
import sys
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parent

NUMBERED_GODS = (
    "anubis",
    "bastet",
    "hathor",
    "horus",
    "maat",
    "osiris",
    "ra",
    "sekhmet",
    "set",
    "thoth",
)
STYLE_GODS = (
    "amun",
    "anubis",
    "bastet",
    "hathor",
    "horus",
    "isis",
    "maat",
    "osiris",
    "ra",
    "sekhmet",
    "set",
    "thoth",
)

# Counts and byte totals taken from Drive's file metadata during enumeration.
EXPECTED = {
    "pantheon-svg": {
        "names": {f"{god}-{n:02d}.svg" for god in NUMBERED_GODS for n in range(1, 4)},
        "bytes": 923_756,
    },
    "pantheon-svg-batch-2/amun": {
        "names": {f"amun-{n:02d}.svg" for n in range(1, 4)},
        "bytes": 91_067,
    },
    "pantheon-svg-batch-2/aset": {
        "names": {f"aset-{n:02d}.svg" for n in range(1, 4)},
        "bytes": 226_246,
    },
    "pantheon-svg-batch-2/bold-01": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 105_049,
    },
    "pantheon-svg-batch-2/bold-02": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 103_297,
    },
    "pantheon-svg-batch-2/bold-03": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 120_653,
    },
    "pantheon-svg-batch-2/faceted-01": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 112_194,
    },
    "pantheon-svg-batch-2/minimal-01": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 29_296,
    },
    "pantheon-svg-batch-2/minimal-02": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 29_975,
    },
    "pantheon-svg-batch-2/minimal-03": {
        "names": {f"{god}.svg" for god in STYLE_GODS},
        "bytes": 45_787,
    },
}


def digest(path: Path, algorithm: str) -> str:
    h = hashlib.new(algorithm)
    with path.open("rb") as src:
        for chunk in iter(lambda: src.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def main() -> int:
    errors: list[str] = []
    assets: list[Path] = []

    expected_dirs = set(EXPECTED)
    actual_dirs = {
        str(path.parent.relative_to(ROOT))
        for path in ROOT.rglob("*.svg")
    }
    if actual_dirs != expected_dirs:
        errors.append(
            f"directory set differs: missing={sorted(expected_dirs - actual_dirs)}, "
            f"extra={sorted(actual_dirs - expected_dirs)}"
        )

    for relative_dir, expected in EXPECTED.items():
        folder = ROOT / relative_dir
        files = sorted(folder.glob("*.svg"))
        actual_names = {p.name for p in files}
        expected_names = expected["names"]
        if actual_names != expected_names:
            errors.append(
                f"{relative_dir}: missing={sorted(expected_names - actual_names)}, "
                f"extra={sorted(actual_names - expected_names)}"
            )
        actual_bytes = sum(p.stat().st_size for p in files)
        if actual_bytes != expected["bytes"]:
            errors.append(
                f"{relative_dir}: {actual_bytes} bytes, expected {expected['bytes']}"
            )
        assets.extend(files)

    for path in assets:
        detected = mimetypes.guess_type(path.name)[0]
        if detected != "image/svg+xml":
            errors.append(f"{path.relative_to(ROOT)}: MIME {detected!r}")
        try:
            root_element = ET.parse(path).getroot()
            if root_element.tag not in ("svg", "{http://www.w3.org/2000/svg}svg"):
                errors.append(
                    f"{path.relative_to(ROOT)}: XML root is {root_element.tag!r}"
                )
        except Exception as exc:
            errors.append(f"{path.relative_to(ROOT)}: invalid XML/SVG: {exc}")

    manifest_path = ROOT / "manifest.csv"
    try:
        with manifest_path.open(newline="", encoding="utf-8") as src:
            rows = list(csv.DictReader(src))
    except OSError as exc:
        errors.append(f"cannot read fixed checksum manifest: {exc}")
        rows = []

    if len(rows) != 120:
        errors.append(f"manifest rows: {len(rows)}, expected 120")
    indexed = {row.get("relative_path", ""): row for row in rows}
    actual_relative = {path.relative_to(ROOT).as_posix() for path in assets}
    if set(indexed) != actual_relative:
        errors.append(
            f"manifest paths differ: missing={sorted(actual_relative - set(indexed))}, "
            f"extra={sorted(set(indexed) - actual_relative)}"
        )
    for path in assets:
        relative = path.relative_to(ROOT).as_posix()
        row = indexed.get(relative)
        if row is None:
            continue
        if row.get("mime_type") != "image/svg+xml":
            errors.append(f"{relative}: manifest MIME is {row.get('mime_type')!r}")
        try:
            recorded_size = int(row.get("size_bytes", "-1"))
        except ValueError:
            recorded_size = -1
        if path.stat().st_size != recorded_size:
            errors.append(
                f"{relative}: size {path.stat().st_size}, manifest {recorded_size}"
            )
        if digest(path, "md5") != row.get("md5"):
            errors.append(f"{relative}: MD5 differs from fixed manifest")
        if digest(path, "sha256") != row.get("sha256"):
            errors.append(f"{relative}: SHA-256 differs from fixed manifest")

    total_bytes = sum(p.stat().st_size for p in assets)
    expected_bytes = sum(int(entry["bytes"]) for entry in EXPECTED.values())
    if len(assets) != 120:
        errors.append(f"total files: {len(assets)}, expected 120")
    if total_bytes != expected_bytes or expected_bytes != 1_787_320:
        errors.append(
            f"total bytes: local={total_bytes}, Drive inventory={expected_bytes}, "
            "expected grand total=1787320"
        )

    print(f"SVG assets: {len(assets)}")
    print(f"Asset bytes: {total_bytes}")
    print("MIME type: image/svg+xml")
    print(f"Manifest: {manifest_path.relative_to(ROOT)}")
    if errors:
        print(f"FAILED ({len(errors)} issue(s))")
        for error in errors:
            print(f"- {error}")
        return 1
    print("PASS: local snapshot matches the enumerated Drive inventory")
    return 0


if __name__ == "__main__":
    sys.exit(main())
