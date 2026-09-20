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
- `static/images/` - Gallery images (binder spreads and slabs)
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

Binder spreads are organized by volume:
- Volume I: Add to `static/images/binder/volume-1/`, reference in `content/gallery/volume-1/_index.md`
- Volume II: Add to `static/images/binder/volume-2/`, reference in `content/gallery/volume-2/_index.md`

Slabs: Add to `static/images/slabs/`, reference in `content/gallery/slabs/_index.md`

Image markup pattern:
```html
<figure class="gallery-item">
  <img src="../../images/binder/volume-1/filename.png" alt="Description" loading="lazy">
  <figcaption>Caption</figcaption>
</figure>
```

## Deployment

Automatic via GitHub Actions on push to `main`. Deploys to GitHub Pages.
