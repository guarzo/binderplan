# Handoff — filling in set and number from the physical cards

**Status, 2026-09-19: the confirmation pass is done.** The rest of this file is the procedure for
the next time a row needs filling or correcting — a new card joining the binder, or a misread found
later.

## Where it stands

`docs/card-registry.md` holds 175 rows, one per card. The pass started with 146 `uncertain` rows
and duplicate detection able to compare only 31 of them (18%). It now compares 164 of 175, and
finds no duplicate printings. The pass had two sources:

- **The owner's doubleholo catalogue**, entered card by card with each card in hand and exported
  one lot per binder chapter. Rows were matched on species + collector number, and within a
  chapter where a species had several cards. Those values count as read from the card.
- **An in-hand check sheet** for everything the export could not settle: 49 cards where the export
  and the photo read disagreed, or a field was still blank. Neither source was reliably right on
  its own — the photo reads misread digits through sleeves, and the export sometimes picked the
  wrong catalogue entry — which is why disagreements went to the card rather than to a rule.

What is left in the queue, 22 rows, is expected to stay there:

| Rows | Why |
|---|---|
| 21 | Vintage Japanese Pokédex-number prints (`No.xxx`). Uncertain by rule — see below. |
| `umbreon-03` | In the holding box, not the binder. Optional. |

`docs/registry-confirmation.md` is the worklist. Regenerate it when you finish (see below) rather
than editing it by hand.

## How to work

Edit `docs/card-registry.md` directly. Columns:

```
| id | species | card_name | language | set | number | confidence | first_seen | notes |
```

For each card you pick up:

1. Fill in `set` and `number` from what is **printed on the card**.
2. Set `confidence` to `confirmed` — that value means "read from the physical card in hand" and is
   what removes the row from the worklist. Nothing else does.
3. Trim the `notes` if it now says something stale like `number illegible after crop attempt`. Keep
   anything still true (`distinct from umbreon-01/02`, `AR rarity mark`).

Never touch `id`. Those are cited by `docs/ledger.md` now, and rewriting one breaks every reference.
If a card turns out to be a different species than its ID suggests, correct the `species` column and
leave the ID alone — that is the design working, not a bug. (Three IDs were renumbered pre-merge,
when nothing cited them; that window has closed.)

Never record where a card sits. No volume, theme, page or pocket, in any column including `notes`.
The registry records what a card **is**; movement belongs in `docs/ledger.md`.

## Recording the set

Record **what is printed**, with the conventions the column already follows:

- Japanese set codes as printed, lowercase letter prefix: `sv11B`, `s12a`, `sv5K`, `sm1`, `m1S`.
  Older Japanese sets that print no code use the set's name: `Rulers of the Heavens`,
  `Flight of Legends`.
- English sets by **name**, even where a modern card prints a code: write `Scarlet & Violet`, not
  `SVI`; `Black Bolt`, not `BLK`. Most English rows were named before modern codes came up, and a
  code on one row would never match a name on another.
- Chinese set codes as printed: `CSM2BC`, `CSV5C`.
- Promo markers: `SVP`, `XY`, `S-P`, `XY-P`, with the number as printed (`224/S-P`, `155/XY-P`).
- Numbers as printed. Modern Japanese cards print three digits both sides — `087/086`, not `87/86`.
- A card that prints no number (most vintage trainers, some movie promos) gets a blank `number` and
  `no number printed` in `notes`. That row can still be `confirmed`: the blank is the reading.

One consistency rule that matters: **duplicate detection compares these strings** (case-insensitively).
If the same printing appears twice and you write `Base Set` on one row and `base set` on the other,
they will still match — but `Base` versus `Base Set` will not. When you meet a set you have already
recorded elsewhere, grep for it and reuse the exact spelling:

```bash
grep -o '| [^|]*Neo Genesis[^|]*|' docs/card-registry.md | head
```

Vintage Japanese cards print a Pokédex number (`No.157`) rather than a collector number. Put that in
`number`, name the era in `set` only if it is genuinely identifiable from the card, and leave
`confidence` as `uncertain` — a Pokédex number is not a set-unique key, so those rows stay weaker
than the rest even after handling.

## Validate and commit as you go

After each batch — a page, or a species cluster — run:

```bash
python3 scripts/check-registry.py docs/card-registry.md
```

Expect `175 rows` and zero `ERROR` lines. It will catch a malformed row, a bad `confidence` value, a
duplicate or non-contiguous ID, and any row marked `photo` with a blank field.

It also prints the duplicate report. **If a duplicate printing appears, stop and read it** — that is
a rule violation under `CURATORIAL_AUDIT_PROMPT.md` §2 (the same printing must not sit in both
volumes). It is a curatorial decision, not a data fix: one copy leaves, and that move earns a ledger
entry.

Commit each batch. Do not hold a long session's work uncommitted.

```bash
git add docs/card-registry.md
git commit -m "Confirm set and number for <what you did>"
```

## When you finish a session

Regenerate the worklist so it reflects what is left. Section 4 is hand-written narrative the
generator cannot reproduce, so it has to be carried across:

```bash
awk '/^## 4\. Gaps and known issues/,/^## 5\./' docs/registry-confirmation.md | sed '$d' > /tmp/hw4.md
python3 scripts/check-registry.py docs/card-registry.md --worklist > /tmp/gen.md
python3 - <<'PY'
import re
gen = open('/tmp/gen.md').read()
hw = open('/tmp/hw4.md').read()
out = re.sub(r'^## 4\. Gaps and known issues\n.*?(?=^## 5\.)', hw, gen, flags=re.S | re.M)
open('docs/registry-confirmation.md', 'w').write(out)
PY
python3 -m pytest scripts/test_check_registry.py -q
git add docs/card-registry.md docs/registry-confirmation.md
git commit -m "Regenerate confirmation worklist"
```

The generator emits a placeholder §4 telling you to copy the real one forward; the splice above
replaces it. Read the result before committing — if §4 has gone stale against the work you just did,
this is the moment to update it.

The queue count in the regenerated header is the honest progress marker: 146 when the pass began,
22 after it. Compare against the current `docs/registry-confirmation.md` header rather than either
number.

## What good looks like

- A blank you could not read is still a correct answer. If a set code genuinely is not printed on
  the card — which is common on promos and some illustration rares — leave it blank and say so in
  `notes`. Do not look it up online and enter it as though you read it; the column is a record of
  the object, and an inferred value that looks confirmed is worse than a blank.
- If you look something up and want to keep it, put it in `notes` as clearly inferred, leave `set`
  blank, and leave `confidence` as `uncertain`.
- The line between a reading and a lookup: the owner's own catalogue entry, made with the card in
  hand, is a reading. Turning a set the owner named into its printed code (TCGdex maps
  `Black Bolt` to `SV11B`) is a translation of that reading, not a lookup — but check the result
  against the owner's set name. TCGdex matches on name and number, and a vintage card's Pokédex
  number can hit a modern card with the same number (`mew-05` briefly landed in the 151 set).
- Registry rows persist when cards move or leave, so the current outside-binder population changes
  over time. Do not infer occupancy from this historical worklist. Read `docs/ledger.md` forward and
  consult `docs/registry-confirmation.md` §4 for the latest reconciled summary. In particular,
  `ursaring-01` re-entered the binder in Companions on 2026-09-21.

## Reference

- Design and reasoning: `docs/superpowers/specs/2026-08-01-card-registry-design.md`
- Registry conventions: the "How to use this file" header in `docs/card-registry.md`
- Capacity and duplicate rules: `CURATORIAL_AUDIT_PROMPT.md` §2
- **Walking the binder: use §6 of the worklist, "Confirmation queue by page."** It shipped in #13
  and holds the same rows as §3 regrouped by page, so you can open to one page and clear every card
  on it instead of flipping back and forth. Use §3 when you are chasing a species cluster for
  duplicate risk, §6 when you are physically working through the binder.
  (`docs/superpowers/next-session-by-page-worklist.md` is the handoff
  that built it, kept for history; it is not work still to do.)
