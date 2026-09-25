#!/usr/bin/env python3
"""Derive small wall-view images from the published local slab photographs.

The originals in static/images/slabs remain untouched and are used for inspection.
Masaki's three unowned, low-resolution reference scans are intentionally excluded.
"""

from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "static/images/slabs"
DESTINATION = ROOT / "static/images/slab-previews"


def main():
    DESTINATION.mkdir(parents=True, exist_ok=True)
    for source in sorted(SOURCE.iterdir()):
        if not source.is_file() or source.stem.endswith("_wanted"):
            continue
        with Image.open(source) as original:
            height = round(original.height * 720 / original.width)
            preview = original.convert("RGB").resize((720, height), Image.Resampling.LANCZOS)
            options = {"format": "WEBP", "quality": 83, "method": 6}
            if original.info.get("icc_profile"):
                options["icc_profile"] = original.info["icc_profile"]
            preview.save(DESTINATION / f"{source.stem}.webp", **options)


if __name__ == "__main__":
    main()
