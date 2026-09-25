"""Owner review worklist stays synchronized with published digital collections."""

from pathlib import Path
import shutil
import sys

import pytest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
import validation_checklist


def test_priority_items_include_uncertain_images_and_pending_pdf_order():
    items = {item["id"]: item for item in validation_checklist.collect_review_items(ROOT)}
    assert items["tate-lizas-training-01"]["tier"] == "priority"
    assert items["tate-lizas-training-01"]["english_name"] == "Tate & Liza's Training"
    assert items["tate-lizas-training-01"]["number"] == ""
    assert items["bulbasaur-02"]["english_name"] == "Bulbasaur"
    assert items["bulbasaur-02"]["number"] == "No.001"
    assert items["holding-p09-09"]["number"] == "93/130"
    assert items["holding-p09-09"]["number_basis"] == "recorded label; verify"
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
    assert ("emolga-01", "emolga-31") in [pair["ids"] for pair in pairs]
    expected = validation_checklist.render_checklist(items, pairs)
    assert expected.count("- [ ] ") == len(items) + len(pairs)
    assert "English: **Bulbasaur**" in expected
    assert "Printed: フシギダネ" in expected
    assert "Number: No.001" in expected
    assert "Number: 93/130 (recorded label; verify)" in expected
    assert "Number: not recorded" in expected
    assert "English: **Emolga** · Number: 116/086" in expected
    assert expected == (ROOT / "docs/card-validation-checklist.md").read_text(encoding="utf-8")


def test_optional_emolga_requires_a_public_manifest_only_when_route_is_published(tmp_path):
    for name in ("card-registry.md",):
        destination = tmp_path / "docs" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "docs" / name, destination)
    for name in ("card-images.yaml", "holding-binder.yaml"):
        destination = tmp_path / "data" / name
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "data" / name, destination)
    for binder_id in ("volume-1", "volume-2", "waifu", "stamped-cards"):
        destination = tmp_path / "data/binders" / f"{binder_id}.yaml"
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(ROOT / "data/binders" / f"{binder_id}.yaml", destination)

    assert all(item["collection"] != "Emolga Masterset"
               for item in validation_checklist.collect_review_items(tmp_path))
    route = tmp_path / "content/gallery/emolga-masterset/_index.md"
    route.parent.mkdir(parents=True)
    route.write_text('---\ntitle: Emolga Masterset\nbinder: emolga-masterset\n---\n')
    with pytest.raises(FileNotFoundError, match="emolga-masterset.yaml"):
        validation_checklist.collect_review_items(tmp_path)
    route.write_text('---\ntitle: Emolga Masterset\ndraft: true\n---\n')
    assert all(item["collection"] != "Emolga Masterset"
               for item in validation_checklist.collect_review_items(tmp_path))


def test_unplaced_snivy_requires_published_stamped_manifest(monkeypatch):
    original = validation_checklist.digital_binder.load_yaml

    def load_yaml(path):
        manifest = original(path)
        if path.name == "stamped-cards.yaml":
            manifest["publication_status"] = "draft"
        return manifest

    monkeypatch.setattr(validation_checklist.digital_binder, "load_yaml", load_yaml)
    assert "snivy-04" not in {item["id"] for item in validation_checklist.collect_review_items(ROOT)}


def test_pdf_source_receipt_detects_a_stale_markdown_edit(tmp_path):
    docs = tmp_path / "docs"
    docs.mkdir()
    for name in ("card-validation-checklist.md", "card-validation-checklist.pdf", "card-validation-checklist.pdf.sha256"):
        shutil.copy2(ROOT / "docs" / name, docs / name)
    assert validation_checklist.pdf_source_is_current(tmp_path)
    with (docs / "card-validation-checklist.md").open("a", encoding="utf-8") as out:
        out.write("\nChanged after PDF generation.\n")
    assert not validation_checklist.pdf_source_is_current(tmp_path)


def test_pdf_is_present_and_tracks_the_generated_markdown():
    pdf = ROOT / "docs/card-validation-checklist.pdf"
    assert pdf.read_bytes().startswith(b"%PDF-")
    assert validation_checklist.pdf_source_is_current(ROOT)
