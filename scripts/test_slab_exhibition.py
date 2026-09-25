"""Rendered contracts for the slab-only exhibition and its ownership boundary."""

from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys

from PIL import Image

import pytest

ROOT = Path(__file__).resolve().parents[1]
SLAB_ROUTES = {
    "definitive-pokemon": (3, 0),
    "touchstones": (7, 0),
    "personal-significance": (15, 0),
    "chinese-exclusives": (6, 0),
    "masaki": (2, 3),
}


class Exhibition(HTMLParser):
    def __init__(self):
        super().__init__()
        self.images = []
        self.dialogs = []
        self.scripts = []
        self.groups = []
        self.current_group = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "div" and "gallery-grid" in attrs.get("class", "").split():
            self.current_group = []
            self.groups.append(self.current_group)
        if tag == "img" and "/images/slabs/" in attrs.get("src", ""):
            self.images.append(attrs)
            self.current_group.append(attrs)
        if tag == "dialog":
            self.dialogs.append(attrs)
        if tag == "script" and attrs.get("src"):
            self.scripts.append(attrs["src"])

    def handle_endtag(self, tag):
        if tag == "div" and self.current_group is not None:
            # Group boundaries are also checked via the expected image counts.
            self.current_group = None


@pytest.fixture(scope="module")
def site(tmp_path_factory):
    scratch = tmp_path_factory.mktemp("slab-exhibition")
    override = scratch / "override.toml"
    override.write_text(f'resourceDir = "{scratch / "resources"}"\n')
    output = scratch / "public"
    subprocess.run(
        ["hugo", "--config", f"hugo.toml,{override}", "--destination", str(output), "--quiet"],
        cwd=ROOT, check=True,
    )
    return output


@pytest.mark.parametrize("route,counts", SLAB_ROUTES.items())
def test_slab_routes_keep_local_objects_and_have_an_independent_inspector(site, route, counts):
    html = (site / "gallery" / route / "index.html").read_text()
    page = Exhibition()
    page.feed(html)
    owned, wanted = counts
    assert len(page.images) == owned + wanted
    assert all(image["src"].startswith("../../images/slabs/") for image in page.images)
    assert all(image.get("alt") and image.get("loading") == "lazy" for image in page.images)
    assert all(int(image.get("width", 0)) > 0 and int(image.get("height", 0)) > 0 for image in page.images)
    for photo in page.images[:owned]:
        filename = Path(photo["src"]).stem
        preview = ROOT / "static/images/slab-previews" / f"{filename}.webp"
        assert preview.exists(), preview
        with Image.open(preview) as asset:
            assert asset.width == 720
        assert f"../../images/slab-previews/{filename}.webp 720w" in photo.get("srcset", "")
        if int(photo["width"]) >= 1080:
            larger = ROOT / "static/images/slab-previews" / f"{filename}-1080.webp"
            assert larger.exists(), larger
            with Image.open(larger) as asset:
                assert asset.width == 1080
            assert f"../../images/slab-previews/{filename}-1080.webp 1080w" in photo["srcset"]
        assert photo.get("sizes")
    for scan in page.images[owned:]:
        assert "srcset" not in scan
    assert 'class="gallery-page gallery-page--slab"' in html
    assert len([dialog for dialog in page.dialogs if dialog.get("id") == "slab-inspector"]) == 1
    assert len([dialog for dialog in page.dialogs if dialog.get("id") == "lightbox"]) == 1
    assert any("/js/slab-inspector" in script for script in page.scripts)
    assert 'data-slab-inspector-error hidden role="status"' in html
    assert "data-slab-inspector-zoom" in html
    assert "data-slab-inspector-previous" in html
    assert "data-slab-inspector-next" in html
    assert "Still Hunting" in html if wanted else "Still Hunting" not in html
    if wanted:
        assert "data-slab-wanted" in html
        assert [len(group) for group in page.groups] == [owned, wanted]


def test_preview_check_rejects_a_stale_wall_image(tmp_path):
    script = tmp_path / "scripts/make-slab-previews.py"
    script.parent.mkdir()
    shutil.copy2(ROOT / "scripts/make-slab-previews.py", script)
    originals = tmp_path / "static/images/slabs"
    originals.mkdir(parents=True)
    Image.new("RGB", (1200, 2000), "red").save(originals / "sample.jpg")
    subprocess.run([sys.executable, str(script)], check=True)
    preview = tmp_path / "static/images/slab-previews/sample.webp"
    preview.write_bytes(b"a stale derivative")
    result = subprocess.run([sys.executable, str(script), "--check"], capture_output=True, text=True)
    assert result.returncode != 0
    assert "sample.webp" in result.stdout + result.stderr


def test_side_gallery_keeps_its_existing_viewer_without_slab_script(site):
    html = (site / "gallery/waifu/index.html").read_text()
    assert '<dialog id="lightbox"' in html
    assert '<article class="gallery-page--slab"' not in html
    assert "/js/slab-inspector" not in html
