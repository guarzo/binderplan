# Curatorial ledger

An append-only record of **contested** placement decisions and **every** release.

This is not an inventory. It does not track where each card physically is, and it says nothing about cards whose placement was never in doubt. It exists to answer one question: *why does this card sit where it sits?* — so that periodic audits under `CURATORIAL_AUDIT_PROMPT.md` do not re-litigate calls that were already argued out.

## How to use this file

**Append only.** Entries are never edited or deleted. When a later audit overturns an earlier call, write a **new** entry that cites the old one — `Elemental Solitude → Legendary Bearing (reverses 2026-08-01)`. The reversal history is the most useful thing in this file; editing in place destroys it.

**What earns an entry**

- A contested call — two or more themes genuinely competed for the card
- A correction — an earlier read was wrong and the card moved
- Every release, contested or not. Letting a card go is the one action that cannot be undone.
- Theme proposals, accepted or rejected, with the §8 test that decided it

A card that obviously belonged where it went gets no entry.

**Vocabulary.** Destinations use names that already exist — Volume 1 and Volume 2 sub-themes, and the holding-box sections from `content/guides/holding-box.md`: EDGE, REDUNDANT, HERITAGE, FUTURE SELF, RELEASE. No parallel naming scheme.

**Card IDs.** Entries cite cards by registry ID from [`card-registry.md`](card-registry.md), written as `Umbreon (umbreon-02)` — species alongside the ID for readability, neither alone. Species names by themselves are ambiguous: Umbreon appears five times across the binder, Mewtwo four, Pikachu seven. A card with no ID gets one at the moment it is first cited here — **except** a card that left the collection before the registry began on 2026-08-01. Those are named in prose without an ID and never receive one; registering a card nobody can produce would be the backfill this file forbids.

**Citations.** `§` references are to `CURATORIAL_AUDIT_PROMPT.md`.

**No backfill.** This ledger restarts 2026-08-01 with the adoption of card IDs. An earlier ledger covering the holding-box sort was superseded and removed; it survives in git at commit `a254855` if the reasoning is ever needed. Moves are not reconstructed from memory — doing so would put fiction into an audit trail.

---

## 2026-08-01 — Swaps executed from the superseded ledger

Not contested placements. These record **movement**, so that a card no longer in the binder is
discoverable by grepping its ID here rather than by being hunted for in a pocket it has left.

The four swaps below were planned in the superseded ledger (git `a254855`) and are recorded now
because they have been **verified as executed**: each page was photographed before the swap
(2026-07-31 shoot) and again after (2026-08-01 reshoot), and the before/after card sets differ by
exactly the one card named. The reasoning for each was argued in the superseded entry and is not
restated.

| Out | In | Verified by |
|---|---|---|
| Ursaring (`ursaring-01`) | Pikachu (`pikachu-06`) | `at_rest_1.webp` → `IMG_6842` |
| Typhlosion (`typhlosion-02`) | Zapdos (`zapdos-01`) | `legendary_bearing_1.webp` → `IMG_6847` |
| Umbreon (`umbreon-03`) | Jasmine's Ampharos (`ampharos-01`) | `elemental_solitude_1.webp` → `IMG_6853` |
| Electrode (`electrode-01`) | Kangaskhan (`kangaskhan-01`) | `companions_2.webp` → `IMG_6858` |

**Destination of the four departed cards is not recorded here**, because it was not observed. They
are out of the binder; whether they went to REDUNDANT, HERITAGE or RELEASE is a separate decision
and earns its own entry when made. `ursaring-01`, `typhlosion-02`, `umbreon-03` and `electrode-01`
keep their IDs and their registry rows regardless — the registry records identity, not location.

### Cinccino (`cinccino-01`) → Quiet Familiarity

The one empty pocket in either volume, on Quiet Familiarity page 2, is now filled. No eviction. The
superseded ledger planned exactly this. Both volumes are now full: 19 pages, 171 cards, no empty
pockets — recorded in `CURATORIAL_AUDIT_PROMPT.md` §2.

### Hoopa EX (`hoopa-02`) — present in Threshold, swap not verifiable

The superseded ledger planned "Hoopa EX → Threshold (out: Kecleon)". Hoopa EX is on the Threshold
page and no Kecleon exists anywhere in the registry, both consistent with that swap having been
carried out.

**It is recorded as unverified** because the Threshold page was never photographed before the
2026-08-01 reshoot, so there is no before state to compare. The displaced Kecleon is named here in
prose only: it left before the registry began, so it falls under the exception in **Card IDs**
above and carries no identifier. It is a historical card, not a registry entry.

### Note on the seven remaining swaps

The superseded ledger accepted eleven swaps. Four are recorded above as executed. The remaining
seven are not recorded here at all: planning is not movement, and an entry claiming a swap that has
not happened would be worse than no entry. Each earns one when it is carried out.
