# Card registry — stable identifiers for the binders

Design note. 2026-08-01.

## The problem

Cards are referred to by species name, and species names are not unique. Umbreon appears three
times across the binder, Mewtwo four, Charmander three. There are two physical copies of Houndoom G
Lv.45 (Rising Rivals 50/111). An instruction like *"remove Umbreon from Elemental Solitude"* cannot
be resolved today, and `docs/ledger.md` is append-only — references written into it must stay
resolvable years after the card has moved.

## The constraint that shapes everything

**The identifier must survive a move.** Volume/spread/slot is disqualified as an identifier. Cards
are swapped between themes as the normal operation of the binder; a positional ID would invalidate
every historical reference the moment a card moved. Position is a property recorded *against* a
card, never its identity.

Under this scheme, a card's ID is unchanged when it moves from Elemental Solitude to Contemplation,
unchanged when it leaves the binder for the holding box, and unchanged after release. The registry
row is never touched by any of those events. The ledger records them.

## Scheme

`<species-slug>-<NN>` — zero-padded to two digits, assigned in registration order within species.

```
umbreon-01   umbreon-02   umbreon-03
mewtwo-01 … mewtwo-04
houndoom-01  houndoom-02
```

The slug is the **English Pokédex species name only**. No mechanics, prefixes, or set qualifiers:
not `houndoom-g-01`, not `dark-houndoom-01`, not `mewtwo-ex-01`. `ドダイトス Lv.X` is `torterra-01`;
`Jasmine's Ampharos` is `ampharos-0N`; `M Gengar EX` is `gengar-0N`. Using the English name across
all languages gives one cross-language key, so `umbreon-01` (EN) and `umbreon-02` (JP) sort
together.

Non-Pokémon cards use the printed card name slugified: `n-01`, `pokemon-communication-01`.

**Why species plus a meaningless counter.** Species is the only attribute a photograph reliably
yields — set numbers hide behind price tags and glare, language is usually but not always legible.
The ID is therefore built from the one dependable input plus a counter that carries no semantics and
so can never be falsified. Everything falsifiable — language, set, number, printed name — lives in
metadata columns where it can be corrected without breaking a reference.

**Alternatives rejected.** An opaque sequence (`C-001`) is maximally stable but makes ledger prose
unreadable without a lookup, optimising the wrong property. A set-and-number ID (`neo-32-en-a`)
encodes genuine printing identity but stalls on cards whose number cannot be read, forcing
placeholders that must later be rewritten — which breaks every reference already written against
them.

## Collision rules

| Situation | Resolution |
|---|---|
| Same species, different language | Different IDs. Language is a metadata column. |
| Same printing, two physical copies | Different IDs. The two Houndoom G Lv.45 get separate `houndoom-NN` entries distinguished only by counter. |
| Set/number unreadable | ID assigned from species alone. `set`/`number` blank, `confidence: uncertain`. |
| Species unreadable | Held out of the registry during seeding (see below). After seeding, assigned from best guess. |
| Unsure whether it is a new copy or an existing entry | **Assign a new ID.** |

The last rule is deliberately asymmetric. A phantom entry — two IDs, one physical card — is
recoverable: mark one `superseded-by: <id>` and every existing reference still resolves. A merge —
one ID, two physical cards — is not recoverable, because every entry citing that ID becomes
permanently ambiguous, which is the exact failure this scheme exists to prevent. When in doubt,
split.

**IDs are never rewritten.** If `houndour-03` is later confirmed to be a Houndoom, the ID stays and
the `species` column is corrected. The registry will accumulate a small number of IDs that look
wrong. That is the price of references that resolve in 2031, and it is cheaper than any alternative
that breaks history.

## Metadata depth: identity and provenance, no location

The registry holds identity plus the immutable observation that established it. It holds **no
current-location field**.

This is deliberate. `docs/ledger.md` states it is not an inventory; a location column would
recreate one, and would need editing on every swap. A stale location index is worse than none,
because it misleads an audit that trusts it.

The question *"where is `umbreon-02` now?"* is answered by grepping `ledger.md` for the ID and
reading forward. Every ledger entry is a dated observation of a move, so position is reconstructed
from history rather than stored as mutable state. Dated past facts cannot rot.

What the registry does hold is `first_seen` — the photograph and date the row was derived from. That
is provenance, not location: it stays true after the card moves to Contemplation, after it goes to
the holding box, and after it is released. It is the audit trail back to the specific image a
questionable read came from, so a bad attribution can be re-checked against the original evidence
rather than re-derived from scratch.

## Registry file

`docs/card-registry.md` — one Markdown table sorted by ID, with a short "How to use this file"
header mirroring `ledger.md`. Markdown over CSV or YAML because it renders on GitHub, greps the same
way the ledger does, and ~160 rows needs nothing more.

| Column | Notes |
|---|---|
| `id` | `species-NN`. Permanent, never rewritten. |
| `species` | English Pokédex name. Correctable. |
| `card_name` | As printed — `Houndoom G Lv.45`, `ドダイトス Lv.X`. Carries the qualifiers the ID drops. |
| `language` | EN / JP / ZH |
| `set` | Blank if unread. |
| `number` | Blank if unread. |
| `confidence` | `confirmed` (read in hand) / `photo` (legible in photo) / `uncertain` (inferred or obscured) |
| `first_seen` | Image filename + date. Immutable. |
| `notes` | Free text: `superseded-by: <id>`, "price tag over number", etc. |

## Scope

**Volumes 1 and 2 only** — 18 spread photos in `static/images/binder/volume-1/` and `volume-2/`
(excluding dividers and contents cards), roughly 160 pockets. This covers every theme the curatorial
audit governs and every card the ledger has reason to cite.

The Emolga masterset, stamped cards, trainer full arts, and slabs are **out of scope** for this pass.
They use the same scheme when a reason arises to register them; nothing here needs revisiting to
extend to them.

## Assignment: on first durable citation

A card gets an ID the moment it is first named in a ledger entry or placement analysis — whether
that is a placement, a contested call, an EDGE hold, or a release. Assigned by whoever writes that
entry, after grepping the registry for an existing match.

Rejected alternatives: *on entry to the collection* would mean cataloguing every bulk purchase
including immediately-releasable cards; *on first placement into a binder* would leave holding-box
releases and EDGE holds unciteable, which is a live gap — the ledger records every release, and
cards are released straight from the box without ever being placed.

## Seeding, in two passes

**Pass 1.** Work through the 18 spread photos. Register every card whose species can be read with
confidence. Fill `set` and `number` where legible, leave blank where not.
`docs/holding-box-placement.md` is a supporting source: it already names ~84 holding-box cards with
languages and partial set attributions.

**Pass 2 — curator review gate.** Everything that failed pass 1 is brought to the curator before the
file is finalised, split by what is actually blocked:

- **Species unreadable** → no ID assigned yet. Nothing can cite a card that cannot be named, so
  waiting costs nothing. The curator identifies it, then it is registered.
- **Species clear, set/number unreadable** → ID assigned (species is sufficient), row flagged
  `uncertain`, listed for physical confirmation. Reviewed, but not blocking.

**IDs are provisional until the curator signs off on pass 2.** This is a one-time carve-out from the
never-rewrite rule, and it is safe only because nothing has cited these IDs yet. Once signed off, the
registry is frozen and every subsequent ID is permanent from the moment it is written.

## What photographs cannot establish

This list is an expected output, not a failure. Identification comes from photos shot through
sleeves in nine-pocket pages, with price tags and glare.

- **Set and collector number**, whenever the bottom-corner strip is under a price tag, glare band,
  sleeve seam, or pocket edge. This is the common case, not the exception — that corner is the
  worst-lit and most-occluded part of a sleeved card.
- **Which physical copy is which**, for true duplicates. The two Houndoom G Lv.45 are visually
  identical, so which of the two gets the lower counter is an *arbitrary* assignment. The registry can
  establish that two cards exist; it cannot say which one is in hand. Adequate while they are
  interchangeable; inadequate the moment one is graded, damaged, or sold.
- **Edition and print-run markers** — 1st edition vs unlimited, shadowless, and holo vs reverse-holo
  under strong glare.
- **Reprints sharing artwork.** Identical illustration across two sets is indistinguishable without
  the number, so a card with an unread number may also have an unresolvable *set*.
- **Condition**, entirely. Sleeves hide edges and surface.

Pass 2 turns this into a concrete per-card list with the specific reason each entry is blocked.

## Changes to `docs/ledger.md`

The curator has taken a printed copy of the existing ledger for executing the pending swaps and
releases, so the operational content is preserved outside the repository. The digital entries are
therefore removed and the ledger restarts citing IDs.

- **Entries wiped.** All 2026-08-01 entries removed. They remain in git history at `a254855`.
- **"How to use this file" kept**, with these edits:
  - **Card IDs** — new block: entries cite cards by registry ID, written as `Umbreon (umbreon-02)`
    — species alongside the ID for readability, neither alone. A card with no ID gets one at the
    moment it is first cited.
  - **No backfill** — rewritten to note that a prior ledger existed and was superseded, pointing at
    `a254855`, so a future reader does not re-derive the full-binder constraint from scratch.
  - Append-only, what earns an entry, vocabulary, and citations are unchanged.

No ID-retrofit rule is needed: with the entries removed there is nothing to retrofit.

`docs/holding-box-placement.md` is retained as a seeding source for pass 1 and deleted once the
registry stands on its own.

## Out of scope

- Retrofitting IDs onto historical analysis.
- Registering the Emolga masterset, stamped cards, trainer full arts, or slabs.
- Any current-location or inventory tracking.
- Changes to `CURATORIAL_AUDIT_PROMPT.md` or to site content under `content/`.
