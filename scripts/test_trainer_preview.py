"""Trainer Full Arts: public PDF-order digital binder, excluding Pokémon cards."""

import importlib.util
from pathlib import Path
import subprocess

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("digital_binder", ROOT / "scripts/digital_binder.py")
digital_binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digital_binder)

PDF_ORDER = [
    "tate-lizas-training-01", "zinnias-trust-01", "mistys-spirit-01",
    "mela-01", "worker-01", "peonia-01", "cynthias-ambition-01",
    "karens-conviction-01", "aroma-lady-01", "bea-01", "nemona-02",
    "jacinthe-02", "tate-liza-01",
    "lance-01", "arven-01", "honey-s-p-01", "candice-01",
    "rosas-encouragement-01", "iris-fighting-spirit-02", "nemona-01",
    "iris-fighting-spirit-01", "tulip-01", "jacinthe-01", "olivia-01",
    "hilda-01", "furisode-girl-01", "professors-research-02",
    "raifort-01", "erikas-invitation-01",
]


def test_trainer_cards_are_in_pdf_order_on_four_digital_pages():
    manifest = yaml.safe_load((ROOT / "data/binders/waifu.yaml").read_text())
    assert manifest["publication_status"] == "published"
    assert len(manifest["leaves"]) == 4
    assert [leaf["physical_leaf"] for leaf in manifest["leaves"]] == [1, 2, 3, 4]
    assert all("caption" not in leaf for leaf in manifest["leaves"])
    assert [[p["position"] for p in leaf["pockets"]] for leaf in manifest["leaves"]] == [
        list(range(1, 10)) for _ in range(4)
    ]
    pockets = [p for leaf in manifest["leaves"] for p in leaf["pockets"]]
    assert [p["card_id"] for p in pockets if not p.get("empty")] == PDF_ORDER
    assert len(set(PDF_ORDER)) == 29
    assert [sum(p.get("empty") is True for p in leaf["pockets"]) for leaf in manifest["leaves"]] == [0, 0, 0, 7]
    assert not {"larvitar-01", "pyroar-ex-01"} & set(PDF_ORDER)
    for pocket in pockets[:29]:
        placement = pocket["placement"]
        assert placement["status"] == "pending"
        assert placement["physical_state_unknown"] is True
        assert placement["evidence"]["source"].endswith("trainers.pdf")


def test_all_trainers_have_reviewed_local_images_and_japanese_language():
    images = yaml.safe_load((ROOT / "data/card-images.yaml").read_text())["cards"]
    registry = digital_binder.load_registry(ROOT / "docs/card-registry.md")
    for card_id in PDF_ORDER:
        assert registry[card_id]["language"] == "JP"
        record = images[card_id]
        assert record["reviewed"] is True
        assert record["classification"] in {"proxy", "photo-crop"}
        assert (ROOT / record["asset_path"]).is_file()
        if card_id != "olivia-01":
            assert record["provider"] == "doubleholo"
            assert record["source_url"].startswith("https://navythaxplgdibyahpqb.supabase.co/")
        else:
            assert record["provider"] == "evidence-crop"
            assert record["source_path"].startswith("docs/evidence/")


def test_public_manifest_validates_against_main():
    assert digital_binder.validate_project(ROOT, previous_ref="8cd8919") == []


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    scratch = tmp_path_factory.mktemp("trainer-public")
    override = scratch / "override.toml"
    override.write_text(f'resourceDir = "{scratch / "resources"}"\n')
    destination = scratch / "public"
    subprocess.run(
        ["hugo", "--config", f"hugo.toml,{override}", "--destination", str(destination), "--quiet"],
        cwd=ROOT, check=True,
    )
    return destination


def test_public_route_is_digital_and_old_photos_are_not_published(site):
    html = (site / "gallery/waifu/index.html").read_text()
    assert 'data-binder="waifu"' in html
    assert html.count('data-card-id="') == 29
    assert html.count('class="binder-pocket is-empty"') == 7
    assert 'class="pocket-state"' not in html
    assert 'class="pocket-states"' not in html
    assert "Cards 10–18 in the owner-supplied PDF order" not in html
    assert "images/binder/waifu/" not in html
    assert not (site / "images/binder/waifu").exists()
    assert not (site / "gallery/trainer-full-arts-preview/index.html").exists()
    assert digital_binder.validate_public_output(site, require_public_volumes=True) == []
