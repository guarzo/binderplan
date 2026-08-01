#!/usr/bin/env python3
"""Verify gallery content: image refs resolve, and each slab is used exactly once."""
import re
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
SLABS = STATIC / "images" / "slabs"

EXPECTED_COUNTS = {
    "definitive-pokemon": 3,
    "touchstones": 7,
    "personal-significance": 15,
    "chinese-exclusives": 6,
    "masaki": 5,
}

IMG_RE = re.compile(r"<img\s[^>]*>")
SRC_RE = re.compile(r'\ssrc="([^"]*)"')
LAZY_RE = re.compile(r'\sloading="lazy"')


def collect():
    """Return {md_path: [resolved static paths]} for every img src in content/, plus a
    list of per-tag failures: relative-depth problems (paths that resolve on disk only
    because Path() discards the ../ prefix, but a browser would 404 on) and gallery
    images missing the required loading="lazy" attribute."""
    refs = {}
    tag_failures = []
    for md in sorted(CONTENT.rglob("*.md")):
        found = []
        expected_prefix = "../../images/" if md.parent.parent == CONTENT / "gallery" else None
        for tag in IMG_RE.findall(md.read_text(encoding="utf-8")):
            raw = SRC_RE.search(tag)
            if not raw:
                continue
            src = urllib.parse.unquote(raw.group(1))
            if "images/" not in src:
                continue
            if expected_prefix and not src.startswith(expected_prefix):
                tag_failures.append(
                    f"wrong relative depth: {src} in {md.relative_to(ROOT)} (expected ../../images/...)"
                )
                continue
            if expected_prefix and not LAZY_RE.search(tag):
                tag_failures.append(
                    f'missing loading="lazy": {src} in {md.relative_to(ROOT)}'
                )
            found.append(STATIC / src[src.index("images/"):])
        refs[md] = found
    return refs, tag_failures


def check_images_exist(refs):
    """Every referenced image exists on disk."""
    failures = []
    for md, paths in refs.items():
        for p in paths:
            if not p.is_file():
                failures.append(f"missing image: {p.relative_to(ROOT)} (referenced by {md.relative_to(ROOT)})")
    return failures


def check_slab_usage(refs):
    """Every slab image is referenced exactly once across all content."""
    failures = []
    used = Counter()
    for paths in refs.values():
        for p in paths:
            if SLABS in p.parents:
                used[p.name] += 1
    on_disk = {p.name for p in SLABS.iterdir() if p.is_file()}
    for name in sorted(on_disk - set(used)):
        failures.append(f"orphan slab image, referenced by no page: {name}")
    for name, n in sorted(used.items()):
        if name not in on_disk:
            continue
        if n > 1:
            failures.append(f"slab image referenced {n} times, must be exactly 1: {name}")
    return failures


def check_removed_sections():
    """No lingering references to removed sections."""
    failures = []
    for md in sorted(CONTENT.rglob("*.md")):
        if "gold-stars" in md.read_text(encoding="utf-8"):
            failures.append(f"reference to removed gold-stars section: {md.relative_to(ROOT)}")
    return failures


def check_section_counts(refs):
    """Section card counts match the design doc."""
    failures = []
    for section, expected in EXPECTED_COUNTS.items():
        md = CONTENT / "gallery" / section / "_index.md"
        if not md.is_file():
            failures.append(f"missing section page: {md.relative_to(ROOT)}")
            continue
        actual = len([p for p in refs[md] if SLABS in p.parents])
        if actual != expected:
            failures.append(f"{section}: {actual} slab images, expected {expected}")
    return failures


def main():
    refs, tag_failures = collect()
    failures = [
        *tag_failures,
        *check_images_exist(refs),
        *check_slab_usage(refs),
        *check_removed_sections(),
        *check_section_counts(refs),
    ]

    if failures:
        print(f"FAIL ({len(failures)} problem(s)):")
        for f in failures:
            print("  -", f)
        return 1
    total = sum(EXPECTED_COUNTS.values())
    print(f"PASS: {total} slab images, each referenced exactly once")
    return 0


if __name__ == "__main__":
    sys.exit(main())
