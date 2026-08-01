#!/usr/bin/env python
"""Validate docs/card-registry.md and report duplicates and confirmation gaps.

The registry is a Markdown table, one row per physical card. This checks the
things a human reading 160 rows will not: that every ID matches the grammar,
that no ID is used twice, and that enum columns hold legal values.

It also produces two reports. Duplicate printings are a rule violation --
Volumes 1 and 2 must not hold the same printing twice -- and can only be
detected where set and number were actually legible. The confirmation queue is
the complement: rows whose set or number could not be read, ordered so that
species with several unread rows come first, because that is where an
undetected duplicate could be hiding.

Usage:
    python scripts/check-registry.py docs/card-registry.md
"""
import re
import sys
from pathlib import Path

COLUMNS = ["id", "species", "card_name", "language", "set", "number",
           "confidence", "first_seen", "notes"]
ID_RE = re.compile(r"^[a-z0-9]+(-[a-z0-9]+)*-\d{2}$")
LANGUAGES = {"EN", "JP", "ZH"}
CONFIDENCES = {"confirmed", "photo", "uncertain"}


def parse_registry(text):
    """Extract data rows from the Markdown table. Ignores prose and separators."""
    rows = []
    for line in text.splitlines():
        line = line.strip()
        if not line.startswith("|"):
            continue
        cells = [c.strip() for c in line.strip("|").split("|")]
        if len(cells) != len(COLUMNS):
            continue
        if cells[0] == "id" or set(cells[0]) <= {"-", ":"}:
            continue  # header or separator
        rows.append(dict(zip(COLUMNS, cells)))
    return rows


def species_slug(row_id):
    """The slug portion of an ID -- everything before the trailing counter."""
    return row_id.rsplit("-", 1)[0]


def validate(rows):
    errors = []
    seen_ids = set()
    for row in rows:
        rid = row["id"]
        if not ID_RE.match(rid):
            errors.append(f"bad id format: {rid!r} (want species-NN, lowercase, 2-digit)")
        if rid in seen_ids:
            errors.append(f"duplicate id: {rid!r}")
        seen_ids.add(rid)
        if row["language"] not in LANGUAGES:
            errors.append(f"{rid}: bad language {row['language']!r} (want one of {sorted(LANGUAGES)})")
        if row["confidence"] not in CONFIDENCES:
            errors.append(f"{rid}: bad confidence {row['confidence']!r} (want one of {sorted(CONFIDENCES)})")
        if row["confidence"] == "photo":
            if not row["set"]:
                errors.append(f"{rid}: confidence is 'photo' but set is blank")
            if not row["number"]:
                errors.append(f"{rid}: confidence is 'photo' but number is blank")
        if not row["first_seen"]:
            errors.append(f"{rid}: first_seen is required")
        if not row["species"]:
            errors.append(f"{rid}: species is required")
    # Species drift is deliberately NOT an error. The never-rewrite rule means a
    # corrected species column can legitimately disagree with a frozen ID slug.
    errors.extend(counter_gap_errors(rows))
    return errors


def counter_gap_errors(rows):
    """Every species' counters must run contiguously from 01 with no gaps.

    Grouped by species_slug(), which splits on the last hyphen only -- so a
    compound slug like gengar-mimikyu-01 groups under "gengar-mimikyu", never
    under "gengar", and never inflates another species' sequence.
    """
    errors = []
    counters = {}
    for row in rows:
        rid = row["id"]
        if not ID_RE.match(rid):
            continue  # already reported as a bad id format above
        slug = species_slug(rid)
        n = int(rid.rsplit("-", 1)[1])
        counters.setdefault(slug, set()).add(n)
    for slug, numbers in sorted(counters.items()):
        missing = [n for n in range(1, max(numbers) + 1) if n not in numbers]
        if missing:
            missing_str = ", ".join(f"{n:02d}" for n in missing)
            errors.append(f"{slug}: counters are not contiguous from 01, missing {missing_str}")
    return errors


def duplicate_printings(rows):
    """Pairs sharing species, set, number and language.

    Rows with an unread set or number are skipped entirely -- absence of a
    number is not evidence of a match, and guessing here would produce false
    accusations against a rule the curator enforces by discarding cards.
    """
    buckets = {}
    for row in rows:
        if not row["set"] or not row["number"]:
            continue
        key = (row["species"].lower(), row["set"].lower(),
               row["number"].lower(), row["language"].upper())
        buckets.setdefault(key, []).append(row)
    pairs = []
    for group in buckets.values():
        for i in range(len(group)):
            for j in range(i + 1, len(group)):
                pairs.append((group[i], group[j]))
    return pairs


def confirmation_queue(rows):
    """Rows needing a physical check, species clusters first.

    A species holding two or more unresolved rows leads the queue: that is where
    a duplicate printing could be hiding unseen. An isolated unread number is
    cosmetic by comparison.
    """
    buckets = {}
    for row in rows:
        if row["confidence"] == "confirmed":
            continue
        if row["confidence"] != "uncertain" and row["set"] and row["number"]:
            continue
        buckets.setdefault(species_slug(row["id"]), []).append(row)
    return sorted(buckets.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def main(argv):
    if len(argv) != 2:
        print(__doc__)
        return 2
    text = Path(argv[1]).read_text(encoding="utf-8")
    rows = parse_registry(text)
    print(f"{len(rows)} rows")

    errors = validate(rows)
    for error in errors:
        print(f"ERROR {error}")

    pairs = duplicate_printings(rows)
    print(f"\n-- duplicate printings: {len(pairs)} --")
    for a, b in pairs:
        print(f"  {a['id']} / {b['id']}: {a['species']} {a['set']} {a['number']} {a['language']}")

    queue = confirmation_queue(rows)
    total = sum(len(g) for _, g in queue)
    print(f"\n-- needs physical confirmation: {total} rows in {len(queue)} species --")
    for slug, group in queue:
        flag = "  <-- CLUSTER" if len(group) > 1 else ""
        print(f"  {slug} ({len(group)}){flag}")
        for row in group:
            print(f"      {row['id']}  {row['card_name']}  [{row['first_seen']}]")

    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv))
