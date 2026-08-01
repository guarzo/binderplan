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
