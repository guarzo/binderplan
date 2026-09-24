"""The Emolga draft must never turn pictured placeholders into owned cards."""

import hashlib
import importlib.util
import re
import subprocess
from pathlib import Path

from PIL import Image
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("emolga_digital_binder", ROOT / "scripts/digital_binder.py")
digital_binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digital_binder)


def test_optional_four_pocket_binder_is_validated_without_changing_volume_requirements(tmp_path):
    binders = tmp_path / "data/binders"
    binders.mkdir(parents=True)
    for name in ("volume-1", "volume-2", "emolga-masterset"):
        (binders / f"{name}.yaml").write_text(yaml.safe_dump({"volume_id": name}))
    errors = []
    manifests = digital_binder._load_project_manifests(tmp_path, errors)
    assert errors == []
    assert set(manifests) == {"volume-1", "volume-2", "emolga-masterset"}


def test_physical_placeholder_requires_wanted_identity_and_evidence_not_card_id(tmp_path):
    evidence = tmp_path / "docs/evidence/emolga/page.webp"
    evidence.parent.mkdir(parents=True)
    evidence.write_bytes(b"photo")
    pocket = {
        "position": 1, "placeholder": True, "wanted_id": "081/BW-P",
        "evidence": {"type": "published-photo", "source": "docs/evidence/emolga/page.webp", "observed_on": "2026-09-24"},
    }
    manifest = {
        "version": 1, "volume_id": "emolga-masterset", "publication_status": "draft",
        "pocket_layout": {"rows": 2, "columns": 2},
        "leaves": [{"id": "em-01", "kind": "cards", "physical_leaf": 1,
                    "chapter": "Emolga Masterset", "chapter_order": 1, "theme": "Page 1",
                    "pockets": [pocket, {"position": 2, "empty": True},
                                {"position": 3, "empty": True}, {"position": 4, "empty": True}]}],
    }
    errors = []
    occupied = digital_binder._validate_volume_manifest(tmp_path, "emolga-masterset", manifest, {}, errors)
    assert occupied == set()
    assert errors == []
    manifest["leaves"][0]["pockets"][0] = {**pocket, "card_id": "emolga-01"}
    errors = []
    digital_binder._validate_volume_manifest(tmp_path, "emolga-masterset", manifest, {}, errors)
    assert any("placeholder" in error and "card_id" in error for error in errors)
    manifest["leaves"][0]["pockets"][0] = {**pocket, "wanted_id": ""}
    errors = []
    digital_binder._validate_volume_manifest(tmp_path, "emolga-masterset", manifest, {}, errors)
    assert any("wanted_id" in error for error in errors)
    manifest["leaves"][0]["pockets"][0] = {**pocket, "placeholder": "true"}
    errors = []
    digital_binder._validate_volume_manifest(tmp_path, "emolga-masterset", manifest, {}, errors)
    assert any("placeholder" in error for error in errors)
    manifest["leaves"][0]["pockets"][0] = {**pocket, "evidence": {**pocket["evidence"], "observed_on": "20260924"}}
    errors = []
    digital_binder._validate_volume_manifest(tmp_path, "emolga-masterset", manifest, {}, errors)
    assert any("observed_on" in error for error in errors)


def test_previous_revision_includes_existing_optional_binder():
    errors = []
    previous = digital_binder._load_previous_manifests(ROOT, "HEAD", errors)
    assert errors == []
    assert "emolga-masterset" in previous


def test_new_binder_does_not_require_prior_pending_placements():
    previous = {"volume-1": {"leaves": []}}
    current = {
        "volume-1": {"leaves": []},
        "emolga-masterset": {"leaves": [{"kind": "cards", "physical_leaf": 1,
                                       "pockets": [{"position": 1, "card_id": "emolga-02",
                                                    "placement": {"status": "confirmed"}}]}]},
    }
    assert digital_binder.validate_transition(previous, current) == []


def test_draft_preview_preserves_page_order_ownership_and_public_photo_gallery(tmp_path):
    subprocess.run(["hugo", "--buildDrafts", "--destination", str(tmp_path / "draft")],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    preview = tmp_path / "draft/gallery/emolga-masterset-preview/index.html"
    html = preview.read_text()
    assert 'data-binder="emolga-masterset"' in html
    assert 'data-pocket-rows="2" data-pocket-columns="2"' in html
    assert re.findall(r'data-binder-leaf="em-(\d+)"', html) == [f"{n:02d}" for n in range(1, 12)]
    assert len(re.findall(r'\bdata-pocket-position="[1-4]"', html)) == 44
    assert len(re.findall(r'\bdata-card-id="emolga-\d{2}"', html)) == 42
    assert len(re.findall(r'data-placeholder-wanted="(?:025|081)/BW-P"', html)) == 2
    assert 'data-binder-prev' in html and 'data-binder-next' in html
    assert 'data-wanted-section' in html
    assert "Missing%20Emolga%20025%20BW-P.jpg" in html
    assert "Missing%20Emolga%20BW-9%2081.jpg" in html
    assert not re.search(r'<img[^>]+src="https?://', html)
    assert not digital_binder.validate_public_output(tmp_path / "draft")

    subprocess.run(["hugo", "--destination", str(tmp_path / "public")],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    assert not (tmp_path / "public/gallery/emolga-masterset-preview/index.html").exists()
    gallery = (tmp_path / "public/gallery/emolga-masterset/index.html").read_text()
    assert "emolga_1.webp" in gallery and "emolga_11.webp" in gallery
    assert 'data-binder="emolga-masterset"' not in gallery
    assert not digital_binder.validate_public_output(tmp_path / "public", require_public_volumes=True)


def test_crops_are_traced_to_unchanged_archived_photographs():
    manifest = yaml.safe_load((ROOT / "data/binders/emolga-masterset.yaml").read_text())
    images = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]
    archive = ROOT / "docs/evidence/2026-09-24/emolga-masterset"
    assert len(manifest["leaves"]) == 11
    for leaf in manifest["leaves"]:
        assert len(leaf["pockets"]) == 4
        for pocket in leaf["pockets"]:
            if pocket.get("placeholder"):
                assert "card_id" not in pocket
                continue
            record = images[pocket["card_id"]]
            assert record["classification"] == "photo-crop"
            assert record["provider"] == "evidence-crop"
            assert (ROOT / record["source_path"]).is_file()
            assert (ROOT / record["asset_path"]).is_file()
            left, top, right, bottom = record["crop_box"]
            with Image.open(ROOT / record["source_path"]) as source, Image.open(ROOT / record["asset_path"]) as crop:
                assert 0 <= left < right <= source.width
                assert 0 <= top < bottom <= source.height
                assert crop.size == (right - left, bottom - top)
    for source in (ROOT / "static/images/binder/emolga-masterset").iterdir():
        if source.is_file():
            assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256((archive / source.name).read_bytes()).digest()
