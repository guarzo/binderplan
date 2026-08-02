# Handoff — filling in set and number from the physical cards

**Use this when you sit down with the binder to work through the confirmation list.** Paste it
into a fresh session; it assumes PR #12 has merged.

## What the work is

`docs/card-registry.md` holds 175 rows, one per card. **146 of them are `uncertain`** — the set
code, the collector number, or both could not be read from photographs shot through sleeves. Those
fields can only be closed by handling the cards.

| Rows | State | What's needed |
|---|---|---|
| 75 | `number` read, `set` blank | the set |
| 69 | both blank | both |
| 2 | both present, still `uncertain` | verify — `cinccino-01` (ambiguous digit), `lugia-01` (era inferred, not printed) |

`docs/registry-confirmation.md` is the worklist: which cards, and what specifically was unreadable
on each. Regenerate it when you finish (see below) rather than editing it by hand.

## Start with the 75 number-only rows

They are the highest-value subset, and not for tidiness. Duplicate detection needs **all four** of
species + set + number + language to match, so it currently runs against only 31 of 175 rows (18%).
Filling in the sets on those 75 would take coverage to about 61% — turning the no-duplicate-printings
rule from aspiration into something actually enforced.

Within that, do the **species clusters first** (section 3 of the worklist lists them first for this
reason). A species with several unresolved rows is exactly where an undetected duplicate hides.
The largest are pikachu (5), gengar (4), jirachi (4), umbreon (4), joltik (3), cubone (2).

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

Record **what is printed**, not a normalised form. The column already holds both styles because
both appear on cards:

- Japanese set codes as printed: `sv1b`, `s12a`, `sm1`, `s6c`, `sv11B`
- English set names as printed: `Neo Destiny`, `Neo Revelation`, `Cosmic Eclipse`, `Platinum`
- Promo markers: `SVP`, `XY`

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
# splice /tmp/hw4.md over section 4 in /tmp/gen.md, write the result to docs/registry-confirmation.md
python3 -m pytest scripts/test_check_registry.py -q
git add docs/card-registry.md docs/registry-confirmation.md
git commit -m "Regenerate confirmation worklist"
```

The queue count in the regenerated header is the honest progress marker: it starts at 146.

## What good looks like

- A blank you could not read is still a correct answer. If a set code genuinely is not printed on
  the card — which is common on promos and some illustration rares — leave it blank and say so in
  `notes`. Do not look it up online and enter it as though you read it; the column is a record of
  the object, and an inferred value that looks confirmed is worse than a blank.
- If you look something up and want to keep it, put it in `notes` as clearly inferred, leave `set`
  blank, and leave `confidence` as `uncertain`.
- Four cards in the registry are no longer in the binder (`ursaring-01`, `typhlosion-02`,
  `umbreon-03`, `electrode-01`). They still have rows, correctly. Do not hunt for them; if you want
  to confirm them, they are in the holding box.

## Reference

- Design and reasoning: `docs/superpowers/specs/2026-08-01-card-registry-design.md`
- Registry conventions: the "How to use this file" header in `docs/card-registry.md`
- Capacity and duplicate rules: `CURATORIAL_AUDIT_PROMPT.md` §2
- A separate deferred task adds a by-page view to the worklist, which will make walking the binder
  easier than the species view: `docs/superpowers/next-session-by-page-worklist.md`. If that is
  already done, work from the by-page section instead.
