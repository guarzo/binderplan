"""Reconcile the dated sort decisions without changing the historical checklist."""

import hashlib
import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKLIST = ROOT / "docs/2026-09-23-holding-sort-completion-checklist.tex"
RECONCILIATION = ROOT / "docs/evidence/2026-09-24/holding-sort-reconciliation.md"
CURRENT = ROOT / "docs/2026-09-24-holding-sort-current-inventory.md"
EVIDENCE = ROOT / "docs/evidence/2026-09-24/holding-sort-completed"


def test_sort_reconciles_all_owned_cards():
    checklist = CHECKLIST.read_text(encoding="utf-8")
    reconciliation = RECONCILIATION.read_text(encoding="utf-8")
    current = CURRENT.read_text(encoding="utf-8")

    rows = re.findall(
        r"^\\cardrow\{(HB-P\d{2}-\d{2})\}\{[^}]*\}\{[^}]*\}\{([^}]*)\}\{[^}]*\}",
        checklist,
        re.MULTILINE,
    )
    assert len(rows) == len(dict(rows)) == 100
    destinations = dict(rows)

    written = reconciliation.split("## Written destination overrides", 1)[1].split(
        "## Scan-only totals", 1
    )[0]
    overrides = re.findall(
        r"^\| (HB-P\d{2}-\d{2}) \|[^\n]*\| (Keeper · [^|]+|Review · [^|]+) \|$",
        written,
        re.MULTILINE,
    )
    assert len(overrides) == len(dict(overrides)) == 10
    for observation, destination in overrides:
        assert observation in destinations
        destinations[observation] = destination.strip()

    assert destinations["HB-P05-04"] == "Keeper · Beautiful Misfits"
    assert "owner's subsequent confirmation moves Numel" in reconciliation
    destinations["HB-P05-04"] = "Keeper · Species Studies"

    trade = reconciliation.split("## Owner-confirmed final disposition", 1)[1].split(
        "## Current reconciled inventory", 1
    )[0]
    trade_ids = re.findall(r"^\| (HB-P\d{2}-\d{2}) \|", trade, re.MULTILINE)
    assert len(trade_ids) == len(set(trade_ids)) == 5
    assert all(destinations[observation] == "Release" for observation in trade_ids)
    for observation in trade_ids:
        destinations[observation] = "Trade · available now"

    additional = reconciliation.split("## Five additional observed cards", 1)[1].split(
        "## Owner-confirmed final disposition", 1
    )[0]
    additional_roles = re.findall(
        r"^\| (?:Dedenne|Ampharos|McDonald’s Pikachu|Alolan Meowth|Mightyena) [^\n]*\| (Review · [^|]+) \|$",
        additional,
        re.MULTILINE,
    )
    assert len(additional_roles) == 5

    top_level = Counter(destination.split(" · ", 1)[0] for destination in destinations.values())
    top_level.update(destination.split(" · ", 1)[0] for destination in additional_roles)
    assert top_level == {"Review": 36, "Keeper": 64, "Trade": 5}
    assert sum(top_level.values()) == 105

    keeper = Counter(
        destination.split(" · ", 1)[1]
        for destination in destinations.values()
        if destination.startswith("Keeper · ")
    )
    assert keeper == {
        "Personal": 1,
        "Beautiful Misfits": 8,
        "Heritage": 28,
        "Species Studies": 27,
    }
    review = Counter(
        destination.split(" · ")[1]
        for destination in [*destinations.values(), *additional_roles]
        if destination.startswith("Review · ")
    )
    assert review == {
        "EDGE Watches": 6,
        "Existing-theme EDGE": 6,
        "REDUNDANT": 24,
    }
    for label, count in (("Review", 36), ("Keeper", 64), ("Trade · actively available", 5)):
        assert re.search(rf"^\| {re.escape(label)} \| \*\*{count}\*\* \|", current, re.MULTILINE)


def test_original_evidence_is_complete():
    originals = [EVIDENCE / "Holding.pdf", *(EVIDENCE / f"IMG_{i}.HEIC" for i in range(7133, 7148))]
    assert all(path.is_file() for path in originals)
    checksums = (EVIDENCE / "SHA256SUMS").read_text(encoding="utf-8")
    entries = dict(
        (relative_path, digest)
        for digest, relative_path in (line.split("  ", 1) for line in checksums.splitlines())
    )
    assert len(entries) == len(originals)
    assert set(entries) == {str(path.relative_to(ROOT)) for path in originals}
    for relative_path, digest in entries.items():
        assert re.fullmatch(r"[0-9a-f]{64}", digest)
        assert hashlib.sha256((ROOT / relative_path).read_bytes()).hexdigest() == digest
