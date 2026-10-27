# PANTHEON — Google Drive source snapshot

Complete local copy of the prepared asset pool from the Google Drive folder **ПАНТЕОН**.

- Source folder ID: `1EDzc6O5Hoxfymjmn9axY5zs9vJ9nJRVg`
- Source URL: <https://drive.google.com/drive/folders/1EDzc6O5Hoxfymjmn9axY5zs9vJ9nJRVg>
- Download date: 2026-10-27
- Asset count: **120 SVG files**
- Asset bytes: **1,787,320**
- MIME type: `image/svg+xml`
- Structure: the original Drive directory hierarchy is preserved.

## Folder inventory

| Drive-relative folder | Files | Bytes |
|---|---:|---:|
| `pantheon-svg` | 30 | 923,756 |
| `pantheon-svg-batch-2/amun` | 3 | 91,067 |
| `pantheon-svg-batch-2/aset` | 3 | 226,246 |
| `pantheon-svg-batch-2/bold-01` | 12 | 105,049 |
| `pantheon-svg-batch-2/bold-02` | 12 | 103,297 |
| `pantheon-svg-batch-2/bold-03` | 12 | 120,653 |
| `pantheon-svg-batch-2/faceted-01` | 12 | 112,194 |
| `pantheon-svg-batch-2/minimal-01` | 12 | 29,296 |
| `pantheon-svg-batch-2/minimal-02` | 12 | 29,975 |
| `pantheon-svg-batch-2/minimal-03` | 12 | 45,787 |
| **Total** | **120** | **1,787,320** |

## Verification

Run from the repository root:

```bash
python3 assets/svg/pantheon/verify_snapshot.py
```

The verifier checks the enumerated Drive folder structure, exact filename sets, per-folder byte totals, MIME type, XML/SVG validity, the grand total, and every file against the fixed MD5 and SHA-256 values in `manifest.csv`.

This is a source snapshot only. No SVG in this directory was redrawn, optimized, renamed, or otherwise modified after download.
