import re
from collections import Counter
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
INVENTORY = ROOT / "docs/2026-09-22-holding-binder-inventory.md"
CHECKLIST = ROOT / "docs/2026-09-23-holding-sort-completion-checklist.tex"
REGISTRY_CONFIRMATION = ROOT / "docs/registry-confirmation.md"


def inventory_observations() -> set[str]:
    text = INVENTORY.read_text(encoding="utf-8")
    return set(re.findall(r"^\| (HB-P\d{2}-\d{2}) \|", text, re.MULTILINE))


def checklist_rows() -> list[tuple[str, str, str, str, str]]:
    text = CHECKLIST.read_text(encoding="utf-8")
    return re.findall(
        r"^\\cardrow\{(HB-P\d{2}-\d{2})\}\{([^}]*)\}\{([^}]*)\}"
        r"\{([^}]*)\}\{([^}]*)\}",
        text,
        re.MULTILINE,
    )


def test_checklist_covers_every_current_card_exactly_once():
    text = CHECKLIST.read_text(encoding="utf-8")
    rows = checklist_rows()
    observations = [row[0] for row in rows]

    assert len(re.findall(r"^\\cardrow", text, re.MULTILINE)) == 100
    assert len(observations) == 100
    assert len(set(observations)) == 100
    assert set(observations) == inventory_observations()


def test_every_card_has_clear_recommendation_and_reason():
    rows = checklist_rows()

    for _observation, _type, _card, recommendation, reason in rows:
        assert recommendation.strip()
        assert recommendation not in {"Classify", "Choose destination"}
        assert len(reason.strip()) >= 12

    text = CHECKLIST.read_text(encoding="utf-8")
    assert not re.search(r"^\\(?:recommendrow|settledrow|decisionrow)", text, re.MULTILINE)
    assert "Accept recommendation" not in text
    assert "Strongest alternative" not in text


def test_recommended_counts_are_precomputed():
    rows = checklist_rows()
    top_level = Counter(recommendation.split(" · ", 1)[0] for *_, recommendation, _reason in rows)

    assert top_level == Counter({"Keeper": 63, "Review": 32, "Release": 5})
    review_groups = Counter(
        recommendation.split(" · ")[1]
        for *_prefix, recommendation, _reason in rows
        if recommendation.startswith("Review · ")
    )
    assert review_groups == Counter(
        {"EDGE Watches": 6, "Existing-theme EDGE": 2, "REDUNDANT": 23, "FUTURE SELF": 1}
    )
    keeper_subsections = Counter(
        recommendation.split(" · ", 1)[1]
        for *_prefix, recommendation, _reason in rows
        if recommendation.startswith("Keeper · ")
    )
    assert keeper_subsections == Counter(
        {"Personal": 3, "Beautiful Misfits": 12, "Heritage": 32, "Species Studies": 16}
    )

    text = CHECKLIST.read_text(encoding="utf-8")
    assert "Recommended Review count: 32" in text
    assert "Recommended Keeper count: 63" in text
    assert "Recommended Trade count: 0" in text
    assert "Recommended Release count: 5" in text
    assert "Recommended total: 100" in text


def test_checklist_is_walked_by_physical_page_without_visible_locator_instructions():
    text = CHECKLIST.read_text(encoding="utf-8")
    page_headers = re.findall(r"^\\binderpage\{(\d+)\}\{(\d+)\}", text, re.MULTILINE)

    assert page_headers == [
        ("1", "7"), ("2", "9"), ("3", "8"), ("4", "3"), ("5", "7"),
        ("6", "9"), ("7", "9"), ("8", "5"), ("9", "9"), ("10", "8"),
        ("11", "9"), ("12", "9"), ("13", "8"),
    ]
    assert "left-to-right, then top-to-bottom" in text
    assert "page locator" not in text
    assert "HB-PNN" not in text

    current_page = None
    observed_counts = Counter()
    for match in re.finditer(
        r"^\\binderpage\{(\d+)\}\{(\d+)\}|^\\cardrow\{HB-P(\d{2})-(\d{2})\}",
        text,
        re.MULTILINE,
    ):
        if match.group(1):
            current_page = int(match.group(1))
        else:
            row_page = int(match.group(3))
            assert row_page == current_page
            observed_counts[row_page] += 1

    assert observed_counts == Counter({int(page): int(count) for page, count in page_headers})


def test_every_pikachu_row_names_pikachu():
    rows = {observation: card for observation, _type, card, _recommendation, _reason in checklist_rows()}
    pikachu_ids = {
        *(f"HB-P12-{index:02d}" for index in range(4, 10)),
        *(f"HB-P13-{index:02d}" for index in range(1, 9)),
    }

    assert all("Pikachu" in rows[observation] for observation in pikachu_ids)


def test_checklist_preserves_owner_safeguards():
    text = CHECKLIST.read_text(encoding="utf-8")
    release_ids = {
        row[0]
        for row in checklist_rows()
        if row[3] == "Release"
    }
    authorized_rows = set(
        re.findall(r"^\\releaseauth\{(HB-P\d{2}-\d{2})\}", text, re.MULTILINE)
    )

    assert "No card is currently authorized for Trade" in text
    assert "No additional Release is authorized" in text
    assert "Done means moved to Release-pending, not removed from the collection" in text
    assert "For every Trade authorization, record an override from the recommended destination to Trade" in text
    assert "For every recommended Release not authorized, record an override to Review or Keeper" in text
    assert "Yveltal --- Steam Siege 65/114 was already removed" in text
    assert "interim staging" in text
    assert len(release_ids) == 5
    assert release_ids == authorized_rows
    assert len(re.findall(r"^\\tradeauth$", text, re.MULTILINE)) == 6
    assert "Signed authorization continuation attached" in text
    assert "Trade/Release authorization approved by" in text
    assert "Emolga EX must match the master-set copy's card number and finish in hand" in text


def test_checklist_has_capacity_adjustment_and_closeout_sections():
    text = CHECKLIST.read_text(encoding="utf-8")

    assert "Seven nine-pocket Review pages" in text
    assert "Sixteen four-pocket Keeper pages" in text
    assert "prepare one additional four-pocket page for that affected section" in text
    assert "Override adjustment log" in text
    assert "Adjusted Review count" in text
    assert "Adjusted Keeper count" in text
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
