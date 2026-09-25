"""Guard the stamped binder draft against invented placements or upgraded printings."""

import hashlib
import re
import subprocess
from pathlib import Path

import yaml

import digital_binder

ROOT = Path(__file__).resolve().parents[1]
ARCHIVE = ROOT / "docs/evidence/2026-09-24/stamped-cards"


def test_evidence_archive_has_verifiable_immutable_inputs():
    lines = (ARCHIVE / "SHA256SUMS").read_text().splitlines()
    assert len(lines) == 9
    for line in lines:
        digest, path = line.split("  ", 1)
        assert hashlib.sha256((ARCHIVE / path).read_bytes()).hexdigest() == digest
    assert (ARCHIVE / "published-pages/stamp_7.jpg").read_bytes() == (
        ROOT / "static/images/binder/stamped-cards/stamp_7.jpg"
    ).read_bytes()


def test_manifest_preserves_observed_pockets_and_does_not_guess_page_eight():
    manifest = yaml.safe_load((ROOT / "data/binders/stamped-cards.yaml").read_text())
    assert manifest["publication_status"] == "draft"
    leaves = manifest["leaves"]
    assert [leaf["physical_leaf"] for leaf in leaves] == list(range(1, 9))
    for page, leaf in enumerate(leaves[:7], start=1):
        assert leaf["kind"] == "cards"
        assert leaf["theme"] == f"Page {page}"
        assert [p["position"] for p in leaf["pockets"]] == list(range(1, 10))
    assert leaves[6]["pockets"][6] == {"position": 7, "empty": True}
    assert leaves[4]["pockets"][0]["card_id"] == "mudsdale-01"
    assert sum("card_id" in p for leaf in leaves[:7] for p in leaf["pockets"]) == 62
    assert leaves[7]["kind"] == "transition"
    assert "pockets" not in leaves[7]
    assert "provisional" in leaves[7]["copy"].lower()
    errors = []
    occupied = digital_binder._validate_volume_manifest(
        ROOT, "stamped-cards", manifest,
        digital_binder.load_registry(ROOT / "docs/card-registry.md"), errors,
    )
    assert errors == []
    assert len(occupied) == 62
    assert all(p["placement"]["status"] == "confirmed"
               for leaf in leaves[:7] for p in leaf["pockets"] if "card_id" in p)
    assert all("physical_state_unknown" not in p["placement"]
               for leaf in leaves[:7] for p in leaf["pockets"] if "card_id" in p)
    volume_manifests = {
        volume_id: yaml.safe_load((ROOT / f"data/binders/{volume_id}.yaml").read_text())
        for volume_id in ("volume-1", "volume-2")
    }
    duplicate_errors = []
    digital_binder._validate_global_duplicates(
        {**volume_manifests, "stamped-cards": manifest}, duplicate_errors,
    )
    assert duplicate_errors == []


def test_page_seven_cites_the_actual_september_replacement_not_march_derivative():
    manifest = yaml.safe_load((ROOT / "data/binders/stamped-cards.yaml").read_text())
    page_seven = manifest["leaves"][6]["pockets"]
    registry = digital_binder.load_registry_module().parse_registry(
        (ROOT / "docs/card-registry.md").read_text()
    )
    by_id = {row["id"]: row for row in registry}
    for pocket in page_seven:
        if pocket.get("empty"):
            continue
        evidence = pocket["placement"]["evidence"]
        assert evidence["source"] == "docs/evidence/2026-09-20/validation/stamped.jpeg"
        assert evidence["type"] == "owner-supplied-photo"
        assert evidence["observed_on"] == "2026-09-20"
        assert by_id[pocket["card_id"]]["first_seen"] == "stamped.jpeg 2026-09-20"


def test_photo_conflicts_are_not_replaced_with_catalogue_fields():
    registry = digital_binder.load_registry(ROOT / "docs/card-registry.md")
    assert registry["pikachu-10"]["number"] == "051/162"
    assert registry["pikachu-10"]["confidence"] != "confirmed"
    assert registry["double-colorless-energy-01"]["language"] == "EN"
    assert registry["bulbasaur-05"]["number"] == "SWSH231"
    assert registry["lucario-03"]["confidence"] == "uncertain"


def test_selected_stamp_variants_use_verified_local_scans_and_unresolved_ones_keep_crops():
    manifest = yaml.safe_load((ROOT / "data/binders/stamped-cards.yaml").read_text())
    images = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]
    cards = [p["card_id"] for leaf in manifest["leaves"][:7] for p in leaf["pockets"] if "card_id" in p]
    selected = {
        "comfey-01": "29910", "oranguru-01": "30433",
        "tyranitar-02": "26207", "bulbasaur-05": "29664", "yanmega-01": "30554",
        "venusaur-01": "43178", "shroomish-01": "5559", "treecko-01": "17857",
        "ivysaur-01": "6518", "grotle-02": "7203", "charmeleon-01": "6526",
        "mudsdale-01": "30561", "passimian-01": "30647", "machamp-01": "51478",
        "passimian-02": "30288", "squirtle-04": "6481", "pikachu-09": "8078",
        "ditto-02": "5888", "piplup-02": "8133", "luvdisc-01": "6606",
        "ekans-01": "6777", "ditto-03": "5889", "shroomish-02": "5326",
        "reshiram-03": "78654", "shellder-01": "6762", "vibrava-01": "6842",
        "pichu-01": "6895", "horsea-02": "6381",
        "houndoom-05": "39116", "glass-trumpet-01": "78387", "dudunsparce-01": "54192",
        "torterra-03": "17322", "mudkip-03": "6496", "dusclops-01": "6548",
        "dialga-02": "7866", "squirtle-05": "6481", "combusken-01": "6398",
        "latios-04": "32495", "combusken-02": "5560", "pikachu-10": "54229",
        "togepi-02": "6757", "slowking-01": "5907",
    }
    tcgdex = {"oricorio-01": "smp-SM19", "delcatty-01": "smp-SM132"}
    for card_id in cards:
        record = images[card_id]
        assert record["asset_path"].startswith("assets/images/cards/")
        assert (ROOT / record["asset_path"]).is_file()
        if card_id in selected:
            assert record["classification"] == "exact"
            assert record["provider"] == "doubleholo"
            assert str(record["upstream_id"]) == selected[card_id]
            assert any(word in record["note"].lower() for word in ("stamp", "logo", "mark"))
        elif card_id in tcgdex:
            assert record["classification"] == "exact"
            assert record["provider"] == "tcgdex"
            assert record["upstream_id"] == tcgdex[card_id]
        else:
            assert record["classification"] == "photo-crop"
            assert record["provider"] == "evidence-crop"
            assert record["source_path"].startswith("docs/evidence/")
            assert (ROOT / record["source_path"]).is_file()
    assert images["solgaleo-01"]["classification"] == "photo-crop"
    assert images["pikachu-08"]["classification"] == "photo-crop"
    registry_rows = digital_binder.load_registry_module().parse_registry(
        (ROOT / "docs/card-registry.md").read_text()
    )
    by_id = {row["id"]: row for row in registry_rows}
    assert all(not re.search(r"page \d+ pocket \d+", by_id[card_id]["notes"], re.I) for card_id in cards)
    registry = digital_binder.load_registry(ROOT / "docs/card-registry.md")
    assert all(registry[card_id]["confidence"] != "confirmed" for card_id in cards)
    errors = []
    digital_binder._validate_images(
        ROOT, {"version": 1, "cards": images}, registry,
        {"stamped-cards": set(cards)}, {"stamped-cards": "draft"}, errors,
    )
    assert errors == []


def test_draft_route_uses_shared_binder_without_replacing_public_gallery(tmp_path):
    result = subprocess.run(
        ["hugo", "--buildDrafts", "--destination", str(tmp_path)],
        cwd=ROOT, capture_output=True, text=True,
    )
    assert result.returncode == 0, result.stderr
    draft = (tmp_path / "gallery/stamped-cards-draft/index.html").read_text()
    public = (tmp_path / "gallery/stamped-cards/index.html").read_text()
    assert 'data-binder="stamped-cards"' in draft
    assert '<details class="stamped-reconciliation">' in draft
    assert 'data-binder-leaf="stamped-08"' in draft
    assert 'data-pocket-position="7"' in draft
    assert 'data-inspector-src=' in draft
    assert 'data-placement-status="pending"' not in draft
    assert 'data-placement-status="confirmed"' in draft
    assert 'data-image-provenance="evidence-crop"' in draft
    assert 'data-image-provenance="doubleholo"' in draft
    assert 'data-image-provenance="tcgdex"' in draft
    assert "Snivy" in draft
    assert "Houndour" in draft and "Mudsdale" not in draft.split("<details", 1)[1].split("</details>", 1)[0]
    assert re.search(r'<img[^>]+src="/images/cards/snivy-04_[^\"]+\.webp"', draft)
    for page in range(1, 8):
        assert f"stamp_{page}.jpg" in public
        assert (tmp_path / f"images/binder/stamped-cards/stamp_{page}.jpg").is_file()
    assert 'data-binder="stamped-cards"' not in public
    binder_markup = draft.split('data-binder="stamped-cards"', 1)[1]
    assert all(src.startswith("/") for src in re.findall(r'<img[^>]+src="([^"]+)"', binder_markup))


def test_production_route_keeps_photographs_and_excludes_draft(tmp_path):
    result = subprocess.run(["hugo", "--destination", str(tmp_path)], cwd=ROOT,
                            capture_output=True, text=True)
    assert result.returncode == 0, result.stderr
    assert not (tmp_path / "gallery/stamped-cards-draft/index.html").exists()
    assert not (tmp_path / "images/binder/stamped-cards-draft/snivy.webp").exists()
    public = (tmp_path / "gallery/stamped-cards/index.html").read_text()
    for page in range(1, 8):
        assert f"stamp_{page}.jpg" in public
        assert (tmp_path / f"images/binder/stamped-cards/stamp_{page}.jpg").is_file()
    assert 'data-binder="stamped-cards"' not in public
