# Registry confirmation worklist

Generated from `docs/card-registry.md` by `python3 scripts/check-registry.py docs/card-registry.md --worklist --write`. Every section below is recomputed from the registry except "4. Gaps and known issues", which is hand-written; regeneration reads the previous version of this document and carries that section forward automatically.

**Honest numbers, recomputed from the current file.** 319 rows total. 121 `photo` (37.9%), 54 `uncertain` (16.9%). 258 rows have both `set` and `number` read (80.9%) — 4 have `number` only, 8 have `set` only, 49 have neither field. The confirmation queue (section 3) holds 54 rows across 48 species: 5 clusters (11 rows) and 43 singletons.

## 1. Blocked — species unreadable

None. The registry has no state for a card that was seen but never identified to species -- every row that exists already carries one -- so this section is always empty.

## 2. Duplicate printing candidates

**7 found:**

- emolga-01 / emolga-31: Emolga sv11B 116/086 JP
- emolga-06 / emolga-41: Emolga Victini Formation Deck 006/021 JP
- emolga-20 / emolga-37: Emolga Team Up 46/181 EN
- emolga-22 / emolga-40: Emolga Evolving Skies 057/203 EN
- emolga-38 / emolga-43: Emolga SM-P 041/SM-P ZH
- emolga-39 / emolga-44: Emolga Emerging Powers 32/98 EN
- squirtle-04 / squirtle-05: Squirtle Crystal Guardians 63/100 EN

Take that as a weak result, not a clean bill of health. The check requires all four fields — `species`, `set`, `number`, `language` — to match on two rows, and only **258 of 319 rows (80.9%)** have both `set` and `number` read. The remaining 61 rows (19.1%) are missing one or both fields and are structurally invisible to this check: two physical duplicates sitting in the registry right now would not be flagged unless both happened to land among those 258 fully identified rows.

## 3. Confirmation queue — clusters first

54 rows, 48 species. **5 species (11 rows) hold two or more unresolved rows** and lead the list, because that is where an undetected duplicate printing could hide. The remaining 43 species have a single unresolved row each.

The "Unreadable" column is the row's own `notes` field: what specifically blocked the read.

### Clusters (species with 2+ unresolved rows)

**emolga** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| emolga-02 | Emolga (EN) | stamp_2.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Emerging Powers 32; distinguish from separately wanted 025/BW-P and 081/BW-P, not ownership evidence for those. |
| emolga-36 | 电飞鼠 (ZH) | emolga_10.webp | Chinese-language stat-style Emolga print, SR; not established as a standard Pokémon TCG card. |
| emolga-42 | 电飞鼠 (ZH) | emolga_11.webp | Chinese-language flower-lined water artwork; set code not confidently legible. |

**bulbasaur** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| bulbasaur-02 | フシギダネ (JP) | joyful_action_1.webp | set supplied by owner 2026-09-20; character and printed Pokedex number checked in hand, no blanket set/printing verification from checklist ticks |
| bulbasaur-04 | Bulbasaur? (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. Species and printing hard to read in the published derivative; PDF candidate Mega Evolution 133, not verified. |

**iris's-fighting-spirit** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| iris-fighting-spirit-01 | アイリスの闘志 (JP) | waifu_1.jpg | Photographed artwork differs from the PDF entry; separate from the second Iris card |
| iris-fighting-spirit-02 | アイリスの闘志 (JP) | waifu_2.jpg | Separate photographed artwork from the first Iris card; printing unresolved |

**jacinthe** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| jacinthe-01 | ユカリ (JP) | waifu_1.jpg | Feast artwork matches export Nihil Zero Jacinthe 116; printing unverified |
| jacinthe-02 |  (JP) | trainers.pdf | PDF candidate Nihil Zero 108; separate from Jacinthe 116 |

**nemona** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| nemona-01 | ネモ (JP) | waifu_1.jpg | Two Nemona entries in export; exact physical printing unverified |
| nemona-02 |  (JP) | trainers.pdf | PDF candidate Shiny Treasure ex 343; separate from Nemona 351 |

### Singletons (43 species, one unresolved row each)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| ariados-01 | Ariados (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Unseen Forces 2; printing and stamp unverified. |
| aroma-lady-01 |  (JP) | trainers.pdf | PDF candidate Eevee Heroes 86 |
| arven-01 |  (JP) | trainers.pdf | PDF candidate Shiny Treasure ex 353 |
| bea-01 |  (JP) | trainers.pdf | PDF candidate VMAX Climax 261 |
| bidoof-01 | Bidoof [Ditto] (EN) | stamp_2.jpg | Published by 2026-03-18; actual capture date unknown. Ditto mark visible on photographed Bidoof; PDF candidate Pokémon GO 59; printing unverified. |
| blastoise-02 | 水箭龟VMAX (ZH) | IMG_7080.jpeg | holding photo R1C5; Chinese-language VMAX using SWSH103 artwork; exact Chinese set and number unresolved; entered Legendary Bearing p2 in verified 2026-09-21 swap |
| candice-01 |  (JP) | trainers.pdf | PDF candidate Paradigm Trigger 113 |
| chimecho-01 | Chimecho (EN) | stamp_5.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Emerald 12 Reverse Holo; finish unverified. |
| clawitzer-01 | Clawitzer (EN) | stamp_5.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate XY146; printing unverified. |
| cynthias-ambition-01 |  (JP) | trainers.pdf | PDF candidate Star Birth 114 |
| double-colorless-energy-01 | Double Colorless Energy (EN) | stamp_3.jpg | Published by 2026-03-18; actual capture date unknown. English card text visible; PDF lists Japanese Expansion Pack unnumbered, a language/printing conflict. Exact print unverified. |
| dratini-03 | Dratini (EN) | stamp_3.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Team Rocket Returns 53 Reverse Holo; not an existing thematic-binder Dratini copy. |
| erikas-invitation-01 | エリカの招待 (JP) | waifu_1.jpg | Cherry-blossom artwork matches export Erika's Invitation, not Erika's Hospitality; printing unverified |
| furisode-girl-01 | ふりそで (JP) | waifu_1.jpg | Autumn kimono artwork matches export Incandescent Arcana Furisode Girl 82; printing unverified |
| garbodor-01 | Garbodor (EN) | stamp_2.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Prerelease & Staff Promos SWSH025; staff status unverified. |
| hilda-01 |  (JP) | trainers.pdf | PDF candidate White Flare 173 |
| honey-s-p-01 |  (JP) | trainers.pdf | PDF candidate Sword & Shield promo 157 |
| karens-conviction-01 |  (JP) | trainers.pdf | PDF candidate Matchless Fighter 81 |
| kirlia-01 | キルリア (JP) | IMG_7119.HEIC | holding copy; exact set and number unresolved; owner confirmed Beautiful Misfits classification |
| lance-01 |  (JP) | trainers.pdf | PDF candidate Paradigm Trigger 114 |
| leafeon-01 | Leafeon (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Majestic Dawn 24; stamped printing unverified. |
| lucario-03 | Lucario ex (EN) | stamp_5.jpg | Published by 2026-03-18; actual capture date unknown. Photographed card absent from PDF under this name; do not substitute export Salamence ex. |
| meganium-01 | Meganium (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Mega Evolution Promo 1 Staff; staff designation not visually verified. |
| mela-01 |  (JP) | trainers.pdf | PDF candidate Ancient Roar 87 |
| mistys-spirit-01 | カスミのやる気 (JP) | trainer.jpeg | Photo supports artwork, not exact printing |
| olivia-01 | ライチ (JP) | waifu_1.jpg | Owner confirms Japanese card; export Olivia 111 incorrectly lists English; exact printing unverified |
| pansear-01 | バオップ (JP) | stamp_4.jpg | Published by 2026-03-18; actual capture date unknown. Japanese photographed card; PDF includes JP Black Collection 11 and EN Stellar Crown 21; no English metadata copied. |
| peonia-01 |  (JP) | trainers.pdf | PDF candidate Jet-Black Spirit 82 |
| pikachu-08 | Pikachu (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. Pokémon GO logo visible; PDF candidate GO 28; finish and printing not verified. Visual match to DoubleHolo object 32602; Pokémon GO logo and artwork match archived Stamped Cards photograph; foil sheen in page derivative is not independently legible. No in-hand confirmation. Specific stamp/foil variant remains unverified; photo crop retained. |
| pokemon-ranger-01 | Pokémon Ranger (EN) | stamp_3.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Steam Siege 104; printing unverified. |
| professors-research-02 | 博士の研究 (JP) | waifu_1.jpg | Photographed artwork matches the export's VMAX Climax Professor's Research; separate card from volume-2 Professor Willow promo |
| professor-cozmos-discovery-01 | Professor Cozmo's Discovery (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Deoxys 90; printing and stamp unverified. |
| raifort-01 | レホール (JP) | waifu_1.jpg | No exact printing confirmed |
| rosas-encouragement-01 |  (JP) | trainers.pdf | PDF candidate Nihil Zero 115 |
| solgaleo-01 | Solgaleo GX? (EN) | stamp_3.jpg | Published by 2026-03-18; actual capture date unknown. GX identification tentative in derivative; PDF candidate Sun & Moon 89. Photo-to-doubleholo object 456 review: 250 HP, full-size GX illustration, foil art and attacks match archived Stamped Cards photograph; no event stamp is visible. Jumbo variant differs. No in-hand confirmation. Specific stamp/foil variant remains unverified; photo crop retained. |
| tate-liza-01 |  (JP) | trainers.pdf | PDF candidate Sky-Splitting Charisma 103; not Tate & Liza's Training |
| tate-lizas-training-01 | フウとランの特訓 (JP) | trainer.jpeg | Different artwork from the older Tate & Liza entry in the PDF |
| tulip-01 | リップ (JP) | waifu_1.jpg | Photographed artwork differs from the PDF entry; printing unresolved |
| typhlosion-02 | バクフーン (JP) | legendary_bearing_1.webp | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |
| tyranitar-01 | Tyranitar (EN) | stamp_1.jpg | Published by 2026-03-18; actual capture date unknown. PDF candidate Paldea Evolved 135 Cosmos Holo; finish not visually verified. |
| umbreon-03 | Umbreon (EN) | elemental_solitude_1.webp | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |
| worker-01 |  (JP) | trainers.pdf | PDF candidate Paradigm Trigger 111 |
| zinnias-trust-01 | ヒガナの信頼 (JP) | trainer.jpeg | Supplemental HEIC 112/076 is reference only; export 102 unverified |

## 4. Gaps and known issues

**The volume-2 page naming is resolved — do not "fix" it again.** Some registry `first_seen`
values name a photo file that depicts a *different* binder page than the filename suggests. This
was once a live defect. It is not one now, and the correction is already in place.

What happened: the earlier "quiet_familiarity_2 does not exist" claim was wrong. Quiet Familiarity
page 2 does exist — it is on the binder shelf and was photographed in the original 18-image pass —
but it was stored under the filename `enduring_presence_1.webp`, and everything downstream
inherited the error. The gallery refresh fixed the downstream side: filenames and captions under
`content/` and `static/images/binder/` now describe what they actually show.

The registry's `first_seen` values were deliberately *not* changed. `first_seen` is immutable
provenance — it records which file a row was first read from, and that is a historical fact that
stays true no matter what the file is later understood to depict or renamed to. Rewriting it to
match the corrected filenames would destroy the audit trail and make the registry unverifiable
against the original pass. **If you are tempted to "helpfully" align `first_seen` with the current
filenames: don't. That is the bug, not the fix.**

The correction instead lives in `PAGE_ORDER` in `scripts/check-registry.py`, which maps each
`first_seen` filename to the page it truly depicts. Across volume 2 the mapping is off by one:

| Registry `first_seen` | Page it actually depicts |
|---|---|
| `enduring_presence_1.webp` | V2 · Quiet Familiarity p2 |
| `enduring_presence_2.webp` | V2 · Enduring Presence p1 |
| `threshold_1.webp` | V2 · Enduring Presence p2 |
| `IMG_6865.HEIC` | V2 · Threshold |

Two independent lines of evidence fix that offset, and both still hold. First, contents: eight
rows whose `first_seen` is `enduring_presence_1.webp` are Umbreon, Ditto, Snorlax, Arcanine,
Dragonair, Celebi, Togepi and Mudkip. Cinccino is a later `IMG_6860.HEIC` swap-in on the same
Quiet Familiarity p2 page, not an original `enduring_presence_1.webp` row. This is not
Enduring Presence. Second, divider order: in Volume 1 section dividers consistently precede the
pages they name (confirmed across the reshoot). `IMG_6864` is the "THRESHOLD" divider, immediately
followed by `IMG_6865`; the registry's `threshold_1.webp` matches `IMG_6863`, the frame *before*
that divider. Same offset, reached two different ways.

**The single empty pocket was where the earlier ledger said it was.** It was on Quiet Familiarity
p2 (`first_seen` `enduring_presence_1.webp`), exactly as `docs/ledger.md` recorded before a
previous analysis second-guessed it based on a filename. That pocket is no longer empty — the
planned Cinccino AR placement (recorded in the holding-box placement analysis, since retired; it
survives in git at commit `a254855`) has been executed; it is now `cinccino-01`. The binder holds
19 card pages × 9 pockets = 171 cards, no empty pockets anywhere.

**No registry row was ever affected by any of this.** `first_seen` names a source *file*, not a
theme or a shelf location, so every row stayed literally true throughout — the file
`enduring_presence_1.webp` really was the row's source image, regardless of which page that file
turned out to be a photo of. This is the clearest evidence the no-location design decision was
correct: a naming error in the photo pipeline could not corrupt the registry, only the captions
downstream of it. Those captions have since been corrected, and the residue is confined to
`first_seen`, where it is intentional and `PAGE_ORDER` accounts for it.

The original Volume I/II reconciliation counted 171 occupied thematic pockets and 14 other
registered identities at that point. This historical split no longer describes the entire registry:
Stamped Cards, Emolga, and Trainer Full Arts have since added rows, and the generated sections
above now report the current totals. The [2026-09-24 sort](2026-09-24-holding-sort-current-inventory.md)
photographs confirmed 13 of those *original* 14 identities still owned outside the thematic
volumes; one had a previously confirmed removal. The registry records identity, not current
location; do not infer today's ownership or page from row counts.

Radiant Collection Ursaring (`ursaring-01`) is no longer a departed card. The owner identified the
RC16/RC25 card entering Companions on 2026-09-21 as that same physical identity, so it keeps its ID
and re-enters without a new row.

**Historical reconciliation of 14 identities outside Volume I/II at the September sort.**
The recorded states below combine the append-only ledger with the dated
[post-sort evidence](evidence/2026-09-24/README.md).
Absence from the thematic binders does not establish release; only Steam Siege
Yveltal (`yveltal-03`) has an executed removal record. The five newly available Trade cards
are distinct physical copies, not aliases of existing registry rows.

| ID | Card | Former page | Replaced by | Latest recorded state |
|---|---|---|---|---|
| typhlosion-02 | バクフーン (JP) | Legendary Bearing p1 | Zapdos (`zapdos-01`) | Keeper · Heritage; IMG_7137 |
| umbreon-03 | Umbreon (EN) | Elemental Solitude | Ampharos (`ampharos-01`) | Review · REDUNDANT; IMG_7135 |
| electrode-01 | マルマイン (JP) | Companions p2 | Kangaskhan (`kangaskhan-01`) | Review · REDUNDANT; IMG_7135 |
| hoopa-02 | Hoopa EX (EN) | Threshold | Litleo (`litleo-01`) | Review · REDUNDANT; IMG_7137 |
| kasumis-tears-01 | カスミのなみだ (JP) | Threshold | Mudkip (`mudkip-02`) | Keeper · Heritage; IMG_7141 |
| dratini-02 | Dratini (EN) | Quiet Familiarity p1 | Dragonite (`dragonite-03`) | Keeper · Heritage; IMG_7141 |
| rockets-trap-01 | ロケット団のワナ (JP) | Companions p2 | Ursaring (`ursaring-01`) | Keeper · Heritage; IMG_7141 |
| snorlax-02 | カビゴンVMAX (JP) | On the Attack | Charizard (`charizard-03`) | Review · REDUNDANT; IMG_7137 |
| ursaring-02 | リングマ (JP) | On the Attack | Lucario (`lucario-02`) | Review · REDUNDANT; IMG_7137 |
| ns-plan-01 | N's Plan (EN) | Legendary Bearing p2 | Blastoise (`blastoise-02`) | Keeper · Heritage; IMG_7141 |
| kirlia-01 | キルリア (JP) | — | — | Beautiful Misfits |
| mewtwo-05 | Mewtwo EX (EN) | — | — | Keeper · Beautiful Misfits; IMG_7138 |
| torterra-02 | ドダイトス LV.X (JP) | — | — | Keeper · Heritage; IMG_7140 |
| yveltal-03 | Yveltal (EN) | — | — | RELEASE — physically removed 2026-09-22 |

Kirlia's Beautiful Misfits classification is physically corroborated by `IMG_7138.HEIC`;
its exact set and number remain unresolved.

**One binder page had never been photographed at all**, and was entirely absent from pass 1 —
9 cards, seeded from the reshoot as `dawns-stadium-01` through the rest of the `IMG_6865.HEIC`
group (see the cluster and singleton tables above for the individual rows). It is now fully in the
registry.

## 5. Cards no longer in the binder

Not derivable here. The registry records what a card **is**, never where it sits, so a row gives no sign that its card has left the binder. Movement lives in `ledger.md`: grep it for an ID to see whether that card was swapped out. Any list of departed cards in this document is hand-written; put it in section 4, which is carried forward automatically when this document is regenerated.

## 6. Confirmation queue by page

The same rows as section 3, grouped by historical `first_seen` source-image mapping for the original Volume I/II walk. Known pages are in original binder order; a page with nothing unresolved is omitted. Newer Stamped, Emolga, and Trainer sources may appear as 'Unmapped source image', not their published page. For current published placement and owner review use `docs/card-validation-checklist.md` instead.

Photographs record what was on a page when the shoot happened, so a card since swapped out can still appear under its old page. Multiple movements are now recorded; check `ledger.md` before hunting for a card that is no longer there.

### V1 · Joyful Action

| ID | Card name | Unreadable |
|---|---|---|
| bulbasaur-02 | フシギダネ (JP) | set supplied by owner 2026-09-20; character and printed Pokedex number checked in hand, no blanket set/printing verification from checklist ticks |

### V1 · Legendary Bearing p1

| ID | Card name | Unreadable |
|---|---|---|
| typhlosion-02 | バクフーン (JP) | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |

### V1 · Elemental Solitude

| ID | Card name | Unreadable |
|---|---|---|
| umbreon-03 | Umbreon (EN) | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |

### Unmapped source image · IMG_7080.jpeg

| ID | Card name | Unreadable |
|---|---|---|
| blastoise-02 | 水箭龟VMAX (ZH) | holding photo R1C5; Chinese-language VMAX using SWSH103 artwork; exact Chinese set and number unresolved; entered Legendary Bearing p2 in verified 2026-09-21 swap |

### Unmapped source image · IMG_7119.HEIC

| ID | Card name | Unreadable |
|---|---|---|
| kirlia-01 | キルリア (JP) | holding copy; exact set and number unresolved; owner confirmed Beautiful Misfits classification |

### Unmapped source image · emolga_10.webp

| ID | Card name | Unreadable |
|---|---|---|
| emolga-36 | 电飞鼠 (ZH) | Chinese-language stat-style Emolga print, SR; not established as a standard Pokémon TCG card. |

### Unmapped source image · emolga_11.webp

| ID | Card name | Unreadable |
|---|---|---|
| emolga-42 | 电飞鼠 (ZH) | Chinese-language flower-lined water artwork; set code not confidently legible. |

### Unmapped source image · stamp_1.jpg

| ID | Card name | Unreadable |
|---|---|---|
| ariados-01 | Ariados (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Unseen Forces 2; printing and stamp unverified. |
| bulbasaur-04 | Bulbasaur? (EN) | Published by 2026-03-18; actual capture date unknown. Species and printing hard to read in the published derivative; PDF candidate Mega Evolution 133, not verified. |
| leafeon-01 | Leafeon (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Majestic Dawn 24; stamped printing unverified. |
| meganium-01 | Meganium (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Mega Evolution Promo 1 Staff; staff designation not visually verified. |
| pikachu-08 | Pikachu (EN) | Published by 2026-03-18; actual capture date unknown. Pokémon GO logo visible; PDF candidate GO 28; finish and printing not verified. Visual match to DoubleHolo object 32602; Pokémon GO logo and artwork match archived Stamped Cards photograph; foil sheen in page derivative is not independently legible. No in-hand confirmation. Specific stamp/foil variant remains unverified; photo crop retained. |
| professor-cozmos-discovery-01 | Professor Cozmo's Discovery (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Deoxys 90; printing and stamp unverified. |
| tyranitar-01 | Tyranitar (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Paldea Evolved 135 Cosmos Holo; finish not visually verified. |

### Unmapped source image · stamp_2.jpg

| ID | Card name | Unreadable |
|---|---|---|
| bidoof-01 | Bidoof [Ditto] (EN) | Published by 2026-03-18; actual capture date unknown. Ditto mark visible on photographed Bidoof; PDF candidate Pokémon GO 59; printing unverified. |
| emolga-02 | Emolga (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Emerging Powers 32; distinguish from separately wanted 025/BW-P and 081/BW-P, not ownership evidence for those. |
| garbodor-01 | Garbodor (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Prerelease & Staff Promos SWSH025; staff status unverified. |

### Unmapped source image · stamp_3.jpg

| ID | Card name | Unreadable |
|---|---|---|
| double-colorless-energy-01 | Double Colorless Energy (EN) | Published by 2026-03-18; actual capture date unknown. English card text visible; PDF lists Japanese Expansion Pack unnumbered, a language/printing conflict. Exact print unverified. |
| dratini-03 | Dratini (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Team Rocket Returns 53 Reverse Holo; not an existing thematic-binder Dratini copy. |
| pokemon-ranger-01 | Pokémon Ranger (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Steam Siege 104; printing unverified. |
| solgaleo-01 | Solgaleo GX? (EN) | Published by 2026-03-18; actual capture date unknown. GX identification tentative in derivative; PDF candidate Sun & Moon 89. Photo-to-doubleholo object 456 review: 250 HP, full-size GX illustration, foil art and attacks match archived Stamped Cards photograph; no event stamp is visible. Jumbo variant differs. No in-hand confirmation. Specific stamp/foil variant remains unverified; photo crop retained. |

### Unmapped source image · stamp_4.jpg

| ID | Card name | Unreadable |
|---|---|---|
| pansear-01 | バオップ (JP) | Published by 2026-03-18; actual capture date unknown. Japanese photographed card; PDF includes JP Black Collection 11 and EN Stellar Crown 21; no English metadata copied. |

### Unmapped source image · stamp_5.jpg

| ID | Card name | Unreadable |
|---|---|---|
| chimecho-01 | Chimecho (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate Emerald 12 Reverse Holo; finish unverified. |
| clawitzer-01 | Clawitzer (EN) | Published by 2026-03-18; actual capture date unknown. PDF candidate XY146; printing unverified. |
| lucario-03 | Lucario ex (EN) | Published by 2026-03-18; actual capture date unknown. Photographed card absent from PDF under this name; do not substitute export Salamence ex. |

### Unmapped source image · trainer.jpeg

| ID | Card name | Unreadable |
|---|---|---|
| mistys-spirit-01 | カスミのやる気 (JP) | Photo supports artwork, not exact printing |
| tate-lizas-training-01 | フウとランの特訓 (JP) | Different artwork from the older Tate & Liza entry in the PDF |
| zinnias-trust-01 | ヒガナの信頼 (JP) | Supplemental HEIC 112/076 is reference only; export 102 unverified |

### Unmapped source image · trainers.pdf

| ID | Card name | Unreadable |
|---|---|---|
| aroma-lady-01 |  (JP) | PDF candidate Eevee Heroes 86 |
| arven-01 |  (JP) | PDF candidate Shiny Treasure ex 353 |
| bea-01 |  (JP) | PDF candidate VMAX Climax 261 |
| candice-01 |  (JP) | PDF candidate Paradigm Trigger 113 |
| cynthias-ambition-01 |  (JP) | PDF candidate Star Birth 114 |
| hilda-01 |  (JP) | PDF candidate White Flare 173 |
| honey-s-p-01 |  (JP) | PDF candidate Sword & Shield promo 157 |
| jacinthe-02 |  (JP) | PDF candidate Nihil Zero 108; separate from Jacinthe 116 |
| karens-conviction-01 |  (JP) | PDF candidate Matchless Fighter 81 |
| lance-01 |  (JP) | PDF candidate Paradigm Trigger 114 |
| mela-01 |  (JP) | PDF candidate Ancient Roar 87 |
| nemona-02 |  (JP) | PDF candidate Shiny Treasure ex 343; separate from Nemona 351 |
| peonia-01 |  (JP) | PDF candidate Jet-Black Spirit 82 |
| rosas-encouragement-01 |  (JP) | PDF candidate Nihil Zero 115 |
| tate-liza-01 |  (JP) | PDF candidate Sky-Splitting Charisma 103; not Tate & Liza's Training |
| worker-01 |  (JP) | PDF candidate Paradigm Trigger 111 |

### Unmapped source image · waifu_1.jpg

| ID | Card name | Unreadable |
|---|---|---|
| erikas-invitation-01 | エリカの招待 (JP) | Cherry-blossom artwork matches export Erika's Invitation, not Erika's Hospitality; printing unverified |
| furisode-girl-01 | ふりそで (JP) | Autumn kimono artwork matches export Incandescent Arcana Furisode Girl 82; printing unverified |
| iris-fighting-spirit-01 | アイリスの闘志 (JP) | Photographed artwork differs from the PDF entry; separate from the second Iris card |
| jacinthe-01 | ユカリ (JP) | Feast artwork matches export Nihil Zero Jacinthe 116; printing unverified |
| nemona-01 | ネモ (JP) | Two Nemona entries in export; exact physical printing unverified |
| olivia-01 | ライチ (JP) | Owner confirms Japanese card; export Olivia 111 incorrectly lists English; exact printing unverified |
| professors-research-02 | 博士の研究 (JP) | Photographed artwork matches the export's VMAX Climax Professor's Research; separate card from volume-2 Professor Willow promo |
| raifort-01 | レホール (JP) | No exact printing confirmed |
| tulip-01 | リップ (JP) | Photographed artwork differs from the PDF entry; printing unresolved |

### Unmapped source image · waifu_2.jpg

| ID | Card name | Unreadable |
|---|---|---|
| iris-fighting-spirit-02 | アイリスの闘志 (JP) | Separate photographed artwork from the first Iris card; printing unresolved |

