"""The design context describes real site tokens rather than a parallel invented palette."""

from pathlib import Path
import json
import re

import yaml

ROOT = Path(__file__).resolve().parents[1]


def test_design_frontmatter_and_sidecar_match_shipped_colors():
    document = (ROOT / "DESIGN.md").read_text(encoding="utf-8")
    tokens = yaml.safe_load(document.split("---", 2)[1])
    sidecar = json.loads((ROOT / "DESIGN.json").read_text(encoding="utf-8"))
    css = (ROOT / "layouts/partials/head.html").read_text() + (ROOT / "assets/css/site-foundation.css").read_text()
    declared = dict(re.findall(r"--([\w-]+):\s*(oklch\([^)]+\))\s*;", css))

    assert tokens["name"] == "Pokémon Art Collection"
    assert set(tokens["colors"]) == set(sidecar["extensions"]["colorMeta"])
    for name, value in tokens["colors"].items():
        assert declared[name] == value
        assert sidecar["extensions"]["colorMeta"][name]["canonical"] == value
        assert len(sidecar["extensions"]["colorMeta"][name]["tonalRamp"]) == 8
    assert list(re.findall(r"^## \d\. (.+)$", document, flags=re.M)) == [
        "Overview", "Colors", "Typography", "Elevation", "Components", "Do's and Don'ts",
    ]
    assert 'A quiet exhibition under lamplight' in document


def test_repository_has_one_canonical_agent_guide_and_current_product_context():
    assert (ROOT / "AGENTS.md").is_file()
    assert "AGENTS.md" in (ROOT / "CLAUDE.md").read_text()
    product = (ROOT / "PRODUCT.md").read_text(encoding="utf-8")
    assert "\nbrand\n" in product
    assert "five still-owned Holding cards" in product
    assert "Trainer Full Arts is a four-page digital sequence" in product
    assert "remaining side-binder galleries are photographic" not in product
