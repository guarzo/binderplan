#!/usr/bin/env python3
"""Validate the photographed Holding manifest and reproduce locally stored crops.

Usage: python scripts/holding_binder.py --check|--write
--write validates the evidence first, then overwrites only listed local WebP assets.
"""

import argparse
import hashlib
import re
import tempfile
from collections import Counter
from pathlib import Path

import yaml
from PIL import Image

try:
    import pillow_heif
except ImportError:
    pillow_heif = None

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = "docs/evidence/2026-09-24/holding-sort-completed"
CATALOG_ARCHIVE = "docs/evidence/2026-09-24/holding-catalog-images"
# Reuse is restricted to independently reviewed, identical printings in the canonical image manifest.
CANONICAL_COPIES = {
    "holding-p04-01": "hoopa-02", "holding-p04-02": "snorlax-02",
    "holding-p04-03": "ursaring-02", "holding-p08-02": "kasumis-tears-01",
    "holding-p08-03": "dratini-02", "holding-p08-04": "rockets-trap-01",
    "holding-p08-05": "ns-plan-01", "holding-p10-02": "misdreavus-01",
    "holding-p09-05": "eevee-01",
}
SIZES = (4284, 5712)
OCCUPANCY = [6, 9, 9, 9, 5, 8, 9, 9, 9, 1, 9, 7, 6, 4]
POSITIONS = ("upper-left", "upper-right", "middle-left", "middle-right", "lower-centre")
COUNTS = {
    ("Review", "EDGE Watches"): 6,
    ("Review", "Existing-theme EDGE"): 6,
    ("Review", "REDUNDANT"): 24,
    ("Keeper", "Personal"): 1,
    ("Keeper", "Beautiful Misfits"): 8,
    ("Keeper", "Heritage"): 28,
    ("Keeper", "Species Studies"): 27,
    ("Trade", "Actively available"): 5,
}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def verified_sources(root):
    """Check every archived original, not only files referenced by the manifest."""
    checksums = root / ARCHIVE / "SHA256SUMS"
    entries = dict(line.split("  ", 1) for line in checksums.read_text().splitlines())
    require(len(entries) == 16, "archive checksum entry count must be 16")
    expected = {f"{ARCHIVE}/IMG_{number}.HEIC" for number in range(7133, 7148)}
    expected.add(f"{ARCHIVE}/Holding.pdf")
    require(set(entries.values()) == expected, "archive checksum listing differs from expected originals")
    for digest, path in entries.items():
        require(hashlib.sha256((root / path).read_bytes()).hexdigest() == digest, f"archive changed: {path}")


def verified_catalog(root, expected_paths):
    if not expected_paths:
        return {}
    checksums = root / CATALOG_ARCHIVE / "SHA256SUMS"
    require(checksums.is_file(), "catalog archive SHA256SUMS missing")
    entries = {}
    for line in checksums.read_text().splitlines():
        digest, separator, path = line.partition("  ")
        require(separator and re.fullmatch(r"[0-9a-f]{64}", digest) and path not in entries,
                "invalid catalog archive SHA256SUMS")
        entries[path] = digest
    require(set(entries) == expected_paths, "catalog archive listing differs from exact-image originals")
    actual_paths = {f"{CATALOG_ARCHIVE}/{path.name}" for path in (root / CATALOG_ARCHIVE).glob("*.webp")}
    require(actual_paths == expected_paths, "catalog archive contains unlisted or missing originals")
    for path, digest in entries.items():
        require(path.startswith(CATALOG_ARCHIVE + "/") and ".." not in Path(path).parts,
                f"catalog original outside archive: {path}")
        source = root / path
        require(source.is_file() and hashlib.sha256(source.read_bytes()).hexdigest() == digest,
                f"catalog archive original changed or missing: {path}")
    require((root / CATALOG_ARCHIVE / "README.md").is_file(), "catalog archive provenance README missing")
    return entries


def catalog_bytes(original):
    """Produce a bounded local WebP from an archived, byte-for-byte upstream original."""
    from io import BytesIO

    with Image.open(original) as opened:
        require(opened.width >= 200 and opened.height >= 250, f"catalog original is too small: {original}")
        image = opened.convert("RGB")
        image.thumbnail((640, 900), Image.Resampling.LANCZOS)
    output = BytesIO()
    image.save(output, "WEBP", quality=86, method=5)
    return output.getvalue()


def crop_bytes(source, box):
    """Use one fixed encoder for both --write and --check; never alter originals."""
    from io import BytesIO

    with Image.open(source) as opened:
        require(opened.size == SIZES, f"unexpected source dimensions: {source}")
        card = opened.convert("RGB").crop(tuple(box))
    output = BytesIO()
    card.save(output, "WEBP", quality=86, method=5)
    return output.getvalue()


def validate(data, root=ROOT, *, check_assets=True, write_assets=False):
    root = Path(root)
    require(pillow_heif is not None, "pillow_heif is required to read archived HEIC originals")
    pillow_heif.register_heif_opener()
    require(data["version"] == 1 and data["evidence_date"] == "2026-09-24", "manifest version/date")
    require([str(page["id"]) for page in data["pages"]] == [str(i) for i in range(7133, 7147)], "page order must follow final photographs")
    require([item["photo_position"] for item in data["top_loaders"]] == list(POSITIONS), "Trade photo positions differ")
    verified_sources(root)
    canonical = yaml.safe_load((root / "data/card-images.yaml").read_text())["cards"]
    seen_ids, seen_refs, seen_assets = set(), set(), set()
    expected_catalog_paths = set()
    catalog_assets = []
    catalog_provenance = []
    rows = []
    source_cards = {}
    generated = []
    for page, expected_count in zip(data["pages"], OCCUPANCY):
        source = f"{ARCHIVE}/IMG_{page['id']}.HEIC"
        require(page["source_path"] == source, f"wrong page source: {page['id']}")
        slots = page["pockets"]
        require(len(slots) == 9 and [slot["position"] for slot in slots] == list(range(1, 10)), f"page {page['id']} needs all nine ordered slots")
        require(sum("card" in slot for slot in slots) == expected_count, f"wrong page {page['id']} occupancy")
        for slot in slots:
            require(("card" in slot) != (slot.get("empty") is True), f"page {page['id']} slot {slot['position']} ambiguous")
            if "card" in slot:
                rows.append(slot["card"])
                source_cards.setdefault(source, []).append(slot["card"])
    trade_source = f"{ARCHIVE}/IMG_7147.HEIC"
    for item in data["top_loaders"]:
        require("position" not in item and "pockets" not in item, "top loader is not a binder pocket")
        rows.append(item["card"])
        source_cards.setdefault(trade_source, []).append(item["card"])
    require(len(rows) == 105, "expected 100 pockets and five top loaders")
    require(Counter((card["status"], card["subsection"]) for card in rows) == COUNTS, "sort totals differ from owner-confirmed reconciliation")
    for source, cards in source_cards.items():
        source_image = root / source
        with Image.open(source_image) as image:
            require(image.size == SIZES, f"unexpected dimensions: {source}")
        for card in cards:
            key = card["id"]
            ref = card["observation_ref"]
            image = card["image"]
            placement = card["placement"]
            require(isinstance(key, str) and re.fullmatch(r"holding-[a-z0-9]+(?:-[a-z0-9]+)*", key) and key not in seen_ids, f"invalid/duplicate card key: {key}")
            require(isinstance(ref, str) and ref not in seen_refs and (ref.startswith("HB-P") or ref.startswith("observed-")), f"invalid observation reference: {ref}")
            seen_ids.add(key)
            seen_refs.add(ref)
            require(isinstance(card["name"], str) and card["name"], f"missing name: {key}")
            require(card["identity_confidence"] in ("high", "medium", "limited"), f"invalid confidence: {key}")
            require(type(card["availability"]) is bool and card["availability"] == (card["status"] == "Trade"), f"availability/status conflict: {key}")
            require(placement == {"type": "final-photo", "source_path": source, "observed_on": "2026-09-24"}, f"placement evidence: {key}")
            require(image.get("classification") in ("photo-crop", "exact") and image.get("source_path") == source,
                    f"image provenance: {key}")
            require(image.get("reviewed") is True, f"unreviewed image may not be published: {key}")
            if "note" in image:
                require(isinstance(image["note"], str) and bool(image["note"].strip()), f"empty image quality note: {key}")
            box = image["crop_box"]
            require(isinstance(box, list) and len(box) == 4 and all(type(v) is int for v in box), f"invalid crop box: {key}")
            x0, y0, x1, y1 = box
            require(0 <= x0 < x1 <= SIZES[0] and 0 <= y0 < y1 <= SIZES[1], f"crop outside original: {key}")
            require(600 <= x1 - x0 <= 1600 and 900 <= y1 - y0 <= 1900, f"unexpected crop dimensions: {key}")
            crop_asset = f"assets/images/holding/{key}.webp"
            require(image.get("crop_asset_path", crop_asset) == crop_asset, f"invalid crop fallback path: {key}")
            crop_path = root / crop_asset
            require(crop_path.resolve().parent == (root / "assets/images/holding").resolve(), f"crop path escapes Holding directory: {key}")
            if check_assets or write_assets:
                encoded = crop_bytes(source_image, box)
                if write_assets:
                    generated.append((crop_path, encoded))
                else:
                    require(crop_path.is_file() and crop_path.read_bytes() == encoded, f"missing/stale crop: {crop_asset}")
            asset = image["asset_path"]
            require(isinstance(asset, str) and asset not in seen_assets, f"duplicate/invalid local asset path: {key}")
            seen_assets.add(asset)
            if image["classification"] == "photo-crop":
                require(asset == crop_asset and not any(field in image for field in
                        ("provider", "upstream_id", "canonical_id", "original_path", "source_url")),
                        f"photo crop may not imply a catalog source: {key}")
                continue
            require(card.get("language") in ("EN", "JP", "CN") and bool(card.get("set") or card.get("number")),
                    f"exact image needs language and catalogued set/number: {key}")
            require(image.get("crop_asset_path") == crop_asset, f"exact image needs its reproducible crop fallback: {key}")
            require(image.get("provider") in ("doubleholo", "tcgdex") and isinstance(image.get("upstream_id"), str)
                    and bool(image["upstream_id"].strip()), f"unsourced exact provider/id: {key}")
            url = image.get("source_url")
            require(isinstance(url, str) and url.startswith("https://") and url.find("/", 8) > 8,
                    f"exact image requires HTTPS source_url: {key}")
            note = image.get("note", "")
            require(isinstance(note, str) and not re.search(r"\b(photo|glare|clipped|clips)\b", note, re.IGNORECASE),
                    f"exact image note must not describe fallback photo/glare: {key}")
            if "fallback_crop" in image:
                fallback = image["fallback_crop"]
                require(isinstance(fallback, dict) and isinstance(fallback.get("photo_note"), str) and
                        bool(fallback["photo_note"].strip()), f"invalid fallback photo note: {key}")
            if "canonical_id" in image:
                canonical_id = image["canonical_id"]
                require(CANONICAL_COPIES.get(key) == canonical_id and canonical_id in canonical,
                        f"canonical printing not approved for holding copy: {key}")
                record = canonical[canonical_id]
                require(record.get("classification") == "exact" and record.get("reviewed") is True and
                        all(image[field] == record.get(field) for field in ("asset_path", "provider", "upstream_id", "source_url")) and
                        (root / asset).is_file(), f"canonical exact image does not match reviewed printing: {key}")
                require("original_path" not in image, f"canonical exact image must not invent a source archive: {key}")
            else:
                require(asset == f"assets/images/holding/catalog/{key}.webp", f"exact asset must be local catalog WebP: {key}")
                expected_url = ("https://navythaxplgdibyahpqb.supabase.co/storage/v1/object/public/"
                                f"card-images/card_images/{image['upstream_id']}/primary.webp")
                require(image["provider"] == "doubleholo" and url == expected_url,
                        f"exact source_url does not match DoubleHolo provider provenance: {key}")
                catalog_provenance.append(f"| `{key}` | `{image['upstream_id']}` | {url} | `{ref.removeprefix('HB-')}` |")
                original = f"{CATALOG_ARCHIVE}/{key}.webp"
                require(image.get("original_path") == original, f"unarchived catalog original: {key}")
                expected_catalog_paths.add(original)
                catalog_assets.append((root / original, root / asset))
    verified_catalog(root, expected_catalog_paths)
    if catalog_provenance:
        readme = (root / CATALOG_ARCHIVE / "README.md").read_text()
        require(all(row in readme for row in catalog_provenance), "catalog archive README missing per-image source provenance")
    if check_assets or write_assets:
        for source, path in catalog_assets:
            encoded = catalog_bytes(source)
            if write_assets:
                generated.append((path, encoded))
            else:
                require(path.is_file() and path.read_bytes() == encoded, f"missing/stale exact derivative: {path}")
    require(len([ref for ref in seen_refs if ref.startswith("HB-P")]) == 100, "expected 100 observation references")
    require(len([ref for ref in seen_refs if ref.startswith("observed-")]) == 5, "expected five new observed keys")
    for path, encoded in generated:
        path.parent.mkdir(parents=True, exist_ok=True)
        temporary_path = None
        try:
            with tempfile.NamedTemporaryFile(dir=path.parent, prefix=".holding-", suffix=".webp", delete=False) as temporary:
                temporary_path = Path(temporary.name)
                temporary.write(encoded)
            temporary_path.replace(path)
        finally:
            if temporary_path is not None:
                temporary_path.unlink(missing_ok=True)
    return len(rows)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    action = parser.add_mutually_exclusive_group(required=True)
    action.add_argument("--check", action="store_true", help="validate data, originals and exact reproduced WebP bytes")
    action.add_argument("--write", action="store_true", help="validate and regenerate all listed local crops")
    args = parser.parse_args()
    data = yaml.safe_load((ROOT / "data/holding-binder.yaml").read_text())
    count = validate(data, check_assets=args.check, write_assets=args.write)
    print(f"Holding: {count} owned cards, 100 pockets, five top loaders; archives verified; crops and exact derivatives {'reproduced' if args.check else 'written'}")


if __name__ == "__main__":
    main()
