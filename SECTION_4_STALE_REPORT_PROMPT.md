# Handoff — correct the stale bug report in section 4

**Run this after the by-page worklist branch (`worktree-by-page-worklist`) merges.** Step 4
depends on the section-4 carry-forward, which does not exist on `main` yet.

## The ask

Section 4 ("Gaps and known issues") of `docs/registry-confirmation.md` claims
`content/gallery/volume-2/_index.md:41` captions `enduring_presence_1.webp` as "Enduring
Presence spread 1", and calls this "a repository bug — filenames and captions under
`content/` misdescribe which page they show."

**That was true before the gallery refresh. It is not true now.** The `content/` files were
renamed and recaptioned correctly; only the registry's `first_seen` values still carry the old
names, deliberately, because `first_seen` is immutable provenance. The correction now lives in
`PAGE_ORDER` in `scripts/check-registry.py`.

So section 4 is describing a fixed bug as though it were open, and citing a line number that no
longer says what it claims. A future reader will go hunting for a defect that isn't there.

## Evidence this is already fixed

Gallery `quiet_familiarity_2.webp` alt text lists Umbreon, Ditto, Snorlax, Light Arcanine,
Erika's Dragonair, Celebi, Togepi, Mudkip, Cinccino — exactly the nine rows the registry sources
from `enduring_presence_1.webp`. The gallery is one page ahead of the registry's filenames, which
is precisely the off-by-one `PAGE_ORDER` encodes. Confirm this yourself rather than taking it on
faith; that is step 1.

## Steps

1. **Confirm the gallery is consistent.** For each V2 page image, compare the `alt` and
   `figcaption` in `content/gallery/volume-2/_index.md` against the registry rows whose
   `first_seen` maps to that page via `PAGE_ORDER`. The mapping is off by one: gallery
   `quiet_familiarity_2.webp` ↔ registry `enduring_presence_1.webp`, gallery
   `enduring_presence_1.webp` ↔ registry `enduring_presence_2.webp`, gallery `threshold_1.webp`
   ↔ registry `IMG_6865.HEIC`. Expect all seven to line up.

2. **Resolve one real discrepancy.** Gallery `enduring_presence_1.webp` alt text lists
   **Pikachu**; the corresponding registry rows list **Joltik** (`joltik-01`). Eight of nine
   agree. Look at the image and fix whichever side is wrong. If it is the registry, that is a
   `species`/`card_name` correction and is permitted — the never-rewrite rule freezes IDs, not
   species. See `docs/superpowers/specs/2026-08-01-card-registry-design.md`.

3. **Rewrite section 4's narrative** to describe the resolved state: the misnaming is now
   confined to the registry's `first_seen`, where it is intentional, and the correction lives in
   `PAGE_ORDER`. Keep the explanation of *why* `first_seen` still carries the old names — that
   context is load-bearing for the next reader, and without it someone will "helpfully" rewrite
   the registry to match the filenames. Drop the "repository bug" framing and the stale
   `_index.md:41` citation.

4. **Round-trip it.** Section 4 is hand-written but now carried forward automatically by
   `--worklist`. Edit `docs/registry-confirmation.md` directly, then run:

   ```bash
   python3 scripts/check-registry.py docs/card-registry.md --worklist > /tmp/gen.md
   ```

   Confirm your edit survives into `/tmp/gen.md` and that nothing else changed.

## Verify

```bash
python3 -m pytest scripts/test_check_registry.py -q      # all pass
python3 scripts/check-registry.py docs/card-registry.md  # 175 rows, 0 ERROR
hugo --gc --minify --baseURL http://localhost/ --quiet
```

If step 2 changes a registry row, also re-check that every ledger ID citation still resolves:

```bash
for id in $(grep -oE '`[a-z0-9-]+-[0-9]{2}`' docs/ledger.md | tr -d '`' | sort -u); do
  grep -qE "^\| $id " docs/card-registry.md || echo "DANGLING $id"
done
```

## Note

Stage explicit paths, never `git add -A` — this repo has several worktrees with concurrent
writers, and one past commit was contaminated that way.
