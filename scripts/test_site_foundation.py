"""Rendered-contract checks for the exhibition entry points."""

from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
from urllib.parse import urljoin, urlparse

import pytest
import yaml

ROOT = Path(__file__).resolve().parents[1]


class Links(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hrefs = []
        self.link_text = []
        self._link = None

    def handle_starttag(self, tag, attrs):
        if tag == "a":
            self._link = dict(attrs).get("href")
            self.hrefs.append(self._link)

    def handle_data(self, data):
        if self._link is not None:
            self.link_text.append(data.strip())

    def handle_endtag(self, tag):
        if tag == "a":
            self._link = None


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    output = tmp_path_factory.mktemp("stage2-site")
    subprocess.run(["hugo", "--destination", str(output), "--quiet"], cwd=ROOT, check=True)
    return output


def test_home_shelf_links_existing_collections_but_not_unpublished_binders(site):
    html = (site / "index.html").read_text()
    links = Links()
    links.feed(html)
    for route in ("volume-1", "volume-2", "stamped-cards", "waifu", "emolga-masterset", "masaki", "chinese-exclusives", "definitive-pokemon", "personal-significance", "touchstones"):
        assert any(urlparse(urljoin("https://collection.dpao.la/", href)).path == f"/gallery/{route}/" for href in links.hrefs if href), route
    assert "Holding binder" in html and "Trade binder" in html
    assert not any("Holding binder" in text or "Trade binder" in text for text in links.link_text)
    assert any("/guides/shopping/" in href for href in links.hrefs if href)
    assert any("/philosophy/" in href for href in links.hrefs if href)


def test_gallery_directory_shares_published_routes_and_marks_future_binders(site):
    html = (site / "gallery" / "index.html").read_text()
    links = Links()
    links.feed(html)
    for route in ("volume-1", "volume-2", "stamped-cards", "waifu", "emolga-masterset", "masaki", "chinese-exclusives", "definitive-pokemon", "personal-significance", "touchstones"):
        assert any(urlparse(urljoin("https://collection.dpao.la/gallery/", href)).path == f"/gallery/{route}/" for href in links.hrefs if href), route
    assert "Holding binder" in html and "Trade binder" in html
    assert not any("Holding binder" in text or "Trade binder" in text for text in links.link_text)
    assert "Each spread is photographed" not in html


def test_home_refuses_to_show_a_card_from_an_unpublished_volume(tmp_path):
    data_dir = tmp_path / "data"
    shutil.copytree(ROOT / "data", data_dir)
    manifest_path = data_dir / "binders" / "volume-1.yaml"
    manifest = yaml.safe_load(manifest_path.read_text())
    manifest["publication_status"] = "draft"
    manifest_path.write_text(yaml.safe_dump(manifest, allow_unicode=True))
    override = tmp_path / "override.toml"
    override.write_text(f'dataDir = "{data_dir}"\nresourceDir = "{tmp_path / "resources"}"\n')
    result = subprocess.run(
        ["hugo", "--config", f"hugo.toml,{override}", "--destination", str(tmp_path / "public")],
        cwd=ROOT, text=True, capture_output=True,
    )
    assert result.returncode != 0
    assert "published volume leaf" in result.stderr


def test_photo_gallery_viewer_is_a_native_modal(site):
    html = (site / "gallery" / "waifu" / "index.html").read_text()
    assert '<dialog id="lightbox"' in html


def test_volume_inspector_names_are_english_first_with_printed_script(site):
    html = (site / "gallery" / "volume-1" / "index.html").read_text()
    assert 'data-card-name="Audino · タブンネ"' in html
    assert 'data-card-english-name="Audino" data-card-printed-name="タブンネ"' in html
    assert 'data-card-english-name="Cubone" data-card-printed-name="卡拉卡拉"' in html


def test_home_framed_cards_open_inspector_without_becoming_collection_links(site):
    html = (site / "index.html").read_text()
    assert 'data-card-inspector' in html
    assert html.count('class="exhibit-frame" type="button" disabled') >= 3
    assert 'data-image-provenance=' in html
    assert 'data-placement-status=' in html
