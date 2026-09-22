import argparse
import importlib.util
import json
import re
import shutil
import subprocess
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs

from PIL import Image
import yaml

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


class FakeBinaryHTTPResponse:
    def __init__(self, payload):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def image_bytes(format_="PNG", size=(12, 10), color=(64, 128, 192)):
    from io import BytesIO

    buffer = BytesIO()
    Image.new("RGB", size, color).save(buffer, format=format_)
    return buffer.getvalue()


def write_candidate_cache(root, card_id, candidates):
    path = root / "tmp/digital-binder-review/candidates" / f"{card_id}.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(
        json.dumps({"card_id": card_id, "registry": {}, "candidates": candidates}),
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
                 confirm_identity=False):
    return argparse.Namespace(
        card_id=card_id,
        candidate_index=candidate_index,
        classification=classification,
        note=note,
        confirm_identity=confirm_identity,
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


def test_doubleholo_name_match_rejects_embedded_species_without_token_boundary():
    assert ranked_doubleholo_name_match("Mew", "Mew", "Mewtwo") is False
    assert ranked_doubleholo_name_match("Abra", "Abra", "Kadabra") is False


def test_search_doubleholo_skips_bad_hits_and_returns_empty_on_failed_or_malformed_response():
    row = {
        "id": "abra-01", "species": "Abra", "card_name": "Abra",
        "language": "EN", "set": "Base Set", "number": "43/102",
    }

    def mixed_hits_opener(request, timeout):
        return FakeHTTPResponse({"results": [{"hits": [
            None,
            {"objectID": "ok", "name": "Abra", "set_name": "Pokemon Base Set",
             "number": "43/102", "language": "english"},
            {"name": "missing object"},
        ]}]})

    candidates = digital_binder.search_doubleholo(row, opener=mixed_hits_opener)
    assert [candidate["provider_id"] for candidate in candidates] == ["ok"]

    def failed_opener(request, timeout):
        raise OSError("network down")

    assert digital_binder.search_doubleholo(row, opener=failed_opener) == []

    def malformed_opener(request, timeout):
        return FakeBinaryHTTPResponse(b"not json")

    assert digital_binder.search_doubleholo(row, opener=malformed_opener) == []


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
    monkeypatch.chdir(root)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "HTTP(S)" in str(exc)
    else:
        raise AssertionError("approve-doubleholo should reject file: candidate URLs")

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
    monkeypatch.chdir(root)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "exact identity" in str(exc)
    else:
        raise AssertionError("exact doubleholo approval should require an exact identity match")

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


def test_approve_doubleholo_confirm_identity_is_documented_only_on_doubleholo_help():
    script = Path(__file__).with_name("manage-card-images.py")
    doubleholo_help = subprocess.run(
        ["python3", str(script), "approve-doubleholo", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )
    approve_help = subprocess.run(
        ["python3", str(script), "approve", "--help"],
        capture_output=True,
        text=True,
        check=True,
    )

    assert "--confirm-identity" in doubleholo_help.stdout
    assert "curator-confirmed" in doubleholo_help.stdout
    assert "--confirm-identity" not in approve_help.stdout


def test_approve_doubleholo_rejects_missing_raw_original_with_rerun_search_error(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "dh-43",
        "image_url": "https://supabase.example/abra.png",
        "exact_identity_match": True,
    }])

    def fail_if_called(request, timeout):
        raise AssertionError("approval should reject before image download")

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fail_if_called)

    try:
        manage_card_images.approve_doubleholo_command(approve_args())
    except ValueError as exc:
        assert "raw candidate fields" in str(exc)
        assert "rerun search-doubleholo" in str(exc)
    else:
        raise AssertionError("missing raw DoubleHolo candidate fields should reject approval")

    assert not (root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp").exists()


def test_approve_doubleholo_uses_recomputed_raw_url_and_upstream_id(tmp_path, monkeypatch, capsys):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_doubleholo_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "tampered-id",
        "image_url": "https://attacker.example/tampered.png",
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
    requested_urls = []

    def fake_urlopen(request, timeout):
        requested_urls.append(request.full_url)
        if request.full_url != "https://supabase.example/abra.png":
            raise AssertionError(f"unexpected approval download URL {request.full_url}")
        return FakeBinaryHTTPResponse(image_bytes("PNG"))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_doubleholo_command(approve_args()) == 0

    assert requested_urls == ["https://supabase.example/abra.png"]
    output = capsys.readouterr().out
    assert "exact_identity_match does not verify edition/variant" in output
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "doubleholo"
    assert record["upstream_id"] == "dh-43"
    assert record["source_url"] == "https://supabase.example/abra.png"


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


def test_approve_rejects_file_candidate_url(tmp_path, monkeypatch):
    root = project_fixture(tmp_path)
    write_current_generated(root)
    write_candidate_cache(root, "abra-01", [{
        "candidate_index": 0,
        "provider_id": "base1-43",
        "image_url": "file:///tmp/abra.webp",
    }])
    monkeypatch.chdir(root)

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
        "image_url": "https://example.invalid/not-image.webp",
    }])

    def fake_urlopen(request, timeout):
        return FakeBinaryHTTPResponse(b"not an image")

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
        "image_url": "https://example.invalid/abra.png",
    }])

    def fake_urlopen(request, timeout):
        return FakeBinaryHTTPResponse(image_bytes("PNG"))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    assert manage_card_images.approve_command(approve_args()) == 0

    asset_path = root / manage_card_images.CARD_ASSET_DIR / "abra-01.webp"
    with Image.open(asset_path) as image:
        assert image.format == "WEBP"
    record = load_images(root)["cards"]["abra-01"]
    assert record["provider"] == "tcgdex"
    assert record["upstream_id"] == "base1-43"
    assert record["source_url"] == "https://example.invalid/abra.png"


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

    def fake_urlopen(request, timeout):
        return FakeBinaryHTTPResponse(image_bytes("PNG", color=(255, 0, 0)))

    monkeypatch.chdir(root)
    monkeypatch.setattr(manage_card_images, "urlopen", fake_urlopen)

    try:
        manage_card_images.approve_command(approve_args())
    except ValueError as exc:
        assert "exact" in str(exc) and "set and number" in str(exc)
    else:
        raise AssertionError("invalid exact approval should be rejected")

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
            "python3", str(Path(__file__).with_name("manage-card-images.py")),
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
        "data-binder-controls", "data-binder-legend", "data-card-inspector",
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


def test_rendered_draft_pilot_uses_binder_markup_without_remote_card_images(tmp_path):
    root = Path(__file__).parents[1]
    destination = tmp_path / "public"

    result = subprocess.run(
        ["hugo", "--buildDrafts", "--destination", str(destination)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert result.returncode == 0, result.stderr
    html = (destination / "gallery/digital-binder-pilot/index.html").read_text(
        encoding="utf-8"
    )
    assert 'data-binder="volume-1"' in html
    assert html.count('data-binder-leaf="') == 19
    assert 'data-binder-leaf="v1-17"' in html
    assert 'data-pocket-position="1"' in html
    assert '<dialog' in html
    assert not re.search(r'(?:src|srcset)="https://assets\.tcgdex\.net', html)
    assert 'srcset="' in html
    assert re.search(r'srcset="[^"]+ 360w, [^"]+ 900w"', html)
    assert 'sizes="(max-width: 860px) 30vw, 180px"' in html
    assert 'data-inspector-src="' in html
    assert html.count('data-initial-binder-image') == html.count('loading="eager"')
    assert 'loading="lazy"' in html
    assert 'Image unavailable' in html

    elements = rendered_elements(html)
    controls = [attrs for tag, attrs in elements
                if tag == "nav" and "data-binder-controls" in attrs]
    assert len(controls) == 1
    control_links = [
        attrs for tag, attrs in elements
        if tag == "a"
        and ("data-binder-prev" in attrs or "data-binder-next" in attrs)
    ]
    assert {link["href"] for link in control_links} == {"#leaf-v1-01", "#leaf-v1-03"}
    assert any(tag == "p" and "data-binder-position" in attrs
               and attrs.get("aria-live") == "polite" for tag, attrs in elements)

    card_buttons = [attrs for tag, attrs in elements
                    if tag == "button" and "data-card-id" in attrs]
    assert card_buttons
    for button in card_buttons:
        assert button["data-card-name"]
        assert button["data-card-language"]
        assert button["data-card-set"]
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

    assert any(tag == "aside" and "data-binder-legend" in attrs
               and "hidden" in attrs for tag, attrs in elements)
    assert any(tag == "dialog" and "data-card-inspector" in attrs for tag, attrs in elements)
    assert binder_owners(html) == [
        ("data-binder-controls", "volume-1"),
        ("data-binder-legend", "volume-1"),
        ("data-card-inspector", "volume-1"),
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

    production_destination = tmp_path / "production-public"
    production = subprocess.run(
        ["hugo", "--destination", str(production_destination)],
        cwd=root,
        capture_output=True,
        text=True,
    )

    assert production.returncode == 0, production.stderr
    assert not (production_destination / "gallery/digital-binder-pilot/index.html").exists()


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
    assert 'window.matchMedia("(max-width: 720px)")' in javascript
    assert 'dialog.showModal()' in javascript
    assert 'dialog.addEventListener("cancel"' in javascript
    assert 'dialog.addEventListener("close"' in javascript
    assert 'event.key !== "Tab"' in javascript
    assert 'originFocus.focus()' in javascript
    assert 'image.removeAttribute("src")' in javascript
    assert 'const controls = root.querySelector("[data-binder-controls]")' in javascript
    assert 'const legend = root.querySelector("[data-binder-legend]")' in javascript
    assert 'const dialog = root.querySelector("[data-card-inspector]")' in javascript
    assert 'document.querySelector("[data-binder-controls]")' not in javascript
    assert 'document.querySelector("[data-binder-legend]")' not in javascript
    assert 'document.querySelector("[data-card-inspector]")' not in javascript
    assert "focusedAdjacentControl.disabled" in javascript
    assert "focusedAdjacentControl.focus()" not in javascript
    assert "@media (max-width: 720px)" in stylesheet
    assert "@media (prefers-reduced-motion: reduce)" in stylesheet
    assert "transition: none !important" in stylesheet


def test_rendered_synthetic_binder_marks_only_first_spread_images_eager(tmp_path):
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
        "title = 'Synthetic Binder'\n",
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
        pockets.extend(empty_pocket(position) for position in range(len(pockets) + 1, 10))
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
    html = (destination / "gallery/digital-binder-pilot/index.html").read_text(
        encoding="utf-8"
    )
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


def write_html(root: Path, body: str) -> None:
    page = root / "gallery/volume-1/index.html"
    page.parent.mkdir(parents=True, exist_ok=True)
    page.write_text(body, encoding="utf-8")


def valid_public_binder_html() -> str:
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
            '<button data-pocket data-pocket-position="1" data-card-id="abra-01">'
            f'<img src="/images/cards/{image_name}" alt="Abra, Base Set 43/102" '
            f'loading="{loading}"{initial_attribute}>'
            '</button>'
            f'{empty_pockets}'
            '</div>'
            '</section>'
        )

    return (
        '<!doctype html><html><body>'
        '<div data-binder="volume-1">'
        '<nav data-binder-controls aria-label="Binder pages">'
        '<a data-binder-prev href="#leaf-v1-01">Previous</a>'
        '<p data-binder-position aria-live="polite"></p>'
        '<a data-binder-next href="#leaf-v1-03">Next</a>'
        '</nav>'
        '<div data-binder-spread="1">'
        f'{card_leaf("v1-01", "one.webp", initial=True)}'
        f'{card_leaf("v1-02", "two.webp", initial=True)}'
        '</div>'
        '<div data-binder-spread="2">'
        f'{card_leaf("v1-03", "three.webp", initial=False)}'
        '<section id="leaf-v1-04" data-binder-leaf="v1-04" data-kind="transition"></section>'
        '</div>'
        '<dialog id="card-inspector-volume-1" data-card-inspector>'
        '<button data-card-inspector-close>Close</button>'
        '<button data-card-inspector-previous>Previous card</button>'
        '<button data-card-inspector-next>Next card</button>'
        '</dialog>'
        '</div>'
        '</body></html>'
    )


def write_valid_public_binder(root: Path) -> None:
    write_html(root, valid_public_binder_html())
    for name in ("one.webp", "two.webp", "three.webp"):
        asset = root / "images/cards" / name
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(b"fixture image")


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
        '<nav data-binder-controls aria-label="Binder pages">',
        '<nav data-binder-controls>',
    ).replace(
        '<dialog id="card-inspector-volume-1" data-card-inspector>',
        '<div>',
    ).replace("</dialog>", "</div>")
    write_html(tmp_path, html)

    errors = digital_binder.validate_public_output(tmp_path)

    assert any("dialog" in error for error in errors)
    assert any("controls" in error and "label" in error for error in errors)


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
    image = tmp_path / "images/cards/one.webp"
    image.parent.mkdir(parents=True)
    image.write_bytes(b"x" * 1_572_864)

    assert digital_binder.validate_public_output(tmp_path) == []

    image.write_bytes(b"x" * 1_572_865)
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


def test_public_check_accepts_zero_binders_and_unrelated_site_images(tmp_path):
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
    for name in ("one.webp", "two.webp"):
        asset = tmp_path / "images/cards" / name
        asset.parent.mkdir(parents=True, exist_ok=True)
        asset.write_bytes(b"fixture image")

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
        volume_id = command[2].split("/")[-1].removesuffix(".yaml")
        return subprocess.CompletedProcess(
            command,
            0,
            stdout=yaml.safe_dump(project_manifest()[volume_id]),
            stderr="",
        )

    monkeypatch.setattr(digital_binder.subprocess, "run", fake_run)

    assert digital_binder.main(["--check", "--root", str(root)]) == 0
    assert calls == [
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
    assert digital_binder.validate_public_output(draft_destination) == []
    assert production.returncode == 0, production.stderr
    assert digital_binder.validate_public_output(production_destination) == []
