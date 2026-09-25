# Repository working agreement

## Purpose and stack

This is a Hugo static exhibition of a personal Pokémon card collection. Read `PRODUCT.md` for audience and truth rules and `DESIGN.md` for the shipped visual system. Preserve the image-first, quietly curatorial presentation; do not turn it into a marketplace or inventory database. GitHub Actions builds and deploys to Pages on `main`.

## Sources of truth

- `docs/card-registry.md`: stable card identity, printing fields, and `confirmed` / `photo` / `uncertain` confidence. It does **not** own placement or cover every Holding observation. The registry projection is `data/generated/card-registry.json`.
- `data/binders/volume-1.yaml`, `volume-2.yaml`, `stamped-cards.yaml`, `emolga-masterset.yaml`, and `waifu.yaml`: published leaf order and pocket placement. `waifu` is the stable route key for **Trainer Full Arts**, a PDF-order digital sequence with pending physical pocket claims, not a reconstruction of the old three photographed pages. Emolga has 2×2 pages with two unowned wanted-reference pockets. Do not assign provisional Stamped page-eight cards to physical pockets.
- `data/holding-binder.yaml`: photographed Holding pockets and five separately top-loaded still-owned Trade cards. Only those five are actively available; a digital Trade page does not imply a physical binder pocket, a sale, or a transfer of ownership. Check with `python scripts/holding_binder.py --check`.
- `data/card-images.yaml`: reviewed fidelity and source for registered-card images. `exact` means a visually reviewed printing match, **not** proof of an in-hand identity check. `photo-crop`, `proxy`, and `missing` stay honest until owner review. Holding has image metadata in its manifest. Visitor image requests must use local assets, not third-party image endpoints.
- `docs/ledger.md`: append-only reasoning and verified moves. `first_seen` in the registry is immutable historical provenance, not current location.

## Evidence intake

`tmp/` is disposable. Archive owner uploads unchanged under `docs/evidence/<receipt-date>/` before making derivatives, verify byte copies and checksums, and document source filenames, provenance, and limits in a README. Keep archival originals separate from `assets/images/cards/`, `assets/images/holding/`, and slab derivatives. Catalogue exports and screenshots can be erroneous proxies: artwork, name, or number alone does not verify set, stamp, edition, foil treatment, ownership, or an executed move. Ignore incidental files such as `desktop.ini`.

Use `scripts/manage-card-images.py` for reviewed card-image approvals and crop generation. DoubleHolo use is owner-authorized but live provider identity and the physical printing must still be reviewed. Do not fabricate in-hand confirmation. Keep recorded uncertainty available in the inspector/source records; `docs/card-validation-checklist.md` is the generated owner review queue, not evidence that a checkbox was completed. Two Emolga wanted cards are **not** owned.

## UI and content

- `layouts/partials/binder.html` and `binder-leaf.html` render reconstructed binders; `assets/css/binder.css` and `assets/js/binder.js` own their presentation and interaction. Preserve desktop spreads, mobile single-leaf reading, keyboard navigation, and physical order. Do not put photographed binder spreads back into public inline gallery markup.
- `layouts/gallery/holding.html` and `assets/css/holding.css` represent Holding, including Trade. Slabs use separate page styling, previews, and `assets/js/slab-inspector.js`; do not force them into binder pockets.
- `content/gallery/` owns visitor prose; `data/exhibition.yaml` owns the gallery directory entries. `static/images/slabs/` holds original slab images, and `static/images/slab-previews/` holds reproducible previews.
- Dated evidence, specs, plans, and sorting snapshots are historical records. Fix misleading *living* guidance (README, current worklists, public copy) rather than rewriting old receipts to match today.

## Local checks

```bash
hugo server
python -m pytest scripts -q
python scripts/check-registry.py docs/card-registry.md
python scripts/check-digital-binder.py --check-generated
python scripts/check-digital-binder.py --check
python scripts/holding_binder.py --check
python scripts/validation_checklist.py --check
python scripts/check-gallery.py
node --test scripts/test_binder_js_behavior.mjs
node scripts/test_slab_js_behavior.mjs
actionlint
```

CI runs strict draft and production Hugo builds followed by `python scripts/check-digital-binder.py --check-public <destination>`. Use a linked worktree for repository changes and protect unrelated primary-checkout files. Do not claim verification without running it.
