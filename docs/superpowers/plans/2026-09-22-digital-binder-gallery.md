# Digital Binder Gallery Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Replace the photographed Volume I and Volume II galleries with a validated, locally hosted digital binder that preserves physical leaf parity and clearly distinguishes image fidelity from placement confidence.

**Architecture:** Markdown remains the identity source, YAML manifests own current leaf and pocket presentation, and a separate YAML map owns image provenance. Python tools generate Hugo-ready registry JSON, validate all cross-file invariants, and stage reviewed TCGdex assets; Hugo renders responsive local images into accessible binder leaves, while JavaScript manages leaf navigation and the card inspector.

**Tech Stack:** Hugo 0.154.5 extended, Go templates, vanilla CSS and JavaScript, Python 3 with pytest, PyYAML 6.0.3, and Pillow 12.1.1, TCGdex v2 HTTP API, GitHub Actions and GitHub Pages.

**Spec:** `docs/superpowers/specs/2026-09-22-digital-binder-design.md`

## Global Constraints

- `docs/card-registry.md` remains canonical for identity and gains no location field.
- `data/binders/*.yaml` owns intended placement and pocket-level physical confirmation state.
- Every card leaf has exactly nine ordered pockets; transition leaves have no pockets.
- Site-native transition leaves preserve the physical positions of removed contents, chapter-divider, and closing leaves.
- `exact` image mappings are forbidden for `confidence: uncertain` registry rows.
- Visitors never fetch card images from third-party APIs at runtime.
- The old photographed gallery stays public until both volumes and the pilot review pass.
- Slab and side-binder galleries remain unchanged.
- All image states and pending placements are communicated without relying on color alone.
- Existing registry tests and the Hugo production build must continue to pass after every task.

---

## Execution gate

Tasks 1-8 produce a complete local pilot and CI-enforced foundation. Execution must stop after Task 8 for curator approval. Tasks 9-11 perform the high-volume asset review and public cutover only after that gate passes. These parts remain one plan because the migration depends on the exact validator, manifest, and renderer contracts established by the pilot.

## File structure

### Python and data boundaries

- Create `requirements.txt`: pin the YAML parser used locally and in CI.
- Create `scripts/digital_binder.py`: pure parsing, generation, validation, transition, and TCGdex candidate functions. It performs no CLI prompting.
- Create `scripts/check-digital-binder.py`: thin CLI for generated-data writes/checks and full semantic validation.
- Create `scripts/manage-card-images.py`: candidate search, review-artifact generation, approval, and local download CLI.
- Create `scripts/test_digital_binder.py`: unit and integration tests for all Python behavior.
- Create `data/generated/card-registry.json`: committed deterministic projection of the Markdown registry.
- Create `data/binders/volume-1.yaml` and `data/binders/volume-2.yaml`: ordered leaves, pockets, and placement evidence.
- Create `data/card-images.yaml`: image provenance and review state keyed by registry ID.

### Presentation boundaries

- Create `layouts/partials/binder.html`: volume-level rendering and inspector markup.
- Create `layouts/partials/binder-leaf.html`: one card or transition leaf.
- Create `assets/css/binder.css`: binder-only responsive layout, statuses, and focus styles.
- Create `assets/js/binder.js`: navigation, hash state, responsive leaf/spread behavior, and dialog focus management.
- Modify `layouts/gallery/list.html`: select the binder renderer only when the page has a `binder` parameter.
- Modify `layouts/partials/head.html`: include the fingerprinted binder stylesheet only for binder pages.
- Modify `layouts/partials/footer.html`: include the fingerprinted binder script only for binder pages while retaining the existing photograph lightbox for unchanged galleries.
- Modify `content/gallery/volume-1/_index.md` and `content/gallery/volume-2/_index.md`: retain introductory copy, set the binder key, and remove old gallery markup only at final cutover.

### Evidence and operations

- Create `docs/evidence/2026-09-22/digital-binder-migration/README.md`: provenance and migration limits.
- Preserve the current published Volume I and II derivatives under `docs/evidence/2026-09-22/digital-binder-migration/published-gallery/`.
- Modify `docs/card-registry.md` and `docs/ledger.md`: document the post-migration ownership boundaries.
- Modify `.github/workflows/hugo.yml`: install Python requirements and run semantic and rendered-output checks around Hugo.

---

### Task 1: Registry projection and dependency setup

**Files:**
- Create: `requirements.txt`
- Create: `scripts/digital_binder.py`
- Create: `scripts/check-digital-binder.py`
- Create: `scripts/test_digital_binder.py`
- Create: `data/generated/card-registry.json`

**Interfaces:**
- Consumes: `docs/card-registry.md` through the existing `parse_registry(text) -> list[dict]` function in `scripts/check-registry.py`.
- Produces: `load_registry(path: Path) -> dict[str, dict]`, `render_registry_json(rows: dict[str, dict]) -> str`, and CLI modes `--write-generated` and `--check-generated`.

- [ ] **Step 1: Pin PyYAML and write failing registry-projection tests**

Create `requirements.txt`:

```text
PyYAML==6.0.3
Pillow==12.1.1
```

Start `scripts/test_digital_binder.py` with import loading that matches the existing hyphenated-script convention:

```python
import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "digital_binder", Path(__file__).parent / "digital_binder.py"
)
digital_binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digital_binder)


def test_registry_projection_is_sorted_and_stable(tmp_path):
    registry = tmp_path / "registry.md"
    registry.write_text(
        "# Card registry\n\n## Registry\n\n"
        "| id | species | card_name | language | set | number | confidence | first_seen | notes |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| zubat-01 | Zubat | Zubat | EN | Fossil | 57/62 | photo | page.webp 2026-08-01 | |\n"
        "| abra-01 | Abra | Abra | EN | Base Set | 43/102 | confirmed | page.webp 2026-08-01 | |\n",
        encoding="utf-8",
    )
    rows = digital_binder.load_registry(registry)
    rendered = digital_binder.render_registry_json(rows)
    assert list(json.loads(rendered)) == ["abra-01", "zubat-01"]
    assert rendered.endswith("\n")


def test_check_generated_reports_drift(tmp_path):
    generated = tmp_path / "card-registry.json"
    generated.write_text("{}\n", encoding="utf-8")
    assert digital_binder.generated_is_current(
        generated, '{"abra-01": {}}\n'
    ) is False
```

- [ ] **Step 2: Run the focused tests and confirm red state**

Run:

```bash
python3 -m pytest scripts/test_digital_binder.py -q
```

Expected: collection or test failures because `scripts/digital_binder.py` and its functions do not exist.

- [ ] **Step 3: Implement deterministic registry loading and projection**

In `scripts/digital_binder.py`, dynamically load `scripts/check-registry.py` through `load_registry_module()` using `importlib.util.spec_from_file_location`, reject its validation errors, key rows by permanent ID, and serialize only these public fields:

```python
def load_registry_module():
    path = Path(__file__).with_name("check-registry.py")
    spec = importlib.util.spec_from_file_location("check_registry", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


GENERATED_FIELDS = (
    "id", "species", "card_name", "language", "set", "number", "confidence"
)


def load_registry(path: Path) -> dict[str, dict]:
    rows = load_registry_module().parse_registry(path.read_text(encoding="utf-8"))
    errors = load_registry_module().validate(rows)
    if errors:
        raise ValueError("\n".join(errors))
    return {row["id"]: {key: row[key] for key in GENERATED_FIELDS} for row in rows}


def render_registry_json(rows: dict[str, dict]) -> str:
    ordered = {card_id: rows[card_id] for card_id in sorted(rows)}
    return json.dumps(ordered, ensure_ascii=False, indent=2) + "\n"


def generated_is_current(path: Path, expected: str) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == expected
```

Make `scripts/check-digital-binder.py` call a `main(argv=None) -> int` in the module. `--write-generated` writes atomically through a sibling `.tmp` file; `--check-generated` prints a drift error and exits 1 without writing.

- [ ] **Step 4: Generate the committed projection and run green tests**

Run:

```bash
python3 scripts/check-digital-binder.py --write-generated
python3 scripts/check-digital-binder.py --check-generated
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
```

Expected: generated JSON contains 175 keyed rows; both commands exit 0; 62 tests pass at minimum.

- [ ] **Step 5: Commit the registry projection**

```bash
git add requirements.txt scripts/digital_binder.py scripts/check-digital-binder.py \
  scripts/test_digital_binder.py data/generated/card-registry.json
git commit -m "Add digital binder registry projection"
```

---

### Task 2: Binder and image semantic validation

**Files:**
- Modify: `scripts/digital_binder.py`
- Modify: `scripts/check-digital-binder.py`
- Modify: `scripts/test_digital_binder.py`
- Create: `data/binders/volume-1.yaml`
- Create: `data/binders/volume-2.yaml`
- Create: `data/card-images.yaml`

**Interfaces:**
- Consumes: `load_registry(path) -> dict[str, dict]` from Task 1.
- Produces: `load_yaml(path: Path) -> dict`, `validate_project(root: Path, previous_ref: str | None = None) -> list[str]`, and CLI `--check`.

- [ ] **Step 1: Write failing tests for leaf and pocket invariants**

Add fixture helpers before the tests. `confirmed_pocket(card_id)` returns a position-1 pocket with confirmed placement and dated fixture evidence. `pending_pocket(card_id, observed_card_id=None, physical_state_unknown=False)` returns the same pocket with pending placement and only the requested physical-state field. `empty_pocket(position=1)` returns an explicit empty pocket. `project_fixture(tmp_path, pockets=None, transition_pockets=None, registry_confidence="confirmed", image_classification="missing", publication_status="draft", reviewed=True)` writes a minimal valid registry, generated JSON, both volume YAML files, image YAML, evidence file, and optional local image under `tmp_path`; each keyword changes only the named test condition and it returns `tmp_path`.

Then add tests with these assertions:

```python
def test_card_leaf_requires_nine_pockets(tmp_path):
    root = project_fixture(tmp_path, pockets=[confirmed_pocket("abra-01")])
    errors = digital_binder.validate_project(root)
    assert any("exactly 9 pockets" in error for error in errors)


def test_transition_leaf_rejects_pockets(tmp_path):
    root = project_fixture(tmp_path, transition_pockets=[empty_pocket()])
    errors = digital_binder.validate_project(root)
    assert any("transition leaf" in error and "pockets" in error for error in errors)


def test_pending_pocket_requires_observed_or_unknown(tmp_path):
    root = project_fixture(tmp_path, pockets=[pending_pocket("abra-01")])
    errors = digital_binder.validate_project(root)
    assert any("observed_card_id" in error and "physical_state_unknown" in error
               for error in errors)


def test_exact_image_rejects_uncertain_registry_identity(tmp_path):
    root = project_fixture(
        tmp_path,
        registry_confidence="uncertain",
        image_classification="exact",
    )
    errors = digital_binder.validate_project(root)
    assert any("exact" in error and "uncertain" in error for error in errors)


def test_published_volume_rejects_unreviewed_image(tmp_path):
    root = project_fixture(tmp_path, publication_status="published", reviewed=False)
    errors = digital_binder.validate_project(root)
    assert any("unreviewed" in error for error in errors)
```

Also cover unknown IDs, duplicate occupied placements, missing assets, proxy without note, missing classification without an empty asset path, invalid transition roles, noncontiguous physical leaf numbers, and a draft volume permitting unresolved image review.

- [ ] **Step 2: Run the focused tests and confirm failures**

```bash
python3 -m pytest scripts/test_digital_binder.py -q
```

Expected: new tests fail because YAML loading and semantic validation are absent.

- [ ] **Step 3: Implement the YAML contracts and validator**

Use these top-level shapes:

```yaml
# data/binders/volume-1.yaml
version: 1
volume_id: volume-1
publication_status: draft
leaves: []
```

```yaml
# data/card-images.yaml
version: 1
cards: {}
```

Implement validation as pure functions that append human-readable errors rather than exiting early. A card pocket shape is:

```yaml
position: 1
card_id: abra-01
placement:
  status: confirmed
  evidence:
    type: published-photo
    source: docs/evidence/2026-09-22/digital-binder-migration/published-gallery/volume-1/example.webp
    observed_on: 2026-08-01
```

A pending replacement uses exactly one of:

```yaml
observed_card_id: outgoing-card-01
```

or:

```yaml
physical_state_unknown: true
note: No earlier pocket observation exists.
```

Implement `publication_status: draft | published`. Draft volumes still enforce structure and IDs, but may have absent or `reviewed: false` image records. Published volumes enforce every image and review invariant from the spec.

- [ ] **Step 4: Add previous-state transition tests and implementation**

Test stable pocket identity by `(volume_id, physical_leaf, position)`. Add `confirmed_project(tmp_path, card_id) -> dict` and `pending_project(tmp_path, card_id, observed_card_id) -> dict` helpers that return already-loaded manifest dictionaries, then cover:

```python
def test_confirmed_to_pending_requires_last_observed_card(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    current = pending_project(tmp_path, card_id="kadabra-01",
                              observed_card_id="abra-01")
    assert digital_binder.validate_transition(previous, current) == []


def test_pending_to_confirmed_rejects_unrelated_card(tmp_path):
    previous = pending_project(tmp_path, card_id="kadabra-01",
                               observed_card_id="abra-01")
    current = confirmed_project(tmp_path, card_id="alakazam-01")
    errors = digital_binder.validate_transition(previous, current)
    assert any("pending card" in error for error in errors)
```

`validate_project(root, previous_ref)` loads prior manifests by passing the validated `previous_ref` argument to:

```python
subprocess.run(
    ["git", "show", f"{previous_ref}:data/binders/volume-1.yaml"],
    check=True,
    capture_output=True,
    text=True,
)
```

Skip transition comparison when the ref does not contain binder manifests, but never skip current structural validation.

- [ ] **Step 5: Run all Python checks and commit**

```bash
python3 scripts/check-digital-binder.py --check
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
git add scripts/digital_binder.py scripts/check-digital-binder.py \
  scripts/test_digital_binder.py data/binders data/card-images.yaml
git commit -m "Validate digital binder manifests"
```

Expected: all tests pass; draft empty manifests pass structural validation.

---

### Task 3: Preserve evidence and seed physical leaf structure

**Files:**
- Create: `docs/evidence/2026-09-22/digital-binder-migration/README.md`
- Create: `docs/evidence/2026-09-22/digital-binder-migration/published-gallery/volume-1/*`
- Create: `docs/evidence/2026-09-22/digital-binder-migration/published-gallery/volume-2/*`
- Modify: `data/binders/volume-1.yaml`
- Modify: `data/binders/volume-2.yaml`
- Modify: `data/card-images.yaml`
- Modify: `scripts/test_digital_binder.py`

**Interfaces:**
- Consumes: manifest schema and validator from Task 2; `PAGE_ORDER` and `SWAP_INS` from `scripts/check-registry.py` for page membership only.
- Produces: 30 ordered leaves, 19 card leaves, 171 unique occupied pockets, and explicit draft image records for all intended cards.

- [ ] **Step 1: Copy the current published evidence before changing gallery behavior**

```bash
mkdir -p docs/evidence/2026-09-22/digital-binder-migration/published-gallery
a=docs/evidence/2026-09-22/digital-binder-migration/published-gallery
cp -a static/images/binder/volume-1 "$a/volume-1"
cp -a static/images/binder/volume-2 "$a/volume-2"
diff -qr static/images/binder/volume-1 "$a/volume-1"
diff -qr static/images/binder/volume-2 "$a/volume-2"
```

Write the README to state that these are the current published WebP derivatives, not the unavailable camera originals; name commit `2587c3d` as the source baseline; explain that they establish page composition and pocket order but do not independently prove every printing; and link `docs/evidence/2026-09-20/README.md` for later owner verification limits.

- [ ] **Step 2: Commit the verified evidence archive before manifests cite it**

```bash
git add docs/evidence/2026-09-22/digital-binder-migration
git commit -m "Preserve digital binder migration evidence"
```

This commit must precede every manifest commit so each cited evidence path resolves in its own checkout.

- [ ] **Step 3: Seed Volume I leaves in true physical order**

Record 19 leaves: volume opening, five chapter transitions, twelve card leaves, and a volume-closing transition. Use the current published pages to read pockets top-left to bottom-right. Apply the three verified Volume I swaps from `docs/ledger.md`; do not resurrect departed IDs.

For every card pocket, cite its archived page path and the observation date documented by the registry or evidence README. Transition leaves use native headings and short copy from the existing content page, not card imagery.

Transcribe card leaves in this exact order:

```text
v1-03 v1-04 v1-05 v1-07 v1-09 v1-10
v1-11 v1-12 v1-14 v1-15 v1-17 v1-18
```

After each card leaf, set `LEAF_ID` to that literal ID and run:

```bash
python3 scripts/check-digital-binder.py --check
git add data/binders/volume-1.yaml data/card-images.yaml
git commit -m "Seed ${LEAF_ID} digital binder page"
```

This per-page commit rule protects expensive visual transcription work.

- [ ] **Step 4: Seed Volume II leaves in true physical order**

Record 11 leaves: volume opening, three chapter transitions, and seven card leaves. Follow the corrected published filenames rather than the immutable pre-correction `first_seen` labels. Apply the verified Companions swap and filled Quiet Familiarity pocket from `docs/ledger.md`. Use `PAGE_ORDER` to reconcile membership and the archived page image to establish pocket position.

Transcribe card leaves in this exact order:

```text
v2-03 v2-04 v2-05 v2-06 v2-08 v2-09 v2-11
```

After each card leaf, set `LEAF_ID` to that literal ID and run:

```bash
python3 scripts/check-digital-binder.py --check
git add data/binders/volume-2.yaml data/card-images.yaml
git commit -m "Seed ${LEAF_ID} digital binder page"
```

- [ ] **Step 5: Add the final repository-data count test**

After both manifests are complete, add this regression test so every commit before it remains green:

```python
def test_seeded_repository_has_expected_leaf_and_card_counts():
    root = Path(__file__).parents[1]
    volumes = [
        digital_binder.load_yaml(root / "data/binders/volume-1.yaml"),
        digital_binder.load_yaml(root / "data/binders/volume-2.yaml"),
    ]
    leaves = [leaf for volume in volumes for leaf in volume["leaves"]]
    card_leaves = [leaf for leaf in leaves if leaf["kind"] == "cards"]
    occupied = [
        pocket for leaf in card_leaves for pocket in leaf["pockets"]
        if "card_id" in pocket
    ]
    assert len(leaves) == 30
    assert len(card_leaves) == 19
    assert len(occupied) == 171
    assert len({pocket["card_id"] for pocket in occupied}) == 171
```

Run final seed and provenance verification:

```bash
python3 -m pytest scripts/test_digital_binder.py \
  scripts/test_check_registry.py -q
python3 scripts/check-digital-binder.py --check
find docs/evidence/2026-09-22/digital-binder-migration/published-gallery \
  -type f | sort > /tmp/archived-binder-files.txt
git status --short
```

Expected: 30 leaves, 19 card leaves, 171 unique occupied cards, no manifest errors, and every current Volume I/II gallery file represented in the evidence inventory.

```bash
git add scripts/test_digital_binder.py
git commit -m "Lock digital binder seed counts"
```

---

### Task 4: TCGdex candidate and approval tooling

**Files:**
- Modify: `scripts/digital_binder.py`
- Create: `scripts/manage-card-images.py`
- Modify: `scripts/test_digital_binder.py`
- Create at runtime only: `tmp/digital-binder-review/`

**Interfaces:**
- Consumes: registry rows and `data/card-images.yaml`.
- Produces: `search_tcgdex(row: dict, opener=urlopen) -> list[dict]`, `rank_candidates(row, candidates) -> list[dict]`, `crop_evidence_photo(source: Path, box: tuple[int, int, int, int], target: Path)`, review HTML, and guarded `approve`, `approve-local`, `crop-evidence`, and `mark-missing` CLI operations.

- [ ] **Step 1: Write failing API-shape and ranking tests**

Use injected fake HTTP responses. Cover language mapping `EN -> en`, `JP -> ja`, `ZH -> zh-tw`; local-number normalization such as `156/086 -> 156`; missing upstream images; deterministic score ordering; and no automatic approval. Add Pillow-backed tests proving evidence crops reject out-of-bounds boxes and produce a WebP file, plus validation that an external photograph requires both `source_url` and `usage_basis`.

```python
def test_tcgdex_language_mapping_includes_traditional_chinese():
    assert digital_binder.TCGDEX_LANGUAGE == {
        "EN": "en", "JP": "ja", "ZH": "zh-tw"
    }


def test_candidate_without_image_remains_reviewable():
    candidate = digital_binder.normalize_tcgdex_candidate({
        "id": "SV11B-156",
        "localId": "156",
        "name": "タブンネ",
        "image": None,
        "set": {"id": "SV11B", "name": "ブラックボルト"},
    })
    assert candidate["image_url"] is None
    assert candidate["provider_id"] == "SV11B-156"


def test_ranker_does_not_mark_top_candidate_approved():
    registry = {
        "id": "audino-01", "card_name": "タブンネ", "language": "JP",
        "set": "sv11B", "number": "156/086", "confidence": "confirmed",
    }
    candidate = {
        "provider_id": "SV11B-156", "name": "タブンネ",
        "set_id": "SV11B", "local_id": "156", "image_url": None,
    }
    ranked = digital_binder.rank_candidates(registry, [candidate])
    assert ranked[0]["review_state"] == "candidate"
```

- [ ] **Step 2: Run tests and confirm red state**

```bash
python3 -m pytest scripts/test_digital_binder.py -q
```

- [ ] **Step 3: Implement candidate search and review output**

Use verified endpoints:

```text
GET https://api.tcgdex.net/v2/{language}/cards?name={urlencoded-card-name}
GET https://api.tcgdex.net/v2/{language}/cards/{provider-id}
```

When a detail record supplies an image base such as `https://assets.tcgdex.net/en/base/base1/4`, derive the review/download URL by appending `/high.webp`. Set a descriptive User-Agent and a 20-second timeout. Cache raw JSON under `tmp/digital-binder-review/cache/`; do not commit it.

`review --page LEAF_ID` creates one HTML file showing the registry identity, confidence, candidate fields, and candidate image for each occupied pocket. `LEAF_ID` must resolve to an existing manifest leaf such as `v1-17`. The command also writes deterministic JSON containing candidate indexes and provider IDs so approval never depends on HTML scraping.

- [ ] **Step 4: Implement guarded approval and download operations**

The argparse subcommands are:

```text
review --page LEAF_ID
approve CARD_ID --candidate-index INDEX --classification exact|proxy [--note TEXT]
approve-local CARD_ID --file FILE --source-url URL --usage-basis TEXT --classification exact|proxy [--note TEXT]
crop-evidence CARD_ID --source FILE --box LEFT,TOP,RIGHT,BOTTOM --reviewed-on YYYY-MM-DD
mark-missing CARD_ID --note TEXT
```

The operations must:

1. Load cached candidate data for `approve`, a curator-supplied file for `approve-local`, or an archived evidence image for `crop-evidence`.
2. Refuse `exact` when registry confidence is `uncertain`.
3. Refuse `proxy` without a note.
4. Refuse `approve-local` without both an HTTP(S) source URL and a nonempty usage basis.
5. Restrict `crop-evidence` sources to `docs/evidence/`, validate the crop box against source dimensions, and encode the result as WebP with Pillow.
6. Download or write atomically to the Python path `root / "assets/images/cards" / f"{card_id}.webp"`.
7. Record provider, provider ID when available, original source URL or evidence path, usage basis when applicable, classification, review date, and note in `data/card-images.yaml`.
8. Run semantic validation before replacing the YAML file.

- [ ] **Step 5: Verify against the live API without approving anything**

```bash
python3 scripts/manage-card-images.py search audino-01
python3 scripts/manage-card-images.py search charizard-01
python3 scripts/manage-card-images.py search cubone-01
python3 -m pytest scripts/test_digital_binder.py -q
```

Expected: all three language routes return parseable candidate reports or an explicit no-candidate result; no tracked file changes during `search`.

- [ ] **Step 6: Commit acquisition tooling**

```bash
git add scripts/digital_binder.py scripts/manage-card-images.py \
  scripts/test_digital_binder.py
git commit -m "Add reviewed card image acquisition"
```

---

### Task 5: Review pilot image mappings

**Files:**
- Modify: `data/card-images.yaml`
- Create: `assets/images/cards/*.webp` for approved pilot assets
- Modify only when evidence resolves identity: `docs/card-registry.md`
- Regenerate when registry changes: `data/generated/card-registry.json`

**Interfaces:**
- Consumes: image-review CLI and Volume I leaf IDs from prior tasks.
- Produces: reviewed image states for the Elemental Solitude and Contemplation card leaves.

- [ ] **Step 1: Generate the pilot review artifact**

Use the manifest leaf IDs corresponding to physical leaves 17 and 18:

```bash
python3 scripts/manage-card-images.py review --page v1-17
python3 scripts/manage-card-images.py review --page v1-18
```

Confirm the artifact covers these current occupants:

```text
absol-01 ampharos-01 cyndaquil-02 darkrai-02 espeon-01 glaceon-01
houndoom-03 kyogre-01 latios-02
dragonite-01 dratini-01 joltik-03 latios-01 mewtwo-03 snivy-02
spheal-03 umbreon-02 victini-02
```

- [ ] **Step 2: Stop for curator approval of the contact sheet**

Present the local review artifact. Do not approve candidates, update registry confidence, or download assets until the curator explicitly accepts each exact or proxy choice. For no accepted source, record `missing`; for an existing-photo fallback, create a `photo-crop` only from the archived evidence copy and cite that path.

- [ ] **Step 3: Apply approved classifications and resolve identity atomically**

For each accepted candidate, run `approve` with the reviewed candidate index and classification. For `espeon-01`, `dragonite-01`, and `umbreon-02`, `exact` remains forbidden unless the review supplies enough evidence to correct the registry identity first. When that happens, make the registry edit, regenerate JSON, and approve in the same commit:

```bash
python3 scripts/check-digital-binder.py --write-generated
python3 scripts/check-digital-binder.py --check
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
git add docs/card-registry.md data/generated/card-registry.json \
  data/card-images.yaml assets/images/cards
git commit -m "Review pilot card image mappings"
```

- [ ] **Step 4: Verify the pilot mappings without requiring every volume asset**

```bash
python3 scripts/check-digital-binder.py --check
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
```

Expected: both draft volumes remain valid; all 18 pilot cards have a reviewed exact, photo-crop, proxy, or missing state.

---

### Task 6: Render binder leaves with Hugo image derivatives

**Files:**
- Create: `layouts/partials/binder.html`
- Create: `layouts/partials/binder-leaf.html`
- Modify: `layouts/gallery/list.html`
- Modify: `layouts/partials/head.html`
- Modify: `layouts/partials/footer.html`
- Create: `content/gallery/digital-binder-pilot/_index.md`
- Create: `assets/css/binder.css`
- Modify: `scripts/test_digital_binder.py`

**Interfaces:**
- Consumes: `index .Site.Data.binders .Params.binder`, `index .Site.Data "card-images"`, `index .Site.Data.generated "card-registry"`, and local `assets/images/cards/` resources.
- Produces: semantic `[data-binder]`, `[data-binder-leaf]`, `[data-pocket]`, and `<dialog data-card-inspector>` markup.

- [ ] **Step 1: Add a draft-only pilot page and a failing rendered-markup check**

Create `content/gallery/digital-binder-pilot/_index.md` so Hugo treats the pilot as a gallery section and selects `layouts/gallery/list.html`:

```yaml
---
title: "Digital Binder Pilot"
description: "Local review surface for the reconstructed binder"
draft: true
binder: "volume-1"
---
```

Add a test helper that runs `hugo --buildDrafts --destination` against pytest's `tmp_path / "public"` directory and asserts:

```python
assert 'data-binder="volume-1"' in html
assert 'data-binder-leaf="v1-17"' in html
assert 'data-pocket-position="1"' in html
assert '<dialog' in html
assert 'https://assets.tcgdex.net' not in html
```

- [ ] **Step 2: Run the rendered check and confirm failure**

```bash
python3 -m pytest scripts/test_digital_binder.py -k rendered -q
```

Expected: failure because the gallery template still renders only Markdown content.

- [ ] **Step 3: Implement conditional gallery rendering**

In `layouts/gallery/list.html`, preserve current behavior for every page without `.Params.binder`:

```go-html-template
{{ if .Params.binder }}
  {{ partial "binder.html" . }}
{{ else }}
  <div class="gallery-content">{{ .Content }}</div>
{{ end }}
```

`binder.html` resolves the selected data file, pairs consecutive leaves into spread containers, renders stable anchors such as `id="leaf-v1-17"`, and includes one `<dialog>` inspector after the binder. Pass `eager: true` only to the first two leaves; every later leaf receives `eager: false`. Missing volume data must call `errorf` so Hugo fails loudly.

- [ ] **Step 4: Implement card and transition leaf templates**

`binder-leaf.html` switches on `kind`:

```go-html-template
{{ if eq .leaf.kind "transition" }}
  <section class="binder-leaf binder-transition" data-binder-leaf="{{ .leaf.id }}">
    <p class="binder-transition-role">{{ .leaf.role }}</p>
    <h2>{{ .leaf.heading }}</h2>
    {{ with .leaf.copy }}<p>{{ . }}</p>{{ end }}
  </section>
{{ else if eq .leaf.kind "cards" }}
  <section class="binder-leaf binder-card-leaf" data-binder-leaf="{{ .leaf.id }}" data-kind="cards">
    <header class="binder-leaf-label">
      <p>{{ .leaf.chapter }}</p>
      <h2>{{ .leaf.theme }}</h2>
    </header>
    <div class="binder-pockets">
      {{ range .leaf.pockets }}
        {{ if .empty }}
          <div class="binder-pocket is-empty" data-pocket data-pocket-position="{{ .position }}">
            <span>Empty pocket</span>
          </div>
        {{ else }}
          {{ $card := index $.cards .card_id }}
          {{ $mapping := index (index $.images "cards") .card_id }}
          <button class="binder-pocket" type="button" data-pocket
                  data-pocket-position="{{ .position }}"
                  data-card-id="{{ .card_id }}"
                  data-classification="{{ $mapping.classification }}"
                  data-placement-status="{{ .placement.status }}"
                  aria-label="Inspect {{ $card.card_name }}, {{ $.leaf.theme }} pocket {{ .position }}">
            {{ if eq $mapping.classification "missing" }}
              <span class="binder-missing">{{ $card.card_name }}<small>Image unavailable</small></span>
            {{ else }}
              {{ $source := resources.Get $mapping.asset }}
              {{ $thumb := $source.Resize "360x webp q80" }}
              {{ $large := $source.Resize "900x webp q84" }}
              <img src="{{ $thumb.RelPermalink }}" width="{{ $thumb.Width }}" height="{{ $thumb.Height }}"
                   alt="{{ $card.card_name }}, {{ $card.set }} {{ $card.number }}"
                   loading="{{ if $.eager }}eager{{ else }}lazy{{ end }}"
                   {{ if $.eager }}data-initial-binder-image{{ end }}
                   data-inspector-src="{{ $large.RelPermalink }}">
            {{ end }}
            {{ if eq $mapping.classification "proxy" }}<span class="pocket-state">Reference image</span>{{ end }}
            {{ if eq .placement.status "pending" }}<span class="pocket-state">Placement pending</span>{{ end }}
          </button>
        {{ end }}
      {{ end }}
    </div>
  </section>
{{ else }}
  {{ errorf "unknown binder leaf kind %q" .leaf.kind }}
{{ end }}
```

For reviewed local images, resolve `resources.Get`, create `360x webp q80` and `900x webp q84` derivatives, and place only thumbnail URLs in `src`/`srcset`. Put the 900-pixel URL in `data-inspector-src` so it is not requested before inspection. Missing images render the card name as an intentional empty-pocket state.

- [ ] **Step 5: Add binder-only CSS inclusion and initial structural styles**

In `head.html`, gate the fingerprinted resource on `.Params.binder`. Define leaf dimensions, three-by-three pockets, stable 5:7 card aspect ratios, transition typography, non-color status labels, and visible focus. Do not add page-turn animation.

Keep the old `.gallery-grid` and lightbox CSS because side binders and slabs still use it.

- [ ] **Step 6: Run draft build checks and commit rendering**

```bash
python3 -m pytest scripts/test_digital_binder.py -q
hugo --buildDrafts --gc --minify
hugo --gc --minify
git add layouts assets/css/binder.css scripts/test_digital_binder.py \
  content/gallery/digital-binder-pilot/_index.md
git commit -m "Render digital binder leaves"
```

Expected: pilot markup contains 19 Volume I leaves; production build still serves the unchanged photographed galleries because the pilot is draft and volume front matter is not switched.

---

### Task 7: Add responsive navigation and accessible card inspection

**Files:**
- Create: `assets/js/binder.js`
- Modify: `assets/css/binder.css`
- Modify: `layouts/partials/binder.html`
- Modify: `layouts/partials/binder-leaf.html`
- Modify: `layouts/partials/footer.html`

**Interfaces:**
- Consumes: stable leaf IDs and pocket data attributes from Task 6.
- Produces: direct leaf hashes, desktop spread navigation, mobile leaf navigation, and dialog focus restoration.

- [ ] **Step 1: Define the DOM contract in the templates**

Add:

```html
<nav class="binder-controls" aria-label="Binder pages">
  <a data-binder-prev href="#">Previous</a>
  <p data-binder-position aria-live="polite"></p>
  <a data-binder-next href="#">Next</a>
</nav>
```

Each pocket button carries card metadata in `data-*` attributes, including image classification, placement status, source attribution, and inspector image URL. The dialog contains named fields rather than receiving unsanitized HTML.

- [ ] **Step 2: Implement navigation state and direct links**

In `binder.js`, expose a small initializer:

```javascript
function initBinder(root) {
  const leaves = Array.from(root.querySelectorAll('[data-binder-leaf]'));
  const mobile = window.matchMedia('(max-width: 720px)');
  let index = indexFromHash(leaves, window.location.hash);
  render();
}
```

On desktop, normalize the selected index to its even spread start and show two leaves. On mobile, show one leaf. Previous/next moves by two desktop leaves or one mobile leaf. Update the URL with the visible leaf ID, preserve working `href` values without JavaScript, and recalculate when the media query changes.

ArrowLeft and ArrowRight operate only when focus is outside an input, link, button, or open dialog. Visible buttons remain the primary controls.

- [ ] **Step 3: Implement dialog focus and card navigation**

Use the native `<dialog>` element. On pocket activation:

1. Save the originating button.
2. Assign text with `textContent`.
3. Assign the reviewed local `data-inspector-src` to the dialog image.
4. Call `showModal()` and focus the close button.
5. Trap Tab and Shift+Tab within dialog controls.
6. Support Escape and adjacent-card buttons.
7. On close, clear the large image `src` and restore focus.

Do not inject manifest text through `innerHTML`.

- [ ] **Step 4: Finish responsive and reduced-motion styles**

At widths above 720 pixels, render the active two-leaf spread with a central spine. At 720 pixels and below, render one active leaf, keep the nine-card grid, and update the position copy to include the containing spread. Add `@media (prefers-reduced-motion: reduce)` rules that remove nonessential transitions.

Proxy and pending markers must include visible text. A legend renders only when the active spread contains a proxy, missing, photo-crop, or pending state.

- [ ] **Step 5: Exercise the pilot manually**

Run:

```bash
hugo server --buildDrafts --disableFastRender
```

Verify at desktop and mobile widths:

- Direct `#leaf-v1-17` loading
- Two leaves on desktop and one on mobile
- Theme labels on both card leaves
- A transition leaf retaining its physical position
- Previous/next links without JavaScript, then enhanced behavior with JavaScript
- Tab order, Escape, focus restoration, and adjacent-card navigation
- Reduced-motion mode
- Exact, proxy, photo-crop, missing, and pending labels represented in the pilot fixture data

Record the tested browser, viewport widths, and results in the implementation commit body.

- [ ] **Step 6: Run builds and commit interaction**

```bash
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
hugo --buildDrafts --gc --minify
hugo --gc --minify
git add assets/js/binder.js assets/css/binder.css layouts/partials
git commit -m "Add accessible binder navigation"
```

---

### Task 8: Add rendered-output checks and pass the pilot review gate

**Files:**
- Modify: `scripts/digital_binder.py`
- Modify: `scripts/check-digital-binder.py`
- Modify: `scripts/test_digital_binder.py`
- Modify: `.github/workflows/hugo.yml`

**Interfaces:**
- Consumes: built `public/` output and manifest expectations.
- Produces: CLI `--check-public PATH` and CI enforcement around Hugo.

- [ ] **Step 1: Write failing generated-output tests**

Create this fixture helper and tests:

```python
def write_html(root: Path, body: str) -> None:
    page = root / "gallery/volume-1/index.html"
    page.parent.mkdir(parents=True)
    page.write_text(body, encoding="utf-8")


def test_public_check_rejects_remote_card_image_url(tmp_path):
    write_html(tmp_path, '<img src="https://assets.tcgdex.net/en/base/base1/4/high.webp">')
    errors = digital_binder.validate_public_output(tmp_path)
    assert any("remote card image" in error for error in errors)


def test_public_check_requires_nine_pockets_per_card_leaf(tmp_path):
    write_html(tmp_path, '<section data-binder-leaf="v1-03" data-kind="cards"></section>')
    errors = digital_binder.validate_public_output(tmp_path)
    assert any("9 pockets" in error for error in errors)
```

Also test unique leaf IDs, alt text on local card images, direct-link anchors, dialog presence, navigation labels, transition leaves without pockets, lazy loading after the first spread, and an initial-spread image budget no greater than 1,572,864 bytes. The budget check resolves each `data-initial-binder-image` URL to its file under `public/` and sums unique files.

- [ ] **Step 2: Implement `validate_public_output(public_dir) -> list[str]`**

Use `html.parser.HTMLParser` from the standard library. Do not add a browser-testing dependency. `--check-public` exits 1 with all accumulated errors.

- [ ] **Step 3: Wire semantic checks before Hugo and output checks after Hugo**

In `.github/workflows/hugo.yml`, add before the build:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.14'

- name: Install validation dependencies
  run: python -m pip install -r requirements.txt

- name: Test and validate binder data
  env:
    DIGITAL_BINDER_PREVIOUS_REF: ${{ github.event.before }}
  run: |
    python -m pytest scripts/test_check_registry.py scripts/test_digital_binder.py -q
    python scripts/check-registry.py docs/card-registry.md
    python scripts/check-digital-binder.py --check
```

After Hugo builds and before artifact upload, add:

```yaml
- name: Validate rendered binder output
  run: python scripts/check-digital-binder.py --check-public public
```

`check-digital-binder.py` ignores an all-zero or absent previous ref but always performs current-state validation.

- [ ] **Step 4: Run the exact CI sequence locally**

```bash
python3 -m pip install -r requirements.txt
python3 -m pytest scripts/test_check_registry.py scripts/test_digital_binder.py -q
python3 scripts/check-registry.py docs/card-registry.md
python3 scripts/check-digital-binder.py --check
hugo --gc --minify --baseURL "https://collection.dpao.la/"
python3 scripts/check-digital-binder.py --check-public public
```

Production output must still contain no binder pages because the pilot remains draft; the output checker treats zero published binders as valid until a manifest becomes `published`.

- [ ] **Step 5: Commit checks and stop for pilot approval**

```bash
git add scripts/digital_binder.py scripts/check-digital-binder.py \
  scripts/test_digital_binder.py .github/workflows/hugo.yml
git commit -m "Validate rendered digital binder output"
```

Present the draft pilot to the curator. Do not begin full image acquisition or public cutover until the curator approves visual quality, transition parity, status language, keyboard behavior, and mobile behavior.

---

### Task 9: Complete Volume I image review

**Files:**
- Modify: `data/card-images.yaml`
- Create: `assets/images/cards/*.webp`
- Modify when identity is resolved: `docs/card-registry.md`
- Regenerate after registry edits: `data/generated/card-registry.json`

**Interfaces:**
- Consumes: approved pilot design and image tooling.
- Produces: reviewed image state for all 108 current Volume I occupants.

- [ ] **Step 1: Generate review artifacts by card leaf**

For each Volume I `kind: cards` leaf in physical order, run:

```bash
python3 scripts/manage-card-images.py review --page "$LEAF_ID"
```

Set `LEAF_ID` to the literal ID read from the manifest before each invocation. Skip the already approved pilot leaves. Present each contact sheet for curator approval before applying mappings.

- [ ] **Step 2: Apply the approved fallback hierarchy page by page**

Use exact scan, archived photo crop, sourced photograph, proxy, then missing. Never mark an uncertain registry row exact. For a newly resolved identity, update the registry, regenerate JSON, and include both with the mapping commit.

Process the remaining card leaves in this exact order:

```text
v1-03 v1-04 v1-05 v1-07 v1-09 v1-10 v1-11 v1-12 v1-14 v1-15
```

After each page, set `LEAF_ID` to that literal ID and run:

```bash
python3 scripts/check-digital-binder.py --write-generated
python3 scripts/check-digital-binder.py --check
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
git add docs/card-registry.md data/generated/card-registry.json \
  data/card-images.yaml assets/images/cards
git commit -m "Review ${LEAF_ID} card images"
```

- [ ] **Step 3: Mark Volume I publishable and validate**

Change only Volume I to `publication_status: published`, then run:

```bash
python3 scripts/check-digital-binder.py --check
hugo --buildDrafts --gc --minify
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
git add data/binders/volume-1.yaml
git commit -m "Complete Volume I digital assets"
```

Expected: all 108 Volume I card IDs have reviewed states; unresolved scans are explicit proxy, photo-crop, or missing records rather than validation exceptions.

---

### Task 10: Complete Volume II image review

**Files:**
- Modify: `data/card-images.yaml`
- Create: `assets/images/cards/*.webp`
- Modify when identity is resolved: `docs/card-registry.md`
- Regenerate after registry edits: `data/generated/card-registry.json`
- Modify: `data/binders/volume-2.yaml`

**Interfaces:**
- Consumes: approved pilot design and Volume I-complete shared image map.
- Produces: reviewed image state for all 63 current Volume II occupants.

- [ ] **Step 1: Generate and review each remaining Volume II card leaf**

```bash
python3 scripts/manage-card-images.py review --page "$LEAF_ID"
```

Proceed in physical order. Require curator approval for each contact sheet. Reuse a local image only when the registry proves it is the same printing; different physical cards retain separate registry mappings even when a future policy permits visually identical assets.

- [ ] **Step 2: Apply mappings and commit after each page**

Process card leaves in this exact order:

```text
v2-03 v2-04 v2-05 v2-06 v2-08 v2-09 v2-11
```

After each page, set `LEAF_ID` to that literal ID and run:

```bash
python3 scripts/check-digital-binder.py --write-generated
python3 scripts/check-digital-binder.py --check
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
git add docs/card-registry.md data/generated/card-registry.json \
  data/card-images.yaml assets/images/cards
git commit -m "Review ${LEAF_ID} card images"
```

- [ ] **Step 3: Mark Volume II publishable and validate both volumes**

Set `publication_status: published`, then run:

```bash
python3 scripts/check-digital-binder.py --check
hugo --buildDrafts --gc --minify
python3 -m pytest scripts/test_digital_binder.py scripts/test_check_registry.py -q
git add data/binders/volume-2.yaml
git commit -m "Complete Volume II digital assets"
```

Expected: 171 occupied manifest cards have reviewed image records and both volume manifests satisfy published-state validation.

---

### Task 11: Public cutover and operational documentation

**Files:**
- Modify: `content/gallery/volume-1/_index.md`
- Modify: `content/gallery/volume-2/_index.md`
- Delete: `content/gallery/digital-binder-pilot/_index.md`
- Delete after evidence verification: `static/images/binder/volume-1/*`
- Delete after evidence verification: `static/images/binder/volume-2/*`
- Modify: `docs/card-registry.md`
- Modify: `docs/ledger.md`
- Modify: `layouts/partials/footer.html` to add binder attribution without changing other gallery behavior

**Interfaces:**
- Consumes: two published manifests, complete image map, renderer, and CI checks.
- Produces: public `/gallery/volume-1/` and `/gallery/volume-2/` binder experiences with unchanged side galleries.

- [ ] **Step 1: Switch volume content to binder rendering**

Add to each volume front matter:

```yaml
binder: volume-1
```

or:

```yaml
binder: volume-2
```

Retain only the volume introduction in Markdown. Remove chapter headings, `gallery-grid`, photographed figures, and contents/divider/closing card markup because manifests and native transition leaves now own that sequence.

- [ ] **Step 2: Add public source attribution and fan-site notice**

On pages with `.Params.binder`, render concise footer copy stating that the collection is an unofficial fan project, Pokémon card artwork belongs to its respective rights holders, and card data/reference scans are sourced from TCGdex where the inspector identifies that provider. Keep source-specific URLs and classification in each card inspector rather than placing hundreds of links in the footer.

- [ ] **Step 3: Update location guidance without changing registry semantics**

In `docs/card-registry.md`, replace guidance that says current location is reconstructed only from `first_seen` and the ledger. State:

```text
The binder manifests answer intended current pocket placement and whether that
placement has been physically confirmed. `first_seen` remains immutable
provenance, and the ledger remains the history and reasoning for contested
moves, corrections, and releases.
```

Add the same ownership boundary to `docs/ledger.md`. Do not add location columns to the registry or routine uncontested moves to the ledger.

- [ ] **Step 4: Remove public photographed derivatives only after evidence comparison**

```bash
diff -qr static/images/binder/volume-1 \
  docs/evidence/2026-09-22/digital-binder-migration/published-gallery/volume-1 &&
diff -qr static/images/binder/volume-2 \
  docs/evidence/2026-09-22/digital-binder-migration/published-gallery/volume-2 &&
rm -rf static/images/binder/volume-1 static/images/binder/volume-2
```

Do not remove side-binder directories.

- [ ] **Step 5: Run full production verification**

```bash
python3 -m pytest scripts/test_check_registry.py scripts/test_digital_binder.py -q
python3 scripts/check-registry.py docs/card-registry.md
python3 scripts/check-digital-binder.py --check
hugo --gc --minify --baseURL "https://collection.dpao.la/"
python3 scripts/check-digital-binder.py --check-public public
git diff --check
```

Manually verify:

- `/gallery/volume-1/` and `/gallery/volume-2/`
- One transition/card spread and one card/card theme-change spread
- Mobile single-leaf sequence and spread position copy
- Direct leaf hashes
- Keyboard navigation, dialog focus, Escape, and focus restoration
- Proxy, missing, photo-crop, and pending placement states
- Unchanged slab and side-binder galleries
- Network panel shows no remote card-image requests
- Initial desktop image transfer remains at or below approximately 1.5 MB

- [ ] **Step 6: Inspect final scope and commit cutover**

```bash
git status --short
git diff --stat
git diff --check
git add content layouts docs data assets scripts requirements.txt .github/workflows/hugo.yml
git commit -m "Publish reconstructed digital binders"
```

The final diff must not include `tmp/`, `public/`, API caches, browser review artifacts, unrelated slab changes, or changes to `.claude/settings.local.json`.
