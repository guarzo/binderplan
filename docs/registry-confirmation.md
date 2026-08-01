# Registry pass-2 confirmation — curator review

`docs/card-registry.md` holds 161 rows, one per pocket in Volumes 1 and 2, seeded from 18 spread
photographs shot through sleeves. This document is the pass-2 gate described in
`docs/superpowers/specs/2026-08-01-card-registry-design.md`: everything pass 1 could not settle,
handed to the curator before the registry is frozen.

**Honest numbers.** 161 rows total. 28 `photo` (legible in the photograph), 133 `uncertain`
(inferred or partly obscured) — an 82.6% uncertain rate. 30 rows have both `set` and `number`
read (two of those — `lucario-01`, `lugia-01` — are still `confidence: uncertain` because a digit
is ambiguous or the era/set is inferred rather than printed as text, not because the fields are
blank). 67 rows have `number` only, no rows have `set` only, and 64 rows have neither field. The
confirmation queue (section 3) holds 133 rows across 85 species.

IDs below are provisional until sign-off, per the design note's one-time carve-out from the
never-rewrite rule.

## 1. Blocked — species unreadable

None. All 161 pockets across the 18 spread photos were identified to species. Nothing is held
out of the registry.

## 2. Duplicate printing candidates

**None found** — `python3 scripts/check-registry.py docs/card-registry.md` reports
`duplicate printings: 0`.

Take that as a weak result, not a clean bill of health. The check requires all four fields —
`species`, `set`, `number`, `language` — to match on two rows, and only **30 of 161 rows (18.6%)**
have both `set` and `number` read. The remaining 131 rows (81.4%) are missing one or both fields
and are structurally invisible to this check: two physical duplicates sitting in the registry right
now would not be flagged unless both happened to land among that same 30-row minority. A zero-count
result here is evidence the check found nothing to compare, not evidence the binders hold no
duplicate printings.

The species clusters in section 3 — species with several unread rows — are exactly where an
undetected duplicate could be hiding, per the design note.

## 3. Confirmation queue — clusters first

133 rows, 85 species. **32 species (80 rows) hold two or more unresolved rows** and lead the list,
because that is where an undetected duplicate printing could hide. The remaining 53 species have a
single unresolved row each — cosmetic on their own, but still needed to close out `set`/`number`.

The "Unreadable" column is the row's own `notes` field: what specifically blocked the read, so the
curator knows what to look for on each physical card.

### Clusters (species with 2+ unresolved rows)

**gengar** (4)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| gengar-02 | ゲンガー (JP) | intimidation_1.webp | Lv.38 print, distinct from gengar-01 and gengar-mimikyu-01, number illegible |
| gengar-03 | M Gengar EX (JP) | on_attack_1.webp | Mega Evolution EX, "ファントムゲート"/Phantom Gate, distinct from gengar-01/02 and gengar-mimikyu-01, number illegible |
| gengar-04 | ゲンガー (JP) | companions_1.webp | Ability たくらみのうごう, スクリームサークル attack, distinct from gengar-01..03, number illegible after crop attempt |
| gengar-05 | わるいゲンガー (JP) | enduring_presence_2.webp | Dark Gengar, HP70, distinct from gengar-01..04, footer illegible after crop attempt |

**pikachu** (4)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| pikachu-01 | Pikachu (EN) | calm_nature_1.webp | classic border, corner number illegible |
| pikachu-02 | Surfing Pikachu (EN) | joyful_action_1.webp | vintage-style print, distinct from pikachu-01 |
| pikachu-03 | 皮卡丘 (ZH) | companions_1.webp | CHR rarity mark, Ash-style artwork, set not readable as text |
| pikachu-05 | Pikachu (EN) | quiet_familiarity_1.webp | Max Voltage attack, e-Card era, distinct from pikachu-01..04, set not readable as text |

**umbreon** (4)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| umbreon-02 | ブラッキー (JP) | contemplation_1.webp | vintage Pokedex-number print, distinct from umbreon-01, era not identifiable |
| umbreon-03 | Umbreon (EN) | elemental_solitude_1.webp | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |
| umbreon-04 | Umbreon (EN) | legendary_bearing_2.webp | Moonlight Fang/Quick Blow, RH holo mark, distinct from umbreon-01/02/03, set code not textual |
| umbreon-05 | ブラッキー (JP) | enduring_presence_1.webp | distinct from umbreon-01..04, set not readable as text |

**bulbasaur** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| bulbasaur-01 | Bulbasaur (EN) | calm_nature_1.webp | number legible, set name not printed on visible area |
| bulbasaur-02 | フシギダネ (JP) | joyful_action_1.webp | vintage Pokedex-number print, distinct from bulbasaur-01; era not identifiable |
| bulbasaur-03 | Bulbasaur (EN) | enduring_presence_2.webp | Sleep Seed ability, Vine Whip attack, distinct from bulbasaur-01/02, footer illegible after crop attempt |

**charmander** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| charmander-01 | Charmander (EN) | world_people_1.webp | number illegible |
| charmander-02 | Charmander (EN) | joyful_action_1.webp | distinct printing from charmander-01, set code not textual |
| charmander-03 | Charmander (EN) | quiet_familiarity_1.webp | Gnaw/Searing Flame attacks, distinct from charmander-01/02, footer obscured by sleeve tab |

**darkrai** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| darkrai-01 | Darkrai EX (EN) | awakened_power_1.webp | set code not textual |
| darkrai-02 | ダークライVSTAR (JP) | elemental_solitude_1.webp | VSTAR, SAR rarity mark, distinct from darkrai-01, set code not textual |
| darkrai-03 | Darkrai (EN) | legendary_bearing_1.webp | Dark Cutter/Abyssal Sleep, distinct from darkrai-01/02, number illegible |

**groudon** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| groudon-01 | Groudon (EN) | awakened_power_1.webp | number illegible |
| groudon-02 | Groudon (EN) | legendary_bearing_1.webp | Swelling Power/Magma Purge, distinct from groudon-01, set code not textual |
| groudon-03 | Groudon (EN) | enduring_presence_2.webp | Rock Smash/Break Ground attacks, AR rarity mark, set not readable as text |

**houndoom** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| houndoom-01 | Houndoom (EN) | awakened_power_1.webp | Single Strike era print, number illegible |
| houndoom-03 | Houndoom (EN) | elemental_solitude_1.webp | Dark Flame/Black Fang, Lv.35 #219 dex entry in flavor text, distinct from houndoom-01/02, set code not textual |
| houndoom-04 | Houndoom (EN) | threshold_1.webp | Crunch/Flamethrower attacks, distinct from houndoom-01..03, set not readable as text |

**jirachi** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| jirachi-01 | Jirachi (EN) | joyful_action_1.webp | number illegible |
| jirachi-02 | 基拉祈V (ZH) | awakened_power_1.webp | distinct printing from jirachi-01, number illegible |
| jirachi-03 | ジラーチex (JP) | enduring_presence_2.webp | ex card, promo Play number, set not readable as text |

**mew** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| mew-03 | Mew GX (JP) | legendary_bearing_2.webp | double-star SR rarity mark, distinct from mew-01/02, set code not textual |
| mew-04 | ミュウ (JP) | quiet_familiarity_1.webp | Pokepower type-change, Link Blast attack, distinct from mew-01..03, footer illegible after crop attempt |
| mew-05 | ミュウ (JP) | threshold_1.webp | Psywave/Recover-Beam attacks, distinct from mew-01..04, footer illegible after crop attempt |

**mewtwo** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| mewtwo-01 | Mewtwo (EN) | awakened_power_2.webp | heavy holo glare, number illegible after crop attempt |
| mewtwo-02 | Mewtwo EX (EN) | intimidation_1.webp | Shatter Shot/Damage Change EX card, distinct from mewtwo-01, set code not textual |
| mewtwo-04 | Mewtwo (EN) | legendary_bearing_1.webp | delta species, Delta Switch/Energy Burst, distinct from mewtwo-01/02/03, set code not textual |

**shaymin** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| shaymin-02 | シェイミLv.X (JP) | awakened_power_2.webp | distinct printing from shaymin-01, glare obscured number after crop attempt |
| shaymin-03 | Shaymin (EN) | quiet_familiarity_1.webp | Ability Flower Curtain, Smash Kick attack, distinct from shaymin-01/02, set not readable as text |
| shaymin-04 | Shaymin (EN) | threshold_1.webp | Ability Celebration Wind, Energy Bloom attack, distinct from shaymin-01..03, footer illegible after crop attempt |

**snivy** (3)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| snivy-01 | Snivy (EN) | calm_nature_1.webp | number illegible |
| snivy-02 | ツタージャ (JP) | contemplation_1.webp | distinct from snivy-01, set code not textual, number read with low confidence |
| snivy-03 | Snivy (EN) | quiet_familiarity_1.webp | Leaf Blade attack, distinct from snivy-01/02, set not readable as text |

**charizard** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| charizard-01 | リザードンG (JP) | on_attack_1.webp | Lv.X print, set code not textual, number read with low confidence |
| charizard-02 | リザードン (JP) | companions_1.webp | Ability バトルセンス, キングブレイズ attack, distinct from charizard-01, number illegible after crop attempt |

**cyndaquil** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| cyndaquil-01 | Cyndaquil (EN) | calm_nature_1.webp | number illegible |
| cyndaquil-02 | Cyndaquil (EN) | elemental_solitude_1.webp | distinct from cyndaquil-01, set code not textual |

**dragonite** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| dragonite-01 | カイリュー (JP) | contemplation_1.webp | Lv.45 print, vintage Pokedex-number print, era not identifiable |
| dragonite-02 | カイリューex (JP) | legendary_bearing_2.webp | ex card, distinct from dragonite-01, set code not textual |

**dratini** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| dratini-01 | Dratini (EN) | contemplation_1.webp | set code not textual |
| dratini-02 | Dratini (EN) | quiet_familiarity_1.webp | Pound attack, Wizards era, distinct from dratini-01, set not readable as text |

**espeon** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| espeon-01 | わるいエーフィ (JP) | elemental_solitude_1.webp | Dark Espeon, vintage-style print, number illegible |
| espeon-02 | 太阳伊布GX (ZH) | legendary_bearing_2.webp | GX card, SSR rarity mark, distinct from espeon-01; 太阳伊布 is Espeon's Chinese localized name, set code not textual |

**gardevoir** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| gardevoir-01 | ザーナイトex (JP) | legendary_bearing_2.webp | ex card, Breakdown/Psycho Storm, number illegible after crop attempt |
| gardevoir-02 | Gardevoir (EN) | companions_1.webp | Ability Shining Arcana, Prainwave attack, distinct from gardevoir-01, number illegible after crop attempt |

**golem** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| golem-01 | Golem EX (EN) | awakened_power_2.webp | set code not textual |
| golem-02 | ゴローニャex (JP) | legendary_bearing_2.webp | ex card, distinct from golem-01, number illegible after crop attempt |

**houndour** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| houndour-01 | Houndour (EN) | intimidation_1.webp | illustrator Mitsuhiro Arita credited, set code not textual |
| houndour-02 | デルビル (JP) | companions_2.webp | distinct from houndour-01, number illegible after crop attempt |

**joltik** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| joltik-01 | 电电虫 (ZH) | companions_2.webp | holo print, number illegible after crop attempt |
| joltik-02 | Joltik (EN) | enduring_presence_2.webp | Jolting Charge attack, distinct from joltik-01, set not readable as text |

**latios** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| latios-01 | ラティオス (JP) | contemplation_1.webp | AR rarity, set code not textual |
| latios-02 | ラティオス (JP) | elemental_solitude_1.webp | distinct from latios-01, number illegible |

**lugia** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| lugia-01 | ルギア (JP) | awakened_power_1.webp | vintage Pokedex-number print, era inferred from card style/border, not printed text |
| lugia-03 | Lugia (EN) | legendary_bearing_1.webp | Aerowing attack, No.249 dex entry, vintage print, distinct from lugia-01/02, era not identifiable |

**marowak** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| marowak-01 | カラカラ (JP) | at_rest_1.webp | vintage-style print, set name not identifiable |
| marowak-02 | ガラガラ (JP) | intimidation_1.webp | delta species print, distinct from marowak-01, number illegible after crop attempt |

**reshiram** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| reshiram-01 | レシラム (JP) | companions_1.webp | AR rarity mark, set not readable as text |
| reshiram-02 | Reshiram (EN) | threshold_1.webp | Outrage/Blue Flare attacks, distinct from reshiram-01, set not readable as text |

**sandshrew** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| sandshrew-01 | Sandshrew (EN) | calm_nature_1.webp | small logo bottom-right, number illegible |
| sandshrew-02 | Sandshrew (EN) | threshold_1.webp | Dig Under/Scratch attacks, distinct from sandshrew-01, footer illegible after crop attempt |

**snorlax** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| snorlax-01 | カビゴン (JP) | at_rest_1.webp | number illegible |
| snorlax-03 | Snorlax (EN) | enduring_presence_1.webp | Rest Up ability, Collapse/Toss and Turn attacks, distinct from snorlax-01/02, number illegible after crop attempt |

**spheal** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| spheal-02 | タマザラシ (JP) | on_attack_1.webp | Lv.18 print, distinct from spheal-01, set code not textual |
| spheal-03 | Spheal (EN) | contemplation_1.webp | Lv.17 print, distinct from spheal-01/02, number illegible |

**squirtle** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| squirtle-01 | Squirtle (EN) | world_people_1.webp | set code ambiguous under magnification |
| squirtle-02 | Squirtle (EN) | quiet_familiarity_1.webp | Wave Splash/Doubleslap attacks, distinct from squirtle-01, footer illegible after crop attempt |

**typhlosion** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| typhlosion-01 | バクフーン (JP) | intimidation_1.webp | vintage Pokedex-number print, era not identifiable |
| typhlosion-02 | バクフーン (JP) | legendary_bearing_1.webp | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |

**yveltal** (2)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| yveltal-01 | Yveltal EX (EN) | on_attack_1.webp | set code not textual |
| yveltal-02 | 伊裴尔塔尔 (ZH) | legendary_bearing_1.webp | distinct from yveltal-01, number illegible |

### Singletons (53 species, one unresolved row each)

| ID | Card name | Source image | Unreadable |
|---|---|---|---|
| absol-01 | Absol (EN) | elemental_solitude_1.webp | promo-style number, set code not textual |
| beldum-01 | Beldum (EN) | companions_1.webp | Steven's Beldum, Ram attack, number illegible after crop attempt |
| bewear-01 | キテルグマ (JP) | intimidation_1.webp | number illegible after crop attempt |
| blastoise-01 | カメックス (JP) | enduring_presence_2.webp | Lv.52 HP100, vintage Pokedex-number print, era not identifiable |
| chansey-01 | ラッキー (JP) | world_people_1.webp | set code truncated/illegible |
| cubone-01 | 卡拉卡拉 (ZH) | world_people_1.webp | number illegible |
| dialga-01 | ディアルガ (JP) | legendary_bearing_1.webp | Lv.69, No.483 dex entry, card number partially visible ("006/...") but remainder illegible, left blank rather than guessed |
| ditto-01 | Ditto (EN) | enduring_presence_1.webp | Metamorphosis Gene ability, Stick On attack, promo number, set not readable as text |
| dragonair-01 | エリカのハクリュー (JP) | enduring_presence_1.webp | Erika's Dragonair, Lv.32, vintage Pokedex-number print, era not identifiable |
| eevee-01 | Eevee (EN) | at_rest_1.webp | number illegible |
| entei-01 | 結晶塔のエンテイ (JP) | legendary_bearing_1.webp | No.244 dex entry, number illegible |
| gengar-mimikyu-01 | 耿鬼＆谜拟丘GX (ZH) | awakened_power_1.webp | TAG TEAM card featuring two species, printed name kept whole rather than split; number illegible |
| glaceon-01 | Glaceon (EN) | elemental_solitude_1.webp | Lv.46 print, number illegible after crop attempt |
| gyarados-01 | Dark Gyarados (EN) | awakened_power_1.webp | Team Rocket-era print with PRERELEASE stamp, number illegible |
| hoopa-01 | フーパ (JP) | threshold_1.webp | full-art secret rare, footer illegible after crop attempt |
| horsea-01 | Horsea (EN) | calm_nature_1.webp | e-card era border, number illegible |
| imposter-professor-oaks-revenge-01 | にせオーキドの逆襲 (JP) | companions_1.webp | Trainer card, vintage Team Rocket-era print, "R" rarity mark visible, number illegible |
| kingdra-01 | キングドラ (JP) | on_attack_1.webp | Lv.47, vintage Pokedex-number print, illustrator Mitsuhiro Arita, era not identifiable |
| kyogre-01 | Kyogre ex (EN) | elemental_solitude_1.webp | number illegible, below visible border |
| latias-01 | Latias (EN) | joyful_action_1.webp | secret rare numbering, set name not identifiable |
| lucario-01 | ルカリオVSTAR (JP) | intimidation_1.webp | VSTAR, SAR rarity mark; third digit of number ambiguous 5-vs-6 at source resolution |
| machop-01 | Machop (EN) | threshold_1.webp | Punch attack, set not readable as text |
| marill-01 | Marill (EN) | joyful_action_1.webp | vintage-style print, number legible, set name not shown |
| master-ball-01 | マスターボール (JP) | threshold_1.webp | Trainer item card, no number field visible after crop attempt |
| mimikyu-01 | 谜拟丘 (ZH) | companions_1.webp | Ability 假扮 (Disguise), number illegible |
| misdreavus-01 | ムウマ (JP) | intimidation_1.webp | number illegible |
| mudkip-01 | Mudkip (EN) | enduring_presence_1.webp | Nap/Waterfall attacks, number illegible after crop attempt |
| muk-01 | ベトベトン (JP) | enduring_presence_2.webp | Grimer evolution Lv.34, HP70, vintage Pokedex-number print, era not identifiable |
| ninetales-01 | キュウコン (JP) | legendary_bearing_2.webp | Lv.32, vintage Pokedex-number print, era not identifiable |
| ns-plan-01 | N's Plan (EN) | legendary_bearing_2.webp | Supporter trainer, double-star SR rarity mark, set code not textual |
| numel-01 | Numel (EN) | quiet_familiarity_1.webp | Firebreathing/Tackle attacks, e-Card era, set not readable as text |
| oshawott-01 | Oshawott (EN) | at_rest_1.webp | number illegible |
| pachirisu-01 | バチュル (JP) | contemplation_1.webp | AR rarity, set code not textual, number read with low confidence |
| piplup-01 | Piplup (EN) | quiet_familiarity_1.webp | Lv.9, Peck/Water Splash attacks, footer illegible after crop attempt |
| plusle-01 | プラスル (JP) | calm_nature_1.webp | notes blank in registry — number/set not captured |
| professors-research-01 | 博士の研究 (JP) | companions_2.webp | Supporter trainer, promo S-P number, featuring Professor Willow, set not readable as text |
| quaxly-01 | Quaxly (EN) | world_people_1.webp | number illegible |
| rayquaza-01 | Rayquaza (EN) | awakened_power_2.webp | set code not textual |
| rockets-trap-01 | ロケット団のワナ (JP) | companions_2.webp | Trainer card, vintage print, number illegible after crop attempt |
| sabrinas-gaze-01 | ナツメの眼 (JP) | intimidation_1.webp | trainer card, number illegible |
| salamence-01 | ボーマンダex (JP) | awakened_power_2.webp | set code not textual |
| scyther-01 | ストライク (JP) | awakened_power_2.webp | vintage Pokedex-number print, era not identifiable |
| sprigatito-01 | Sprigatito (EN) | at_rest_1.webp | number illegible |
| steelix-01 | ハガネール (JP) | enduring_presence_2.webp | vintage Pokedex-number print, era not identifiable |
| togepi-01 | トゲピー (JP) | enduring_presence_1.webp | number illegible after crop attempt |
| torterra-01 | Torterra (EN) | awakened_power_2.webp | set code not textual |
| ursaring-02 | リングマ (JP) | on_attack_1.webp | Lv.43 print, distinct from ursaring-01, vintage Pokedex-number print, era not identifiable |
| victini-01 | Victini (EN) | joyful_action_1.webp | number illegible |
| vulpix-01 | Vulpix (EN) | enduring_presence_2.webp | Collect Fire attack, e-Card era stamp, number ambiguous (119 or 116)/147, set not readable as text |
| walrein-01 | トドゼルガex (JP) | awakened_power_1.webp | number illegible |
| woobat-01 | オンバット (JP) | calm_nature_1.webp | set/number code visible but digits ambiguous under magnification, left blank rather than guess |
| zekrom-01 | Zekrom EX (EN) | legendary_bearing_2.webp | Slash/Voltage Burst, set code not textual |
| zygarde-01 | ジガルデ (JP) | threshold_1.webp | Aura Break attack, set not readable as text |

## 4. Gaps

**`quiet_familiarity_2` does not exist.** The design note assumed a Quiet Familiarity page 2
holding the binder's single empty pocket. `static/images/binder/volume-2/` has no file by that
name — only `quiet_familiarity_1.webp`, which shows 9 occupied pockets and 0 empty. Two
possibilities, both real:

- The page exists physically but was never photographed, in which case roughly 9 cards on it are
  missing from this registry entirely (not even in the "blocked" bucket — they were never seen).
- The page does not exist, and the earlier assumption that it did was simply wrong.

The curator needs to say which. Neither is assumed here.

**The one empty pocket is on a different page than expected.** Across both volumes, the only empty
pocket found is on `enduring_presence_1.webp` — 8 occupied, 1 empty, bottom-right. A current
curatorial ledger entry (`docs/ledger.md`, scheduled to be wiped and restarted under the ID scheme;
the entries remain in place until then, and will stay recoverable at git commit `a254855` afterward)
records the binder's single free pocket as being in Quiet Familiarity p2, with a pending card swap
planned into it (`docs/holding-box-placement.md` lines 14, 52, 167 — Cinccino AR into that slot).

If Quiet Familiarity p2 does not exist, that planned swap has no destination. If it does exist and
is simply unphotographed, its own empty-pocket status is unverified — this registry cannot confirm
or deny it. Either way, the planned Cinccino placement is now unresolved. This document does not
attempt to resolve it; flagging it for the curator's judgment only.
