import importlib.util
import json
from pathlib import Path

import yaml

spec = importlib.util.spec_from_file_location(
    "digital_binder", Path(__file__).parent / "digital_binder.py"
)
digital_binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digital_binder)


EVIDENCE_SOURCE = (
    "docs/evidence/2026-09-22/digital-binder-migration/"
    "published-gallery/volume-1/example.webp"
)
IMAGE_ASSET = "static/images/cards/abra-01.webp"


def confirmed_pocket(card_id):
    return {
        "position": 1,
        "card_id": card_id,
        "placement": {
            "status": "confirmed",
            "evidence": {
                "type": "published-photo",
                "source": EVIDENCE_SOURCE,
                "observed_on": "2026-08-01",
            },
        },
    }


def pending_pocket(card_id, observed_card_id=None, physical_state_unknown=False):
    pocket = {
        "position": 1,
        "card_id": card_id,
        "placement": {
            "status": "pending",
            "evidence": {
                "type": "proposal",
                "source": "docs/ledger.md",
                "observed_on": "2026-09-22",
            },
        },
    }
    if observed_card_id is not None:
        pocket["placement"]["observed_card_id"] = observed_card_id
    if physical_state_unknown:
        pocket["placement"]["physical_state_unknown"] = True
        pocket["placement"]["note"] = "No earlier pocket observation exists."
    return pocket


def empty_pocket(position=1):
    return {"position": position, "empty": True}


def valid_pockets(card_id="abra-01"):
    return [confirmed_pocket(card_id)] + [empty_pocket(position) for position in range(2, 10)]


def registry_doc(confidence="confirmed", set_="Base Set", number="43/102"):
    return (
        "# Card registry\n\n## Registry\n\n"
        "| id | species | card_name | language | set | number | confidence | first_seen | notes |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        f"| abra-01 | Abra | Abra | EN | {set_} | {number} | {confidence} | "
        "page.webp 2026-08-01 | |\n"
        "| kadabra-01 | Kadabra | Kadabra | EN | Base Set | 32/102 | confirmed | "
        "page.webp 2026-08-01 | |\n"
        "| alakazam-01 | Alakazam | Alakazam | EN | Base Set | 1/102 | confirmed | "
        "page.webp 2026-08-01 | |\n"
    )


def project_fixture(tmp_path, pockets=None, transition_pockets=None,
                    registry_confidence="confirmed", image_classification="missing",
                    publication_status="draft", reviewed=True):
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs" / "card-registry.md").write_text(
        registry_doc(confidence=registry_confidence),
        encoding="utf-8",
    )
    evidence_path = tmp_path / EVIDENCE_SOURCE
    evidence_path.parent.mkdir(parents=True)
    evidence_path.write_bytes(b"fixture evidence")

    generated = tmp_path / "data" / "generated"
    generated.mkdir(parents=True)
    generated.joinpath("card-registry.json").write_text(
        json.dumps({"abra-01": {"id": "abra-01"}}, indent=2) + "\n",
        encoding="utf-8",
    )

    binder_dir = tmp_path / "data" / "binders"
    binder_dir.mkdir(parents=True)
    leaves = [{
        "id": "leaf-1",
        "kind": "cards",
        "physical_leaf": 1,
        "chapter": "Fixture Chapter",
        "chapter_order": 1,
        "theme": "Fixture Theme",
        "theme_page": 1,
        "pockets": valid_pockets() if pockets is None else pockets,
    }]
    if transition_pockets is not None:
        transition = {
            "id": "transition-1",
            "kind": "transition",
            "physical_leaf": 2,
            "role": "chapter",
            "heading": "Fixture transition",
        }
        if transition_pockets is not None:
            transition["pockets"] = transition_pockets
        leaves.append(transition)
    volume_one = {
        "version": 1,
        "volume_id": "volume-1",
        "publication_status": publication_status,
        "leaves": leaves,
    }
    volume_two = {
        "version": 1,
        "volume_id": "volume-2",
        "publication_status": "draft",
        "leaves": [],
    }
    binder_dir.joinpath("volume-1.yaml").write_text(
        yaml.safe_dump(volume_one, sort_keys=False),
        encoding="utf-8",
    )
    binder_dir.joinpath("volume-2.yaml").write_text(
        yaml.safe_dump(volume_two, sort_keys=False),
        encoding="utf-8",
    )

    image_record = {
        "classification": image_classification,
        "asset_path": "",
        "reviewed": reviewed,
        "reviewed_on": "2026-09-22" if reviewed else "",
    }
    if image_classification != "missing":
        image_record.update({
            "asset_path": IMAGE_ASSET,
            "provider": "fixture",
            "upstream_id": "fixture-abra-01",
            "source_url": "https://example.invalid/abra-01.webp",
        })
        image_path = tmp_path / IMAGE_ASSET
        image_path.parent.mkdir(parents=True)
        image_path.write_bytes(b"fixture image")
    if image_classification == "proxy":
        image_record["note"] = "Fixture proxy differs from the owned printing."
    tmp_path.joinpath("data", "card-images.yaml").write_text(
        yaml.safe_dump({"version": 1, "cards": {"abra-01": image_record}}, sort_keys=False),
        encoding="utf-8",
    )
    return tmp_path


def load_volume(root, volume_id="volume-1"):
    return yaml.safe_load(
        (root / "data" / "binders" / f"{volume_id}.yaml").read_text(encoding="utf-8")
    )


def write_volume(root, volume):
    (root / "data" / "binders" / f"{volume['volume_id']}.yaml").write_text(
        yaml.safe_dump(volume, sort_keys=False),
        encoding="utf-8",
    )


def load_images(root):
    return yaml.safe_load((root / "data" / "card-images.yaml").read_text(encoding="utf-8"))


def write_images(root, images):
    (root / "data" / "card-images.yaml").write_text(
        yaml.safe_dump(images, sort_keys=False),
        encoding="utf-8",
    )


def project_manifest(card_id="abra-01", status="confirmed", observed_card_id=None):
    pocket = confirmed_pocket(card_id)
    if status == "pending":
        pocket = pending_pocket(card_id, observed_card_id=observed_card_id)
    return {
        "volume-1": {
            "version": 1,
            "volume_id": "volume-1",
            "publication_status": "draft",
            "leaves": [{
                "id": "leaf-1",
                "kind": "cards",
                "physical_leaf": 1,
                "chapter": "Fixture Chapter",
                "chapter_order": 1,
                "theme": "Fixture Theme",
                "theme_page": 1,
                "pockets": [pocket] + [empty_pocket(position) for position in range(2, 10)],
            }],
        },
        "volume-2": {
            "version": 1,
            "volume_id": "volume-2",
            "publication_status": "draft",
            "leaves": [],
        },
    }


def confirmed_project(tmp_path, card_id):
    return project_manifest(card_id=card_id, status="confirmed")


def pending_project(tmp_path, card_id, observed_card_id):
    return project_manifest(card_id=card_id, status="pending", observed_card_id=observed_card_id)


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


def test_unknown_card_id_is_rejected(tmp_path):
    root = project_fixture(tmp_path, pockets=valid_pockets("missing-01"))
    errors = digital_binder.validate_project(root)
    assert any("unknown card_id" in error and "missing-01" in error for error in errors)


def test_duplicate_occupied_placements_are_rejected(tmp_path):
    duplicate = confirmed_pocket("abra-01")
    duplicate["position"] = 2
    root = project_fixture(
        tmp_path,
        pockets=[confirmed_pocket("abra-01"), duplicate]
                + [empty_pocket(position) for position in range(3, 10)],
    )
    errors = digital_binder.validate_project(root)
    assert any("duplicate occupied placement" in error and "abra-01" in error
               for error in errors)


def test_non_missing_image_requires_existing_asset(tmp_path):
    root = project_fixture(tmp_path, image_classification="photo-crop")
    (root / IMAGE_ASSET).unlink()
    errors = digital_binder.validate_project(root)
    assert any("missing asset" in error and IMAGE_ASSET in error for error in errors)


def test_proxy_image_requires_note(tmp_path):
    root = project_fixture(tmp_path, image_classification="proxy")
    images = load_images(root)
    del images["cards"]["abra-01"]["note"]
    write_images(root, images)
    errors = digital_binder.validate_project(root)
    assert any("proxy" in error and "note" in error for error in errors)


def test_missing_image_requires_empty_asset_path(tmp_path):
    root = project_fixture(tmp_path)
    images = load_images(root)
    images["cards"]["abra-01"]["asset_path"] = IMAGE_ASSET
    write_images(root, images)
    errors = digital_binder.validate_project(root)
    assert any("missing" in error and "asset_path" in error for error in errors)


def test_invalid_transition_role_is_rejected(tmp_path):
    root = project_fixture(tmp_path, transition_pockets=[])
    volume = load_volume(root)
    volume["leaves"][1].pop("pockets")
    volume["leaves"][1]["role"] = "intermission"
    write_volume(root, volume)
    errors = digital_binder.validate_project(root)
    assert any("transition role" in error and "intermission" in error for error in errors)


def test_physical_leaf_numbers_must_be_contiguous(tmp_path):
    root = project_fixture(tmp_path, transition_pockets=[])
    volume = load_volume(root)
    volume["leaves"][1].pop("pockets")
    volume["leaves"][1]["physical_leaf"] = 3
    write_volume(root, volume)
    errors = digital_binder.validate_project(root)
    assert any("contiguous physical_leaf" in error for error in errors)


def test_draft_volume_permits_unreviewed_image(tmp_path):
    root = project_fixture(tmp_path, publication_status="draft", reviewed=False)
    errors = digital_binder.validate_project(root)
    assert not any("unreviewed" in error for error in errors)


def test_exact_image_requires_distinguishing_registry_fields(tmp_path):
    root = project_fixture(tmp_path, image_classification="exact")
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    errors = digital_binder.validate_project(root)
    assert any("exact" in error and "set and number" in error for error in errors)


def test_exact_image_allows_confirmed_unnumbered_printing_with_identity_basis(tmp_path):
    root = project_fixture(tmp_path, image_classification="exact")
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Promo", number=""),
        encoding="utf-8",
    )
    images = load_images(root)
    images["cards"]["abra-01"]["identity_basis"] = "Confirmed unnumbered promo stamp."
    write_images(root, images)
    assert digital_binder.validate_project(root) == []


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
