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

**Vocabulary.** Destinations use names that already exist — Volume 1 and Volume 2 sub-themes, and the holding-box sections from `content/guides/holding-box.md`: EDGE, REDUNDANT, HERITAGE, FUTURE SELF, RELEASE. No parallel naming scheme.

**Card IDs.** Entries cite cards by registry ID from [`card-registry.md`](card-registry.md), written as `Umbreon (umbreon-02)` — species alongside the ID for readability, neither alone. Species names by themselves are ambiguous: Umbreon appears five times across the binder, Mewtwo four, Pikachu seven. A card with no ID gets one at the moment it is first cited here.

**Citations.** `§` references are to `CURATORIAL_AUDIT_PROMPT.md`.

**No backfill.** This ledger restarts 2026-08-01 with the adoption of card IDs. An earlier ledger covering the holding-box sort was superseded and removed; it survives in git at commit `a254855` if the reasoning is ever needed. Moves are not reconstructed from memory — doing so would put fiction into an audit trail.
