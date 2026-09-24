# Digital binder migration evidence — archived 2026-09-22

This directory preserves the Volume I and Volume II gallery images as the stable public-gallery evidence baseline for the digital binder migration, so that later manifest work can cite a page that will not move or be deleted underneath it.

The archive date is the date these copies were taken. It is not a photograph capture date.

## What these files are

Most files in `published-gallery/volume-1/` and `published-gallery/volume-2/` remain byte-for-byte copies of `static/images/binder/volume-1/` and `static/images/binder/volume-2/` as committed at `2587c3d` ("Preserve audit evidence and apply owner validation (#18)"), the last commit to touch those directories before this migration.

Five files are later final pre-cutover public derivatives refreshed from verified 2026-09-21 movements: `volume-1/legendary_bearing_2.webp`, `volume-1/on_attack_1.webp`, `volume-2/companions_2.webp`, `volume-2/quiet_familiarity_1.webp`, and `volume-2/threshold_1.webp`. Their camera originals are preserved under `docs/evidence/2026-09-21/after/`; this directory retains only the public WebP derivatives.

**These are the published WebP derivatives, not camera originals.** The originals from the 2026-08-01 reshoot are not available in this repository, and this archive does not recover them. The 2026-09-21 camera originals for the five refreshed pages are available in the 2026-09-21 evidence directory, not here. Every page in this archive is a resized, re-encoded WebP: the nine-pocket pages are 1125 × 1500, and `vol1_contents.webp` (736 × 1064) and `vol2_contents.webp` (498 × 723) are smaller still. Fine print — set symbols, collector numbers, copyright footers — is frequently unreadable at that resolution.

| Location | Files | Source / status |
|---|---:|---|
| `published-gallery/volume-1/` | 19 | Stable published Volume I gallery evidence. Seventeen files are byte-for-byte copies from `2587c3d`; `legendary_bearing_2.webp` and `on_attack_1.webp` are final pre-cutover public derivatives refreshed from verified 2026-09-21 movements. |
| `published-gallery/volume-2/` | 11 | Stable published Volume II gallery evidence. Eight files are byte-for-byte copies from `2587c3d`; `companions_2.webp`, `quiet_familiarity_1.webp`, and `threshold_1.webp` are final pre-cutover public derivatives refreshed from verified 2026-09-21 movements. |
| `SHA256SUMS` | 1 | Integrity hashes of all 30 archived files, relative to this directory. |

Verification performed at archive time: `diff -r` against each live directory reported no differences, and a `sha256sum` cross-check of all 30 files matched. After the five refreshed derivatives were merged, `SHA256SUMS` was regenerated for all 30 archived files. The GNU `cmp` utility has no `-r` option, so `diff -r` was used for the recursive byte comparison.

Incidental files such as `desktop.ini` are not present. These archived copies live outside Hugo's `content/` and `static/` trees: they are retained in the repository, not republished as gallery assets.

## What they do and do not establish

**They do establish page composition and pocket order.** Each nine-pocket page shows which cards sat on that leaf and where, top-left to bottom-right, when the page was shot. That is what the binder manifests under `data/binders/` cite them for, with `type: published-photo`.

**They do not independently prove every printing.** The resolution above is too low to read set symbols and collector numbers reliably on most cards, so these images cannot promote a registry row's `confidence`. Identity remains owned by `docs/card-registry.md` and its own evidence semantics; a pocket citation here is a placement observation, not an identity confirmation.

**They do not prove a card is still in that pocket today.** A photograph records a page at the moment of the shoot. Movement lives in [`docs/ledger.md`](../../../ledger.md), which must be consulted alongside any page cited here.

**Observation date.** Twenty-five archived derivatives preserve the 2026-08-01 public baseline. Five refreshed page derivatives — `volume-1/legendary_bearing_2.webp`, `volume-1/on_attack_1.webp`, `volume-2/companions_2.webp`, `volume-2/quiet_familiarity_1.webp`, and `volume-2/threshold_1.webp` — depict the verified 2026-09-21 after pages. Binder manifests should cite the source-specific observation date: 2026-08-01 for untouched baseline pages and 2026-09-21 for refreshed affected pages. Registry `first_seen` values remain historical provenance and are not rewritten to match later derivative refreshes.

## Known naming correction in Volume II

`scripts/check-registry.py` documents a systematic off-by-one in the pre-2026-08-01 Volume II filenames: the earlier shoot missed the Threshold page, so every page after `quiet_familiarity_1` was filed under the next page's name. The registry's `first_seen` column deliberately keeps those old names because it is immutable provenance.

**The files archived here use the corrected names.** They were renamed during the gallery refresh and match the page they actually depict. So a Volume II pocket citing `published-gallery/volume-2/quiet_familiarity_2.webp` is citing the page whose registry rows carry `first_seen: enduring_presence_1.webp`, and so on through `threshold_1.webp`. Do not "fix" the registry to match these names, and do not assume a registry `first_seen` filename resolves to the file of the same name in this archive.

## Related evidence

See [`docs/evidence/2026-09-20/README.md`](../../2026-09-20/README.md) for the September audit inputs, the owner's completed validation checklist, and the verification limits recorded there. That directory governed the collection state at that time: its "no moves" and "Review Holding First" rulings remain important context, while the seven later verified 2026-09-21 movements supersede them only for the listed swaps. The declined September comparisons remain non-moves.
