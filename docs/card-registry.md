# Card registry

Stable identifiers for every card in Volumes 1 and 2.

This is not an inventory. It records what a card **is**, never where it sits. A card's ID is unchanged when it moves from one theme to another, unchanged when it goes to the holding box, and unchanged after release. To find where a card is now, grep `ledger.md` for its ID and read forward.

## How to use this file

**IDs are permanent.** `<species>-<NN>`, using the English Pokédex species name for cards of every language, plus a counter that means nothing. If an ID later proves inaccurate — the card is a Houndoom, not the Houndour its ID says — correct the `species` column and leave the `id` alone. A rewritten ID breaks every reference already written against it.

**The ID carries no qualifiers.** `Houndoom G Lv.45` is `houndoom-NN`; `ドダイトス Lv.X` is `torterra-NN`; `M Gengar EX` is `gengar-NN`. Printed names live in `card_name`.

**Two species on one card.** A card printing two species — a TAG TEAM, or similar — uses both names hyphen-joined in printed order: `gengar-mimikyu-01`. One physical card, one ID.

**When in doubt, split.** If you cannot tell whether a card is a new copy or one already listed, assign a new ID. Two IDs for one card is recoverable — note `superseded-by: <id>`. One ID for two cards is not.

**Reshoot provenance.** Rows whose `first_seen` names an `IMG_####.HEIC` file come from the 2026-08-01 whole-binder reshoot. Those originals are the owner's camera files and are not stored in this repository.

**Design note:** `superpowers/specs/2026-08-01-card-registry-design.md`.

**Validate with:** `python scripts/check-registry.py docs/card-registry.md`

## Registry

| id | species | card_name | language | set | number | confidence | first_seen | notes |
|---|---|---|---|---|---|---|---|---|
| absol-01 | Absol | Absol | EN | | XY178 | uncertain | elemental_solitude_1.webp 2026-08-01 | promo-style number, set code not textual |
| arcanine-01 | Arcanine | Light Arcanine | EN | Neo Destiny | 12/105 | photo | enduring_presence_1.webp 2026-08-01 | Light card, Drive Off ability, Gentle Flames attack |
| audino-01 | Audino | タブンネ | JP | sv1b | 156/086 | photo | calm_nature_1.webp 2026-08-01 | |
| beldum-01 | Beldum | Beldum | EN | | | uncertain | companions_1.webp 2026-08-01 | Steven's Beldum, Ram attack, number illegible after crop attempt |
| bewear-01 | Bewear | キテルグマ | JP | | | uncertain | intimidation_1.webp 2026-08-01 | number illegible after crop attempt |
| blastoise-01 | Blastoise | カメックス | JP | | No.009 | uncertain | enduring_presence_2.webp 2026-08-01 | Lv.52 HP100, vintage Pokedex-number print, era not identifiable |
| bulbasaur-01 | Bulbasaur | Bulbasaur | EN | | 45/100 | uncertain | calm_nature_1.webp 2026-08-01 | number legible, set name not printed on visible area |
| bulbasaur-02 | Bulbasaur | フシギダネ | JP | | No.001 | uncertain | joyful_action_1.webp 2026-08-01 | vintage Pokedex-number print, distinct from bulbasaur-01; era not identifiable |
| bulbasaur-03 | Bulbasaur | Bulbasaur | EN | | | uncertain | enduring_presence_2.webp 2026-08-01 | Sleep Seed ability, Vine Whip attack, distinct from bulbasaur-01/02, footer illegible after crop attempt |
| celebi-01 | Celebi | Celebi | EN | Neo Revelation | 16/64 | photo | enduring_presence_1.webp 2026-08-01 | Psychic Leaf attack |
| chansey-01 | Chansey | ラッキー | JP | | 113/101 | uncertain | world_people_1.webp 2026-08-01 | set code truncated/illegible |
| charizard-01 | Charizard | リザードンG | JP | | 007/016 | uncertain | on_attack_1.webp 2026-08-01 | Lv.X print, set code not textual, number read with low confidence |
| charizard-02 | Charizard | リザードン | JP | | | uncertain | companions_1.webp 2026-08-01 | Ability バトルセンス, キングブレイズ attack, distinct from charizard-01, number illegible after crop attempt |
| charmander-01 | Charmander | Charmander | EN | | | uncertain | world_people_1.webp 2026-08-01 | number illegible |
| charmander-02 | Charmander | Charmander | EN | | 023/185 | uncertain | joyful_action_1.webp 2026-08-01 | distinct printing from charmander-01, set code not textual |
| charmander-03 | Charmander | Charmander | EN | | | uncertain | quiet_familiarity_1.webp 2026-08-01 | Gnaw/Searing Flame attacks, distinct from charmander-01/02, footer obscured by sleeve tab |
| cubone-01 | Cubone | 卡拉卡拉 | ZH | | | uncertain | world_people_1.webp 2026-08-01 | number illegible |
| cyndaquil-01 | Cyndaquil | Cyndaquil | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | number illegible |
| cyndaquil-02 | Cyndaquil | Cyndaquil | EN | | 54/115 | uncertain | elemental_solitude_1.webp 2026-08-01 | distinct from cyndaquil-01, set code not textual |
| darkrai-01 | Darkrai | Darkrai EX | EN | | 37/122 | uncertain | awakened_power_1.webp 2026-08-01 | set code not textual |
| darkrai-02 | Darkrai | ダークライVSTAR | JP | | 228/172 | uncertain | elemental_solitude_1.webp 2026-08-01 | VSTAR, SAR rarity mark, distinct from darkrai-01, set code not textual |
| darkrai-03 | Darkrai | Darkrai | EN | | | uncertain | legendary_bearing_1.webp 2026-08-01 | Dark Cutter/Abyssal Sleep, distinct from darkrai-01/02, number illegible |
| dialga-01 | Dialga | ディアルガ | JP | | | uncertain | legendary_bearing_1.webp 2026-08-01 | Lv.69, No.483 dex entry, card number partially visible ("006/...") but remainder illegible, left blank rather than guessed |
| ditto-01 | Ditto | Ditto | EN | | XY40 | uncertain | enduring_presence_1.webp 2026-08-01 | Metamorphosis Gene ability, Stick On attack, promo number, set not readable as text |
| dragonair-01 | Dragonair | エリカのハクリュー | JP | | No.148 | uncertain | enduring_presence_1.webp 2026-08-01 | Erika's Dragonair, Lv.32, vintage Pokedex-number print, era not identifiable |
| dragonite-01 | Dragonite | カイリュー | JP | | No.149 | uncertain | contemplation_1.webp 2026-08-01 | Lv.45 print, vintage Pokedex-number print, era not identifiable |
| dragonite-02 | Dragonite | カイリューex | JP | | 038/054 | uncertain | legendary_bearing_2.webp 2026-08-01 | ex card, distinct from dragonite-01, set code not textual |
| dratini-01 | Dratini | Dratini | EN | | 33/62 | uncertain | contemplation_1.webp 2026-08-01 | set code not textual |
| dratini-02 | Dratini | Dratini | EN | | 26/102 | uncertain | quiet_familiarity_1.webp 2026-08-01 | Pound attack, Wizards era, distinct from dratini-01, set not readable as text |
| eevee-01 | Eevee | Eevee | EN | | | uncertain | at_rest_1.webp 2026-08-01 | number illegible |
| electrode-01 | Electrode | マルマイン | JP | sm1 | 037/095 | photo | companions_2.webp 2026-08-01 | |
| emolga-01 | Emolga | エモンガ | JP | sv11B | 174/086 | photo | joyful_action_1.webp 2026-08-01 | |
| entei-01 | Entei | 結晶塔のエンテイ | JP | | | uncertain | legendary_bearing_1.webp 2026-08-01 | No.244 dex entry, number illegible |
| espeon-01 | Espeon | わるいエーフィ | JP | | | uncertain | elemental_solitude_1.webp 2026-08-01 | Dark Espeon, vintage-style print, number illegible |
| espeon-02 | Espeon | 太阳伊布GX | ZH | | 195/151 | uncertain | legendary_bearing_2.webp 2026-08-01 | GX card, SSR rarity mark, distinct from espeon-01; 太阳伊布 is Espeon's Chinese localized name, set code not textual |
| flareon-01 | Flareon | Flareon EX | EN | Radiant Collection | RC28/RC32 | photo | companions_2.webp 2026-08-01 | |
| gardevoir-01 | Gardevoir | ザーナイトex | JP | | | uncertain | legendary_bearing_2.webp 2026-08-01 | ex card, Breakdown/Psycho Storm, number illegible after crop attempt |
| gardevoir-02 | Gardevoir | Gardevoir | EN | | | uncertain | companions_1.webp 2026-08-01 | Ability Shining Arcana, Prainwave attack, distinct from gardevoir-01, number illegible after crop attempt |
| gengar-01 | Gengar | 耿鬼VMAX | ZH | s6c | 072/172 | photo | awakened_power_2.webp 2026-08-01 | Single Strike era, distinct from gengar-mimikyu-01 TAG TEAM |
| gengar-02 | Gengar | ゲンガー | JP | | | uncertain | intimidation_1.webp 2026-08-01 | Lv.38 print, distinct from gengar-01 and gengar-mimikyu-01, number illegible |
| gengar-03 | Gengar | M Gengar EX | JP | | | uncertain | on_attack_1.webp 2026-08-01 | Mega Evolution EX, "ファントムゲート"/Phantom Gate, distinct from gengar-01/02 and gengar-mimikyu-01, number illegible |
| gengar-04 | Gengar | ゲンガー | JP | | | uncertain | companions_1.webp 2026-08-01 | Ability たくらみのうごう, スクリームサークル attack, distinct from gengar-01..03, number illegible after crop attempt |
| gengar-05 | Gengar | わるいゲンガー | JP | | | uncertain | enduring_presence_2.webp 2026-08-01 | Dark Gengar, HP70, distinct from gengar-01..04, footer illegible after crop attempt |
| gengar-mimikyu-01 | Gengar & Mimikyu | 耿鬼＆谜拟丘GX | ZH | | | uncertain | awakened_power_1.webp 2026-08-01 | TAG TEAM card featuring two species, printed name kept whole rather than split; number illegible |
| glaceon-01 | Glaceon | Glaceon | EN | | | uncertain | elemental_solitude_1.webp 2026-08-01 | Lv.46 print, number illegible after crop attempt |
| golem-01 | Golem | Golem EX | EN | | 189/165 | uncertain | awakened_power_2.webp 2026-08-01 | set code not textual |
| golem-02 | Golem | ゴローニャex | JP | | | uncertain | legendary_bearing_2.webp 2026-08-01 | ex card, distinct from golem-01, number illegible after crop attempt |
| greavard-01 | Greavard | Greavard | EN | sv1w | 274/190 | photo | world_people_1.webp 2026-08-01 | secret rare |
| grotle-01 | Grotle | ハヤシガメ | JP | A2 | 022/071 | photo | companions_1.webp 2026-08-01 | |
| groudon-01 | Groudon | Groudon | EN | | | uncertain | awakened_power_1.webp 2026-08-01 | number illegible |
| groudon-02 | Groudon | Groudon | EN | | 049/131 | uncertain | legendary_bearing_1.webp 2026-08-01 | Swelling Power/Magma Purge, distinct from groudon-01, set code not textual |
| groudon-03 | Groudon | Groudon | EN | | 84/100 | uncertain | enduring_presence_2.webp 2026-08-01 | Rock Smash/Break Ground attacks, AR rarity mark, set not readable as text |
| gyarados-01 | Gyarados | Dark Gyarados | EN | | | uncertain | awakened_power_1.webp 2026-08-01 | Team Rocket-era print with PRERELEASE stamp, number illegible |
| hoopa-01 | Hoopa | フーパ | JP | | | uncertain | threshold_1.webp 2026-08-01 | full-art secret rare, footer illegible after crop attempt |
| horsea-01 | Horsea | Horsea | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | e-card era border, number illegible |
| houndoom-01 | Houndoom | Houndoom | EN | | | uncertain | awakened_power_1.webp 2026-08-01 | Single Strike era print, number illegible |
| houndoom-02 | Houndoom | ヘルガー | JP | sv6a | 066/064 | photo | on_attack_1.webp 2026-08-01 | AR rarity, distinct from houndoom-01 |
| houndoom-03 | Houndoom | Houndoom | EN | | 8/64 | uncertain | elemental_solitude_1.webp 2026-08-01 | Dark Flame/Black Fang, Lv.35 #219 dex entry in flavor text, distinct from houndoom-01/02, set code not textual |
| houndoom-04 | Houndoom | Houndoom | EN | | 11/75 | uncertain | threshold_1.webp 2026-08-01 | Crunch/Flamethrower attacks, distinct from houndoom-01..03, set not readable as text |
| houndour-01 | Houndour | Houndour | EN | | 113/165 | uncertain | intimidation_1.webp 2026-08-01 | illustrator Mitsuhiro Arita credited, set code not textual |
| houndour-02 | Houndour | デルビル | JP | | | uncertain | companions_2.webp 2026-08-01 | distinct from houndour-01, number illegible after crop attempt |
| imposter-professor-oaks-revenge-01 | Imposter Professor Oak's Revenge | にせオーキドの逆襲 | JP | | | uncertain | companions_1.webp 2026-08-01 | Trainer card, vintage Team Rocket-era print, "R" rarity mark visible, number illegible |
| jirachi-01 | Jirachi | Jirachi | EN | | | uncertain | joyful_action_1.webp 2026-08-01 | number illegible |
| jirachi-02 | Jirachi | 基拉祈V | ZH | | | uncertain | awakened_power_1.webp 2026-08-01 | distinct printing from jirachi-01, number illegible |
| jirachi-03 | Jirachi | ジラーチex | JP | | 022/PLAY | uncertain | enduring_presence_2.webp 2026-08-01 | ex card, promo Play number, set not readable as text |
| joltik-01 | Joltik | 电电虫 | ZH | | | uncertain | companions_2.webp 2026-08-01 | holo print, number illegible after crop attempt |
| joltik-02 | Joltik | Joltik | EN | | 150/142 | uncertain | enduring_presence_2.webp 2026-08-01 | Jolting Charge attack, distinct from joltik-01, set not readable as text |
| kingdra-01 | Kingdra | キングドラ | JP | | No.230 | uncertain | on_attack_1.webp 2026-08-01 | Lv.47, vintage Pokedex-number print, illustrator Mitsuhiro Arita, era not identifiable |
| kyogre-01 | Kyogre | Kyogre ex | EN | | | uncertain | elemental_solitude_1.webp 2026-08-01 | number illegible, below visible border |
| latias-01 | Latias | Latias | EN | | 35/30 | uncertain | joyful_action_1.webp 2026-08-01 | secret rare numbering, set name not identifiable |
| latios-01 | Latios | ラティオス | JP | | 070/064 | uncertain | contemplation_1.webp 2026-08-01 | AR rarity, set code not textual |
| latios-02 | Latios | ラティオス | JP | | | uncertain | elemental_solitude_1.webp 2026-08-01 | distinct from latios-01, number illegible |
| latios-03 | Latios | Latios | EN | Dragon Vault | 10/20 | photo | legendary_bearing_1.webp 2026-08-01 | Sky Blade/Speed Wing, distinct from latios-01/02, "DRAGON VAULT" printed on card face |
| lucario-01 | Lucario | ルカリオVSTAR | JP | s12a | 226/172 | uncertain | intimidation_1.webp 2026-08-01 | VSTAR, SAR rarity mark; third digit of number ambiguous 5-vs-6 at source resolution |
| lugia-01 | Lugia | ルギア | JP | Neo Genesis | No.249 | uncertain | awakened_power_1.webp 2026-08-01 | vintage Pokedex-number print, era inferred from card style/border, not printed text |
| lugia-02 | Lugia | ルギアV | JP | s12 | 079/098 | photo | on_attack_1.webp 2026-08-01 | V card, distinct from lugia-01 |
| lugia-03 | Lugia | Lugia | EN | | 28/64 | uncertain | legendary_bearing_1.webp 2026-08-01 | Aerowing attack, No.249 dex entry, vintage print, distinct from lugia-01/02, era not identifiable |
| machop-01 | Machop | Machop | EN | | 086/136 | uncertain | threshold_1.webp 2026-08-01 | Punch attack, set not readable as text |
| marill-01 | Marill | Marill | EN | | 44/111 | uncertain | joyful_action_1.webp 2026-08-01 | vintage-style print, number legible, set name not shown |
| marowak-01 | Marowak | カラカラ | JP | | 067/072 | uncertain | at_rest_1.webp 2026-08-01 | vintage-style print, set name not identifiable |
| marowak-02 | Marowak | ガラガラ | JP | | | uncertain | intimidation_1.webp 2026-08-01 | delta species print, distinct from marowak-01, number illegible after crop attempt |
| master-ball-01 | Master Ball | マスターボール | JP | | | uncertain | threshold_1.webp 2026-08-01 | Trainer item card, no number field visible after crop attempt |
| mew-01 | Mew | Mew ex | EN | SVP | 053 | photo | world_people_1.webp 2026-08-01 | promo stamp |
| mew-02 | Mew | ミュウ | JP | s12a | 187/172 | photo | at_rest_1.webp 2026-08-01 | distinct printing from mew-01 |
| mew-03 | Mew | Mew GX | JP | | 137/165 | uncertain | legendary_bearing_2.webp 2026-08-01 | double-star SR rarity mark, distinct from mew-01/02, set code not textual |
| mew-04 | Mew | ミュウ | JP | | | uncertain | quiet_familiarity_1.webp 2026-08-01 | Pokepower type-change, Link Blast attack, distinct from mew-01..03, footer illegible after crop attempt |
| mew-05 | Mew | ミュウ | JP | | | uncertain | threshold_1.webp 2026-08-01 | Psywave/Recover-Beam attacks, distinct from mew-01..04, footer illegible after crop attempt |
| mewtwo-01 | Mewtwo | Mewtwo | EN | | | uncertain | awakened_power_2.webp 2026-08-01 | heavy holo glare, number illegible after crop attempt |
| mewtwo-02 | Mewtwo | Mewtwo EX | EN | | 164/162 | uncertain | intimidation_1.webp 2026-08-01 | Shatter Shot/Damage Change EX card, distinct from mewtwo-01, set code not textual |
| mewtwo-03 | Mewtwo | Mewtwo | EN | SVP | 052 | photo | contemplation_1.webp 2026-08-01 | Scarlet & Violet promo, Reflective Barrier/Psyslash, distinct from mewtwo-01/02 |
| mewtwo-04 | Mewtwo | Mewtwo | EN | | 12/113 | uncertain | legendary_bearing_1.webp 2026-08-01 | delta species, Delta Switch/Energy Burst, distinct from mewtwo-01/02/03, set code not textual |
| mimikyu-01 | Mimikyu | 谜拟丘 | ZH | | | uncertain | companions_1.webp 2026-08-01 | Ability 假扮 (Disguise), number illegible |
| misdreavus-01 | Misdreavus | ムウマ | JP | | | uncertain | intimidation_1.webp 2026-08-01 | number illegible |
| mudkip-01 | Mudkip | Mudkip | EN | | | uncertain | enduring_presence_1.webp 2026-08-01 | Nap/Waterfall attacks, number illegible after crop attempt |
| muk-01 | Muk | ベトベトン | JP | | No.089 | uncertain | enduring_presence_2.webp 2026-08-01 | Grimer evolution Lv.34, HP70, vintage Pokedex-number print, era not identifiable |
| ninetales-01 | Ninetales | キュウコン | JP | | No.038 | uncertain | legendary_bearing_2.webp 2026-08-01 | Lv.32, vintage Pokedex-number print, era not identifiable |
| ns-plan-01 | N's Plan | N's Plan | EN | | 163/086 | uncertain | legendary_bearing_2.webp 2026-08-01 | Supporter trainer, double-star SR rarity mark, set code not textual |
| numel-01 | Numel | Numel | EN | | 49/97 | uncertain | quiet_familiarity_1.webp 2026-08-01 | Firebreathing/Tackle attacks, e-Card era, set not readable as text |
| oshawott-01 | Oshawott | Oshawott | EN | | | uncertain | at_rest_1.webp 2026-08-01 | number illegible |
| pachirisu-01 | Pachirisu | バチュル | JP | | 117/086 | uncertain | contemplation_1.webp 2026-08-01 | AR rarity, set code not textual, number read with low confidence |
| palkia-01 | Palkia | Palkia | EN | Platinum | 26/106 | photo | awakened_power_2.webp 2026-08-01 | Lv.67, "PLATINUM" printed on card face |
| pikachu-01 | Pikachu | Pikachu | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | classic border, corner number illegible |
| pikachu-02 | Pikachu | Surfing Pikachu | EN | | 111/108 | uncertain | joyful_action_1.webp 2026-08-01 | vintage-style print, distinct from pikachu-01 |
| pikachu-03 | Pikachu | 皮卡丘 | ZH | | 153/150 | uncertain | companions_1.webp 2026-08-01 | CHR rarity mark, Ash-style artwork, set not readable as text |
| pikachu-04 | Pikachu | Pikachu | EN | Pokémon GO | 027/078 | photo | companions_2.webp 2026-08-01 | Buddy Bolt attack, distinct from pikachu-01/02/03 |
| pikachu-05 | Pikachu | Pikachu | EN | | 84/144 | uncertain | quiet_familiarity_1.webp 2026-08-01 | Max Voltage attack, e-Card era, distinct from pikachu-01..04, set not readable as text |
| piplup-01 | Piplup | Piplup | EN | | | uncertain | quiet_familiarity_1.webp 2026-08-01 | Lv.9, Peck/Water Splash attacks, footer illegible after crop attempt |
| plusle-01 | Plusle | プラスル | JP | | | uncertain | calm_nature_1.webp 2026-08-01 | |
| professor-elm-01 | Professor Elm | Professor Elm | EN | Neo Genesis | 94/111 | photo | companions_2.webp 2026-08-01 | |
| professors-research-01 | Professor's Research | 博士の研究 | JP | | 224/S-P | uncertain | companions_2.webp 2026-08-01 | Supporter trainer, promo S-P number, featuring Professor Willow, set not readable as text |
| quaxly-01 | Quaxly | Quaxly | EN | | | uncertain | world_people_1.webp 2026-08-01 | number illegible |
| ralts-01 | Ralts | ラルトス | JP | sv1S | 093/078 | photo | world_people_1.webp 2026-08-01 | AR rarity |
| rayquaza-01 | Rayquaza | Rayquaza | EN | | 138/185 | uncertain | awakened_power_2.webp 2026-08-01 | set code not textual |
| reshiram-01 | Reshiram | レシラム | JP | | 109/100 | uncertain | companions_1.webp 2026-08-01 | AR rarity mark, set not readable as text |
| reshiram-02 | Reshiram | Reshiram | EN | | 112/114 | uncertain | threshold_1.webp 2026-08-01 | Outrage/Blue Flare attacks, distinct from reshiram-01, set not readable as text |
| rockets-trap-01 | Rocket's Trap | ロケット団のワナ | JP | | | uncertain | companions_2.webp 2026-08-01 | Trainer card, vintage print, number illegible after crop attempt |
| sabrinas-gaze-01 | Sabrina's Gaze | ナツメの眼 | JP | | | uncertain | intimidation_1.webp 2026-08-01 | trainer card, number illegible |
| salamence-01 | Salamence | ボーマンダex | JP | | 119/100 | uncertain | awakened_power_2.webp 2026-08-01 | set code not textual |
| sandshrew-01 | Sandshrew | Sandshrew | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | small logo bottom-right, number illegible |
| sandshrew-02 | Sandshrew | Sandshrew | EN | | | uncertain | threshold_1.webp 2026-08-01 | Dig Under/Scratch attacks, distinct from sandshrew-01, footer illegible after crop attempt |
| scyther-01 | Scyther | ストライク | JP | | No.123 | uncertain | awakened_power_2.webp 2026-08-01 | vintage Pokedex-number print, era not identifiable |
| shaymin-01 | Shaymin | Shaymin EX | EN | XY | 148 | photo | at_rest_1.webp 2026-08-01 | XY Black Star Promo, artist Kouki Saito |
| shaymin-02 | Shaymin | シェイミLv.X | JP | | | uncertain | awakened_power_2.webp 2026-08-01 | distinct printing from shaymin-01, glare obscured number after crop attempt |
| shaymin-03 | Shaymin | Shaymin | EN | | 185/142 | uncertain | quiet_familiarity_1.webp 2026-08-01 | Ability Flower Curtain, Smash Kick attack, distinct from shaymin-01/02, set not readable as text |
| shaymin-04 | Shaymin | Shaymin | EN | | | uncertain | threshold_1.webp 2026-08-01 | Ability Celebration Wind, Energy Bloom attack, distinct from shaymin-01..03, footer illegible after crop attempt |
| slowpoke-01 | Slowpoke | ヤドン | JP | sv1V | 082/078 | photo | world_people_1.webp 2026-08-01 | AR rarity |
| snivy-01 | Snivy | Snivy | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | number illegible |
| snivy-02 | Snivy | ツタージャ | JP | | 037/078 | uncertain | contemplation_1.webp 2026-08-01 | distinct from snivy-01, set code not textual, number read with low confidence |
| snivy-03 | Snivy | Snivy | EN | | 6/113 | uncertain | quiet_familiarity_1.webp 2026-08-01 | Leaf Blade attack, distinct from snivy-01/02, set not readable as text |
| snorlax-01 | Snorlax | カビゴン | JP | | | uncertain | at_rest_1.webp 2026-08-01 | number illegible |
| snorlax-02 | Snorlax | カビゴンVMAX | JP | s1H | 046/060 | photo | on_attack_1.webp 2026-08-01 | VMAX, distinct from snorlax-01 |
| snorlax-03 | Snorlax | Snorlax | EN | | | uncertain | enduring_presence_1.webp 2026-08-01 | Rest Up ability, Collapse/Toss and Turn attacks, distinct from snorlax-01/02, number illegible after crop attempt |
| spheal-01 | Spheal | タマザラシ | JP | sv8 | 133/106 | photo | joyful_action_1.webp 2026-08-01 | AR rarity |
| spheal-02 | Spheal | タマザラシ | JP | | 016/086 | uncertain | on_attack_1.webp 2026-08-01 | Lv.18 print, distinct from spheal-01, set code not textual |
| spheal-03 | Spheal | Spheal | EN | | | uncertain | contemplation_1.webp 2026-08-01 | Lv.17 print, distinct from spheal-01/02, number illegible |
| sprigatito-01 | Sprigatito | Sprigatito | EN | | | uncertain | at_rest_1.webp 2026-08-01 | number illegible |
| squirtle-01 | Squirtle | Squirtle | EN | | 148/142 | uncertain | world_people_1.webp 2026-08-01 | set code ambiguous under magnification |
| squirtle-02 | Squirtle | Squirtle | EN | | | uncertain | quiet_familiarity_1.webp 2026-08-01 | Wave Splash/Doubleslap attacks, distinct from squirtle-01, footer illegible after crop attempt |
| steelix-01 | Steelix | ハガネール | JP | | No.205 | uncertain | enduring_presence_2.webp 2026-08-01 | vintage Pokedex-number print, era not identifiable |
| stufful-01 | Stufful | ヌイコグマ | JP | s10 | 073/067 | photo | at_rest_1.webp 2026-08-01 | |
| togedemaru-01 | Togedemaru | Togedemaru | EN | Cosmic Eclipse | 104/236 | photo | companions_2.webp 2026-08-01 | |
| togepi-01 | Togepi | トゲピー | JP | | | uncertain | enduring_presence_1.webp 2026-08-01 | number illegible after crop attempt |
| torterra-01 | Torterra | Torterra | EN | | 10/95 | uncertain | awakened_power_2.webp 2026-08-01 | set code not textual |
| typhlosion-01 | Typhlosion | バクフーン | JP | | No.157 | uncertain | intimidation_1.webp 2026-08-01 | vintage Pokedex-number print, era not identifiable |
| typhlosion-02 | Typhlosion | バクフーン | JP | | No.157 | uncertain | legendary_bearing_1.webp 2026-08-01 | Lv.46 print, distinct from typhlosion-01, vintage Pokedex-number print, era not identifiable |
| umbreon-01 | Umbreon | 月亮伊布VMAX | ZH | s6c | 053/032 | photo | awakened_power_1.webp 2026-08-01 | alt-art VMAX, art matches the well-known "Moonbreon" print; 月亮伊布 is Umbreon's Chinese localized name |
| umbreon-02 | Umbreon | ブラッキー | JP | | No.197 | uncertain | contemplation_1.webp 2026-08-01 | vintage Pokedex-number print, distinct from umbreon-01, era not identifiable |
| umbreon-03 | Umbreon | Umbreon | EN | | 61/108 | uncertain | elemental_solitude_1.webp 2026-08-01 | Confuse Ray/Shadow Shutdown, distinct from umbreon-01/02, set code not textual |
| umbreon-04 | Umbreon | Umbreon | EN | | 13/90 | uncertain | legendary_bearing_2.webp 2026-08-01 | Moonlight Fang/Quick Blow, RH holo mark, distinct from umbreon-01/02/03, set code not textual |
| umbreon-05 | Umbreon | ブラッキー | JP | | 062/080 | uncertain | enduring_presence_1.webp 2026-08-01 | distinct from umbreon-01..04, set not readable as text |
| ursaring-01 | Ursaring | Ursaring | EN | Radiant Collection | RC16/RC25 | photo | at_rest_1.webp 2026-08-01 | artist Sonosuke Sakuma |
| ursaring-02 | Ursaring | リングマ | JP | | No.217 | uncertain | on_attack_1.webp 2026-08-01 | Lv.43 print, distinct from ursaring-01, vintage Pokedex-number print, era not identifiable |
| victini-01 | Victini | Victini | EN | | | uncertain | joyful_action_1.webp 2026-08-01 | number illegible |
| victini-02 | Victini | Victini | EN | SVP | 208 | photo | contemplation_1.webp 2026-08-01 | Scarlet & Violet promo, V-Force attack, distinct from victini-01 |
| vulpix-01 | Vulpix | Vulpix | EN | | 119/147 | uncertain | enduring_presence_2.webp 2026-08-01 | Collect Fire attack, e-Card era stamp, number ambiguous (119 or 116)/147, set not readable as text |
| walrein-01 | Walrein | トドゼルガex | JP | | | uncertain | awakened_power_1.webp 2026-08-01 | number illegible |
| woobat-01 | Woobat | オンバット | JP | | | uncertain | calm_nature_1.webp 2026-08-01 | set/number code visible but digits ambiguous under magnification, left blank rather than guess |
| yveltal-01 | Yveltal | Yveltal EX | EN | | 79/146 | uncertain | on_attack_1.webp 2026-08-01 | set code not textual |
| yveltal-02 | Yveltal | 伊裴尔塔尔 | ZH | | | uncertain | legendary_bearing_1.webp 2026-08-01 | distinct from yveltal-01, number illegible |
| zekrom-01 | Zekrom | Zekrom EX | EN | | 158/046 | uncertain | legendary_bearing_2.webp 2026-08-01 | Slash/Voltage Burst, set code not textual |
| zygarde-01 | Zygarde | ジガルデ | JP | | 040/078U | uncertain | threshold_1.webp 2026-08-01 | Aura Break attack, set not readable as text |
| pikachu-06 | Pikachu | ピカチュウ | JP | SVP | 242 | photo | IMG_6842.HEIC 2026-08-01 | Pokémon Illustration Contest 2024 promo stamp |
| zapdos-01 | Zapdos | サンダー | JP | | No.143 | uncertain | IMG_6847.HEIC 2026-08-01 | vintage Pokedex-number print, era not identifiable |
| ampharos-01 | Ampharos | ミカンのデンリュウ | JP | | 021/141 | uncertain | IMG_6853.HEIC 2026-08-01 | Jasmine's Ampharos, VS-series print, set code not textual |
| kangaskhan-01 | Kangaskhan | ガルーラ | JP | | No.115 | uncertain | IMG_6858.HEIC 2026-08-01 | vintage Pokedex-number print, era not identifiable |
| cinccino-01 | Cinccino | チラチーノ | JP | | 083/071 AR | uncertain | IMG_6860.HEIC 2026-08-01 | AR rarity mark, third digit of number ambiguous under magnification, set code not textual |
