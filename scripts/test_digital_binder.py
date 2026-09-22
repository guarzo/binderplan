import importlib.util
import json
import subprocess
from pathlib import Path

from PIL import Image
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


def write_current_generated(root):
    rendered = digital_binder.render_registry_json(
        digital_binder.load_registry(root / "docs" / "card-registry.md")
    )
    (root / "data" / "generated" / "card-registry.json").write_text(
        rendered,
        encoding="utf-8",
    )


def write_image(path, size=(12, 10), color=(64, 128, 192)):
    path.parent.mkdir(parents=True, exist_ok=True)
    Image.new("RGB", size, color).save(path)


class FakeHTTPResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return json.dumps(self.payload).encode("utf-8")


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


def test_tcgdex_language_mapping_includes_traditional_chinese():
    assert digital_binder.TCGDEX_LANGUAGE == {
        "EN": "en", "JP": "ja", "ZH": "zh-tw"
    }


def test_search_tcgdex_maps_language_and_uses_detail_records():
    calls = []

    def fake_opener(request, timeout):
        calls.append((request.full_url, request.headers.get("User-agent"), timeout))
        if request.full_url.endswith("/ja/cards?name=%E3%82%BF%E3%83%96%E3%83%B3%E3%83%8D"):
            return FakeHTTPResponse([{
                "id": "SV11B-156", "localId": "156", "name": "タブンネ",
                "image": None, "set": {"id": "SV11B", "name": "ブラックボルト"},
            }])
        if request.full_url.endswith("/ja/cards/SV11B-156"):
            return FakeHTTPResponse({
                "id": "SV11B-156", "localId": "156", "name": "タブンネ",
                "image": "https://assets.tcgdex.net/ja/sv/sv11b/156",
                "set": {"id": "SV11B", "name": "ブラックボルト"},
            })
        raise AssertionError(f"unexpected URL {request.full_url}")

    row = {
        "id": "audino-01", "card_name": "タブンネ", "language": "JP",
        "set": "sv11B", "number": "156/086", "confidence": "confirmed",
    }

    candidates = digital_binder.search_tcgdex(row, opener=fake_opener)

    assert [candidate["provider_id"] for candidate in candidates] == ["SV11B-156"]
    assert candidates[0]["image_url"] == "https://assets.tcgdex.net/ja/sv/sv11b/156/high.webp"
    assert calls[0][0] == "https://api.tcgdex.net/v2/ja/cards?name=%E3%82%BF%E3%83%96%E3%83%B3%E3%83%8D"
    assert calls[1][0] == "https://api.tcgdex.net/v2/ja/cards/SV11B-156"
    assert all(user_agent and "binderplan" in user_agent for _, user_agent, _ in calls)
    assert all(timeout == 20 for _, _, timeout in calls)


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


def test_rank_candidates_orders_by_identity_score_then_provider_id():
    row = {
        "id": "audino-01", "card_name": "タブンネ", "language": "JP",
        "set": "sv11B", "number": "156/086", "confidence": "confirmed",
    }
    candidates = [
        {"provider_id": "SV11B-999", "name": "タブンネ", "set_id": "SV11B", "local_id": "999"},
        {"provider_id": "SV11B-156B", "name": "タブンネ", "set_id": "SV11B", "local_id": "156"},
        {"provider_id": "SV11B-156A", "name": "タブンネ", "set_id": "SV11B", "local_id": "156"},
    ]

    ranked = digital_binder.rank_candidates(row, candidates)

    assert [candidate["provider_id"] for candidate in ranked] == [
        "SV11B-156A", "SV11B-156B", "SV11B-999",
    ]
    assert ranked[0]["score"] > ranked[2]["score"]


def test_crop_evidence_photo_rejects_out_of_bounds_box(tmp_path):
    source = tmp_path / "source.png"
    target = tmp_path / "crop.webp"
    write_image(source, size=(10, 10))

    try:
        digital_binder.crop_evidence_photo(source, (0, 0, 11, 10), target)
    except ValueError as exc:
        assert "bounds" in str(exc)
    else:
        raise AssertionError("crop should reject out-of-bounds boxes")
    assert not target.exists()


def test_crop_evidence_photo_writes_webp(tmp_path):
    source = tmp_path / "source.png"
    target = tmp_path / "crop.webp"
    write_image(source, size=(10, 10))

    digital_binder.crop_evidence_photo(source, (1, 2, 8, 9), target)

    assert target.exists()
    with Image.open(target) as image:
        assert image.format == "WEBP"
        assert image.size == (7, 7)


def test_external_photo_record_requires_source_url_and_usage_basis(tmp_path):
    root = project_fixture(tmp_path, image_classification="exact")
    images = load_images(root)
    images["cards"]["abra-01"].update({"provider": "local-file"})
    images["cards"]["abra-01"].pop("source_url")
    write_images(root, images)

    errors = digital_binder.validate_project(root)

    assert any("source_url" in error for error in errors)
    assert any("usage_basis" in error for error in errors)


def test_approve_local_cli_requires_http_source_url_and_usage_basis(tmp_path):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    image_file = tmp_path / "local.png"
    write_image(image_file)

    missing_basis = subprocess.run(
        [
            "python3", str(Path(__file__).with_name("manage-card-images.py")),
            "approve-local", "abra-01", "--file", str(image_file),
            "--source-url", "file:///tmp/abra.png", "--usage-basis", "curator-supplied",
            "--classification", "exact",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert missing_basis.returncode == 1
    assert "HTTP(S)" in missing_basis.stderr
    assert not (root / "assets/images/cards/abra-01.webp").exists()


def test_approve_local_cli_writes_asset_and_reviewed_mapping(tmp_path):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    image_file = tmp_path / "local.png"
    write_image(image_file)

    result = subprocess.run(
        [
            "python3", str(Path(__file__).with_name("manage-card-images.py")),
            "approve-local", "abra-01", "--file", str(image_file),
            "--source-url", "https://example.invalid/abra.png",
            "--usage-basis", "Curator-supplied reference photograph.",
            "--classification", "exact", "--note", "Checked against registry.",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (root / "assets/images/cards/abra-01.webp").is_file()
    record = load_images(root)["cards"]["abra-01"]
    assert record["classification"] == "exact"
    assert record["provider"] == "local-file"
    assert record["source_url"] == "https://example.invalid/abra.png"
    assert record["usage_basis"] == "Curator-supplied reference photograph."
    assert record["reviewed"] is True


def test_crop_evidence_cli_restricts_sources_to_evidence_directory(tmp_path):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    source = tmp_path / "outside.png"
    write_image(source)

    result = subprocess.run(
        [
            "python3", str(Path(__file__).with_name("manage-card-images.py")),
            "crop-evidence", "abra-01", "--source", str(source),
            "--box", "0,0,5,5", "--reviewed-on", "2026-09-22",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "docs/evidence" in result.stderr
    assert not (root / "assets/images/cards/abra-01.webp").exists()


def test_crop_evidence_cli_writes_photo_crop_mapping(tmp_path):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    source = root / "docs/evidence/2026-09-22/crop-source.png"
    write_image(source)

    result = subprocess.run(
        [
            "python3", str(Path(__file__).with_name("manage-card-images.py")),
            "crop-evidence", "abra-01", "--source", str(source),
            "--box", "1,1,8,9", "--reviewed-on", "2026-09-22",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert (root / "assets/images/cards/abra-01.webp").is_file()
    record = load_images(root)["cards"]["abra-01"]
    assert record["classification"] == "photo-crop"
    assert record["provider"] == "evidence-crop"
    assert record["source_path"] == "docs/evidence/2026-09-22/crop-source.png"
    assert record["reviewed_on"] == "2026-09-22"


def test_image_manifest_write_validates_before_replacing(tmp_path):
    root = project_fixture(
        tmp_path,
        registry_confidence="uncertain",
        image_classification="missing",
    )
    write_current_generated(root)
    images = load_images(root)
    images["cards"]["abra-01"] = {
        "classification": "exact",
        "asset_path": IMAGE_ASSET,
        "reviewed": True,
        "reviewed_on": "2026-09-22",
        "provider": "tcgdex",
        "upstream_id": "base1-43",
        "source_url": "https://example.invalid/abra.webp",
    }
    image_path = root / IMAGE_ASSET
    image_path.parent.mkdir(parents=True)
    image_path.write_bytes(b"fixture image")

    try:
        digital_binder.write_image_manifest_atomically(root, images)
    except ValueError as exc:
        assert "exact" in str(exc) and "uncertain" in str(exc)
    else:
        raise AssertionError("invalid image manifest should be rejected")

    assert load_images(root)["cards"]["abra-01"]["classification"] == "missing"


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


def test_check_reports_malformed_registry_without_traceback(tmp_path, capsys):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text("not a registry\n", encoding="utf-8")

    rc = digital_binder.main(["--check", "--root", str(root)])

    output = capsys.readouterr().out
    assert rc == 1
    assert "registry validation failed" in output


def test_check_reports_missing_registry_without_traceback(tmp_path, capsys):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").unlink()

    rc = digital_binder.main(["--check", "--root", str(root)])

    output = capsys.readouterr().out
    assert rc == 1
    assert "registry validation failed" in output
    assert "card-registry.md" in output


def test_duplicate_occupied_placements_are_rejected_across_volumes(tmp_path):
    root = project_fixture(tmp_path)
    volume_two = load_volume(root, "volume-2")
    volume_two["leaves"] = [{
        "id": "volume-2-leaf-1",
        "kind": "cards",
        "physical_leaf": 1,
        "chapter": "Fixture Chapter",
        "chapter_order": 1,
        "theme": "Fixture Theme",
        "pockets": valid_pockets("abra-01"),
    }]
    write_volume(root, volume_two)

    errors = digital_binder.validate_project(root)

    assert any("duplicate occupied placement" in error and "volume-1" in error
               and "volume-2" in error for error in errors)


def test_card_leaf_requires_core_metadata(tmp_path):
    root = project_fixture(tmp_path)
    volume = load_volume(root)
    leaf = volume["leaves"][0]
    leaf["chapter"] = ""
    leaf["theme"] = 123
    leaf["chapter_order"] = 0
    leaf["theme_page"] = 0
    write_volume(root, volume)

    errors = digital_binder.validate_project(root)

    assert any("chapter" in error and "nonempty string" in error for error in errors)
    assert any("theme" in error and "nonempty string" in error for error in errors)
    assert any("chapter_order" in error and "positive integer" in error for error in errors)
    assert any("theme_page" in error and "positive integer" in error for error in errors)


def test_single_page_card_leaf_may_omit_theme_page(tmp_path):
    root = project_fixture(tmp_path)
    volume = load_volume(root)
    del volume["leaves"][0]["theme_page"]
    write_volume(root, volume)

    assert digital_binder.validate_project(root) == []


def test_load_previous_manifests_uses_git_show_for_each_volume(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, check, capture_output, text, cwd):
        calls.append((command, check, capture_output, text, cwd))
        volume_id = command[2].split("/")[-1].removesuffix(".yaml")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=yaml.safe_dump(project_manifest()[volume_id]),
            stderr="",
        )

    monkeypatch.setattr(digital_binder.subprocess, "run", fake_run)
    errors = []

    manifests = digital_binder._load_previous_manifests(tmp_path, "main", errors)

    assert errors == []
    assert manifests["volume-1"]["volume_id"] == "volume-1"
    assert [call[0] for call in calls] == [
        ["git", "show", "main:data/binders/volume-1.yaml"],
        ["git", "show", "main:data/binders/volume-2.yaml"],
    ]
    assert all(call[4] == tmp_path for call in calls)


def test_validate_project_rejects_unsafe_previous_ref_without_git(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("git should not be called for an unsafe ref")

    monkeypatch.setattr(digital_binder.subprocess, "run", fail_if_called)

    errors = digital_binder.validate_project(root, previous_ref="-bad")

    assert any("invalid previous_ref" in error and "-bad" in error for error in errors)


def test_validate_project_skips_absent_previous_manifest_but_keeps_current_validation(tmp_path, monkeypatch):
    root = project_fixture(tmp_path, pockets=[confirmed_pocket("abra-01")])

    def missing_manifest(command, check, capture_output, text, cwd):
        raise subprocess.CalledProcessError(128, command, stderr="not found")

    monkeypatch.setattr(digital_binder.subprocess, "run", missing_manifest)

    errors = digital_binder.validate_project(root, previous_ref="main")

    assert any("exactly 9 pockets" in error for error in errors)
    assert not any("previous" in error for error in errors)


def test_check_passes_previous_ref_to_git_loader(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    calls = []

    def fake_run(command, check, capture_output, text, cwd):
        calls.append(command)
        volume_id = command[2].split("/")[-1].removesuffix(".yaml")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=yaml.safe_dump(project_manifest()[volume_id]),
            stderr="",
        )

    monkeypatch.setattr(digital_binder.subprocess, "run", fake_run)

    rc = digital_binder.main(["--check", "--root", str(root), "--previous-ref", "main"])

    assert rc == 0
    assert calls == [
        ["git", "show", "main:data/binders/volume-1.yaml"],
        ["git", "show", "main:data/binders/volume-2.yaml"],
    ]


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
