# Slab Gallery Reorganization Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Rebuild the graded-card gallery sections to match the current 36-card collection, under a two-tier Themes/Runs structure.

**Architecture:** This is a Hugo static content site — there is no application code and no unit-test framework. The equivalent of a test suite is a verification script that parses `content/**/*.md`, resolves every `<img src>` against `static/`, and enforces the one-card-one-section rule by requiring each slab image to be referenced exactly once. Task 1 builds that script and it fails until the content tasks are done; every subsequent task ends by re-running it. Images are added before old ones are removed, so the site is never in a broken state mid-plan.

**Tech Stack:** Hugo v0.154.5 extended, Python 3.14 (verification script + image staging), plain HTML embedded in Markdown (`markup.goldmark.renderer.unsafe = true`).

## Global Constraints

- Design doc: `docs/superpowers/specs/2026-08-01-slab-gallery-reorg-design.md`. It is approved. Do not re-litigate placements.
- Worktree `/home/tng/workspace/binderplan/.claude/worktrees/slabs-refresh`, branch `worktree-slabs-refresh`. Do not create another worktree.
- **Every card appears in exactly one section.** No cross-listing.
- Grid is 6 columns. `span-wide`=4, `span-narrow`=2, `span-half`=3, `span-full`=6. **Every row must sum to exactly 6.** The span sequences in this plan already satisfy this — do not reorder figures without recomputing.
- Figure markup is exactly:
  ```html
  <figure class="gallery-item span-X">
    <img src="../../images/slabs/FILE" alt="ALT" loading="lazy">
    <figcaption>CAPTION</figcaption>
  </figure>
  ```
- Every gallery `_index.md` ends with the lightbox block (copy verbatim from any existing section file).
- `_inbox/` is gitignored and is the image source. It stays out of `static/`.
- Captions are thematic, not spec sheets. Never put grades or cert numbers in captions.
- Do not touch: `content/gallery/volume-1/`, `volume-2/`, `stamped-cards/`, `waifu/`, or any file under `layouts/`.

---

### Task 1: Verification script

**Files:**
- Create: `scripts/check-gallery.py`

**Interfaces:**
- Produces: `python3 scripts/check-gallery.py` — exit 0 on pass, exit 1 with a printed list of failures. Every later task runs this.

- [ ] **Step 1: Write the script**

```python
#!/usr/bin/env python3
"""Verify gallery content: image refs resolve, and each slab is used exactly once."""
import re
import sys
import urllib.parse
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
CONTENT = ROOT / "content"
STATIC = ROOT / "static"
SLABS = STATIC / "images" / "slabs"

EXPECTED_COUNTS = {
    "definitive-pokemon": 3,
    "touchstones": 7,
    "personal-significance": 15,
    "chinese-exclusives": 6,
    "masaki": 5,
}

SRC_RE = re.compile(r'<img[^>]*\ssrc="([^"]+)"')


def collect():
    """Return {md_path: [resolved static paths]} for every img src in content/."""
    refs = {}
    for md in sorted(CONTENT.rglob("*.md")):
        found = []
        for raw in SRC_RE.findall(md.read_text(encoding="utf-8")):
            src = urllib.parse.unquote(raw)
            if "images/" not in src:
                continue
            found.append(STATIC / src[src.index("images/"):])
        refs[md] = found
    return refs


def main():
    failures = []
    refs = collect()

    # 1. Every referenced image exists on disk.
    for md, paths in refs.items():
        for p in paths:
            if not p.is_file():
                failures.append(f"missing image: {p.relative_to(ROOT)} (referenced by {md.relative_to(ROOT)})")

    # 2. Every slab image is referenced exactly once across all content.
    used = Counter()
    for paths in refs.values():
        for p in paths:
            if SLABS in p.parents:
                used[p.name] += 1
    on_disk = {p.name for p in SLABS.iterdir() if p.is_file()}
    for name in sorted(on_disk - set(used)):
        failures.append(f"orphan slab image, referenced by no page: {name}")
    for name, n in sorted(used.items()):
        if name not in on_disk:
            continue
        if n > 1:
            failures.append(f"slab image referenced {n} times, must be exactly 1: {name}")

    # 3. No lingering references to removed sections.
    for md in sorted(CONTENT.rglob("*.md")):
        if "gold-stars" in md.read_text(encoding="utf-8"):
            failures.append(f"reference to removed gold-stars section: {md.relative_to(ROOT)}")

    # 4. Section card counts match the design doc.
    for section, expected in EXPECTED_COUNTS.items():
        md = CONTENT / "gallery" / section / "_index.md"
        if not md.is_file():
            failures.append(f"missing section page: {md.relative_to(ROOT)}")
            continue
        actual = len([p for p in refs[md] if SLABS in p.parents])
        if actual != expected:
            failures.append(f"{section}: {actual} slab images, expected {expected}")

    if failures:
        print(f"FAIL ({len(failures)} problem(s)):")
        for f in failures:
            print("  -", f)
        return 1
    total = sum(EXPECTED_COUNTS.values())
    print(f"PASS: {total} slab images, each referenced exactly once")
    return 0


if __name__ == "__main__":
    sys.exit(main())
```

- [ ] **Step 2: Run it to verify it fails**

Run: `cd /home/tng/workspace/binderplan/.claude/worktrees/slabs-refresh && python3 scripts/check-gallery.py`
Expected: FAIL. It will report the missing `chinese-exclusives` section page and wrong counts for every other section. This is correct — the content doesn't exist yet.

- [ ] **Step 3: Commit**

```bash
git add scripts/check-gallery.py
git commit -m "test: add gallery reference verification script"
```

---

### Task 2: Stage the 36 images

Adds new images under their target names. **Does not delete anything** — the old files stay until Task 9, so the site never references a missing file.

**Files:**
- Create: 36 files in `static/images/slabs/`
- Source: `_inbox/` (gitignored, already populated and verified full-size)

**Interfaces:**
- Produces: the exact filenames every content task references.

- [ ] **Step 1: Copy and rename**

```bash
cd /home/tng/workspace/binderplan/.claude/worktrees/slabs-refresh
python3 - <<'EOF'
import shutil
from pathlib import Path

ROOT = Path.cwd()
SRC = ROOT / "_inbox"
DST = ROOT / "static" / "images" / "slabs"

MAPPING = {
    # Definitive Pokemon
    "charizard.jpg": "definitive_charizard_base_shadowless.jpg",
    "Umbreon.jpg": "definitive_umbreon_gx_rainbow.jpg",
    "Kyogre.jpg": "definitive_kyogre_primal.jpg",
    # Touchstones
    "Pikachu.jpg": "touchstone_pikachu_blackstar_2000.jpg",
    "CelebiGoldStar.jpg": "touchstone_celebi_gold_star.jpg",
    "Professor.jpg": "touchstone_professor_program_energy.jpg",
    "Typholosion.jpg": "touchstone_typhlosion_vs_1st_ed.jpg",
    "Shaymin.jpg": "touchstone_shaymin_leafeon_deck.jpg",
    "PikaJP.jpg": "touchstone_pikachu_ex_sar.jpg",
    "Dragonite.jpg": "touchstone_dragonite_mega_ex.jpg",
    # Personal Significance
    "HoundoomAq.jpg": "personal_houndoom_aquapolis.jpg",
    "Houndoom.jpg": "personal_houndoom_ex_154.jpg",
    "Houndoom2.jpg": "personal_houndoom_ex_22.jpg",
    "Houndoor.jpg": "personal_houndour_neo2.jpg",
    "GengarEX.jpg": "personal_gengar_ex_phantom.jpg",
    "GengarJP.jpg": "personal_gengar_sabrina_gym2.jpg",
    "GengarTopps.jpg": "personal_gengar_topps.jpg",
    "Lickitung-Personal.jpg": "personal_lickitung_dragon_frontiers.jpg",
    "Mew2nd.jpg": "personal_mew_2nd.jpg",
    "Keckleon.jpg": "personal_kecleon_jp.jpg",
    "EmolgaCard.jpg": "personal_emolga_playing_3.jpg",
    "EmolgaSummer.jpg": "personal_emolga_carnival.jpg",
    "ShinyEmolga.jpg": "personal_emolga_shiny_fa.jpg",
    "Iris.jpg": "personal_iris_fa.jpg",
    "Rosa.jpg": "personal_rosa_sar.jpg",
    # Chinese Exclusives
    "eeveeccic.webp": "chinese_eevee_cbb2c.webp",
    "umbreonccic.webp": "chinese_umbreon_cbb2c.webp",
    "leafeon.webp": "chinese_leafeon_cbb2c.webp",
    "sylveonccic.webp": "chinese_sylveon_cbb2c.webp",
    "mauseholdccic.webp": "chinese_maushold_ex_sar.webp",
    "carmine.jpg": "chinese_carmine_sar.jpg",
    # Masaki
    "Alakazam.jpg": "masaki_alakazam.jpg",
    "GengarMasaki.jpg": "masaki_gengar.jpg",
    "golemmasakimissing.webp": "masaki_golem_wanted.webp",
    "omastarmasakimissing.webp": "masaki_omastar_wanted.webp",
    "machampmasaki-missing.webp": "masaki_machamp_wanted.webp",
}

assert len(MAPPING) == 36, f"expected 36 mappings, got {len(MAPPING)}"
assert len(set(MAPPING.values())) == 36, "duplicate target filename"

missing = [s for s in MAPPING if not (SRC / s).is_file()]
assert not missing, f"missing source files: {missing}"

for src, dst in MAPPING.items():
    shutil.copyfile(SRC / src, DST / dst)
print(f"staged {len(MAPPING)} images")
EOF
```

Note: `personal_mew_2nd.jpg`, `personal_kecleon_jp.jpg`, `personal_emolga_playing_3.jpg`, `personal_emolga_carnival.jpg`, `masaki_alakazam.jpg`, `masaki_gengar.jpg` and `touchstone_pikachu_blackstar_2000.jpg` intentionally overwrite existing files — same card, full-resolution replacement.

- [ ] **Step 2: Verify all 36 landed and are full-size**

```bash
python3 - <<'EOF'
from pathlib import Path
from PIL import Image
d = Path("static/images/slabs")
small = [(p.name, f"{Image.open(p).width}x{Image.open(p).height}")
         for p in sorted(d.iterdir()) if p.is_file() and Image.open(p).width < 700]
print("files on disk:", len([p for p in d.iterdir() if p.is_file()]))
print("under 700px:", small)
EOF
```

Expected: **55** files on disk. Seven of the 36 target names already existed and were overwritten in place (`personal_mew_2nd`, `personal_kecleon_jp`, `personal_emolga_playing_3`, `personal_emolga_carnival`, `masaki_alakazam`, `masaki_gengar`, `touchstone_pikachu_blackstar_2000`), so 26 old + 29 net-new = 55. Task 9 removes 19 of them, landing at the final 36.

Under 700px should list **only** the three Masaki want-scans (`masaki_golem_wanted.webp`, `masaki_omastar_wanted.webp`, `masaki_machamp_wanted.webp`) — these are accepted per the design doc.

- [ ] **Step 3: Commit**

```bash
git add static/images/slabs/
git commit -m "feat: stage 36 full-resolution slab images"
```

---

### Task 3: Definitive Pokemon

**Files:**
- Modify: `content/gallery/definitive-pokemon/_index.md`

Rows: `wide(4) + narrow(2)` = 6; `full(6)` = 6.

- [ ] **Step 1: Replace the file contents**

```markdown
---
title: "Definitive Pokemon"
description: "The cards that currently represent their Pokemon best in my collection"
layout: "gallery"
---

These are the cards that currently represent their Pokemon best in my collection. The choices are personal rather than permanent; a new illustration can always change my mind.

<div class="gallery-grid">
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/definitive_charizard_base_shadowless.jpg" alt="Graded Shadowless Base Set Charizard card" loading="lazy">
    <figcaption>Charizard Base Shadowless</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/definitive_kyogre_primal.jpg" alt="Graded full-art Primal Kyogre EX card" loading="lazy">
    <figcaption>Primal Kyogre EX</figcaption>
  </figure>
  <figure class="gallery-item span-full">
    <img src="../../images/slabs/definitive_umbreon_gx_rainbow.jpg" alt="Graded rainbow rare Umbreon GX card" loading="lazy">
    <figcaption>Umbreon GX Rainbow</figcaption>
  </figure>
</div>

<!-- Lightbox container -->
<div id="lightbox" class="lightbox">
  <span class="lightbox-close">&times;</span>
  <img id="lightbox-img" src="" alt="Full size image">
</div>
```

- [ ] **Step 2: Verify**

Run: `python3 scripts/check-gallery.py`
Expected: still FAIL overall, but no `definitive-pokemon` count error and no missing-image error for its three files.

- [ ] **Step 3: Commit**

```bash
git add content/gallery/definitive-pokemon/_index.md
git commit -m "feat: rebuild Definitive Pokemon section"
```

---

### Task 4: Touchstones

**Files:**
- Modify: `content/gallery/touchstones/_index.md`

Rows: `wide+narrow` | `half+half` | `wide+narrow` | `full` = 7 figures.

- [ ] **Step 1: Replace the file contents**

```markdown
---
title: "Touchstones"
description: "Cards that capture a moment in the hobby"
layout: "gallery"
---

These are reference points for eras and release styles I want represented in the collection. Some were major hobby moments; others simply capture how the TCG looked and felt at a particular time.

<div class="gallery-grid">
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/touchstone_pikachu_blackstar_2000.jpg" alt="Pikachu Black Star 2000 slab" loading="lazy">
    <figcaption><strong>Pikachu Black Star 2000.</strong> A turn-of-the-millennium Black Star promo.</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/touchstone_celebi_gold_star.jpg" alt="Graded Celebi Gold Star card from EX Crystal Guardians" loading="lazy">
    <figcaption><strong>Celebi Gold Star.</strong> The Gold Star treatment at the height of its scarcity.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/touchstone_professor_program_energy.jpg" alt="Graded Professor Program Psychic Energy card" loading="lazy">
    <figcaption><strong>Professor Program Energy.</strong> An organized-play reward that never reached retail.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/touchstone_typhlosion_vs_1st_ed.jpg" alt="Graded Japanese Blaine's Typhlosion card from the VS series" loading="lazy">
    <figcaption><strong>Blaine's Typhlosion.</strong> The VS series, where Gym leaders got their own deck identity.</figcaption>
  </figure>
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/touchstone_pikachu_ex_sar.jpg" alt="Graded Japanese Pikachu ex special art rare card" loading="lazy">
    <figcaption><strong>Pikachu ex SAR.</strong> The modern special-art treatment at full volume.</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/touchstone_shaymin_leafeon_deck.jpg" alt="Graded Japanese Shaymin card from the Leafeon expert deck" loading="lazy">
    <figcaption><strong>Shaymin Leafeon Deck.</strong> A promo tied to a Japanese expert deck release.</figcaption>
  </figure>
  <figure class="gallery-item span-full">
    <img src="../../images/slabs/touchstone_dragonite_mega_ex.jpg" alt="Graded Japanese Mega Dragonite ex card" loading="lazy">
    <figcaption><strong>Mega Dragonite ex.</strong> Mega Evolution's return, rendered as spectacle.</figcaption>
  </figure>
</div>

<!-- Lightbox container -->
<div id="lightbox" class="lightbox">
  <span class="lightbox-close">&times;</span>
  <img id="lightbox-img" src="" alt="Full size image">
</div>
```

- [ ] **Step 2: Verify**

Run: `python3 scripts/check-gallery.py`
Expected: no `touchstones` count error.

- [ ] **Step 3: Commit**

```bash
git add content/gallery/touchstones/_index.md
git commit -m "feat: rebuild Touchstones section"
```

---

### Task 5: Personal Significance

**Files:**
- Modify: `content/gallery/personal-significance/_index.md`

15 figures. Rows: `wide+narrow` | `half+half` | `wide+narrow` | `full` | `half+half` | `wide+narrow` | `half+half` | `half+half`.

- [ ] **Step 1: Replace the file contents**

```markdown
---
title: "Personal Significance"
description: "Cards with irreplaceable personal meaning"
layout: "gallery"
---

These cards are here because of private memories, milestones, or associations rather than a broader collecting category. I keep the labels simple because the stories matter more to me than turning them into public criteria.

<div class="gallery-grid">
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/personal_houndoom_aquapolis.jpg" alt="Graded Houndoom reverse foil card from Aquapolis" loading="lazy">
    <figcaption><strong>Houndoom Aquapolis.</strong> Where the Houndoom habit started.</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/personal_houndour_neo2.jpg" alt="Graded Japanese Houndour holo card from Neo Discovery" loading="lazy">
    <figcaption><strong>Houndour Neo 2.</strong> The line's beginning, in Japanese holo.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_houndoom_ex_154.jpg" alt="Graded full-art Mega Houndoom EX card" loading="lazy">
    <figcaption><strong>M Houndoom EX.</strong> The full-art Mega treatment, in its wider frame.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_houndoom_ex_22.jpg" alt="Graded Mega Houndoom EX card in standard set layout" loading="lazy">
    <figcaption><strong>M Houndoom EX 22.</strong> The same Mega, in the set's standard layout.</figcaption>
  </figure>
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/personal_gengar_sabrina_gym2.jpg" alt="Graded Japanese Sabrina's Gengar holo card from Gym 2" loading="lazy">
    <figcaption><strong>Sabrina's Gengar.</strong> The Gym-era printing, and the oldest Gengar here.</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/personal_gengar_topps.jpg" alt="Graded Topps TV Animation Gengar foil card" loading="lazy">
    <figcaption><strong>Gengar Topps.</strong> The TV animation printing, outside the TCG proper.</figcaption>
  </figure>
  <figure class="gallery-item span-full">
    <img src="../../images/slabs/personal_gengar_ex_phantom.jpg" alt="Graded Gengar EX card from XY Phantom Forces" loading="lazy">
    <figcaption><strong>Gengar EX.</strong> A modern Gengar with the confetti background.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_lickitung_dragon_frontiers.jpg" alt="Graded Lickitung Delta Species card from EX Dragon Frontiers" loading="lazy">
    <figcaption><strong>Lickitung Dragon Frontiers.</strong> A Delta Species oddity worth keeping.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_mew_2nd.jpg" alt="Graded Mew card labeled Mew 2nd" loading="lazy">
    <figcaption><strong>Mew 2nd.</strong> Kept for its personal association rather than a collection-wide role.</figcaption>
  </figure>
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/personal_kecleon_jp.jpg" alt="Graded Japanese Kecleon art rare card" loading="lazy">
    <figcaption><strong>Kecleon.</strong> A card whose place in the collection is personal rather than thematic.</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/personal_emolga_playing_3.jpg" alt="Graded Emolga three of hearts playing card" loading="lazy">
    <figcaption><strong>Emolga Playing.</strong> A personal favorite within the wider Emolga collection.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_emolga_carnival.jpg" alt="Graded Japanese Emolga Summer Carnival promo card" loading="lazy">
    <figcaption><strong>Emolga Summer Carnival.</strong> A favorite Emolga promo and the card featured on the homepage.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_emolga_shiny_fa.jpg" alt="Graded Japanese full-art Emolga card from Shiny Collection" loading="lazy">
    <figcaption><strong>Emolga Shiny Collection.</strong> The full-art shiny, first edition.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_iris_fa.jpg" alt="Graded Japanese full-art Iris trainer card" loading="lazy">
    <figcaption><strong>Iris.</strong> Black &amp; White full art, kept for the illustration.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/personal_rosa_sar.jpg" alt="Graded Japanese Rosa's Encouragement special art rare card" loading="lazy">
    <figcaption><strong>Rosa.</strong> The modern counterpart, thirteen years later.</figcaption>
  </figure>
</div>

<!-- Lightbox container -->
<div id="lightbox" class="lightbox">
  <span class="lightbox-close">&times;</span>
  <img id="lightbox-img" src="" alt="Full size image">
</div>
```

- [ ] **Step 2: Verify**

Run: `python3 scripts/check-gallery.py`
Expected: no `personal-significance` count error.

- [ ] **Step 3: Commit**

```bash
git add content/gallery/personal-significance/_index.md
git commit -m "feat: rebuild Personal Significance section"
```

---

### Task 6: Chinese Exclusives (new section)

**Files:**
- Create: `content/gallery/chinese-exclusives/_index.md`

Rows: `half+half` | `half+half` | `wide+narrow` = 6 figures. No Still Hunting block — the four CBB2C cards are the full arts, which is the whole of what's collected there.

- [ ] **Step 1: Create the file**

```markdown
---
title: "Chinese Exclusives"
description: "Cards from Chinese-market releases with no international printing"
layout: "gallery"
---

Chinese-market releases have their own sets, their own numbering, and their own grading companies. I collect them because that parallel track produces cards the rest of the hobby never sees. This one stays open-ended — there's no set I'm trying to finish here.

<div class="gallery-grid">
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/chinese_eevee_cbb2c.webp" alt="Graded Chinese Eevee full art card" loading="lazy">
    <figcaption><strong>Eevee.</strong> The starting point of the CBB2C gem-pack Eeveelutions.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/chinese_umbreon_cbb2c.webp" alt="Graded Chinese Umbreon full art card" loading="lazy">
    <figcaption><strong>Umbreon.</strong> Moonlight, in the set's signature holo.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/chinese_leafeon_cbb2c.webp" alt="Graded Chinese Leafeon full art card" loading="lazy">
    <figcaption><strong>Leafeon.</strong> The same treatment turned green.</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/chinese_sylveon_cbb2c.webp" alt="Graded Chinese Sylveon full art card" loading="lazy">
    <figcaption><strong>Sylveon.</strong> The brightest of the four.</figcaption>
  </figure>
  <figure class="gallery-item span-wide">
    <img src="../../images/slabs/chinese_maushold_ex_sar.webp" alt="Graded Chinese Maushold ex special art rare card" loading="lazy">
    <figcaption><strong>Maushold ex.</strong> A special art from the Chinese Scarlet &amp; Violet line.</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/chinese_carmine_sar.jpg" alt="Graded Chinese Carmine special art rare trainer card" loading="lazy">
    <figcaption><strong>Carmine.</strong> A Chinese-exclusive trainer special art.</figcaption>
  </figure>
</div>

<!-- Lightbox container -->
<div id="lightbox" class="lightbox">
  <span class="lightbox-close">&times;</span>
  <img id="lightbox-img" src="" alt="Full size image">
</div>
```

- [ ] **Step 2: Verify**

Run: `python3 scripts/check-gallery.py`
Expected: no `chinese-exclusives` errors.

- [ ] **Step 3: Confirm the page renders**

Run: `hugo --quiet --destination /tmp/hugocheck && test -f /tmp/hugocheck/gallery/chinese-exclusives/index.html && echo RENDERED`
Expected: `RENDERED`

- [ ] **Step 4: Commit**

```bash
git add content/gallery/chinese-exclusives/_index.md
git commit -m "feat: add Chinese Exclusives section"
```

---

### Task 7: Masaki — owned grid plus Still Hunting

**Files:**
- Modify: `content/gallery/masaki/_index.md`

Owned row: `half+half` = 6. Still Hunting row: `narrow+narrow+narrow` = 6 — the narrowest slot, chosen deliberately because the three want-scans are 424×589 and would look soft in anything larger.

- [ ] **Step 1: Replace the file contents**

```markdown
---
title: "Masaki"
description: "Japanese mail-in trade promos from the 1998–1999 Communication Evolution campaign"
layout: "gallery"
---

These cards were distributed through Japan's 1998–1999 Communication Evolution campaign, which asked participants to mail in designated cards for evolved promotional versions. I like them as a compact set with an unusual release story and a consistent visual identity.

<div class="gallery-grid">
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/masaki_alakazam.jpg" alt="Graded Japanese Masaki Alakazam promotional card" loading="lazy">
    <figcaption>Alakazam Masaki</figcaption>
  </figure>
  <figure class="gallery-item span-half">
    <img src="../../images/slabs/masaki_gengar.jpg" alt="Graded Japanese Masaki Gengar promotional card" loading="lazy">
    <figcaption>Gengar Masaki</figcaption>
  </figure>
</div>

---

## Still Hunting

These are the ones I haven't tracked down yet. If you've got a lead, I'm listening.

<div class="gallery-grid">
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/masaki_golem_wanted.webp" alt="Japanese Masaki Golem promotional card" loading="lazy">
    <figcaption>Golem Masaki</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/masaki_omastar_wanted.webp" alt="Japanese Masaki Omastar promotional card" loading="lazy">
    <figcaption>Omastar Masaki</figcaption>
  </figure>
  <figure class="gallery-item span-narrow">
    <img src="../../images/slabs/masaki_machamp_wanted.webp" alt="Japanese Masaki Machamp promotional card" loading="lazy">
    <figcaption>Machamp Masaki</figcaption>
  </figure>
</div>

<!-- Lightbox container -->
<div id="lightbox" class="lightbox">
  <span class="lightbox-close">&times;</span>
  <img id="lightbox-img" src="" alt="Full size image">
</div>
```

- [ ] **Step 2: Verify**

Run: `python3 scripts/check-gallery.py`
Expected: no `masaki` count error. The only remaining failures should be orphaned old images (cleaned up in Task 9).

- [ ] **Step 3: Commit**

```bash
git add content/gallery/masaki/_index.md
git commit -m "feat: rebuild Masaki section with Still Hunting block"
```

---

### Task 8: Prose — gallery index, Emolga intro, grading philosophy

Three prose edits, grouped because they are one coherent change: making the written structure match the rebuilt gallery. No images involved.

**Files:**
- Modify: `content/gallery/_index.md:19-27`
- Modify: `content/gallery/emolga-masterset/_index.md:9`
- Modify: `content/philosophy/grading.md:12-28` and `:35`

- [ ] **Step 1: Restructure the gallery index**

In `content/gallery/_index.md`, replace lines 14–27 (the `## Other Collections`, `## Special Collections`, and `## Personal Slabs` blocks) with:

```markdown
## Other Collections

- **[Stamped Cards](stamped-cards/)** — Prerelease, league, and event-stamped cards
- **[Trainer Full Arts](waifu/)** — Japanese trainer cards collected for character illustration

## Themes

Groups defined by judgment. There's no such thing as a card missing from a theme.

- **[Definitive Pokemon](definitive-pokemon/)** — The best versions, chosen with intent
- **[Touchstones](touchstones/)** — Cards that capture a moment in the hobby
- **[Personal Significance](personal-significance/)** — Cards with irreplaceable personal meaning

## Runs

Groups with a defined outside, where a card can be genuinely missing.

- **[Masaki](masaki/)** — Japanese mail-in trade promos from the Communication Evolution campaign
- **[Chinese Exclusives](chinese-exclusives/)** — Chinese-market releases with no international printing
- **[Emolga Masterset](emolga-masterset/)** — Every Emolga card I can get my hands on. No regrets.
```

Then **remove** the `- **[Emolga Masterset](emolga-masterset/)** — ...` line from the `## Volumes` block at line 12, since it now lives under Runs. The Volumes block keeps only Volume I and Volume II.

- [ ] **Step 2: Rewrite the Emolga intro**

In `content/gallery/emolga-masterset/_index.md`, replace the paragraph at line 9 with:

```markdown
I'm working toward every Emolga printing I can track down. It's the longest-running of the runs and the only one that will never actually end: one Pokemon across languages, eras, and illustration styles, because Emolga is the best and I will not be taking questions.
```

- [ ] **Step 3: Rewrite grading.md Public Roles**

In `content/philosophy/grading.md`, replace lines 12–28 (from `## Public Roles` through the trade/resale paragraph) with:

```markdown
## Public Roles

Every graded card needs one clear reason to be in plastic, and each card takes exactly one. The reasons come in two kinds, and the difference is whether the group has an outside.

### Themes

Membership is a judgment call. There is no such thing as a card missing from a theme, because the theme is defined by what's in it.

**Definitive Pokemon** — the card that currently represents a Pokemon best in the collection.

**Touchstones** — cards tied to a particular era, release style, or moment in the hobby.

**Personal Significance** — cards whose meaning comes from a memory, milestone, gift, or personal connection rather than a broader collecting category.

### Runs

Membership is a fact about the card rather than an opinion, so a run can be incomplete — and saying which cards are still missing is part of the point.

**Masaki** — the Communication Evolution mail-in promos, collected as a set I intend to finish.

**Chinese Exclusives** — Chinese-market releases, collected as an ongoing interest rather than a defined set.

**Emolga Masterset** — every Emolga printing I can track down.

Cards held mainly for trade or resale may still be stored with the collection, but I do not treat that as a public curatorial role.
```

- [ ] **Step 4: Fix the Tier A display rule**

In the same file, in `## Physical Organization`, replace the Tier A bullet `- Crown Art and selected Historical / Touchstone cards` with:

```markdown
- Selected Touchstones and standout cards from the runs
```

This removes the last reference to Crown Art, which is dropped entirely per the design doc.

- [ ] **Step 5: Verify no stale concepts remain**

```bash
grep -rn "Crown Art\|Historical / Touchstone\|gold-stars\|Gold Star" content/ || echo "CLEAN"
```
Expected: the only hit is the Celebi caption in `touchstones/_index.md` ("Celebi Gold Star" — the card name, which is correct and stays). No hits for `Crown Art`, `Historical / Touchstone`, or `gold-stars`.

- [ ] **Step 6: Commit**

```bash
git add content/gallery/_index.md content/gallery/emolga-masterset/_index.md content/philosophy/grading.md
git commit -m "docs: align gallery index and grading philosophy with Themes/Runs"
```

---

### Task 9: Remove superseded and sold images

Now that no page references them, delete the 19 old files. This is last so the site is never broken mid-plan.

**Files:**
- Delete: 19 files in `static/images/slabs/` (16 sold + 1 pre-existing orphan + 2 superseded-and-renamed)

- [ ] **Step 1: Confirm they are unreferenced**

Run: `python3 scripts/check-gallery.py`
Expected: FAIL, listing exactly 19 `orphan slab image` lines and nothing else. If any *other* failure type appears, stop and fix it before deleting.

- [ ] **Step 2: Delete**

```bash
cd /home/tng/workspace/binderplan/.claude/worktrees/slabs-refresh
git rm static/images/slabs/definitive_umbreon_aquapolis.jpg \
       static/images/slabs/definitive_mew_shining_darkness.jpg \
       static/images/slabs/definitive_charizard_base_2.jpg \
       static/images/slabs/definitive_kingdra_aquapolis.jpg \
       static/images/slabs/definitive_gengar_chinese_2025.jpg \
       static/images/slabs/definitive_plusle_jp.jpg \
       static/images/slabs/definitive_minun_jp.jpg \
       static/images/slabs/definitive_houndoom_aquapolis.jpg \
       static/images/slabs/touchstone_jolteon_pop.jpg \
       static/images/slabs/touchstone_dragonite_expedition.jpg \
       static/images/slabs/touchstone_squirtle_expedition.jpg \
       static/images/slabs/touchstone_charizard_jp_basic.jpg \
       static/images/slabs/touchstone_umbreon_tag.jpg \
       static/images/slabs/touchstone_charizard_151_jp.jpg \
       static/images/slabs/touchstone_mew_sv4a_jp.jpg \
       static/images/slabs/touchstone_maushold_ccic.jpg \
       static/images/slabs/masaki_golem.jpg \
       static/images/slabs/masaki_omastar.jpg \
       static/images/slabs/personal_kanga_mega_jp.jpg
```

Note: 19 paths — the 16 sold, the 1 orphan (`personal_kanga_mega_jp`), and the 2 superseded files that changed name (`definitive_houndoom_aquapolis` → now `personal_houndoom_aquapolis`; `touchstone_maushold_ccic` → now `chinese_maushold_ex_sar`). The other 7 superseded files were overwritten in place in Task 2 and must **not** be deleted.

- [ ] **Step 3: Verify the full suite passes**

Run: `python3 scripts/check-gallery.py`
Expected: `PASS: 36 slab images, each referenced exactly once`

- [ ] **Step 4: Commit**

```bash
git commit -m "chore: remove sold and superseded slab images"
```

---

### Task 10: Final verification

**Files:** none modified.

- [ ] **Step 1: Clean build**

```bash
rm -rf public /tmp/hugocheck
hugo --gc --minify --destination /tmp/hugocheck
```
Expected: build completes with no ERROR or WARN lines.

- [ ] **Step 2: Verification script**

Run: `python3 scripts/check-gallery.py`
Expected: `PASS: 36 slab images, each referenced exactly once`

- [ ] **Step 3: Confirm every gallery page rendered**

```bash
for s in definitive-pokemon touchstones personal-significance chinese-exclusives masaki emolga-masterset volume-1 volume-2 stamped-cards waifu; do
  test -f /tmp/hugocheck/gallery/$s/index.html && echo "ok  $s" || echo "MISSING  $s"
done
test -e /tmp/hugocheck/gallery/gold-stars && echo "PROBLEM: gold-stars still built" || echo "ok  gold-stars absent"
```
Expected: `ok` for all ten sections, and `gold-stars absent`.

- [ ] **Step 4: Confirm no broken image paths in built HTML**

```bash
python3 - <<'EOF'
import re
from pathlib import Path
out = Path("/tmp/hugocheck")
bad = []
SRC_RE = re.compile(r'<img[^>]*\ssrc=(?:"([^"]+)"|\'([^\']+)\'|([^\s>]+))')
for html in out.rglob("*.html"):
    for m in SRC_RE.finditer(html.read_text(encoding="utf-8")):
        src = next(g for g in m.groups() if g)
        if not src.startswith("/") and "images/" not in src:
            continue
        import urllib.parse
        rel = urllib.parse.unquote(src)
        target = (out / rel.lstrip("/")) if rel.startswith("/") else (html.parent / rel)
        if not target.exists():
            bad.append(f"{html.relative_to(out)} -> {src}")
print("broken:", len(bad))
for b in bad[:20]:
    print("  ", b)
EOF
```
Expected: `broken: 0`

- [ ] **Step 5: Review the full diff**

```bash
git diff main --stat
git diff main -- content/ scripts/
```
Confirm: no changes to `layouts/`, `hugo.toml`, `volume-1`, `volume-2`, `stamped-cards`, or `waifu`.

- [ ] **Step 6: Commit any stragglers and report**

```bash
git status --short
```
Expected: clean, apart from ignored `_inbox/`.

---

## Post-plan notes

- **Deferred:** replacing the three Masaki want-scans (424×589) with images at the Emolga Still Hunting standard (~712×998). Drop-in — same filenames, no content change.
- **Deferred:** re-verifying the 24 PSA cert numbers against the full-size images. Cert numbers are recorded in the design doc for reference only and are not published.
- **Not recoverable:** CCIC cert numbers are masked in the source photos.
