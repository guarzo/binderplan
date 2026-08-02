# Handoff — add a by-page view to the confirmation worklist

**Run this after PR #12 merges.** Everything below assumes `main` contains the card
registry work.

> **Before your first commit:** stage explicit paths, never `git add -A`. The previous
> session ran several agents concurrently in `.claude/worktrees/card-registry`, and one commit
> was contaminated by `-A` sweeping in another agent's stray files.

## The ask

`docs/registry-confirmation.md` lists cards needing a physical check, grouped by **species
cluster**. That grouping is right for spotting duplicate printings, but wrong for actually
walking the binder — you end up flipping between pages constantly.

Add a **by-page** view so the curator can open the binder to one page, check every unresolved
card on it, and move on. Keep the species view; this is an addition, not a replacement.

## Where things stand

- `docs/card-registry.md` — 175 rows, one per card. Columns:
  `id | species | card_name | language | set | number | confidence | first_seen | notes`
- `scripts/check-registry.py` — validator plus `--worklist`, which regenerates the confirmation
  document from the registry. `render_worklist(rows)` builds it; sections 1–3 and 5 are
  generated, section 4 ("Gaps and known issues") is hand-written narrative that must be carried
  forward manually on each regeneration.
- `scripts/test_check_registry.py` — 41 tests, all passing.
- 146 of 175 rows need a physical check, across 92 species.

Regeneration currently requires a manual splice, because the hand-written section 4 must
survive:

```bash
awk '/^## 4\. Gaps and known issues/,/^## 5\./' docs/registry-confirmation.md | sed '$d' > /tmp/hw4.md
python3 scripts/check-registry.py docs/card-registry.md --worklist > /tmp/gen.md
# splice /tmp/hw4.md over the placeholder section 4 in /tmp/gen.md, then write the result
```

**Fix this as part of the task.** An `awk` range extract plus a by-hand splice, repeated on
every regeneration, will eventually drop the narrative silently — and nothing would fail. Have
`--worklist` take the existing `docs/registry-confirmation.md` (default path, overridable),
extract its section 4, and emit it in place of the placeholder; fall back to the placeholder
when the file is absent or the section is missing. That is a small change to one function, it
deletes a manual step this handoff otherwise has to describe twice, and it wants a test of its
own for the fallback path.

## Four gotchas — these are the whole difficulty

### 1. `first_seen` filenames are NOT reliable page labels

The registry's `first_seen` names the image a row was read from. Several of those filenames
**misdescribe what they show**, because the pre-2026-08-01 photo set had a systematic off-by-one
in Volume II — every page after `quiet_familiarity_1` carried the next page's name, since the
shoot missed the Threshold page entirely.

Grouping naively on the filename would send the curator to the wrong page four times. Use an
explicit image → page map. The correct mapping, verified against the images:

| `first_seen` image | Actual page |
|---|---|
| `calm_nature_1.webp` | V1 · Calm in Nature |
| `world_people_1.webp` | V1 · World of People |
| `at_rest_1.webp` | V1 · At Rest |
| `joyful_action_1.webp` | V1 · Joyful Action |
| `awakened_power_1.webp` | V1 · Awakened Power p1 |
| `awakened_power_2.webp` | V1 · Awakened Power p2 |
| `legendary_bearing_1.webp` | V1 · Legendary Bearing p1 |
| `legendary_bearing_2.webp` | V1 · Legendary Bearing p2 |
| `intimidation_1.webp` | V1 · Intimidation |
| `on_attack_1.webp` | V1 · On the Attack |
| `elemental_solitude_1.webp` | V1 · Elemental Solitude |
| `contemplation_1.webp` | V1 · Contemplation |
| `companions_1.webp` | V2 · Companions p1 |
| `companions_2.webp` | V2 · Companions p2 |
| `quiet_familiarity_1.webp` | V2 · Quiet Familiarity p1 |
| `enduring_presence_1.webp` | **V2 · Quiet Familiarity p2** ← misnamed |
| `enduring_presence_2.webp` | **V2 · Enduring Presence p1** ← off by one |
| `threshold_1.webp` | **V2 · Enduring Presence p2** ← off by one |
| `IMG_6865.HEIC` | **V2 · Threshold** ← never published before the reshoot |

Present pages in that order — it is binder order, which is what makes the document walkable.

These 19 images are exactly the set of non-`IMG_*` `first_seen` values in the registry today, so
the map is complete as written. Each maps to 9 rows except `enduring_presence_1.webp`, which has
8: that page (Quiet Familiarity p2) held the single empty pocket in either volume, and
`cinccino-01` — an `IMG_*` swap-in, see gotcha 2 — fills it. After the merge every page is 9.
`docs/ledger.md` records this.

Note the `static/images/binder/` **files** were renamed correctly during the gallery refresh;
only the registry's historical `first_seen` values still carry the old names, deliberately, because
`first_seen` is immutable provenance. Do not "fix" the registry to match.

### 2. The five `IMG_*.HEIC` singles are swap-ins, not pages

These are single cards added after the original shoot. Each belongs to an existing page and must
be **merged into that page's group**, not shown as a one-card page:

| ID | `first_seen` | Belongs to |
|---|---|---|
| `pikachu-06` | `IMG_6842.HEIC` | V1 · At Rest |
| `zapdos-01` | `IMG_6847.HEIC` | V1 · Legendary Bearing p1 |
| `ampharos-01` | `IMG_6853.HEIC` | V1 · Elemental Solitude |
| `kangaskhan-01` | `IMG_6858.HEIC` | V2 · Companions p2 |
| `cinccino-01` | `IMG_6860.HEIC` | V2 · Quiet Familiarity p2 |

(`IMG_6865.HEIC` is different — it is a whole page, per the table above.)

**Never dispatch on the `IMG_*` filename pattern.** `IMG_6865.HEIC` matches it and carries 9
rows as a full page, while these five are singles. The two tables above are the only source of
truth: an image is a page if it is in the gotcha-1 map, a swap-in if it is in this one, and
unmapped otherwise (see Requirements). A pattern match would misplace nine cards.

### 3. Four cards in the registry are no longer in the binder

`ursaring-01`, `typhlosion-02`, `umbreon-03`, `electrode-01` were swapped out. They keep their
rows and IDs — correct, the registry records identity, not location — but a by-page view would
list them on pages they have left, sending the curator hunting for cards that aren't there.

Only three of the four actually reach this view: `electrode-01` is `photo` with both `set` and
`number` read, so `confirmation_queue()` already filters it out.

**Handle it with a caveat in the section preamble** pointing at `docs/ledger.md`, which is where
movement lives. That is proportionate for three rows. Do not build ledger parsing for this —
`ledger.md` is prose with tables, and a fragile parser is worse than a clear sentence.

Do not solve it by writing location into the registry. That is the one thing the design forbids;
see `docs/superpowers/specs/2026-08-01-card-registry-design.md`.

### 4. The page map is about images, not cards — keep it that way

The map above is a stable fact: a photograph shows what it shows. That is why it can live in the
script. It is **not** a card → page index, which would rot on the first swap. If you find yourself
wanting to store which page a *card* is on, stop — that is the inventory the curator explicitly
rejected.

## Suggested shape

A new section in the generated worklist, after the species view:

```markdown
## 6. Confirmation queue by page

Walk the binder in order. Each page lists only its unresolved rows.
Cards photographed on a page but since swapped out still appear here — see `ledger.md`.

### V1 · Calm in Nature

| ID | Card name | Unreadable |
|---|---|---|
| ... | ... | ... |
```

Drop the source-image column here (it is implied by the page) and keep ID, card name with
language, and the `notes` text saying what specifically was unreadable.

## Requirements

- TDD. Write the failing tests first; do not weaken or delete any of the 41 existing ones.
- Cover at minimum: pages appear in binder order; a swap-in `IMG_*` row merges into its page's
  group; `IMG_6865.HEIC` renders as a full 9-row page and is *not* treated as a swap-in; a page
  with no unresolved rows is omitted; the off-by-one images render their corrected page labels.
- An unmapped `first_seen` must not be silently dropped — emit it under an explicit
  "Unmapped source image" heading so a future image cannot vanish from the worklist.
- Section 4 carry-forward happens in the script, with a test for the missing-file fallback.
- Regenerate `docs/registry-confirmation.md`.

## Verify

```bash
python3 -m pytest scripts/test_check_registry.py -q      # all pass
python3 scripts/check-registry.py docs/card-registry.md  # 175 rows, 0 ERROR
python3 scripts/check-registry.py docs/card-registry.md --worklist | head -40
hugo --gc --minify --baseURL http://localhost/ --quiet   # docs/ is outside content/, must still build
```

Also confirm every ledger ID citation still resolves:

```bash
for id in $(grep -oE '`[a-z0-9-]+-[0-9]{2}`' docs/ledger.md | tr -d '`' | sort -u); do
  grep -qE "^\| $id " docs/card-registry.md || echo "DANGLING $id"
done
```
