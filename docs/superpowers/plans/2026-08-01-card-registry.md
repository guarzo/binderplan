# Card Registry Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Give every card in Volumes 1 and 2 a stable identifier that survives moves between themes, so append-only ledger references stay resolvable indefinitely.

**Architecture:** A Markdown table at `docs/card-registry.md` holds one row per physical card — identity plus the immutable photograph the row was derived from, and deliberately no location field. A Python validator at `scripts/check-registry.py` enforces the ID grammar, catches uniqueness violations, and generates the duplicate-printing report and the physical-confirmation queue. Seeding is a two-pass process with a curator review gate between them.

**Tech Stack:** Markdown, Python 3 with Pillow and numpy (both already used by `scripts/crop-binder-photos.py`). Hugo is untouched — `docs/` sits outside `content/` and is not part of the site build.

**Design note:** `docs/superpowers/specs/2026-08-01-card-registry-design.md`. Read it before starting; this plan implements it and does not restate its reasoning.

## Global Constraints

- **ID grammar:** `<species-slug>-<NN>`, `NN` zero-padded to two digits. Regex: `^[a-z0-9]+(-[a-z0-9]+)*-\d{2}$`
- **Slug source:** English Pokédex species name only, for cards of every language. No mechanics, prefixes, or set qualifiers — not `houndoom-g-01`, not `dark-houndoom-01`, not `mewtwo-ex-01`. Non-Pokémon cards use the printed card name slugified.
- **IDs are never rewritten**, even when later proven inaccurate. Correct the `species` column, leave the `id` alone. The sole exception is the pass-2 gate in Task 6, before any ID has been cited anywhere.
- **No location field.** Not in the registry, not in any file this plan creates.
- **When unsure whether a card is a new copy or an existing entry, assign a new ID.** A phantom entry is recoverable via `superseded-by`; a merge is not.
- **Scope is Volumes 1 and 2 only** — the 18 page images listed in Task 2. Emolga masterset, stamped cards, trainer full arts, and slabs are out of scope.
- **`language` is one of:** `EN`, `JP`, `ZH`
- **`confidence` is one of:** `confirmed` (read from the physical card), `photo` (legible in the image), `uncertain` (inferred or obscured)
- **Seeding tasks (2, 3, 4) commit after every page, not once at the end.** Read a page, append its rows, run the validator, commit that page, move to the next. Reading a page is expensive — roughly 20 minutes of image work — and batching six pages behind one commit means any interruption loses all of it. This is not a style preference: attempt 1 at Task 2 read all six pages, hit a session limit before its single commit, and lost every row. Commit subject per page: `Seed registry from <image basename>`.
- **Commit after every task.** Match the existing message style — imperative mood, no `feat:`/`fix:` prefixes (the repo does not use them). End every commit message with these two trailers, matching the branch's existing commits:

  ```
  Co-Authored-By: Claude Opus 5 <noreply@anthropic.com>
  Claude-Session: https://claude.ai/code/session_01WUw2d7Bii9F3xngLgxJQov
  ```

## Working Context

- **Worktree:** `.claude/worktrees/card-registry`, branch `worktree-card-registry`, branched off `origin/main` at `a254855`. All work happens here.
- **Photos show the pre-swap binder.** The ledger's 11 accepted swaps and 28 releases have **not** been executed — the curator holds a printed copy and is working through them physically. The registry therefore records the binder as photographed, which is correct: `first_seen` is a dated observation, not a claim about the present. The pending swaps become the first ID-citing ledger entry later, and the 11 incoming cards get IDs at that point under the on-first-citation rule. **Do not try to pre-apply the swaps to the registry.**

---

## File Structure

| File | Responsibility |
|---|---|
| `docs/card-registry.md` | Create. The registry: conventions header + one table, sorted by ID. |
| `scripts/check-registry.py` | Create. Parses the registry, validates grammar and uniqueness, emits duplicate report and confirmation queue. |
| `scripts/test_check_registry.py` | Create. Tests for the validator, using inline fixture tables. |
| `docs/ledger.md` | Modify. Entries wiped; conventions header gains a **Card IDs** block and a rewritten **No backfill**. |
| `CURATORIAL_AUDIT_PROMPT.md` | Modify. Two blocks appended to §2. |
| `docs/holding-box-placement.md` | Delete, in the final task only — it is a seeding source until then. |

---

## Task 1: Registry validator

Build the validator before the data, so seeding is checked from the first row.

**Files:**
- Create: `scripts/check-registry.py`
- Create: `scripts/test_check_registry.py`
- Create: `docs/card-registry.md`

**Interfaces:**
- Consumes: nothing.
- Produces: `parse_registry(text: str) -> list[dict]`, `validate(rows: list[dict]) -> list[str]` (returns error strings, empty when clean), `duplicate_printings(rows) -> list[tuple[dict, dict]]`, `confirmation_queue(rows) -> list[tuple[str, list[dict]]]` (species slug, rows — clusters first). CLI: `python scripts/check-registry.py docs/card-registry.md`, exit 1 on validation errors.

- [ ] **Step 1: Create the registry file with its header and an empty table**

Create `docs/card-registry.md`:

```markdown
# Card registry

Stable identifiers for every card in Volumes 1 and 2.

This is not an inventory. It records what a card **is**, never where it sits. A card's ID is unchanged when it moves from one theme to another, unchanged when it goes to the holding box, and unchanged after release. To find where a card is now, grep `ledger.md` for its ID and read forward.

## How to use this file

**IDs are permanent.** `<species>-<NN>`, using the English Pokédex species name for cards of every language, plus a counter that means nothing. If an ID later proves inaccurate — the card is a Houndoom, not the Houndour its ID says — correct the `species` column and leave the `id` alone. A rewritten ID breaks every reference already written against it.

**The ID carries no qualifiers.** `Houndoom G Lv.45` is `houndoom-NN`; `ドダイトス Lv.X` is `torterra-NN`; `M Gengar EX` is `gengar-NN`. Printed names live in `card_name`.

**When in doubt, split.** If you cannot tell whether a card is a new copy or one already listed, assign a new ID. Two IDs for one card is recoverable — note `superseded-by: <id>`. One ID for two cards is not.

**Design note:** `superpowers/specs/2026-08-01-card-registry-design.md`.

**Validate with:** `python scripts/check-registry.py docs/card-registry.md`

## Registry

| id | species | card_name | language | set | number | confidence | first_seen | notes |
|---|---|---|---|---|---|---|---|---|
```

- [ ] **Step 2: Write the failing tests**

Create `scripts/test_check_registry.py`:

```python
"""Tests for the card registry validator."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "check_registry", Path(__file__).parent / "check-registry.py"
)
check_registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_registry)

parse_registry = check_registry.parse_registry
validate = check_registry.validate
duplicate_printings = check_registry.duplicate_printings
confirmation_queue = check_registry.confirmation_queue

HEADER = (
    "| id | species | card_name | language | set | number | confidence | first_seen | notes |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
)


def table(*rows):
    return "# Card registry\n\n## Registry\n\n" + HEADER + "".join(rows)


def row(id_, species, name="X", lang="EN", set_="Base", num="1/10",
        conf="photo", seen="img.webp 2026-08-01", notes=""):
    return f"| {id_} | {species} | {name} | {lang} | {set_} | {num} | {conf} | {seen} | {notes} |\n"


def test_parses_a_row_into_a_dict():
    rows = parse_registry(table(row("umbreon-01", "Umbreon")))
    assert len(rows) == 1
    assert rows[0]["id"] == "umbreon-01"
    assert rows[0]["species"] == "Umbreon"
    assert rows[0]["language"] == "EN"


def test_blank_cells_become_empty_strings():
    rows = parse_registry(table(row("umbreon-01", "Umbreon", set_="", num="")))
    assert rows[0]["set"] == ""
    assert rows[0]["number"] == ""


def test_valid_table_has_no_errors():
    assert validate(parse_registry(table(row("umbreon-01", "Umbreon")))) == []


def test_rejects_unpadded_counter():
    errors = validate(parse_registry(table(row("umbreon-1", "Umbreon"))))
    assert any("umbreon-1" in e for e in errors)


def test_rejects_uppercase_id():
    errors = validate(parse_registry(table(row("Umbreon-01", "Umbreon"))))
    assert any("Umbreon-01" in e for e in errors)


def test_rejects_duplicate_ids():
    errors = validate(parse_registry(
        table(row("umbreon-01", "Umbreon"), row("umbreon-01", "Umbreon"))
    ))
    assert any("duplicate id" in e.lower() for e in errors)


def test_rejects_unknown_language():
    errors = validate(parse_registry(table(row("umbreon-01", "Umbreon", lang="FR"))))
    assert any("FR" in e for e in errors)


def test_rejects_unknown_confidence():
    errors = validate(parse_registry(table(row("umbreon-01", "Umbreon", conf="maybe"))))
    assert any("maybe" in e for e in errors)


def test_requires_first_seen():
    errors = validate(parse_registry(table(row("umbreon-01", "Umbreon", seen=""))))
    assert any("first_seen" in e for e in errors)


def test_species_drift_is_a_warning_not_an_error():
    # The never-rewrite rule permits an ID whose slug no longer matches species.
    errors = validate(parse_registry(table(row("houndour-03", "Houndoom"))))
    assert errors == []


def test_finds_duplicate_printings():
    pairs = duplicate_printings(parse_registry(table(
        row("houndoom-01", "Houndoom", set_="Rising Rivals", num="50/111"),
        row("houndoom-02", "Houndoom", set_="Rising Rivals", num="50/111"),
    )))
    assert len(pairs) == 1


def test_different_numbers_are_not_duplicates():
    pairs = duplicate_printings(parse_registry(table(
        row("umbreon-01", "Umbreon", set_="Neo Discovery", num="32/75"),
        row("umbreon-02", "Umbreon", set_="Neo Discovery", num="13/75"),
    )))
    assert pairs == []


def test_different_languages_are_not_duplicates():
    pairs = duplicate_printings(parse_registry(table(
        row("umbreon-01", "Umbreon", lang="EN", set_="S", num="1/10"),
        row("umbreon-02", "Umbreon", lang="JP", set_="S", num="1/10"),
    )))
    assert pairs == []


def test_unread_numbers_never_report_as_duplicates():
    # Cannot confirm a violation without the number. Must not guess.
    pairs = duplicate_printings(parse_registry(table(
        row("umbreon-01", "Umbreon", set_="", num=""),
        row("umbreon-02", "Umbreon", set_="", num=""),
    )))
    assert pairs == []


def test_confirmation_queue_leads_with_species_clusters():
    queue = confirmation_queue(parse_registry(table(
        row("cinccino-01", "Cinccino", num="", conf="uncertain"),
        row("umbreon-01", "Umbreon", num="", conf="uncertain"),
        row("umbreon-02", "Umbreon", num="", conf="uncertain"),
    )))
    assert queue[0][0] == "umbreon"
    assert len(queue[0][1]) == 2


def test_confidence_confirmed_rows_are_not_queued():
    queue = confirmation_queue(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed"),
    )))
    assert queue == []
```

- [ ] **Step 3: Run the tests to verify they fail**

Run: `python -m pytest scripts/test_check_registry.py -v`
Expected: collection error — `check-registry.py` does not exist.

If `pytest` is unavailable, install it: `pip install pytest`.

- [ ] **Step 4: Write the validator**

Create `scripts/check-registry.py`:

```python
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
        if not row["first_seen"]:
            errors.append(f"{rid}: first_seen is required")
        if not row["species"]:
            errors.append(f"{rid}: species is required")
    # Species drift is deliberately NOT an error. The never-rewrite rule means a
    # corrected species column can legitimately disagree with a frozen ID slug.
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
        if row["set"] and row["number"]:
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
```

- [ ] **Step 5: Run the tests to verify they pass**

Run: `python -m pytest scripts/test_check_registry.py -v`
Expected: 15 passed.

- [ ] **Step 6: Run the validator against the empty registry**

Run: `python scripts/check-registry.py docs/card-registry.md`
Expected: `0 rows`, no errors, both reports empty. Exit code 0.

- [ ] **Step 7: Commit**

```bash
git add scripts/check-registry.py scripts/test_check_registry.py docs/card-registry.md
git commit -m "Add card registry scaffold and validator"
```

---

## Task 2: Seed Volume 1, chapters I–III

**Files:**
- Modify: `docs/card-registry.md`

**Interfaces:**
- Consumes: the table format and `scripts/check-registry.py` from Task 1.
- Produces: registry rows for the first six Volume 1 pages. Later tasks append below them and re-sort.

Read each image and add one row per occupied pocket. These are single 9-pocket pages, not two-page spreads, so expect up to 9 rows each — but **count the actual occupied pockets**; do not assume 9.

**Pages in this task:**

| Image | Theme |
|---|---|
| `static/images/binder/volume-1/calm_nature_1.webp` | Calm in Nature |
| `static/images/binder/volume-1/world_people_1.webp` | World of People |
| `static/images/binder/volume-1/at_rest_1.webp` | At Rest |
| `static/images/binder/volume-1/joyful_action_1.webp` | Joyful Action |
| `static/images/binder/volume-1/awakened_power_1.webp` | Awakened Power p1 |
| `static/images/binder/volume-1/awakened_power_2.webp` | Awakened Power p2 |

- [ ] **Step 1: Convert the six images to PNG for reading**

`.webp` is not directly readable by the Read tool. Convert into the scratchpad, never into the repo:

```bash
OUT=/tmp/claude-1000/-home-tng-workspace-binderplan/2e24ee4d-3042-400e-95e2-350be0a647fb/scratchpad
mkdir -p "$OUT"
python3 -c "
from PIL import Image
import pathlib
out = pathlib.Path('$OUT')
names = ['calm_nature_1','world_people_1','at_rest_1','joyful_action_1','awakened_power_1','awakened_power_2']
for n in names:
    p = f'static/images/binder/volume-1/{n}.webp'
    Image.open(p).convert('RGB').save(out / f'{n}.png')
    print(n)
"
```

- [ ] **Step 2: Read each page and record its cards**

Read each PNG. For every occupied pocket, in reading order (top-left → bottom-right), capture:

- **species** — the English Pokédex name, translating Japanese where needed (バクフーン → Typhlosion, ムウマ → Misdreavus, キテルグマ → Bewear, ガラガラ → Marowak, ゲンガー → Gengar). This is reliably legible; if a species genuinely cannot be read, **do not invent an ID** — note it for Task 5's blocked list instead.
- **card_name** — as printed, including qualifiers the ID drops: `Mewtwo EX`, `ルカリオVSTAR`, `Houndoom G Lv.45`.
- **language** — `EN` / `JP` / `ZH`.
- **set** and **number** — only when actually legible. Leave blank otherwise. Do not infer from art or era.
- **confidence** — `photo` when set and number were both read from the image; `uncertain` when either is blank or a guess. Never `confirmed`; that value means the physical card was handled.
- **first_seen** — `<image filename> <date>`, e.g. `calm_nature_1.webp 2026-08-01`.

Where a number is nearly legible, crop and upscale before giving up:

```bash
python3 -c "
from PIL import Image
im = Image.open('static/images/binder/volume-1/calm_nature_1.webp')
c = im.crop((790, 1430, 1125, 1560)).convert('RGB')   # adjust box per pocket
c.resize((c.width*4, c.height*4), Image.LANCZOS).save('$OUT/corner.png')
"
```

Be aware this often fails — the source resolution is the ceiling and upscaling adds no information. A blurred corner stays blurred. That is expected, not a failure; leave the field blank and move on.

**Vintage Japanese cards** print a Pokédex `No.157` rather than a modern collector number. Record it as `No.157` in `number` and name the era in `set` (e.g. `Neo Genesis`). Flag `confidence: uncertain` unless the set is genuinely identifiable, because a Pokédex number is not a set-unique key and the duplicate check is correspondingly weaker for these.

**Trainer and other non-Pokémon cards** use the printed name slugified: `ナツメの眼` (Sabrina's Gaze) is `sabrinas-gaze-01`, with `species` set to the same human-readable name.

- [ ] **Step 3: Assign IDs and append rows**

Counters run per species across the **whole registry**, not per page. Before assigning, grep for an existing entry:

```bash
grep -i "^| umbreon-" docs/card-registry.md
```

Append rows to the table in `docs/card-registry.md`. Sorting happens in Task 5; keep them grouped by page for now so a reviewer can check a page against its image.

- [ ] **Step 4: Validate**

Run: `python scripts/check-registry.py docs/card-registry.md`
Expected: row count matching the pockets you recorded, zero `ERROR` lines. Duplicate and confirmation reports will be non-empty and that is fine — they are reviewed in Task 5.

- [ ] **Step 5: Commit**

```bash
git add docs/card-registry.md
git commit -m "Seed registry from Volume 1 chapters I-III"
```

---

## Task 3: Seed Volume 1, chapters IV–V

**Files:**
- Modify: `docs/card-registry.md`

**Interfaces:**
- Consumes: rows and per-species counters from Task 2. Continue counters; do not restart them.
- Produces: rows for the remaining six Volume 1 pages.

**Pages in this task:**

| Image | Theme |
|---|---|
| `static/images/binder/volume-1/intimidation_1.webp` | Intimidation |
| `static/images/binder/volume-1/on_attack_1.webp` | On the Attack |
| `static/images/binder/volume-1/contemplation_1.webp` | Contemplation |
| `static/images/binder/volume-1/elemental_solitude_1.webp` | Elemental Solitude |
| `static/images/binder/volume-1/legendary_bearing_1.webp` | Legendary Bearing p1 |
| `static/images/binder/volume-1/legendary_bearing_2.webp` | Legendary Bearing p2 |

- [ ] **Step 1: Convert to PNG**

```bash
OUT=/tmp/claude-1000/-home-tng-workspace-binderplan/2e24ee4d-3042-400e-95e2-350be0a647fb/scratchpad
python3 -c "
from PIL import Image
import pathlib
out = pathlib.Path('$OUT')
names = ['intimidation_1','on_attack_1','contemplation_1','elemental_solitude_1','legendary_bearing_1','legendary_bearing_2']
for n in names:
    Image.open(f'static/images/binder/volume-1/{n}.webp').convert('RGB').save(out / f'{n}.png')
    print(n)
"
```

- [ ] **Step 2: Read each page and record its cards**

Same procedure and same field rules as Task 2 Step 2. `intimidation_1.webp` has been read already during design and contains, in reading order: Mewtwo EX (EN), ナツメの眼 / Sabrina's Gaze trainer (JP), バクフーン / Typhlosion (JP), ムウマ / Misdreavus (JP), ルカリオVSTAR / Lucario VSTAR (JP, `s12a 225/172`), Houndour (EN, `113/165`), キテルグマ / Bewear (JP), ガラガラ / Marowak (JP, delta species), ゲンガー / Gengar (JP, Lv.38, number illegible). Verify against the image rather than trusting this list.

- [ ] **Step 3: Assign IDs and append rows**

Continue per-species counters from Task 2. Grep before every assignment — this is where recurring species start colliding, and Umbreon, Mewtwo and Charmander are all expected to recur.

- [ ] **Step 4: Validate**

Run: `python scripts/check-registry.py docs/card-registry.md`
Expected: zero `ERROR` lines. Row count should now be roughly 100–110.

- [ ] **Step 5: Commit**

```bash
git add docs/card-registry.md
git commit -m "Seed registry from Volume 1 chapters IV-V"
```

---

## Task 4: Seed Volume 2

**Files:**
- Modify: `docs/card-registry.md`

**Interfaces:**
- Consumes: rows and counters from Tasks 2–3.
- Produces: the complete pass-1 registry.

**Pages in this task:**

| Image | Theme |
|---|---|
| `static/images/binder/volume-2/companions_1.webp` | Companions p1 |
| `static/images/binder/volume-2/companions_2.webp` | Companions p2 |
| `static/images/binder/volume-2/enduring_presence_1.webp` | Enduring Presence p1 |
| `static/images/binder/volume-2/enduring_presence_2.webp` | Enduring Presence p2 |
| `static/images/binder/volume-2/quiet_familiarity_1.webp` | Quiet Familiarity p1 |
| `static/images/binder/volume-2/threshold_1.webp` | Threshold |

**Note:** the design references a *Quiet Familiarity p2* holding the binder's one empty pocket, but no `quiet_familiarity_2.webp` exists in `static/images/binder/volume-2/`. Record this in Task 5's report as a gap — a binder page with no photograph is a hole in the registry, and the curator needs to know rather than have it silently omitted. Do not fabricate rows for it.

- [ ] **Step 1: Convert to PNG**

```bash
OUT=/tmp/claude-1000/-home-tng-workspace-binderplan/2e24ee4d-3042-400e-95e2-350be0a647fb/scratchpad
python3 -c "
from PIL import Image
import pathlib
out = pathlib.Path('$OUT')
names = ['companions_1','companions_2','enduring_presence_1','enduring_presence_2','quiet_familiarity_1','threshold_1']
for n in names:
    Image.open(f'static/images/binder/volume-2/{n}.webp').convert('RGB').save(out / f'{n}.png')
    print(n)
"
```

- [ ] **Step 2: Read each page and record its cards**

Same procedure and field rules as Task 2 Step 2.

- [ ] **Step 3: Assign IDs and append rows**

Continue per-species counters. Grep before every assignment.

- [ ] **Step 4: Sort the table by ID**

The table must be sorted so that species clusters sit adjacent — that is what makes duplicate review by eye possible and what the grep-before-assign workflow depends on.

```bash
python3 - <<'PY'
import re
from pathlib import Path
p = Path('docs/card-registry.md')
lines = p.read_text(encoding='utf-8').splitlines(keepends=True)
start = next(i for i, l in enumerate(lines) if l.startswith('| id |'))
sep = start + 1
body_end = sep + 1
while body_end < len(lines) and lines[body_end].startswith('|'):
    body_end += 1
body = sorted(lines[sep + 1:body_end], key=lambda l: l.split('|')[1].strip())
p.write_text(''.join(lines[:sep + 1] + body + lines[body_end:]), encoding='utf-8')
print(f'sorted {len(body)} rows')
PY
```

- [ ] **Step 5: Validate**

Run: `python scripts/check-registry.py docs/card-registry.md`
Expected: zero `ERROR` lines, total roughly 150–162 rows.

- [ ] **Step 6: Commit**

```bash
git add docs/card-registry.md
git commit -m "Seed registry from Volume 2 and sort by id"
```

---

## Task 5: Pass-2 report and curator review gate

**Files:**
- Create: `docs/registry-confirmation.md` (temporary — deleted in Task 9)

**Interfaces:**
- Consumes: the complete pass-1 registry and `scripts/check-registry.py` reports.
- Produces: a review document for the curator. **This task ends by stopping and waiting for the curator.** Do not proceed to Task 6 without their answers.

- [ ] **Step 1: Generate the reports**

```bash
python scripts/check-registry.py docs/card-registry.md > /tmp/claude-1000/-home-tng-workspace-binderplan/2e24ee4d-3042-400e-95e2-350be0a647fb/scratchpad/report.txt
cat /tmp/claude-1000/-home-tng-workspace-binderplan/2e24ee4d-3042-400e-95e2-350be0a647fb/scratchpad/report.txt
```

- [ ] **Step 2: Write the review document**

Create `docs/registry-confirmation.md` with four sections, in this order:

1. **Blocked — species unreadable.** Cards seen in a photo but not identifiable, so **not yet in the registry** and holding no ID. One line each: page image, pocket position, what is visible. These are the only cards the curator must resolve before the registry is complete.
2. **Duplicate printing candidates.** From the `duplicate printings` report — confirmed rule violations under the §2 rule added in Task 8. Give both IDs, the shared printing, and the two source images.
3. **Confirmation queue, clusters first.** From the `needs physical confirmation` report. Species with two or more unresolved rows lead, because an undetected duplicate could be hiding there. State for each row what specifically was unreadable — `number obscured by price tag`, `glare across set symbol`, `vintage JP, Pokédex No. only`.
4. **Gaps.** Any binder page with no photograph, including the missing `quiet_familiarity_2` noted in Task 4.

Give real counts, not estimates. State plainly how many rows are `uncertain` versus `photo` — the honest ratio is the point of this document.

- [ ] **Step 3: Commit and stop**

```bash
git add docs/registry-confirmation.md
git commit -m "Add pass-2 confirmation report for curator review"
```

**STOP.** Present the four sections to the curator and wait. IDs are provisional only until they sign off; after Task 6 the never-rewrite rule takes full effect and nothing here can be changed.

---

## Task 6: Apply curator answers and freeze

**Files:**
- Modify: `docs/card-registry.md`
- Modify: `docs/registry-confirmation.md`

**Interfaces:**
- Consumes: the curator's answers from the Task 5 gate.
- Produces: the frozen registry. Every subsequent ID is permanent from the moment it is written.

- [ ] **Step 1: Register the previously-blocked cards**

For each species the curator identified, assign an ID and add a row. Set `confidence: confirmed` where they read the physical card, `photo` where they identified it from the image.

- [ ] **Step 2: Apply corrections to existing rows**

Fill in sets and numbers the curator confirmed; upgrade those rows to `confidence: confirmed`. **This is the only moment an ID may be changed** — if the curator's identification means a slug is wrong and nothing has cited it yet, correct it now. After this task, correct the `species` column instead and leave the ID.

- [ ] **Step 3: Re-sort and validate**

Re-run the sort snippet from Task 4 Step 4, then:

Run: `python scripts/check-registry.py docs/card-registry.md`
Expected: zero `ERROR` lines.

- [ ] **Step 4: Record what remains unresolved**

Rewrite `docs/registry-confirmation.md` to hold only what is *still* open after the curator's pass — rows that stay `uncertain` because the card was not available to check, and any duplicate candidates not yet resolved. Delete the sections that are now closed. This file is the standing list of cards needing physical confirmation, and it is a legitimate output rather than a defect.

- [ ] **Step 5: Commit**

```bash
git add docs/card-registry.md docs/registry-confirmation.md
git commit -m "Freeze registry after curator confirmation pass"
```

---

## Task 7: Restart the ledger citing IDs

**Files:**
- Modify: `docs/ledger.md`

**Interfaces:**
- Consumes: `docs/card-registry.md` (referenced by path from the new conventions block).
- Produces: an empty, ID-citing ledger.

The curator holds a printed copy of the existing entries for executing the pending swaps, so the operational content is preserved outside the repository. The entries also remain in git at `a254855`.

- [ ] **Step 1: Wipe the entries**

Delete everything from the `---` separator that follows the `## How to use this file` section to the end of the file. Keep the title, the intro paragraph, and the conventions section.

- [ ] **Step 2: Add the Card IDs block**

Insert after the **Vocabulary** block and before **Citations**:

```markdown
**Card IDs.** Entries cite cards by registry ID from [`card-registry.md`](card-registry.md), written as `Umbreon (umbreon-02)` — species alongside the ID for readability, neither alone. Species names by themselves are ambiguous: Umbreon appears three times across the binder, Mewtwo four, Charmander three, and there are two copies of Houndoom G Lv.45. A card with no ID gets one at the moment it is first cited here.
```

- [ ] **Step 3: Rewrite the No backfill block**

Replace the existing **No backfill** paragraph with:

```markdown
**No backfill.** This ledger restarts 2026-08-01 with the adoption of card IDs. An earlier ledger covering the holding-box sort was superseded and removed; it survives in git at commit `a254855` if the reasoning is ever needed. Moves are not reconstructed from memory — doing so would put fiction into an audit trail.
```

- [ ] **Step 4: Verify nothing dangles**

Run: `grep -n "holding-box-placement" docs/ledger.md`
Expected: no output. The only links to that file were inside the wiped entries.

Run: `grep -c "" docs/ledger.md`
Expected: roughly 30 lines — title, intro, conventions, nothing else.

- [ ] **Step 5: Commit**

```bash
git add docs/ledger.md
git commit -m "Restart ledger citing card registry IDs"
```

---

## Task 8: Record capacity and duplication rules in the audit prompt

**Files:**
- Modify: `CURATORIAL_AUDIT_PROMPT.md` — insert into §2, after the *Volume 2 — Active Curation* block and before the `---` that closes the section.

**Interfaces:**
- Consumes: nothing.
- Produces: the §2 rules that Task 5's duplicate report is judged against.

Both rules are already in force but were never written down. A grep confirms the document currently says nothing about capacity or duplication — the same class of gap the old ledger flagged around the undocumented Trainer Full Arts restriction.

- [ ] **Step 1: Confirm the gap still exists**

Run: `grep -n -i "duplicat\|binder capacity\|structurally closed" CURATORIAL_AUDIT_PROMPT.md`
Expected: exactly one hit — `- Volume 1 is **structurally closed**.` in §2. No `duplicat` hit and no `binder capacity` hit.

Do not grep for the bare word `full`: it matches *Full-art*, *fully realized*, and the document title, so it will report a false conflict.

If a real hit appears, read it and reconcile before inserting, rather than adding a contradicting rule.

- [ ] **Step 2: Insert both blocks**

```markdown
### Binder Capacity
- **Assume every existing theme in both volumes is full unless a specific empty pocket has been verified.** As of 2026-08-01 they are.
- Placing into an existing theme is therefore a **challenge, not an addition**: a card enters only by displacing a named incumbent, which then leaves the binder.
- Any analysis recommending placements into existing themes without naming the card each one evicts has not applied this rule.
- **Volume 2 has room for additional themes.** A new theme that passes §8 adds pages rather than displacing cards, so its cards evict nothing. This is the only additive path into the binder.

### No Duplicate Printings
- The same printing — same card, same set, same collector number, same language — must not appear twice across Volumes 1 and 2.
- A second copy goes to the holding pool or is released.
- Different illustrations of the same species in different themes are **not** duplicates and are permitted.
```

- [ ] **Step 3: Verify placement**

Run: `sed -n '/^## 2\./,/^## 3\./p' CURATORIAL_AUDIT_PROMPT.md`
Expected: both new blocks appear inside §2, after *Volume 2 — Active Curation*, and §3 still opens correctly.

- [ ] **Step 4: Commit**

```bash
git add CURATORIAL_AUDIT_PROMPT.md
git commit -m "Document binder capacity and no-duplicate-printings rules in section 2"
```

---

## Task 9: Retire the placement document and verify

**Files:**
- Delete: `docs/holding-box-placement.md`

**Interfaces:**
- Consumes: everything above. This task runs last because the placement document is a seeding source until the registry stands.

- [ ] **Step 1: Confirm nothing references it**

Run: `grep -rn "holding-box-placement" --include="*.md" --include="*.toml" --include="*.html" . | grep -v docs/superpowers`
Expected: only the file's own self-reference, if any. Any other hit must be resolved before deleting.

- [ ] **Step 2: Delete it**

```bash
git rm docs/holding-box-placement.md
```

- [ ] **Step 3: Full verification**

```bash
python -m pytest scripts/test_check_registry.py -v
python scripts/check-registry.py docs/card-registry.md
hugo --gc --minify --baseURL http://localhost/ --quiet && echo "hugo build OK"
git status --short
```

Expected: tests pass; validator reports zero `ERROR` lines; Hugo builds clean (it should be entirely unaffected — `docs/` is outside `content/` and has no mount); working tree clean apart from the staged deletion.

- [ ] **Step 4: Confirm the design's hard constraint holds**

Run: `grep -n -i "volume\|spread\|pocket\|slot\|location\|theme" docs/card-registry.md | grep -v "^[0-9]*:.*first_seen" | head -20`

Read the hits. Any that record **where a card currently sits** is a violation of the design's central rule and must be removed. Mentions inside the conventions header explaining that location is *not* tracked are correct and expected. `first_seen` values naming an image file are provenance, not location, and are correct.

- [ ] **Step 5: Commit**

```bash
git add -A
git commit -m "Retire holding-box placement document"
```

---

## Self-Review Notes

Spec coverage checked section by section: scheme (Task 1 grammar + Task 2 slug rules), collision rules (Task 1 validator + grep-before-assign in Tasks 2–4), metadata depth and the no-location rule (Task 1 columns + Task 9 Step 4 audit), registry file (Task 1), scope (Tasks 2–4 page lists), assignment timing (Task 7's Card IDs block), two-pass seeding and the review gate (Tasks 2–6), duplicate detection (Task 1 `duplicate_printings` + Task 5 report + Task 8 rule), photograph limits (Task 5 Step 2 sections 1 and 3), ledger changes (Task 7), audit prompt changes (Task 8), placement doc retirement (Task 9).

Two things this plan adds beyond the spec, both discovered while spiking the images:

- **Vintage Japanese cards carry a Pokédex number, not a collector number** (Task 2 Step 2). The `set + number` duplicate key is inherently weaker for them regardless of photo quality.
- **`quiet_familiarity_2` has no photograph** (Task 4). The design assumes a page there. Reported as a gap rather than silently omitted.
