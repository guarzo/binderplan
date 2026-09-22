#!/usr/bin/env python3
"""Project the card registry into committed JSON output."""

import argparse
import importlib.util
import json
from functools import lru_cache
from pathlib import Path

GENERATED_FIELDS = (
    "id",
    "species",
    "card_name",
    "language",
    "set",
    "number",
    "confidence",
)


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
    errors = module.validate(rows)
    if errors:
        raise ValueError("\n".join(errors))
    return {
        row["id"]: {key: row[key] for key in GENERATED_FIELDS}
        for row in rows
    }


def render_registry_json(rows: dict[str, dict]) -> str:
    ordered = {card_id: rows[card_id] for card_id in sorted(rows)}
    return json.dumps(ordered, ensure_ascii=False, indent=2) + "\n"


def generated_is_current(path: Path, expected: str) -> bool:
    return path.exists() and path.read_text(encoding="utf-8") == expected


def _write_atomic(path: Path, content: str) -> None:
    tmp = path.with_name(path.name + ".tmp")
    tmp.write_text(content, encoding="utf-8")
    tmp.replace(path)


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--write-generated", action="store_true")
    mode.add_argument("--check-generated", action="store_true")
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
    args = parser.parse_args(argv)

    rendered = render_registry_json(load_registry(args.registry))
    if args.write_generated:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        _write_atomic(args.output, rendered)
        return 0

    if generated_is_current(args.output, rendered):
        return 0
    print(f"drift detected: {args.output} is out of date", flush=True)
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
