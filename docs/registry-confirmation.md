# Registry confirmation worklist

Generated from `docs/card-registry.md` by `python3 scripts/check-registry.py docs/card-registry.md --worklist --write`. Every section below is recomputed from the registry except "4. Gaps and known issues", which is hand-written; regeneration reads the previous version of this document and carries that section forward automatically.

**Honest numbers, recomputed from the current file.** 175 rows total. 20 `photo` (11.4%), 68 `uncertain` (38.9%). 125 rows have both `set` and `number` read (71.4%) — 30 have `number` only, 7 have `set` only, 13 have neither field. The confirmation queue (section 3) holds 68 rows across 50 species: 13 clusters (31 rows) and 37 singletons.

## 1. Blocked — species unreadable

None. The registry has no state for a card that was seen but never identified to species -- every row that exists already carries one -- so this section is always empty.

## 2. Duplicate printing candidates

**None found** — `python3 scripts/check-registry.py docs/card-registry.md` reports `duplicate printings: 0`.

Take that as a weak result, not a clean bill of health. The check requires all four fields — `species`, `set`, `number`, `language` — to match on two rows, and only **125 of 175 rows (71.4%)** have both `set` and `number` read. The remaining 50 rows (28.6%) are missing one or both fields and are structurally invisible to this check: two physical duplicates sitting in the registry right now would not be flagged unless both happened to land among that same 125-row minority.

## 3. Confirmation queue — clusters first

68 rows, 50 species. **13 species (31 rows) hold two or more unresolved rows** and lead the list, because that is where an undetected duplicate printing could hide. The remaining 37 species have a single unresolved row each.

The "Unreadable" column is the row's own `notes` field: what specifically blocked the read.

### Clusters (species with 2+ unresolved rows)

**umbreon** (4)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| umbreon-02 | ブラッキー (JP) | contemplation_1.webp | vintage Pokedex-number print, distinct from umbreon-01, set per owner's doubleholo entry |
| umbreon-03 | Umbreon (EN) | elemental_solitude_1.webp | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |
| umbreon-04 | Umbreon (EN) | legendary_bearing_2.webp | Moonlight Fang/Quick Blow, RH holo mark, distinct from umbreon-01/02/03, set code not textual |
| umbreon-05 | ブラッキー (JP) | enduring_presence_1.webp | distinct from umbreon-01..04, set not readable as text |

**gengar** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| gengar-02 | ゲンガー (JP) | intimidation_1.webp | Lv.38 print, distinct from gengar-01 and gengar-mimikyu-01, number illegible |
| gengar-03 | M Gengar EX (JP) | on_attack_1.webp | Mega Evolution EX, "ファントムゲート"/Phantom Gate, distinct from gengar-01/02 and gengar-mimikyu-01, number illegible |
| gengar-05 | わるいゲンガー (JP) | enduring_presence_2.webp | Dark Gengar, HP70, distinct from gengar-01..04, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |

**jirachi** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| jirachi-02 | 基拉祈V (ZH) | awakened_power_1.webp | distinct printing from jirachi-01, number illegible |
| jirachi-03 | ジラーチex (JP) | enduring_presence_2.webp | ex card, promo Play number, set not readable as text |
| jirachi-04 | 七夜のジラーチ (JP) | IMG_6865.HEIC | みらいよち/はめつのねがい attacks, distinct from jirachi-01..03, set from owner's doubleholo export 2026-09-18, no number in export |

**joltik** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| joltik-01 | 电电虫 (ZH) | companions_2.webp | holo print, number illegible after crop attempt |
| joltik-02 | Joltik (EN) | enduring_presence_2.webp | Jolting Charge attack, distinct from joltik-01, set not readable as text |
| joltik-03 | バチュル (JP) | contemplation_1.webp | AR rarity, set code not textual, number read with low confidence |

**darkrai** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| darkrai-01 | Darkrai EX (EN) | awakened_power_1.webp | set code not textual |
| darkrai-03 | Darkrai (EN) | legendary_bearing_1.webp | Dark Cutter/Abyssal Sleep, distinct from darkrai-01/02, number illegible |

**dratini** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| dratini-01 | Dratini (EN) | contemplation_1.webp | set code not textual |
| dratini-02 | Dratini (EN) | quiet_familiarity_1.webp | Pound attack, Wizards era, distinct from dratini-01, set not readable as text |

**espeon** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| espeon-01 | わるいエーフィ (JP) | elemental_solitude_1.webp | Dark Espeon, vintage-style print, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| espeon-02 | 太阳伊布GX (ZH) | legendary_bearing_2.webp | GX card, SSR rarity mark, distinct from espeon-01; 太阳伊布 is Espeon's Chinese localized name, set code not textual |

**groudon** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| groudon-01 | Groudon (EN) | awakened_power_1.webp | number illegible |
| groudon-02 | Groudon (EN) | legendary_bearing_1.webp | Swelling Power/Magma Purge, distinct from groudon-01, set code not textual |

**lugia** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| lugia-01 | ルギア (JP) | awakened_power_1.webp | vintage Pokedex-number print, set per owner's doubleholo entry |
| lugia-03 | Lugia (EN) | legendary_bearing_1.webp | Aerowing attack, No.249 dex entry, vintage print, distinct from lugia-01/02, era not identifiable |

**mew** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| mew-03 | Mew GX (JP) | legendary_bearing_2.webp | double-star SR rarity mark, distinct from mew-01/02, set code not textual |
| mew-05 | ミュウ (JP) | threshold_1.webp | Psywave/Recover-Beam attacks, distinct from mew-01..04, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |

**mewtwo** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| mewtwo-01 | Mewtwo (EN) | awakened_power_2.webp | heavy holo glare, number illegible after crop attempt |
| mewtwo-04 | Mewtwo (EN) | legendary_bearing_1.webp | delta species, Delta Switch/Energy Burst, distinct from mewtwo-01/02/03, set code not textual |

**pikachu** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| pikachu-01 | Pikachu (EN) | calm_nature_1.webp | classic border, corner number illegible |
| pikachu-03 | 皮卡丘 (ZH) | companions_1.webp | CHR rarity mark, Ash-style artwork, set not readable as text |

**typhlosion** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| typhlosion-01 | バクフーン (JP) | intimidation_1.webp | vintage Pokedex-number print, set per owner's doubleholo entry |
| typhlosion-02 | バクフーン (JP) | legendary_bearing_1.webp | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |

### Singletons (37 species, one unresolved row each)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| ampharos-01 | ミカンのデンリュウ (JP) | IMG_6853.HEIC | Jasmine's Ampharos, VS-series print, set code not textual |
| blastoise-01 | カメックス (JP) | enduring_presence_2.webp | Lv.52 HP100, vintage Pokedex-number print, set per owner's doubleholo entry |
| bulbasaur-02 | フシギダネ (JP) | joyful_action_1.webp | vintage Pokedex-number print, distinct from bulbasaur-01; era not identifiable |
| charizard-01 | リザードンG (JP) | on_attack_1.webp | Lv.X print, set code not textual, number read with low confidence |
| cubone-02 | カラカラ (JP) | at_rest_1.webp | vintage-style print, set name not identifiable |
| dawns-stadium-01 | 夜明けのスタジアム (JP) | IMG_6865.HEIC | Stadium trainer card, set from owner's doubleholo export 2026-09-18, no number in export |
| dragonair-01 | エリカのハクリュー (JP) | enduring_presence_1.webp | Erika's Dragonair, Lv.32, vintage Pokedex-number print, set per owner's doubleholo entry |
| dragonite-01 | カイリュー (JP) | contemplation_1.webp | Lv.45 print, vintage Pokedex-number print, set per owner's doubleholo entry |
| entei-01 | 結晶塔のエンテイ (JP) | legendary_bearing_1.webp | No.244 dex entry, holo, set supplied by owner 2026-09-18, no card number recorded |
| gengar-mimikyu-01 | 耿鬼＆谜拟丘GX (ZH) | awakened_power_1.webp | TAG TEAM card featuring two species, printed name kept whole rather than split; number illegible |
| hoopa-02 | Hoopa EX (EN) | IMG_6865.HEIC | Scoundrel Ring ability, Hyperspace Fury attack, distinct from hoopa-01, number partially obscured by holo glare |
| houndoom-04 | Houndoom (EN) | threshold_1.webp | Crunch/Flamethrower attacks, distinct from houndoom-01..03, set not readable as text |
| imposter-professor-oaks-revenge-01 | にせオーキドの逆襲 (JP) | companions_1.webp | Trainer card, vintage Team Rocket-era print, "R" rarity mark visible, number illegible |
| kangaskhan-01 | ガルーラ (JP) | IMG_6858.HEIC | vintage Pokedex-number print, set per owner's doubleholo entry |
| kasumis-tears-01 | カスミのなみだ (JP) | IMG_6865.HEIC | Trainer card, set from owner's doubleholo export 2026-09-18, no number in export |
| kingdra-01 | キングドラ (JP) | on_attack_1.webp | Lv.47, vintage Pokedex-number print, illustrator Mitsuhiro Arita, set per owner's doubleholo entry |
| latios-02 | ラティオス (JP) | elemental_solitude_1.webp | distinct from latios-01, number illegible |
| marill-01 | Marill (EN) | joyful_action_1.webp | vintage-style print, number legible, set name not shown |
| master-ball-01 | マスターボール (JP) | threshold_1.webp | Trainer item card, set from owner's doubleholo export 2026-09-18, no number in export |
| mimikyu-01 | 谜拟丘 (ZH) | companions_1.webp | Ability 假扮 (Disguise), number illegible |
| misdreavus-01 | ムウマ (JP) | intimidation_1.webp | Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| muk-01 | ベトベトン (JP) | enduring_presence_2.webp | Grimer evolution Lv.34, HP70, vintage Pokedex-number print, set per owner's doubleholo entry |
| ns-plan-01 | N's Plan (EN) | legendary_bearing_2.webp | Supporter trainer, double-star SR rarity mark, set code not textual |
| ninetales-01 | キュウコン (JP) | legendary_bearing_2.webp | Lv.32, vintage Pokedex-number print, set per owner's doubleholo entry |
| numel-01 | Numel (EN) | quiet_familiarity_1.webp | Firebreathing/Tackle attacks, e-Card era, set not readable as text |
| reshiram-02 | Reshiram (EN) | threshold_1.webp | Outrage/Blue Flare attacks, distinct from reshiram-01, set not readable as text |
| rockets-trap-01 | ロケット団のワナ (JP) | companions_2.webp | Trainer card, vintage print, set from owner's doubleholo export 2026-09-18, no number in export |
| sabrinas-gaze-01 | ナツメの眼 (JP) | intimidation_1.webp | trainer card, set from owner's doubleholo export 2026-09-18, no number in export |
| scyther-01 | ストライク (JP) | awakened_power_2.webp | vintage Pokedex-number print, set per owner's doubleholo entry |
| snivy-02 | ツタージャ (JP) | contemplation_1.webp | distinct from snivy-01, set code not textual, number read with low confidence |
| squirtle-03 | Squirtle (EN) | IMG_6865.HEIC | Withdraw/Skull Bash attacks, distinct from squirtle-01/02, set code not textual |
| steelix-01 | ハガネール (JP) | enduring_presence_2.webp | vintage Pokedex-number print, number corrected from No.205 (misread): Steelix is Pokédex #208, matching owner's doubleholo export 2026-09-18 |
| ursaring-02 | リングマ (JP) | on_attack_1.webp | Lv.43 print, distinct from ursaring-01, vintage Pokedex-number print, set per owner's doubleholo entry |
| vulpix-01 | Vulpix (EN) | enduring_presence_2.webp | Collect Fire attack, e-Card era stamp, number ambiguous (119 or 116)/147, set not readable as text |
| yveltal-02 | 伊裴尔塔尔 (ZH) | legendary_bearing_1.webp | distinct from yveltal-01, number illegible |
| zapdos-01 | サンダー (JP) | IMG_6847.HEIC | vintage Pokedex-number print, number corrected from No.143 (misread): Zapdos is Pokédex #145, matching owner's doubleholo export 2026-09-18 |
| zekrom-01 | Zekrom EX (EN) | legendary_bearing_2.webp | Slash/Voltage Burst, set code not textual |

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

Two independent lines of evidence fix that offset, and both still hold. First, contents: the nine
rows whose `first_seen` is `enduring_presence_1.webp` are Umbreon, Ditto, Snorlax, Arcanine,
Dragonair, Celebi, Togepi, Mudkip and Cinccino — which is the Quiet Familiarity p2 page, not
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

The registry currently holds 175 rows: the 171 cards in the binder plus the 4 below that have left
it.

**Four cards have physically left the binder** as part of planned swaps the owner has been
executing. Their registry rows still exist and still hold their IDs — this is correct, not a bug.
The registry records identity, not shelf location; a card in the holding box keeps the ID it was
first seen under.

| ID | Card | Was at | Replaced by |
|---|---|---|---|
| ursaring-01 | Ursaring (EN, Radiant Collection) | at_rest_1.webp | Pikachu (pikachu-06) |
| typhlosion-02 | バクフーン (JP) | legendary_bearing_1.webp | Zapdos (zapdos-01) |
| umbreon-03 | Umbreon (EN) | elemental_solitude_1.webp | Jasmine's Ampharos (ampharos-01) |
| electrode-01 | マルマイン (JP) | companions_2.webp | Kangaskhan (kangaskhan-01) |

**One binder page had never been photographed at all**, and was entirely absent from pass 1 —
9 cards, seeded from the reshoot as `dawns-stadium-01` through the rest of the `IMG_6865.HEIC`
group (see the cluster and singleton tables above for the individual rows). It is now fully in the
registry.

## 5. Cards no longer in the binder

Not derivable here. The registry records what a card **is**, never where it sits, so a row gives no sign that its card has left the binder. Movement lives in `ledger.md`: grep it for an ID to see whether that card was swapped out. Any list of departed cards in this document is hand-written; put it in section 4, which is carried forward automatically when this document is regenerated.

## 6. Confirmation queue by page

The same rows as section 3, regrouped for walking the binder. Open to a page, clear every card listed under it, move on. Pages in binder order; a page with nothing unresolved is omitted. The source image is dropped here — the page implies it.

Photographs record what was on a page when the shoot happened, so a card since swapped out still appears under its old page. `ursaring-01`, `typhlosion-02` and `umbreon-03` are the known cases; check `ledger.md` before hunting for a card that is not there.

### V1 · Calm in Nature

| ID | Card name | Unreadable |
|---|---|---|
| pikachu-01 | Pikachu (EN) | classic border, corner number illegible |

### V1 · At Rest

| ID | Card name | Unreadable |
|---|---|---|
| cubone-02 | カラカラ (JP) | vintage-style print, set name not identifiable |

### V1 · Joyful Action

| ID | Card name | Unreadable |
|---|---|---|
| bulbasaur-02 | フシギダネ (JP) | vintage Pokedex-number print, distinct from bulbasaur-01; era not identifiable |
| marill-01 | Marill (EN) | vintage-style print, number legible, set name not shown |

### V1 · Awakened Power p1

| ID | Card name | Unreadable |
|---|---|---|
| darkrai-01 | Darkrai EX (EN) | set code not textual |
| gengar-mimikyu-01 | 耿鬼＆谜拟丘GX (ZH) | TAG TEAM card featuring two species, printed name kept whole rather than split; number illegible |
| groudon-01 | Groudon (EN) | number illegible |
| jirachi-02 | 基拉祈V (ZH) | distinct printing from jirachi-01, number illegible |
| lugia-01 | ルギア (JP) | vintage Pokedex-number print, set per owner's doubleholo entry |

### V1 · Awakened Power p2

| ID | Card name | Unreadable |
|---|---|---|
| mewtwo-01 | Mewtwo (EN) | heavy holo glare, number illegible after crop attempt |
| scyther-01 | ストライク (JP) | vintage Pokedex-number print, set per owner's doubleholo entry |

### V1 · Legendary Bearing p1

| ID | Card name | Unreadable |
|---|---|---|
| darkrai-03 | Darkrai (EN) | Dark Cutter/Abyssal Sleep, distinct from darkrai-01/02, number illegible |
| entei-01 | 結晶塔のエンテイ (JP) | No.244 dex entry, holo, set supplied by owner 2026-09-18, no card number recorded |
| groudon-02 | Groudon (EN) | Swelling Power/Magma Purge, distinct from groudon-01, set code not textual |
| lugia-03 | Lugia (EN) | Aerowing attack, No.249 dex entry, vintage print, distinct from lugia-01/02, era not identifiable |
| mewtwo-04 | Mewtwo (EN) | delta species, Delta Switch/Energy Burst, distinct from mewtwo-01/02/03, set code not textual |
| typhlosion-02 | バクフーン (JP) | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |
| yveltal-02 | 伊裴尔塔尔 (ZH) | distinct from yveltal-01, number illegible |
| zapdos-01 | サンダー (JP) | vintage Pokedex-number print, number corrected from No.143 (misread): Zapdos is Pokédex #145, matching owner's doubleholo export 2026-09-18 |

### V1 · Legendary Bearing p2

| ID | Card name | Unreadable |
|---|---|---|
| espeon-02 | 太阳伊布GX (ZH) | GX card, SSR rarity mark, distinct from espeon-01; 太阳伊布 is Espeon's Chinese localized name, set code not textual |
| mew-03 | Mew GX (JP) | double-star SR rarity mark, distinct from mew-01/02, set code not textual |
| ninetales-01 | キュウコン (JP) | Lv.32, vintage Pokedex-number print, set per owner's doubleholo entry |
| ns-plan-01 | N's Plan (EN) | Supporter trainer, double-star SR rarity mark, set code not textual |
| umbreon-04 | Umbreon (EN) | Moonlight Fang/Quick Blow, RH holo mark, distinct from umbreon-01/02/03, set code not textual |
| zekrom-01 | Zekrom EX (EN) | Slash/Voltage Burst, set code not textual |

### V1 · Intimidation

| ID | Card name | Unreadable |
|---|---|---|
| gengar-02 | ゲンガー (JP) | Lv.38 print, distinct from gengar-01 and gengar-mimikyu-01, number illegible |
| misdreavus-01 | ムウマ (JP) | Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| sabrinas-gaze-01 | ナツメの眼 (JP) | trainer card, set from owner's doubleholo export 2026-09-18, no number in export |
| typhlosion-01 | バクフーン (JP) | vintage Pokedex-number print, set per owner's doubleholo entry |

### V1 · On the Attack

| ID | Card name | Unreadable |
|---|---|---|
| charizard-01 | リザードンG (JP) | Lv.X print, set code not textual, number read with low confidence |
| gengar-03 | M Gengar EX (JP) | Mega Evolution EX, "ファントムゲート"/Phantom Gate, distinct from gengar-01/02 and gengar-mimikyu-01, number illegible |
| kingdra-01 | キングドラ (JP) | Lv.47, vintage Pokedex-number print, illustrator Mitsuhiro Arita, set per owner's doubleholo entry |
| ursaring-02 | リングマ (JP) | Lv.43 print, distinct from ursaring-01, vintage Pokedex-number print, set per owner's doubleholo entry |

### V1 · Elemental Solitude

| ID | Card name | Unreadable |
|---|---|---|
| ampharos-01 | ミカンのデンリュウ (JP) | Jasmine's Ampharos, VS-series print, set code not textual |
| espeon-01 | わるいエーフィ (JP) | Dark Espeon, vintage-style print, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| latios-02 | ラティオス (JP) | distinct from latios-01, number illegible |
| umbreon-03 | Umbreon (EN) | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |

### V1 · Contemplation

| ID | Card name | Unreadable |
|---|---|---|
| dragonite-01 | カイリュー (JP) | Lv.45 print, vintage Pokedex-number print, set per owner's doubleholo entry |
| dratini-01 | Dratini (EN) | set code not textual |
| joltik-03 | バチュル (JP) | AR rarity, set code not textual, number read with low confidence |
| snivy-02 | ツタージャ (JP) | distinct from snivy-01, set code not textual, number read with low confidence |
| umbreon-02 | ブラッキー (JP) | vintage Pokedex-number print, distinct from umbreon-01, set per owner's doubleholo entry |

### V2 · Companions p1

| ID | Card name | Unreadable |
|---|---|---|
| imposter-professor-oaks-revenge-01 | にせオーキドの逆襲 (JP) | Trainer card, vintage Team Rocket-era print, "R" rarity mark visible, number illegible |
| mimikyu-01 | 谜拟丘 (ZH) | Ability 假扮 (Disguise), number illegible |
| pikachu-03 | 皮卡丘 (ZH) | CHR rarity mark, Ash-style artwork, set not readable as text |

### V2 · Companions p2

| ID | Card name | Unreadable |
|---|---|---|
| joltik-01 | 电电虫 (ZH) | holo print, number illegible after crop attempt |
| kangaskhan-01 | ガルーラ (JP) | vintage Pokedex-number print, set per owner's doubleholo entry |
| rockets-trap-01 | ロケット団のワナ (JP) | Trainer card, vintage print, set from owner's doubleholo export 2026-09-18, no number in export |

### V2 · Quiet Familiarity p1

| ID | Card name | Unreadable |
|---|---|---|
| dratini-02 | Dratini (EN) | Pound attack, Wizards era, distinct from dratini-01, set not readable as text |
| numel-01 | Numel (EN) | Firebreathing/Tackle attacks, e-Card era, set not readable as text |

### V2 · Quiet Familiarity p2

| ID | Card name | Unreadable |
|---|---|---|
| dragonair-01 | エリカのハクリュー (JP) | Erika's Dragonair, Lv.32, vintage Pokedex-number print, set per owner's doubleholo entry |
| umbreon-05 | ブラッキー (JP) | distinct from umbreon-01..04, set not readable as text |

### V2 · Enduring Presence p1

| ID | Card name | Unreadable |
|---|---|---|
| blastoise-01 | カメックス (JP) | Lv.52 HP100, vintage Pokedex-number print, set per owner's doubleholo entry |
| gengar-05 | わるいゲンガー (JP) | Dark Gengar, HP70, distinct from gengar-01..04, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| jirachi-03 | ジラーチex (JP) | ex card, promo Play number, set not readable as text |
| joltik-02 | Joltik (EN) | Jolting Charge attack, distinct from joltik-01, set not readable as text |
| muk-01 | ベトベトン (JP) | Grimer evolution Lv.34, HP70, vintage Pokedex-number print, set per owner's doubleholo entry |
| steelix-01 | ハガネール (JP) | vintage Pokedex-number print, number corrected from No.205 (misread): Steelix is Pokédex #208, matching owner's doubleholo export 2026-09-18 |
| vulpix-01 | Vulpix (EN) | Collect Fire attack, e-Card era stamp, number ambiguous (119 or 116)/147, set not readable as text |

### V2 · Enduring Presence p2

| ID | Card name | Unreadable |
|---|---|---|
| houndoom-04 | Houndoom (EN) | Crunch/Flamethrower attacks, distinct from houndoom-01..03, set not readable as text |
| master-ball-01 | マスターボール (JP) | Trainer item card, set from owner's doubleholo export 2026-09-18, no number in export |
| mew-05 | ミュウ (JP) | Psywave/Recover-Beam attacks, distinct from mew-01..04, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| reshiram-02 | Reshiram (EN) | Outrage/Blue Flare attacks, distinct from reshiram-01, set not readable as text |

### V2 · Threshold

| ID | Card name | Unreadable |
|---|---|---|
| dawns-stadium-01 | 夜明けのスタジアム (JP) | Stadium trainer card, set from owner's doubleholo export 2026-09-18, no number in export |
| hoopa-02 | Hoopa EX (EN) | Scoundrel Ring ability, Hyperspace Fury attack, distinct from hoopa-01, number partially obscured by holo glare |
| jirachi-04 | 七夜のジラーチ (JP) | みらいよち/はめつのねがい attacks, distinct from jirachi-01..03, set from owner's doubleholo export 2026-09-18, no number in export |
| kasumis-tears-01 | カスミのなみだ (JP) | Trainer card, set from owner's doubleholo export 2026-09-18, no number in export |
| squirtle-03 | Squirtle (EN) | Withdraw/Skull Bash attacks, distinct from squirtle-01/02, set code not textual |

