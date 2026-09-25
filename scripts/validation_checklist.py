#!/usr/bin/env python3
"""Build the owner's review checklist from published card and placement records."""

import argparse
from pathlib import Path

import digital_binder

BINDERS = (
    ("volume-1", "Volume I"),
    ("volume-2", "Volume II"),
    ("waifu", "Trainer Full Arts"),
    ("stamped-cards", "Stamped Cards"),
    ("emolga-masterset", "Emolga Masterset"),
)
OUTPUT = Path("docs/card-validation-checklist.md")
# A photo-confirmed owner card with provisional inclusion but no pocket in a leaf.
UNPLACED_OWNED = {"snivy-04": ("Stamped Cards", "Provisional page 8 · pocket unverified")}


def collect_review_items(root: Path) -> list[dict]:
    registry = digital_binder.load_registry(root / "docs/card-registry.md")
    images = digital_binder.load_yaml(root / "data/card-images.yaml")["cards"]
    items = []
    occupied_ids = set()
    for binder_id, title in BINDERS:
        binder = digital_binder.load_yaml(root / "data/binders" / f"{binder_id}.yaml")
        if binder["publication_status"] != "published":
            continue
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
                    "collection": title, "location": location,
                    "reasons": reasons,
                    "tier": "follow-up" if reasons == ["photo-based identity"] else "priority",
                })

    for card_id, (title, location) in UNPLACED_OWNED.items():
        if card_id in occupied_ids:
            continue
        card, image = registry[card_id], images[card_id]
        items.append({
            "id": card_id, "name": card["card_name"] or card["species"],
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
        items.append({
            "id": card["id"], "name": card["name"],
            "collection": "Holding binder", "location": location,
            "reasons": reasons,
            "tier": "follow-up" if reasons == ["photo-based identity"] else "priority",
        })
    return items


def collect_duplicate_candidates(root: Path) -> list[tuple[str, str]]:
    registry = digital_binder.load_registry(root / "docs/card-registry.md")
    pairs = digital_binder.load_registry_module().duplicate_printings(registry.values())
    return sorted((left["id"], right["id"]) for left, right in pairs)


def render_checklist(items: list[dict], pairs: list[tuple[str, str]]) -> str:
    lines = [
        "# Card validation checklist",
        "",
        "Owner review of **published, owned cards** whose image, printing, or placement still needs checking. "
        "Unchecked entries are questions, not evidence of a mistake. This checklist does not change the public collection or establish an in-hand confirmation.",
        "",
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
                lines.append(f"- [ ] **{item['name']}** (`{item['id']}`) · {item['location']} · {reasons}.")
                lines.append("  - Verified print / variant, image, location, evidence and date: ______________________________")
            lines.append("")
    lines.extend((
        f"## Possible duplicate-printing pairs ({len(pairs)})",
        "",
        "These share recorded species, set, number and language, but can be distinct owned copies "
        "or bad catalogue matches. Check the physical cards and current placement before merging IDs or claiming a violation.",
        "",
    ))
    for left, right in pairs:
        lines.extend((
            f"- [ ] `{left}` / `{right}` · Compare both physical copies, printing and ownership.",
            "  - Observed copies / correction, evidence and date: ______________________________",
        ))
    return "\n".join(lines).rstrip() + "\n"


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--check", action="store_true", help="reject a stale checklist")
    mode.add_argument("--write", action="store_true", help="regenerate the checklist")
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    path = root / OUTPUT
    expected = render_checklist(collect_review_items(root), collect_duplicate_candidates(root))
    if args.check:
        if not path.exists() or path.read_text(encoding="utf-8") != expected:
            parser.exit(1, f"{OUTPUT} is stale; run python scripts/validation_checklist.py --write\n")
    else:
        path.write_text(expected, encoding="utf-8")
        print(f"wrote {OUTPUT}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
