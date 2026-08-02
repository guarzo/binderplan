# Enduring Presence definition conflict — resolve when images are readable

**Status:** open. Blocked on being able to view the binder page images.

**Why this is waiting:** a 2026-08-02 evaluation could not read any file in
`static/images/binder/`. The Read tool returns empty for valid WebP files, and
the box has no `magick`/`convert`/`dwebp`/`ffmpeg`. PIL converts them fine, so
the files are good — the failure is in image ingestion. Every question below
needs the artwork, so nothing here should be decided from text alone.

---

## The conflict

`CURATORIAL_AUDIT_PROMPT.md` assigns the same phrase to two different themes:

- Line 102–103 — **Enduring Presence:** "complete, self-contained forces…
  power contained (not expressed), pose suggests continuity"
- Lines 72, 120, 122 — **Legendary Bearing:** "power contained, timeless
  presence… a complete, enduring force"

`content/philosophy/themes.md` — which is canonical, and which
`content/guides/volume-2-refinement.md` explicitly defers to — defines Enduring
Presence differently again, as **time witnessed**: ruins, weathering, artifacts,
a world shaped around the Pokemon.

This is not a small wording drift. The published Enduring Presence page 2,
captioned "Contained Power" ("force held rather than spent — sealed in a Master
Ball, ringed by Hoopa, or simply standing whole"), follows the §4 definition
faithfully. Whoever built that page was not making an error against the
document; they were following one half of a document that contradicts itself.

## The decision to make

**Which definition of Enduring Presence is canonical — time-witnessed, or
power-contained?**

`themes.md` is the stated authority, which makes §4 the stale text. But confirm
that against the actual page before editing, because the page is evidence about
what the collection has really been doing.

## What to do once you can see the images

1. **Look at `enduring_presence_2.webp`** — Machop (`machop-01`), Mew
   (`mew-05`), Zygarde (`zygarde-01`), Reshiram (`reshiram-02`), Hoopa
   (`hoopa-01`), Master Ball (`master-ball-01`), Sandshrew (`sandshrew-02`),
   Houndoom (`houndoom-04`), Shaymin (`shaymin-04`).

   Apply the tie-breaker now recorded in `themes.md` under Enduring Presence:
   strip every sign of age, memory, and history from each artwork. Does its
   meaning survive? A text-only pass judged that a Master Ball, Zygarde's aura
   and Hoopa's rings all survive intact — i.e. they sit on the **Legendary
   Bearing** side — but that pass could not see them and may be wrong.

2. **Decide the §4 question above.** Then make `CURATORIAL_AUDIT_PROMPT.md` §4
   and §5A agree with the ruling and with each other. They currently collide
   with one another as well as with `themes.md`.

3. **Then, and only then, consider card moves.** If `themes.md` wins, the
   time-signal-free cards on that page should leave. Note two constraints:
   Volume I is "structurally closed" per §2, so any Legendary Bearing placement
   needs a named evictee; and review-order step 4 of the refinement guide says
   to **hold pockets open** rather than force replacements. Holding is probably
   the right answer.

4. **Record the ruling in `docs/ledger.md`** — it is a contested call, which is
   exactly what that file is for. Nothing about this conflict is settled there
   yet; the 2026-08-02 pass confirmed the ledger does not address it.

## Also unresolved, same blocker

**Threshold could not be evaluated at all.** The planned three-row structure
(approach / cross / depart) is a spatial question that a flat card list cannot
answer. One concrete item: Kabuto (`kabuto-01`) is still on the page, and line
96 of the refinement guide says to move fossils out — though the gallery caption
argues for keeping it, "carried out of one age into another." That is a *time*
claim, which is Enduring Presence's axis, so this may resolve with the question
above.

**Confirm the registry off-by-one.** `docs/card-registry.md` now documents that
Volume II `first_seen` names are shifted by one page. One glance at
`quiet_familiarity_2.webp` settles it: nine cards including Cinccino and a
sleeping Snorlax means the documented mapping is right. If it shows something
else, that note needs correcting.

---

## Settled — do not re-litigate

**Quiet Familiarity was only re-photographed, never re-sorted** (owner
confirmed, 2026-08-02). The page-1 caption is byte-identical across the
2026-08-01 refresh, and `ledger.md` records only the Cinccino insert while
explicitly declining to record the other planned swaps: "planning is not
movement." So `content/guides/volume-2-refinement.md` is **outstanding work, not
stale documentation** — do not delete it as historical. The pull of
outdoor-portrait cards from Quiet Familiarity page 1 is still owed.

**"Contained Power" is not a new theme.** It fails §8 test #1 (distinct axis —
it is the Legendary Bearing axis) and #4 (solves a real classification problem —
Legendary Bearing already holds this). The open question is which existing theme
those cards belong to, not whether to create a theme for them.
