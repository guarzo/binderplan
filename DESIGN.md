---
name: Pokémon Art Collection
description: A quiet exhibition of a personal card collection
colors:
  bg-deep: "oklch(0.16 0.018 285)"
  bg-primary: "oklch(0.19 0.02 285)"
  bg-raised: "oklch(0.235 0.022 285)"
  bg-hair: "oklch(0.30 0.02 285)"
  text-primary: "oklch(0.93 0.012 285)"
  text-muted: "oklch(0.70 0.02 285)"
  text-faint: "oklch(0.56 0.02 285)"
  accent: "oklch(0.78 0.13 300)"
  accent-soft: "oklch(0.70 0.09 300)"
  foil-violet: "oklch(0.72 0.15 300)"
  foil-cyan: "oklch(0.80 0.11 210)"
  foil-rose: "oklch(0.78 0.13 20)"
  border: "oklch(0.30 0.02 285)"
  border-faint: "oklch(0.26 0.018 285)"
  room-wall: "oklch(0.245 0.018 300)"
  room-warmth: "oklch(0.57 0.043 62)"
  room-wood: "oklch(0.34 0.035 58)"
  room-paper: "oklch(0.86 0.025 80)"
typography:
  display:
    fontFamily: "DM Serif Display, serif"
    fontSize: "clamp(2.6rem, 6vw, 4.4rem)"
    fontWeight: 400
    lineHeight: 1.12
    letterSpacing: "-0.01em"
  body:
    fontFamily: "Source Sans 3, -apple-system, BlinkMacSystemFont, Segoe UI, sans-serif"
    fontSize: "1rem"
    fontWeight: 400
    lineHeight: 1.7
  label:
    fontFamily: "Source Sans 3, sans-serif"
    fontSize: "0.72rem"
    fontWeight: 500
    letterSpacing: "0.22em"
spacing:
  binder-pocket-gap: "clamp(0.45rem, 1.2vw, 0.85rem)"
  binder-leaf-pad: "clamp(0.85rem, 2vw, 1.35rem)"
rounded:
  shelf-spine: "0.2rem"
  trade-image: "0.4rem"
  binder-arrow: "999px"
components:
  directory-entry:
    textColor: "{colors.text-primary}"
    padding: "1rem 0"
    typography: "{typography.body}"
  binder-arrow:
    backgroundColor: "oklch(0.93 0.018 285 / 0.96)"
    textColor: "oklch(0.16 0.035 285)"
    rounded: "{rounded.binder-arrow}"
    width: "2.75rem"
    height: "2.75rem"
  slab-trigger:
    backgroundColor: "oklch(0.205 0.018 285)"
    textColor: "{colors.text-primary}"
    padding: "clamp(0.75rem, 2vw, 1.5rem)"
  trade-evidence:
    textColor: "{colors.text-muted}"
  gallery-placard:
    textColor: "{colors.text-faint}"
    typography: "{typography.label}"
---

# Design System: Pokémon Art Collection

## 1. Overview

**Creative North Star: "A quiet exhibition under lamplight"**

The site is a personal, low-glare place to linger with art. The homepage frames actual collection cards on a dim wall and places volumes and collections on tactile shelves; the directory is a quieter finding aid. Both paths lead toward the artwork, never a dashboard of metrics. The published site and `PRODUCT.md` are the authority if this descriptive document drifts.

**Key Characteristics:** image-first; warm but restrained; navigable like a book; visibly distinct treatment for photographed slabs versus reconstructed binder leaves; factual provenance and physical uncertainty available without pretending a catalogue image is an in-hand check.

The main layout is not an identical grid of cards. Homepage frames, shelf spines, directory rows, two-leaf desktop spreads, single-leaf mobile pages, and whole-slab viewing have different purposes. Do not force slabs into pockets or fabricate physical locations for the Trainer PDF-order sequence or top-loaded Trade cards.

## 2. Colors

The code's canonical palette is **OKLCH** (`layouts/partials/head.html`, `assets/css/site-foundation.css`). The frontmatter uses those real values instead of approximate sRGB hex; a Stitch-only hex linter may warn, but the running CSS must remain the source of truth.

### Primary and neutral

- **Indigo-tinted ink:** `--bg-deep`, `--bg-primary`, `--bg-raised` build low-glare depth. `--bg-hair`, `--border`, and `--border-faint` divide without forming nested cards.
- **Gallery light:** `--text-primary` carries important prose; `--text-muted` handles secondary content. `--text-faint` is reserved for short labels and low-priority details, not primary instructions.
- **One luminous thread:** `--accent` marks links. `--foil-violet`, `--foil-cyan`, and `--foil-rose` provide sparse shimmer for focus, hover, and occasional rules; they are not a background for every component.
- **Lamplit physical details:** `--room-wall`, `--room-warmth`, `--room-wood`, and `--room-paper` belong to the homepage wall, shelves and watchlist, not the default inner page.

**The Artwork Leads Rule.** Keep color on navigation and framing subordinate to actual local card and slab images. Do not use the foil sweep as gradient text.

## 3. Typography

**Display:** `DM Serif Display` (serif fallback), regular weight. Existing `h1` uses `clamp(2.6rem, 6vw, 4.4rem)` at `1.12` line-height; gallery headers narrow this at mobile widths. The type evokes printed exhibition titles, not a price catalogue.

**Body:** `Source Sans 3` (system sans fallback) at `1rem`, `1.7` line-height. Long-form measures are capped by `--content-width: 680px` or around 65–70 characters. Directory titles use the serif; captions and controls stay in readable sans.

**Placard / eyebrow:** Source Sans 3, `0.72rem`, weight 500, `0.22em` letter-spacing, uppercase. This is for short labels only, never paragraphs. Reserve `--text-faint` for large enough, nonessential text.

**Printed names:** render Japanese in `--font-cjk-jp` (Noto Sans JP and platform fallbacks), Chinese in `--font-cjk-sc` (Noto Sans SC and platform fallbacks), with appropriate `lang`. Keep the English identity and the original printed script together where the card calls for it; do not force an English display face onto CJK glyphs. Fonts load via Google Fonts with system fallbacks (`layouts/partials/head.html`).

## 4. Elevation

Depth comes from dark tonal surfaces, lightly outlined page material, the physical shelf and frame, and the photographs themselves. Static controls generally do not float; the homepage frames and shelf spines use shadows to suggest physical objects. The slab wall shows the full case without decorative glare, and the binder holds pages rather than cards-on-cards.

### Shadow vocabulary

- **Framed card mat:** `0 1rem 1.6rem oklch(0.08 0.01 285 / 0.45)` in `assets/css/site-foundation.css`, only for the homepage art wall.
- **Binder side arrow:** `0 0.85rem 1.8rem -1.2rem oklch(0.04 0.02 285 / 0.95)` in `assets/css/binder.css`, to keep navigation clear beside a spread.
- **Slab photography:** no CSS shadow on the photograph in the dedicated slab gallery; the real photographed object is the material.

## 5. Components

### Navigation

The header is opaque ink, not default glass. Links have a readable hover, active state, and a 2.75rem mobile minimum height. The directory uses typographic rows with descriptions and an outbound arrow; shelf spines are the homepage's more tactile route map. Keyboard focus has a 3px `--foil-cyan` outline with offset. The skip link appears on focus.

### Binder leaves and controls

Desktop shows paired physical-sequence leaves; mobile shows one. Pocket grids reflect their actual manifest geometry (3×3 or Emolga 2×2). The arrow control is a 2.75rem circular light surface, clearly separate from card imagery; the current leaf is announced to assistive technology. The inspector is a temporary detailed view with Escape, previous/next, focus restoration, source attribution, image classification and placement context. Keep uncertain states in source records and inspector while checks remain unresolved, not as grounds to invent exact images.

### Holding Trade evidence

The five top-loaded cards are a digital grouping after photographed pages, not a new physical spread. Their availability is explicit and limited to those five. Each card's image evidence can be expanded inline, including the archived photograph, provider record where used, and review note. Do not imply a price, sale, or ownership transfer.

### Slab exhibition

Slab photographs use a dedicated two-column desktop wall and one-column mobile wall. Each full object opens an independent dialog with previous/next, an enlarge control, source photograph, keyboard support and a fallback description. The wanted Masaki references stay distinguishable from owned objects. Never replace the whole graded object with an unlabelled bare card scan.

### States and motion

Use `--ease-out-expo` and `--ease-out-quart` for small hover/position feedback, not bouncing or layout-property animation. Keep `prefers-reduced-motion` effective. Controls have default, hover, focus, disabled and missing-image treatments where applicable. Local reviewed media is required; no visitor-side third-party card-image fetches.

## 6. Do's and Don'ts

### Do:

- **Do** let the cards and whole slabs set the visual mood while chrome recedes.
- **Do** use manifest-backed physical order and distinguish owner-directed digital sequences from observed pocket placements in data and inspector.
- **Do** keep controls operable by keyboard and touch; check dark-background WCAG AA text contrast and multilingual glyphs at desktop and mobile widths.
- **Do** treat `PRODUCT.md` as the strategic brief, this file as a scan of real CSS, and `AGENTS.md` as the evidence and implementation rules.

### Don't:

- **Don't** use generic SaaS / dashboard chrome: dark-blue uniform cards or a sticky app header.
- **Don't** turn the site into TCG marketplaces (TCGPlayer, eBay): price tags, condition badges, buy buttons or listing-grid clutter. A handful of Trade cards does not change that rule.
- **Don't** mimic crypto / NFT galleries with neon-on-black, glossy 3D or hype energy.
- **Don't** make a corporate-minimal startup landing page: sterile white or stock-photo cleanliness.
- **Don't** use gradient text, glassmorphism as a default, invented grades, owner status inferred from a reference print, or catalogue matches presented as in-hand identity checks.
