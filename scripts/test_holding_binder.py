"""Independent guardrails for the photographed, still-owned holding inventory."""

import copy
import hashlib
import importlib.util
import re
from collections import Counter
from pathlib import Path

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/holding_binder.py"
MANIFEST = ROOT / "data/holding-binder.yaml"


def load_validator():
    spec = importlib.util.spec_from_file_location("holding_binder", SCRIPT)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def cards(data):
    for page in data["pages"]:
        for pocket in page["pockets"]:
            if "card" in pocket:
                yield pocket["card"]
    for item in data["top_loaders"]:
        yield item["card"]


def test_manifest_matches_approved_physical_inventory():
    data = yaml.safe_load(MANIFEST.read_text())
    assert [page["id"] for page in data["pages"]] == [str(n) for n in range(7133, 7147)]
    assert [sum("card" in slot for slot in page["pockets"]) for page in data["pages"]] == [
        6, 9, 9, 9, 5, 8, 9, 9, 9, 1, 9, 7, 6, 4
    ]
    assert all([slot["position"] for slot in page["pockets"]] == list(range(1, 10)) for page in data["pages"])
    assert [item["photo_position"] for item in data["top_loaders"]] == [
        "upper-left", "upper-right", "middle-left", "middle-right", "lower-centre"
    ]
    rows = list(cards(data))
    assert len(rows) == len({card["id"] for card in rows}) == 105
    assert Counter(card["status"] for card in rows) == {"Review": 36, "Keeper": 64, "Trade": 5}
    assert Counter((card["status"], card["subsection"]) for card in rows) == {
        ("Review", "EDGE Watches"): 6, ("Review", "Existing-theme EDGE"): 6,
        ("Review", "REDUNDANT"): 24, ("Keeper", "Personal"): 1,
        ("Keeper", "Beautiful Misfits"): 8, ("Keeper", "Heritage"): 28,
        ("Keeper", "Species Studies"): 27, ("Trade", "Actively available"): 5,
    }
    assert {card["id"] for card in rows if card["availability"]} == {
        item["card"]["id"] for item in data["top_loaders"]
    }
    assert {card["observation_ref"] for card in rows if card["observation_ref"].startswith("HB-")} == {
        f"HB-P{page:02d}-{row:02d}" for page, count in enumerate([7, 9, 8, 3, 7, 9, 9, 5, 9, 8, 9, 9, 8], 1)
        for row in range(1, count + 1)
    }
    assert len([card for card in rows if card["observation_ref"].startswith("observed-")]) == 5
    assert {card["image"]["classification"] for card in rows} == {"exact", "photo-crop"}
    assert Counter(card["image"]["classification"] for card in rows) == {"exact": 62, "photo-crop": 43}
    assert all(card["image"]["reviewed"] is True for card in rows)
    assert all(card["image"].get("crop_asset_path", card["image"]["asset_path"]) == f"assets/images/holding/{card['id']}.webp" for card in rows)
    assert all(card.get("language") in ("EN", "JP", "CN") and card.get("set") for card in rows if card["image"]["classification"] == "exact")
    assert all(not str(card.get("number", "")).startswith("No.") for card in rows if card["image"]["classification"] == "exact")
    by_ref = {card["observation_ref"]: card for card in rows}
    assert "glare" in by_ref["HB-P13-01"]["image"]["fallback_crop"]["photo_note"].lower()
    assert "glare" not in by_ref["HB-P13-01"]["image"].get("note", "").lower()
    assert "clips" in by_ref["HB-P06-01"]["image"]["note"].lower()
    assert by_ref["HB-P05-04"]["subsection"] == "Species Studies"
    assert by_ref["HB-P12-06"]["subsection"] == "Species Studies"
    assert "93/130" in by_ref["HB-P09-09"]["name"]
    assert "Manaphy" not in by_ref["HB-P09-09"]["name"]
    assert "139/128" in by_ref["observed-alolan-meowth-139-128"]["name"]
    assert by_ref["HB-P07-07"]["subsection"] == "Beautiful Misfits"
    assert by_ref["HB-P09-09"]["image"]["classification"] == "photo-crop"
    assert by_ref["HB-P01-06"]["image"]["classification"] == "photo-crop"
    assert "DEOXYS stamp" in by_ref["HB-P01-06"]["image"]["note"]
    assert "1st Edition" not in by_ref["HB-P07-08"]["name"]
    assert "Japanese" in by_ref["HB-P02-01"]["name"]
    assert "Japanese" in by_ref["HB-P06-07"]["name"]
    assert by_ref["HB-P11-05"]["image"]["classification"] == "photo-crop"
    assert by_ref["HB-P11-05"]["language"] == "JP"
    assert by_ref["HB-P11-05"]["set"] == "XY8"
    assert "Bulbasaur" in by_ref["HB-P09-06"]["name"] and "Venusaur" not in by_ref["HB-P09-06"]["name"]
    assert by_ref["HB-P03-07"]["name"] == "Groudon ex — Japanese, printing unresolved"
    assert "Butler" in by_ref["HB-P07-07"]["name"]
    assert "Lv.28" in by_ref["HB-P09-02"]["name"]
    for ref, collector_number in (("observed-dedenne-perfect-order", "093/088"),
                                  ("observed-ampharos-chaos-rising", "090/086"),
                                  ("HB-P12-01", "090/128")):
        assert by_ref[ref]["number"] == collector_number
        assert by_ref[ref]["identity_confidence"] == "medium"
        assert "photo" in by_ref[ref]["identity_note"].lower()
    assert "Megalo Cannon" in by_ref["HB-P01-04"]["name"]
    assert "Lv.15" in by_ref["HB-P11-04"]["name"]
    assert by_ref["HB-P11-04"]["image"]["classification"] == "photo-crop"


def test_photograph_order_and_written_owner_decisions_are_independent():
    data = yaml.safe_load(MANIFEST.read_text())
    expected = [
        ["P01-01", "P01-02", None, "P01-03", "P01-05", "P01-07", "P01-06", None, None],
        ["dedenne-perfect-order", "ampharos-chaos-rising", "P03-03", "pikachu-burger", "alolan-meowth-139-128", "P13-03", "P12-08", "P12-09", "P13-01"],
        ["P02-01", "P02-02", "P02-03", "P02-04", "P02-05", "P02-06", "P02-07", "P02-08", "P02-09"],
        ["P03-01", "P03-08", "mightyena-japanese-hp70", "P03-04", "P03-05", "P03-07", "P03-06", "P12-07", "P10-03"],
        ["P04-01", "P04-02", "P04-03", "P10-04", "P10-01", None, None, None, None],
        [None, "P10-06", "P10-05", "P05-07", "P05-05", "P07-07", "P09-07", "P09-04", "P09-06"],
        ["P06-01", "P06-02", "P06-03", "P06-04", "P06-05", "P06-06", "P06-07", "P06-08", "P06-09"],
        ["P07-01", "P07-02", "P07-03", "P07-04", "P07-05", "P07-06", "P05-06", "P07-08", "P07-09"],
        ["P08-01", "P08-02", "P08-03", "P08-04", "P08-05", "P09-01", "P09-02", "P09-08", "P05-01"],
        ["P03-02", None, None, None, None, None, None, None, None],
        ["P11-01", "P11-02", "P11-03", "P11-04", "P11-05", "P11-06", "P11-07", "P11-08", "P01-04"],
        ["P12-01", "P12-02", "P12-03", "P11-09", "P12-05", "P12-06", "P12-04", None, None],
        ["P13-08", "P13-02", "P13-07", "P13-04", "P13-05", "P13-06", None, None, None],
        ["P05-03", "P05-04", "P09-03", "P05-02", None, None, None, None, None],
    ]
    for page, observation_slots in zip(data["pages"], expected):
        assert [slot["card"]["observation_ref"].removeprefix("HB-").removeprefix("observed-") if "card" in slot else None for slot in page["pockets"]] == observation_slots

    checklist = (ROOT / "docs/2026-09-23-holding-sort-completion-checklist.tex").read_text()
    original = dict(re.findall(r"^\\cardrow\{(HB-P\d\d-\d\d)\}\{[^}]*\}\{[^}]*\}\{([^}]*)\}", checklist, re.MULTILINE))
    overrides = {
        "HB-P05-01": "Species Studies", "HB-P05-02": "Species Studies",
        "HB-P05-03": "Species Studies", "HB-P05-04": "Species Studies",
        "HB-P11-05": "Species Studies", "HB-P12-06": "Species Studies",
        "HB-P13-02": "Species Studies", "HB-P13-04": "Species Studies",
        "HB-P13-06": "Species Studies", "HB-P13-07": "Species Studies",
        "HB-P13-08": "Species Studies",
    }
    for card in cards(data):
        ref = card["observation_ref"]
        if ref.startswith("HB-"):
            recommendation = original[ref].replace("Release", "Trade · Actively available")
            if ref == "HB-P12-06":
                recommendation = "Keeper · Species Studies"
            destination = recommendation.split(" · ")
            assert card["status"] == destination[0]
            assert card["subsection"] == overrides.get(ref, destination[1])


def test_validator_checks_archives_and_reproduces_all_crops():
    load_validator().validate(yaml.safe_load(MANIFEST.read_text()), ROOT, check_assets=True)


def test_validator_rejects_asset_path_escape_from_holding_directory():
    data = yaml.safe_load(MANIFEST.read_text())
    card = data["pages"][0]["pockets"][0]["card"]
    card["id"] = "holding-x/../../../../../tmp/escape"
    card["image"]["asset_path"] = f"assets/images/holding/{card['id']}.webp"
    with pytest.raises(ValueError, match="card key|asset path"):
        load_validator().validate(data, ROOT, check_assets=False)


def test_validator_accepts_only_reviewed_matching_canonical_exact_image():
    data = yaml.safe_load(MANIFEST.read_text())
    card = data["pages"][4]["pockets"][0]["card"]  # photographed Hoopa EX
    original_crop = card["image"].get("crop_asset_path", card["image"]["asset_path"])
    canonical = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]["hoopa-02"]
    card["image"].update({
        "classification": "exact", "asset_path": canonical["asset_path"],
        "crop_asset_path": original_crop, "provider": canonical["provider"],
        "upstream_id": canonical["upstream_id"], "source_url": canonical["source_url"],
        "canonical_id": "hoopa-02",
    })
    assert load_validator().validate(data, ROOT, check_assets=False) == 105
    card["image"]["canonical_id"] = "dratini-02"  # reviewed, but a different printing
    with pytest.raises(ValueError, match="canonical|printing"):
        load_validator().validate(data, ROOT, check_assets=False)


def test_catalog_checksum_list_covers_every_archived_original(tmp_path):
    validator = load_validator()
    archive = tmp_path / validator.CATALOG_ARCHIVE
    archive.mkdir(parents=True)
    name = "holding-p01-02.webp"
    original = ROOT / validator.CATALOG_ARCHIVE / name
    archived = archive / name
    archived.write_bytes(original.read_bytes())
    (archive / "SHA256SUMS").write_text(
        f"{hashlib.sha256(archived.read_bytes()).hexdigest()}  {validator.CATALOG_ARCHIVE}/{name}\n"
    )
    (archive / "README.md").write_text("Intake record\n")
    (archive / "unlisted.webp").write_bytes(b"unlisted source")
    with pytest.raises(ValueError, match="catalog archive"):
        validator.verified_catalog(tmp_path, {f"{validator.CATALOG_ARCHIVE}/{name}"})


def test_validator_rejects_photo_crop_with_catalog_provenance():
    data = yaml.safe_load(MANIFEST.read_text())
    image = data["pages"][0]["pockets"][0]["card"]["image"]
    assert image["classification"] == "photo-crop"
    image["provider"] = "doubleholo"
    image["upstream_id"] = "1234"
    with pytest.raises(ValueError, match="photo crop"):
        load_validator().validate(data, ROOT, check_assets=False)


def test_validator_rejects_unsourced_or_unarchived_new_exact():
    data = yaml.safe_load(MANIFEST.read_text())
    card = data["pages"][0]["pockets"][1]["card"]  # Dhelmise
    image = card["image"]
    image.update({"classification": "exact", "crop_asset_path": f"assets/images/holding/{card['id']}.webp",
                  "asset_path": f"assets/images/holding/catalog/{card['id']}.webp",
                  "provider": "doubleholo", "upstream_id": "85053",
                  "source_url": "https://navythaxplgdibyahpqb.supabase.co/storage/v1/object/public/card-images/card_images/85053/primary.webp",
                  "original_path": "docs/evidence/2026-09-24/holding-catalog-images/not-archived.webp"})
    with pytest.raises(ValueError, match="archive|original"):
        load_validator().validate(data, ROOT, check_assets=False)
    del image["source_url"]
    with pytest.raises(ValueError, match="source_url"):
        load_validator().validate(data, ROOT, check_assets=False)


def test_validator_rejects_catalog_image_with_inconsistent_source_or_photo_quality_note():
    data = yaml.safe_load(MANIFEST.read_text())
    image = data["pages"][0]["pockets"][1]["card"]["image"]
    assert image["classification"] == "exact"
    image["source_url"] = "https://example.test/wrong-upstream.webp"
    with pytest.raises(ValueError, match="source_url|provenance"):
        load_validator().validate(data, ROOT, check_assets=False)
    image["source_url"] = "https://navythaxplgdibyahpqb.supabase.co/storage/v1/object/public/card-images/card_images/85053/primary.webp"
    image["note"] = "Photo glare hides the footer."
    with pytest.raises(ValueError, match="photo|glare"):
        load_validator().validate(data, ROOT, check_assets=False)


def test_write_refuses_partial_regeneration_when_late_row_is_invalid(monkeypatch):
    data = yaml.safe_load(MANIFEST.read_text())
    data["top_loaders"][-1]["card"]["observation_ref"] = "HB-P01-01"
    writes = []
    monkeypatch.setattr(Path, "replace", lambda self, target: writes.append(target))
    with pytest.raises(ValueError):
        load_validator().validate(data, ROOT, check_assets=False, write_assets=True)
    assert writes == []


@pytest.mark.parametrize("corruption", ["available", "duplicate", "occupancy", "bounds", "source", "unreviewed"])
def test_validator_rejects_dangerous_mutations(corruption):
    data = copy.deepcopy(yaml.safe_load(MANIFEST.read_text()))
    first = data["pages"][0]["pockets"][0]["card"]
    if corruption == "available":
        first["availability"] = True
    elif corruption == "duplicate":
        data["pages"][0]["pockets"][1]["card"]["id"] = first["id"]
    elif corruption == "occupancy":
        data["pages"][0]["pockets"][3] = {"position": 4, "empty": True}
    elif corruption == "bounds":
        first["image"]["crop_box"] = [0, 0, 5000, 3000]
    elif corruption == "source":
        first["image"]["source_path"] = "https://example.org/image.jpg"
    elif corruption == "unreviewed":
        first["image"]["reviewed"] = False
        first["image"]["note"] = "Not approved"
        first["image"]["quality_note"] = "Not approved"
    with pytest.raises(ValueError):
        load_validator().validate(data, ROOT, check_assets=False)
