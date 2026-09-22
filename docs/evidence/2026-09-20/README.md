# Binder audit evidence — received 2026-09-20

This directory preserves the inputs and owner clarifications used by the September curatorial audit. The receipt date is not an inferred photograph capture date. `tmp/` was a disposable upload inbox and must not be used as durable evidence storage.

## Sources and recovery limits

| Location | Source / status |
|---|---|
| `holding/IMG_7078.jpeg` through `IMG_7082.jpeg`, plus `IMG_7088.jpeg` | Owner-restored holding-box photographs, copied byte-for-byte from the upload inbox and verified. Originals retain EXIF orientation. |
| `holding/doubleholo-export.txt` | Complete `pdftotext -layout` extraction of the seven-page `Holding.pdf`, exported September 20, 2026. The original PDF was no longer available when archiving; this is extracted text, not a recovered original PDF. It contains 97 export records. |
| `holding/*.recovered.png` | Five screenshot renditions recovered from the saved `read` tool results for `bulb.png`, `keck.png`, `mewtwo.png`, `pika.png`, and `venus.png`. These are not authenticated original-upload bytes; see recovery provenance below. |
| `validation/completed-checklist.pdf` | Owner's scanned checklist, archived byte-for-byte. PDF page 1 is the printed Decisions & Photos page; PDF page 2 is Facts & Identity. |
| `validation/rayquaza.WEBP` | Supplied card-art reference, archived byte-for-byte. Not evidence of a new physical copy or a move. |
| `validation/stamped.jpeg` | Original replacement image for the existing last stamped-card gallery page, as explicitly directed by the owner. |
| `validation/trainer.jpeg` | Original image of a new trainer full-art page. Append it; do not replace either existing trainer page. |
| `checklists/` | Three printable checklists and their LaTeX sources, including the blank curatorial movement form later completed on 2026-09-21. These are historical review forms, not a current movement log; the completed scan lives with the 2026-09-21 evidence. |
| `SHA256SUMS` | Integrity hashes of the archived source assets and checklist files. |

Incidental `desktop.ini` was excluded. Archival inputs are outside Hugo's `content/` and `static/` trees: they are retained in the repository, not published as gallery assets. The gallery JPEGs are EXIF-oriented derivatives, limited to 1500 pixels on the longest edge and encoded at JPEG quality 90. The archived originals are not resized or reencoded.

### Screenshot recovery provenance

The five images were recovered from session `01a0bcae-93cb-741b-b2e3-f9dc5472368b`, from tool calls at `2026-09-20T14:53:32.684Z`. Each result was matched to the full call ID of the `read` request for its original filename. All recovered files are PNG, 660 × 1434 pixels. Recovery decoded the stored payload without reencoding or resizing; whether the original image-read tool transformed an upload cannot be established from that record.

| Archived screenshot | Tool-result record | Identified physical artwork |
|---|---|---|
| `bulb.recovered.png` | `78de0d4a` | Erika's Bulbasaur; catalogue suggests CoroCoro 1998. Holding photo 7082, R2C4. |
| `keck.recovered.png` | `f46e6c45` | Kecleon; catalogue suggests 001/P. Holding photo 7081, R4C3. |
| `mewtwo.recovered.png` | `73f7f225` | Japanese Mewtwo; reference suggests 049/DPt-P. Holding photo 7082, R4C3. |
| `pika.recovered.png` | `a24e023e` | McDonald's meal Pikachu; catalogue suggests 020/M-P. Holding photo 7081, R1C1. |
| `venus.recovered.png` | `076bedc5` | Japanese Venusaur ex; catalogue lists 004 without a sufficiently specific set. Holding photo 7082, R2C5. |

These screenshot matches support artwork identification, not independently verified printing metadata or ownership counts. They depict five cards already visible in the holding photographs, not five additional physical sightings.

## Holding-box reconciliation

| Photograph | Occupied card positions |
|---|---:|
| IMG_7078 | 11 |
| IMG_7079 | 16 |
| IMG_7080 | 20 |
| IMG_7081 | 20 |
| IMG_7082 | 20 |
| IMG_7088 | 15 |
| **Total** | **102** |

The 102 photographed positions reconcile at artwork level to 97 export records plus the five screenshot-supported supplements. This is not certification of 102 distinct printings or exact catalogue matches. The overview JPEGs are 640 × 480 pixels; many footers and fine scene details cannot be read reliably.

Coordinates mean card lettering upright, rows top-to-bottom and columns left-to-right. For IMG_7078, orient with Aquapolis Houndour at top-left; the empty position is R2C4. The other five images become upright using their EXIF rotation.

### Owner clarification: export versions and duplicate copies

The owner confirmed that mismatched export versions are either deliberate stand-ins or mistakes. Do not copy English metadata onto photographed Japanese cards or assign a printing solely from matching artwork. One clear species conflict is the photographed Kirlia at IMG_7080 R1C1 versus the export's Ralts entry.

The owner also confirmed that holding-box cards overlapping current binder cards are **additional copies, not moves out of the binder**. The four specifically identified overlaps were Eevee SVP 173, Charmander SVP 44, Darkrai XY114, and Japanese Misdreavus. They belong in a separate duplicate-removal review; that review is not a release record. Compare stamps and finishes before selecting copies.

Groudon at IMG_7080 R3C2 still needs a printing comparison: its illustration matches the binder's Prismatic Evolutions 049/131 card, while the export names Paradox Rift 93. The two Houndoom G cards in IMG_7078 are separate physical copies; their finishes may differ. Neither an export duplicate row nor a holding-box duplicate by itself violates the no-duplicate rule across the thematic binders.

A matching holding-box card must not automatically inherit a registered binder copy's ID. Likewise, the documented old departures of Ursaring (`ursaring-01`), Typhlosion (`typhlosion-02`), Umbreon (`umbreon-03`) and Electrode (`electrode-01`) remain historical facts; crossed-out checklist questions do not establish their destinations or release.

## Completed checklist: exact scope of confirmation

The owner clarified in the follow-up conversation:

> The 20 ticks mean I verified the card number/character — you didn't print set names, so I didn't validate that.

The following 20 entries have owner verification of the **character and displayed number**, not a new exact-set/printing confirmation. Several numbers are Pokédex numbers. Preserve their `uncertain` printing confidence rather than interpreting the ticks as blanket validation of the registry rows.

| Last photographed page | Checked registry IDs |
|---|---|
| V1 Joyful Action | `bulbasaur-02` |
| V1 Awakened Power p1 | `lugia-01` |
| V1 Awakened Power p2 | `scyther-01` |
| V1 Legendary Bearing p1 | `zapdos-01` |
| V1 Legendary Bearing p2 | `ninetales-01` |
| V1 Intimidation | `gengar-02`, `misdreavus-01`, `typhlosion-01` |
| V1 On the Attack | `kingdra-01`, `ursaring-02` |
| V1 Elemental Solitude | `espeon-01` |
| V1 Contemplation | `dragonite-01`, `umbreon-02` |
| V2 Companions p2 | `kangaskhan-01` |
| V2 Quiet Familiarity p2 | `dragonair-01` |
| V2 Enduring Presence p1 | `blastoise-01`, `gengar-05`, `muk-01`, `steelix-01` |
| V2 Enduring Presence p2 | `mew-05` |

The two outside-binder entries, Typhlosion (`typhlosion-02`) and Umbreon (`umbreon-03`), were crossed out, not independently verified by this checklist.

### Explicit metadata corrections, separate from the ticks

- **Bulbasaur (`bulbasaur-02`):** owner separately supplied **Corocoro Promo** as its set. Fill that field; do not use the checklist tick to upgrade printing confidence.
- **Umbreon (`umbreon-01`):** handwritten correction **Chinese, CS4AC, 085/132**. Remove the incorrect moon-and-tower artwork identification. The physical card did not move.
- **Latios (`latios-03`):** handwritten correction **30/30, Latios + Latias deck**, with Supersonic Flight / Psyburn in the photograph. The Dragon Vault 10/20 card is a separate card visible in the supplied stamped image.
- **Dratini (`dratini-02`):** handwritten correction **Base Set, 26/102**, not Base Set 2 38/130.

These correct metadata on the existing identities. IDs and `first_seen` provenance stay unchanged.

## Curatorial and gallery decisions

- **No moves:** the owner wrote “no moves” for the thematic binders.
- **Review Holding First:** the bracket defers the proposed Hoopa/Snorlax and Kasumi's Tears/Rocket's Trap swaps, other Threshold removals, and replacement comparisons. No move or release is recorded as executed.
- **Threshold:** Squirtle (`squirtle-03`) and Dawn's Stadium (`dawns-stadium-01`) remain. Rayquaza's supplied reference is visual evidence for further review, not an owner decision to move it.
- **World of People:** owner selected **environmental emphasis**. Human-made places are central; relationships primarily belong in Companions. This resolves the prompt/philosophy conflict without deciding Ralts's placement.
- **Enduring Presence:** the existing August 2 ruling remains unchanged.
- **Emolga:** both **025/BW-P and 081/BW-P are still wanted**. The apparent copies in the gallery are **placeholder prints**. Occupied pockets do not establish ownership of those printings.
- **Stamped cards:** owner noted four additions and explicitly authorized the supplied image to **replace the existing last page**. Do not infer a new collection-wide count from this replacement photograph.
- **Trainer full arts:** owner noted three additions and explicitly said the supplied image is a **new page**. Preserve the existing two gallery pages and append the third.

## What has not been established

The export's NM grades, exact printing identity of every holding card, capture dates of the new photographs, new permanent registry IDs for holding copies, release destinations, and execution of any proposed curatorial swap are not established by this evidence. Neither catalogue matches nor a crossed-out task closes those gaps.
