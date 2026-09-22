# Card registry

Stable identifiers for every card in Volumes 1 and 2.

This is not an inventory. It records what a card **is**, never where it sits. A card's ID is unchanged when it moves from one theme to another, unchanged when it goes to the holding box, and unchanged after release. To find where a card is now, grep `ledger.md` for its ID and read forward.

## How to use this file

**IDs are permanent.** `<species>-<NN>`, using the English Pokédex species name for cards of every language, plus a counter that means nothing. If an ID later proves inaccurate — the card is a Houndoom, not the Houndour its ID says — correct the `species` column and leave the `id` alone. A rewritten ID breaks every reference already written against it.

**An ID freezes when something cites it.** The never-rewrite rule protects references, so it binds per-ID from the first citation — in `ledger.md` or anywhere else durable — not on a date. Three misidentified species caught in review were renumbered rather than left mismatched: the カラカラ card once numbered `marowak-01` is now `cubone-02`, and `marowak-01` now holds the genuine Marowak. That was safe because nothing cited those IDs. Renaming a **cited** ID means updating every citation in the same commit; leaving one dangling is the failure the rule exists to prevent. Every other column stays correctable forever — filling in a `set`, correcting a `species`, upgrading a `confidence` are all normal and expected.

**The ID carries no qualifiers.** `Houndoom G Lv.45` is `houndoom-NN`; `ドダイトス Lv.X` is `torterra-NN`; `M Gengar EX` is `gengar-NN`. Printed names live in `card_name`.

**Two species on one card.** A card printing two species — a TAG TEAM, or similar — uses both names hyphen-joined in printed order: `gengar-mimikyu-01`. One physical card, one ID.

**When in doubt, split.** If you cannot tell whether a card is a new copy or one already listed, assign a new ID. Two IDs for one card is recoverable — note `superseded-by: <id>`. One ID for two cards is not.

**Image filenames change.** `first_seen` names the file a row was read from at the time, not a file that necessarily still exists with that content. The 2026-08-01 gallery refresh replaced the binder images and corrected an off-by-one in the Volume II names; earlier filenames remain resolvable through git history.

**Volume II `first_seen` names are offset by one page.** The off-by-one correction above landed in the gallery filenames but not in this column, which still carries the pre-correction names. Do not read a Volume II `first_seen` value as the page a card sits on today — as written, the rows labelled `threshold_1.webp` are the Master Ball / Zygarde / Reshiram page, not Threshold.

The column is left as recorded rather than rewritten: `first_seen` is provenance, and these are the names the rows were genuinely read under. The authoritative mapping from these names to the pages they truly depict is `PAGE_ORDER` in `scripts/check-registry.py`, so the correction is enforced by the validator rather than restated in prose; `docs/registry-confirmation.md` §4 explains how the offset was pinned. To place a card, read its `first_seen` through `PAGE_ORDER` — never off this column directly — then check `ledger.md` for a later move. The ledger records only contested placements and releases, so a card with no entry there has not moved and sits where `PAGE_ORDER` puts it.

**Reshoot provenance.** Rows whose `first_seen` names an `IMG_####.HEIC` file come from the 2026-08-01 whole-binder reshoot. Those originals are the owner's camera files and are not stored in this repository.

**Design note:** `superpowers/specs/2026-08-01-card-registry-design.md`.

**Validate with:** `python scripts/check-registry.py docs/card-registry.md`

**2026-09-20 verification scope.** The owner checked the character and printed number for the 20 in-binder entries on the [completed checklist](evidence/2026-09-20/validation/completed-checklist.pdf), not their set names. Those ticks do not upgrade printing confidence. Bulbasaur's `Corocoro Promo` set was supplied separately; the explicit Umbreon, Latios and Dratini corrections are recorded below. See the [evidence notes](evidence/2026-09-20/README.md) for the checked IDs and limitations.

## Registry

| id | species | card_name | language | set | number | confidence | first_seen | notes |
|---|---|---|---|---|---|---|---|---|
| absol-01 | Absol | Absol | EN | XY | XY178 | confirmed | elemental_solitude_1.webp 2026-08-01 | promo-style number |
| ampharos-01 | Ampharos | ミカンのデンリュウ | JP | Pokémon VS | 031/141 | confirmed | IMG_6853.HEIC 2026-08-01 | Jasmine's Ampharos, VS-series print, checked in hand 2026-09-19 |
| arcanine-01 | Arcanine | Light Arcanine | EN | Neo Destiny | 12/105 | confirmed | enduring_presence_1.webp 2026-08-01 | Light card, Drive Off ability, Gentle Flames attack |
| audino-01 | Audino | タブンネ | JP | sv11B | 156/086 | confirmed | calm_nature_1.webp 2026-08-01 | set corrected from sv1b (misread): owner's doubleholo entry is Black Bolt, TCGdex SV11B-156 is タブンネ |
| beldum-01 | Beldum | Beldum | EN | SVP | 207 | confirmed | companions_1.webp 2026-08-01 | Steven's Beldum, Ram attack, set/number from owner's doubleholo export 2026-09-18 |
| bewear-01 | Bewear | キテルグマ | JP | sv6a | 076 | confirmed | intimidation_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| blastoise-01 | Blastoise | カメックス | JP | Expansion Pack | No.009 | uncertain | enduring_presence_2.webp 2026-08-01 | Lv.52 HP100, vintage Pokedex-number print, set per owner's doubleholo entry |
| bulbasaur-01 | Bulbasaur | Bulbasaur | EN | Crystal Guardians | 45/100 | confirmed | calm_nature_1.webp 2026-08-01 |  |
| bulbasaur-02 | Bulbasaur | フシギダネ | JP | Corocoro Promo | No.001 | uncertain | joyful_action_1.webp 2026-08-01 | set supplied by owner 2026-09-20; character and printed Pokedex number checked in hand, no blanket set/printing verification from checklist ticks |
| bulbasaur-03 | Bulbasaur | Bulbasaur | EN | Expedition | 95 | confirmed | enduring_presence_2.webp 2026-08-01 | Sleep Seed ability, Vine Whip attack, distinct from bulbasaur-01/02, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| celebi-01 | Celebi | Celebi | EN | Neo Revelation | 16/64 | confirmed | enduring_presence_1.webp 2026-08-01 | Psychic Leaf attack |
| chansey-01 | Chansey | ラッキー | JP | sv6 | 113/101 | confirmed | world_people_1.webp 2026-08-01 |  |
| charizard-01 | Charizard | リザードンG | JP | Charizard Half Deck | 002/016 | confirmed | on_attack_1.webp 2026-08-01 | Lv.X print, checked in hand 2026-09-19 |
| charizard-02 | Charizard | リザードン | JP | s8b | 187 | confirmed | companions_1.webp 2026-08-01 | Ability バトルセンス, キングブレイズ attack, distinct from charizard-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| charmander-01 | Charmander | Charmander | EN | SVP | 44 | confirmed | world_people_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18 |
| charmander-02 | Charmander | Charmander | EN | Vivid Voltage | 023/185 | confirmed | joyful_action_1.webp 2026-08-01 | distinct printing from charmander-01 |
| charmander-03 | Charmander | Charmander | EN | Expedition | 98 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Gnaw/Searing Flame attacks, distinct from charmander-01/02, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| cinccino-01 | Cinccino | チラチーノ | JP | sv5K | 083/071 | confirmed | IMG_6860.HEIC 2026-08-01 | AR rarity mark |
| cubone-01 | Cubone | 卡拉卡拉 | ZH | Gem Pack 3 | 407 | confirmed | world_people_1.webp 2026-08-01 | set/number supplied by owner 2026-09-18 (Chinese Gem Pack 3), printed set code not recorded |
| cubone-02 | Cubone | カラカラ | JP | Flight of Legends | 062/082 | confirmed | at_rest_1.webp 2026-08-01 | vintage-style print, checked in hand 2026-09-19 |
| cyndaquil-01 | Cyndaquil | Cyndaquil | EN | Dragon Frontiers | 45 | confirmed | calm_nature_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| cyndaquil-02 | Cyndaquil | Cyndaquil | EN | Unseen Forces | 54/115 | confirmed | elemental_solitude_1.webp 2026-08-01 | distinct from cyndaquil-01 |
| darkrai-01 | Darkrai | Darkrai EX | EN | BREAKpoint | 118/122 | confirmed | awakened_power_1.webp 2026-08-01 | checked in hand 2026-09-19 |
| darkrai-02 | Darkrai | ダークライVSTAR | JP | s12a | 228/172 | confirmed | elemental_solitude_1.webp 2026-08-01 | VSTAR, SAR rarity mark, distinct from darkrai-01 |
| darkrai-03 | Darkrai | Darkrai | EN | XY | XY114 | confirmed | legendary_bearing_1.webp 2026-08-01 | Dark Cutter/Abyssal Sleep, distinct from darkrai-01/02, set/number from owner's doubleholo export 2026-09-18 |
| dawns-stadium-01 | Dawn's Stadium | 夜明けのスタジアム | JP | Dawn Dash |  | confirmed | IMG_6865.HEIC 2026-08-01 | Stadium trainer card, no number printed, checked in hand 2026-09-19 |
| deoxys-01 | Deoxys | Deoxys | EN | Call of Legends | SL1 | confirmed | IMG_6865.HEIC 2026-08-01 | Cell Storm attack, set/number from owner's doubleholo export 2026-09-18 |
| dialga-01 | Dialga | ディアルガ | JP | 11th Movie Commemoration Promo | 8 | confirmed | legendary_bearing_1.webp 2026-08-01 | Lv.69, No.483 dex entry, set/number from owner's doubleholo export 2026-09-18 |
| ditto-01 | Ditto | Ditto | EN | XY | XY40 | confirmed | enduring_presence_1.webp 2026-08-01 | Metamorphosis Gene ability, Stick On attack, promo number |
| dragonair-01 | Dragonair | エリカのハクリュー | JP | Leaders' Stadium | No.148 | uncertain | enduring_presence_1.webp 2026-08-01 | Erika's Dragonair, Lv.32, vintage Pokedex-number print, set per owner's doubleholo entry |
| dragonite-01 | Dragonite | カイリュー | JP | Mystery of the Fossils | No.149 | uncertain | contemplation_1.webp 2026-08-01 | Lv.45 print, vintage Pokedex-number print, set per owner's doubleholo entry |
| dragonite-02 | Dragonite | カイリューex | JP | Rulers of the Heavens | 038/054 | confirmed | legendary_bearing_2.webp 2026-08-01 | ex card, distinct from dragonite-01 |
| dratini-01 | Dratini | Dratini | EN | Team Rocket | 53/82 | confirmed | contemplation_1.webp 2026-08-01 | checked in hand 2026-09-19 |
| dratini-02 | Dratini | Dratini | EN | Base Set | 26/102 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Pound attack, distinct from dratini-01; owner corrected Base Set 2 38/130 to Base Set 26/102 on completed checklist 2026-09-20; no card move |
| eevee-01 | Eevee | Eevee | EN | SVP | 173 | confirmed | at_rest_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18 |
| electrode-01 | Electrode | マルマイン | JP | sm1 | 037/095 | photo | companions_2.webp 2026-08-01 |  |
| emolga-01 | Emolga | エモンガ | JP | sv11B | 116/086 | confirmed | joyful_action_1.webp 2026-08-01 | checked in hand 2026-09-19 |
| entei-01 | Entei | 結晶塔のエンテイ | JP | 10th Movie Commemoration Promo |  | confirmed | legendary_bearing_1.webp 2026-08-01 | No.244 dex entry, holo, no card number recorded, no number printed, checked in hand 2026-09-19 |
| espeon-01 | Espeon | わるいエーフィ | JP | Darkness, and to Light | No.196 | uncertain | elemental_solitude_1.webp 2026-08-01 | Dark Espeon, vintage-style print, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| espeon-02 | Espeon | 太阳伊布GX | ZH | CSM1AC | 195/151 | confirmed | legendary_bearing_2.webp 2026-08-01 | GX card, SSR rarity mark, distinct from espeon-01, 太阳伊布 is Espeon's Chinese localized name, checked in hand 2026-09-19 |
| flareon-01 | Flareon | Flareon EX | EN | Radiant Collection | RC28/RC32 | confirmed | companions_2.webp 2026-08-01 | checked in hand 2026-09-19 |
| gardevoir-01 | Gardevoir | ザーナイトex | JP | Miracle of the Desert | 28 | confirmed | legendary_bearing_2.webp 2026-08-01 | ex card, Breakdown/Psycho Storm, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| gardevoir-02 | Gardevoir | Gardevoir | EN | Astral Radiance | TG05 | confirmed | companions_1.webp 2026-08-01 | Ability Shining Arcana, Prainwave attack, distinct from gardevoir-01, set/number from owner's doubleholo export 2026-09-18 |
| gengar-01 | Gengar | 耿鬼VMAX | ZH | s6c | 072/172 | photo | awakened_power_2.webp 2026-08-01 | Single Strike era, distinct from gengar-mimikyu-01 TAG TEAM |
| gengar-02 | Gengar | ゲンガー | JP | Mystery of the Fossils | No.094 | uncertain | intimidation_1.webp 2026-08-01 | Lv.38 print, distinct from gengar-01 and gengar-mimikyu-01, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| gengar-03 | Gengar | M Gengar EX | EN | Phantom Forces | 35/119 | confirmed | on_attack_1.webp 2026-08-01 | Mega Evolution EX, Phantom Gate attack, distinct from gengar-01/02 and gengar-mimikyu-01, language corrected from JP, checked in hand 2026-09-19 |
| gengar-04 | Gengar | ゲンガー | JP | s10a | 074 | confirmed | companions_1.webp 2026-08-01 | Ability たくらみのうごう, スクリームサークル attack, distinct from gengar-01..03, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| gengar-05 | Gengar | わるいゲンガー | JP | Darkness, and to Light | No.094 | uncertain | enduring_presence_2.webp 2026-08-01 | Dark Gengar, HP70, distinct from gengar-01..04, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| gengar-mimikyu-01 | Gengar & Mimikyu | 耿鬼＆谜拟丘GX | ZH | CSM2BC | 033/150 | confirmed | awakened_power_1.webp 2026-08-01 | TAG TEAM card featuring two species, printed name kept whole rather than split, checked in hand 2026-09-19 |
| glaceon-01 | Glaceon | Glaceon | EN | Majestic Dawn | 20 | confirmed | elemental_solitude_1.webp 2026-08-01 | Lv.46 print, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| golem-01 | Golem | Golem EX | EN | Scarlet & Violet 151 | 189/165 | confirmed | awakened_power_2.webp 2026-08-01 |  |
| golem-02 | Golem | ゴローニャex | JP | Magma Vs Aqua Two Ambitions | 48 | confirmed | legendary_bearing_2.webp 2026-08-01 | ex card, distinct from golem-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| greavard-01 | Greavard | Greavard | EN | Scarlet & Violet | 214/198 | confirmed | world_people_1.webp 2026-08-01 | secret rare, checked in hand 2026-09-19 |
| grotle-01 | Grotle | ハヤシガメ | JP | sv5K | 072/071 | confirmed | companions_1.webp 2026-08-01 | checked in hand 2026-09-19 |
| groudon-01 | Groudon | Groudon | EN | Hidden Legends | 102 | confirmed | awakened_power_1.webp 2026-08-01 | denominator not recorded, checked in hand 2026-09-19 |
| groudon-02 | Groudon | Groudon | EN | Prismatic Evolutions | 049/131 | confirmed | legendary_bearing_1.webp 2026-08-01 | Swelling Power/Magma Purge, distinct from groudon-01, checked in hand 2026-09-19 |
| groudon-03 | Groudon | Groudon | EN | Primal Clash | 84/100 | confirmed | enduring_presence_2.webp 2026-08-01 | Rock Smash/Break Ground attacks, AR rarity mark |
| gyarados-01 | Gyarados | Dark Gyarados | EN | Team Rocket | 25 | confirmed | awakened_power_1.webp 2026-08-01 | Team Rocket-era print with PRERELEASE stamp, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| hoopa-01 | Hoopa | フーパ | JP | XY-P | 155/XY-P | confirmed | threshold_1.webp 2026-08-01 | full-art secret rare, set/number from owner's doubleholo export 2026-09-18 |
| hoopa-02 | Hoopa | Hoopa EX | EN | Ancient Origins | 36/98 | confirmed | IMG_6865.HEIC 2026-08-01 | Scoundrel Ring ability, Hyperspace Fury attack, distinct from hoopa-01, checked in hand 2026-09-19 |
| horsea-01 | Horsea | Horsea | EN | Aquapolis | 84 | confirmed | calm_nature_1.webp 2026-08-01 | e-card era border, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| houndoom-01 | Houndoom | Houndoom | EN | Battle Styles | 179 | confirmed | awakened_power_1.webp 2026-08-01 | Single Strike era print, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| houndoom-02 | Houndoom | ヘルガー | JP | sv6a | 066/064 | confirmed | on_attack_1.webp 2026-08-01 | AR rarity, distinct from houndoom-01 |
| houndoom-03 | Houndoom | Houndoom | EN | Neo Revelation | 8/64 | confirmed | elemental_solitude_1.webp 2026-08-01 | Dark Flame/Black Fang, Lv.35 #219 dex entry in flavor text, distinct from houndoom-01/02 |
| houndoom-04 | Houndoom | Houndoom | EN | Neo Discovery | 23/75 | confirmed | threshold_1.webp 2026-08-01 | Crunch/Flamethrower attacks, distinct from houndoom-01..03, checked in hand 2026-09-19 |
| houndour-01 | Houndour | Houndour | EN | Expedition | 113/165 | confirmed | intimidation_1.webp 2026-08-01 | illustrator Mitsuhiro Arita credited |
| houndour-02 | Houndour | デルビル | JP | sv3 | 115 | confirmed | companions_2.webp 2026-08-01 | distinct from houndour-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| imposter-professor-oaks-revenge-01 | Imposter Professor Oak's Revenge | にせオーキドの逆襲 | JP | Rocket Gang |  | confirmed | companions_1.webp 2026-08-01 | Trainer card, vintage Team Rocket-era print, "R" rarity mark visible, no number printed, checked in hand 2026-09-19 |
| jirachi-01 | Jirachi | Jirachi | EN | XY | XY67a | confirmed | joyful_action_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18 |
| jirachi-02 | Jirachi | 基拉祈V | ZH | CS5.5C | 36/66 | confirmed | awakened_power_1.webp 2026-08-01 | distinct printing from jirachi-01, checked in hand 2026-09-19 |
| jirachi-03 | Jirachi | ジラーチex | JP | Player's Club | 032/PLAY | confirmed | enduring_presence_2.webp 2026-08-01 | ex card, promo Play number, checked in hand 2026-09-19 |
| jirachi-04 | Jirachi | 七夜のジラーチ | JP | Temple of Anger |  | confirmed | IMG_6865.HEIC 2026-08-01 | みらいよち/はめつのねがい attacks, distinct from jirachi-01..03, no number printed, checked in hand 2026-09-19 |
| joltik-01 | Joltik | 电电虫 | ZH | CSV5C | 132/129 | confirmed | companions_2.webp 2026-08-01 | holo print, checked in hand 2026-09-19 |
| joltik-02 | Joltik | Joltik | EN | Stellar Crown | 150/142 | confirmed | enduring_presence_2.webp 2026-08-01 | Jolting Charge attack, distinct from joltik-01, checked in hand 2026-09-19 |
| joltik-03 | Joltik | バチュル | JP | sv11W | 113/086 | confirmed | contemplation_1.webp 2026-08-01 | AR rarity, checked in hand 2026-09-19 |
| kabuto-01 | Kabuto | Kabuto | EN | Fossil | 50/62 | confirmed | IMG_6865.HEIC 2026-08-01 | Kabuto Armor ability, Scratch attack |
| kangaskhan-01 | Kangaskhan | ガルーラ | JP | Jungle | No.115 | uncertain | IMG_6858.HEIC 2026-08-01 | vintage Pokedex-number print, set per owner's doubleholo entry |
| kasumis-tears-01 | Kasumi's Tears | カスミのなみだ | JP | Leaders' Stadium |  | confirmed | IMG_6865.HEIC 2026-08-01 | Trainer card, no number printed, checked in hand 2026-09-19 |
| kingdra-01 | Kingdra | キングドラ | JP | Awakening Legends | No.230 | uncertain | on_attack_1.webp 2026-08-01 | Lv.47, vintage Pokedex-number print, illustrator Mitsuhiro Arita, set per owner's doubleholo entry |
| kyogre-01 | Kyogre | Kyogre ex | EN | Crystal Guardians | 95 | confirmed | elemental_solitude_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| latias-01 | Latias | Latias | EN | Latias & Latios 2015 | 30/30 | confirmed | joyful_action_1.webp 2026-08-01 | XY Trainer Kit card, owner checked in hand 2026-09-18; earlier 35/30 was a misread |
| latios-01 | Latios | ラティオス | JP | sv7a | 070/064 | confirmed | contemplation_1.webp 2026-08-01 | AR rarity |
| latios-02 | Latios | ラティオス | JP | Holon Phantom | 14 | confirmed | elemental_solitude_1.webp 2026-08-01 | distinct from latios-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| latios-03 | Latios | Latios | EN | Latios & Latias Trainer Kit | 30/30 | confirmed | legendary_bearing_1.webp 2026-08-01 | Supersonic Flight/Psyburn; owner corrected Dragon Vault 10/20 to Latios + Latias deck 30/30 on completed checklist 2026-09-20; the Dragon Vault card is separate in the stamped collection |
| lucario-01 | Lucario | ルカリオVSTAR | JP | s12a | 226/172 | confirmed | intimidation_1.webp 2026-08-01 | VSTAR, SAR rarity mark |
| lugia-01 | Lugia | ルギア | JP | Gold, Silver, New World | No.249 | photo | awakened_power_1.webp 2026-08-01 | vintage Pokedex-number print, set per owner's doubleholo entry; 2026-09-22 identity was visually established from the archived photo and DoubleHolo provider image, not an in-hand check. |
| lugia-02 | Lugia | ルギアV | JP | s12 | 079/098 | confirmed | on_attack_1.webp 2026-08-01 | V card, distinct from lugia-01 |
| lugia-03 | Lugia | Lugia | EN | Neo Revelation | 20/64 | confirmed | legendary_bearing_1.webp 2026-08-01 | Aerowing attack, No.249 dex entry, vintage print, distinct from lugia-01/02, checked in hand 2026-09-19 |
| machop-01 | Machop | Machop | EN | Lost Origin | 086/136 | confirmed | threshold_1.webp 2026-08-01 | Punch attack |
| marill-01 | Marill | Marill | EN | Neo Genesis | 66/111 | confirmed | joyful_action_1.webp 2026-08-01 | vintage-style print, number legible, set name not shown, checked in hand 2026-09-19 |
| marowak-01 | Marowak | ガラガラ | JP | Holon Research | 58 | confirmed | intimidation_1.webp 2026-08-01 | delta species print, distinct from cubone-02 (the カラカラ), set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| master-ball-01 | Master Ball | マスターボール | JP | City Gym Decks |  | confirmed | threshold_1.webp 2026-08-01 | Trainer item card, no number printed, checked in hand 2026-09-19 |
| mew-01 | Mew | Mew ex | EN | SVP | 053 | photo | world_people_1.webp 2026-08-01 | promo stamp |
| mew-02 | Mew | ミュウ | JP | s12a | 183/172 | photo | at_rest_1.webp 2026-08-01 | number corrected from 187/172 by owner 2026-09-22; identity was visually established from the archived photo and provider images (DoubleHolo 37751, TCGdex S12a-183), not an in-hand check; distinct printing from mew-01 |
| mew-03 | Mew | Mew ex | EN | Scarlet & Violet 151 | 193/165 | confirmed | legendary_bearing_2.webp 2026-08-01 | double-star SR rarity mark, distinct from mew-01/02, language and name corrected from JP Mew GX, checked in hand 2026-09-19 |
| mew-04 | Mew | ミュウ | JP | Mirage's Mew Constructed Starter Deck | 5 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Pokepower type-change, Link Blast attack, distinct from mew-01..03, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| mew-05 | Mew | ミュウ | JP | Mystery of the Fossils | No.151 | uncertain | threshold_1.webp 2026-08-01 | Psywave/Recover-Beam attacks, distinct from mew-01..04, Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| mewtwo-01 | Mewtwo | Mewtwo | EN | Legendary Collection | 29/110 | photo | awakened_power_2.webp 2026-08-01 | reverse holo; owner corrected prior confirmed WoTC Promos 12 identity during 2026-09-22 image review; corrected identity was visually established from the archived photo and authorized DoubleHolo card 2767, not an in-hand check |
| mewtwo-02 | Mewtwo | Mewtwo EX | EN | BREAKthrough | 164/162 | confirmed | intimidation_1.webp 2026-08-01 | Shatter Shot/Damage Change EX card, distinct from mewtwo-01 |
| mewtwo-03 | Mewtwo | Mewtwo | EN | SVP | 052 | confirmed | contemplation_1.webp 2026-08-01 | Scarlet & Violet promo, Reflective Barrier/Psyslash, distinct from mewtwo-01/02 |
| mewtwo-04 | Mewtwo | Mewtwo | EN | Delta Species | 12/113 | confirmed | legendary_bearing_1.webp 2026-08-01 | delta species, Delta Switch/Energy Burst, distinct from mewtwo-01/02/03, set from owner's doubleholo export 2026-09-18; Delta Species has 113 cards, matching the /113 read |
| mimikyu-01 | Mimikyu | 谜拟丘 | ZH | CSM2BC | 151/150 | confirmed | companions_1.webp 2026-08-01 | Ability 假扮 (Disguise), checked in hand 2026-09-19 |
| misdreavus-01 | Misdreavus | ムウマ | JP | Awakening Legends | No.200 | uncertain | intimidation_1.webp 2026-08-01 | Pokédex-number print, set per owner's doubleholo export 2026-09-18 |
| mudkip-01 | Mudkip | Mudkip | EN | Crystal Guardians | 58 | confirmed | enduring_presence_1.webp 2026-08-01 | Nap/Waterfall attacks, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| muk-01 | Muk | ベトベトン | JP | Mystery of the Fossils | No.089 | uncertain | enduring_presence_2.webp 2026-08-01 | Grimer evolution Lv.34, HP70, vintage Pokedex-number print, set per owner's doubleholo entry |
| ninetales-01 | Ninetales | キュウコン | JP | Expansion Pack | No.038 | uncertain | legendary_bearing_2.webp 2026-08-01 | Lv.32, vintage Pokedex-number print, set per owner's doubleholo entry |
| noibat-01 | Noibat | オンバット | JP | sv9 | 111 | confirmed | calm_nature_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| ns-plan-01 | N's Plan | N's Plan | EN | Black Bolt | 163/086 | confirmed | legendary_bearing_2.webp 2026-08-01 | Supporter trainer, double-star SR rarity mark, checked in hand 2026-09-19 |
| numel-01 | Numel | Numel | EN | EX Dragon | 69/97 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Firebreathing/Tackle attacks, e-Card era, checked in hand 2026-09-19 |
| oshawott-01 | Oshawott | Oshawott | EN | White Flare | 105 | confirmed | at_rest_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| palkia-01 | Palkia | Palkia | EN | Great Encounters | 26/106 | confirmed | awakened_power_2.webp 2026-08-01 | Lv.67, "PLATINUM" is a stamp on the card face, checked in hand 2026-09-19 |
| pikachu-01 | Pikachu | Pikachu | EN | WoTC Promos | 27 | confirmed | calm_nature_1.webp 2026-08-01 | classic border, set/number from owner's doubleholo export 2026-09-18 |
| pikachu-02 | Pikachu | Surfing Pikachu | EN | Evolutions | 111/108 | confirmed | joyful_action_1.webp 2026-08-01 | vintage-style print, distinct from pikachu-01 |
| pikachu-03 | Pikachu | 皮卡丘 | ZH | CSM2AC | 153/150 | confirmed | companions_1.webp 2026-08-01 | CHR rarity mark, Ash-style artwork, checked in hand 2026-09-19 |
| pikachu-04 | Pikachu | Pikachu | EN | Pokémon GO | 027/078 | photo | companions_2.webp 2026-08-01 | Buddy Bolt attack, distinct from pikachu-01/02/03 |
| pikachu-05 | Pikachu | Pikachu | EN | Skyridge | 84/144 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Max Voltage attack, e-Card era, distinct from pikachu-01..04 |
| pikachu-06 | Pikachu | ピカチュウ | JP | SVP | 242 | confirmed | IMG_6842.HEIC 2026-08-01 | Pokémon Illustration Contest 2024 promo stamp |
| pikachu-07 | Pikachu | Pikachu | EN | POP Series 5 | 12/17 | confirmed | IMG_6865.HEIC 2026-08-01 | Lightning Ball/Thunderbolt attacks, distinct from pikachu-01..06 |
| piplup-01 | Piplup | Piplup | EN | POP Series 6 | 15 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Lv.9, Peck/Water Splash attacks, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| plusle-01 | Plusle | プラスル | JP | Rulers of the Heavens | 26 | confirmed | calm_nature_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| professor-elm-01 | Professor Elm | Professor Elm | EN | Neo Genesis | 96/111 | confirmed | companions_2.webp 2026-08-01 | checked in hand 2026-09-19 |
| professors-research-01 | Professor's Research | 博士の研究 | JP | S-P | 224/S-P | confirmed | companions_2.webp 2026-08-01 | Supporter trainer, promo S-P number, featuring Professor Willow |
| quaxly-01 | Quaxly | Quaxly | EN | Paldea Evolved | 206 | confirmed | world_people_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| ralts-01 | Ralts | ラルトス | JP | sv1S | 083/078 | confirmed | world_people_1.webp 2026-08-01 | AR rarity, checked in hand 2026-09-19 |
| rayquaza-01 | Rayquaza | Rayquaza | EN | Vivid Voltage | 138/185 | confirmed | awakened_power_2.webp 2026-08-01 |  |
| rayquaza-02 | Rayquaza | Rayquaza ex | EN | Nintendo Promos | 39 | confirmed | IMG_6865.HEIC 2026-08-01 | Frenzy/Dragon Bind/Twister, distinct from rayquaza-01, set/number from owner's doubleholo export 2026-09-18 |
| reshiram-01 | Reshiram | レシラム | JP | sv9 | 109/100 | confirmed | companions_1.webp 2026-08-01 | AR rarity mark |
| reshiram-02 | Reshiram | Reshiram | EN | Black & White | 113/114 | confirmed | threshold_1.webp 2026-08-01 | Outrage/Blue Flare attacks, distinct from reshiram-01, checked in hand 2026-09-19 |
| rockets-trap-01 | Rocket's Trap | ロケット団のワナ | JP | Leaders' Stadium |  | confirmed | companions_2.webp 2026-08-01 | Trainer card, vintage print, no number printed, checked in hand 2026-09-19 |
| sabrinas-gaze-01 | Sabrina's Gaze | ナツメの眼 | JP | Challenge From The Darkness |  | confirmed | intimidation_1.webp 2026-08-01 | trainer card, no number printed, checked in hand 2026-09-19 |
| salamence-01 | Salamence | ボーマンダex | JP | sv9 | 119/100 | confirmed | awakened_power_2.webp 2026-08-01 |  |
| sandshrew-01 | Sandshrew | Sandshrew | EN | Team Rocket Returns | 74 | confirmed | calm_nature_1.webp 2026-08-01 | small logo bottom-right, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| sandshrew-02 | Sandshrew | Sandshrew | EN | Delta Species | 82 | confirmed | threshold_1.webp 2026-08-01 | Dig Under/Scratch attacks, distinct from sandshrew-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| scyther-01 | Scyther | ストライク | JP | Jungle | No.123 | photo | awakened_power_2.webp 2026-08-01 | vintage Pokedex-number print; 2026-09-22 identity was visually established from the archived photo and DoubleHolo candidate 22164, not an in-hand check |
| shaymin-01 | Shaymin | Shaymin EX | EN | XY | XY148 | photo | at_rest_1.webp 2026-08-01 | promo number normalized from 148 to XY148 during 2026-09-22 image review; XY Black Star Promo, artist Kanako Eo |
| shaymin-02 | Shaymin | シェイミLv.X | JP | Galactic's Conquest | 15 | confirmed | awakened_power_2.webp 2026-08-01 | distinct printing from shaymin-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| shaymin-03 | Shaymin | Shaymin | EN | Destined Rivals | 185/142 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Ability Flower Curtain, Smash Kick attack, distinct from shaymin-01/02 |
| shaymin-04 | Shaymin | Shaymin | EN | Unleashed | 8 | confirmed | threshold_1.webp 2026-08-01 | Ability Celebration Wind, Energy Bloom attack, distinct from shaymin-01..03, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| slowpoke-01 | Slowpoke | ヤドン | JP | sv1V | 082/078 | confirmed | world_people_1.webp 2026-08-01 | AR rarity |
| snivy-01 | Snivy | Snivy | EN | BW | BW06 | confirmed | calm_nature_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18 |
| snivy-02 | Snivy | ツタージャ | JP | sv11B | 087/086 | confirmed | contemplation_1.webp 2026-08-01 | distinct from snivy-01, checked in hand 2026-09-19 |
| snivy-03 | Snivy | Snivy | EN | Legendary Treasures | 6/113 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Leaf Blade attack, distinct from snivy-01/02 |
| snorlax-01 | Snorlax | カビゴン | JP | sv2a | 181 | confirmed | at_rest_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| snorlax-02 | Snorlax | カビゴンVMAX | JP | s1H | 046/060 | photo | on_attack_1.webp 2026-08-01 | VMAX, distinct from snorlax-01 |
| snorlax-03 | Snorlax | Snorlax | EN | Fire Red & Leaf Green | 15 | confirmed | enduring_presence_1.webp 2026-08-01 | Rest Up ability, Collapse/Toss and Turn attacks, distinct from snorlax-01/02, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| spheal-01 | Spheal | タマザラシ | JP | sv8 | 111/106 | photo | joyful_action_1.webp 2026-08-01 | AR rarity; owner corrected number 2026-09-22; identity was visually established from the archived photo and DoubleHolo card 37220 provider image matching JP sv8 Super Electric Breaker AR, not an in-hand check |
| spheal-02 | Spheal | タマザラシ | JP | Bonds to the End of Time | 016/086 | confirmed | on_attack_1.webp 2026-08-01 | Lv.18 print, distinct from spheal-01 |
| spheal-03 | Spheal | Spheal | EN | Mysterious Treasures | 102 | confirmed | contemplation_1.webp 2026-08-01 | Lv.17 print, distinct from spheal-01/02, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| sprigatito-01 | Sprigatito | Sprigatito | EN | Paldea Evolved | 196 | confirmed | at_rest_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| squirtle-01 | Squirtle | Squirtle | EN | Stellar Crown | 148/142 | confirmed | world_people_1.webp 2026-08-01 |  |
| squirtle-02 | Squirtle | Squirtle | EN | Expedition | 131 | confirmed | quiet_familiarity_1.webp 2026-08-01 | Wave Splash/Doubleslap attacks, distinct from squirtle-01, set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| squirtle-03 | Squirtle | Squirtle | EN | Scarlet & Violet 151 | 170/165 | confirmed | IMG_6865.HEIC 2026-08-01 | Withdraw/Skull Bash attacks, distinct from squirtle-01/02, checked in hand 2026-09-19 |
| steelix-01 | Steelix | ハガネール | JP | Gold, Silver, New World | No.208 | uncertain | enduring_presence_2.webp 2026-08-01 | vintage Pokedex-number print, number corrected from No.205 (misread): Steelix is Pokédex #208, matching owner's doubleholo export 2026-09-18 |
| stufful-01 | Stufful | ヌイコグマ | JP | m1S | 075/063 | confirmed | at_rest_1.webp 2026-08-01 | checked in hand 2026-09-19 |
| togedemaru-01 | Togedemaru | Togedemaru | EN | Phantasmal Flames | 104/94 | confirmed | companions_2.webp 2026-08-01 | checked in hand 2026-09-19 |
| togepi-01 | Togepi | トゲピー | JP | Rocket Gang Strikes Back | 56 | confirmed | enduring_presence_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| torterra-01 | Torterra | Torterra | EN | Unleashed | 10/95 | confirmed | awakened_power_2.webp 2026-08-01 |  |
| typhlosion-01 | Typhlosion | バクフーン | JP | Gold, Silver, New World | No.157 | uncertain | intimidation_1.webp 2026-08-01 | vintage Pokedex-number print, set per owner's doubleholo entry |
| typhlosion-02 | Typhlosion | バクフーン | JP |  | No.157 | uncertain | legendary_bearing_1.webp 2026-08-01 | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |
| umbreon-01 | Umbreon | 月亮伊布VMAX | ZH | CS4AC | 085/132 | confirmed | awakened_power_1.webp 2026-08-01 | owner corrected set/number to CS4AC 085/132 and confirmed Chinese on completed checklist 2026-09-20; close rearing figure amid energy, not moon-and-tower artwork |
| umbreon-02 | Umbreon | ブラッキー | JP | Crossing The Ruins | No.197 | uncertain | contemplation_1.webp 2026-08-01 | vintage Pokedex-number print, distinct from umbreon-01, set per owner's doubleholo entry |
| umbreon-03 | Umbreon | Umbreon | EN |  | 61/108 | uncertain | elemental_solitude_1.webp 2026-08-01 | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |
| umbreon-04 | Umbreon | Umbreon | EN | Undaunted | 10/90 | confirmed | legendary_bearing_2.webp 2026-08-01 | Moonlight Fang/Quick Blow, RH holo mark, distinct from umbreon-01/02/03, checked in hand 2026-09-19 |
| umbreon-05 | Umbreon | ブラッキー | JP | Magma Vs Aqua Two Ambitions | 062/080 | confirmed | enduring_presence_1.webp 2026-08-01 | distinct from umbreon-01..04, checked in hand 2026-09-19 |
| ursaring-01 | Ursaring | Ursaring | EN | Radiant Collection | RC16/RC25 | photo | at_rest_1.webp 2026-08-01 | artist Sonosuke Sakuma |
| ursaring-02 | Ursaring | リングマ | JP | Crossing The Ruins | No.217 | uncertain | on_attack_1.webp 2026-08-01 | Lv.43 print, distinct from ursaring-01, vintage Pokedex-number print, set per owner's doubleholo entry |
| victini-01 | Victini | Victini | EN | Unified Minds | 26 | confirmed | joyful_action_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| victini-02 | Victini | Victini | EN | SVP | 208 | confirmed | contemplation_1.webp 2026-08-01 | Scarlet & Violet promo, V-Force attack, distinct from victini-01 |
| vulpix-01 | Vulpix | Vulpix | EN | Aquapolis | 116/147 | confirmed | enduring_presence_2.webp 2026-08-01 | Collect Fire attack, e-Card era stamp, checked in hand 2026-09-19 |
| walrein-01 | Walrein | トドゼルガex | JP | Mirage Forest | 29 | confirmed | awakened_power_1.webp 2026-08-01 | set/number from owner's doubleholo export 2026-09-18, denominator not recorded |
| yveltal-01 | Yveltal | Yveltal EX | EN | XY | 79/146 | confirmed | on_attack_1.webp 2026-08-01 |  |
| yveltal-02 | Yveltal | 伊裴尔塔尔 | ZH | CSV5C | 135/129 | confirmed | legendary_bearing_1.webp 2026-08-01 | distinct from yveltal-01, checked in hand 2026-09-19 |
| zapdos-01 | Zapdos | サンダー | JP | Mystery of the Fossils | No.145 | uncertain | IMG_6847.HEIC 2026-08-01 | vintage Pokedex-number print, number corrected from No.143 (misread): Zapdos is Pokédex #145, matching owner's doubleholo export 2026-09-18 |
| zekrom-01 | Zekrom | Zekrom EX | EN | Black Bolt | 158/086 | confirmed | legendary_bearing_2.webp 2026-08-01 | Slash/Voltage Burst, checked in hand 2026-09-19 |
| zygarde-01 | Zygarde | ジガルデ | JP | Awakening Psychic King | 040/078 | confirmed | threshold_1.webp 2026-08-01 | Aura Break attack, U rarity mark |
