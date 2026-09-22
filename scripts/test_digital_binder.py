import importlib.util
import json
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "digital_binder", Path(__file__).parent / "digital_binder.py"
)
digital_binder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(digital_binder)


def test_registry_projection_is_sorted_and_stable(tmp_path):
    registry = tmp_path / "registry.md"
    registry.write_text(
        "# Card registry\n\n## Registry\n\n"
        "| id | species | card_name | language | set | number | confidence | first_seen | notes |\n"
        "|---|---|---|---|---|---|---|---|---|\n"
        "| zubat-01 | Zubat | Zubat | EN | Fossil | 57/62 | photo | page.webp 2026-08-01 | |\n"
        "| abra-01 | Abra | Abra | EN | Base Set | 43/102 | confirmed | page.webp 2026-08-01 | |\n",
        encoding="utf-8",
    )
    rows = digital_binder.load_registry(registry)
    rendered = digital_binder.render_registry_json(rows)
    assert list(json.loads(rendered)) == ["abra-01", "zubat-01"]
    assert rendered.endswith("\n")


def test_check_generated_reports_drift(tmp_path):
    generated = tmp_path / "card-registry.json"
    generated.write_text("{}\n", encoding="utf-8")
    assert digital_binder.generated_is_current(
        generated, '{"abra-01": {}}\n'
    ) is False
