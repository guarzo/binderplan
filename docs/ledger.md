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

**Vocabulary.** Destinations use names that already exist — Volume 1 and Volume 2 sub-themes; the historical holding-box sections from `content/guides/holding-box.md`; and the Review, Keeper, Trade, and Release architecture adopted in [`Review, Keeper, and Trade Binder Design`](superpowers/specs/2026-09-22-review-keeper-trade-binders-design.md). No parallel naming scheme.

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

---

## 2026-08-02 — Enduring Presence redefined: power held whole, not time witnessed

A contested definition, not a contested card. Recorded here because every future Enduring
Presence call depends on it and because it **reverses** the test written in
`content/guides/volume-2-refinement.md` on 2026-07-10.

### The conflict

`CURATORIAL_AUDIT_PROMPT.md` §4 defined Enduring Presence as "complete, self-contained forces —
power contained (not expressed), pose suggests continuity." `content/philosophy/themes.md` and the
July refinement guide defined the same theme as *time witnessed*: ruins, weathering, artifacts, a
world shaped around the Pokemon. §5A compounded it by assigning "power contained… complete,
enduring force" to **Legendary Bearing** as well, so the audit prompt contradicted itself as well
as the canonical file.

### What the pages showed

Both Enduring Presence pages were read card by card on 2026-08-02, the first time the artwork was
examined rather than the captions.

`enduring_presence_2.webp` — Machop (`machop-01`), Mew (`mew-05`), Zygarde (`zygarde-01`), Reshiram
(`reshiram-02`), Hoopa (`hoopa-01`), Master Ball (`master-ball-01`), Sandshrew (`sandshrew-02`),
Houndoom (`houndoom-04`), Shaymin (`shaymin-04`). No ruins, architecture, artifacts, weathering or
generations anywhere on the page. Under the time test the entire page failed.

`enduring_presence_1.webp` — Muk (`muk-01`), Vulpix (`vulpix-01`), Groudon (`groudon-03`), Steelix
(`steelix-01`), Blastoise (`blastoise-01`), Jirachi (`jirachi-03`), Joltik (`joltik-02`), Dark
Gengar (`gengar-05`), Bulbasaur (`bulbasaur-03`). Genuinely old *cards* — Neo, e-Card and
Pokédex-number prints — but the *artwork* carries no historical signal either. The refinement
guide anticipated exactly this: "the age of the physical card is not enough by itself."

So the time definition was not describing one drifted page. It had never described the theme as
physically built, in either page.

### The ruling

**§4 is canonical. The time definition is retired.** Enduring Presence is completeness and
containment: finished rather than becoming, power held rather than spent, continuity in the pose.

The Legendary Bearing boundary is redrawn as **encounter versus containment**. `themes.md` already
defined Legendary Bearing as "the power is already complete; the scene is about encountering it,"
so that file needed no change on the Legendary Bearing side — it was the audit prompt's §3 and §5A
that had borrowed Enduring Presence's language, and those were corrected.

Both photographed pages are ratified where they stand. **No card moves.**

### What was rejected

"Contained Power" as a new theme, per §8: it fails test 1 (not a distinct axis — it is the axis
Enduring Presence now owns) and test 4 (solves no classification problem that the redefinition does
not already solve). The page keeps the caption as a page name, not as a theme.

### Reversed by this entry

- `volume-2-refinement.md` "The Power Distinction" and "Enduring Presence Audit", both marked
  superseded in place rather than deleted
- Review-order step 3, "test every Enduring Presence card for evidence of time" — dropped

The Quiet Familiarity and Threshold audits in that guide are untouched and still stand.

---

## 2026-09-20 — World of People boundary clarified; placement changes deferred

The owner selected **environmental emphasis** on the [completed audit checklist](evidence/2026-09-20/validation/completed-checklist.pdf): human-made places are central to World of People; relationships primarily belong in Companions. This resolves the conflict between §3's environmental/non-relational rule and the broader partnership wording previously in `content/philosophy/themes.md`. The philosophy now follows the selected boundary.

This is a definition ruling, not a move of Ralts (`ralts-01`) or any other card. The owner wrote **“no moves”** and **“Review Holding First”** across the proposed swaps and replacement review. No Threshold extractions, cross-theme swaps, or releases are recorded as executed. Squirtle (`squirtle-03`) and Dawn's Stadium (`dawns-stadium-01`) remain in Threshold; the 2026-08-02 Enduring Presence ruling is unchanged.

The holding-box overlaps identified during this audit are additional copies, not evidence that the corresponding binder cards moved. They must not inherit the binder copies' IDs. A separate duplicate-removal review is not a release record. See the [preserved evidence and owner clarifications](evidence/2026-09-20/README.md).

---

## 2026-09-21 — Seven holding-box challenges executed

Governing evidence: the owner-marked [movement checklist](evidence/2026-09-21/validation/completed-movement-checklist.pdf) and five dated [after photographs](evidence/2026-09-21/README.md). Each movement below is verified executed: the checklist marks it moved, and the named incoming card appears on the corresponding after page in a one-for-one exchange.

| In | Destination | Out | Observed holding destination |
|---|---|---|---|
| Litleo (`litleo-01`) | Threshold | Hoopa EX (`hoopa-02`) | EDGE |
| Mudkip (`mudkip-02`) | Threshold | Kasumi's Tears (`kasumis-tears-01`) | HERITAGE |
| Dragonite (`dragonite-03`) | Quiet Familiarity | Dratini (`dratini-02`) | HERITAGE |
| Ursaring (`ursaring-01`) | Companions | Rocket's Trap (`rockets-trap-01`) | HERITAGE |
| Charizard (`charizard-03`) | On the Attack | Snorlax (`snorlax-02`) | EDGE |
| Lucario (`lucario-02`) | On the Attack | Ursaring (`ursaring-02`) | EDGE |
| Blastoise (`blastoise-02`) | Legendary Bearing | N's Plan (`ns-plan-01`) | HERITAGE |

### Identity continuity: Ursaring (`ursaring-01`)

The incoming Radiant Collection RC16/RC25 Ursaring is the same physical identity previously photographed in At Rest and recorded leaving that page on 2026-08-01. At the owner's direction it keeps `ursaring-01`; re-entering in Companions does not create a new registry row.

### Threshold correction

Hoopa EX (`hoopa-02`) is no longer treated as a Threshold anchor. Its rings frame an expressed attack rather than a visible boundary being crossed. Litleo (`litleo-01`) replaces it with an explicit doorway and emergence; Mudkip (`mudkip-02`) replaces Kasumi's Tears with a readable sheltered opening. This reverses the earlier unverified Hoopa/Kecleon placement rationale without claiming that historical Kecleon movement can now be reconstructed.

### Reviewed and declined

Three additional comparisons on the checklist were not executed:

- McDonald's Pikachu 020/M-P did not replace Charmander (`charmander-03`); the owner's note points toward World of People instead.
- Alolan Meowth did not replace Shaymin (`shaymin-03`); the owner's note likewise points toward World of People.
- Mewtwo EX did not replace Groudon (`groudon-01`) because it would add another Mewtwo to Awakened Power.

Those incumbents remain where they were. A comparison is not movement, so none of the three reserve cards receives a registry ID from this decision alone.

No release is recorded. EDGE and HERITAGE are observed holding-box destinations, not disposal states.

---

## 2026-09-22 — Holding reshoot reconciled; Yveltal released

Governing evidence: the complete [holding-sort photograph sequence](evidence/2026-09-22/README.md), its [100-card inventory](2026-09-22-holding-binder-inventory.md), and the owner's follow-up clarifications.

The photographed nine-pocket binder is **interim staging**, not execution of the final Review/Keeper/Trade binder architecture. The 100 photographed cards supersede the earlier 97-entry inventory proposal. No photographed card is currently confirmed available for Trade.

### Mewtwo EX (`mewtwo-05`) and Torterra Lv.X (`torterra-02`) → Keeper, subsection undecided

The superseded proposal placed both cards in Review/REDUNDANT under Awakened Power. The owner instead confirmed permanent Keeper status but deliberately left the Keeper subsection undecided. This is a classification decision, not evidence of final four-pocket Keeper placement.

### Kirlia (`kirlia-01`) remains Beautiful Misfits

The photographed Kirlia sits among Heritage cards because it was found later. The owner explicitly declined a Heritage reassignment; its Beautiful Misfits classification remains unchanged. Its exact set and number remain unresolved, but the photographed physical identity now has a permanent registry ID.

### Yveltal (`yveltal-03`) → RELEASE

The English Steam Siege 65/114 holding copy was physically removed. This is the only Release action confirmed from the sort. It is distinct from Yveltal EX (`yveltal-01`) and Chinese Yveltal (`yveltal-02`) in the thematic binders.

The earlier proposed releases of Yveltal Celebrations, Pokémon Communication, and Piplup from Manaphy & Lucario were **not** executed; all three remain visible in the authoritative holding photographs.
