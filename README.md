# Pokémon Art Collection

A personal exhibition of Pokémon cards as art, built with [Hugo](https://gohugo.io/). Start at [PRODUCT.md](PRODUCT.md) for the visitor experience, [DESIGN.md](DESIGN.md) for its visual system, and [AGENTS.md](AGENTS.md) for contributor rules and evidence handling.

## Develop and verify

```bash
hugo server
python -m pytest scripts -q
python scripts/check-registry.py docs/card-registry.md
python scripts/check-digital-binder.py --check
python scripts/holding_binder.py --check
python scripts/validation_checklist.py --check
python scripts/check-gallery.py
hugo --gc --minify --baseURL https://collection.dpao.la/
python scripts/check-digital-binder.py --check-public public
```

CI also builds with drafts and verifies rendered output. The site deploys through `.github/workflows/hugo.yml` after a push to `main`.

## Collection sources of truth

- `docs/card-registry.md` records stable card identity and confidence, **not** physical location. It is not a complete ownership inventory.
- `data/binders/*.yaml` records the physical leaves and evidence for Volumes I/II, Stamped Cards, Emolga Masterset, and the owner-directed *digital* Trainer Full Arts sequence. Trainer PDF order is not a claim about photographed pocket positions.
- `data/holding-binder.yaml` records 100 photographed Holding pockets plus five separately top-loaded, still-owned Trade cards. Only those five are explicitly available. Its observed IDs are not automatically registry IDs.
- `data/card-images.yaml` records the reviewed local image, fidelity class, and source for registered cards. Holding also records image provenance alongside its physical observations. A catalogue match does not prove an in-hand printing.
- `assets/images/cards/` and `assets/images/holding/` are public derivatives. Keep original photos and approved provider responses under dated `docs/evidence/` with provenance and checksums *before* making replacements.
- Five slab collections use `static/images/slabs/` and an independent image inspector; their pages live under `content/gallery/`, not `content/gallery/slabs/`.

Use `scripts/manage-card-images.py` for card-image review and approval. Do not add photographed spreads as inline markup to the reconstructed binder pages. For unresolved printings, non-exact images, and owner-directed digital placement, use the [owner validation checklist](docs/card-validation-checklist.md) or its [printable A4 PDF](docs/card-validation-checklist.pdf). It includes recorded English names and card numbers where known; missing numbers are not inferred from catalogue images. After reviewed records change, regenerate both with `python scripts/validation_checklist.py --write` followed by `python scripts/validation_checklist.py --pdf` (requires Pandoc and XeLaTeX). CI checks the Markdown and PDF source receipt. The [registry worklist](docs/registry-confirmation.md) serves a different purpose: physical checks for registry confidence and duplicate-printing candidates.
