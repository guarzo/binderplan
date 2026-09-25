"""The Emolga binder must never turn pictured placeholders into owned cards."""

import hashlib
import importlib.util
import json
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
                                       "pockets": [{"position": 1, "card_id": "emolga-44",
                                                    "placement": {"status": "confirmed"}}]}]},
    }
    assert digital_binder.validate_transition(previous, current) == []


def test_photo_supported_fallbacks_do_not_call_the_set_uncertain():
    registry = digital_binder.load_registry(ROOT / "docs/card-registry.md")
    images = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]
    for card_id in ("emolga-11", "emolga-19"):
        assert registry[card_id]["confidence"] == "photo"
        assert "set uncertain" not in images[card_id]["note"].lower()
        assert "not checked in hand" in images[card_id]["note"]


def test_stamped_emolga_and_masterset_copy_have_distinct_card_ids():
    stamped = yaml.safe_load((ROOT / "data/binders/stamped-cards.yaml").read_text())
    masterset = yaml.safe_load((ROOT / "data/binders/emolga-masterset.yaml").read_text())
    stamped_ids = {p["card_id"] for leaf in stamped["leaves"] for p in leaf.get("pockets", []) if "card_id" in p}
    masterset_ids = {p["card_id"] for leaf in masterset["leaves"] for p in leaf.get("pockets", []) if "card_id" in p}
    assert "emolga-02" in stamped_ids
    assert "emolga-44" in masterset_ids
    assert stamped_ids.isdisjoint(masterset_ids)


def test_public_binder_preserves_pockets_and_wanted_separation_in_both_builds(tmp_path):
    subprocess.run(["hugo", "--buildDrafts", "--destination", str(tmp_path / "draft")],
                   cwd=ROOT, check=True, capture_output=True, text=True)
    assert not (tmp_path / "draft/gallery/emolga-masterset-preview/index.html").exists()
    html = (tmp_path / "draft/gallery/emolga-masterset/index.html").read_text()
    assert 'data-binder="emolga-masterset"' in html
    assert 'data-pocket-rows="2" data-pocket-columns="2"' in html
    assert re.findall(r'data-binder-leaf="em-(\d+)"', html) == [f"{n:02d}" for n in range(1, 12)]
    assert len(re.findall(r'\bdata-pocket-position="[1-4]"', html)) == 44
    assert len(re.findall(r'\bdata-card-id="emolga-\d{2}"', html)) == 42
    assert len(re.findall(r'data-card-confidence="photo"', html)) == 40
    assert len(re.findall(r'data-card-confidence="uncertain"', html)) == 2
    assert html.count('Printing uncertain</span>') == 2
    assert 'class="emolga-image-note"' in html
    assert html.index('class="emolga-image-note"') < html.index('data-binder="emolga-masterset"')
    assert 'TCGdex or DoubleHolo' in html and 'Select a card for its image source' in html
    assert 'Catalog scan</span>' not in html
    assert html.count('class="pocket-states"') == 2  # Only unresolved identities, never proxy pills.
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
    public_route = tmp_path / "public/gallery/emolga-masterset/index.html"
    gallery = public_route.read_text()
    assert 'data-binder="emolga-masterset"' in gallery
    assert 'data-publication-status="published"' in gallery
    assert 'data-pocket-rows="2" data-pocket-columns="2"' in gallery
    assert len(re.findall(r'\bdata-card-id="emolga-\d{2}"', gallery)) == 42
    assert len(re.findall(r'data-placeholder-wanted="(?:025|081)/BW-P"', gallery)) == 2
    assert 'data-wanted-section' in gallery
    assert 'Draft preview · not published' not in gallery
    assert '<figure class="gallery-item"' not in gallery
    assert not re.search(r'<img[^>]+src="[^"]*/images/binder/emolga-masterset/emolga_\d+\.webp', gallery)
    assert 'href="/gallery/emolga-masterset/"' in (tmp_path / "public/gallery/index.html").read_text()
    assert not digital_binder.validate_public_output(tmp_path / "public", require_public_volumes=True)
    leaked_preview = tmp_path / "public/gallery/emolga-masterset-preview/index.html"
    leaked_preview.parent.mkdir(parents=True)
    leaked_preview.write_text("<h1>Draft leak</h1>")
    assert any("emolga-masterset-preview" in error and "must not be present" in error
               for error in digital_binder.validate_public_output(tmp_path / "public", require_public_volumes=True))
    leaked_preview.unlink()
    public_route.write_text(gallery.replace('</body>', '<img src="/images/binder/emolga-masterset/emolga_1.webp"></body>'))
    assert any("legacy photographed binder image reference" in error and "emolga-masterset/emolga_" in error
               for error in digital_binder.validate_public_output(tmp_path / "public", require_public_volumes=True))
    public_route.write_text(gallery)
    public_route.unlink()
    assert any("emolga-masterset" in error and "missing public" in error
               for error in digital_binder.validate_public_output(tmp_path / "public", require_public_volumes=True))


def test_catalog_matches_visible_card_numbers_without_certifying_variants():
    # Cross-checked against the photographed footers and Bulbapedia's Emolga (TCG) list.
    expected = {
        "emolga-44": ("Emerging Powers", "32/98"),
        "emolga-03": ("BW1", "021/053"),
        "emolga-04": ("McDonald's Collection 2012", "6/12"),
        "emolga-05": ("Noble Victories", "37/101"),
        "emolga-06": ("Victini Formation Deck", "006/021"),
        "emolga-07": ("Next Destinies", "49/99"),
        "emolga-08": ("BKZ", "007/018"),
        "emolga-09": ("Dragons Exalted", "45/124"),
        "emolga-10": ("Dragon Blade", "017/050"),
        "emolga-11": ("Master Deck Build Box EX", "010/046"),
        "emolga-12": ("Legendary Treasures", "49/113"),
        "emolga-13": ("EBB", "041/093"),
        "emolga-14": ("Legendary Treasures", "RC23/RC25"),
        "emolga-15": ("Shiny Collection", "023/020"),
        "emolga-16": ("BW-P", "236/BW-P"),
        "emolga-17": ("Crimson Invasion", "35/111"),
        "emolga-18": ("Awakened Heroes", "019/050"),
        "emolga-19": ("GX Starter Decks", "039/131"),
        "emolga-20": ("Team Up", "46/181"),
        "emolga-21": ("Dark Order", "009/052"),
        "emolga-22": ("Evolving Skies", "057/203"),
        "emolga-23": ("Jet-Black Spirit", "023/070"),
        "emolga-24": ("Silver Tempest", "054/195"),
        "emolga-25": ("Lost Abyss", "038/100"),
        "emolga-26": ("Twilight Masquerade", "069/167"),
        "emolga-27": ("Transformation Mask", "042/101"),
        "emolga-28": ("Black Bolt", "029/086"),
        "emolga-29": ("Black Bolt", "032/086"),
        "emolga-30": ("Black Bolt", "112/086"),
        "emolga-31": ("sv11B", "116/086"),
        "emolga-32": ("XY", "46/146"),
        "emolga-33": ("Collection Y", "023/060"),
        "emolga-34": ("XY", "143/146"),
        "emolga-35": ("Collection Y", "062/060"),
        "emolga-37": ("Team Up", "46/181"),
        "emolga-39": ("Emerging Powers", "32/98"),
        "emolga-40": ("Evolving Skies", "057/203"),
        "emolga-41": ("Victini Formation Deck", "006/021"),
    }
    rows = digital_binder.load_registry(ROOT / "docs/card-registry.md")
    for card_id, (set_name, number) in expected.items():
        assert (rows[card_id]["set"], rows[card_id]["number"]) == (set_name, number), card_id
    assert len(expected) == 38
    assert all(rows[card_id]["confidence"] == "photo" for card_id in expected)
    assert rows["emolga-38"]["confidence"] == rows["emolga-43"]["confidence"] == "photo"
    assert rows["emolga-36"]["confidence"] == "uncertain"  # Chinese stat-style object, not catalogued TCG printing.
    assert rows["emolga-42"]["confidence"] == "uncertain"  # Chinese set unresolved.


def test_reviewed_provider_scan_is_local_and_distinct_from_photo_evidence():
    images = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]
    card = images["emolga-44"]
    assert card["provider"] in {"tcgdex", "doubleholo"}
    assert card["classification"] in {"exact", "proxy"}
    assert card["source_url"].startswith("https://")
    assert card["reviewed"] is True
    assert card["asset_path"] != "assets/images/cards/emolga-masterset-01-1.webp"
    assert (ROOT / card["asset_path"]).is_file()


def test_crops_are_traced_to_unchanged_archived_photographs():
    manifest = yaml.safe_load((ROOT / "data/binders/emolga-masterset.yaml").read_text())
    images = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]
    archive = ROOT / "docs/evidence/2026-09-24/emolga-masterset"
    assert len(manifest["leaves"]) == 11
    provider_ids = set()
    for leaf in manifest["leaves"]:
        assert len(leaf["pockets"]) == 4
        for pocket in leaf["pockets"]:
            if pocket.get("placeholder"):
                assert "card_id" not in pocket
                continue
            record = images[pocket["card_id"]]
            assert (ROOT / record["asset_path"]).is_file()
            if record["provider"] == "evidence-crop":
                assert record["classification"] == "photo-crop"
                assert (ROOT / record["source_path"]).is_file()
                left, top, right, bottom = record["crop_box"]
                with Image.open(ROOT / record["source_path"]) as source, Image.open(ROOT / record["asset_path"]) as crop:
                    assert 0 <= left < right <= source.width
                    assert 0 <= top < bottom <= source.height
                    assert crop.size == (right - left, bottom - top)
            else:
                provider_ids.add(pocket["card_id"])
                assert record["provider"] in {"tcgdex", "doubleholo"}
                assert record["classification"] in {"proxy", "exact"}
                assert record["source_url"].startswith("https://")
                assert record["reviewed"] is True
                if record["classification"] == "proxy":
                    assert record["note"]
    assert len(provider_ids) == 36
    for fallback in ("emolga-11", "emolga-19", "emolga-36", "emolga-38", "emolga-42", "emolga-43"):
        assert images[fallback]["provider"] == "evidence-crop"
    receipts = json.loads((ROOT / "docs/evidence/2026-09-25/emolga-provider-sources/receipts.json").read_text())
    provider_archive = ROOT / "docs/evidence/2026-09-25/emolga-provider-sources"
    assert len(receipts) == 34
    receipt_ids = set()
    for receipt in receipts:
        source = provider_archive / receipt["filename"]
        assert hashlib.sha256(source.read_bytes()).hexdigest() == receipt["sha256"]
        for card_id in receipt["card_ids"]:
            receipt_ids.add(card_id)
            assert images[card_id]["source_url"] == receipt["url"]
    assert receipt_ids == provider_ids
    for source in (ROOT / "static/images/binder/emolga-masterset").iterdir():
        if source.is_file():
            assert hashlib.sha256(source.read_bytes()).digest() == hashlib.sha256((archive / source.name).read_bytes()).digest()
