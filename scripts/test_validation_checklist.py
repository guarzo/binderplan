"""Owner review worklist stays synchronized with published digital collections."""

from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validation_checklist


def test_priority_items_include_uncertain_images_and_pending_pdf_order():
    items = {item["id"]: item for item in validation_checklist.collect_review_items(ROOT)}
    assert items["tate-lizas-training-01"]["tier"] == "priority"
    assert "physical placement" in items["tate-lizas-training-01"]["reasons"]
    assert "proxy image" in items["tate-lizas-training-01"]["reasons"]
    assert items["holding-p01-01"]["tier"] == "priority"
    assert "photo-crop image" in items["holding-p01-01"]["reasons"]
    assert items["holding-p01-02"]["tier"] == "priority"
    assert "holding-p01-05" not in items  # Holding high is not an in-hand-status field.
    assert items["holding-p09-09"]["location"].startswith("Trade top loader")
    assert items["dragonite-01"]["tier"] == "follow-up"
    assert "025/BW-P" not in items  # Wanted references are not owned review cards.
    assert items["snivy-04"]["tier"] == "priority"
    assert "physical placement" in items["snivy-04"]["reasons"]
    assert "pocket unverified" in items["snivy-04"]["location"]


def test_ci_rejects_stale_owner_checklist():
    workflow = (ROOT / ".github/workflows/hugo.yml").read_text()
    assert "python scripts/validation_checklist.py --check" in workflow


def test_checklist_is_complete_deduplicated_and_generated_from_live_records():
    items = validation_checklist.collect_review_items(ROOT)
    ids = [item["id"] for item in items]
    assert len(ids) == len(set(ids))
    assert all(item["collection"] and item["location"] and item["reasons"] for item in items)
    pairs = validation_checklist.collect_duplicate_candidates(ROOT)
    assert len(pairs) == 7
    assert ("emolga-01", "emolga-31") in pairs
    expected = validation_checklist.render_checklist(items, pairs)
    assert expected.count("- [ ] ") == len(items) + len(pairs)
    assert expected == (ROOT / "docs/card-validation-checklist.md").read_text(encoding="utf-8")
