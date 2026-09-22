# Printable Holding Sort Checklist Implementation Plan

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Produce a printable checklist that lets the owner physically sort all 97 current holding-pool cards into the approved Review, Keeper, Trade, Release, and identity-check destinations.

**Architecture:** Create one LaTeX source and compiled PDF beside the approved manifest. The checklist mirrors the manifest rather than creating a second classification source: cards are grouped by physical destination, each line carries its evidence key and a checkbox, and summary counts must reconcile to 97.

**Tech Stack:** LaTeX (`pdflatex`), shell verification, existing Markdown design/manifest

**Spec:** `docs/superpowers/specs/2026-09-22-review-keeper-trade-binders-design.md`

## Global Constraints

- The approved manifest at `docs/2026-09-22-holding-pool-sorting-manifest.md` is the classification source of truth.
- The checklist must contain exactly 97 uniquely keyed cards.
- Destination totals must remain Review 38, Keeper 46, Trade 10, Release 3.
- Review ordering is EDGE Watches, Existing-theme EDGE, REDUNDANT, FUTURE SELF, Event Staging.
- Keeper ordering is Personal Keepers, Beautiful Misfits, Heritage, Species Studies.
- Event Staging remains empty and appears at the end of Review.
- Trade placements remain proposed until the owner confirms active availability.
- Release placements remain recommendations until physically executed.
- Low-confidence identity conflicts must appear as a separate in-hand check section.

---

### Task 1: Build and verify the printable checklist

**Files:**
- Create: `docs/2026-09-22-holding-pool-sorting-checklist.tex`
- Create: `docs/2026-09-22-holding-pool-sorting-checklist.pdf`
- Reference: `docs/2026-09-22-holding-pool-sorting-manifest.md`

**Interfaces:**
- Consumes: the 97 manifest rows and destination totals from the approved Markdown manifest.
- Produces: a human-printable A4 PDF and editable LaTeX source.

- [x] **Step 1: Create the LaTeX checklist structure**

Use A4 paper, compact margins, page numbers, square checkboxes, and sections in this exact order:

1. Setup and count reconciliation
2. Review — EDGE Watches
3. Review — Existing-theme EDGE, including named incumbents
4. Review — REDUNDANT by target theme
5. Review — FUTURE SELF and empty Event Staging reminder
6. Keeper — Personal Keepers
7. Keeper — Beautiful Misfits
8. Keeper — Heritage
9. Keeper — Species Studies
10. Trade — Core Value, with an `Available now` checkbox
11. Release — with a second `Release executed` checkbox
12. In-hand identity checks
13. Final count and section-photo close-out

Every card line must include its manifest key, short card name, and destination-specific checkbox.

- [x] **Step 2: Compile the PDF twice**

Run:

```bash
cd docs
pdflatex -interaction=nonstopmode -halt-on-error 2026-09-22-holding-pool-sorting-checklist.tex
pdflatex -interaction=nonstopmode -halt-on-error 2026-09-22-holding-pool-sorting-checklist.tex
```

Expected: exit code 0 and `2026-09-22-holding-pool-sorting-checklist.pdf` created.

- [x] **Step 3: Verify document structure and counts**

Run a script or text check that confirms:

```text
97 unique manifest keys
38 Review cards
46 Keeper cards
10 Trade cards
3 Release cards
```

Run:

```bash
pdfinfo docs/2026-09-22-holding-pool-sorting-checklist.pdf
```

Expected: A4 page size and a nonzero page count.

Inspect the LaTeX log:

```bash
rg 'Overfull|LaTeX Warning' docs/2026-09-22-holding-pool-sorting-checklist.log
```

Expected: no overfull boxes or unresolved-reference warnings.

- [x] **Step 4: Visually inspect every rendered page**

Render pages to temporary PNG files using `pdftoppm`, inspect for clipped rows, illegible type, orphaned headings, and insufficient writing space, then adjust and recompile if needed.

- [x] **Step 5: Remove generated build intermediates**

Delete only:

```text
docs/2026-09-22-holding-pool-sorting-checklist.aux
docs/2026-09-22-holding-pool-sorting-checklist.log
docs/2026-09-22-holding-pool-sorting-checklist.out
```

Keep the `.tex` and `.pdf` files.

- [x] **Step 6: Commit the checklist**

```bash
git add docs/2026-09-22-holding-pool-sorting-checklist.tex \
        docs/2026-09-22-holding-pool-sorting-checklist.pdf
git commit -m "Add printable holding pool sort checklist"
```

- [x] **Step 7: Run final branch verification**

Run:

```bash
python3 -m pytest scripts/test_check_registry.py -q
python3 scripts/check-registry.py docs/card-registry.md
python3 scripts/check-gallery.py
hugo --gc --minify
git diff --check origin/main...HEAD
```

Expected: tests and validators pass, Hugo builds successfully, and the branch diff has no whitespace errors.

- [ ] **Step 8: Push and open a pull request**

Push the design branch and open a PR against `main` summarizing the architecture, 97-card manifest, printable checklist, and verification results.
