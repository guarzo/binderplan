import argparse
import hashlib
import importlib.util
import json
import re
import shutil
from http.client import IncompleteRead
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs

from PIL import Image
import yaml
import pytest

spec = importlib.util.spec_from_file_location(
    "digital_binder", Path(__file__).parent / "digital_binder.py"
)
digital_binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digital_binder)
sys.modules["digital_binder"] = digital_binder

manage_spec = importlib.util.spec_from_file_location(
    "manage_card_images", Path(__file__).parent / "manage-card-images.py"
)
manage_card_images = importlib.util.module_from_spec(manage_spec)
manage_spec.loader.exec_module(manage_card_images)


EVIDENCE_SOURCE = (
    "docs/evidence/2026-09-22/digital-binder-migration/"
    "published-gallery/volume-1/example.webp"
)
IMAGE_ASSET = "assets/images/cards/abra-01.webp"


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
    (tmp_path / "docs" / "ledger.md").write_text(
        "# Fixture ledger\n",
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


class FakeBinaryHTTPResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def test_remote_candidate_image_download_failure_has_controlled_context(tmp_path, monkeypatch):
    image_url = "https://example.invalid/card.webp"

    def fail_download(request, timeout):
        raise IncompleteRead(b"partial", 20)

    monkeypatch.setattr(manage_card_images, "urlopen", fail_download)
    args = argparse.Namespace(card_id="abra-01", classification="exact", note=None)

    try:
        manage_card_images._approve_remote_candidate(
            tmp_path, args, {"image_url": image_url}, {}, "tcgdex"
        )
    except ValueError as exc:
        assert "tcgdex" in str(exc)
        assert image_url in str(exc)
        assert "download failed" in str(exc)
    else:
        raise AssertionError("truncated image download should fail with controlled context")


def image_bytes(format_="PNG", size=(12, 10), color=(64, 128, 192)):
    from io import BytesIO

    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format=format_)
    return buffer.getvalue()


def write_candidate_cache(root, card_id, candidates):
    path = root / "tmp/digital-binder-review/candidates" / f"{card_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    registry = digital_binder.load_registry(root / "docs" / "card-registry.md").get(card_id, {})
    path.write_text(
        json.dumps({
            "card_id": card_id,
            "provider": "tcgdex",
            "registry": registry,
            "candidates": candidates,
        }),
        encoding="utf-8",
    )


def write_doubleholo_candidate_cache(root, card_id, candidates):
    path = root / "tmp/digital-binder-review/doubleholo" / f"{card_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"card_id": card_id, "registry": {}, "candidates": candidates}),
        encoding="utf-8",
    )


def doubleholo_cached_candidate(
        name="Abra", set_name="Pokemon Base Set", number="43", language="english",
        image_url="https://supabase.example/abra.png", object_id="dh-43"):
    return {
        "candidate_index": 0,
        "provider_id": object_id,
        "image_url": image_url,
        "exact_identity_match": False,
        "original": {
            "objectID": object_id,
            "name": name,
            "set_name": set_name,
            "number": number,
            "language": language,
            "image_url": image_url,
            "image_url_small": None,
        },
    }


def doubleholo_live_object(
        name="Abra", set_name="Pokemon Base Set", number="43", language="english",
        image_url="https://supabase.example/abra.png", object_id="dh-43"):
    return {
        "objectID": object_id,
        "name": name,
        "set_name": set_name,
        "number": number,
        "language": language,
        "image_url": image_url,
        "image_url_small": None,
    }


def doubleholo_object_url(object_id="dh-43"):
    return f"https://w5sf479zkl-dsn.algolia.net/1/indexes/production_cards/{object_id}"


def tcgdex_live_object(
        name="Abra", set_id="base1", set_name="Base Set", local_id="43",
        image_url="https://assets.tcgdex.net/en/base/base1/43", object_id="base1-43"):
    return {
        "id": object_id,
        "localId": local_id,
        "name": name,
        "image": image_url,
        "set": {"id": set_id, "name": set_name},
    }


def tcgdex_object_url(object_id="base1-43", language="en"):
    return f"https://api.tcgdex.net/v2/{language}/cards/{object_id}"


def patch_doubleholo_live_object(monkeypatch, **kwargs):
    def fake_fetch(object_id, opener=None):
        return doubleholo_live_object(object_id=object_id, **kwargs)

    monkeypatch.setattr(manage_card_images, "_fetch_doubleholo_object", fake_fetch)


def patch_doubleholo_live_candidate(monkeypatch, candidate):
    original = dict(candidate.get("original") or {})

    def fake_fetch(object_id, opener=None):
        fetched = dict(original)
        fetched["objectID"] = object_id
        return fetched

    monkeypatch.setattr(manage_card_images, "_fetch_doubleholo_object", fake_fetch)


def seed_existing_proxy_image(root):
    asset_path = root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp"
    write_image(asset_path, color=(9, 8, 7))
    images = load_images(root)
    images["cards"]["abra-01"] = {
        "classification": "proxy",
        "asset_path": str(manage_card_images.CARD_ASSET_DIR / "abra-01.webp"),
        "reviewed": True,
        "reviewed_on": "2026-09-22",
        "provider": "tcgdex",
        "upstream_id": "old-proxy",
        "source_url": "https://example.invalid/old.webp",
        "note": "Existing reviewed proxy.",
    }
    write_images(root, images)
    return (
        (root / "data/card-images.yaml").read_bytes(),
        asset_path.read_bytes(),
        asset_path,
    )


def approve_args(card_id="abra-01", candidate_index=0, classification="exact", note=None,
                 confirm_identity=False, confirm_unnumbered=False, identity_basis=None):
    return argparse.Namespace(
        card_id=card_id,
        candidate_index=candidate_index,
        classification=classification,
        note=note,
        confirm_identity=confirm_identity,
        confirm_unnumbered=confirm_unnumbered,
        identity_basis=identity_basis,
    )


def project_manifest(card_id="abra-01", status="confirmed", observed_card_id=None,
                     pockets=None, leaves=None):
    pocket = confirmed_pocket(card_id)
    if status == "pending":
        pocket = pending_pocket(card_id, observed_card_id=observed_card_id)
    if pockets is None:
        pockets = [pocket] + [empty_pocket(position) for position in range(2, 10)]
    if leaves is None:
        leaves = [{
            "id": "leaf-1",
            "kind": "cards",
            "physical_leaf": 1,
            "chapter": "Fixture Chapter",
            "chapter_order": 1,
            "theme": "Fixture Theme",
            "theme_page": 1,
            "pockets": pockets,
        }]
    return {
        "volume-1": {
            "version": 1,
            "volume_id": "volume-1",
            "publication_status": "draft",
            "leaves": leaves,
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


def test_search_tcgdex_keeps_summary_when_one_detail_fetch_fails():
    def fake_opener(request, timeout):
        if request.full_url.endswith("/en/cards?name=Abra"):
            return FakeHTTPResponse([
                {
                    "id": "base1-43", "localId": "43", "name": "Abra",
                    "image": None, "set": {"id": "base1", "name": "Base Set"},
                },
                {
                    "id": "base1-44", "localId": "44", "name": "Abra",
                    "image": None, "set": {"id": "base1", "name": "Base Set"},
                },
            ])
        if request.full_url.endswith("/en/cards/base1-43"):
            raise OSError("404 not found")
        if request.full_url.endswith("/en/cards/base1-44"):
            return FakeHTTPResponse({
                "id": "base1-44", "localId": "44", "name": "Abra",
                "image": "https://assets.tcgdex.net/en/base/base1/44",
                "set": {"id": "base1", "name": "Base Set"},
            })
        raise AssertionError(f"unexpected URL {request.full_url}")

    row = {
        "id": "abra-01", "card_name": "Abra", "language": "EN",
        "set": "Base Set", "number": "43/102", "confidence": "confirmed",
    }

    candidates = digital_binder.search_tcgdex(row, opener=fake_opener)

    assert [candidate["provider_id"] for candidate in candidates] == ["base1-43", "base1-44"]
    assert candidates[0]["image_url"] is None
    assert "404 not found" in candidates[0]["detail_error"]
    assert "detail_error" not in candidates[1]
    assert candidates[1]["image_url"] == "https://assets.tcgdex.net/en/base/base1/44/high.webp"


def test_search_tcgdex_rejects_malformed_top_level_json_envelope():
    def malformed_opener(request, timeout):
        return FakeHTTPResponse({"error": "provider rate limit"})

    row = {
        "id": "abra-01", "card_name": "Abra", "language": "EN",
        "set": "Base Set", "number": "43/102", "confidence": "confirmed",
    }

    try:
        digital_binder.search_tcgdex(row, opener=malformed_opener)
    except ValueError as exc:
        assert "TCGdex search returned malformed results envelope" in str(exc)
    else:
        raise AssertionError("malformed TCGdex search envelopes must not become no-hit results")


def test_search_tcgdex_marks_every_failed_detail_explicitly():
    def fake_opener(request, timeout):
        if request.full_url.endswith("/en/cards?name=Abra"):
            return FakeHTTPResponse([
                {"id": "base1-43", "localId": "43", "name": "Abra"},
                {"id": "base1-44", "localId": "44", "name": "Abra"},
            ])
        if request.full_url.endswith(("/en/cards/base1-43", "/en/cards/base1-44")):
            raise OSError("detail service unavailable")
        raise AssertionError(f"unexpected URL {request.full_url}")

    row = {
        "id": "abra-01", "card_name": "Abra", "language": "EN",
        "set": "Base Set", "number": "43/102", "confidence": "confirmed",
    }

    candidates = digital_binder.search_tcgdex(row, opener=fake_opener)

    assert [candidate["provider_id"] for candidate in candidates] == ["base1-43", "base1-44"]
    assert all(candidate["image_url"] is None for candidate in candidates)
    assert all("detail service unavailable" in candidate["detail_error"] for candidate in candidates)


def test_search_doubleholo_posts_public_algolia_query_shape():
    calls = []

    def fake_opener(request, timeout):
        calls.append((request, timeout))
        body = json.loads(request.data.decode("utf-8"))
        params = parse_qs(body["requests"][0]["params"])
        assert body["requests"][0]["indexName"] == "production_cards"
        assert params["query"] == ["Dragonite 149 Mystery Fossils"]
        assert int(params["hitsPerPage"][0]) >= 80
        assert params["attributesToRetrieve"] == [
            "objectID,name,set_name,number,language,image_url,image_url_small"
        ]
        return FakeHTTPResponse({"results": [{"hits": []}]})

    row = {
        "id": "dragonite-01", "species": "Dragonite", "card_name": "カイリュー",
        "language": "JP", "set": "Mystery of the Fossils", "number": "No.149",
    }

    assert digital_binder.search_doubleholo(row, opener=fake_opener) == []

    request, timeout = calls[0]
    assert request.full_url == "https://w5sf479zkl-dsn.algolia.net/1/indexes/*/queries"
    assert request.get_method() == "POST"
    assert request.headers["X-algolia-application-id"] == "W5SF479ZKL"
    assert request.headers["X-algolia-api-key"] == "50fdd89ab8d777151bc000bba6097357"
    assert "Cookie" not in request.headers
    assert timeout == 20


def test_search_doubleholo_query_ignores_accented_pokemon_set_prefix():
    queries = []

    def fake_opener(request, timeout):
        body = json.loads(request.data.decode("utf-8"))
        queries.append(parse_qs(body["requests"][0]["params"])["query"][0])
        return FakeHTTPResponse({"results": [{"hits": []}]})

    row = {
        "id": "ampharos-01", "species": "Ampharos", "card_name": "ミカンのデンリュウ",
        "language": "JP", "set": "Pokémon VS", "number": "031/141",
    }

    digital_binder.search_doubleholo(row, opener=fake_opener)

    assert queries == ["Ampharos 31 VS"]


def test_normalize_doubleholo_candidate_preserves_original_fields_and_normalizes_identity():
    candidate = digital_binder.normalize_doubleholo_candidate({
        "objectID": "dh-123",
        "name": "Dark Espeon",
        "set_name": "Pokemon Japanese Neo 4 Darkness, and to Light",
        "number": "196",
        "language": "japanese",
        "image_url": "https://supabase.example/card.webp",
        "image_url_small": "https://supabase.example/card-small.webp",
    })

    assert candidate["provider"] == "doubleholo"
    assert candidate["provider_id"] == "dh-123"
    assert candidate["name"] == "Dark Espeon"
    assert candidate["set_name"] == "Pokemon Japanese Neo 4 Darkness, and to Light"
    assert candidate["local_id"] == "196"
    assert candidate["language"] == "JP"
    assert candidate["normalized_set"] == "neo4darknesstolight"
    assert candidate["normalized_number"] == "196"
    assert candidate["original"] == {
        "objectID": "dh-123",
        "name": "Dark Espeon",
        "set_name": "Pokemon Japanese Neo 4 Darkness, and to Light",
        "number": "196",
        "language": "japanese",
        "image_url": "https://supabase.example/card.webp",
        "image_url_small": "https://supabase.example/card-small.webp",
    }


def test_normalize_doubleholo_candidate_maps_chinese_variants_to_registry_zh():
    labels = [
        "chinese",
        "chinese_traditional",
        "chinese traditional",
        "chinese-traditional",
        "traditional_chinese",
        "traditional chinese",
        "chinese_simplified",
        "chinese simplified",
        "chinese-simplified",
        "simplified_chinese",
        "simplified chinese",
    ]

    for label in labels:
        candidate = digital_binder.normalize_doubleholo_candidate({
            "objectID": f"dh-{label}",
            "name": "Cubone",
            "set_name": "Pokemon Chinese Gem Pack 3",
            "number": "407",
            "language": label,
            "image_url": "https://supabase.example/cubone.webp",
        })

        assert candidate["language"] == "ZH"


def test_rank_doubleholo_candidates_accepts_traditional_chinese_exact_identity():
    row = {
        "id": "cubone-01", "species": "Cubone", "card_name": "卡拉卡拉",
        "language": "ZH", "set": "Gem Pack 3", "number": "407",
    }
    candidate = digital_binder.normalize_doubleholo_candidate({
        "objectID": "49932",
        "name": "Cubone",
        "set_name": "Pokemon Chinese Gem Pack 3",
        "number": "407",
        "language": "chinese_traditional",
        "image_url": "https://supabase.example/cubone.webp",
    })

    ranked = digital_binder.rank_doubleholo_candidates(row, [candidate])

    assert ranked[0]["language"] == "ZH"
    assert ranked[0]["language_match"] is True
    assert ranked[0]["exact_identity_match"] is True


def test_rank_doubleholo_candidates_scores_identity_components_without_approval():
    row = {
        "id": "espeon-01", "species": "Espeon", "card_name": "わるいエーフィ",
        "language": "JP", "set": "Darkness, and to Light", "number": "No.196",
    }
    candidates = [
        digital_binder.normalize_doubleholo_candidate({
            "objectID": "wrong-language", "name": "Dark Espeon",
            "set_name": "Pokemon Darkness, and to Light",
            "number": "196", "language": "english",
            "image_url": "https://example.invalid/wrong.webp",
        }),
        digital_binder.normalize_doubleholo_candidate({
            "objectID": "exact", "name": "Dark Espeon",
            "set_name": "Pokemon Japanese Darkness, and to Light",
            "number": "196", "language": "japanese",
            "image_url": "https://example.invalid/exact.webp",
        }),
        digital_binder.normalize_doubleholo_candidate({
            "objectID": "wrong-number", "name": "Dark Espeon",
            "set_name": "Pokemon Japanese Darkness, and to Light",
            "number": "197", "language": "japanese",
            "image_url": "https://example.invalid/wrong-number.webp",
        }),
    ]

    ranked = digital_binder.rank_doubleholo_candidates(row, candidates)

    assert [candidate["provider_id"] for candidate in ranked] == [
        "exact", "wrong-number", "wrong-language",
    ]
    assert ranked[0]["number_match"] is True
    assert ranked[0]["language_match"] is True
    assert ranked[0]["set_match"] is True
    assert ranked[0]["name_match"] is True
    assert ranked[0]["exact_identity_match"] is True
    assert ranked[0]["review_state"] == "candidate"
    assert "approved" not in ranked[0].values()
    assert ranked[1]["exact_identity_match"] is False
    assert ranked[2]["exact_identity_match"] is False


def test_doubleholo_exact_identity_requires_normalized_set_equality_not_substring():
    row = {
        "id": "promo-01", "species": "Umbreon", "card_name": "Umbreon",
        "language": "EN", "set": "Promo", "number": "60",
    }
    candidate = digital_binder.normalize_doubleholo_candidate({
        "objectID": "stamped-promo", "name": "Umbreon",
        "set_name": "Pokemon Stamped Promo", "number": "60", "language": "english",
        "image_url": "https://example.invalid/umbreon.webp",
    })

    ranked = digital_binder.rank_doubleholo_candidates(row, [candidate])

    assert ranked[0]["number_match"] is True
    assert ranked[0]["language_match"] is True
    assert ranked[0]["set_match"] is False
    assert ranked[0]["exact_identity_match"] is False


def test_doubleholo_exact_identity_requires_name_match_not_just_number_language_and_set():
    row = {
        "id": "abra-01", "species": "Abra", "card_name": "Abra",
        "language": "EN", "set": "Base Set", "number": "43/102",
    }
    candidate = digital_binder.normalize_doubleholo_candidate({
        "objectID": "wrong-species", "name": "Kadabra",
        "set_name": "Pokemon Base Set", "number": "43", "language": "english",
        "image_url": "https://example.invalid/kadabra.webp",
    })

    ranked = digital_binder.rank_doubleholo_candidates(row, [candidate])

    assert ranked[0]["number_match"] is True
    assert ranked[0]["language_match"] is True
    assert ranked[0]["set_match"] is True
    assert ranked[0]["name_match"] is False
    assert ranked[0]["exact_identity_match"] is False


def ranked_doubleholo_name_match(card_name, species, candidate_name, language="EN", hit_language="english"):
    row = {
        "id": "name-01", "species": species, "card_name": card_name,
        "language": language, "set": "Base Set", "number": "1",
    }
    candidate = digital_binder.normalize_doubleholo_candidate({
        "objectID": "name-candidate", "name": candidate_name,
        "set_name": "Pokemon Base Set", "number": "1", "language": hit_language,
        "image_url": "https://example.invalid/name.webp",
    })
    return digital_binder.rank_doubleholo_candidates(row, [candidate])[0]["name_match"]


def test_doubleholo_name_match_accepts_exact_japanese_native_name_with_nfkc():
    assert ranked_doubleholo_name_match(
        "ピカチュウ", "Pikachu", "ﾋﾟｶﾁｭｳ", language="JP", hit_language="japanese"
    ) is True


def test_doubleholo_name_match_accepts_exact_chinese_native_name():
    assert ranked_doubleholo_name_match(
        "皮卡丘", "Pikachu", "皮卡丘", language="ZH", hit_language="chinese"
    ) is True


def test_doubleholo_name_match_preserves_nidoran_gender_variants():
    assert ranked_doubleholo_name_match("Nidoran♀", "Nidoran♀", "Nidoran♀") is True
    assert ranked_doubleholo_name_match("Nidoran♀", "Nidoran♀", "Nidoran♂") is False


def test_doubleholo_name_match_accepts_qualified_english_species_token_sequence():
    assert ranked_doubleholo_name_match(
        "わるいエーフィ", "Espeon", "Dark Espeon", language="JP", hit_language="japanese"
    ) is True


def test_doubleholo_name_match_accepts_imposter_oak_full_name_alias():
    assert ranked_doubleholo_name_match(
        "にせオーキドの逆襲", "Imposter Professor Oak's Revenge", "Imposter Oak's Revenge",
        language="JP", hit_language="japanese"
    ) is True


def test_doubleholo_name_match_accepts_misty_as_kasumi_trainer_alias():
    assert ranked_doubleholo_name_match(
        "カスミのなみだ", "Kasumi's Tears", "Misty's Tears",
        language="JP", hit_language="japanese"
    ) is True


def test_doubleholo_name_match_rejects_embedded_species_without_token_boundary():
    assert ranked_doubleholo_name_match("Mew", "Mew", "Mewtwo") is False
    assert ranked_doubleholo_name_match("Abra", "Abra", "Kadabra") is False


def doubleholo_search_row():
    return {
        "id": "abra-01", "species": "Abra", "card_name": "Abra",
        "language": "EN", "set": "Base Set", "number": "43/102",
    }


def test_search_doubleholo_skips_bad_hits_but_keeps_valid_hits():
    def mixed_hits_opener(request, timeout):
        return FakeHTTPResponse({"results": [{"hits": [
            None,
            {"objectID": "ok", "name": "Abra", "set_name": "Pokemon Base Set",
             "number": "43/102", "language": "english"},
            {"name": "missing object"},
        ]}]})

    candidates = digital_binder.search_doubleholo(doubleholo_search_row(), opener=mixed_hits_opener)

    assert [candidate["provider_id"] for candidate in candidates] == ["ok"]


def test_search_doubleholo_returns_empty_for_valid_no_hits():
    def no_hits_opener(request, timeout):
        return FakeHTTPResponse({"results": [{"hits": []}]})

    assert digital_binder.search_doubleholo(doubleholo_search_row(), opener=no_hits_opener) == []


def test_search_doubleholo_raises_clear_error_for_network_failure():
    def failed_opener(request, timeout):
        raise OSError("network down")

    try:
        digital_binder.search_doubleholo(doubleholo_search_row(), opener=failed_opener)
    except ValueError as exc:
        assert "DoubleHolo search failed" in str(exc)
        assert "network down" in str(exc)
    else:
        raise AssertionError("DoubleHolo provider network failures must not become no-hit results")


def test_search_doubleholo_raises_clear_error_for_truncated_response():
    def truncated_opener(request, timeout):
        raise IncompleteRead(b"partial", 20)

    try:
        digital_binder.search_doubleholo(doubleholo_search_row(), opener=truncated_opener)
    except ValueError as exc:
        assert "DoubleHolo search failed" in str(exc)
    else:
        raise AssertionError("truncated provider responses must use controlled error handling")


def test_search_doubleholo_raises_clear_error_for_bad_json():
    def malformed_opener(request, timeout):
        return FakeBinaryHTTPResponse(b"not json")

    try:
        digital_binder.search_doubleholo(doubleholo_search_row(), opener=malformed_opener)
    except ValueError as exc:
        assert "DoubleHolo search returned invalid JSON" in str(exc)
    else:
        raise AssertionError("DoubleHolo provider JSON failures must not become no-hit results")


def test_search_doubleholo_raises_clear_error_for_malformed_results_envelope():
    def malformed_envelope_opener(request, timeout):
        return FakeHTTPResponse({"results": {"hits": []}})

    try:
        digital_binder.search_doubleholo(doubleholo_search_row(), opener=malformed_envelope_opener)
    except ValueError as exc:
        assert "DoubleHolo search returned malformed results" in str(exc)
    else:
        raise AssertionError("DoubleHolo malformed envelopes must not become no-hit results")


def test_cache_opener_keys_post_requests_by_body(tmp_path, monkeypatch):
    calls = []

    def fake_urlopen(request, timeout):
        calls.append(request.data)
        return FakeBinaryHTTPResponse(request.data)

    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)
    opener = manage_card_images._cache_opener(tmp_path)
    first_request = manage_card_images.Request("https://example.invalid/search", data=b"first")
    second_request = manage_card_images.Request("https://example.invalid/search", data=b"second")

    with opener(first_request, timeout=20) as response:
        assert response.read() == b"first"
    with opener(second_request, timeout=20) as response:
        assert response.read() == b"second"

    assert calls == [b"first", b"second"]


def test_tcgdex_search_command_preserves_existing_cache_and_exits_nonzero_on_provider_error(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    cache_path = root / "tmp/digital-binder-review/candidates/abra-01.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text('{"old": "cache"}\n', encoding="utf-8")

    def failed_search(row, opener):
        raise ValueError("TCGdex search failed: network down")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_tcgdex", failed_search)

    assert manage_card_images.main(["search", "abra-01"]) == 1

    assert cache_path.read_text(encoding="utf-8") == '{"old": "cache"}\n'
    assert "TCGdex search failed: network down" in capsys.readouterr().err


def test_tcgdex_search_command_preserves_existing_cache_when_all_detail_fetches_fail(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    cache_path = root / "tmp/digital-binder-review/candidates/abra-01.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text('{"old": "cache"}\n', encoding="utf-8")

    def all_details_failed(row, opener):
        return [
            {
                "provider": "tcgdex", "provider_id": "base1-43", "name": "Abra",
                "set_id": "base1", "local_id": "43", "image_url": None,
                "detail_error": "detail service unavailable",
            },
            {
                "provider": "tcgdex", "provider_id": "base1-44", "name": "Abra",
                "set_id": "base1", "local_id": "44", "image_url": None,
                "detail_error": "detail service unavailable",
            },
        ]

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_tcgdex", all_details_failed)

    assert manage_card_images.main(["search", "abra-01"]) == 1

    assert cache_path.read_text(encoding="utf-8") == '{"old": "cache"}\n'
    stderr = capsys.readouterr().err
    assert "all TCGdex detail fetches failed" in stderr
    assert "detail service unavailable" in stderr


def test_tcgdex_search_command_caches_and_prints_partial_detail_errors(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)

    def partial_detail_failure(row, opener):
        return [
            {
                "provider": "tcgdex", "provider_id": "base1-43", "name": "Abra",
                "set_id": "base1", "set_name": "Base Set", "local_id": "43", "image_url": None,
                "detail_error": "404 not found",
            },
            {
                "provider": "tcgdex", "provider_id": "base1-44", "name": "Abra",
                "set_id": "base1", "set_name": "Base Set", "local_id": "44",
                "image_url": "https://assets.tcgdex.net/en/base/base1/44/high.webp",
            },
        ]

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_tcgdex", partial_detail_failure)

    assert manage_card_images.main(["search", "abra-01"]) == 0

    cached = json.loads(
        (root / "tmp/digital-binder-review/candidates/abra-01.json").read_text(encoding="utf-8")
    )
    assert cached["provider"] == "tcgdex"
    assert cached["registry"]["id"] == "abra-01"
    assert "404 not found" in cached["candidates"][0]["detail_error"]
    assert "detail_error=404 not found" in capsys.readouterr().out


def test_tcgdex_review_html_includes_per_candidate_detail_error(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)

    def partial_detail_failure(row, opener):
        return [
            {
                "provider": "tcgdex", "provider_id": "base1-43", "name": "Abra",
                "set_id": "base1", "set_name": "Base Set", "local_id": "43", "image_url": None,
                "detail_error": "detail timeout",
            },
            {
                "provider": "tcgdex", "provider_id": "base1-44", "name": "Abra",
                "set_id": "base1", "set_name": "Base Set", "local_id": "44",
                "image_url": "https://assets.tcgdex.net/en/base/base1/44/high.webp",
            },
        ]

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_tcgdex", partial_detail_failure)

    assert manage_card_images.review_command(argparse.Namespace(page="leaf-1")) == 0

    html = (root / "tmp/digital-binder-review/pages/leaf-1.html").read_text(encoding="utf-8")
    assert "detail_error" in html
    assert "detail timeout" in html


def test_doubleholo_search_command_prints_variant_confirmation_warning(tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)

    def fake_search(row, opener):
        return [{
            "provider": "doubleholo", "provider_id": "dh-43", "name": "Abra",
            "set_name": "Base Set", "local_id": "43/102", "language": "EN",
            "image_url": "https://example.invalid/abra.webp",
        }]

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_doubleholo", fake_search)

    assert manage_card_images.search_doubleholo_command(argparse.Namespace(card_id="abra-01")) == 0

    output = capsys.readouterr().out
    assert "exact_identity_match does not verify edition/variant" in output
    assert "visual confirmation" in output


def test_doubleholo_search_command_caches_under_doubleholo_review_dir(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)

    def fake_search(row, opener):
        return [{
            "provider": "doubleholo", "provider_id": "dh-43", "name": "Abra",
            "set_name": "Base Set", "local_id": "43/102", "language": "EN",
            "image_url": "https://example.invalid/abra.webp",
        }]

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_doubleholo", fake_search)

    assert manage_card_images.search_doubleholo_command(argparse.Namespace(card_id="abra-01")) == 0

    cached = json.loads(
        (root / "tmp/digital-binder-review/doubleholo/abra-01.json").read_text(encoding="utf-8")
    )
    assert cached["card_id"] == "abra-01"
    assert cached["candidates"][0]["candidate_index"] == 0
    assert cached["candidates"][0]["provider"] == "doubleholo"


def test_doubleholo_search_command_preserves_existing_cache_and_exits_nonzero_on_provider_error(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    cache_path = root / "tmp/digital-binder-review/doubleholo/abra-01.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text('{"old": "cache"}\n', encoding="utf-8")

    def failed_search(row, opener):
        raise ValueError("DoubleHolo search failed: network down")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_doubleholo", failed_search)

    assert manage_card_images.main(["search-doubleholo", "abra-01"]) == 1

    assert cache_path.read_text(encoding="utf-8") == '{"old": "cache"}\n'
    assert "DoubleHolo search failed: network down" in capsys.readouterr().err


def test_doubleholo_search_command_writes_empty_cache_for_valid_no_hits(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)

    def no_hits_search(row, opener):
        return []

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "search_doubleholo", no_hits_search)

    assert manage_card_images.main(["search-doubleholo", "abra-01"]) == 0

    cached = json.loads(
        (root / "tmp/digital-binder-review/doubleholo/abra-01.json").read_text(encoding="utf-8")
    )
    assert cached["card_id"] == "abra-01"
    assert cached["candidates"] == []


def test_approve_doubleholo_rejects_file_candidate_url(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "file:///tmp/abra.webp",
        "exact_identity_match": True,
        "original": {
            "objectID": "dh-43",
            "name": "Abra",
            "set_name": "Pokemon Base Set",
            "number": "43",
            "language": "english",
            "image_url": "file:///tmp/abra.webp",
            "image_url_small": None,
        },
    }])
    patch_doubleholo_live_object(monkeypatch, image_url="file:///tmp/abra.webp")
    monkeypatch.chdir(root)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "HTTP(S)" in str(exc)
    else:
        raise AssertionError("approve-doubleholo should reject file: candidate URLs")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_fetches_live_object_with_public_algolia_headers():
    calls = []

    def fake_opener(request, timeout):
        calls.append((request, timeout))
        return FakeHTTPResponse(doubleholo_live_object(object_id="dh-43"))

    fetched = manage_card_images._fetch_doubleholo_object("dh-43", opener=fake_opener)

    assert fetched["objectID"] == "dh-43"
    request, timeout = calls[0]
    assert request.full_url == doubleholo_object_url("dh-43")
    assert request.get_method() == "GET"
    assert request.headers["X-algolia-application-id"] == "W5SF479ZKL"
    assert request.headers["X-algolia-api-key"] == "50fdd89ab8d777151bc000bba6097357"
    assert "Cookie" not in request.headers
    assert timeout == 20


def test_approve_doubleholo_object_fetch_wraps_truncated_response():
    def truncated_opener(request, timeout):
        raise IncompleteRead(b"partial", 20)

    try:
        manage_card_images._fetch_doubleholo_object("dh-43", opener=truncated_opener)
    except ValueError as exc:
        assert "DoubleHolo object fetch failed for dh-43" in str(exc)
    else:
        raise AssertionError("truncated object responses must use controlled error handling")


def test_approve_doubleholo_uses_live_object_not_tampered_cached_original_url_or_identity(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://attacker.example/cached.png",
        "exact_identity_match": True,
        "original": {
            "objectID": "attacker-id",
            "name": "Kadabra",
            "set_name": "Pokemon Jungle",
            "number": "64",
            "language": "japanese",
            "image_url": "https://attacker.example/cached.png",
            "image_url_small": None,
        },
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == doubleholo_object_url("dh-43"):
            return FakeHTTPResponse(doubleholo_live_object(object_id="dh-43"))
        if request.full_url == "https://supabase.example/abra.png":
            return FakeBinaryHTTPResponse(image_bytes("PNG"))
        raise AssertionError(f"unexpected URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args()) == 0

    assert requested_urls == [doubleholo_object_url("dh-43"), "https://supabase.example/abra.png"]
    assert "exact_identity_match does not verify edition/variant" in capsys.readouterr().out
    record = load_images(root)["cards"]["abra-01"]
    assert record["upstream_id"] == "dh-43"
    assert record["source_url"] == "https://supabase.example/abra.png"


def test_approve_doubleholo_rejects_live_wrong_species_even_when_number_language_and_set_match(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate()])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == doubleholo_object_url("dh-43"):
            return FakeHTTPResponse(doubleholo_live_object(name="Kadabra", object_id="dh-43"))
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "exact identity" in str(exc)
    else:
        raise AssertionError("wrong species must not pass exact DoubleHolo approval")

    assert requested_urls == [doubleholo_object_url("dh-43")]
    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_proxy_uses_live_object_and_live_url(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "live-proxy-id",
        "image_url": "https://attacker.example/cached.png",
        "exact_identity_match": False,
        "original": {
            "objectID": "cached-id",
            "name": "Wrong cached card",
            "set_name": "Pokemon Wrong Set",
            "number": "999",
            "language": "english",
            "image_url": "https://attacker.example/cached.png",
            "image_url_small": None,
        },
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == doubleholo_object_url("live-proxy-id"):
            return FakeHTTPResponse(doubleholo_live_object(
                object_id="live-proxy-id",
                name="Kadabra",
                set_name="Pokemon Jungle",
                number="64",
                image_url="https://supabase.example/proxy.png",
            ))
        if request.full_url == "https://supabase.example/proxy.png":
            return FakeBinaryHTTPResponse(image_bytes("PNG"))
        raise AssertionError(f"unexpected approval URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args(
        classification="proxy",
        note="Proxy image: DoubleHolo live object does not match the registry identity.",
    )) == 0

    assert requested_urls == [
        doubleholo_object_url("live-proxy-id"),
        "https://supabase.example/proxy.png",
    ]
    record = load_images(root)["cards"]["abra-01"]
    assert record["classification"] == "proxy"
    assert record["upstream_id"] == "live-proxy-id"
    assert record["source_url"] == "https://supabase.example/proxy.png"
    assert record["note"] == "Proxy image: DoubleHolo live object does not match the registry identity."
    assert "identity_basis" not in record


def test_approve_doubleholo_live_fetch_failure_preserves_existing_yaml_asset_and_skips_download(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    original_yaml, original_asset, asset_path = seed_existing_proxy_image(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate()])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == doubleholo_object_url("dh-43"):
            raise OSError("Algolia unavailable")
        raise AssertionError("image download should not run after live object fetch failure")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "DoubleHolo object fetch failed" in str(exc)
        assert "Algolia unavailable" in str(exc)
    else:
        raise AssertionError("live object fetch failure should reject approval")

    assert requested_urls == [doubleholo_object_url("dh-43")]
    assert (root / "data/card-images.yaml").read_bytes() == original_yaml
    assert asset_path.read_bytes() == original_asset


def test_approve_doubleholo_rejects_live_object_id_mismatch_before_download(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate(object_id="dh-43")])

    def fake_urlopen(request, timeout):
        if request.full_url == doubleholo_object_url("dh-43"):
            return FakeHTTPResponse(doubleholo_live_object(object_id="different-id"))
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "objectID" in str(exc)
        assert "dh-43" in str(exc)
    else:
        raise AssertionError("live object id mismatch should reject approval")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_rejects_tampered_cached_exact_identity_flag(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://example.invalid/abra.png",
        "exact_identity_match": True,
        "original": {
            "objectID": "dh-43",
            "name": "Abra",
            "set_name": "Pokemon Jungle",
            "number": "43",
            "language": "english",
            "image_url": "https://example.invalid/abra.png",
            "image_url_small": None,
        },
    }])
    patch_doubleholo_live_object(monkeypatch, set_name="Pokemon Jungle", image_url="https://example.invalid/abra.png")

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "exact identity" in str(exc)
    else:
        raise AssertionError("tampered cached exact flag should not permit exact approval")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_recomputes_exact_identity_from_current_registry(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Jungle", number="43/64"),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://example.invalid/abra.png",
        "exact_identity_match": True,
        "original": {
            "objectID": "dh-43",
            "name": "Abra",
            "set_name": "Pokemon Base Set",
            "number": "43",
            "language": "english",
            "image_url": "https://example.invalid/abra.png",
            "image_url_small": None,
        },
    }])
    patch_doubleholo_live_object(monkeypatch, set_name="Pokemon Base Set", image_url="https://example.invalid/abra.png")

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "exact identity" in str(exc)
    else:
        raise AssertionError("stale exact flag should be recomputed against current registry")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_rejects_uncertain_registry_exact_before_candidate_lookup(tmp_path, monkeypatch):
    root = project_fixture(tmp_path, registry_confidence="uncertain")
    write_current_generated(root)

    def fail_if_candidate_loaded(*args, **kwargs):
        raise AssertionError("uncertain exact should reject before reading candidate cache")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "_load_doubleholo_candidate", fail_if_candidate_loaded)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "uncertain" in str(exc)
    else:
        raise AssertionError("uncertain registry identity should reject exact approval")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_rejects_exact_when_candidate_identity_is_not_exact(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://example.invalid/abra.png",
        "exact_identity_match": False,
        "original": {
            "objectID": "dh-43",
            "name": "Abra",
            "set_name": "Pokemon Jungle",
            "number": "43",
            "language": "english",
            "image_url": "https://example.invalid/abra.png",
            "image_url_small": None,
        },
    }])
    patch_doubleholo_live_object(monkeypatch, set_name="Pokemon Jungle", image_url="https://example.invalid/abra.png")
    monkeypatch.chdir(root)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "exact identity" in str(exc)
    else:
        raise AssertionError("exact doubleholo approval should require an exact identity match")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_unnumbered_accepts_provider_internal_number_and_records_provenance(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [
        doubleholo_cached_candidate(number="SEALED-5427857")
    ])
    patch_doubleholo_live_object(monkeypatch, number="SEALED-5427857")
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        return FakeBinaryHTTPResponse(image_bytes("PNG"))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args(
        note="Curator compared the unnumbered printing visually.",
        confirm_unnumbered=True,
        identity_basis="No collector number printed; curator matched name, language, and set.",
    )) == 0

    assert requested_urls == ["https://supabase.example/abra.png"]
    assert "exact_identity_match does not verify edition/variant" in capsys.readouterr().out
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "doubleholo"
    assert record["classification"] == "exact"
    assert record["upstream_id"] == "dh-43"
    assert record["source_url"] == "https://supabase.example/abra.png"
    assert record["identity_basis"] == (
        "No collector number printed; curator matched name, language, and set."
    )
    assert record["note"] == "Curator compared the unnumbered printing visually."
    assert "number" not in record
    assert "local_id" not in record


def test_approve_doubleholo_confirm_unnumbered_accepts_blank_candidate_number(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate(number="")])
    patch_doubleholo_live_object(monkeypatch, number="")

    def fake_urlopen(request, timeout):
        return FakeBinaryHTTPResponse(image_bytes("PNG"))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args(
        note="Curator compared the unnumbered printing visually.",
        confirm_unnumbered=True,
        identity_basis="No collector number printed; matched to the registry printing.",
    )) == 0

    record = load_images(root)["cards"]["abra-01"]
    assert record["identity_basis"] == "No collector number printed; matched to the registry printing."


def test_approve_doubleholo_without_confirm_unnumbered_rejects_unnumbered_exact_before_download(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate(number="")])
    patch_doubleholo_live_object(monkeypatch, number="")

    def fail_if_called(request, timeout):
        raise AssertionError("default exact approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "exact identity" in str(exc)
    else:
        raise AssertionError("default DoubleHolo exact approval should not accept blank registry number")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_unnumbered_requires_exact_note_and_identity_basis_before_candidate_lookup(
        tmp_path, monkeypatch):
    cases = [
        ("proxy", {"classification": "proxy", "note": "Curator note.", "identity_basis": "Basis."}, "exact"),
        ("missing-note", {"note": " ", "identity_basis": "Basis."}, "--note"),
        ("missing-basis", {"note": "Curator note.", "identity_basis": " "}, "--identity-basis"),
    ]
    for label, kwargs, expected in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        (root / "docs" / "card-registry.md").write_text(
            registry_doc(confidence="confirmed", set_="Base Set", number=""),
            encoding="utf-8",
        )
        write_current_generated(root)

        def fail_if_candidate_loaded(*args, **kwargs):
            raise AssertionError("approval should reject before reading candidate cache")

        monkeypatch.chdir(root)
        monkeypatch.setattr(manage_card_images, "_load_doubleholo_candidate", fail_if_candidate_loaded)

        try:
            manage_card_images.approve_doubleholo_command(approve_args(
                confirm_unnumbered=True,
                **kwargs,
            ))
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"confirm-unnumbered should reject {label}")

        assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_unnumbered_rejects_confidence_and_number_before_candidate_lookup(
        tmp_path, monkeypatch):
    cases = [
        ("uncertain", registry_doc(confidence="uncertain", set_="Base Set", number=""), "uncertain"),
        ("photo", registry_doc(confidence="photo", set_="Base Set", number="43/102"), "confirmed"),
        ("numbered", registry_doc(confidence="confirmed", set_="Base Set", number="43/102"), "blank"),
    ]
    for label, registry_text, expected in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        (root / "docs" / "card-registry.md").write_text(registry_text, encoding="utf-8")
        write_current_generated(root)

        def fail_if_candidate_loaded(*args, **kwargs):
            raise AssertionError("approval should reject before reading candidate cache")

        monkeypatch.chdir(root)
        monkeypatch.setattr(manage_card_images, "_load_doubleholo_candidate", fail_if_candidate_loaded)

        try:
            manage_card_images.approve_doubleholo_command(approve_args(
                note="Curator compared the unnumbered printing visually.",
                confirm_unnumbered=True,
                identity_basis="No collector number printed; matched to registry.",
            ))
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"confirm-unnumbered should reject {label} registry")

        assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_unnumbered_rejects_candidate_mismatches_before_download(
        tmp_path, monkeypatch):
    cases = [
        ("missing-image", doubleholo_cached_candidate(image_url=None), "image_url"),
        ("printed-number", doubleholo_cached_candidate(number="43"), "number"),
        ("name", doubleholo_cached_candidate(name="Kadabra", number=""), "unnumbered"),
        ("language", doubleholo_cached_candidate(language="japanese", number=""), "unnumbered"),
        ("set", doubleholo_cached_candidate(set_name="Pokemon Jungle", number=""), "unnumbered"),
    ]
    for label, candidate, expected in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        (root / "docs" / "card-registry.md").write_text(
            registry_doc(confidence="confirmed", set_="Base Set", number=""),
            encoding="utf-8",
        )
        write_current_generated(root)
        write_doubleholo_candidate_cache(root, "abra-01", [candidate])
        downloads = []

        def fail_if_called(request, timeout):
            downloads.append(request.full_url)
            raise AssertionError("approval should reject before image download")

        patch_doubleholo_live_candidate(monkeypatch, candidate)
        monkeypatch.chdir(root)
        monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

        try:
            manage_card_images.approve_doubleholo_command(approve_args(
                note="Curator compared the unnumbered printing visually.",
                confirm_unnumbered=True,
                identity_basis="No collector number printed; matched to registry.",
            ))
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"confirm-unnumbered should reject wrong {label}")

        assert downloads == []
        assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_unnumbered_cannot_combine_with_confirm_identity_before_lookup(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)

    def fail_if_candidate_loaded(*args, **kwargs):
        raise AssertionError("approval should reject before reading candidate cache")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "_load_doubleholo_candidate", fail_if_candidate_loaded)

    try:
        manage_card_images.approve_doubleholo_command(approve_args(
            note="Curator compared the unnumbered printing visually.",
            confirm_identity=True,
            confirm_unnumbered=True,
            identity_basis="No collector number printed; matched to registry.",
        ))
    except ValueError as exc:
        assert "cannot combine" in str(exc)
    else:
        raise AssertionError("confirm-unnumbered should not combine with confirm-identity")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_identity_accepts_set_alias_and_records_provenance(
        tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="BS", number="43/102"),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate()])
    patch_doubleholo_live_object(monkeypatch)
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        return FakeBinaryHTTPResponse(image_bytes("PNG"))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args(
        note="Curator compared the printing visually.",
        confirm_identity=True,
    )) == 0

    assert requested_urls == ["https://supabase.example/abra.png"]
    assert "exact_identity_match does not verify edition/variant" in capsys.readouterr().out
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "doubleholo"
    assert record["classification"] == "exact"
    assert record["upstream_id"] == "dh-43"
    assert record["source_url"] == "https://supabase.example/abra.png"
    assert record["identity_basis"] == (
        "curator visually confirmed printing; DoubleHolo set-name alias differs from registry"
    )
    assert record["note"] == "Curator compared the printing visually."


def test_approve_doubleholo_confirm_identity_requires_nonempty_note_before_download(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="BS", number="43/102"),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate()])

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args(
            note=" ",
            confirm_identity=True,
        ))
    except ValueError as exc:
        assert "--note" in str(exc)
    else:
        raise AssertionError("curator-confirmed DoubleHolo alias approval should require a note")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_identity_rejects_uncertain_registry_before_candidate_lookup(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path, registry_confidence="uncertain")
    write_current_generated(root)

    def fail_if_candidate_loaded(*args, **kwargs):
        raise AssertionError("uncertain exact should reject before reading candidate cache")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "_load_doubleholo_candidate", fail_if_candidate_loaded)

    try:
        manage_card_images.approve_doubleholo_command(approve_args(
            note="Curator compared the printing visually.",
            confirm_identity=True,
        ))
    except ValueError as exc:
        assert "uncertain" in str(exc)
    else:
        raise AssertionError("curator-confirmed identity should not override uncertain registry")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_identity_rejects_wrong_number_language_or_name_before_download(
        tmp_path, monkeypatch):
    cases = [
        ("number", doubleholo_cached_candidate(number="44")),
        ("language", doubleholo_cached_candidate(language="japanese")),
        ("name", doubleholo_cached_candidate(name="Kadabra")),
    ]
    for label, candidate in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        (root / "docs" / "card-registry.md").write_text(
            registry_doc(confidence="confirmed", set_="BS", number="43/102"),
            encoding="utf-8",
        )
        write_current_generated(root)
        write_doubleholo_candidate_cache(root, "abra-01", [candidate])
        downloads = []

        def fail_if_called(request, timeout):
            downloads.append(request.full_url)
            raise AssertionError("approval should reject before image download")

        patch_doubleholo_live_candidate(monkeypatch, candidate)
        monkeypatch.chdir(root)
        monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

        try:
            manage_card_images.approve_doubleholo_command(approve_args(
                note="Curator compared the printing visually.",
                confirm_identity=True,
            ))
        except ValueError as exc:
            assert "set-name alias" in str(exc) or "identity" in str(exc)
        else:
            raise AssertionError(f"curator confirmation should not override wrong {label}")

        assert downloads == []
        assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_confirm_identity_rejects_missing_image_before_download(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="BS", number="43/102"),
        encoding="utf-8",
    )
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [doubleholo_cached_candidate(image_url=None)])
    patch_doubleholo_live_object(monkeypatch, image_url=None)

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args(
            note="Curator compared the printing visually.",
            confirm_identity=True,
        ))
    except ValueError as exc:
        assert "image_url" in str(exc)
    else:
        raise AssertionError("curator confirmation should not override a missing image")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_curator_confirmation_flags_are_documented_only_on_doubleholo_help():
    script = Path(__file__).with_name("manage-card-images.py")
    doubleholo_help = subprocess.run(
        [sys.executable, str(script), "approve-doubleholo", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    approve_help = subprocess.run(
        [sys.executable, str(script), "approve", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--confirm-identity" in doubleholo_help.stdout
    assert "--confirm-unnumbered" in doubleholo_help.stdout
    assert "--identity-basis" in doubleholo_help.stdout
    assert "curator-confirmed" in doubleholo_help.stdout
    assert "cannot be" in doubleholo_help.stdout
    assert "combined with --confirm-identity" in doubleholo_help.stdout
    assert "--confirm-identity" not in approve_help.stdout
    assert "--confirm-unnumbered" not in approve_help.stdout
    assert "--identity-basis" not in approve_help.stdout


def test_approve_doubleholo_rejects_stale_cache_without_provider_id_with_refetch_instruction(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "image_url": "https://supabase.example/abra.png",
        "exact_identity_match": True,
    }])

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before object fetch or image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "stale or malformed" in str(exc)
        assert "provider_id" in str(exc)
        assert "rerun search-doubleholo" in str(exc)
    else:
        raise AssertionError("stale DoubleHolo candidate cache should reject approval")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_missing_candidate_cache_names_actual_recovery_commands(tmp_path, monkeypatch, capsys):
    cases = [
        (
            "tcgdex",
            ["approve", "abra-01", "--candidate-index", "0", "--classification", "exact"],
            "run search abra-01 first",
        ),
        (
            "doubleholo",
            ["approve-doubleholo", "abra-01", "--candidate-index", "0", "--classification", "exact"],
            "run search-doubleholo abra-01 first",
        ),
    ]
    for label, argv, expected in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        write_current_generated(root)
        monkeypatch.chdir(root)

        assert manage_card_images.main(argv) == 1

        stderr = capsys.readouterr().err
        assert expected in stderr
        assert "run doubleholo search" not in stderr
        assert "run tcgdex search" not in stderr


def test_approve_doubleholo_uses_cached_provider_id_to_select_live_object(
         tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "live-id",
        "image_url": "https://attacker.example/tampered.png",
        "exact_identity_match": True,
        "original": {
            "objectID": "dh-43",
            "name": "Kadabra",
            "set_name": "Pokemon Jungle",
            "number": "64",
            "language": "japanese",
            "image_url": "https://attacker.example/tampered.png",
            "image_url_small": None,
        },
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == doubleholo_object_url("live-id"):
            return FakeHTTPResponse(doubleholo_live_object(
                object_id="live-id", image_url="https://supabase.example/live.png"
            ))
        if request.full_url == "https://supabase.example/live.png":
            return FakeBinaryHTTPResponse(image_bytes("PNG"))
        raise AssertionError(f"unexpected approval URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args()) == 0

    assert requested_urls == [doubleholo_object_url("live-id"), "https://supabase.example/live.png"]
    output = capsys.readouterr().out
    assert "exact_identity_match does not verify edition/variant" in output
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "doubleholo"
    assert record["upstream_id"] == "live-id"
    assert record["source_url"] == "https://supabase.example/live.png"


def test_approve_doubleholo_writes_authorized_provider_record(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://supabase.example/abra.png",
        "exact_identity_match": True,
        "original": {
            "objectID": "dh-43",
            "name": "Abra",
            "set_name": "Pokemon Base Set",
            "number": "43",
            "language": "english",
            "image_url": "https://supabase.example/abra.png",
            "image_url_small": None,
        },
    }])
    patch_doubleholo_live_object(monkeypatch)

    def fake_urlopen(request, timeout):
        return FakeBinaryHTTPResponse(image_bytes("PNG"))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args()) == 0

    asset_path = root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp"
    with Image.open(asset_path) as image:
        assert image.format == "WEBP"
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "doubleholo"
    assert record["upstream_id"] == "dh-43"
    assert record["source_url"] == "https://supabase.example/abra.png"
    assert record["usage_basis"] == "Owner-authorized DoubleHolo card catalog image."


def test_approve_doubleholo_preserves_existing_asset_and_yaml_when_manifest_write_fails(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    original_yaml, original_asset, asset_path = seed_existing_proxy_image(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://supabase.example/abra.png",
        "exact_identity_match": True,
        "original": {
            "objectID": "dh-43",
            "name": "Abra",
            "set_name": "Pokemon Base Set",
            "number": "43",
            "language": "english",
            "image_url": "https://supabase.example/abra.png",
            "image_url_small": None,
        },
    }])
    patch_doubleholo_live_object(monkeypatch)

    def fake_urlopen(request, timeout):
        return FakeBinaryHTTPResponse(image_bytes("PNG", color=(255, 0, 0)))

    def fail_write(root_arg, images):
        raise OSError("simulated DoubleHolo manifest write failure")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)
    monkeypatch.setattr(manage_card_images.digital_binder, "write_image_manifest_atomically", fail_write)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except OSError as exc:
        assert "simulated DoubleHolo" in str(exc)
    else:
        raise AssertionError("manifest write failure should reject DoubleHolo update")

    assert (root / "data/card-images.yaml").read_bytes() == original_yaml
    assert asset_path.read_bytes() == original_asset


def test_merged_images_preserves_identity_basis_for_same_doubleholo_upstream_id(tmp_path):
    root = project_fixture(tmp_path)
    images = load_images(root)
    images["cards"]["abra-01"] = {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-22",
        "provider": "doubleholo",
        "upstream_id": "dh-43",
        "source_url": "https://supabase.example/old.png",
        "usage_basis": "Owner-authorized DoubleHolo card catalog image.",
        "identity_basis": "Curator confirmed unnumbered printing.",
    }
    write_images(root, images)

    merged = manage_card_images._merged_images(root, "abra-01", {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-23",
        "provider": "doubleholo",
        "upstream_id": "dh-43",
        "source_url": "https://supabase.example/new-render.png",
        "usage_basis": "Owner-authorized DoubleHolo card catalog image.",
    })

    assert merged["cards"]["abra-01"]["identity_basis"] == "Curator confirmed unnumbered printing."


def test_merged_images_preserves_identity_basis_for_same_provider_source_url_without_upstream_id(tmp_path):
    root = project_fixture(tmp_path)
    images = load_images(root)
    images["cards"]["abra-01"] = {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-22",
        "provider": "local-file",
        "source_url": "https://example.invalid/source.png",
        "usage_basis": "Owner supplied scan.",
        "identity_basis": "Curator confirmed unnumbered printing.",
    }
    write_images(root, images)

    merged = manage_card_images._merged_images(root, "abra-01", {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-23",
        "provider": "local-file",
        "source_url": "https://example.invalid/source.png",
        "usage_basis": "Owner supplied scan.",
    })

    assert merged["cards"]["abra-01"]["identity_basis"] == "Curator confirmed unnumbered printing."


def test_replace_reviewed_image_does_not_reuse_identity_basis_for_replaced_doubleholo_candidate(
        tmp_path):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)
    images = load_images(root)
    images["cards"]["abra-01"] = {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-22",
        "provider": "doubleholo",
        "upstream_id": "old-candidate",
        "source_url": "https://supabase.example/old.png",
        "usage_basis": "Owner-authorized DoubleHolo card catalog image.",
        "identity_basis": "Old curator basis for old candidate.",
    }
    write_images(root, images)
    staged_asset = root / "tmp/digital-binder-review/staged/abra-01.webp"
    write_image(staged_asset)

    try:
        manage_card_images._replace_reviewed_image(root, "abra-01", {
            "classification": "exact",
            "asset_path": "assets/images/cards/abra-01.webp",
            "reviewed": True,
            "reviewed_on": "2026-09-23",
            "provider": "doubleholo",
            "upstream_id": "new-candidate",
            "source_url": "https://supabase.example/new.png",
            "usage_basis": "Owner-authorized DoubleHolo card catalog image.",
        }, staged_asset)
    except ValueError as exc:
        assert "identity_basis" in str(exc)
    else:
        raise AssertionError("replaced DoubleHolo candidate must provide a fresh unnumbered identity basis")


def test_merged_images_does_not_carry_identity_basis_across_providers(tmp_path):
    root = project_fixture(tmp_path)
    images = load_images(root)
    images["cards"]["abra-01"] = {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-22",
        "provider": "local-file",
        "source_url": "https://example.invalid/source.png",
        "usage_basis": "Owner supplied scan.",
        "identity_basis": "Old local-file basis.",
    }
    write_images(root, images)

    merged = manage_card_images._merged_images(root, "abra-01", {
        "classification": "exact",
        "asset_path": "assets/images/cards/abra-01.webp",
        "reviewed": True,
        "reviewed_on": "2026-09-23",
        "provider": "doubleholo",
        "upstream_id": "dh-43",
        "source_url": "https://supabase.example/abra.png",
        "usage_basis": "Owner-authorized DoubleHolo card catalog image.",
    })

    assert "identity_basis" not in merged["cards"]["abra-01"]


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


def test_crop_evidence_photo_applies_exif_orientation_before_bounds(tmp_path):
    source = tmp_path / "source.jpg"
    target = tmp_path / "crop.webp"
    image = Image.new("RGB", (80, 40), (0, 0, 255))
    image.paste((255, 0, 0), (0, 0, 40, 40))
    exif = image.getexif()
    exif[274] = 6
    image.save(source, quality=100, subsampling=0, exif=exif)

    digital_binder.crop_evidence_photo(source, (0, 0, 40, 40), target)

    with Image.open(target) as cropped:
        assert cropped.format == "WEBP"
        assert cropped.size == (40, 40)
        red, _green, blue = cropped.resize((1, 1)).getpixel((0, 0))
        assert red > 240
        assert blue < 15


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
            sys.executable, str(Path(__file__).with_name("manage-card-images.py")),
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


def test_approve_rejects_tcgdex_cache_missing_trust_metadata(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    cache_path = root / "tmp/digital-binder-review/candidates/abra-01.json"
    cache_path.parent.mkdir(parents=True)
    cache_path.write_text(json.dumps({
        "card_id": "abra-01",
        "registry": {},
        "candidates": [{
            "candidate_index": 0,
            "provider_id": "base1-43",
            "image_url": "https://attacker.example/cached.png",
            "exact_identity_match": True,
        }],
    }), encoding="utf-8")

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before live fetch or image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "tcgdex candidate cache" in str(exc)
        assert "provider" in str(exc)
    else:
        raise AssertionError("TCGdex approval must reject caches without trust metadata")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_rejects_tcgdex_cache_for_wrong_card_or_provider(tmp_path, monkeypatch):
    cases = [
        ("wrong-card", {"card_id": "kadabra-01", "provider": "tcgdex"}, "card_id"),
        ("wrong-provider", {"card_id": "abra-01", "provider": "doubleholo"}, "provider"),
    ]
    for label, overrides, expected in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        write_current_generated(root)
        current_registry = digital_binder.load_registry(root / "docs" / "card-registry.md")["abra-01"]
        cache_path = root / "tmp/digital-binder-review/candidates/abra-01.json"
        cache_path.parent.mkdir(parents=True)
        payload = {
            "card_id": "abra-01",
            "provider": "tcgdex",
            "registry": current_registry,
            "candidates": [{
                "candidate_index": 0,
                "provider_id": "base1-43",
                "image_url": "https://attacker.example/cached.png",
            }],
        }
        payload.update(overrides)
        cache_path.write_text(json.dumps(payload), encoding="utf-8")

        def fail_if_called(request, timeout):
            raise AssertionError("approval should reject before live fetch or image download")

        monkeypatch.chdir(root)
        monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

        try:
            manage_card_images.approve_command(approve_args())
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"TCGdex approval must reject {label} cache")

        assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_rejects_tcgdex_cache_stale_against_current_registry(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
    }])
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Jungle", number="43/64"),
        encoding="utf-8",
    )
    write_current_generated(root)

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before live fetch or image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "stale" in str(exc)
        assert "registry" in str(exc)
    else:
        raise AssertionError("TCGdex approval must reject cache from stale registry identity")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_tcgdex_uses_live_object_not_cached_url_or_exact_flag(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
        "exact_identity_match": False,
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(
                object_id="base1-43",
                image_url="https://assets.tcgdex.net/en/base/base1/43-live",
            ))
        if request.full_url == "https://assets.tcgdex.net/en/base/base1/43-live/high.webp":
            return FakeBinaryHTTPResponse(image_bytes("PNG"))
        raise AssertionError(f"unexpected approval URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_command(approve_args()) == 0

    assert requested_urls == [
        tcgdex_object_url("base1-43"),
        "https://assets.tcgdex.net/en/base/base1/43-live/high.webp",
    ]
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "tcgdex"
    assert record["upstream_id"] == "base1-43"
    assert record["source_url"] == "https://assets.tcgdex.net/en/base/base1/43-live/high.webp"


def test_approve_tcgdex_rejects_cached_provider_id_tamper_by_recomputing_identity(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-44",
        "image_url": "https://attacker.example/cached.png",
        "exact_identity_match": True,
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == tcgdex_object_url("base1-44"):
            return FakeHTTPResponse(tcgdex_live_object(object_id="base1-44", local_id="44"))
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "exact TCGdex approval requires a recomputed exact identity match" in str(exc)
    else:
        raise AssertionError("tampered TCGdex provider_id must not pass exact approval")

    assert requested_urls == [tcgdex_object_url("base1-44")]
    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_tcgdex_rejects_live_id_mismatch_before_download(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
    }])

    def fake_urlopen(request, timeout):
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(object_id="different-id"))
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "TCGdex card id mismatch" in str(exc)
        assert "base1-43" in str(exc)
    else:
        raise AssertionError("live TCGdex id mismatch should reject approval")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_tcgdex_rejects_live_identity_mismatch_before_download(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
        "exact_identity_match": True,
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(object_id="base1-43", name="Kadabra"))
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "exact TCGdex approval requires a recomputed exact identity match" in str(exc)
    else:
        raise AssertionError("wrong live TCGdex identity must not pass exact approval")

    assert requested_urls == [tcgdex_object_url("base1-43")]
    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_tcgdex_live_fetch_failures_preserve_existing_yaml_asset_and_skip_download(
        tmp_path, monkeypatch):
    cases = [
        ("network", "TCGdex object fetch failed", OSError("TCGdex unavailable")),
        ("json", "TCGdex object fetch returned invalid JSON", b"{not json"),
        ("envelope", "TCGdex object fetch returned malformed object", ["not an object"]),
    ]
    for label, expected, response in cases:
        root = tmp_path / label
        root.mkdir()
        project_fixture(root)
        write_current_generated(root)
        original_yaml, original_asset, asset_path = seed_existing_proxy_image(root)
        write_candidate_cache(root, "abra-01", [{
            "candidate_index": 0,
            "provider_id": "base1-43",
            "image_url": "https://attacker.example/cached.png",
        }])
        requested_urls = []

        def fake_urlopen(request, timeout):
            requested_urls.append(request.full_url)
            if request.full_url == tcgdex_object_url("base1-43"):
                if isinstance(response, OSError):
                    raise response
                if isinstance(response, bytes):
                    return FakeBinaryHTTPResponse(response)
                return FakeHTTPResponse(response)
            raise AssertionError("image download should not run after live object fetch failure")

        monkeypatch.chdir(root)
        monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

        try:
            manage_card_images.approve_command(approve_args())
        except ValueError as exc:
            assert expected in str(exc)
        else:
            raise AssertionError(f"{label} live object fetch failure should reject approval")

        assert requested_urls == [tcgdex_object_url("base1-43")]
        assert (root / "data/card-images.yaml").read_bytes() == original_yaml
        assert asset_path.read_bytes() == original_asset


def test_approve_tcgdex_proxy_uses_live_object_and_preserves_note_requirement(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-64",
        "image_url": "https://attacker.example/cached.png",
        "exact_identity_match": False,
    }])
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == tcgdex_object_url("base1-64"):
            return FakeHTTPResponse(tcgdex_live_object(
                object_id="base1-64",
                name="Kadabra",
                local_id="64",
                image_url="https://assets.tcgdex.net/en/base/base1/64",
            ))
        if request.full_url == "https://assets.tcgdex.net/en/base/base1/64/high.webp":
            return FakeBinaryHTTPResponse(image_bytes("PNG"))
        raise AssertionError(f"unexpected approval URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_command(approve_args(
        classification="proxy",
        note="Proxy image: live TCGdex card does not match the registry identity.",
    )) == 0

    assert requested_urls == [
        tcgdex_object_url("base1-64"),
        "https://assets.tcgdex.net/en/base/base1/64/high.webp",
    ]
    record = load_images(root)["cards"]["abra-01"]
    assert record["classification"] == "proxy"
    assert record["upstream_id"] == "base1-64"
    assert record["source_url"] == "https://assets.tcgdex.net/en/base/base1/64/high.webp"
    assert record["note"] == "Proxy image: live TCGdex card does not match the registry identity."


def test_approve_rejects_file_candidate_url(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
    }])

    def fake_urlopen(request, timeout):
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(object_id="base1-43", image_url="file:///tmp/abra"))
        raise AssertionError("approval should reject live file: URL before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "HTTP(S)" in str(exc)
    else:
        raise AssertionError("approve should reject file: candidate URLs")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_rejects_invalid_image_payload(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
    }])

    def fake_urlopen(request, timeout):
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(
                object_id="base1-43", image_url="https://example.invalid/not-image"
            ))
        if request.full_url == "https://example.invalid/not-image/high.webp":
            return FakeBinaryHTTPResponse(b"not an image")
        raise AssertionError(f"unexpected approval URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except OSError:
        pass
    else:
        raise AssertionError("approve should reject invalid image payloads")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_reencodes_valid_candidate_image_to_webp(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://attacker.example/cached.png",
    }])

    def fake_urlopen(request, timeout):
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(
                object_id="base1-43", image_url="https://example.invalid/abra"
            ))
        if request.full_url == "https://example.invalid/abra/high.webp":
            return FakeBinaryHTTPResponse(image_bytes("PNG"))
        raise AssertionError(f"unexpected approval URL {request.full_url}")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_command(approve_args()) == 0

    asset_path = root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp"
    with Image.open(asset_path) as image:
        assert image.format == "WEBP"
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "tcgdex"
    assert record["upstream_id"] == "base1-43"
    assert record["source_url"] == "https://example.invalid/abra/high.webp"


def test_approve_preserves_existing_asset_and_yaml_when_validation_rejects(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)
    original_yaml, original_asset, asset_path = seed_existing_proxy_image(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "https://example.invalid/abra.png",
    }])

    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url == tcgdex_object_url("base1-43"):
            return FakeHTTPResponse(tcgdex_live_object(object_id="base1-43"))
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "exact TCGdex approval requires a recomputed exact identity match" in str(exc)
    else:
        raise AssertionError("invalid exact approval should be rejected")

    assert requested_urls == [tcgdex_object_url("base1-43")]
    assert (root / "data/card-images.yaml").read_bytes() == original_yaml
    assert asset_path.read_bytes() == original_asset


def test_approve_local_preserves_existing_asset_and_yaml_when_validation_rejects(tmp_path):
    root = project_fixture(tmp_path)
    (root / "docs" / "card-registry.md").write_text(
        registry_doc(confidence="confirmed", set_="Base Set", number=""),
        encoding="utf-8",
    )
    write_current_generated(root)
    original_yaml, original_asset, asset_path = seed_existing_proxy_image(root)
    image_file = tmp_path / "local.png"
    write_image(image_file, color=(255, 0, 0))

    result = subprocess.run(
        [
            sys.executable, str(Path(__file__).with_name("manage-card-images.py")),
            "approve-local", "abra-01", "--file", str(image_file),
            "--source-url", "https://example.invalid/abra.png",
            "--usage-basis", "Curator-supplied reference photograph.",
            "--classification", "exact",
        ],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 1
    assert "set and number" in result.stderr
    assert (root / "data/card-images.yaml").read_bytes() == original_yaml
    assert asset_path.read_bytes() == original_asset


def test_crop_evidence_preserves_existing_asset_and_yaml_when_manifest_write_fails(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    original_yaml, original_asset, asset_path = seed_existing_proxy_image(root)
    source = root / "docs/evidence/2026-09-22/crop-source.png"
    write_image(source, color=(255, 0, 0))

    def fail_write(root_arg, images):
        raise OSError("simulated manifest write failure")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images.digital_binder, "write_image_manifest_atomically", fail_write)

    args = argparse.Namespace(
        card_id="abra-01",
        source=str(source),
        box="1,1,8,9",
        reviewed_on="2026-09-22",
    )
    try:
        manage_card_images.crop_evidence_command(args)
    except OSError as exc:
        assert "simulated" in str(exc)
    else:
        raise AssertionError("manifest write failure should reject crop update")

    assert (root / "data/card-images.yaml").read_bytes() == original_yaml
    assert asset_path.read_bytes() == original_asset


def test_approve_local_cli_writes_asset_and_reviewed_mapping(tmp_path):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    image_file = tmp_path / "local.png"
    write_image(image_file)

    result = subprocess.run(
        [
            sys.executable, str(Path(__file__).with_name("manage-card-images.py")),
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
            sys.executable, str(Path(__file__).with_name("manage-card-images.py")),
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
            sys.executable, str(Path(__file__).with_name("manage-card-images.py")),
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
    assert record["crop_box"] == [1, 1, 8, 9]
    assert record["reviewed_on"] == "2026-09-22"


def test_image_manifest_allows_legacy_evidence_crop_without_crop_box(tmp_path):
    root = project_fixture(tmp_path, image_classification="photo-crop")
    images = load_images(root)
    images["cards"]["abra-01"].update({
        "provider": "evidence-crop",
        "source_path": EVIDENCE_SOURCE,
    })
    images["cards"]["abra-01"].pop("source_url", None)
    errors = digital_binder.validate_image_manifest(root, images)

    assert errors == []


def test_image_manifest_rejects_malformed_evidence_crop_box(tmp_path):
    root = project_fixture(tmp_path, image_classification="photo-crop")
    images = load_images(root)
    record = images["cards"]["abra-01"]
    record.update({
        "provider": "evidence-crop",
        "source_path": EVIDENCE_SOURCE,
    })
    record.pop("source_url", None)

    bad_boxes = [
        [0, 0, 5],
        [0, 0, 0, 5],
        [0, 0, 5, 0],
        [0, 0, 5, 5.5],
        [0, False, 5, 5],
        [-1, 0, 5, 5],
    ]
    for box in bad_boxes:
        record["crop_box"] = box
        errors = digital_binder.validate_image_manifest(root, images)
        assert any("crop_box" in error for error in errors), box


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


def test_card_leaf_accepts_declared_two_by_four_geometry(tmp_path):
    root = project_fixture(
        tmp_path,
        pockets=[confirmed_pocket("abra-01")] + [empty_pocket(i) for i in range(2, 9)],
    )
    volume = load_volume(root)
    volume["pocket_layout"] = {"rows": 2, "columns": 4}
    write_volume(root, volume)
    write_current_generated(root)

    assert digital_binder.validate_project(root) == []


def test_card_leaf_rejects_invalid_declared_geometry(tmp_path):
    root = project_fixture(tmp_path)
    volume = load_volume(root)
    volume["pocket_layout"] = {"rows": True, "columns": 4}
    write_volume(root, volume)

    errors = digital_binder.validate_project(root)
    assert any("pocket_layout.rows" in error and "positive integer" in error for error in errors)


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


def test_confirmed_to_empty_requires_pending_state(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    current = project_manifest(pockets=[empty_pocket(position) for position in range(1, 10)])

    errors = digital_binder.validate_transition(previous, current)

    assert any("removed without pending state" in error for error in errors)


def test_confirmed_to_removed_pocket_requires_pending_state(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    current = project_manifest(pockets=[empty_pocket(position) for position in range(2, 10)])

    errors = digital_binder.validate_transition(previous, current)

    assert any("removed without pending state" in error for error in errors)


def test_confirmed_to_removed_leaf_requires_pending_state(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    current = project_manifest(leaves=[])

    errors = digital_binder.validate_transition(previous, current)

    assert any("removed without pending state" in error for error in errors)


def test_direct_confirmed_move_reports_removal_and_appearance(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    moved = confirmed_pocket("abra-01")
    moved["position"] = 2
    current = project_manifest(
        pockets=[empty_pocket(1), moved] + [empty_pocket(position) for position in range(3, 10)]
    )

    errors = digital_binder.validate_transition(previous, current)

    assert any("physical_leaf 1 pocket 1" in error and "removed without pending" in error
               for error in errors)
    assert any("physical_leaf 1 pocket 2" in error and "appeared without pending" in error
               for error in errors)


def test_confirmed_card_appearing_in_empty_pocket_requires_pending_state(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    new_card = confirmed_pocket("kadabra-01")
    new_card["position"] = 2
    current = project_manifest(
        pockets=[confirmed_pocket("abra-01"), new_card]
                + [empty_pocket(position) for position in range(3, 10)]
    )

    errors = digital_binder.validate_transition(previous, current)

    assert any("physical_leaf 1 pocket 2" in error and "appeared without pending" in error
               for error in errors)


def test_pending_to_removed_pocket_is_allowed_final_removal(tmp_path):
    previous = pending_project(tmp_path, card_id="kadabra-01", observed_card_id="abra-01")
    current = project_manifest(pockets=[empty_pocket(position) for position in range(1, 10)])

    assert digital_binder.validate_transition(previous, current) == []


def test_empty_to_pending_is_allowed_staging(tmp_path):
    previous = project_manifest(pockets=[empty_pocket(position) for position in range(1, 10)])
    current = pending_project(tmp_path, card_id="kadabra-01", observed_card_id="abra-01")

    assert digital_binder.validate_transition(previous, current) == []


def test_pending_replacement_lifecycle_can_confirm_new_card(tmp_path):
    previous = confirmed_project(tmp_path, card_id="abra-01")
    pending = pending_project(tmp_path, card_id="kadabra-01", observed_card_id="abra-01")
    confirmed = confirmed_project(tmp_path, card_id="kadabra-01")

    assert digital_binder.validate_transition(previous, pending) == []
    assert digital_binder.validate_transition(pending, confirmed) == []


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


def test_integer_schema_fields_reject_booleans(tmp_path):
    root = project_fixture(tmp_path)
    volume = load_volume(root)
    leaf = volume["leaves"][0]
    leaf["physical_leaf"] = True
    leaf["chapter_order"] = True
    leaf["theme_page"] = True
    leaf["pockets"][0]["position"] = True
    write_volume(root, volume)

    errors = digital_binder.validate_project(root)

    assert any("physical_leaf" in error and "integer" in error for error in errors)
    assert any("chapter_order" in error and "positive integer" in error for error in errors)
    assert any("theme_page" in error and "positive integer" in error for error in errors)
    assert any("pocket position" in error and "1-9" in error for error in errors)


def test_malformed_enum_values_report_errors_not_type_errors(tmp_path):
    root = project_fixture(tmp_path, image_classification="exact", transition_pockets=[])
    volume = load_volume(root)
    volume["publication_status"] = ["published"]
    volume["leaves"][0]["kind"] = {"cards": True}
    volume["leaves"][1].pop("pockets")
    volume["leaves"][1]["role"] = ["chapter"]
    write_volume(root, volume)
    images = load_images(root)
    images["cards"]["abra-01"]["classification"] = {"exact": True}
    write_images(root, images)

    errors = digital_binder.validate_project(root)

    assert any("publication_status" in error for error in errors)
    assert any("leaf kind" in error for error in errors)
    assert any("transition role" in error for error in errors)
    assert any("classification" in error for error in errors)


def test_transition_leaf_requires_heading_and_string_copy(tmp_path):
    root = project_fixture(tmp_path, transition_pockets=[])
    volume = load_volume(root)
    transition = volume["leaves"][1]
    transition.pop("pockets")
    transition["heading"] = ""
    transition["copy"] = ["not", "copy"]
    write_volume(root, volume)

    errors = digital_binder.validate_project(root)

    assert any("heading" in error and "nonempty string" in error for error in errors)
    assert any("copy" in error and "string" in error for error in errors)


def test_placement_evidence_requires_strings_valid_date_and_existing_relative_source(tmp_path):
    root = project_fixture(tmp_path)
    volume = load_volume(root)
    evidence = volume["leaves"][0]["pockets"][0]["placement"]["evidence"]
    evidence["type"] = ["published-photo"]
    evidence["source"] = "../outside.webp"
    evidence["observed_on"] = "2026-02-30"
    write_volume(root, volume)

    errors = digital_binder.validate_project(root)

    assert any("evidence" in error and "type" in error and "nonempty string" in error
               for error in errors)
    assert any("evidence" in error and "source" in error and "relative" in error
               for error in errors)
    assert any("observed_on" in error and "YYYY-MM-DD" in error for error in errors)


def test_confirmed_placement_rejects_pending_only_keys(tmp_path):
    root = project_fixture(tmp_path)
    placement = load_volume(root)["leaves"][0]["pockets"][0]["placement"]
    placement["observed_card_id"] = "abra-01"
    placement["physical_state_unknown"] = True
    placement["note"] = "General curatorial note remains allowed."
    volume = load_volume(root)
    volume["leaves"][0]["pockets"][0]["placement"] = placement
    write_volume(root, volume)

    errors = digital_binder.validate_project(root)

    assert any("confirmed placement" in error and "observed_card_id" in error for error in errors)
    assert any("confirmed placement" in error and "physical_state_unknown" in error
               for error in errors)
    assert not any("confirmed placement" in error and "note" in error for error in errors)


def test_image_manifest_rejects_malicious_asset_and_evidence_paths(tmp_path):
    root = project_fixture(tmp_path, image_classification="photo-crop")
    images = load_images(root)
    record = images["cards"]["abra-01"]
    record.update({
        "asset_path": "../assets/images/cards/abra-01.webp",
        "provider": "evidence-crop",
        "source_path": "/docs/evidence/source.webp",
    })
    write_images(root, images)

    errors = digital_binder.validate_project(root)

    assert any("asset_path" in error and "assets/images/cards" in error for error in errors)
    assert any("source_path" in error and "docs/evidence" in error for error in errors)


def test_image_manifest_requires_real_review_date_and_existing_crop_source(tmp_path):
    root = project_fixture(tmp_path, image_classification="photo-crop")
    images = load_images(root)
    record = images["cards"]["abra-01"]
    record.update({
        "provider": "evidence-crop",
        "source_path": "docs/evidence/2026-09-22/missing-source.webp",
        "reviewed_on": "2026-02-30",
    })
    write_images(root, images)

    errors = digital_binder.validate_project(root)

    assert any("reviewed_on" in error and "YYYY-MM-DD" in error for error in errors)
    assert any("source_path" in error and "missing" in error for error in errors)


def test_load_previous_manifests_verifies_ref_and_uses_git_show_for_each_volume(tmp_path, monkeypatch):
    calls = []

    def fake_run(command, check, capture_output, text, cwd):
        calls.append((command, check, capture_output, text, cwd))
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            source = "" if command[4].endswith(("/waifu.yaml", "/stamped-cards.yaml")) else command[4] + "\n"
            return subprocess.CompletedProcess(command, 0, stdout=source, stderr="")
        if command[:2] == ["git", "show"]:
            volume_id = command[2].split("/")[-1].removesuffix(".yaml")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=yaml.safe_dump(project_manifest()[volume_id]),
                stderr="",
            )
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", fake_run)
    errors = []

    manifests = digital_binder._load_previous_manifests(tmp_path, "main", errors)

    assert errors == []
    assert manifests["volume-1"]["volume_id"] == "volume-1"
    assert [call[0] for call in calls] == [
        ["git", "rev-parse", "--verify", "main^{commit}"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/volume-1.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/volume-2.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/waifu.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/stamped-cards.yaml"],
        ["git", "show", "abc123:data/binders/volume-1.yaml"],
        ["git", "show", "abc123:data/binders/volume-2.yaml"],
    ]
    assert all(call[4] == tmp_path for call in calls)


def test_validate_project_rejects_unsafe_previous_ref_without_git(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("git should not be called for an unsafe ref")

    monkeypatch.setattr(digital_binder.subprocess, "run", fail_if_called)

    errors = digital_binder.validate_project(root, previous_ref="-bad")

    assert any("invalid previous_ref" in error and "-bad" in error for error in errors)


def test_validate_project_rejects_unresolved_previous_ref_with_git_context(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def invalid_ref(command, check, capture_output, text, cwd):
        assert command == ["git", "rev-parse", "--verify", "origin/missing^{commit}"]
        raise subprocess.CalledProcessError(
            128, command, stderr="fatal: Needed a single revision"
        )

    monkeypatch.setattr(digital_binder.subprocess, "run", invalid_ref)

    errors = digital_binder.validate_project(root, previous_ref="origin/missing")

    assert any("previous_ref" in error and "origin/missing" in error
               and "Needed a single revision" in error for error in errors)


def test_validate_project_skips_valid_previous_commit_with_absent_manifest_but_keeps_current_validation(
        tmp_path, monkeypatch):
    root = project_fixture(tmp_path, pockets=[confirmed_pocket("abra-01")])

    def missing_manifest(command, check, capture_output, text, cwd):
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            return subprocess.CompletedProcess(command, 0, stdout="", stderr="")
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", missing_manifest)

    errors = digital_binder.validate_project(root, previous_ref="main")

    assert any("exactly 9 pockets" in error for error in errors)
    assert not any("previous" in error for error in errors)


def test_validate_project_rejects_partially_missing_previous_manifests(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def partial_manifests(command, check, capture_output, text, cwd):
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            output = command[4] + "\n" if command[4].endswith("volume-1.yaml") else ""
            return subprocess.CompletedProcess(command, 0, stdout=output, stderr="")
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", partial_manifests)

    errors = digital_binder.validate_project(root, previous_ref="main")

    assert any("incomplete binder manifests" in error and "volume-2" in error
               for error in errors)


def test_validate_project_fails_closed_when_previous_tree_inspection_fails(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def tree_failure(command, check, capture_output, text, cwd):
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            raise subprocess.CalledProcessError(128, command, stderr="fatal: bad tree")
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", tree_failure)

    errors = digital_binder.validate_project(root, previous_ref="main")

    assert any("inspect previous manifest path" in error and "bad tree" in error
               for error in errors)


def test_validate_project_fails_closed_when_git_show_fails(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def show_failure(command, check, capture_output, text, cwd):
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            return subprocess.CompletedProcess(command, 0, stdout=command[4] + "\n", stderr="")
        if command[:2] == ["git", "show"]:
            raise subprocess.CalledProcessError(128, command, stderr="fatal: object corrupt")
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", show_failure)

    errors = digital_binder.validate_project(root, previous_ref="main")

    assert any("previous volume-1 manifest" in error and "object corrupt" in error
               for error in errors)


def test_validate_project_reports_malformed_previous_yaml(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)

    def malformed_previous(command, check, capture_output, text, cwd):
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            return subprocess.CompletedProcess(command, 0, stdout=command[4] + "\n", stderr="")
        if command[:2] == ["git", "show"]:
            return subprocess.CompletedProcess(command, 0, stdout="- not\n- a mapping\n", stderr="")
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", malformed_previous)

    errors = digital_binder.validate_project(root, previous_ref="main")

    assert any("previous volume-1 manifest" in error and "YAML mapping" in error
               for error in errors)


def test_check_passes_previous_ref_to_git_loader(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    calls = []

    def fake_run(command, check, capture_output, text, cwd):
        calls.append(command)
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            source = "" if command[4].endswith(("/waifu.yaml", "/stamped-cards.yaml")) else command[4] + "\n"
            return subprocess.CompletedProcess(command, 0, stdout=source, stderr="")
        if command[:2] == ["git", "show"]:
            volume_id = command[2].split("/")[-1].removesuffix(".yaml")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=yaml.safe_dump(project_manifest()[volume_id]),
                stderr="",
            )
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", fake_run)

    rc = digital_binder.main(["--check", "--root", str(root), "--previous-ref", "main"])

    assert rc == 0
    assert calls == [
        ["git", "rev-parse", "--verify", "main^{commit}"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/volume-1.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/volume-2.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/waifu.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/stamped-cards.yaml"],
        ["git", "show", "abc123:data/binders/volume-1.yaml"],
        ["git", "show", "abc123:data/binders/volume-2.yaml"],
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
    assert [volume["publication_status"] for volume in volumes] == ["published", "published"]
    assert len(leaves) == 30
    assert len(card_leaves) == 19
    assert len(occupied) == 171
    assert len({pocket["card_id"] for pocket in occupied}) == 171


def test_printable_exact_image_checklist_matches_published_non_exact_cards():
    root = Path(__file__).parents[1]
    images = digital_binder.load_yaml(root / "data/card-images.yaml")["cards"]
    expected_by_volume = {}
    for volume_id in ("volume-1", "volume-2"):
        volume = digital_binder.load_yaml(root / f"data/binders/{volume_id}.yaml")
        expected_by_volume[volume_id] = [
            pocket["card_id"]
            for leaf in volume["leaves"]
            for pocket in leaf.get("pockets", [])
            if pocket.get("card_id")
            and images[pocket["card_id"]]["classification"] != "exact"
        ]

    checklist = (
        root / "docs/2026-09-24-digital-binder-exact-image-checklist.tex"
    ).read_text(encoding="utf-8")
    listed_ids = re.findall(r"\\cardrow\{([^}]+)\}", checklist)

    assert expected_by_volume == {
        "volume-1": listed_ids[:8],
        "volume-2": listed_ids[8:],
    }
    assert len(listed_ids) == len(set(listed_ids)) == 11
    assert sum(
        images[card_id]["classification"] == "photo-crop" for card_id in listed_ids
    ) == 10
    assert sum(images[card_id]["classification"] == "proxy" for card_id in listed_ids) == 1
    assert not any(images[card_id]["classification"] == "missing" for card_id in listed_ids)


def test_seeded_repository_has_curator_replacement_images_and_clean_crops():
    root = Path(__file__).parents[1]
    images = digital_binder.load_yaml(root / "data/card-images.yaml")["cards"]
    expected_doubleholo = {
        "charizard-03": "30828",
        "lucario-02": "7329",
        "ursaring-01": "38276",
        "dragonite-03": "30862",
        "mudkip-02": "76339",
        "litleo-01": "31512",
    }
    for card_id, upstream_id in expected_doubleholo.items():
        record = images[card_id]
        assert record["classification"] == "exact"
        assert record["provider"] == "doubleholo"
        assert record["upstream_id"] == upstream_id
        assert record["usage_basis"] == "Owner-authorized DoubleHolo card catalog image."

    for card_id, source_name in {
        "marowak-01": "marowak.webp",
        "joltik-01": "joltik-chinese.jpg",
    }.items():
        record = images[card_id]
        assert record["classification"] == "exact"
        assert record["provider"] == "evidence-crop"
        assert record["source_path"].endswith(source_name)
        assert record["crop_box"]

    for card_id in ("ampharos-01", "umbreon-05", "ursaring-01"):
        record = images[card_id]
        assert record["classification"] == "exact"
        assert "cropped" in record["note"].casefold()


def test_seeded_repository_reflects_september_ledger_swaps():
    root = Path(__file__).parents[1]
    volumes = {
        "volume-1": digital_binder.load_yaml(root / "data/binders/volume-1.yaml"),
        "volume-2": digital_binder.load_yaml(root / "data/binders/volume-2.yaml"),
    }
    expected = {
        ("volume-1", 12, 2): ("blastoise-02", "docs/evidence/2026-09-21/after/IMG_7103.jpeg"),
        ("volume-1", 15, 5): ("charizard-03", "docs/evidence/2026-09-21/after/IMG_7102.jpeg"),
        ("volume-1", 15, 8): ("lucario-02", "docs/evidence/2026-09-21/after/IMG_7102.jpeg"),
        ("volume-2", 4, 7): ("ursaring-01", "docs/evidence/2026-09-21/after/IMG_7106.jpeg"),
        ("volume-2", 5, 6): ("dragonite-03", "docs/evidence/2026-09-21/after/IMG_7105.jpeg"),
        ("volume-2", 11, 7): ("mudkip-02", "docs/evidence/2026-09-21/after/IMG_7104.jpeg"),
        ("volume-2", 11, 9): ("litleo-01", "docs/evidence/2026-09-21/after/IMG_7104.jpeg"),
    }
    outgoing = {
        "ns-plan-01", "snorlax-02", "ursaring-02", "rockets-trap-01",
        "dratini-02", "kasumis-tears-01", "hoopa-02",
    }
    occupied = {}
    for volume_id, volume in volumes.items():
        for leaf in volume["leaves"]:
            if leaf["kind"] != "cards":
                continue
            for pocket in leaf["pockets"]:
                if "card_id" not in pocket:
                    continue
                key = (volume_id, leaf["physical_leaf"], pocket["position"])
                occupied[key] = pocket

    assert set(expected) <= set(occupied)
    for key, (card_id, source) in expected.items():
        pocket = occupied[key]
        evidence = pocket["placement"]["evidence"]
        assert pocket["card_id"] == card_id
        assert pocket["placement"]["status"] == "confirmed"
        assert evidence == {
            "type": "verified-after-photo",
            "source": source,
            "observed_on": "2026-09-21",
        }
    assert outgoing.isdisjoint({pocket["card_id"] for pocket in occupied.values()})


def test_seeded_repository_uses_source_specific_evidence_dates_and_crop_boxes():
    root = Path(__file__).parents[1]
    volumes = {
        "volume-1": digital_binder.load_yaml(root / "data/binders/volume-1.yaml"),
        "volume-2": digital_binder.load_yaml(root / "data/binders/volume-2.yaml"),
    }
    images = digital_binder.load_yaml(root / "data/card-images.yaml")
    affected_leaves = {
        ("volume-1", "v1-12"),
        ("volume-1", "v1-15"),
        ("volume-2", "v2-04"),
        ("volume-2", "v2-05"),
        ("volume-2", "v2-11"),
    }
    incoming = {
        ("volume-1", 12, 2): (
            "blastoise-02", "docs/evidence/2026-09-21/after/IMG_7103.jpeg", [168, 0, 305, 195]
        ),
        ("volume-1", 15, 5): (
            "charizard-03", "docs/evidence/2026-09-21/after/IMG_7102.jpeg", [168, 205, 305, 390]
        ),
        ("volume-1", 15, 8): (
            "lucario-02", "docs/evidence/2026-09-21/after/IMG_7102.jpeg", [168, 400, 305, 625]
        ),
        ("volume-2", 4, 7): (
            "ursaring-01", "docs/evidence/2026-09-21/after/IMG_7106.jpeg", [5, 400, 148, 625]
        ),
        ("volume-2", 5, 6): (
            "dragonite-03", "docs/evidence/2026-09-21/after/IMG_7105.jpeg", [315, 200, 462, 395]
        ),
        ("volume-2", 11, 7): (
            "mudkip-02", "docs/evidence/2026-09-21/after/IMG_7104.jpeg", [5, 400, 148, 625]
        ),
        ("volume-2", 11, 9): (
            "litleo-01", "docs/evidence/2026-09-21/after/IMG_7104.jpeg", [315, 400, 462, 625]
        ),
    }
    migration_prefix = "docs/evidence/2026-09-22/digital-binder-migration/published-gallery/"

    pockets_by_key = {}
    affected_migration_pockets = 0
    all_migration_pockets = 0
    after_photo_pockets = 0
    for volume_id, volume in volumes.items():
        for leaf in volume["leaves"]:
            if leaf["kind"] != "cards":
                continue
            for pocket in leaf["pockets"]:
                if "card_id" not in pocket:
                    continue
                key = (volume_id, leaf["physical_leaf"], pocket["position"])
                pockets_by_key[key] = pocket
                evidence = pocket["placement"]["evidence"]
                if evidence["source"].startswith(migration_prefix):
                    all_migration_pockets += 1
                    assert evidence["type"] == "published-photo"
                    assert evidence["observed_on"] == "2026-08-01"
                    if (volume_id, leaf["id"]) in affected_leaves:
                        affected_migration_pockets += 1
                elif evidence["source"].startswith("docs/evidence/2026-09-21/after/"):
                    after_photo_pockets += 1
                    assert evidence["type"] == "verified-after-photo"
                    assert evidence["observed_on"] == "2026-09-21"

    assert all_migration_pockets == 164
    assert affected_migration_pockets == 38
    assert after_photo_pockets == 7
    assert set(incoming) <= set(pockets_by_key)
    for key, (card_id, source, crop_box) in incoming.items():
        pocket = pockets_by_key[key]
        assert pocket["card_id"] == card_id
        assert pocket["placement"]["status"] == "confirmed"
        assert pocket["placement"]["evidence"] == {
            "type": "verified-after-photo",
            "source": source,
            "observed_on": "2026-09-21",
        }
        record = images["cards"][card_id]
        if card_id == "blastoise-02":
            assert record["provider"] == "evidence-crop"
            assert record["source_path"] == source
            assert record["crop_box"] == crop_box
        else:
            assert record["provider"] == "doubleholo"
            assert record["classification"] == "exact"


def parse_sha256sums(text):
    hashes = {}
    for line in text.splitlines():
        digest, relative = line.split(maxsplit=1)
        hashes[relative] = digest
    return hashes


IMMUTABLE_MIGRATION_SHA256SUMS = """8f1937eca91396c3bd76f4347a8d98d37183d0b94323670e9aeb211f9c4d80db  published-gallery/volume-1/at_rest_1.webp
fa29aead511286a22e6847f0f7ac4101278965455c3b2d8b8244db70783c432c  published-gallery/volume-1/awakened_power_1.webp
09f24a9c69ada502ce35621382a495496fc36dfd1a53c84ad4ddab61da8e110c  published-gallery/volume-1/awakened_power_2.webp
5879a76c5fdee0a933e90a289a9e4f8e31397f78c61fee1c75c864dae5a11fb5  published-gallery/volume-1/calm_nature_1.webp
87f4e9999eadb9affe2d82b342ed12da343aeed26902e83b7adca88232380d26  published-gallery/volume-1/ch1_belonging_safety.webp
7bb6a322499f4c5b1bf9d78e2ead50575a14c0841f1d41a2c9cacdd2a073388e  published-gallery/volume-1/ch2_motion_life.webp
973b5ba5f3f25b8520553d85877c52bf10689edddd4d2629f00cf97c446192b0  published-gallery/volume-1/ch3_power_awakening.webp
0d3fb4e2cf74c0b9bf861250db4ebdd9968e2eccd5c6540e3496360c07fd89f2  published-gallery/volume-1/ch4_threat_conflict.webp
3f39b6fae093b30021c5d8f7983213a74484813c0332ced8ac216f349f44ce7c  published-gallery/volume-1/ch5_isolation_reflection.webp
34ebd1827758dc5d52a5dda8418df861fe18e6f717a0203c4ba186410590d3c7  published-gallery/volume-1/contemplation_1.webp
e21cacb2be02890748be8ab7bc790ca3fd86b93877c9bb4c87690dabf992b897  published-gallery/volume-1/elemental_solitude_1.webp
8780aa165eeb984c5f060cec02f5e331fa7b1b83f0d7462d8092c6cd34b70dca  published-gallery/volume-1/intimidation_1.webp
5b4889711d98d818e8ae1aa94a9b6a08c6a48d62d6407b6961d9d69cca4ee447  published-gallery/volume-1/joyful_action_1.webp
eb7bd2aba987e8820e077badeb6f135bc2176f2d7522da1a46c0fb7e15c32dd3  published-gallery/volume-1/legendary_bearing_1.webp
7ea94889faf9475c5798199691db3ec8455da42aeba7ed0a41e74d3eef6de26e  published-gallery/volume-1/legendary_bearing_2.webp
2c0faac7a7accbda5f0c7dddd58628844d80f0eb45a5f731736a788b141f33dc  published-gallery/volume-1/on_attack_1.webp
36e4d337510ab590b1033d3b1bb7b0254fad6ac52e2a56c45ac8f958ad42c06c  published-gallery/volume-1/vol1_contents.webp
f0851daf53dc7b92efb01b3d850a3ac6b158f5439e598799aa700126813a681a  published-gallery/volume-1/vol1_fin.webp
a3737b3a9e8cbbc34d641ac068aaa8f60b144feac8a30b49dbfe874c24c973fc  published-gallery/volume-1/world_people_1.webp
e49fde074a150c5928bcb5ed898bc385d0caa433d279a7d26d38e3827160d0d8  published-gallery/volume-2/ch1_nearness.webp
909302a345b0f184b6c7eacfcd9cac5cae1cf55525f271e72a1b735d24ac3046  published-gallery/volume-2/ch2_permanence.webp
ca9cd86eecf5f5f90e5faf6f2ccc9f17ebf3873c72c18e665bf805f5dc1f1868  published-gallery/volume-2/ch3_passage.webp
f43eb19b0afdb1486bc500f151b7bdffa092a1f9e67f4a2166027fdac9b53060  published-gallery/volume-2/companions_1.webp
f6b4607428f2255c70a52b51e202969a19051530510e546304d0ddbae9d639e5  published-gallery/volume-2/companions_2.webp
24a6b4f992595477e6f7878535a9f08fc57675dbd708c3d995d356c551058a7a  published-gallery/volume-2/enduring_presence_1.webp
4804f00ae33d69b08788ac81142a9f94afd321d12c1ce37bd7c9e697ff984066  published-gallery/volume-2/enduring_presence_2.webp
1212af60c8ae97afa1e090c0762c2d9f0a1f373deb9c98689dfac849e430b8b8  published-gallery/volume-2/quiet_familiarity_1.webp
c32bffb7ed6e1fe1a4045ec4aa87c49822a2780fd61c1d131c19789620ad0b87  published-gallery/volume-2/quiet_familiarity_2.webp
a5f6d2cefc323885e460fe2371dd99470ea3892fbd948c251575db90caca413b  published-gallery/volume-2/threshold_1.webp
ae52fcf0abc53c83e969a8b57763144c0e203c7e02af8d7d371df95594a729fe  published-gallery/volume-2/vol2_contents.webp
"""

REFRESHED_DERIVATIVE_SHA256SUMS = """6a09eabbfd0505df138e16ca058606a7ac9b4bf49ec9931614e42d126a5c968f  volume-1/legendary_bearing_2.webp
caeb04f62979c8c8e3553ebf8ecf3a32dd2abf12f10126cd76f2bc58f2098b14  volume-1/on_attack_1.webp
a20eb34db21c3ad4f70a4f1bbac059e6ecfb7c1e88554fabdd36c4d04ad3d0a4  volume-2/companions_2.webp
c812d60961f586d890f23880366f05cd50d5cbf552fc20a7288779e599997819  volume-2/quiet_familiarity_1.webp
73804c46cfdce1ebbd5bafa45e77497abd213a425a8721e3bf90dc93fc2175ec  volume-2/threshold_1.webp
"""


def assert_archive_hashes(root, expected_text):
    expected_hashes = parse_sha256sums(expected_text)
    sha_path = root / "SHA256SUMS"
    assert sha_path.read_text(encoding="utf-8") == expected_text
    assert parse_sha256sums(sha_path.read_text(encoding="utf-8")) == expected_hashes
    for relative, digest in expected_hashes.items():
        archived = root / relative
        assert archived.is_file(), f"missing archived evidence file: {relative}"
        assert hashlib.sha256(archived.read_bytes()).hexdigest() == digest


def test_public_cutover_removes_reconstructed_binder_photo_sources():
    root = Path(__file__).parents[1]
    photographed = root / "static/images/binder"
    evidence_root = root / "docs/evidence/2026-09-22/digital-binder-migration"
    published = evidence_root / "published-gallery"

    assert not (photographed / "volume-1").exists()
    assert not (photographed / "volume-2").exists()
    assert not (photographed / "stamped-cards").exists()
    assert "emolga-masterset" in {
        path.name for path in photographed.iterdir() if path.is_dir()
    }
    assert not (photographed / "waifu").exists()
    assert (root / "static/images/slabs").is_dir()

    assert_archive_hashes(evidence_root, IMMUTABLE_MIGRATION_SHA256SUMS)
    assert len(list((published / "volume-1").glob("*"))) == 19
    assert len(list((published / "volume-2").glob("*"))) == 11


def test_refreshed_public_derivatives_are_preserved_separately_from_migration_archive():
    root = Path(__file__).parents[1]
    evidence_root = root / "docs/evidence/2026-09-21"
    derivative_root = evidence_root / "published-gallery"
    readme = (derivative_root / "README.md").read_text(encoding="utf-8")

    assert "final public WebP derivatives" in readme
    assert "not camera originals" in readme
    assert "../after/" in readme
    assert_archive_hashes(derivative_root, REFRESHED_DERIVATIVE_SHA256SUMS)
    assert len(list((derivative_root / "volume-1").glob("*"))) == 2
    assert len(list((derivative_root / "volume-2").glob("*"))) == 3


class RenderedElementParser(HTMLParser):
    def __init__(self):
        super().__init__()
        self.elements = []

    def handle_starttag(self, tag, attrs):
        self.elements.append((tag, dict(attrs)))


def rendered_elements(html):
    parser = RenderedElementParser()
    parser.feed(html)
    return parser.elements


class BinderOwnershipParser(HTMLParser):
    VOID_ELEMENTS = {
        "area", "base", "br", "col", "embed", "hr", "img", "input",
        "link", "meta", "param", "source", "track", "wbr",
    }
    OWNED_ATTRIBUTES = {
        "data-binder-stage",
        "data-binder-spreads",
        "data-binder-controls",
        "data-card-inspector",
    }

    def __init__(self):
        super().__init__()
        self.stack = []
        self.owners = []

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        owner = attributes.get("data-binder")
        if owner is None and self.stack:
            owner = self.stack[-1][1]
        for attribute in self.OWNED_ATTRIBUTES:
            if attribute in attributes:
                self.owners.append((attribute, owner))
        if tag not in self.VOID_ELEMENTS:
            self.stack.append((tag, owner))

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                del self.stack[index:]
                return


def binder_owners(html):
    parser = BinderOwnershipParser()
    parser.feed(html)
    return parser.owners


class ArrowControlTextParser(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.text = {"previous": "", "next": ""}
        self.hidden_spans = {"previous": 0, "next": 0}

    def handle_starttag(self, tag, attrs):
        attributes = dict(attrs)
        current = self.stack[-1] if self.stack else None
        if "data-binder-prev" in attributes:
            current = "previous"
        elif "data-binder-next" in attributes:
            current = "next"
        if current and tag == "span" and attributes.get("aria-hidden") == "true":
            self.hidden_spans[current] += 1
        if tag not in BinderOwnershipParser.VOID_ELEMENTS:
            self.stack.append(current)

    def handle_data(self, data):
        current = self.stack[-1] if self.stack else None
        if current:
            self.text[current] += data

    def handle_endtag(self, tag):
        if self.stack:
            self.stack.pop()


def arrow_control_text(html):
    parser = ArrowControlTextParser()
    parser.feed(html)
    return {key: value.strip() for key, value in parser.text.items()}, parser.hidden_spans


def matching_brace(source, open_index):
    depth = 1
    for index in range(open_index + 1, len(source)):
        if source[index] == "{":
            depth += 1
        elif source[index] == "}":
            depth -= 1
            if depth == 0:
                return index
    raise AssertionError("unmatched CSS brace")


def iter_css_rules(source, active_media=None):
    position = 0
    while True:
        open_index = source.find("{", position)
        if open_index == -1:
            return
        selector = source[position:open_index].strip()
        close_index = matching_brace(source, open_index)
        body = source[open_index + 1:close_index]
        if selector.startswith("@media"):
            yield from iter_css_rules(body, selector)
        else:
            yield active_media, selector, body
        position = close_index + 1


def css_declarations(source, selector, *, media=None):
    merged = {}
    for active_media, selector_text, body in iter_css_rules(source):
        selector_parts = [part.strip() for part in selector_text.split(",")]
        if active_media == media and selector in selector_parts:
            merged.update({
                name.strip(): value.strip()
                for declaration in body.split(";")
                if ":" in declaration
                for name, value in [declaration.split(":", 1)]
            })
    if merged:
        return merged
    raise AssertionError(f"missing CSS rule for {selector!r} in {media!r}")


def css_px(value):
    assert value.endswith("px"), value
    return float(value[:-2])


def test_rendered_public_volume_routes_use_binder_markup_without_remote_card_images(tmp_path):
    root = Path(__file__).parents[1]
    destination = tmp_path / "public"

    result = subprocess.run(
        ["hugo", "--buildDrafts", "--destination", str(destination)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not (destination / "gallery/digital-binder-pilot/index.html").exists()

    volume_expectations = {
        "volume-1": {
            "intro": "Volume I is where it all started.",
            "leaf_count": 19,
            "last_leaf": "v1-17",
            "controls": {"#leaf-v1-01", "#leaf-v1-03"},
        },
        "volume-2": {
            "intro": "Volume II is less about action and more about memory",
            "leaf_count": 11,
            "last_leaf": "v2-11",
            "controls": {"#leaf-v2-01", "#leaf-v2-03"},
        },
    }
    for volume_id, expected in volume_expectations.items():
        html = (destination / f"gallery/{volume_id}/index.html").read_text(
            encoding="utf-8"
        )
        assert expected["intro"] in html
        assert 'unofficial fan project' in html
        assert 'TCGdex' in html
        assert 'DoubleHolo' in html
        assert f'data-binder="{volume_id}"' in html
        assert html.count('data-binder-leaf="') == expected["leaf_count"]
        assert f'data-binder-leaf="{expected["last_leaf"]}"' in html
        assert 'data-pocket-position="1"' in html
        assert '<dialog' in html
        assert '/images/binder/volume-' not in html
        assert not re.search(r'(?:src|srcset)="https://assets\.tcgdex\.net', html)
        assert 'srcset="' in html
        assert re.search(r'srcset="[^"]+ \d+w(?:, [^"]+ \d+w)?"', html)
        assert 'sizes="(max-width: 860px) 30vw, 180px"' in html
        assert 'data-inspector-src="' in html
        assert html.count('data-initial-binder-image') == html.count('loading="eager"')
        assert 'loading="lazy"' in html

        elements = rendered_elements(html)
        stages = [attrs for tag, attrs in elements
                  if tag == "div" and "data-binder-stage" in attrs]
        assert len(stages) == 1
        assert "binder-stage" in stages[0].get("class", "")
        spread_owners = [attrs for tag, attrs in elements
                         if tag == "div" and "data-binder-spreads" in attrs]
        assert len(spread_owners) == 1
        assert "binder-spreads" in spread_owners[0].get("class", "")
        controls = [attrs for tag, attrs in elements
                    if tag == "nav" and "data-binder-controls" in attrs]
        assert len(controls) == 1
        assert "binder-controls" in controls[0].get("class", "")
        control_links = [
            attrs for tag, attrs in elements
            if tag == "a"
            and ("data-binder-prev" in attrs or "data-binder-next" in attrs)
        ]
        assert len(control_links) == 2
        assert {link["href"] for link in control_links} == expected["controls"]
        assert {link["aria-label"] for link in control_links} == {"Previous page", "Next page"}
        assert html.count("data-binder-prev") == 1
        assert html.count("data-binder-next") == 1
        arrow_text, hidden_spans = arrow_control_text(html)
        assert arrow_text == {"previous": "‹", "next": "›"}
        assert hidden_spans == {"previous": 1, "next": 1}
        live_positions = [attrs for tag, attrs in elements
                          if tag == "p" and "data-binder-position" in attrs]
        assert len(live_positions) == 1
        assert live_positions[0].get("aria-live") == "polite"
        assert "hidden" not in live_positions[0]

        card_buttons = [attrs for tag, attrs in elements
                        if tag == "button" and "data-card-id" in attrs]
        assert card_buttons
        for button in card_buttons:
            assert button["data-card-name"]
            assert button["data-card-language"]
            assert "data-card-set" in button
            assert "data-card-number" in button
            assert button["data-leaf-theme"]
            assert button["data-pocket-position"]
            assert button["data-classification"] in {"exact", "photo-crop", "proxy", "missing"}
            assert button["data-placement-status"] in {"confirmed", "pending"}
            assert "data-image-provenance" in button
            assert "data-image-source" in button
            assert "data-image-note" in button
            assert "data-placement-observed-card-id" in button
            assert "data-placement-physical-state" in button
            assert "data-inspector-src" in button
            if button["data-classification"] == "missing":
                assert button["data-inspector-src"] == ""
            else:
                assert button["data-inspector-src"].startswith("/")

        assert "data-binder-legend" not in html
        assert "Active spread notes" not in html
        assert any(tag == "dialog" and "data-card-inspector" in attrs for tag, attrs in elements)
        assert binder_owners(html) == [
            ("data-binder-stage", volume_id),
            ("data-binder-controls", volume_id),
            ("data-binder-spreads", volume_id),
            ("data-card-inspector", volume_id),
        ]
        inspector_fields = {
            attrs.get("data-card-inspector-field")
            for tag, attrs in elements
            if attrs.get("data-card-inspector-field")
        }
        assert inspector_fields == {
            "language",
            "set-number",
            "theme-pocket",
            "image-classification",
            "image-source",
            "image-note",
            "placement",
        }
        assert any(tag == "img" and "data-card-inspector-image" in attrs
                   and "hidden" in attrs and "src" not in attrs for tag, attrs in elements)
        assert any(tag == "script" and "data-binder-script" in attrs and "defer" in attrs
                   for tag, attrs in elements)

    side_html = (destination / "gallery/waifu/index.html").read_text(encoding="utf-8")
    assert 'data-binder="waifu"' in side_html
    assert side_html.count('data-card-id="') == 29
    assert side_html.count('class="binder-pocket is-empty"') == 7
    assert 'data-binder-script' in side_html
    assert 'images/binder/waifu/' not in side_html

    slab_html = (destination / "gallery/touchstones/index.html").read_text(encoding="utf-8")
    assert 'data-binder="' not in slab_html
    assert 'data-binder-script' not in slab_html
    assert 'unofficial fan project' not in slab_html
    assert '../../images/slabs/touchstone_celebi_gold_star.jpg' in slab_html


def test_binder_interaction_assets_declare_accessible_contract():
    root = Path(__file__).parents[1]
    javascript = (root / "assets/js/binder.js").read_text(encoding="utf-8")
    stylesheet = (root / "assets/css/binder.css").read_text(encoding="utf-8")

    syntax = subprocess.run(
        ["node", "--check", str(root / "assets/js/binder.js")],
        capture_output=True,
        text=True,
    )
    assert syntax.returncode == 0, syntax.stderr
    assert ".innerHTML" not in javascript
    assert "textContent" in javascript
    assert 'setField("set-number", setNumber || "Unresolved")' in javascript
    assert 'window.matchMedia("(max-width: 720px)")' in javascript
    assert 'dialog.showModal()' in javascript
    assert 'dialog.addEventListener("cancel"' in javascript
    assert 'dialog.addEventListener("close"' in javascript
    assert 'event.key !== "Tab"' in javascript
    assert 'originFocus.focus()' in javascript
    assert 'image.removeAttribute("src")' in javascript
    assert 'const controls = root.querySelector("[data-binder-controls]")' in javascript
    assert "data-binder-legend" not in javascript
    assert "updateLegend" not in javascript
    assert 'const dialog = root.querySelector("[data-card-inspector]")' in javascript
    assert 'if (!hasRequiredInspectorParts()) return;' in javascript
    assert 'fields.get(field).textContent = value;' not in javascript
    assert 'document.querySelector("[data-binder-controls]")' not in javascript
    assert 'document.querySelector("[data-card-inspector]")' not in javascript
    assert "focusedAdjacentControl.disabled" in javascript
    assert "focusedAdjacentControl.focus()" not in javascript
    assert "@media (max-width: 720px)" in stylesheet
    assert "@media (prefers-reduced-motion: reduce)" in stylesheet
    assert "transition: none !important" in stylesheet
    assert ".binder-stage" in stylesheet
    assert ".binder-spreads" in stylesheet

    prev_base = css_declarations(stylesheet, ".binder-controls [data-binder-prev]")
    next_base = css_declarations(stylesheet, ".binder-controls [data-binder-next]")
    for declarations in (prev_base, next_base):
        assert declarations["min-width"] == "2.75rem"
        assert declarations["min-height"] == "2.75rem"
    assert prev_base["grid-column"] == "1"
    assert next_base["grid-column"] == "3"

    focus = css_declarations(stylesheet, ".binder-controls a:focus-visible")
    assert focus["outline"].startswith("3px solid")

    ready_controls = css_declarations(
        stylesheet, '.binder[data-binder-ready="true"] .binder-controls'
    )
    assert ready_controls["position"] == "absolute"
    assert ready_controls["inset"] == "0"
    assert ready_controls["pointer-events"] == "none"
    assert "position" not in css_declarations(stylesheet, ".binder-controls")

    ready_prev = css_declarations(
        stylesheet, '.binder[data-binder-ready="true"] .binder-controls [data-binder-prev]'
    )
    ready_next = css_declarations(
        stylesheet, '.binder[data-binder-ready="true"] .binder-controls [data-binder-next]'
    )
    for declarations in (ready_prev, ready_next):
        assert declarations["position"] == "absolute"
        assert declarations["top"] == "50%"
        assert declarations["transform"] == "translateY(-50%)"
        assert declarations["pointer-events"] == "auto"
    assert ready_prev["left"] == "0"
    assert ready_next["right"] == "0"

    position_copy = css_declarations(stylesheet, ".binder-controls [data-binder-position]")
    assert position_copy["position"] == "absolute"
    assert css_px(position_copy["width"]) <= 1
    assert css_px(position_copy["height"]) <= 1
    assert position_copy["overflow"] == "hidden"
    assert position_copy["pointer-events"] == "none"
    assert position_copy.get("display") != "none"
    assert position_copy.get("visibility") != "hidden"
    assert position_copy.get("clip", "auto") != "auto" or position_copy.get("clip-path", "none") != "none"

    stage = css_declarations(stylesheet, '.binder[data-binder-ready="true"] .binder-stage')
    assert stage["padding-inline"] == "clamp(3.5rem, 6vw, 5rem)"
    tablet_stage = css_declarations(
        stylesheet,
        '.binder[data-binder-ready="true"] .binder-stage',
        media="@media (max-width: 900px)",
    )
    assert tablet_stage["padding-inline"] == "clamp(3rem, 7vw, 4rem)"
    mobile_stage = css_declarations(
        stylesheet,
        '.binder[data-binder-ready="true"] .binder-stage',
        media="@media (max-width: 720px)",
    )
    assert mobile_stage["padding-inline"] == "clamp(2.75rem, 10vw, 3.35rem)"


def test_binder_javascript_updates_live_status_and_hash_functionally():
    root = Path(__file__).parents[1]
    result = subprocess.run(
        ["node", str(root / "scripts/test_binder_js_behavior.mjs")],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr


@pytest.mark.parametrize("rows, columns", [(3, 3), (2, 4)])
def test_rendered_synthetic_binder_marks_only_first_spread_images_eager(tmp_path, rows, columns):
    root = Path(__file__).parents[1]
    site = tmp_path / "site"
    destination = tmp_path / "public"
    shutil.copytree(root / "layouts", site / "layouts")
    shutil.copytree(root / "assets/css", site / "assets/css")
    shutil.copytree(root / "assets/js", site / "assets/js")
    (site / "content/gallery/digital-binder-pilot").mkdir(parents=True)
    (site / "content/gallery/digital-binder-pilot/_index.md").write_text(
        "---\n"
        "title: Synthetic Binder\n"
        "draft: true\n"
        "binder: volume-1\n"
        "---\n",
        encoding="utf-8",
    )
    (site / "hugo.toml").write_text(
        "baseURL = 'https://example.invalid/'\n"
        "languageCode = 'en-us'\n"
        "title = 'Synthetic Binder'\n"
        "disableKinds = ['home']\n",
        encoding="utf-8",
    )

    card_ids = [
        "first-leaf-card",
        "second-leaf-card",
        "third-leaf-card",
        "missing-card",
    ]
    registry = {
        card_id: {
            "id": card_id,
            "card_name": card_id.replace("-", " ").title(),
            "language": "EN",
            "set": "Fixture Set",
            "number": str(index),
        }
        for index, card_id in enumerate(card_ids, start=1)
    }
    (site / "data/generated").mkdir(parents=True)
    (site / "data/generated/card-registry.json").write_text(
        json.dumps(registry, indent=2) + "\n",
        encoding="utf-8",
    )
    classifications = {
        "first-leaf-card": "exact",
        "second-leaf-card": "proxy",
        "third-leaf-card": "photo-crop",
        "missing-card": "missing",
    }
    image_records = {}
    for card_id, classification in classifications.items():
        image_records[card_id] = {
            "classification": classification,
            "asset_path": (
                "" if classification == "missing"
                else f"assets/images/cards/{card_id}.webp"
            ),
            "reviewed": classification != "missing",
            "reviewed_on": "" if classification == "missing" else "2026-09-22",
            "provider": "" if classification == "missing" else "fixture",
            "source_url": (
                "" if classification == "missing"
                else "https://example.invalid/card.webp"
            ),
            "note": "Different printing used for reference" if classification == "proxy" else "",
        }
    (site / "data").joinpath("card-images.yaml").write_text(
        yaml.safe_dump({"version": 1, "cards": image_records}, sort_keys=False),
        encoding="utf-8",
    )
    for card_id in card_ids:
        if classifications[card_id] != "missing":
            write_image(site / "assets/images/cards" / f"{card_id}.webp", size=(500, 700))

    leaves = []
    for index, card_id in enumerate(card_ids[:3], start=1):
        first_pocket = (
            pending_pocket(card_id, physical_state_unknown=True)
            if card_id == "second-leaf-card"
            else confirmed_pocket(card_id)
        )
        pockets = [first_pocket]
        if card_id == "third-leaf-card":
            missing = confirmed_pocket("missing-card")
            missing["position"] = 2
            pockets.append(missing)
        pockets.extend(empty_pocket(position) for position in range(len(pockets) + 1, rows * columns + 1))
        leaves.append({
            "id": f"leaf-{index}",
            "kind": "cards",
            "physical_leaf": index,
            "chapter": "Fixture Chapter",
            "chapter_order": 1,
            "theme": f"Leaf {index}",
            "pockets": pockets,
        })
    (site / "data/binders").mkdir(parents=True)
    (site / "data/binders/volume-1.yaml").write_text(
        yaml.safe_dump({
            "version": 1,
            "volume_id": "volume-1",
            "publication_status": "draft",
            "pocket_layout": {"rows": rows, "columns": columns},
            "leaves": leaves,
        }, sort_keys=False),
        encoding="utf-8",
    )

    result = subprocess.run(
        ["hugo", "--buildDrafts", "--destination", str(destination)],
        cwd=site,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    assert not (destination / "index.html").exists()
    html = (destination / "gallery/digital-binder-pilot/index.html").read_text(
        encoding="utf-8"
    )
    elements = rendered_elements(html)
    binder = next(attrs for _, attrs in elements if attrs.get("data-binder") == "volume-1")
    assert binder["data-pocket-rows"] == str(rows)
    assert binder["data-pocket-columns"] == str(columns)
    assert binder["style"] == f"--binder-pocket-columns: {columns}; --binder-pocket-rows: {rows}"
    assert len([attrs for _, attrs in elements if "data-pocket" in attrs]) == 3 * rows * columns
    first = re.search(
        r'data-card-id="first-leaf-card"(?P<body>.*?)</button>', html, re.S
    ).group("body")
    second = re.search(
        r'data-card-id="second-leaf-card"(?P<body>.*?)</button>', html, re.S
    ).group("body")
    third = re.search(
        r'data-card-id="third-leaf-card"(?P<body>.*?)</button>', html, re.S
    ).group("body")
    assert 'loading="eager"' in first
    assert 'data-initial-binder-image' in first
    assert 'loading="eager"' in second
    assert 'data-initial-binder-image' in second
    assert 'loading="lazy"' in third
    assert 'data-initial-binder-image' not in third
    assert 'data-classification="exact"' in html
    assert 'data-classification="photo-crop"' in html
    assert 'Reference image' in html
    assert 'Image unavailable' in html
    assert 'Placement pending' in html
    assert second.count('class="pocket-states"') == 1
    assert second.count('class="pocket-state"') == 2
    assert "reference image" in second
    assert "placement pending" in second


def write_html_at(root: Path, relative_path: str, body: str) -> None:
    page = root / relative_path
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(body, encoding="utf-8")


def write_html(root: Path, body: str) -> None:
    write_html_at(root, "gallery/volume-1/index.html", body)


def valid_public_binder_html(volume_id="volume-1", leaf_prefix="v1") -> str:
    inspector_fields = "".join(
        f'<dd data-card-inspector-field="{field}"></dd>'
        for field in (
            "language",
            "set-number",
            "theme-pocket",
            "image-classification",
            "image-source",
            "image-note",
            "placement",
        )
    )

    def card_leaf(leaf_id: str, image_name: str, *, initial: bool) -> str:
        loading = "eager" if initial else "lazy"
        initial_attribute = " data-initial-binder-image" if initial else ""
        empty_pockets = "".join(
            f'<div data-pocket data-pocket-position="{position}"></div>'
            for position in range(2, 10)
        )
        return (
            f'<section id="leaf-{leaf_id}" data-binder-leaf="{leaf_id}" data-kind="cards">'
            '<div class="binder-pockets">'
            '<button data-pocket data-pocket-position="1" data-card-id="abra-01" '
            'data-inspector-src="/images/cards/inspector.webp">'
            f'<img src="/images/cards/{image_name}" alt="Abra, Base Set 43/102" '
            f'loading="{loading}"{initial_attribute}>'
            '</button>'
            f'{empty_pockets}'
            '</div>'
            '</section>'
        )

    return (
        '<!doctype html><html><body>'
        f'<div data-binder="{volume_id}">'
        '<div class="binder-stage" data-binder-stage>'
        '<nav class="binder-controls" data-binder-controls aria-label="Binder pages">'
        f'<a data-binder-prev href="#leaf-{leaf_prefix}-01" aria-label="Previous page">'
        '<span aria-hidden="true">&#8249;</span></a>'
        '<p data-binder-position aria-live="polite"></p>'
        f'<a data-binder-next href="#leaf-{leaf_prefix}-03" aria-label="Next page">'
        '<span aria-hidden="true">&#8250;</span></a>'
        '</nav>'
        '<div class="binder-spreads" data-binder-spreads>'
        '<div data-binder-spread="1">'
        f'{card_leaf(f"{leaf_prefix}-01", "one.webp", initial=True)}'
        f'{card_leaf(f"{leaf_prefix}-02", "two.webp", initial=True)}'
        '</div>'
        '<div data-binder-spread="2">'
        f'{card_leaf(f"{leaf_prefix}-03", "three.webp", initial=False)}'
        f'<section id="leaf-{leaf_prefix}-04" data-binder-leaf="{leaf_prefix}-04" data-kind="transition"></section>'
        '</div>'
        '</div>'
        '</div>'
        f'<dialog id="card-inspector-{volume_id}" data-card-inspector>'
        '<button data-card-inspector-close>Close</button>'
        '<button data-card-inspector-previous>Previous card</button>'
        '<button data-card-inspector-next>Next card</button>'
        '<img data-card-inspector-image alt="" hidden>'
        '<h2 data-card-inspector-name></h2>'
        f'<dl>{inspector_fields}</dl>'
        '</dialog>'
        '</div>'
        '</body></html>'
    )


def write_public_card_assets(root: Path) -> None:
    for name in ("one.webp", "two.webp", "three.webp", "inspector.webp"):
        asset = root / "images/cards" / name
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(b"fixture image")


def write_valid_public_binder(root: Path) -> None:
    write_html(root, valid_public_binder_html())
    write_public_card_assets(root)


def write_valid_strict_public_binders(root: Path) -> None:
    write_html_at(
        root,
        "gallery/volume-1/index.html",
        valid_public_binder_html("volume-1", "v1"),
    )
    write_html_at(
        root,
        "gallery/volume-2/index.html",
        valid_public_binder_html("volume-2", "v2"),
    )
    write_html_at(
        root,
        "gallery/emolga-masterset/index.html",
        valid_public_binder_html("emolga-masterset", "em"),
    )
    write_html_at(
        root,
        "gallery/waifu/index.html",
        valid_public_binder_html("waifu", "trainer"),
    )
    write_html_at(
        root,
        "gallery/stamped-cards/index.html",
        valid_public_binder_html("stamped-cards", "stamp"),
    )
    write_public_card_assets(root)


def test_public_check_rejects_remote_card_image_url(tmp_path):
    html = valid_public_binder_html().replace(
        "/images/cards/one.webp",
        "https://assets.tcgdex.net/en/base/base1/4/high.webp",
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("remote card image" in error for error in errors)


def test_public_check_requires_nine_pockets_per_card_leaf(tmp_path):
    html = valid_public_binder_html().replace(
        '<div data-pocket data-pocket-position="9"></div>',
        "",
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("9 pockets" in error for error in errors)


def test_public_check_accepts_declared_two_by_four_geometry(tmp_path):
    html = valid_public_binder_html().replace(
        'data-binder="volume-1"',
        'data-binder="volume-1" data-pocket-rows="2" data-pocket-columns="4"',
    ).replace('<div data-pocket data-pocket-position="9"></div>', '')
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    assert digital_binder.validate_public_output(tmp_path) == []


def test_public_check_rejects_wrong_count_for_declared_geometry(tmp_path):
    html = valid_public_binder_html().replace(
        'data-binder="volume-1"',
        'data-binder="volume-1" data-pocket-rows="2" data-pocket-columns="4"',
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(tmp_path)
    assert any("exactly 8 pockets" in error for error in errors)


def test_public_check_rejects_invalid_geometry(tmp_path):
    html = valid_public_binder_html().replace(
        'data-binder="volume-1"',
        'data-binder="volume-1" data-pocket-rows="0" data-pocket-columns="4"',
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(tmp_path)
    assert any("data-pocket-rows" in error for error in errors)


def test_public_check_requires_unique_leaf_ids(tmp_path):
    html = valid_public_binder_html().replace(
        'id="leaf-v1-02" data-binder-leaf="v1-02"',
        'id="leaf-v1-01" data-binder-leaf="v1-01"',
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("duplicate" in error and "v1-01" in error for error in errors)


def test_public_check_requires_alt_text_on_local_card_images(tmp_path):
    html = valid_public_binder_html().replace(
        'alt="Abra, Base Set 43/102"',
        'alt=""',
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("alt text" in error for error in errors)


def test_public_check_requires_direct_link_leaf_anchors(tmp_path):
    html = valid_public_binder_html().replace('id="leaf-v1-02"', "", 1)
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("direct-link anchor" in error and "v1-02" in error for error in errors)


def test_public_check_requires_dialog_and_labelled_controls(tmp_path):
    html = valid_public_binder_html().replace(
        '<nav class="binder-controls" data-binder-controls aria-label="Binder pages">',
        '<nav class="binder-controls" data-binder-controls>',
    ).replace(
        '<dialog id="card-inspector-volume-1" data-card-inspector>',
        '<div>',
    ).replace("</dialog>", "</div>")
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("dialog" in error for error in errors)
    assert any("controls" in error and "label" in error for error in errors)


def test_public_check_requires_inspector_parts_inside_dialog(tmp_path):
    html = valid_public_binder_html().replace(
        '<img data-card-inspector-image alt="" hidden>'
        '<h2 data-card-inspector-name></h2>'
        '<dl>',
        '</dialog><img data-card-inspector-image alt="" hidden>'
        '<h2 data-card-inspector-name></h2><dl>',
        1,
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("inspector image" in error and "inside" in error for error in errors)
    assert any("inspector name" in error and "inside" in error for error in errors)
    assert any("inspector field" in error and "inside" in error for error in errors)


def test_public_check_requires_binder_stage_and_spreads_owner(tmp_path):
    html = valid_public_binder_html().replace(" data-binder-stage", "", 1).replace(
        " data-binder-spreads", "", 1
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder stage" in error for error in errors)
    assert any("binder spreads" in error for error in errors)


def test_public_check_requires_controls_and_spreads_inside_stage(tmp_path):
    html = valid_public_binder_html().replace(
        '<div class="binder-stage" data-binder-stage>'
        '<nav class="binder-controls" data-binder-controls aria-label="Binder pages">',
        '<nav class="binder-controls" data-binder-controls aria-label="Binder pages">',
        1,
    ).replace(
        '</nav><div class="binder-spreads" data-binder-spreads>',
        '</nav><div class="binder-stage" data-binder-stage>'
        '<div class="binder-spreads" data-binder-spreads>',
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder controls navigation must be inside binder stage" in error for error in errors)

    html = valid_public_binder_html().replace(
        '</nav><div class="binder-spreads" data-binder-spreads>',
        '</nav></div><div class="binder-spreads" data-binder-spreads>',
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder spreads owner must be inside binder stage" in error for error in errors)


def test_public_check_requires_spreads_inside_spreads_owner(tmp_path):
    html = valid_public_binder_html().replace(
        '<div class="binder-spreads" data-binder-spreads><div data-binder-spread="1">',
        '<div class="binder-spreads" data-binder-spreads></div><div data-binder-spread="1">',
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder spread 1 must be inside binder spreads owner" in error for error in errors)


def test_public_check_rejects_controls_on_same_element_as_stage(tmp_path):
    html = valid_public_binder_html().replace(
        '<div class="binder-stage" data-binder-stage>'
        '<nav class="binder-controls" data-binder-controls aria-label="Binder pages">',
        '<nav class="binder-stage binder-controls" '
        'data-binder-stage data-binder-controls aria-label="Binder pages">',
        1,
    ).replace('</div></div></div><dialog', '</div></div><dialog', 1)
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder controls navigation must be inside binder stage" in error for error in errors)


def test_public_check_rejects_spreads_owner_on_same_element_as_stage(tmp_path):
    html = valid_public_binder_html().replace(
        '<div class="binder-stage" data-binder-stage>',
        '<div class="binder-stage binder-spreads" data-binder-stage data-binder-spreads>',
        1,
    ).replace('<div class="binder-spreads" data-binder-spreads>', '', 1).replace(
        '</div></div></div><dialog', '</div></div><dialog', 1
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder spreads owner must be inside binder stage" in error for error in errors)


def test_public_check_rejects_spread_on_same_element_as_spreads_owner(tmp_path):
    html = valid_public_binder_html().replace(
        '<div class="binder-spreads" data-binder-spreads><div data-binder-spread="1">',
        '<div class="binder-spreads" data-binder-spreads data-binder-spread="1">',
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder spread 1 must be inside binder spreads owner" in error for error in errors)


def test_public_check_accepts_stage_controls_spreads_as_nested_descendants(tmp_path):
    write_valid_public_binder(tmp_path)

    assert digital_binder.validate_public_output(tmp_path) == []


def test_public_check_requires_arrow_control_accessible_labels(tmp_path):
    html = valid_public_binder_html().replace(' aria-label="Previous page"', "", 1)
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("previous control" in error and "aria-label" in error for error in errors)


def test_public_check_requires_previous_and_next_controls(tmp_path):
    html = valid_public_binder_html().replace(" data-binder-next", "", 1)
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("next control" in error for error in errors)


def test_public_check_rejects_transition_pockets(tmp_path):
    html = valid_public_binder_html().replace(
        '<section id="leaf-v1-04" data-binder-leaf="v1-04" data-kind="transition"></section>',
        '<section id="leaf-v1-04" data-binder-leaf="v1-04" data-kind="transition">'
        '<div data-pocket></div></section>',
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("transition" in error and "pockets" in error for error in errors)


def test_public_check_requires_non_initial_card_images_to_be_lazy(tmp_path):
    html = valid_public_binder_html().replace(
        '<img src="/images/cards/three.webp" alt="Abra, Base Set 43/102" loading="lazy">',
        '<img src="/images/cards/three.webp" alt="Abra, Base Set 43/102" loading="eager">',
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("loading=\"lazy\"" in error for error in errors)


def test_public_check_requires_lazy_image_src_to_resolve(tmp_path):
    html = valid_public_binder_html().replace("/images/cards/three.webp", "/images/cards/missing.webp")
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder image URL" in error and "missing.webp" in error for error in errors)


def test_public_check_requires_each_srcset_candidate_to_resolve(tmp_path):
    html = valid_public_binder_html().replace(
        'src="/images/cards/one.webp"',
        'src="/images/cards/one.webp" srcset="/images/cards/one.webp 360w, '
        '/images/cards/one-large.webp 900w"',
        1,
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder image URL" in error and "one-large.webp" in error for error in errors)


def test_public_check_requires_inspector_source_to_resolve(tmp_path):
    html = valid_public_binder_html().replace(
        '/images/cards/inspector.webp',
        '/images/cards/missing-inspector.webp',
        1,
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("binder image URL" in error and "missing-inspector.webp" in error
               for error in errors)


def test_public_check_requires_initial_images_to_be_eager(tmp_path):
    html = valid_public_binder_html().replace(
        'loading="eager" data-initial-binder-image',
        'loading="lazy" data-initial-binder-image',
        1,
    )
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("initial binder image" in error and "eager" in error for error in errors)


def test_public_check_enforces_unique_initial_image_file_budget(tmp_path):
    html = valid_public_binder_html().replace(
        "/images/cards/two.webp",
        "/images/cards/one.webp",
        1,
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)
    image = tmp_path / "images/cards/one.webp"
    image.write_bytes(b"x" * 1_572_864)

    assert digital_binder.validate_public_output(tmp_path) == []

    image.write_bytes(b"x" * 1_572_865)
    errors = digital_binder.validate_public_output(tmp_path)

    assert any("initial image budget" in error and "1,572,864" in error for error in errors)


def test_public_check_counts_largest_initial_srcset_candidate_for_budget(tmp_path):
    html = valid_public_binder_html().replace(
        'src="/images/cards/one.webp"',
        'src="/images/cards/one.webp" srcset="/images/cards/one.webp 360w, '
        '/images/cards/one-large.webp 900w"',
        1,
    )
    write_html(tmp_path, html)
    write_public_card_assets(tmp_path)
    large = tmp_path / "images/cards/one-large.webp"
    large.write_bytes(b"x" * 1_572_865)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("initial image budget" in error and "1,572,864" in error for error in errors)


def test_public_check_accumulates_errors(tmp_path):
    html = valid_public_binder_html().replace(
        'alt="Abra, Base Set 43/102"',
        'alt=""',
        1,
    ).replace(
        '<dialog id="card-inspector-volume-1" data-card-inspector>',
        '<div>',
    ).replace("</dialog>", "</div>")
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("alt text" in error for error in errors)
    assert any("dialog" in error for error in errors)


def test_public_check_accepts_valid_binder_output(tmp_path):
    write_valid_public_binder(tmp_path)

    assert digital_binder.validate_public_output(tmp_path) == []


def test_strict_public_check_accepts_cutover_volume_routes(tmp_path):
    write_valid_strict_public_binders(tmp_path)

    assert digital_binder.validate_public_output(
        tmp_path, require_public_volumes=True
    ) == []


def test_stamped_manifest_uses_shared_cross_binder_validation():
    root = Path(__file__).parents[1]
    errors = []
    manifests = digital_binder._load_project_manifests(root, errors)

    assert errors == []
    assert "stamped-cards" in manifests
    assert sum(leaf["kind"] == "cards" for leaf in manifests["stamped-cards"]["leaves"]) == 7


def test_strict_public_check_rejects_missing_stamped_route(tmp_path):
    write_valid_strict_public_binders(tmp_path)
    (tmp_path / "gallery/stamped-cards/index.html").unlink()

    errors = digital_binder.validate_public_output(tmp_path, require_public_volumes=True)

    assert any("gallery/stamped-cards/index.html" in error and "missing" in error
               for error in errors)


def test_strict_public_check_rejects_missing_public_volume_route(tmp_path):
    write_valid_public_binder(tmp_path)

    errors = digital_binder.validate_public_output(
        tmp_path, require_public_volumes=True
    )

    assert any("gallery/volume-2/index.html" in error and "missing" in error
               for error in errors)


def test_strict_public_check_rejects_wrong_binder_root(tmp_path):
    write_html_at(
        tmp_path,
        "gallery/volume-1/index.html",
        valid_public_binder_html("volume-2", "v2"),
    )
    write_html_at(
        tmp_path,
        "gallery/volume-2/index.html",
        valid_public_binder_html("volume-2", "v2"),
    )
    write_public_card_assets(tmp_path)

    errors = digital_binder.validate_public_output(
        tmp_path, require_public_volumes=True
    )

    assert any("gallery/volume-1/index.html" in error
               and "expected exactly one volume-1" in error for error in errors)
    assert any("gallery/volume-1/index.html" in error
               and "unexpected binder root" in error and "volume-2" in error
               for error in errors)


def test_strict_public_check_rejects_multiple_binder_roots(tmp_path):
    write_valid_strict_public_binders(tmp_path)
    volume_one = tmp_path / "gallery/volume-1/index.html"
    volume_one.write_text(
        volume_one.read_text(encoding="utf-8").replace(
            "</body>", f"{valid_public_binder_html('volume-1', 'v1')}</body>", 1
        ),
        encoding="utf-8",
    )

    errors = digital_binder.validate_public_output(
        tmp_path, require_public_volumes=True
    )

    assert any("gallery/volume-1/index.html" in error
               and "expected exactly one volume-1" in error
               and "found 2" in error for error in errors)


def test_strict_public_check_rejects_pilot_output(tmp_path):
    write_valid_strict_public_binders(tmp_path)
    write_html_at(tmp_path, "gallery/digital-binder-pilot/index.html", "<main>Pilot</main>")

    errors = digital_binder.validate_public_output(
        tmp_path, require_public_volumes=True
    )

    assert any("digital-binder-pilot" in error and "must not be present" in error
               for error in errors)


def test_strict_public_check_rejects_legacy_photographed_volume_refs(tmp_path):
    write_valid_strict_public_binders(tmp_path)
    write_html_at(
        tmp_path,
        "gallery/side/index.html",
        '<img src="/images/binder/volume-1/calm_nature_1.webp" alt="Old photo">',
    )

    errors = digital_binder.validate_public_output(
        tmp_path, require_public_volumes=True
    )

    assert any("legacy photographed binder image reference" in error
               and "images/binder/volume-1/" in error for error in errors)


def test_public_check_accepts_zero_binders_and_unrelated_site_images_in_component_mode(tmp_path):
    write_html(
        tmp_path,
        '<main><img src="https://example.com/gallery-photo.webp" alt="Gallery photo"></main>',
    )

    assert digital_binder.validate_public_output(tmp_path) == []


def test_public_check_ignores_unrelated_images_outside_binder_root(tmp_path):
    write_html(
        tmp_path,
        '<img src="https://example.com/gallery-photo.webp" alt="Gallery photo">'
        + valid_public_binder_html(),
    )
    write_public_card_assets(tmp_path)

    assert digital_binder.validate_public_output(tmp_path) == []


def test_check_public_cli_prints_all_errors_and_exits_one(tmp_path, capsys):
    html = valid_public_binder_html().replace(
        'alt="Abra, Base Set 43/102"',
        'alt=""',
        1,
    ).replace(
        '<dialog id="card-inspector-volume-1" data-card-inspector>',
        '<div>',
    ).replace("</dialog>", "</div>")
    write_html(tmp_path, html)

    rc = digital_binder.main(["--check-public", str(tmp_path)])

    output = capsys.readouterr().out
    assert rc == 1
    assert "alt text" in output
    assert "dialog" in output
    assert "gallery/volume-2/index.html" in output


def test_check_public_cli_uses_strict_cutover_mode(tmp_path, capsys):
    write_valid_public_binder(tmp_path)

    rc = digital_binder.main(["--check-public", str(tmp_path)])

    output = capsys.readouterr().out
    assert rc == 1
    assert "gallery/volume-2/index.html" in output
    assert "missing" in output


def test_check_ignores_absent_previous_ref_environment(tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path, pockets=[confirmed_pocket("abra-01")])
    write_current_generated(root)
    monkeypatch.delenv("DIGITAL_BINDER_PREVIOUS_REF", raising=False)

    rc = digital_binder.main(["--check", "--root", str(root)])

    assert rc == 1
    assert "exactly 9 pockets" in capsys.readouterr().out


def test_check_ignores_all_zero_previous_ref_environment(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    monkeypatch.setenv("DIGITAL_BINDER_PREVIOUS_REF", "0" * 40)

    def fail_if_called(*args, **kwargs):
        raise AssertionError("git should not be called for an all-zero ref")

    monkeypatch.setattr(digital_binder.subprocess, "run", fail_if_called)

    assert digital_binder.main(["--check", "--root", str(root)]) == 0


def test_check_passes_valid_previous_ref_environment(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    calls = []
    monkeypatch.setenv("DIGITAL_BINDER_PREVIOUS_REF", "abc123")

    def fake_run(command, check, capture_output, text, cwd):
        calls.append(command)
        if command[:3] == ["git", "rev-parse", "--verify"]:
            return subprocess.CompletedProcess(command, 0, stdout="abc123\n", stderr="")
        if command[:3] == ["git", "ls-tree", "--name-only"]:
            source = "" if command[4].endswith(("/waifu.yaml", "/stamped-cards.yaml")) else command[4] + "\n"
            return subprocess.CompletedProcess(command, 0, stdout=source, stderr="")
        if command[:2] == ["git", "show"]:
            volume_id = command[2].split("/")[-1].removesuffix(".yaml")
            return subprocess.CompletedProcess(
                command,
                0,
                stdout=yaml.safe_dump(project_manifest()[volume_id]),
                stderr="",
            )
        raise AssertionError(f"unexpected git command: {command}")

    monkeypatch.setattr(digital_binder.subprocess, "run", fake_run)

    assert digital_binder.main(["--check", "--root", str(root)]) == 0
    assert calls == [
        ["git", "rev-parse", "--verify", "abc123^{commit}"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/volume-1.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/volume-2.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/waifu.yaml"],
        ["git", "ls-tree", "--name-only", "abc123", "data/binders/stamped-cards.yaml"],
        ["git", "show", "abc123:data/binders/volume-1.yaml"],
        ["git", "show", "abc123:data/binders/volume-2.yaml"],
    ]


def test_rendered_draft_and_production_outputs_pass_public_validation(tmp_path):
    root = Path(__file__).parents[1]
    draft_destination = tmp_path / "draft-public"
    production_destination = tmp_path / "public"

    draft = subprocess.run(
        ["hugo", "--buildDrafts", "--destination", str(draft_destination)],
        cwd=root,
        capture_output=True,
        text=True,
    )
    production = subprocess.run(
        ["hugo", "--destination", str(production_destination)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert draft.returncode == 0, draft.stderr
    assert digital_binder.validate_public_output(
        draft_destination, require_public_volumes=True
    ) == []
    assert digital_binder.main(["--check-public", str(draft_destination)]) == 0
    assert production.returncode == 0, production.stderr
    assert digital_binder.validate_public_output(
        production_destination, require_public_volumes=True
    ) == []
    assert digital_binder.main(["--check-public", str(production_destination)]) == 0
