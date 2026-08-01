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
