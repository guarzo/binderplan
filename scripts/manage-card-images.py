#!/usr/bin/env python3
"""Review and approve local card images for the digital binder."""

import argparse
from io import BytesIO
import hashlib
import html
import json
import sys
from datetime import date
from http.client import IncompleteRead
from pathlib import Path
from urllib.parse import quote, urlparse
from urllib.request import Request, urlopen

import yaml
from PIL import Image

import digital_binder

REVIEW_ROOT = Path("tmp/digital-binder-review")
CARD_ASSET_DIR = Path("assets/images/cards")
DOUBLEHOLO_VARIANT_WARNING = (
    "Warning: exact_identity_match does not verify edition/variant; "
    "visual confirmation of edition, stamp, holo treatment, and other variants is required before approval."
)
DOUBLEHOLO_CONFIRMED_IDENTITY_BASIS = (
    "curator visually confirmed printing; DoubleHolo set-name alias differs from registry"
)
DOUBLEHOLO_NONPRINTED_NUMBER_MARKERS = {
    "n-a",
    "na",
    "no-number",
    "none",
    "non-printed",
    "nonprinted",
    "not-numbered",
    "un-numbered",
    "unnumbered",
}


class CachedHTTPResponse:
    def __init__(self, payload: bytes):
        self.payload = payload

    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc, tb):
        return False

    def read(self):
        return self.payload


def _write_bytes_atomic(path: Path, payload: bytes) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_bytes(payload)
    tmp.replace(path)


def _remove_if_exists(path: Path) -> None:
    try:
        path.unlink()
    except FileNotFoundError:
        pass


def _write_text_atomic(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def _json_dump(data: object) -> str:
    return json.dumps(data, ensure_ascii=False, indent=2, sort_keys=True) + "\n"


def _load_images(root: Path) -> dict:
    return digital_binder.load_yaml(root / "data/card-images.yaml")


def _load_registry(root: Path) -> dict[str, dict]:
    return digital_binder.load_registry(root / "docs/card-registry.md")


def _card_asset_path(root: Path, card_id: str) -> Path:
    return root / CARD_ASSET_DIR / f"{card_id}.webp"


def _asset_record_path(card_id: str) -> str:
    return str(CARD_ASSET_DIR / f"{card_id}.webp")


def _candidate_cache_path(root: Path, card_id: str) -> Path:
    return root / REVIEW_ROOT / "candidates" / f"{card_id}.json"


def _doubleholo_candidate_cache_path(root: Path, card_id: str) -> Path:
    return root / REVIEW_ROOT / "doubleholo" / f"{card_id}.json"


def _page_review_paths(root: Path, leaf_id: str) -> tuple[Path, Path]:
    base = root / REVIEW_ROOT / "pages" / leaf_id
    return base.with_suffix(".html"), base.with_suffix(".json")


def _cache_opener(root: Path):
    cache_dir = root / REVIEW_ROOT / "cache"

    def opener(request: Request, timeout: int):
        url = request.full_url
        cache_identity = b"\0".join((
            request.get_method().encode("utf-8"),
            url.encode("utf-8"),
            request.data or b"",
        ))
        key = hashlib.sha256(cache_identity).hexdigest() + ".json"
        path = cache_dir / key
        if path.exists():
            return CachedHTTPResponse(path.read_bytes())
        with urlopen(request, timeout=timeout) as response:
            payload = response.read()
        _write_bytes_atomic(path, payload)
        return CachedHTTPResponse(payload)

    return opener


def _search_candidates(root: Path, card_id: str) -> dict:
    registry = _load_registry(root)
    if card_id not in registry:
        raise ValueError(f"unknown card_id {card_id}")
    row = registry[card_id]
    candidates = digital_binder.rank_candidates(
        row,
        digital_binder.search_tcgdex(row, opener=_cache_opener(root)),
    )
    report = {
        "card_id": card_id,
        "registry": row,
        "candidates": [
            {"candidate_index": index, **candidate}
            for index, candidate in enumerate(candidates)
        ],
    }
    _write_text_atomic(_candidate_cache_path(root, card_id), _json_dump(report))
    return report


def _print_candidate_summary(report: dict) -> None:
    if report["candidates"]:
        for candidate in report["candidates"]:
            print(
                f"[{candidate['candidate_index']}] {candidate.get('provider_id')} "
                f"score={candidate.get('score')} image={candidate.get('image_url') or 'none'}"
            )
    else:
        print(f"no candidates for {report['card_id']}")


def search_command(args) -> int:
    root = Path.cwd()
    report = _search_candidates(root, args.card_id)
    _print_candidate_summary(report)
    return 0


def _search_doubleholo_candidates(root: Path, card_id: str) -> dict:
    registry = _load_registry(root)
    if card_id not in registry:
        raise ValueError(f"unknown card_id {card_id}")
    row = registry[card_id]
    candidates = digital_binder.rank_doubleholo_candidates(
        row,
        digital_binder.search_doubleholo(row, opener=_cache_opener(root)),
    )
    report = {
        "card_id": card_id,
        "registry": row,
        "candidates": [
            {"candidate_index": index, **candidate}
            for index, candidate in enumerate(candidates)
        ],
    }
    _write_text_atomic(_doubleholo_candidate_cache_path(root, card_id), _json_dump(report))
    return report


def search_doubleholo_command(args) -> int:
    root = Path.cwd()
    report = _search_doubleholo_candidates(root, args.card_id)
    _print_candidate_summary(report)
    print(DOUBLEHOLO_VARIANT_WARNING)
    return 0


def _find_leaf(root: Path, leaf_id: str) -> dict:
    for volume_id in digital_binder.VOLUME_IDS:
        manifest = digital_binder.load_yaml(root / "data" / "binders" / f"{volume_id}.yaml")
        for leaf in manifest.get("leaves", []):
            if isinstance(leaf, dict) and leaf.get("id") == leaf_id:
                return leaf
    raise ValueError(f"unknown leaf_id {leaf_id}")


def _occupied_leaf_card_ids(leaf: dict) -> list[str]:
    if leaf.get("kind") != "cards":
        raise ValueError(f"leaf {leaf.get('id')} is not a card leaf")
    card_ids = []
    for pocket in leaf.get("pockets", []):
        if isinstance(pocket, dict) and pocket.get("empty") is not True and pocket.get("card_id"):
            card_ids.append(pocket["card_id"])
    return card_ids


def _render_review_html(leaf_id: str, reports: list[dict]) -> str:
    parts = [
        "<!doctype html><meta charset=\"utf-8\">",
        f"<title>Digital binder review {html.escape(leaf_id)}</title>",
        f"<h1>Digital binder review {html.escape(leaf_id)}</h1>",
    ]
    for report in reports:
        registry = report["registry"]
        heading = f"{html.escape(report['card_id'])}: {html.escape(registry.get('card_name', ''))}"
        parts.append(f"<section><h2>{heading}</h2>")
        parts.append("<dl>")
        for field in ("language", "set", "number", "confidence"):
            parts.append(f"<dt>{field}</dt><dd>{html.escape(str(registry.get(field, '')))}</dd>")
        parts.append("</dl>")
        if not report["candidates"]:
            parts.append("<p>No candidates returned.</p>")
        for candidate in report["candidates"]:
            parts.append("<article>")
            parts.append(
                f"<h3>Candidate {candidate['candidate_index']}: "
                f"{html.escape(str(candidate.get('provider_id', '')))}</h3>"
            )
            parts.append("<dl>")
            for field in ("name", "set_id", "set_name", "local_id", "score", "review_state"):
                value = html.escape(str(candidate.get(field, "")))
                parts.append(f"<dt>{field}</dt><dd>{value}</dd>")
            parts.append("</dl>")
            image_url = candidate.get("image_url")
            if image_url:
                escaped_url = html.escape(image_url, quote=True)
                parts.append(f"<img src=\"{escaped_url}\" alt=\"Candidate card image\">")
            else:
                parts.append("<p>No upstream image.</p>")
            parts.append("</article>")
        parts.append("</section>")
    return "\n".join(parts) + "\n"


def review_command(args) -> int:
    root = Path.cwd()
    leaf = _find_leaf(root, args.page)
    reports = [_search_candidates(root, card_id) for card_id in _occupied_leaf_card_ids(leaf)]
    html_path, json_path = _page_review_paths(root, args.page)
    _write_text_atomic(html_path, _render_review_html(args.page, reports))
    _write_text_atomic(json_path, _json_dump({"leaf_id": args.page, "cards": reports}))
    print(f"wrote {html_path}")
    print(f"wrote {json_path}")
    return 0


def _parse_box(raw: str) -> tuple[int, int, int, int]:
    try:
        parts = tuple(int(part) for part in raw.split(","))
    except ValueError as exc:
        raise ValueError("box must be LEFT,TOP,RIGHT,BOTTOM") from exc
    if len(parts) != 4:
        raise ValueError("box must be LEFT,TOP,RIGHT,BOTTOM")
    left, top, right, bottom = parts
    if not (0 <= left < right and 0 <= top < bottom):
        raise ValueError("box must satisfy 0 <= LEFT < RIGHT and 0 <= TOP < BOTTOM")
    return parts


def _validate_date(raw: str) -> str:
    if not digital_binder.DATE_RE.match(raw):
        raise ValueError("reviewed-on must use YYYY-MM-DD")
    return raw


def _require_card(root: Path, card_id: str) -> dict:
    registry = _load_registry(root)
    if card_id not in registry:
        raise ValueError(f"unknown card_id {card_id}")
    return registry[card_id]


def _check_classification(row: dict, classification: str, note: str | None) -> None:
    if classification == "exact" and row.get("confidence") == "uncertain":
        raise ValueError("exact image cannot use uncertain registry identity")
    if classification == "proxy" and not str(note or "").strip():
        raise ValueError("proxy approval requires --note")


def _same_stable_image_source(existing: dict, record: dict) -> bool:
    if existing.get("provider") != record.get("provider"):
        return False
    existing_upstream_id = str(existing.get("upstream_id") or "").strip()
    record_upstream_id = str(record.get("upstream_id") or "").strip()
    if existing_upstream_id or record_upstream_id:
        return bool(existing_upstream_id and record_upstream_id and existing_upstream_id == record_upstream_id)
    existing_source_url = str(existing.get("source_url") or "").strip()
    record_source_url = str(record.get("source_url") or "").strip()
    return bool(existing_source_url and record_source_url and existing_source_url == record_source_url)


def _merged_images(root: Path, card_id: str, record: dict) -> dict:
    images = _load_images(root)
    existing = images.setdefault("cards", {}).get(card_id)
    if (
            isinstance(existing, dict)
            and existing.get("identity_basis")
            and not record.get("identity_basis")
            and record.get("classification") == "exact"
            and _same_stable_image_source(existing, record)):
        record["identity_basis"] = existing["identity_basis"]
    images["cards"][card_id] = record
    return images


def _replace_reviewed_image(root: Path, card_id: str, record: dict, staged_asset: Path) -> None:
    final_asset = _card_asset_path(root, card_id)
    images = _merged_images(root, card_id, record)
    asset_record_path = _asset_record_path(card_id)
    errors = digital_binder.validate_image_manifest(
        root,
        images,
        asset_overrides={asset_record_path: staged_asset},
    )
    if errors:
        _remove_if_exists(staged_asset)
        raise ValueError("\n".join(errors))

    manifest_path = root / "data/card-images.yaml"
    old_manifest = manifest_path.read_bytes()
    old_asset = final_asset.read_bytes() if final_asset.exists() else None
    try:
        final_asset.parent.mkdir(parents=True, exist_ok=True)
        staged_asset.replace(final_asset)
        digital_binder.write_image_manifest_atomically(root, images)
    except Exception:
        _write_bytes_atomic(manifest_path, old_manifest)
        if old_asset is None:
            _remove_if_exists(final_asset)
        else:
            _write_bytes_atomic(final_asset, old_asset)
        _remove_if_exists(staged_asset)
        raise


def _stage_path(root: Path, card_id: str) -> Path:
    return root / REVIEW_ROOT / "staged" / f"{card_id}.webp"


def _save_local_image_as_webp(source: Path, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    with Image.open(source) as image:
        image.convert("RGB").save(tmp, format="WEBP")
    tmp.replace(target)


def _save_image_payload_as_webp(payload: bytes, target: Path) -> None:
    target.parent.mkdir(parents=True, exist_ok=True)
    tmp = target.with_name(target.name + ".tmp")
    with Image.open(BytesIO(payload)) as image:
        image.verify()
    with Image.open(BytesIO(payload)) as image:
        image.convert("RGB").save(tmp, format="WEBP")
    tmp.replace(target)


def _require_http_url(url: str, context: str) -> None:
    if urlparse(url).scheme not in {"http", "https"}:
        raise ValueError(f"{context} requires an HTTP(S) URL")


def approve_local_command(args) -> int:
    root = Path.cwd()
    if not args.source_url.startswith(("http://", "https://")):
        raise ValueError("approve-local requires an HTTP(S) source URL")
    if not args.usage_basis.strip():
        raise ValueError("approve-local requires a nonempty usage basis")
    row = _require_card(root, args.card_id)
    _check_classification(row, args.classification, args.note)
    staged_asset = _stage_path(root, args.card_id)
    _save_local_image_as_webp(Path(args.file), staged_asset)
    record = {
        "classification": args.classification,
        "asset_path": _asset_record_path(args.card_id),
        "reviewed": True,
        "reviewed_on": date.today().isoformat(),
        "provider": "local-file",
        "source_url": args.source_url,
        "usage_basis": args.usage_basis.strip(),
    }
    if args.note:
        record["note"] = args.note
    _replace_reviewed_image(root, args.card_id, record, staged_asset)
    print(f"approved local image for {args.card_id}")
    return 0


def _candidate_cache_recovery_command(source: str, card_id: str) -> str:
    commands = {
        "tcgdex": "search",
        "doubleholo": "search-doubleholo",
    }
    command = commands.get(source, source)
    return f"{command} {card_id}"


def _load_candidate_from_path(path: Path, card_id: str, candidate_index: int, source: str) -> dict:
    if not path.exists():
        recovery_command = _candidate_cache_recovery_command(source, card_id)
        raise ValueError(
            f"missing {source} candidate cache for {card_id}; run {recovery_command} first"
        )
    data = json.loads(path.read_text(encoding="utf-8"))
    for candidate in data.get("candidates", []):
        if candidate.get("candidate_index") == candidate_index:
            return candidate
    raise ValueError(f"candidate index {candidate_index} not found for {card_id}")


def _load_candidate(root: Path, card_id: str, candidate_index: int) -> dict:
    return _load_candidate_from_path(
        _candidate_cache_path(root, card_id), card_id, candidate_index, "tcgdex"
    )


def _load_doubleholo_candidate(root: Path, card_id: str, candidate_index: int) -> dict:
    return _load_candidate_from_path(
        _doubleholo_candidate_cache_path(root, card_id), card_id, candidate_index, "doubleholo"
    )


def _fetch_doubleholo_object(object_id: str, opener=urlopen) -> dict:
    clean_object_id = str(object_id or "").strip()
    if not clean_object_id:
        raise ValueError(
            "DoubleHolo approval cache is stale or malformed: selected candidate lacks provider_id; "
            "rerun search-doubleholo"
        )
    request = Request(
        f"https://w5sf479zkl-dsn.algolia.net/1/indexes/production_cards/{quote(clean_object_id, safe='')}",
        headers={
            "User-Agent": digital_binder.TCGDEX_USER_AGENT,
            "X-Algolia-Application-Id": digital_binder.DOUBLEHOLO_APPLICATION_ID,
            "X-Algolia-API-Key": digital_binder.DOUBLEHOLO_SEARCH_ONLY_API_KEY,
        },
        method="GET",
    )
    try:
        with opener(request, timeout=20) as response:
            payload = response.read()
    except (OSError, IncompleteRead) as exc:
        raise ValueError(f"DoubleHolo object fetch failed for {clean_object_id}: {exc}") from exc
    try:
        data = json.loads(payload.decode("utf-8"))
    except UnicodeDecodeError as exc:
        raise ValueError(f"DoubleHolo object fetch returned invalid JSON for {clean_object_id}: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise ValueError(f"DoubleHolo object fetch returned invalid JSON for {clean_object_id}: {exc}") from exc
    if not isinstance(data, dict):
        raise ValueError(f"DoubleHolo object fetch returned malformed object for {clean_object_id}")
    return data


def _recomputed_doubleholo_candidate(row: dict, candidate: dict, opener=urlopen) -> dict:
    provider_id = str(candidate.get("provider_id") or "").strip()
    raw = _fetch_doubleholo_object(provider_id, opener=opener)
    if str(raw.get("objectID") or "") != provider_id:
        raise ValueError(
            f"DoubleHolo objectID mismatch for selected candidate: expected {provider_id}, "
            f"got {raw.get('objectID')!r}"
        )
    normalized = digital_binder.normalize_doubleholo_candidate(raw)
    ranked = digital_binder.rank_doubleholo_candidates(row, [normalized])
    if not ranked:
        raise ValueError("selected DoubleHolo candidate could not be ranked")
    return ranked[0]


def _doubleholo_confirmed_identity_record(args, recomputed: dict) -> dict:
    if args.classification != "exact":
        raise ValueError("--confirm-identity is only allowed for exact DoubleHolo approvals")
    if not str(args.note or "").strip():
        raise ValueError("--confirm-identity requires a nonempty --note")
    if not recomputed.get("image_url"):
        raise ValueError("--confirm-identity requires a recomputed candidate with image_url")
    for field in ("name_match", "number_match", "language_match"):
        if recomputed.get(field) is not True:
            raise ValueError(
                "--confirm-identity may only override a DoubleHolo set-name alias mismatch"
            )
    if recomputed.get("set_match") is True:
        raise ValueError("--confirm-identity is only for DoubleHolo set-name alias mismatches")
    return {"identity_basis": DOUBLEHOLO_CONFIRMED_IDENTITY_BASIS}


def _check_doubleholo_confirm_unnumbered_args(args, row: dict) -> None:
    if args.classification != "exact":
        raise ValueError("--confirm-unnumbered is only allowed for exact DoubleHolo approvals")
    if row.get("confidence") != "confirmed":
        raise ValueError("--confirm-unnumbered requires registry confidence exactly confirmed")
    if str(row.get("number") or "").strip():
        raise ValueError("--confirm-unnumbered requires blank registry number")
    if not str(args.note or "").strip():
        raise ValueError("--confirm-unnumbered requires a nonempty --note")
    if not str(getattr(args, "identity_basis", None) or "").strip():
        raise ValueError("--confirm-unnumbered requires a nonempty --identity-basis")


def _doubleholo_number_is_blank_or_nonprinted(number: str | None) -> bool:
    raw_number = str(number or "").strip()
    if not raw_number:
        return True
    normalized = raw_number.casefold().replace(" ", "-").replace("/", "-")
    if normalized.startswith("sealed-") and len(normalized) > len("sealed-"):
        return True
    return normalized in DOUBLEHOLO_NONPRINTED_NUMBER_MARKERS


def _doubleholo_confirmed_unnumbered_record(args, recomputed: dict) -> dict:
    if not recomputed.get("image_url"):
        raise ValueError("--confirm-unnumbered requires a recomputed candidate with image_url")
    if not _doubleholo_number_is_blank_or_nonprinted(recomputed.get("local_id")):
        raise ValueError(
            "--confirm-unnumbered requires blank, provider-internal, or nonprinted candidate number"
        )
    for field in ("name_match", "language_match", "set_match"):
        if recomputed.get(field) is not True:
            raise ValueError(
                "--confirm-unnumbered requires recomputed name_match, language_match, and set_match"
            )
    return {"identity_basis": str(args.identity_basis).strip()}


def _approve_remote_candidate(root: Path, args, candidate: dict, record: dict, context: str) -> None:
    image_url = candidate.get("image_url")
    if not image_url:
        raise ValueError("selected candidate has no image_url")
    _require_http_url(image_url, f"approve {context} candidate image")
    request = Request(image_url, headers={"User-Agent": digital_binder.TCGDEX_USER_AGENT})
    with urlopen(request, timeout=20) as response:
        payload = response.read()
    staged_asset = _stage_path(root, args.card_id)
    _save_image_payload_as_webp(payload, staged_asset)
    record.update({
        "classification": args.classification,
        "asset_path": _asset_record_path(args.card_id),
        "reviewed": True,
        "reviewed_on": date.today().isoformat(),
        "source_url": image_url,
    })
    if args.note:
        record["note"] = args.note
    _replace_reviewed_image(root, args.card_id, record, staged_asset)


def approve_command(args) -> int:
    root = Path.cwd()
    row = _require_card(root, args.card_id)
    _check_classification(row, args.classification, args.note)
    candidate = _load_candidate(root, args.card_id, args.candidate_index)
    _approve_remote_candidate(root, args, candidate, {
        "provider": "tcgdex",
        "upstream_id": candidate.get("provider_id") or "",
    }, "tcgdex")
    print(f"approved candidate {args.candidate_index} for {args.card_id}")
    return 0


def approve_doubleholo_command(args) -> int:
    root = Path.cwd()
    row = _require_card(root, args.card_id)
    confirm_identity = bool(getattr(args, "confirm_identity", False))
    confirm_unnumbered = bool(getattr(args, "confirm_unnumbered", False))
    if confirm_identity and confirm_unnumbered:
        raise ValueError("--confirm-unnumbered cannot combine with --confirm-identity")
    _check_classification(row, args.classification, args.note)
    if confirm_identity and args.classification != "exact":
        raise ValueError("--confirm-identity is only allowed for exact DoubleHolo approvals")
    if confirm_identity and not str(args.note or "").strip():
        raise ValueError("--confirm-identity requires a nonempty --note")
    if confirm_unnumbered:
        _check_doubleholo_confirm_unnumbered_args(args, row)
    candidate = _load_doubleholo_candidate(root, args.card_id, args.candidate_index)
    recomputed = _recomputed_doubleholo_candidate(row, candidate, opener=urlopen)
    identity_record = {}
    if confirm_identity:
        identity_record = _doubleholo_confirmed_identity_record(args, recomputed)
    elif confirm_unnumbered:
        identity_record = _doubleholo_confirmed_unnumbered_record(args, recomputed)
    elif args.classification == "exact" and recomputed.get("exact_identity_match") is not True:
        raise ValueError("exact DoubleHolo approval requires a recomputed exact identity match")
    print(DOUBLEHOLO_VARIANT_WARNING)
    record = {
        "provider": "doubleholo",
        "upstream_id": recomputed.get("provider_id") or "",
        "usage_basis": "Owner-authorized DoubleHolo card catalog image.",
    }
    record.update(identity_record)
    _approve_remote_candidate(root, args, recomputed, record, "doubleholo")
    print(f"approved DoubleHolo candidate {args.candidate_index} for {args.card_id}")
    return 0


def _source_under_evidence(root: Path, source: Path) -> tuple[Path, str]:
    source_abs = source.resolve()
    root_abs = root.resolve()
    try:
        rel = source_abs.relative_to(root_abs)
    except ValueError as exc:
        raise ValueError("crop-evidence source must be under docs/evidence") from exc
    if len(rel.parts) < 2 or rel.parts[0] != "docs" or rel.parts[1] != "evidence":
        raise ValueError("crop-evidence source must be under docs/evidence")
    return source_abs, rel.as_posix()


def crop_evidence_command(args) -> int:
    root = Path.cwd()
    _require_card(root, args.card_id)
    reviewed_on = _validate_date(args.reviewed_on)
    source, source_rel = _source_under_evidence(root, Path(args.source))
    staged_asset = _stage_path(root, args.card_id)
    box = _parse_box(args.box)
    digital_binder.crop_evidence_photo(source, box, staged_asset)
    record = {
        "classification": "photo-crop",
        "asset_path": _asset_record_path(args.card_id),
        "reviewed": True,
        "reviewed_on": reviewed_on,
        "provider": "evidence-crop",
        "source_path": source_rel,
        "crop_box": list(box),
    }
    _replace_reviewed_image(root, args.card_id, record, staged_asset)
    print(f"cropped evidence image for {args.card_id}")
    return 0


def mark_missing_command(args) -> int:
    root = Path.cwd()
    _require_card(root, args.card_id)
    record = {
        "classification": "missing",
        "asset_path": "",
        "reviewed": True,
        "reviewed_on": date.today().isoformat(),
        "note": args.note,
    }
    images = _merged_images(root, args.card_id, record)
    digital_binder.write_image_manifest_atomically(root, images)
    print(f"marked {args.card_id} missing")
    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    subcommands = parser.add_subparsers(dest="command", required=True)

    search = subcommands.add_parser("search")
    search.add_argument("card_id")
    search.set_defaults(func=search_command)

    search_doubleholo = subcommands.add_parser(
        "search-doubleholo",
        description=DOUBLEHOLO_VARIANT_WARNING,
        epilog=DOUBLEHOLO_VARIANT_WARNING,
    )
    search_doubleholo.add_argument("card_id")
    search_doubleholo.set_defaults(func=search_doubleholo_command)

    review = subcommands.add_parser("review")
    review.add_argument("--page", required=True)
    review.set_defaults(func=review_command)

    approve = subcommands.add_parser("approve")
    approve.add_argument("card_id")
    approve.add_argument("--candidate-index", required=True, type=int)
    approve.add_argument("--classification", choices=("exact", "proxy"), required=True)
    approve.add_argument("--note")
    approve.set_defaults(func=approve_command)

    approve_doubleholo = subcommands.add_parser(
        "approve-doubleholo",
        description=(
            "Approve an owner-authorized DoubleHolo image. Use --confirm-identity only for "
            "curator-confirmed exact approvals where DoubleHolo's set name is an alias for the "
            "registry identity. Use --confirm-unnumbered only for curator-confirmed exact "
            "approvals of genuinely unnumbered registry printings."
        ),
    )
    approve_doubleholo.add_argument("card_id")
    approve_doubleholo.add_argument("--candidate-index", required=True, type=int)
    approve_doubleholo.add_argument("--classification", choices=("exact", "proxy"), required=True)
    approve_doubleholo.add_argument("--note")
    approve_doubleholo.add_argument(
        "--confirm-identity",
        action="store_true",
        help=(
            "permit a curator-confirmed exact DoubleHolo set-name alias mismatch; requires "
            "--note and cannot override number, language, name, image, uncertain registry, or variants"
        ),
    )
    approve_doubleholo.add_argument(
        "--confirm-unnumbered",
        action="store_true",
        help=(
            "permit a curator-confirmed exact DoubleHolo scan for a genuinely unnumbered "
            "confirmed registry printing; requires --note and --identity-basis, and cannot be "
            "combined with --confirm-identity"
        ),
    )
    approve_doubleholo.add_argument(
        "--identity-basis",
        help="curator provenance explaining the unnumbered printing identity",
    )
    approve_doubleholo.set_defaults(func=approve_doubleholo_command)

    approve_local = subcommands.add_parser("approve-local")
    approve_local.add_argument("card_id")
    approve_local.add_argument("--file", required=True)
    approve_local.add_argument("--source-url", required=True)
    approve_local.add_argument("--usage-basis", required=True)
    approve_local.add_argument("--classification", choices=("exact", "proxy"), required=True)
    approve_local.add_argument("--note")
    approve_local.set_defaults(func=approve_local_command)

    crop = subcommands.add_parser("crop-evidence")
    crop.add_argument("card_id")
    crop.add_argument("--source", required=True)
    crop.add_argument("--box", required=True)
    crop.add_argument("--reviewed-on", required=True)
    crop.set_defaults(func=crop_evidence_command)

    missing = subcommands.add_parser("mark-missing")
    missing.add_argument("card_id")
    missing.add_argument("--note", required=True)
    missing.set_defaults(func=mark_missing_command)

    return parser


def main(argv=None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        return args.func(args)
    except (OSError, ValueError, yaml.YAMLError, json.JSONDecodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
