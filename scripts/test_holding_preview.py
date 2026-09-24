"""The Holding preview must remain draft-only and truthful in rendered HTML."""

from html.parser import HTMLParser
from pathlib import Path
import re
import subprocess

import pytest

ROOT = Path(__file__).resolve().parents[1]


class PreviewElements(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.buttons = []
        self.links = []
        self.sections = []
        self.trade_cards = []

    def handle_starttag(self, tag, attributes):
        attrs = dict(attributes)
        if tag == "img":
            self.images.append(attrs)
        if tag == "button" and "data-card-id" in attrs:
            self.buttons.append(attrs)
        if tag == "a":
            self.links.append(attrs)
        if tag == "section":
            self.sections.append(attrs)
        if "data-holding-trade-card" in attrs:
            self.trade_cards.append(attrs)


@pytest.fixture(scope="module")
def builds(tmp_path_factory):
    scratch = tmp_path_factory.mktemp("holding-preview")
    config = scratch / "hugo.toml"
    config.write_text(f'resourceDir = "{scratch / "resources"}"\n')
    results = {}
    for mode, options in (("draft", ["--buildDrafts"]), ("production", [])):
        destination = scratch / mode
        subprocess.run(
            ["hugo", "--config", f"hugo.toml,{config}", *options,
             "--destination", str(destination), "--quiet"],
            cwd=ROOT, check=True,
        )
        results[mode] = destination
    return results


def test_draft_displays_every_photographed_pocket_and_five_top_loaders(builds):
    page = builds["draft"] / "gallery" / "holding-preview" / "index.html"
    html = page.read_text()
    parsed = PreviewElements()
    parsed.feed(html)
    occupied = [button for button in parsed.buttons if "data-pocket-position" in button]
    assert len(occupied) == 100
    assert len({button["data-card-id"] for button in occupied}) == 100
    assert len(parsed.trade_cards) == 5
    assert len({card["data-holding-trade-card"] for card in parsed.trade_cards}) == 5
    assert len({section["data-binder-leaf"] for section in parsed.sections
                if "data-binder-leaf" in section}) == 14
    assert sum('class="binder-pocket is-empty"' in part for part in html.splitlines()) == 26


def test_only_five_top_loaders_are_marked_actively_available(builds):
    html = (builds["draft"] / "gallery" / "holding-preview" / "index.html").read_text()
    parsed = PreviewElements()
    parsed.feed(html)
    assert all(button.get("data-available") != "true" for button in parsed.buttons)
    assert all(card.get("data-available") == "true" for card in parsed.trade_cards)
    assert html.count("<span>Trade · actively available</span>") == 5
    assert "Still owned" in html
    assert "for sale" not in html.lower()
    assert "price" not in html.lower()


def test_page_navigation_and_images_are_local(builds):
    html = (builds["draft"] / "gallery" / "holding-preview" / "index.html").read_text()
    parsed = PreviewElements()
    parsed.feed(html)
    assert {f"#leaf-{n}" for n in range(7133, 7147)} <= {
        link.get("href") for link in parsed.links
    }
    assert "#trade-cards" in {link.get("href") for link in parsed.links}
    assert len([img for img in parsed.images if "holding/" in img.get("src", "")]) == 105
    assert all(not re.match(r"https?://", img.get("src", "")) for img in parsed.images)
    assert html.count('data-classification="photo-crop"') == 105
    assert 'data-binder="holding-preview"' in html
    assert 'data-card-inspector' in html
    assert 'data-card-inspector-field="sort-status"' in html
    assert 'data-card-inspector-field="identity-confidence"' in html
    assert 'data-card-name="Alolan Meowth — English 139/128"' in html
    assert re.search(r'data-card-name="Alolan Meowth — English 139/128"[^>]*data-card-language="EN"[^>]*data-card-number="139/128"', html)


def test_production_does_not_publish_or_link_draft(builds):
    assert not (builds["production"] / "gallery" / "holding-preview" / "index.html").exists()
    for route in ("index.html", "gallery/index.html"):
        html = (builds["production"] / route).read_text()
        assert "/gallery/holding-preview/" not in html
