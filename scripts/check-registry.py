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
    python scripts/check-registry.py docs/card-registry.md --worklist --write
    python scripts/check-registry.py docs/card-registry.md --worklist [--previous PATH]

--worklist regenerates the confirmation document. It reads the document it is
replacing (docs/registry-confirmation.md, or --previous) to carry section 4's
hand-written narrative forward, so regeneration cannot silently drop it.

Prefer --write, which reads the old document and replaces it atomically. Plain
--worklist prints to stdout, and redirecting that back onto the source document
destroys section 4: the shell truncates the file before the script can read it,
so the narrative is gone before carry-forward runs. Redirect only to a different
path.
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
        # Counters run from 01. A 00 matches ID_RE but breaks that invariant, and the
        # contiguity check below cannot see it -- range(1, 0 + 1) is empty.
        if 0 in numbers:
            errors.append(f"{slug}-00: counters start at 01, not 00")
            numbers = numbers - {0}
            if not numbers:
                continue
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

    Grouped by the `species` column, NOT by the ID slug. The never-rewrite rule
    freezes an ID once something cites it, but lets a mistaken `species` be
    corrected, so the two drift apart -- a row keeping an ID of marowak-NN while
    its species reads Cubone. A duplicate printing is defined by
    species, so a cluster built on the slug would hide exactly the pair it exists
    to surface. species_slug() stays in use for counter validation, where the ID
    sequence is the thing being checked.
    """
    buckets = {}
    for row in rows:
        if row["confidence"] == "confirmed":
            continue
        if row["confidence"] != "uncertain" and row["set"] and row["number"]:
            continue
        key = row["species"].strip().lower().replace(" ", "-")
        buckets.setdefault(key, []).append(row)
    return sorted(buckets.items(), key=lambda kv: (-len(kv[1]), kv[0]))


def _pct(count, total):
    return (count / total * 100) if total else 0.0


def _source_image(first_seen):
    """The filename portion of first_seen, which is 'filename date'."""
    return first_seen.split()[0] if first_seen else first_seen


# Image -> page, in binder order. A photograph shows what it shows, so this is a
# stable fact and can live here. It is deliberately NOT a card -> page index:
# that would rot on the first swap, and it is the inventory the curator rejected.
#
# Volume II carries a systematic off-by-one: the pre-2026-08-01 shoot missed the
# Threshold page, so every page after quiet_familiarity_1 was filed under the
# next page's name. The registry's first_seen keeps those old names on purpose --
# it is immutable provenance -- so the correction lives here instead. The
# static/images/binder/ files themselves were renamed correctly during the
# gallery refresh; do not "fix" the registry to match.
PAGE_ORDER = {
    "calm_nature_1.webp": "V1 · Calm in Nature",
    "world_people_1.webp": "V1 · World of People",
    "at_rest_1.webp": "V1 · At Rest",
    "joyful_action_1.webp": "V1 · Joyful Action",
    "awakened_power_1.webp": "V1 · Awakened Power p1",
    "awakened_power_2.webp": "V1 · Awakened Power p2",
    "legendary_bearing_1.webp": "V1 · Legendary Bearing p1",
    "legendary_bearing_2.webp": "V1 · Legendary Bearing p2",
    "intimidation_1.webp": "V1 · Intimidation",
    "on_attack_1.webp": "V1 · On the Attack",
    "elemental_solitude_1.webp": "V1 · Elemental Solitude",
    "contemplation_1.webp": "V1 · Contemplation",
    "companions_1.webp": "V2 · Companions p1",
    "companions_2.webp": "V2 · Companions p2",
    "quiet_familiarity_1.webp": "V2 · Quiet Familiarity p1",
    "enduring_presence_1.webp": "V2 · Quiet Familiarity p2",   # misnamed
    "enduring_presence_2.webp": "V2 · Enduring Presence p1",   # off by one
    "threshold_1.webp": "V2 · Enduring Presence p2",           # off by one
    "IMG_6865.HEIC": "V2 · Threshold",   # never published before the reshoot
}

# Single cards added after the original shoot. Each belongs to an existing page
# and merges into that page's group rather than showing as a one-card page.
#
# Do not dispatch on the IMG_* filename shape: IMG_6865.HEIC matches it too but
# is a whole nine-card page, in PAGE_ORDER above. These two tables are the only
# source of truth -- a pattern match would misplace nine cards.
SWAP_INS = {
    "IMG_6842.HEIC": "V1 · At Rest",
    "IMG_6847.HEIC": "V1 · Legendary Bearing p1",
    "IMG_6853.HEIC": "V1 · Elemental Solitude",
    "IMG_6858.HEIC": "V2 · Companions p2",
    "IMG_6860.HEIC": "V2 · Quiet Familiarity p2",
}

_PAGE_POSITION = {label: i for i, label in enumerate(PAGE_ORDER.values())}


def page_groups(rows):
    """Unresolved rows grouped by binder page, in binder order.

    Same row set as confirmation_queue(), regrouped for walking the binder
    instead of for spotting duplicate printings: open to one page, clear every
    card on it, move on. Pages with nothing unresolved are omitted.

    An image in neither table gets its own "Unmapped source image" group, sorted
    last, so a future shoot cannot make cards silently vanish from the worklist.
    """
    buckets = {}
    for _, group in confirmation_queue(rows):
        for row in group:
            image = _source_image(row["first_seen"])
            label = PAGE_ORDER.get(image) or SWAP_INS.get(image)
            if label is None:
                label = f"Unmapped source image · {image}"
            buckets.setdefault(label, []).append(row)
    return sorted(
        buckets.items(),
        key=lambda kv: (_PAGE_POSITION.get(kv[0], len(_PAGE_POSITION)), kv[0]),
    )


DEFAULT_PREVIOUS = Path("docs/registry-confirmation.md")

_HANDWRITTEN_PLACEHOLDER = (
    "<!-- Hand-written. Regenerating this document does not reproduce this section;\n"
    "     write it here and it will be carried forward automatically. -->"
)


def carry_forward_section_four(previous):
    """Section 4's hand-written body, lifted from the previous document.

    Section 4 is narrative the registry cannot reconstruct, so regeneration has
    to preserve it. Doing that by hand -- extract, splice, write back -- fails
    silently the first time someone forgets, and nothing in the verify step
    would catch it. So the script reads the document it is about to replace.

    Returns the placeholder when the file is absent or holds no section 4, which
    covers a first run and a fresh checkout. A previous of None means the caller
    did not ask for carry-forward at all.
    """
    if previous is None:
        return _HANDWRITTEN_PLACEHOLDER
    try:
        text = Path(previous).read_text(encoding="utf-8")
    except OSError:
        return _HANDWRITTEN_PLACEHOLDER
    match = re.search(
        r"^## 4\. Gaps and known issues\s*\n(.*?)(?=^## \d+\.|\Z)",
        text,
        re.DOTALL | re.MULTILINE,
    )
    if not match:
        return _HANDWRITTEN_PLACEHOLDER
    body = match.group(1).strip()
    return body or _HANDWRITTEN_PLACEHOLDER


def render_worklist(rows, previous=None):
    """The full confirmation-worklist document, as Markdown text.

    Reproduces the structure of the hand-written docs/registry-confirmation.md
    (sections 1-3, 5 and 6) purely from the rows
    passed in, so it can be regenerated on demand instead of drifting out of
    date. Section 4, "Gaps and known issues", is hand-written narrative the
    registry cannot reconstruct, so it is carried forward from the previous
    document at `previous`; see carry_forward_section_four().
    """
    total = len(rows)
    photo = sum(1 for r in rows if r["confidence"] == "photo")
    uncertain = sum(1 for r in rows if r["confidence"] == "uncertain")
    both = sum(1 for r in rows if r["set"] and r["number"])
    number_only = sum(1 for r in rows if r["number"] and not r["set"])
    set_only = sum(1 for r in rows if r["set"] and not r["number"])
    neither = sum(1 for r in rows if not r["set"] and not r["number"])
    missing = total - both

    pairs = duplicate_printings(rows)

    queue = confirmation_queue(rows)
    queue_total = sum(len(g) for _, g in queue)
    queue_species = len(queue)
    clusters = [(slug, g) for slug, g in queue if len(g) > 1]
    singletons = [(slug, g) for slug, g in queue if len(g) == 1]
    cluster_rows = sum(len(g) for _, g in clusters)

    lines = []
    lines.append("# Registry confirmation worklist")
    lines.append("")
    lines.append(
        "Generated from `docs/card-registry.md` by `python3 scripts/check-registry.py "
        "docs/card-registry.md --worklist --write`. Every section below is recomputed from the "
        "registry except \"4. Gaps and known issues\", which is hand-written; regeneration "
        "reads the previous version of this document and carries that section forward "
        "automatically."
    )
    lines.append("")
    lines.append(
        f"**Honest numbers, recomputed from the current file.** {total} rows total. "
        f"{photo} `photo` ({_pct(photo, total):.1f}%), {uncertain} `uncertain` "
        f"({_pct(uncertain, total):.1f}%). {both} rows have both `set` and `number` read "
        f"({_pct(both, total):.1f}%) — {number_only} have `number` only, {set_only} have `set` "
        f"only, {neither} have neither field. The confirmation queue (section 3) holds "
        f"{queue_total} rows across {queue_species} species: {len(clusters)} clusters "
        f"({cluster_rows} rows) and {len(singletons)} singletons."
    )
    lines.append("")
    lines.append("## 1. Blocked — species unreadable")
    lines.append("")
    lines.append(
        "None. The registry has no state for a card that was seen but never identified to "
        "species -- every row that exists already carries one -- so this section is always "
        "empty."
    )
    lines.append("")
    lines.append("## 2. Duplicate printing candidates")
    lines.append("")
    if pairs:
        lines.append(f"**{len(pairs)} found:**")
        lines.append("")
        for a, b in pairs:
            lines.append(
                f"- {a['id']} / {b['id']}: {a['species']} {a['set']} {a['number']} {a['language']}"
            )
        lines.append("")
    else:
        lines.append(
            "**None found** — `python3 scripts/check-registry.py docs/card-registry.md` "
            "reports `duplicate printings: 0`."
        )
        lines.append("")
    lines.append(
        "Take that as a weak result, not a clean bill of health. The check requires all four "
        "fields — `species`, `set`, `number`, `language` — to match on two rows, and only "
        f"**{both} of {total} rows ({_pct(both, total):.1f}%)** have both `set` and `number` "
        f"read. The remaining {missing} rows ({_pct(missing, total):.1f}%) are missing one or "
        "both fields and are structurally invisible to this check: two physical duplicates "
        "sitting in the registry right now would not be flagged unless both happened to land "
        f"among that same {both}-row minority."
    )
    lines.append("")
    lines.append("## 3. Confirmation queue — clusters first")
    lines.append("")
    lines.append(
        f"{queue_total} rows, {queue_species} species. **{len(clusters)} species "
        f"({cluster_rows} rows) hold two or more unresolved rows** and lead the list, because "
        f"that is where an undetected duplicate printing could hide. The remaining "
        f"{len(singletons)} species have a single unresolved row each."
    )
    lines.append("")
    lines.append(
        "The \"Unreadable\" column is the row's own `notes` field: what specifically blocked "
        "the read."
    )
    lines.append("")
    if clusters:
        lines.append("### Clusters (species with 2+ unresolved rows)")
        lines.append("")
        for slug, group in clusters:
            lines.append(f"**{slug}** ({len(group)})")
            lines.append("")
            lines.append("| ID | Card name | Source image | Unreadable |")
            lines.append("|---|---|---|---|")
            for r in group:
                lines.append(
                    f"| {r['id']} | {r['card_name']} ({r['language']}) | "
                    f"{_source_image(r['first_seen'])} | {r['notes']} |"
                )
            lines.append("")
    if singletons:
        lines.append(f"### Singletons ({len(singletons)} species, one unresolved row each)")
        lines.append("")
        lines.append("| ID | Card name | Source image | Unreadable |")
        lines.append("|---|---|---|---|")
        for slug, group in singletons:
            r = group[0]
            lines.append(
                f"| {r['id']} | {r['card_name']} ({r['language']}) | "
                f"{_source_image(r['first_seen'])} | {r['notes']} |"
            )
        lines.append("")
    lines.append("## 4. Gaps and known issues")
    lines.append("")
    lines.append(carry_forward_section_four(previous))
    lines.append("")
    lines.append("## 5. Cards no longer in the binder")
    lines.append("")
    lines.append(
        "Not derivable here. The registry records what a card **is**, never where it sits, "
        "so a row gives no sign that its card has left the binder. Movement lives in "
        "`ledger.md`: grep it for an ID to see whether that card was swapped out. Any list "
        "of departed cards in this document is hand-written; put it in section 4, which is "
        "carried forward automatically when this document is regenerated."
    )
    lines.append("")
    lines.append("## 6. Confirmation queue by page")
    lines.append("")
    lines.append(
        "The same rows as section 3, regrouped for walking the binder. Open to a page, clear "
        "every card listed under it, move on. Pages in binder order; a page with nothing "
        "unresolved is omitted. The source image is dropped here — the page implies it."
    )
    lines.append("")
    lines.append(
        "Photographs record what was on a page when the shoot happened, so a card since "
        "swapped out still appears under its old page. `ursaring-01`, `typhlosion-02` and "
        "`umbreon-03` are the known cases; check `ledger.md` before hunting for a card that "
        "is not there."
    )
    lines.append("")
    for label, group in page_groups(rows):
        lines.append(f"### {label}")
        lines.append("")
        lines.append("| ID | Card name | Unreadable |")
        lines.append("|---|---|---|")
        for r in sorted(group, key=lambda r: r["id"]):
            lines.append(
                f"| {r['id']} | {r['card_name']} ({r['language']}) | {r['notes']} |"
            )
        lines.append("")
    return "\n".join(lines)


def main(argv):
    args = argv[1:]
    worklist = "--worklist" in args
    write = "--write" in args
    previous = DEFAULT_PREVIOUS
    if "--previous" in args:
        i = args.index("--previous")
        if i + 1 >= len(args) or args[i + 1].startswith("--"):
            print("--previous needs a path")
            print(__doc__)
            return 2
        previous = Path(args[i + 1])
        args = args[:i] + args[i + 2:]
    positional = [a for a in args if a not in ("--worklist", "--write")]
    if len(positional) != 1:
        print(__doc__)
        return 2
    if write and not worklist:
        print("--write only applies to --worklist")
        print(__doc__)
        return 2
    text = Path(positional[0]).read_text(encoding="utf-8")
    rows = parse_registry(text)
    errors = validate(rows)

    if worklist:
        for error in errors:
            print(f"ERROR {error}", file=sys.stderr)
        document = render_worklist(rows, previous=previous)
        if write:
            # Render first, write second. The document is fully built -- section
            # 4 already carried forward -- before the target is touched, which
            # is the whole point: `--worklist > docs/registry-confirmation.md`
            # lets the shell truncate the file before carry-forward can read it.
            target = Path(previous)
            tmp = target.with_suffix(target.suffix + ".tmp")
            tmp.write_text(document + "\n", encoding="utf-8")
            tmp.replace(target)
            print(f"wrote {target}", file=sys.stderr)
        else:
            print(document)
        return 1 if errors else 0

    print(f"{len(rows)} rows")

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
