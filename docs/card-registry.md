# Card registry

Stable identifiers for every card in Volumes 1 and 2.

This is not an inventory. It records what a card **is**, never where it sits. A card's ID is unchanged when it moves from one theme to another, unchanged when it goes to the holding box, and unchanged after release. To find where a card is now, grep `ledger.md` for its ID and read forward.

## How to use this file

**IDs are permanent.** `<species>-<NN>`, using the English Pokédex species name for cards of every language, plus a counter that means nothing. If an ID later proves inaccurate — the card is a Houndoom, not the Houndour its ID says — correct the `species` column and leave the `id` alone. A rewritten ID breaks every reference already written against it.

**The ID carries no qualifiers.** `Houndoom G Lv.45` is `houndoom-NN`; `ドダイトス Lv.X` is `torterra-NN`; `M Gengar EX` is `gengar-NN`. Printed names live in `card_name`.

**When in doubt, split.** If you cannot tell whether a card is a new copy or one already listed, assign a new ID. Two IDs for one card is recoverable — note `superseded-by: <id>`. One ID for two cards is not.

**Design note:** `superpowers/specs/2026-08-01-card-registry-design.md`.

**Validate with:** `python scripts/check-registry.py docs/card-registry.md`

## Registry

| id | species | card_name | language | set | number | confidence | first_seen | notes |
|---|---|---|---|---|---|---|---|---|
| sandshrew-01 | Sandshrew | Sandshrew | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 1; small logo bottom-right, number illegible |
| woobat-01 | Woobat | オンバット | JP | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 2; set/number code visible but digits ambiguous under magnification, left blank rather than guess |
| audino-01 | Audino | タブンネ | JP | sv1b | 156/086 | photo | calm_nature_1.webp 2026-08-01 | pocket 3 |
| horsea-01 | Horsea | Horsea | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 4; e-card era border, number illegible |
| bulbasaur-01 | Bulbasaur | Bulbasaur | EN | | 45/100 | uncertain | calm_nature_1.webp 2026-08-01 | pocket 5; number legible, set name not printed on visible area |
| plusle-01 | Plusle | プラスル | JP | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 6 |
| pikachu-01 | Pikachu | Pikachu | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 7; classic border, corner number illegible |
| snivy-01 | Snivy | Snivy | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 8; number illegible |
| cyndaquil-01 | Cyndaquil | Cyndaquil | EN | | | uncertain | calm_nature_1.webp 2026-08-01 | pocket 9; number illegible |
| mew-01 | Mew | Mew ex | EN | SVP | 053 | photo | world_people_1.webp 2026-08-01 | pocket 1; promo stamp |
| ralts-01 | Ralts | ラルトス | JP | sv1S | 093/078 | photo | world_people_1.webp 2026-08-01 | pocket 2; AR rarity |
| greavard-01 | Greavard | Greavard | EN | sv1w | 274/190 | photo | world_people_1.webp 2026-08-01 | pocket 3; secret rare |
| chansey-01 | Chansey | ラッキー | JP | | 113/101 | uncertain | world_people_1.webp 2026-08-01 | pocket 4; set code truncated/illegible |
| squirtle-01 | Squirtle | Squirtle | EN | | 148/142 | uncertain | world_people_1.webp 2026-08-01 | pocket 5; set code ambiguous under magnification |
| slowpoke-01 | Slowpoke | ヤドン | JP | sv1V | 082/078 | photo | world_people_1.webp 2026-08-01 | pocket 6; AR rarity |
| quaxly-01 | Quaxly | Quaxly | EN | | | uncertain | world_people_1.webp 2026-08-01 | pocket 7; number illegible |
| charmander-01 | Charmander | Charmander | EN | | | uncertain | world_people_1.webp 2026-08-01 | pocket 8; number illegible |
| cubone-01 | Cubone | 卡拉卡拉 | ZH | | | uncertain | world_people_1.webp 2026-08-01 | pocket 9; number illegible |
| mew-02 | Mew | ミュウ | JP | s12a | 187/172 | photo | at_rest_1.webp 2026-08-01 | pocket 1; distinct printing from mew-01 |
| stufful-01 | Stufful | ヌイコグマ | JP | s10 | 073/067 | photo | at_rest_1.webp 2026-08-01 | pocket 2 |
| shaymin-01 | Shaymin | Shaymin EX | EN | XY | 148 | photo | at_rest_1.webp 2026-08-01 | pocket 3; XY Black Star Promo, artist Kouki Saito |
| eevee-01 | Eevee | Eevee | EN | | | uncertain | at_rest_1.webp 2026-08-01 | pocket 4; number illegible |
| snorlax-01 | Snorlax | カビゴン | JP | | | uncertain | at_rest_1.webp 2026-08-01 | pocket 5; number illegible |
| ursaring-01 | Ursaring | Ursaring | EN | Radiant Collection | RC16/RC25 | photo | at_rest_1.webp 2026-08-01 | pocket 6; artist Sonosuke Sakuma |
| sprigatito-01 | Sprigatito | Sprigatito | EN | | | uncertain | at_rest_1.webp 2026-08-01 | pocket 7; number illegible |
| oshawott-01 | Oshawott | Oshawott | EN | | | uncertain | at_rest_1.webp 2026-08-01 | pocket 8; number illegible |
| marowak-01 | Marowak | カラカラ | JP | | 067/072 | uncertain | at_rest_1.webp 2026-08-01 | pocket 9; vintage-style print, set name not identifiable |
| emolga-01 | Emolga | エモンガ | JP | sv11B | 174/086 | photo | joyful_action_1.webp 2026-08-01 | pocket 1 |
| marill-01 | Marill | Marill | EN | | 44/111 | uncertain | joyful_action_1.webp 2026-08-01 | pocket 2; vintage-style print, number legible, set name not shown |
| bulbasaur-02 | Bulbasaur | フシギダネ | JP | | No.001 | uncertain | joyful_action_1.webp 2026-08-01 | pocket 3; vintage Pokedex-number print, distinct from bulbasaur-01; era not identifiable |
| jirachi-01 | Jirachi | Jirachi | EN | | | uncertain | joyful_action_1.webp 2026-08-01 | pocket 4; number illegible |
| charmander-02 | Charmander | Charmander | EN | | 023/185 | uncertain | joyful_action_1.webp 2026-08-01 | pocket 5; distinct printing from charmander-01, set code not textual |
| spheal-01 | Spheal | タマザラシ | JP | sv8 | 133/106 | photo | joyful_action_1.webp 2026-08-01 | pocket 6; AR rarity |
| victini-01 | Victini | Victini | EN | | | uncertain | joyful_action_1.webp 2026-08-01 | pocket 7; number illegible |
| pikachu-02 | Pikachu | Surfing Pikachu | EN | | 111/108 | uncertain | joyful_action_1.webp 2026-08-01 | pocket 8; vintage-style print, distinct from pikachu-01 |
| latias-01 | Latias | Latias | EN | | 35/30 | uncertain | joyful_action_1.webp 2026-08-01 | pocket 9; secret rare numbering, set name not identifiable |
| walrein-01 | Walrein | トドゼルガex | JP | | | uncertain | awakened_power_1.webp 2026-08-01 | pocket 1; number illegible |
| umbreon-01 | Umbreon | 月亮伊布VMAX | ZH | s6c | 053/032 | photo | awakened_power_1.webp 2026-08-01 | pocket 2; alt-art VMAX, art matches the well-known "Moonbreon" print; 月亮伊布 is Umbreon's Chinese localized name |
| lugia-01 | Lugia | ルギア | JP | Neo Genesis | No.249 | uncertain | awakened_power_1.webp 2026-08-01 | pocket 3; vintage Pokedex-number print, era inferred from card style/border, not printed text |
| houndoom-01 | Houndoom | Houndoom | EN | | | uncertain | awakened_power_1.webp 2026-08-01 | pocket 4; Single Strike era print, number illegible |
| gengar-mimikyu-01 | Gengar & Mimikyu | 耿鬼＆谜拟丘GX | ZH | | | uncertain | awakened_power_1.webp 2026-08-01 | pocket 5; TAG TEAM card featuring two species, printed name kept whole rather than split; number illegible |
| darkrai-01 | Darkrai | Darkrai EX | EN | | 37/122 | uncertain | awakened_power_1.webp 2026-08-01 | pocket 6; set code not textual |
| gyarados-01 | Gyarados | Dark Gyarados | EN | | | uncertain | awakened_power_1.webp 2026-08-01 | pocket 7; Team Rocket-era print with PRERELEASE stamp, number illegible |
| jirachi-02 | Jirachi | 基拉祈V | ZH | | | uncertain | awakened_power_1.webp 2026-08-01 | pocket 8; distinct printing from jirachi-01, number illegible |
| groudon-01 | Groudon | Groudon | EN | | | uncertain | awakened_power_1.webp 2026-08-01 | pocket 9; number illegible |
| gengar-01 | Gengar | 耿鬼VMAX | ZH | s6c | 072/172 | photo | awakened_power_2.webp 2026-08-01 | pocket 1; Single Strike era, distinct from gengar-mimikyu-01 TAG TEAM |
| torterra-01 | Torterra | Torterra | EN | | 10/95 | uncertain | awakened_power_2.webp 2026-08-01 | pocket 2; set code not textual |
| rayquaza-01 | Rayquaza | Rayquaza | EN | | 138/185 | uncertain | awakened_power_2.webp 2026-08-01 | pocket 3; set code not textual |
| scyther-01 | Scyther | ストライク | JP | | No.123 | uncertain | awakened_power_2.webp 2026-08-01 | pocket 4; vintage Pokedex-number print, era not identifiable |
| palkia-01 | Palkia | Palkia | EN | Platinum | 26/106 | photo | awakened_power_2.webp 2026-08-01 | pocket 5; Lv.67, "PLATINUM" printed on card face |
| mewtwo-01 | Mewtwo | Mewtwo | EN | | | uncertain | awakened_power_2.webp 2026-08-01 | pocket 6; heavy holo glare, number illegible after crop attempt |
| salamence-01 | Salamence | ボーマンダex | JP | | 119/100 | uncertain | awakened_power_2.webp 2026-08-01 | pocket 7; set code not textual |
| shaymin-02 | Shaymin | シェイミLv.X | JP | | | uncertain | awakened_power_2.webp 2026-08-01 | pocket 8; distinct printing from shaymin-01, glare obscured number after crop attempt |
| golem-01 | Golem | Golem EX | EN | | 189/165 | uncertain | awakened_power_2.webp 2026-08-01 | pocket 9; set code not textual |
