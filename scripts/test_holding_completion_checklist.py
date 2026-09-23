import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/2026-09-22-holding-binder-inventory.md"
CHECKLIST = ROOT / "docs/2026-09-23-holding-sort-completion-checklist.tex"
REGISTRY_CONFIRMATION = ROOT / "docs/registry-confirmation.md"


def inventory_observations() -> set[str]:
    text = INVENTORY.read_text(encoding="utf-8")
    return set(re.findall(r"^\| (HB-P\d{2}-\d{2}) \|", text, re.MULTILINE))


def checklist_observations() -> list[str]:
    text = CHECKLIST.read_text(encoding="utf-8")
    return re.findall(r"\\(?:settledrow|decisionrow)\{[^}]*\}\{(HB-P\d{2}-\d{2})\}", text)


def test_checklist_covers_every_current_card_exactly_once():
    observations = checklist_observations()

    assert len(observations) == 100
    assert len(set(observations)) == 100
    assert set(observations) == inventory_observations()


def test_checklist_preserves_owner_safeguards():
    text = CHECKLIST.read_text(encoding="utf-8")

    assert "No card is currently authorized for Trade" in text
    assert "No additional Release is authorized" in text
    assert "Yveltal --- Steam Siege 65/114 was already removed" in text
    assert "interim staging" in text


def test_checklist_has_unfinished_decisions_and_closeout():
    text = CHECKLIST.read_text(encoding="utf-8")

    assert text.count(r"\decisionrow") > 0
    assert "Confirm marked destination" in text
    assert "a photographed interim position alone is not a final classification" in text
    assert r"\textbf{Final:}" in text
    assert "Final Review count" in text
    assert "Final Keeper count" in text
    assert "Grand total reconciled" in text
    assert "Section photographs complete" in text


def test_kirlia_latest_state_uses_section_name():
    text = REGISTRY_CONFIRMATION.read_text(encoding="utf-8")

    row = next(
        line
        for line in text.splitlines()
        if line.startswith("| kirlia-01 |") and "| — | — |" in line
    )
    assert "| Beautiful Misfits |" in row
    assert "Keeper · Beautiful Misfits" not in row
