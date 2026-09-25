#!/usr/bin/env python3
"""Derive small wall-view images from the published local slab photographs.

The originals in static/images/slabs remain untouched and are used for inspection.
Masaki's three unowned, low-resolution reference scans are intentionally excluded.
"""

from io import BytesIO
from pathlib import Path
import argparse

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "static/images/slabs"
DESTINATION = ROOT / "static/images/slab-previews"


def main(check=False):
    if not check:
        DESTINATION.mkdir(parents=True, exist_ok=True)
    expected = set()
    failures = []
    for source in sorted(SOURCE.iterdir()):
        if not source.is_file() or source.stem.endswith("_wanted"):
            continue
        with Image.open(source) as original:
            options = {"format": "WEBP", "quality": 83, "method": 6}
            if original.info.get("icc_profile"):
                options["icc_profile"] = original.info["icc_profile"]
            for width in (720, 1080):
                if original.width < width:
                    continue
                height = round(original.height * width / original.width)
                preview = original.convert("RGB").resize((width, height), Image.Resampling.LANCZOS)
                suffix = "" if width == 720 else "-1080"
                target = DESTINATION / f"{source.stem}{suffix}.webp"
                expected.add(target.name)
                if check:
                    buffer = BytesIO()
                    preview.save(buffer, **options)
                    if not target.is_file() or target.read_bytes() != buffer.getvalue():
                        failures.append(f"stale or missing preview: {target.name}")
                else:
                    preview.save(target, **options)
    if check:
        for extra in sorted({path.name for path in DESTINATION.glob("*.webp")} - expected):
            failures.append(f"orphan preview: {extra}")
        for failure in failures:
            print(failure)
    return 1 if failures else 0


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--check", action="store_true", help="fail if published previews differ from their originals")
    args = parser.parse_args()
    raise SystemExit(main(check=args.check))
