#!/usr/bin/env python3
"""Project and validate digital binder data."""

import argparse
import importlib.util
import json
import os
import re
import subprocess
from functools import lru_cache
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import quote, urlencode, unquote, urlsplit
from urllib.request import Request, urlopen

from PIL import Image
import yaml

GENERATED_FIELDS = (
    "id",
    "species",
    "card_name",
    "language",
    "set",
    "number",
    "confidence",
)

VOLUME_IDS = ("volume-1", "volume-2")
PUBLICATION_STATUSES = {"draft", "published"}
LEAF_KINDS = {"cards", "transition"}
TRANSITION_ROLES = {"volume-opening", "chapter", "volume-closing"}
PLACEMENT_STATUSES = {"confirmed", "pending"}
IMAGE_CLASSIFICATIONS = {"exact", "photo-crop", "proxy", "missing"}
TCGDEX_LANGUAGE = {"EN": "en", "JP": "ja", "ZH": "zh-tw"}
TCGDEX_API_ROOT = "https://api.tcgdex.net/v2"
TCGDEX_USER_AGENT = "binderplan digital-binder-image-review/1.0"
DOUBLEHOLO_APPLICATION_ID = "W5SF479ZKL"
DOUBLEHOLO_INDEX = "production_cards"
DOUBLEHOLO_SEARCH_ONLY_API_KEY = "50fdd89ab8d777151bc000bba6097357"  # Owner-authorized public frontend search-only config, not an account secret.
DOUBLEHOLO_SEARCH_ENDPOINT = "https://w5sf479zkl-dsn.algolia.net/1/indexes/*/queries"
DOUBLEHOLO_HITS_PER_PAGE = 100
DOUBLEHOLO_LANGUAGE = {
    "english": "EN",
    "japanese": "JP",
    "chinese": "ZH",
}
SAFE_REF_RE = re.compile(r"^(?!-)[A-Za-z0-9._/@+-]+$")
DATE_RE = re.compile(r"^\d{4}-\d{2}-\d{2}$")
INITIAL_BINDER_IMAGE_BUDGET = 1_572_864
HTML_VOID_ELEMENTS = {
    "area", "base", "br", "col", "embed", "hr", "img", "input",
    "link", "meta", "param", "source", "track", "wbr",
}


@lru_cache(maxsize=1)
def load_registry_module():
    path = Path(__file__).with_name("check-registry.py")
    spec = importlib.util.spec_from_file_location("check_registry", path)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_registry(path: Path) -> dict[str, dict]:
    module = load_registry_module()
    rows = module.parse_registry(path.read_text(encoding="utf-8"))
    if not rows:
        raise ValueError(f"{path}: no registry rows found")
    errors = module.validate(rows)
    if errors:
        raise ValueError("\n".join(errors))
    return {
        row["id"]: {key: row[key] for key in GENERATED_FIELDS}
        for row in rows
    }


def load_yaml(path: Path) -> dict:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data is None:
        return {}
    if not isinstance(data, dict):
        raise ValueError(f"{path} must contain a YAML mapping")
    return data


def render_registry_json(rows: dict[str, dict]) -> str:
    ordered = {card_id: rows[card_id] for card_id in sorted(rows)}
    return json.dumps(ordered, ensure_ascii=False, indent=2) + "\n"


def generated_is_current(path: Path, expected: str) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == expected


def _write_atomic(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _tcgdex_json(url: str, opener=urlopen):
    request = Request(url, headers={"User-Agent": TCGDEX_USER_AGENT})
    with opener(request, timeout=20) as response:
        return json.loads(response.read().decode("utf-8"))


def _local_number(number: str | None) -> str:
    return str(number or "").split("/", 1)[0].strip()


def _fold_identity(value: str | None) -> str:
    return re.sub(r"[^a-z0-9]+", "", str(value or "").casefold())


def _normalize_doubleholo_number(number: str | None) -> str:
    folded = re.sub(r"^no\.?\s*", "", _local_number(number).casefold()).strip()
    compact = re.sub(r"[^a-z0-9]+", "", folded)
    if compact.isdigit():
        return str(int(compact))
    return compact


def _normalize_doubleholo_set(value: str | None) -> str:
    tokens = re.findall(r"[a-z0-9]+", str(value or "").casefold())
    ignored = {"pokemon", "pokémon", "pok", "mon", "english", "japanese", "chinese", "of", "the", "and"}
    return "".join(token for token in tokens if token not in ignored)


def _doubleholo_search_query(row: dict) -> str:
    terms = []
    species = str(row.get("species") or row.get("card_name") or "").strip()
    number = _normalize_doubleholo_number(row.get("number"))
    if species:
        terms.append(species)
    if number:
        terms.append(number)
    set_text = re.sub(r"pok[eé]mon", " ", str(row.get("set") or ""), flags=re.IGNORECASE)
    set_words = re.findall(r"[A-Za-z0-9]+", set_text)
    ignored = {"pokemon", "pok", "mon", "english", "japanese", "chinese", "of", "the", "and", "to"}
    terms.extend(word for word in set_words if word.casefold() not in ignored)
    return " ".join(terms)


def normalize_doubleholo_candidate(hit: dict) -> dict:
    language = DOUBLEHOLO_LANGUAGE.get(str(hit.get("language") or "").casefold(), "")
    number = str(hit.get("number") or "")
    set_name = str(hit.get("set_name") or "")
    return {
        "provider": "doubleholo",
        "provider_id": str(hit.get("objectID") or ""),
        "name": str(hit.get("name") or ""),
        "set_name": set_name,
        "local_id": number,
        "language": language,
        "image_url": hit.get("image_url") or hit.get("image_url_small"),
        "image_url_small": hit.get("image_url_small"),
        "normalized_set": _normalize_doubleholo_set(set_name),
        "normalized_number": _normalize_doubleholo_number(number),
        "original": {
            "objectID": hit.get("objectID"),
            "name": hit.get("name"),
            "set_name": hit.get("set_name"),
            "number": hit.get("number"),
            "language": hit.get("language"),
            "image_url": hit.get("image_url"),
            "image_url_small": hit.get("image_url_small"),
        },
    }


def search_doubleholo(row: dict, opener=urlopen) -> list[dict]:
    params = urlencode({
        "query": _doubleholo_search_query(row),
        "hitsPerPage": str(DOUBLEHOLO_HITS_PER_PAGE),
        "attributesToRetrieve": ",".join((
            "objectID",
            "name",
            "set_name",
            "number",
            "language",
            "image_url",
            "image_url_small",
        )),
    })
    payload = json.dumps({
        "requests": [{"indexName": DOUBLEHOLO_INDEX, "params": params}],
    }).encode("utf-8")
    request = Request(
        DOUBLEHOLO_SEARCH_ENDPOINT,
        data=payload,
        headers={
            "Content-Type": "application/json",
            "User-Agent": TCGDEX_USER_AGENT,
            "X-Algolia-Application-Id": DOUBLEHOLO_APPLICATION_ID,
            "X-Algolia-API-Key": DOUBLEHOLO_SEARCH_ONLY_API_KEY,
        },
        method="POST",
    )
    try:
        with opener(request, timeout=20) as response:
            data = json.loads(response.read().decode("utf-8"))
    except (OSError, UnicodeDecodeError, json.JSONDecodeError, ValueError):
        return []
    results = data.get("results") if isinstance(data, dict) else None
    if not isinstance(results, list) or not results:
        return []
    hits = results[0].get("hits") if isinstance(results[0], dict) else None
    if not isinstance(hits, list):
        return []
    candidates = []
    for hit in hits:
        if not isinstance(hit, dict) or not hit.get("objectID"):
            continue
        try:
            candidates.append(normalize_doubleholo_candidate(hit))
        except (AttributeError, TypeError, ValueError):
            continue
    return candidates


def _doubleholo_set_matches(wanted: str, candidate: str) -> bool:
    if not wanted or not candidate:
        return False
    return wanted == candidate


def _contains_token_sequence(candidate_value: str | None, wanted_value: str | None) -> bool:
    candidate_tokens = re.findall(r"[a-z0-9]+", str(candidate_value or "").casefold())
    wanted_tokens = re.findall(r"[a-z0-9]+", str(wanted_value or "").casefold())
    if not candidate_tokens or not wanted_tokens:
        return False
    width = len(wanted_tokens)
    return any(candidate_tokens[index:index + width] == wanted_tokens
               for index in range(len(candidate_tokens) - width + 1))


def _doubleholo_name_matches(row: dict, candidate: dict) -> bool:
    candidate_name = _fold_identity(candidate.get("name"))
    for raw_name in (row.get("card_name"), row.get("species")):
        name = _fold_identity(raw_name)
        if name and name == candidate_name:
            return True
        if _contains_token_sequence(candidate.get("name"), raw_name):
            return True
    return False


def rank_doubleholo_candidates(row: dict, candidates: list[dict]) -> list[dict]:
    wanted_number = _normalize_doubleholo_number(row.get("number"))
    wanted_language = str(row.get("language") or "").upper()
    wanted_set = _normalize_doubleholo_set(row.get("set"))
    ranked = []
    for candidate in candidates:
        item = dict(candidate)
        number_match = bool(wanted_number and candidate.get("normalized_number") == wanted_number)
        language_match = bool(wanted_language and candidate.get("language") == wanted_language)
        set_match = _doubleholo_set_matches(wanted_set, str(candidate.get("normalized_set") or ""))
        name_match = _doubleholo_name_matches(row, candidate)
        score = 0
        if number_match:
            score += 50
        if language_match:
            score += 55
        if set_match:
            score += 35
        if name_match:
            score += 15
        if candidate.get("image_url"):
            score += 5
        item["number_match"] = number_match
        item["language_match"] = language_match
        item["set_match"] = set_match
        item["name_match"] = name_match
        item["exact_identity_match"] = number_match and language_match and set_match
        item["score"] = score
        item["review_state"] = "candidate"
        ranked.append(item)
    return sorted(ranked, key=lambda item: (-item["score"], item.get("provider_id") or ""))


def _tcgdex_image_url(image_base: str | None) -> str | None:
    if not image_base:
        return None
    if image_base.endswith(".webp"):
        return image_base
    return image_base.rstrip("/") + "/high.webp"


def normalize_tcgdex_candidate(candidate: dict) -> dict:
    card_set = candidate.get("set") if isinstance(candidate.get("set"), dict) else {}
    return {
        "provider": "tcgdex",
        "provider_id": candidate.get("id") or "",
        "name": candidate.get("name") or "",
        "local_id": str(candidate.get("localId") or ""),
        "set_id": card_set.get("id") or "",
        "set_name": card_set.get("name") or "",
        "image_url": _tcgdex_image_url(candidate.get("image")),
    }


def search_tcgdex(row: dict, opener=urlopen) -> list[dict]:
    language = TCGDEX_LANGUAGE.get(row.get("language"))
    if not language:
        return []
    query = quote(str(row.get("card_name") or ""))
    search_url = f"{TCGDEX_API_ROOT}/{language}/cards?name={query}"
    summaries = _tcgdex_json(search_url, opener=opener)
    if not isinstance(summaries, list):
        return []

    candidates = []
    for summary in summaries:
        if not isinstance(summary, dict) or not summary.get("id"):
            continue
        detail_url = f"{TCGDEX_API_ROOT}/{language}/cards/{quote(str(summary['id']))}"
        try:
            detail = _tcgdex_json(detail_url, opener=opener)
        except (OSError, ValueError, json.JSONDecodeError) as exc:
            candidate = normalize_tcgdex_candidate(summary)
            candidate["image_url"] = None
            candidate["detail_error"] = str(exc)
            candidates.append(candidate)
            continue
        if isinstance(detail, dict):
            candidates.append(normalize_tcgdex_candidate(detail))
        else:
            candidate = normalize_tcgdex_candidate(summary)
            candidate["image_url"] = None
            candidate["detail_error"] = "detail response was not a JSON object"
            candidates.append(candidate)
    return candidates


def rank_candidates(row: dict, candidates: list[dict]) -> list[dict]:
    wanted_number = _fold_identity(_local_number(row.get("number")))
    wanted_set = _fold_identity(row.get("set"))
    wanted_name = _fold_identity(row.get("card_name"))
    ranked = []
    for candidate in candidates:
        item = dict(candidate)
        score = 0
        if wanted_number and _fold_identity(candidate.get("local_id")) == wanted_number:
            score += 50
        if wanted_set and _fold_identity(candidate.get("set_id")) == wanted_set:
            score += 35
        elif wanted_set and _fold_identity(candidate.get("set_name")) == wanted_set:
            score += 25
        if wanted_name and _fold_identity(candidate.get("name")) == wanted_name:
            score += 20
        if candidate.get("image_url"):
            score += 5
        item["score"] = score
        item["review_state"] = "candidate"
        ranked.append(item)
    return sorted(ranked, key=lambda item: (-item["score"], item.get("provider_id") or ""))


def crop_evidence_photo(source: Path, box: tuple[int, int, int, int], target: Path) -> None:
    left, top, right, bottom = box
    with Image.open(source) as image:
        width, height = image.size
        if not (0 <= left < right <= width and 0 <= top < bottom <= height):
            raise ValueError(
                f"crop box {(left, top, right, bottom)} is outside image bounds {width}x{height}"
            )
        target.parent.mkdir(parents=True, exist_ok=True)
        tmp = target.with_name(target.name + ".tmp")
        image.crop((left, top, right, bottom)).convert("RGB").save(tmp, format="WEBP")
        tmp.replace(target)


def _validate_images_against_project(
        root: Path,
        images: dict,
        asset_overrides: dict[str, Path] | None = None) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    try:
        registry = load_registry(root / "docs" / "card-registry.md")
    except (FileNotFoundError, ValueError) as exc:
        registry = {}
        errors.append(f"registry validation failed: {exc}")
    manifests = _load_project_manifests(root, errors)
    occupied_by_volume: dict[str, set[str]] = {}
    publication_statuses: dict[str, str] = {}
    for volume_id, manifest in manifests.items():
        publication_statuses[volume_id] = manifest.get("publication_status")
        occupied_by_volume[volume_id] = _validate_volume_manifest(
            volume_id, manifest, registry, errors
        )
    _validate_global_duplicates(manifests, errors)
    _validate_images(
        root, images, registry, occupied_by_volume, publication_statuses, errors,
        asset_overrides=asset_overrides,
    )
    return errors


def validate_image_manifest(root: Path, images: dict,
                            asset_overrides: dict[str, Path] | None = None) -> list[str]:
    return _validate_images_against_project(root, images, asset_overrides=asset_overrides)


def write_image_manifest_atomically(root: Path, images: dict) -> None:
    errors = _validate_images_against_project(root, images)
    if errors:
        raise ValueError("\n".join(errors))
    rendered = yaml.safe_dump(images, sort_keys=False, allow_unicode=True)
    _write_atomic(Path(root) / "data" / "card-images.yaml", rendered)


def _load_project_manifests(root: Path, errors: list[str]) -> dict[str, dict]:
    manifests = {}
    for volume_id in VOLUME_IDS:
        path = root / "data" / "binders" / f"{volume_id}.yaml"
        try:
            manifest = load_yaml(path)
        except FileNotFoundError:
            errors.append(f"missing binder manifest: {path.relative_to(root)}")
            continue
        except ValueError as exc:
            errors.append(str(exc))
            continue
        manifests[volume_id] = manifest
    return manifests


def _load_previous_manifests(root: Path, previous_ref: str, errors: list[str]) -> dict[str, dict] | None:
    if not SAFE_REF_RE.match(previous_ref):
        errors.append(f"invalid previous_ref: {previous_ref}")
        return None

    manifests = {}
    for volume_id in VOLUME_IDS:
        try:
            result = subprocess.run(
                ["git", "show", f"{previous_ref}:data/binders/{volume_id}.yaml"],
                check=True,
                capture_output=True,
                text=True,
                cwd=root,
            )
        except subprocess.CalledProcessError:
            return None
        data = yaml.safe_load(result.stdout) or {}
        if not isinstance(data, dict):
            errors.append(f"previous {volume_id} manifest must contain a YAML mapping")
            return None
        manifests[volume_id] = data
    return manifests


def _validate_volume_manifest(volume_id: str, manifest: dict, registry: dict[str, dict],
                              errors: list[str]) -> set[str]:
    occupied_cards: set[str] = set()
    if manifest.get("version") != 1:
        errors.append(f"{volume_id}: version must be 1")
    if manifest.get("volume_id") != volume_id:
        errors.append(f"{volume_id}: volume_id must be {volume_id}")

    publication_status = manifest.get("publication_status")
    if publication_status not in PUBLICATION_STATUSES:
        errors.append(
            f"{volume_id}: publication_status must be draft or published"
        )

    leaves = manifest.get("leaves")
    if not isinstance(leaves, list):
        errors.append(f"{volume_id}: leaves must be a list")
        return occupied_cards

    physical_numbers = []
    volume_seen_cards: dict[str, tuple[int, int]] = {}
    for leaf_index, leaf in enumerate(leaves, start=1):
        if not isinstance(leaf, dict):
            errors.append(f"{volume_id}: leaf {leaf_index} must be a mapping")
            continue
        leaf_label = leaf.get("id", f"leaf {leaf_index}")
        physical_leaf = leaf.get("physical_leaf")
        if isinstance(physical_leaf, int):
            physical_numbers.append(physical_leaf)
        else:
            errors.append(f"{volume_id} {leaf_label}: physical_leaf must be an integer")

        kind = leaf.get("kind")
        if kind not in LEAF_KINDS:
            errors.append(f"{volume_id} {leaf_label}: unknown leaf kind {kind!r}")
            continue

        if kind == "transition":
            if "pockets" in leaf:
                errors.append(
                    f"{volume_id} {leaf_label}: transition leaf must not define pockets"
                )
            role = leaf.get("role")
            if role not in TRANSITION_ROLES:
                errors.append(
                    f"{volume_id} {leaf_label}: transition role {role!r} is invalid"
                )
            continue

        _validate_card_leaf_metadata(volume_id, leaf_label, leaf, errors)
        pockets = leaf.get("pockets")
        if not isinstance(pockets, list):
            errors.append(f"{volume_id} {leaf_label}: pockets must be a list")
            continue
        if len(pockets) != 9:
            errors.append(f"{volume_id} {leaf_label}: card leaf must define exactly 9 pockets")

        seen_positions: set[int] = set()
        for pocket_index, pocket in enumerate(pockets, start=1):
            if not isinstance(pocket, dict):
                errors.append(f"{volume_id} {leaf_label}: pocket {pocket_index} must be a mapping")
                continue
            position = pocket.get("position")
            if not isinstance(position, int) or not 1 <= position <= 9:
                errors.append(
                    f"{volume_id} {leaf_label}: pocket position {position!r} must be 1-9"
                )
            elif position in seen_positions:
                errors.append(f"{volume_id} {leaf_label}: duplicate pocket position {position}")
            else:
                seen_positions.add(position)

            if pocket.get("empty") is True:
                if "card_id" in pocket:
                    errors.append(f"{volume_id} {leaf_label} pocket {position}: empty pocket has card_id")
                continue

            card_id = pocket.get("card_id")
            if not card_id:
                errors.append(f"{volume_id} {leaf_label} pocket {position}: occupied pocket needs card_id")
                continue
            if card_id not in registry:
                errors.append(f"{volume_id} {leaf_label} pocket {position}: unknown card_id {card_id}")
            if card_id in volume_seen_cards:
                prior_leaf, prior_position = volume_seen_cards[card_id]
                errors.append(
                    f"{volume_id} {leaf_label} pocket {position}: duplicate occupied placement "
                    f"for {card_id} already at physical_leaf {prior_leaf} pocket {prior_position}"
                )
            elif isinstance(physical_leaf, int) and isinstance(position, int):
                volume_seen_cards[card_id] = (physical_leaf, position)
            occupied_cards.add(card_id)

            _validate_placement(
                volume_id, leaf_label, position, pocket.get("placement"), registry, errors
            )

    expected = list(range(1, len(physical_numbers) + 1))
    if physical_numbers and sorted(physical_numbers) != expected:
        errors.append(
            f"{volume_id}: leaves must use contiguous physical_leaf numbers starting at 1"
        )
    return occupied_cards


def _validate_card_leaf_metadata(volume_id: str, leaf_label: str, leaf: dict,
                                 errors: list[str]) -> None:
    for field in ("chapter", "theme"):
        if not isinstance(leaf.get(field), str) or not leaf.get(field).strip():
            errors.append(f"{volume_id} {leaf_label}: {field} must be a nonempty string")
    chapter_order = leaf.get("chapter_order")
    if not isinstance(chapter_order, int) or chapter_order < 1:
        errors.append(f"{volume_id} {leaf_label}: chapter_order must be a positive integer")
    if "theme_page" in leaf:
        theme_page = leaf.get("theme_page")
        if not isinstance(theme_page, int) or theme_page < 1:
            errors.append(f"{volume_id} {leaf_label}: theme_page must be a positive integer")


def _validate_global_duplicates(manifests: dict[str, dict], errors: list[str]) -> None:
    locations: dict[str, list[tuple[str, int, int]]] = {}
    for volume_id, manifest in manifests.items():
        if not isinstance(manifest, dict):
            continue
        for leaf in manifest.get("leaves", []):
            if not isinstance(leaf, dict) or leaf.get("kind") != "cards":
                continue
            physical_leaf = leaf.get("physical_leaf")
            for pocket in leaf.get("pockets", []):
                if not isinstance(pocket, dict) or pocket.get("empty") is True:
                    continue
                card_id = pocket.get("card_id")
                position = pocket.get("position")
                if card_id and isinstance(physical_leaf, int) and isinstance(position, int):
                    locations.setdefault(card_id, []).append((volume_id, physical_leaf, position))
    for card_id, card_locations in locations.items():
        if len({location[0] for location in card_locations}) < 2:
            continue
        rendered = "; ".join(
            f"{volume_id} physical_leaf {physical_leaf} pocket {position}"
            for volume_id, physical_leaf, position in card_locations
        )
        errors.append(f"duplicate occupied placement for {card_id} across volumes: {rendered}")


def _validate_placement(volume_id: str, leaf_label: str, position: int | None,
                        placement: object, registry: dict[str, dict], errors: list[str]) -> None:
    if not isinstance(placement, dict):
        errors.append(f"{volume_id} {leaf_label} pocket {position}: placement is required")
        return
    status = placement.get("status")
    if status not in PLACEMENT_STATUSES:
        errors.append(
            f"{volume_id} {leaf_label} pocket {position}: placement status {status!r} is invalid"
        )
    evidence = placement.get("evidence")
    if not isinstance(evidence, dict):
        errors.append(f"{volume_id} {leaf_label} pocket {position}: placement evidence is required")
    else:
        for field in ("type", "source", "observed_on"):
            if not evidence.get(field):
                errors.append(
                    f"{volume_id} {leaf_label} pocket {position}: placement evidence needs {field}"
                )

    if status != "pending":
        return

    observed = placement.get("observed_card_id")
    unknown = placement.get("physical_state_unknown") is True
    if bool(observed) == unknown:
        errors.append(
            f"{volume_id} {leaf_label} pocket {position}: pending placement requires exactly one "
            "of observed_card_id or physical_state_unknown"
        )
    if observed and observed not in registry:
        errors.append(
            f"{volume_id} {leaf_label} pocket {position}: unknown observed_card_id {observed}"
        )
    if unknown and not placement.get("note"):
        errors.append(
            f"{volume_id} {leaf_label} pocket {position}: physical_state_unknown pending placement needs note"
        )


def _validate_images(root: Path, images: dict, registry: dict[str, dict],
                     occupied_by_volume: dict[str, set[str]], publication_statuses: dict[str, str],
                     errors: list[str],
                     asset_overrides: dict[str, Path] | None = None) -> None:
    if images.get("version") != 1:
        errors.append("data/card-images.yaml: version must be 1")
    cards = images.get("cards")
    if not isinstance(cards, dict):
        errors.append("data/card-images.yaml: cards must be a mapping")
        return

    for card_id, record in cards.items():
        if card_id not in registry:
            errors.append(f"data/card-images.yaml: unknown card_id {card_id}")
            continue
        if not isinstance(record, dict):
            errors.append(f"image record {card_id}: must be a mapping")
            continue
        classification = record.get("classification")
        if classification not in IMAGE_CLASSIFICATIONS:
            errors.append(f"image record {card_id}: classification {classification!r} is invalid")
            continue
        asset_path = record.get("asset_path") or ""
        if classification == "missing":
            if asset_path:
                errors.append(f"image record {card_id}: missing classification requires empty asset_path")
        else:
            if not asset_path:
                errors.append(f"image record {card_id}: {classification} image requires asset_path")
            else:
                effective_asset = asset_overrides.get(asset_path) if asset_overrides else None
                if effective_asset is None:
                    effective_asset = root / asset_path
                if not effective_asset.is_file():
                    errors.append(f"image record {card_id}: missing asset {asset_path}")
        reviewed = record.get("reviewed")
        if not isinstance(reviewed, bool):
            errors.append(f"image record {card_id}: reviewed must be true or false")
        reviewed_on = record.get("reviewed_on")
        if reviewed is True and not (isinstance(reviewed_on, str) and DATE_RE.match(reviewed_on)):
            errors.append(f"image record {card_id}: reviewed image requires reviewed_on YYYY-MM-DD")
        if reviewed is False and reviewed_on not in ("", None):
            errors.append(f"image record {card_id}: unreviewed image requires empty reviewed_on")
        if classification != "missing":
            _validate_non_missing_image_source(card_id, record, errors)
        if classification == "proxy" and not record.get("note"):
            errors.append(f"image record {card_id}: proxy image requires note")
        if classification == "exact":
            _validate_exact_image(card_id, record, registry[card_id], errors)

    published_cards = set()
    for volume_id, card_ids in occupied_by_volume.items():
        if publication_statuses.get(volume_id) == "published":
            published_cards.update(card_ids)
    for card_id in sorted(published_cards):
        record = cards.get(card_id)
        if not isinstance(record, dict) or record.get("reviewed") is not True:
            errors.append(f"published binder uses unreviewed image for {card_id}")


def _validate_non_missing_image_source(card_id: str, record: dict, errors: list[str]) -> None:
    provider = record.get("provider")
    if not isinstance(provider, str) or not provider.strip():
        errors.append(f"image record {card_id}: non-missing image requires provider")
        return
    if provider == "evidence-crop":
        source_path = record.get("source_path")
        if not isinstance(source_path, str) or not source_path.startswith("docs/evidence/"):
            errors.append(f"image record {card_id}: evidence crop requires source_path under docs/evidence")
        return
    source_url = record.get("source_url")
    if not isinstance(source_url, str) or not source_url.startswith(("http://", "https://")):
        errors.append(f"image record {card_id}: {provider} image requires HTTP(S) source_url")
    if provider == "local-file" and not str(record.get("usage_basis") or "").strip():
        errors.append(f"image record {card_id}: local-file image requires usage_basis")
    if provider == "tcgdex" and not str(record.get("upstream_id") or "").strip():
        errors.append(f"image record {card_id}: tcgdex image requires upstream_id")
    if provider == "doubleholo":
        if not str(record.get("upstream_id") or "").strip():
            errors.append(f"image record {card_id}: doubleholo image requires upstream_id")
        if record.get("usage_basis") != "Owner-authorized DoubleHolo card catalog image.":
            errors.append(f"image record {card_id}: doubleholo image requires authorized usage_basis")


def _validate_exact_image(card_id: str, record: dict, registry_row: dict, errors: list[str]) -> None:
    confidence = registry_row.get("confidence")
    if confidence == "uncertain":
        errors.append(f"image record {card_id}: exact image cannot use uncertain registry identity")
        return

    set_name = registry_row.get("set") or ""
    number = registry_row.get("number") or ""
    if confidence in {"photo", "confirmed"} and set_name and number:
        return
    if confidence == "confirmed" and not number and record.get("identity_basis"):
        return
    errors.append(
        f"image record {card_id}: exact image requires photo or confirmed registry identity "
        "with populated set and number, or confirmed unnumbered identity_basis"
    )


def validate_transition(previous: dict, current: dict) -> list[str]:
    errors: list[str] = []
    previous_pockets = _occupied_pockets(previous)
    current_pockets = _occupied_pockets(current)
    for pocket_key, previous_pocket in previous_pockets.items():
        current_pocket = current_pockets.get(pocket_key)
        if not current_pocket:
            continue
        previous_status = previous_pocket.get("status")
        current_status = current_pocket.get("status")
        if previous_status == "confirmed" and current_status == "pending":
            if current_pocket.get("observed_card_id") != previous_pocket.get("card_id"):
                errors.append(
                    f"{_format_pocket_key(pocket_key)}: pending placement must carry last "
                    f"observed_card_id {previous_pocket.get('card_id')}"
                )
        elif previous_status == "confirmed" and current_status == "confirmed":
            if current_pocket.get("card_id") != previous_pocket.get("card_id"):
                errors.append(
                    f"{_format_pocket_key(pocket_key)}: confirmed card changed without pending state"
                )
        elif previous_status == "pending" and current_status == "confirmed":
            allowed_cards = {
                card_id for card_id in (
                    previous_pocket.get("card_id"),
                    previous_pocket.get("observed_card_id"),
                ) if card_id
            }
            if current_pocket.get("card_id") not in allowed_cards:
                errors.append(
                    f"{_format_pocket_key(pocket_key)}: confirmed card does not match pending card "
                    f"or observed card from previous state"
                )
        elif previous_status == "pending" and current_status == "pending":
            if (previous_pocket.get("observed_card_id") and
                    current_pocket.get("observed_card_id") != previous_pocket.get("observed_card_id")):
                errors.append(
                    f"{_format_pocket_key(pocket_key)}: pending observed_card_id changed"
                )
    return errors


def _occupied_pockets(project: dict) -> dict[tuple[str, int, int], dict]:
    pockets = {}
    for volume_id, manifest in project.items():
        if not isinstance(manifest, dict):
            continue
        for leaf in manifest.get("leaves", []):
            if not isinstance(leaf, dict) or leaf.get("kind") != "cards":
                continue
            physical_leaf = leaf.get("physical_leaf")
            for pocket in leaf.get("pockets", []):
                if not isinstance(pocket, dict) or pocket.get("empty") is True:
                    continue
                position = pocket.get("position")
                placement = pocket.get("placement") if isinstance(pocket.get("placement"), dict) else {}
                if isinstance(physical_leaf, int) and isinstance(position, int):
                    pockets[(volume_id, physical_leaf, position)] = {
                        "card_id": pocket.get("card_id"),
                        "status": placement.get("status"),
                        "observed_card_id": placement.get("observed_card_id"),
                    }
    return pockets


def _format_pocket_key(key: tuple[str, int, int]) -> str:
    volume_id, physical_leaf, position = key
    return f"{volume_id} physical_leaf {physical_leaf} pocket {position}"


def validate_project(root: Path, previous_ref: str | None = None) -> list[str]:
    root = Path(root)
    errors: list[str] = []
    try:
        registry = load_registry(root / "docs" / "card-registry.md")
    except (FileNotFoundError, ValueError) as exc:
        registry = {}
        errors.append(f"registry validation failed: {exc}")

    manifests = _load_project_manifests(root, errors)
    images_path = root / "data" / "card-images.yaml"
    images_loaded = False
    try:
        images = load_yaml(images_path)
        images_loaded = True
    except FileNotFoundError:
        images = {}
        errors.append("missing image manifest: data/card-images.yaml")
    except ValueError as exc:
        images = {}
        errors.append(str(exc))

    occupied_by_volume: dict[str, set[str]] = {}
    publication_statuses: dict[str, str] = {}
    for volume_id, manifest in manifests.items():
        publication_statuses[volume_id] = manifest.get("publication_status")
        occupied_by_volume[volume_id] = _validate_volume_manifest(
            volume_id, manifest, registry, errors
        )
    _validate_global_duplicates(manifests, errors)

    if images_loaded:
        _validate_images(root, images, registry, occupied_by_volume, publication_statuses, errors)

    if previous_ref:
        previous_manifests = _load_previous_manifests(root, previous_ref, errors)
        if previous_manifests is not None:
            errors.extend(validate_transition(previous_manifests, manifests))

    return errors


class _PublicBinderParser(HTMLParser):
    """Collect rendered binder structure while ignoring unrelated page markup."""

    def __init__(self, page_path: Path):
        super().__init__(convert_charrefs=True)
        self.page_path = page_path
        self.binders: list[dict] = []
        self.stack: list[dict] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        parent = self.stack[-1] if self.stack else {}
        root = parent.get("root")
        spread = parent.get("spread")
        leaf = parent.get("leaf")
        in_pocket = parent.get("in_pocket", False)

        if "data-binder" in attributes:
            root = {
                "name": attributes.get("data-binder") or "(unnamed)",
                "page_path": self.page_path,
                "leaves": [],
                "ids": [],
                "controls": [],
                "previous_controls": [],
                "next_controls": [],
                "positions": [],
                "dialogs": [],
                "dialog_close": [],
                "dialog_previous": [],
                "dialog_next": [],
                "initial_urls": set(),
                "spread_count": 0,
            }
            self.binders.append(root)
            spread = None
            leaf = None
            in_pocket = False

        if root is not None:
            element_id = attributes.get("id")
            if element_id:
                root["ids"].append(element_id)

            if "data-binder-spread" in attributes:
                root["spread_count"] += 1
                spread = root["spread_count"]

            if "data-binder-leaf" in attributes:
                leaf = {
                    "name": attributes.get("data-binder-leaf") or "(unnamed)",
                    "kind": attributes.get("data-kind"),
                    "id": attributes.get("id"),
                    "pockets": 0,
                    "spread": spread,
                }
                root["leaves"].append(leaf)

            if "data-pocket" in attributes:
                in_pocket = True
                if leaf is not None:
                    leaf["pockets"] += 1

            if "data-binder-controls" in attributes:
                root["controls"].append(attributes)
            if "data-binder-prev" in attributes:
                root["previous_controls"].append(attributes)
            if "data-binder-next" in attributes:
                root["next_controls"].append(attributes)
            if "data-binder-position" in attributes:
                root["positions"].append(attributes)
            if tag == "dialog" and "data-card-inspector" in attributes:
                root["dialogs"].append(attributes)
            if "data-card-inspector-close" in attributes:
                root["dialog_close"].append(attributes)
            if "data-card-inspector-previous" in attributes:
                root["dialog_previous"].append(attributes)
            if "data-card-inspector-next" in attributes:
                root["dialog_next"].append(attributes)

            inspector_src = attributes.get("data-inspector-src")
            if inspector_src:
                root.setdefault("card_urls", []).append(inspector_src)

            if tag == "img":
                self._record_image_urls(root, attributes)
                if in_pocket:
                    self._record_card_image(root, leaf, spread, attributes)

        if tag not in HTML_VOID_ELEMENTS:
            self.stack.append({
                "tag": tag,
                "root": root,
                "spread": spread,
                "leaf": leaf,
                "in_pocket": in_pocket,
            })

    def handle_startendtag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        self.handle_starttag(tag, attrs)
        if tag not in HTML_VOID_ELEMENTS:
            self.handle_endtag(tag)

    def handle_endtag(self, tag: str) -> None:
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]["tag"] == tag:
                del self.stack[index:]
                return

    @staticmethod
    def _record_image_urls(root: dict, attributes: dict[str, str | None]) -> None:
        source = attributes.get("src") or ""
        if source:
            root.setdefault("card_urls", []).append(source)
        srcset = attributes.get("srcset") or ""
        root.setdefault("card_urls", []).extend(
            candidate.strip().split()[0]
            for candidate in srcset.split(",")
            if candidate.strip()
        )

    @staticmethod
    def _record_card_image(root: dict, leaf: dict | None, spread: int | None,
                           attributes: dict[str, str | None]) -> None:
        source = attributes.get("src") or ""
        initial = "data-initial-binder-image" in attributes
        if initial and source:
            root["initial_urls"].add(source)
        root.setdefault("images", []).append({
            "source": source,
            "alt": attributes.get("alt"),
            "loading": attributes.get("loading"),
            "initial": initial,
            "spread": spread,
            "leaf": leaf.get("name") if leaf else "(unknown leaf)",
        })


def _is_remote_url(url: str) -> bool:
    parsed = urlsplit(url)
    return parsed.scheme.lower() in {"http", "https"} or bool(parsed.netloc)


def _public_asset_path(public_dir: Path, page_path: Path, url: str) -> Path | None:
    parsed = urlsplit(url)
    if _is_remote_url(url) or not parsed.path:
        return None
    decoded_path = unquote(parsed.path)
    if decoded_path.startswith("/"):
        candidate = public_dir / decoded_path.lstrip("/")
    else:
        candidate = page_path.parent / decoded_path
    try:
        resolved = candidate.resolve()
        resolved.relative_to(public_dir.resolve())
    except (OSError, ValueError):
        return None
    return resolved


def _validate_public_binder(public_dir: Path, root: dict) -> list[str]:
    page = root["page_path"].relative_to(public_dir)
    label = f"{page}: binder {root['name']}"
    errors: list[str] = []

    leaf_names = [leaf["name"] for leaf in root["leaves"]]
    for leaf_name in sorted({name for name in leaf_names if leaf_names.count(name) > 1}):
        errors.append(f"{label}: duplicate binder leaf ID {leaf_name}")
    html_ids = root["ids"]
    for element_id in sorted({item for item in html_ids if html_ids.count(item) > 1}):
        errors.append(f"{label}: duplicate HTML id {element_id}")

    leaf_anchors = set()
    for leaf in root["leaves"]:
        expected_anchor = f"leaf-{leaf['name']}"
        if leaf["id"] != expected_anchor:
            errors.append(
                f"{label}: leaf {leaf['name']} needs direct-link anchor id={expected_anchor!r}"
            )
        else:
            leaf_anchors.add(expected_anchor)
        if leaf["kind"] == "cards" and leaf["pockets"] != 9:
            errors.append(
                f"{label}: card leaf {leaf['name']} must contain exactly 9 pockets "
                f"(found {leaf['pockets']})"
            )
        if leaf["kind"] == "transition" and leaf["pockets"]:
            errors.append(f"{label}: transition leaf {leaf['name']} must not contain pockets")

    if len(root["controls"]) != 1:
        errors.append(f"{label}: must contain exactly one binder controls navigation")
    else:
        controls = root["controls"][0]
        if not (controls.get("aria-label") or controls.get("aria-labelledby")):
            errors.append(f"{label}: binder controls navigation needs an accessible label")
    for direction, key in (("previous", "previous_controls"), ("next", "next_controls")):
        controls = root[key]
        if len(controls) != 1:
            errors.append(f"{label}: must contain exactly one {direction} control")
            continue
        target = controls[0].get("href") or ""
        if not target.startswith("#") or target[1:] not in leaf_anchors:
            errors.append(f"{label}: {direction} control must link to a binder leaf anchor")
    if len(root["positions"]) != 1:
        errors.append(f"{label}: must contain exactly one binder position control")

    if len(root["dialogs"]) != 1:
        errors.append(f"{label}: must contain exactly one card inspector dialog")
    for control_name, key in (
        ("close", "dialog_close"),
        ("previous card", "dialog_previous"),
        ("next card", "dialog_next"),
    ):
        if len(root[key]) != 1:
            errors.append(f"{label}: card inspector dialog needs one {control_name} control")

    for url in root.get("card_urls", []):
        if _is_remote_url(url):
            errors.append(f"{label}: remote card image URL is not allowed: {url}")

    for image in root.get("images", []):
        if not image["source"]:
            errors.append(f"{label}: card image on {image['leaf']} needs a src URL")
        elif not _is_remote_url(image["source"]) and not str(image["alt"] or "").strip():
            errors.append(f"{label}: local card image on {image['leaf']} needs alt text")

        if image["spread"] == 1:
            if not image["initial"]:
                errors.append(
                    f"{label}: first-spread card image on {image['leaf']} must be an initial binder image"
                )
            if image["loading"] != "eager":
                errors.append(f"{label}: initial binder image on {image['leaf']} must use loading=\"eager\"")
        else:
            if image["initial"]:
                errors.append(
                    f"{label}: only first-spread card images may be initial binder images"
                )
            if image["loading"] != "lazy":
                errors.append(
                    f"{label}: non-initial card image on {image['leaf']} must use loading=\"lazy\""
                )

    initial_bytes = 0
    for url in sorted(root["initial_urls"]):
        asset_path = _public_asset_path(public_dir, root["page_path"], url)
        if asset_path is None or not asset_path.is_file():
            errors.append(f"{label}: initial binder image does not resolve under public output: {url}")
            continue
        initial_bytes += asset_path.stat().st_size
    if initial_bytes > INITIAL_BINDER_IMAGE_BUDGET:
        errors.append(
            f"{label}: initial image budget is {initial_bytes:,} bytes; "
            f"maximum is {INITIAL_BINDER_IMAGE_BUDGET:,} bytes"
        )
    return errors


def validate_public_output(public_dir: Path) -> list[str]:
    """Validate only rendered roots that opt into the digital binder contract."""
    public_dir = Path(public_dir)
    if not public_dir.is_dir():
        return [f"public output directory does not exist: {public_dir}"]

    errors: list[str] = []
    for page_path in sorted(public_dir.rglob("*.html")):
        parser = _PublicBinderParser(page_path)
        try:
            parser.feed(page_path.read_text(encoding="utf-8"))
            parser.close()
        except (OSError, UnicodeError) as exc:
            errors.append(f"{page_path.relative_to(public_dir)}: cannot read HTML: {exc}")
            continue
        for root in parser.binders:
            errors.extend(_validate_public_binder(public_dir, root))
    return errors


def _normalize_previous_ref(previous_ref: str | None) -> str | None:
    if not previous_ref or re.fullmatch(r"0+", previous_ref):
        return None
    return previous_ref


def _previous_ref_from_environment() -> str | None:
    return _normalize_previous_ref(
        os.environ.get("DIGITAL_BINDER_PREVIOUS_REF", "").strip()
    )


def _root_path(root: Path, path: Path) -> Path:
    return path if path.is_absolute() else root / path


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-generated", action="store_true")
    mode.add_argument("--check-generated", action="store_true")
    mode.add_argument("--check", action="store_true")
    mode.add_argument("--check-public", type=Path, metavar="PATH")
    parser.add_argument(
        "--registry",
        type=Path,
        default=Path("docs/card-registry.md"),
    )
    parser.add_argument(
        "--output",
        type=Path,
        default=Path("data/generated/card-registry.json"),
    )
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--previous-ref", default=_previous_ref_from_environment())
    args = parser.parse_args(argv)

    root = args.root
    previous_ref = _normalize_previous_ref(args.previous_ref)
    if args.check_public is not None:
        public_dir = _root_path(root, args.check_public)
        errors = validate_public_output(public_dir)
        for error in errors:
            print(error, flush=True)
        return 1 if errors else 0

    registry_path = _root_path(root, args.registry)
    output_path = _root_path(root, args.output)
    try:
        rendered = render_registry_json(load_registry(registry_path))
    except (FileNotFoundError, ValueError):
        if args.check:
            errors = validate_project(root, previous_ref=previous_ref)
            for error in errors:
                print(error, flush=True)
            return 1
        raise

    if args.write_generated:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(output_path, rendered)
        return 0

    generated_current = generated_is_current(output_path, rendered)
    if args.check_generated:
        if generated_current:
            return 0
        print(f"drift detected: {output_path} is out of date", flush=True)
        return 1

    errors = []
    if not generated_current:
        errors.append(f"drift detected: {output_path} is out of date")
    errors.extend(validate_project(root, previous_ref=previous_ref))
    for error in errors:
        print(error, flush=True)
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())
