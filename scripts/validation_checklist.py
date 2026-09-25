#!/usr/bin/env python3
"""Build the owner's review checklist from published card and placement records."""

import argparse
import hashlib
from pathlib import Path
import re
import shutil
import subprocess
from tempfile import TemporaryDirectory

import yaml

import digital_binder

BINDERS = (
    ("volume-1", "Volume I"),
    ("volume-2", "Volume II"),
    ("waifu", "Trainer Full Arts"),
    ("stamped-cards", "Stamped Cards"),
    ("emolga-masterset", "Emolga Masterset"),
)
OUTPUT = Path("docs/card-validation-checklist.md")
PDF_OUTPUT = OUTPUT.with_suffix(".pdf")
PDF_SOURCE = Path("docs/card-validation-checklist.pdf.sha256")
COLLECTOR_NUMBER = re.compile(r"\b\d{1,3}/\d{1,3}\b")
CJK_RUN = re.compile(r"[\u2e80-\u9fff\uf900-\ufaff\u3040-\u30ff\u31f0-\u31ff\uff00-\uffef\uac00-\ud7af]+")
# A photo-confirmed owner card with provisional inclusion but no pocket in a leaf.
UNPLACED_OWNED = {"snivy-04": ("Stamped Cards", "Provisional page 8 · pocket unverified")}


def _published_route(root: Path, binder_id: str) -> bool:
    route = root / "content/gallery" / binder_id / "_index.md"
    if not route.is_file():
        return False
    content = route.read_text(encoding="utf-8")
    if content.startswith("---\n"):
        frontmatter = yaml.safe_load(content.split("---", 2)[1]) or {}
        return frontmatter.get("draft") is not True
    return True


def collect_review_items(root: Path) -> list[dict]:
    registry = digital_binder.load_registry(root / "docs/card-registry.md")
    images = digital_binder.load_yaml(root / "data/card-images.yaml")["cards"]
    items = []
    occupied_ids = set()
    published_titles = set()
    for binder_id, title in BINDERS:
        path = root / "data/binders" / f"{binder_id}.yaml"
        if binder_id == "emolga-masterset" and not path.is_file() and not _published_route(root, binder_id):
            continue
        binder = digital_binder.load_yaml(path)
        if binder["publication_status"] != "published":
            continue
        published_titles.add(title)
        for leaf in binder["leaves"]:
            for pocket in leaf.get("pockets", []):
                card_id = pocket.get("card_id")
                if not card_id:  # Empty or unowned wanted-reference pocket.
                    continue
                occupied_ids.add(card_id)
                card, image = registry[card_id], images[card_id]
                reasons = []
                if image["classification"] != "exact":
                    reasons.append(f"{image['classification']} image")
                if card["confidence"] == "uncertain":
                    reasons.append("printing uncertain")
                if pocket["placement"]["status"] == "pending":
                    reasons.append("physical placement")
                if not reasons and card["confidence"] == "photo":
                    reasons.append("photo-based identity")
                if not reasons:
                    continue
                if pocket["placement"]["status"] == "pending":
                    location = f"Digital page {leaf['physical_leaf']}, slot {pocket['position']} (not a physical pocket claim)"
                else:
                    location = f"Leaf {leaf['physical_leaf']}, pocket {pocket['position']}"
                items.append({
                    "id": card_id, "name": card["card_name"] or card["species"],
                    "english_name": card["species"], "number": card["number"] or "", "number_basis": "",
                    "collection": title, "location": location,
                    "reasons": reasons,
                    "tier": "follow-up" if reasons == ["photo-based identity"] else "priority",
                })

    for card_id, (title, location) in UNPLACED_OWNED.items():
        if title not in published_titles or card_id in occupied_ids:
            continue
        card, image = registry[card_id], images[card_id]
        items.append({
            "id": card_id, "name": card["card_name"] or card["species"],
            "english_name": card["species"], "number": card["number"] or "", "number_basis": "",
            "collection": title, "location": location,
            "reasons": [f"{image['classification']} image", "stamp/edition verification", "physical placement"],
            "tier": "priority",
        })

    holding = digital_binder.load_yaml(root / "data/holding-binder.yaml")
    holding_cards = (
        (f"Photographed page {page['id']}, pocket {pocket['position']}", pocket["card"])
        for page in holding["pages"] for pocket in page["pockets"] if pocket.get("card")
    )
    top_loaders = (
        (f"Trade top loader ({entry['photo_position']}; no physical pocket)", entry["card"])
        for entry in holding["top_loaders"]
    )
    for location, card in (*holding_cards, *top_loaders):
        reasons = []
        classification = card["image"]["classification"]
        if classification != "exact":
            reasons.append(f"{classification} image")
        if card["identity_confidence"] in {"medium", "limited"}:
            reasons.append("identity needs in-hand review")
        if not reasons:
            continue  # Holding 'high' is photo confidence, not a missing in-hand-review state.
        recorded_number = COLLECTOR_NUMBER.search(card["name"]) if not card.get("number") else None
        items.append({
            "id": card["id"], "name": card["name"],
            "english_name": card["name"].split(" — ", 1)[0],
            "number": card.get("number") or (recorded_number.group() if recorded_number else ""),
            "number_basis": "recorded label; verify" if recorded_number else "",
            "collection": "Holding binder", "location": location,
            "reasons": reasons,
            "tier": "follow-up" if reasons == ["photo-based identity"] else "priority",
        })
    return items


def collect_duplicate_candidates(root: Path) -> list[dict]:
    registry = digital_binder.load_registry(root / "docs/card-registry.md")
    pairs = digital_binder.load_registry_module().duplicate_printings(registry.values())
    return sorted(({
        "ids": (left["id"], right["id"]),
        "english_name": left["species"],
        "number": left["number"],
    } for left, right in pairs), key=lambda pair: pair["ids"])


def render_checklist(items: list[dict], pairs: list[dict]) -> str:
    lines = [
        "# Card validation checklist",
        "",
        "Owner review of **published, owned cards** whose image, printing, or placement still needs checking. "
        "Unchecked entries are questions, not evidence of a mistake. This checklist does not change the public collection or establish an in-hand confirmation.",
        "",
        "English names and recorded card numbers are provided to help locate the physical copy. "
        "A number taken only from a Holding display name is flagged for verification; vintage No.xxx can be a printed Pokédex number rather than a collector number. 'Not recorded' is not a new identification. "
        "For each card, compare the **physical copy** with its gallery image and recorded identity: "
        "printed name/language, set and number, edition/stamp/foil or finish, and actual page/pocket when noted. "
        "Record the corrected printing, a photo or source reference, the verification date, and whether the current local image is exact. "
        "Do not mark an item resolved from a catalogue image alone. Send your completed notes/photos for registry, image, and manifest updates; keep originals archived.",
        "",
        "**Priority** covers non-exact images, uncertain identities, medium/limited Holding readings, "
        "and unverified physical placement. **Follow-up** covers registry photo-confidence identities "
        "with exact images that have not been independently checked in hand. Holding 'high' alone "
        "does not assert whether an in-hand check has or has not occurred, so it is not queued. "
        "The two Emolga wanted reference prints are unowned and are not entries here. "
        "The provisional Stamped Snivy is queued without an invented page-eight pocket. "
        "The five Trade cards remain owned; only their separately recorded availability is authoritative. "
        "Use a separate sheet for notes if more room is needed; do not edit this generated checklist to record checks.",
        "",
    ]
    for tier, heading in (("priority", "Priority review"), ("follow-up", "In-hand follow-up")):
        subset = [item for item in items if item["tier"] == tier]
        lines.extend((f"## {heading} ({len(subset)})", ""))
        for _, title in (*BINDERS, ("holding", "Holding binder")):
            entries = [item for item in subset if item["collection"] == title]
            if not entries:
                continue
            lines.extend((f"### {title} ({len(entries)})", ""))
            for item in entries:
                reasons = ", ".join(item["reasons"])
                label = "Recorded" if title == "Holding binder" else "Printed"
                printed = f" · {label}: {item['name']}" if item["name"] != item["english_name"] else ""
                number = item["number"] or "not recorded"
                if item["number_basis"]:
                    number += f" ({item['number_basis']})"
                lines.append(
                    f"- [ ] English: **{item['english_name']}**{printed} · Number: {number} "
                    f"(`{item['id']}`) · {item['location']} · {reasons}."
                )
                lines.append("  - Verified print / variant, image, location, evidence and date: ______________________________")
            lines.append("")
    lines.extend((
        f"## Possible duplicate-printing pairs ({len(pairs)})",
        "",
        "These share recorded species, set, number and language, but can be distinct owned copies "
        "or bad catalogue matches. Check the physical cards and current placement before merging IDs or claiming a violation.",
        "",
    ))
    for pair in pairs:
        left, right = pair["ids"]
        lines.extend((
            f"- [ ] English: **{pair['english_name']}** · Number: {pair['number']} "
            f"· `{left}` / `{right}` · Compare both physical copies, printing and ownership.",
            "  - Observed copies / correction, evidence and date: ______________________________",
        ))
    return "\n".join(lines).rstrip() + "\n"


def pdf_source_is_current(root: Path) -> bool:
    markdown = root / OUTPUT
    pdf = root / PDF_OUTPUT
    receipt = root / PDF_SOURCE
    if not markdown.is_file() or not pdf.is_file() or not receipt.is_file():
        return False
    digest = hashlib.sha256(markdown.read_bytes()).hexdigest()
    return receipt.read_text(encoding="ascii") == digest + "\n" and pdf.read_bytes().startswith(b"%PDF-")


def build_pdf(root: Path) -> None:
    for command in ("pandoc", "xelatex"):
        if not shutil.which(command):
            raise RuntimeError(f"{command} is required to regenerate {PDF_OUTPUT}")
    markdown = (root / OUTPUT).read_text(encoding="utf-8")
    # XeLaTeX does not automatically fall back to CJK fonts. Scope each printed-script run
    # so the English labels and card numbers retain the main font and remain legible.
    with TemporaryDirectory(prefix="binder-checklist-") as scratch:
        source = Path(scratch) / "checklist.md"
        header = Path(scratch) / "fonts.tex"
        source.write_text(
            CJK_RUN.sub(lambda match: r"\begingroup\cjkfont " + match.group() + r"\endgroup{}", markdown),
            encoding="utf-8",
        )
        header.write_text("\\usepackage{fontspec}\n\\newfontfamily\\cjkfont{Droid Sans Fallback}\n", encoding="utf-8")
        result = subprocess.run(
            ["pandoc", str(source), "--from=markdown+task_lists+raw_tex", "--pdf-engine=xelatex",
             "-V", "mainfont=DejaVu Sans", "-V", "monofont=DejaVu Sans Mono",
             "-V", "papersize=a4", "-V", "geometry:margin=16mm", "-V", "fontsize=9pt",
             f"--include-in-header={header}", "-o", str(root / PDF_OUTPUT)],
            capture_output=True, text=True,
        )
        if result.returncode or "Missing character:" in result.stderr:
            raise RuntimeError(f"PDF rendering failed or omitted glyphs: {result.stderr[-2000:]}")
    digest = hashlib.sha256((root / OUTPUT).read_bytes()).hexdigest()
    (root / PDF_SOURCE).write_text(digest + "\n", encoding="ascii")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="reject a stale checklist")
    mode.add_argument("--write", action="store_true", help="regenerate the Markdown checklist")
    mode.add_argument("--pdf", action="store_true", help="build the printable PDF from current Markdown (requires pandoc and XeLaTeX)")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / OUTPUT
    expected = render_checklist(collect_review_items(root), collect_duplicate_candidates(root))
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            parser.exit(1, f"{OUTPUT} is stale; run python scripts/validation_checklist.py --write\n")
        if not pdf_source_is_current(root):
            parser.exit(1, f"{PDF_OUTPUT} is absent or stale; run python scripts/validation_checklist.py --pdf\n")
    elif args.pdf:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            parser.exit(1, f"{OUTPUT} is stale; run python scripts/validation_checklist.py --write first\n")
        build_pdf(root)
        print(f"wrote {PDF_OUTPUT}")
    else:
        path.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
