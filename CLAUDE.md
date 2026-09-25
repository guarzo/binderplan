# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Hugo static site for curating and displaying a Pokemon card collection as art. The site organizes cards by emotional/narrative themes rather than traditional sorting methods.

## Commands

```bash
# Local development server with hot reload
hugo server

# Build for production (outputs to /public)
hugo
```

Production builds use `hugo --gc --minify --baseURL <url>` via GitHub Actions.

## Architecture

**Hugo Static Site Generator** with:
- `content/` - Markdown content organized into philosophy, gallery, and guides sections
- `layouts/` - Go HTML templates (`_default/`, `partials/`, `gallery/`)
- `assets/images/cards/` - Reviewed per-card assets for the reconstructed Volume I/II and Stamped Cards binders
- `assets/images/holding/` - Holding photo-crop fallbacks and reviewed catalogue derivatives
- `static/images/` - Photo-based side-binder and slab gallery images
- `data/binders/` - Volume and Stamped Cards leaf order, pocket placement, and placement evidence
- `data/holding-binder.yaml` - Holding photographed pocket order and five separately top-loaded Trade cards
- `data/card-images.yaml` - Card-image fidelity and provenance metadata
- `hugo.toml` - Site configuration with menu structure

**Template Hierarchy:**
- `layouts/_default/baseof.html` - Base template wrapping all pages
- `layouts/_default/single.html` - Individual page template
- `layouts/_default/list.html` - Section index template
- `layouts/gallery/list.html` - Custom gallery layout
- `layouts/partials/` - Reusable components (head, header, footer with embedded CSS/JS)

**Content Types:**
- Markdown files with HTML embedded (enabled via `markup.goldmark.renderer.unsafe = true`)
- Gallery images referenced inline using `<figure class="gallery-item">` pattern

## Evidence Intake

- `tmp/` is a disposable upload inbox, not evidence storage. Before relying on an upload for ongoing work, preserve the relevant original under `docs/evidence/<receipt-date>/` in the working branch and verify the copy. Do not rely on session caches or ask the owner to restore files that should have been preserved.
- Keep source filenames and record provenance, verification limits, and any recovered renditions in an evidence README. Keep archival originals separate from optimized gallery derivatives in `static/images/`.
- Archive original inputs before replacing gallery images. Ignore incidental files such as `desktop.ini`.
- Catalogue exports and screenshot matches can contain proxy versions or errors. Preserve them as evidence, not automatically verified metadata. A check of character/number does not verify the set; a pictured placeholder does not establish ownership; a proposed move is not an executed move.

## Adding Gallery Images

For the reconstructed thematic binders:

- Put reviewed card assets at `assets/images/cards/<card_id>.webp` using `scripts/manage-card-images.py`.
- Record image fidelity and provenance in `data/card-images.yaml`.
- Record Volume I/II leaf and pocket placement in `data/binders/volume-1.yaml` or `data/binders/volume-2.yaml`; Stamped Cards uses `data/binders/stamped-cards.yaml`.
- Keep identity-only metadata in `docs/card-registry.md`; do not add pocket location there.
- Do not add photographed Volume I/II, Stamped Cards, or Holding spreads back to `static/images/binder/` or inline gallery markup in their `_index.md` files.

Holding uses `data/holding-binder.yaml` and reviewed local images, with its photo crops retained as reproducible fallbacks. Run `python scripts/holding_binder.py --check` after changes; only the five top-loaded Trade cards are actively available, and their digital page does not establish physical pockets. Stamped Cards uses reviewed local card assets and archived page-photo evidence, not public page photos. The remaining photo-based side binders use `static/images/binder/<gallery>/` and inline gallery markup. Slabs remain under `static/images/slabs/`.

Photo-gallery markup pattern:
```html
<figure class="gallery-item">
  <img src="../../images/binder/waifu/filename.jpg" alt="Description" loading="lazy">
  <figcaption>Caption</figcaption>
</figure>
```

## Deployment

Automatic via GitHub Actions on push to `main`. Deploys to GitHub Pages.
