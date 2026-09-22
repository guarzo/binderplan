# Digital binder gallery design

**Date:** 2026-09-22

**Status:** Approved design

## Summary

Replace the photographed Volume I and Volume II gallery pages with a digital binder assembled from reviewed, locally stored card scans. The public gallery will preserve the physical leaf sequence as open two-page spreads on desktop and one leaf at a time on mobile.

The change removes the ongoing requirement to photograph the binder. It preserves collection truth by distinguishing exact scans, evidence-photo crops, reference images, missing images, and placements that have not been physically confirmed.

The first release covers Volumes I and II. Side binders can migrate in later projects. Slab galleries retain their existing photography because the slab, label, grade, and physical condition are part of the subject.

## Goals

- Make the gallery feel like browsing a physical binder rather than a masonry image grid.
- Eliminate new binder photography as a requirement for routine card additions and moves.
- Use consistent card imagery without overstating printing identity or physical placement.
- Preserve the registry's identity and provenance boundary.
- Keep the published site static, fast, accessible, and independent of third-party API uptime.
- Retain enough source evidence to audit the initial migration and any image fallback.

## Non-goals

- Replacing slab photography.
- Migrating the Emolga, stamped-card, or trainer-card binders in the first release.
- Turning the site into an inventory, pricing tool, marketplace, or collection-management application.
- Adding current location to `docs/card-registry.md`.
- Reproducing or simulating the physical contents, chapter-divider, or Volume I `Fin` cards. Site-native transition leaves preserve the physical page parity those binder leaves created.
- Automatically approving card-image matches.
- Fetching card images from a third party in a visitor's browser.

## Product truth model

The primary gallery represents the intended binder composition. It also exposes when that composition is not fully established as physical fact.

Two independent states must not be conflated:

1. **Image fidelity:** whether the displayed image is the exact printing, an evidence-photo crop, a proxy, or missing.
2. **Placement confidence:** whether the card's displayed pocket is physically confirmed or pending confirmation.

An exact image does not prove placement. A confirmed placement does not make a proxy image exact.

## Architecture and ownership boundaries

### Identity registry

`docs/card-registry.md` remains canonical for card identity, confidence, and immutable first-observation provenance. It gains no current-location field.

Permanent registry IDs are the join key across placement, image mapping, audit history, and rendered output.

### Binder placement manifests

Create one structured placement manifest per volume under `data/binders/`:

- `data/binders/volume-1.yaml`
- `data/binders/volume-2.yaml`

Each manifest contains ordered leaves with `kind: cards` or `kind: transition`. Every leaf records a stable identifier and physical leaf number.

A card leaf also records:

- Chapter name and order
- Theme name
- Theme-local page number when a theme spans multiple leaves
- Exactly nine ordered pocket entries
- Optional page-level curatorial caption

A transition leaf records its role (`volume-opening`, `chapter`, or `volume-closing`), native site heading, and optional short curatorial copy. It contains no pockets and does not depict or simulate a physical card. Transition leaves occupy the same sequence positions as the removed physical navigation leaves so later card pages retain their true left/right parity and facing relationships.

Each pocket on a card leaf stores either an explicit empty state or an intended `card_id` plus placement state:

- `status`: `confirmed` or `pending`
- `evidence`: evidence type, source reference, and observation date
- `observed_card_id`: required for a pending replacement when the last physically observed occupant is known
- `physical_state_unknown`: required and set to `true` for a pending placement when no previous occupant was established
- `note`: required when placement is pending and the evidence reference does not fully explain why

A confirmed pocket means the intended card has been physically observed in that position. A pending pocket means the public composition intentionally shows a move that has not been physically verified. Its `observed_card_id` preserves the last known physical occupant rather than silently erasing that fact. A pending pocket must contain exactly one of `observed_card_id` or `physical_state_unknown: true`.

Allowed placement transitions are:

1. **Propose a move:** replace `card_id` with the intended incoming card, set `status: pending`, retain the outgoing card as `observed_card_id`, and cite the decision or proposal.
2. **Confirm execution:** add dated observation evidence, set `status: confirmed`, and remove `observed_card_id`.
3. **Revert an unexecuted move:** restore `observed_card_id` as `card_id`, set `status: confirmed`, and cite the observation that established the reversion.
4. **Correct contradicted evidence:** make a new manifest change with a note and evidence reference. Never rewrite an evidence file to make the old state appear correct.

The manifest is the current authority for the intended public composition and its pocket-level physical confirmation state. It is a mutable snapshot, not historical evidence, and does not replace the ledger.

### Image mapping

Create `data/card-images.yaml`, keyed by registry ID. Each entry records:

- Local source asset path
- Upstream provider
- Upstream card identifier
- Original source URL
- Image classification: `exact`, `photo-crop`, `proxy`, or `missing`
- Human review state and review date
- Optional note describing a mismatch or fallback

An entry classified as `missing` has no asset path. A `proxy` must explain how it differs from the owned printing.

`exact` means the scan depicts the same printing, not merely the same artwork or species. It is valid only when the canonical registry contains enough established identity to distinguish that printing. A registry row with `confidence: uncertain` cannot receive an `exact` image mapping. If image review establishes previously missing or uncertain printing identity, the reviewer must update the registry and image mapping in the same commit. The registry confidence still follows its existing evidence semantics: image research does not claim an in-hand confirmation. Genuinely unnumbered printings require an explicit identity-basis note naming the distinguishing evidence.

### Generated card metadata

A small build helper parses `docs/card-registry.md` into generated Hugo data for card names, language, set, number, and identity confidence. Templates do not independently retype registry metadata.

Commit generated data at `data/generated/card-registry.json` so ordinary `hugo server` works without a preparatory command. The generator provides a `--check` mode that fails when the committed file differs from the registry. GitHub Actions runs that check before the Hugo production build.

### Validation and acquisition tooling

Add a Python tool responsible for:

- Parsing and validating the existing registry
- Loading binder and image manifests
- Confirming every referenced registry ID exists
- Requiring exactly nine pocket entries per card page
- Rejecting duplicate occupied placements unless explicitly supported by a future design
- Confirming referenced source assets exist
- Rejecting unreviewed public image mappings
- Rejecting `exact` mappings whose registry identity remains uncertain or insufficiently distinguishing
- Validating placement states, evidence fields, the pending-state `observed_card_id` or `physical_state_unknown` requirement, and allowed transitions against the previous committed manifest
- Producing a review queue for proxies, missing assets, uncertain identities, and pending placements
- Searching configured providers for candidate scans
- Downloading only human-approved images

This tooling should extend existing Python conventions rather than introduce a new application framework.

## Image acquisition and provenance

### Candidate matching

TCGdex is the initial candidate source because it supports multiple print languages, including English, Japanese, and Traditional Chinese. Provider support does not imply complete image coverage.

Candidate ranking may use:

- Language
- Set or set code
- Collector number
- Printed card name
- Species
- Known provider identifiers

The importer must show matched and conflicting fields. It must never approve a candidate solely because a query returned one result.

### Human review

The tool produces a contact sheet or local review page containing the registry record, candidate scan, source information, and proposed classification. Approval writes the provider mapping and permits download. Review actions must be deterministic and recoverable from versioned files.

### Fallback order

For the existing collection:

1. Approved exact stock scan
2. Crop from an archived binder photograph
3. Separately researched photograph with recorded provenance and usage basis
4. Clearly marked proxy printing
5. Identified empty pocket

For future additions, no new binder photograph is required. They enter at steps 1, 3, 4, or 5.

### Local assets

Approved images are downloaded into Hugo's `assets/` tree. Hugo creates responsive WebP derivatives for spread thumbnails and focused inspection. Visitors never depend on runtime calls to the image provider.

The image mapping retains provider attribution and the original URL. The site should carry an appropriate unofficial fan-site notice and source attribution. Open catalogue metadata does not transfer ownership of Pokémon card artwork.

### Existing binder photographs

Before the public gallery stops using the current photographs:

- Preserve the relevant original files under a dated `docs/evidence/` directory.
- Keep archival originals separate from public derivatives.
- Record source filenames, provenance, verification limits, and their role in establishing pocket order.
- Retain the files as evidence for image matching and fallback crops.

Existing photographs are the authoritative source for seeding pocket order because the registry records pages but not positions within each page.

## Placement lifecycle and documentation compatibility

After migration, the sources answer different questions:

- `docs/card-registry.md`: what physical card is this, and what observation first established it?
- `data/binders/*.yaml`: where does the intended public composition place it, and has that exact pocket placement been physically confirmed?
- `docs/ledger.md`: why was a contested placement, correction, release, or theme decision made?
- `docs/evidence/`: what immutable observation supports a placement or identity claim?

A routine physical move updates the binder manifest even when it does not meet the ledger's threshold for a historical reasoning entry. A contested move, correction, or release updates the manifest and also appends the ledger entry required by existing policy. Image-only corrections update the registry when identity changes and the image mapping when presentation changes; they do not alter placement unless evidence also establishes a move.

Migration must update the usage guidance in `docs/card-registry.md` and `docs/ledger.md`. Those files currently describe reconstructing location from the photo baseline plus ledger history. Once the manifests launch, they must direct current-placement questions to the binder manifests while retaining `first_seen` and ledger history as provenance.

## Gallery experience

### Desktop spread

The primary desktop view shows two physical-sequence leaves facing one another. A card leaf contains a three-by-three pocket grid; a transition leaf uses native typography and whitespace. A restrained spine, page material, and transparent-pocket treatment provide physical context without imitating photographic glare.

Previous and next controls advance one spread at a time. Left and right arrow keys provide equivalent navigation. A stable URL fragment or query state permits direct links to a spread.

Physical leaf order wins over theme grouping. A one-page theme may face a transition leaf or the first card leaf of the next theme, according to the actual sequence.

### Theme and chapter labels

Each leaf receives an independent label above the page containing:

- Chapter
- Theme
- Page number where useful

When the theme changes at the spine, the two labels make the transition explicit. Site-native transition leaves appear where removed physical navigation leaves are necessary to preserve page parity. They use typography and whitespace rather than fictional pockets, tabs, or simulated cards.

### Mobile presentation

Mobile shows one leaf at a time. Card leaves retain the legible nine-card grid; transition leaves present their native heading and short copy. The sequence preserves physical order and states the spread relationship, such as `Pages 8-9, viewing page 8`.

Visible previous and next controls are required. Swipe may supplement those controls but cannot replace them.

### Card inspection

Each occupied pocket is an accessible interactive control. Activating it opens a focused card-image viewer suitable for image inspection, containing:

- Larger card image
- Printed card name
- Language
- Set and collector number
- Theme and pocket location
- Image source and fidelity classification
- Physical placement status when relevant

An image-inspection overlay is appropriate because the focused image is a temporary enlargement of the selected gallery object. It must trap focus correctly, close with Escape, provide previous and next card navigation, and restore focus to the originating pocket.

### Status presentation

Normal exact and physically verified cards receive no visible badge.

- `photo-crop`: identified in the focused viewer
- `proxy`: receives a quiet `Reference image` marker on the pocket and a full explanation in the viewer
- `missing`: renders an intentional empty pocket naming the identified card
- pending physical placement: receives a small neutral marker and the viewer text `Placement pending confirmation`

A compact legend appears only when the current spread contains a nonstandard state.

## Accessibility

- Use semantic buttons for pockets and navigation controls.
- Give every card image useful alt text derived from verified registry metadata.
- Never encode image or placement state by color alone.
- Preserve visible focus treatment.
- Support keyboard navigation, Escape, and focus restoration.
- Respect `prefers-reduced-motion`.
- Do not require page-turn animation or swipe gestures.
- Maintain WCAG AA text contrast.
- Reserve the trading-card aspect ratio before image load to prevent layout shift.

## Performance

- Load only the initially visible spread eagerly.
- Lazy-load later spreads and focused-view assets.
- Generate separate responsive sizes for spread and inspection use.
- Use `srcset` and `sizes` so mobile does not download desktop inspection images.
- Target an initial desktop image transfer of approximately 1 to 1.5 MB or less, with a smaller mobile transfer.
- Keep card-source assets local so upstream latency and outages do not affect visitors.

## Failure behavior

Production validation fails for:

- Unknown registry IDs
- Unknown leaf kinds, invalid transition leaves, or card leaves without exactly nine pocket definitions
- Duplicate occupied placements
- Invalid placement states, missing placement evidence, or invalid state transitions
- Pending placements that define neither a last-observed occupant nor an explicit unknown physical state
- Missing local files for non-missing image records
- Unreviewed image mappings
- `exact` mappings whose registry identity is uncertain or insufficient
- Proxy records without an explanatory note
- Generated registry data that is out of date
- Public remote card-image URLs

A deliberately missing image is valid only when explicitly classified as `missing`. An upstream provider failure affects acquisition commands, not the published gallery or ordinary Hugo builds.

GitHub Actions must run the complete semantic validator before Hugo:

```text
python3 scripts/check-digital-binder.py --check
hugo --gc --minify --baseURL "https://collection.dpao.la/"
```

The validator's `--check` mode covers registry generation drift, placement and image manifests, local assets, review state, and all failure conditions above. Hugo must not be the first command capable of discovering invalid binder data.

## Migration and rollout

1. Preserve existing Volume I and II photographs under dated evidence storage.
2. Seed card-page and pocket order from those photographs, including dated placement evidence and any known post-photograph changes.
3. Update registry and ledger usage guidance to name the binder manifests as the current intended-placement and confirmation-state authority.
4. Populate initial candidate matches from the registry.
5. Review and approve image matches, updating uncertain registry identity in the same commit whenever review establishes an exact printing.
6. Seed site-native transition leaves at the physical positions of removed contents, chapter-divider, and closing leaves.
7. Implement one representative pilot spread whose two leaves demonstrate a transition or theme change while preserving physical parity.
8. Review desktop presentation, mobile presentation, accessibility, source status, and visual quality.
9. Complete Volume I.
10. Complete Volume II.
11. Replace the photographed public gallery only after both volumes pass review.
12. Remove no evidence files as part of the public replacement.
13. Treat each side-binder migration as a later scoped project.
14. Leave slab galleries unchanged.

The old public experience remains available until the reconstructed volumes are complete, so migration is reversible and does not expose a partially matched binder.

## Verification

### Automated

- Unit tests for registry parsing, placement validation, image mappings, and candidate ranking
- Fixtures for exact images, photo crops, proxies, missing images, duplicate placements, and unknown IDs
- Existing registry test suite
- Production Hugo build
- Generated-output checks for valid leaf sequence and parity, nine pockets per card leaf, alt text, unique controls, navigation metadata, and absence of unintended remote image requests

### Manual

- Desktop two-page spread
- Mobile one-page presentation
- Theme change across the spine
- Direct spread link
- Keyboard-only navigation
- Screen-reader naming
- Focus trapping and restoration
- Reduced-motion behavior
- Exact, photo-crop, proxy, missing, and pending-placement states
- Initial image-transfer budget

## Success criteria

- Adding or moving a card requires structured-data and approved-image changes, not a new binder photograph.
- Visitors experience the collection as a sequence of binder spreads.
- Every displayed image has explicit provenance and review status.
- A proxy or intended placement is never presented as verified physical fact.
- The identity registry remains location-free.
- The site remains static, fast, keyboard accessible, and deployable through the existing GitHub Pages workflow.
