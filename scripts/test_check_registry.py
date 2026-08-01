"""Tests for the card registry validator."""
import importlib.util
from pathlib import Path

spec = importlib.util.spec_from_file_location(
    "check_registry", Path(__file__).parent / "check-registry.py"
)
check_registry = importlib.util.module_from_spec(spec)
spec.loader.exec_module(check_registry)

parse_registry = check_registry.parse_registry
validate = check_registry.validate
duplicate_printings = check_registry.duplicate_printings
confirmation_queue = check_registry.confirmation_queue

HEADER = (
    "| id | species | card_name | language | set | number | confidence | first_seen | notes |\n"
    "|---|---|---|---|---|---|---|---|---|\n"
)


def table(*rows):
    return "# Card registry\n\n## Registry\n\n" + HEADER + "".join(rows)


def row(id_, species, name="X", lang="EN", set_="Base", num="1/10",
        conf="photo", seen="img.webp 2026-08-01", notes=""):
    return f"| {id_} | {species} | {name} | {lang} | {set_} | {num} | {conf} | {seen} | {notes} |\n"


def test_parses_a_row_into_a_dict():
    rows = parse_registry(table(row("umbreon-01", "Umbreon")))
    assert len(rows) == 1
    assert rows[0]["id"] == "umbreon-01"
    assert rows[0]["species"] == "Umbreon"
    assert rows[0]["language"] == "EN"


def test_blank_cells_become_empty_strings():
    rows = parse_registry(table(row("umbreon-01", "Umbreon", set_="", num="")))
    assert rows[0]["set"] == ""
    assert rows[0]["number"] == ""


def test_valid_table_has_no_errors():
    assert validate(parse_registry(table(row("umbreon-01", "Umbreon")))) == []


def test_rejects_unpadded_counter():
    errors = validate(parse_registry(table(row("umbreon-1", "Umbreon"))))
    assert any("umbreon-1" in e for e in errors)


def test_rejects_uppercase_id():
    errors = validate(parse_registry(table(row("Umbreon-01", "Umbreon"))))
    assert any("Umbreon-01" in e for e in errors)


def test_rejects_duplicate_ids():
    errors = validate(parse_registry(
        table(row("umbreon-01", "Umbreon"), row("umbreon-01", "Umbreon"))
    ))
    assert any("duplicate id" in e.lower() for e in errors)


def test_rejects_unknown_language():
    errors = validate(parse_registry(table(row("umbreon-01", "Umbreon", lang="FR"))))
    assert any("FR" in e for e in errors)


def test_rejects_unknown_confidence():
    errors = validate(parse_registry(table(row("umbreon-01", "Umbreon", conf="maybe"))))
    assert any("maybe" in e for e in errors)


def test_requires_first_seen():
    errors = validate(parse_registry(table(row("umbreon-01", "Umbreon", seen=""))))
    assert any("first_seen" in e for e in errors)


def test_species_drift_is_a_warning_not_an_error():
    # The never-rewrite rule permits an ID whose slug no longer matches species.
    # houndour-01/02 included so the counter run stays contiguous from 01.
    errors = validate(parse_registry(table(
        row("houndour-01", "Houndour"),
        row("houndour-02", "Houndour"),
        row("houndour-03", "Houndoom"),
    )))
    assert errors == []


def test_finds_duplicate_printings():
    pairs = duplicate_printings(parse_registry(table(
        row("houndoom-01", "Houndoom", set_="Rising Rivals", num="50/111"),
        row("houndoom-02", "Houndoom", set_="Rising Rivals", num="50/111"),
    )))
    assert len(pairs) == 1


def test_different_numbers_are_not_duplicates():
    pairs = duplicate_printings(parse_registry(table(
        row("umbreon-01", "Umbreon", set_="Neo Discovery", num="32/75"),
        row("umbreon-02", "Umbreon", set_="Neo Discovery", num="13/75"),
    )))
    assert pairs == []


def test_different_languages_are_not_duplicates():
    pairs = duplicate_printings(parse_registry(table(
        row("umbreon-01", "Umbreon", lang="EN", set_="S", num="1/10"),
        row("umbreon-02", "Umbreon", lang="JP", set_="S", num="1/10"),
    )))
    assert pairs == []


def test_unread_numbers_never_report_as_duplicates():
    # Cannot confirm a violation without the number. Must not guess.
    pairs = duplicate_printings(parse_registry(table(
        row("umbreon-01", "Umbreon", set_="", num=""),
        row("umbreon-02", "Umbreon", set_="", num=""),
    )))
    assert pairs == []


def test_confirmation_queue_leads_with_species_clusters():
    queue = confirmation_queue(parse_registry(table(
        row("cinccino-01", "Cinccino", num="", conf="uncertain"),
        row("umbreon-01", "Umbreon", num="", conf="uncertain"),
        row("umbreon-02", "Umbreon", num="", conf="uncertain"),
    )))
    assert queue[0][0] == "umbreon"
    assert len(queue[0][1]) == 2


def test_confidence_confirmed_rows_are_not_queued():
    queue = confirmation_queue(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed"),
    )))
    assert queue == []


def test_confidence_confirmed_rows_are_not_queued_even_if_blank():
    # A confirmed row is never queued, populated or blank.
    queue = confirmation_queue(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed", set_="", num=""),
    )))
    assert queue == []


def test_uncertain_row_with_set_and_number_populated_is_queued():
    # This is the bug: uncertain means inferred/obscured, so a fully
    # populated uncertain row still needs a physical check.
    queue = confirmation_queue(parse_registry(table(
        row("lucario-01", "Lucario", conf="uncertain", set_="s12a", num="226/172"),
    )))
    assert len(queue) == 1
    assert queue[0][0] == "lucario"


def test_photo_row_with_set_and_number_populated_is_not_queued():
    queue = confirmation_queue(parse_registry(table(
        row("lugia-02", "Lugia", conf="photo", set_="s12", num="079/098"),
    )))
    assert queue == []


def test_photo_row_with_blank_number_is_queued():
    queue = confirmation_queue(parse_registry(table(
        row("lugia-03", "Lugia", conf="photo", set_="", num="28/64"),
    )))
    assert len(queue) == 1
    assert queue[0][0] == "lugia"


def test_photo_row_with_blank_set_is_an_error():
    errors = validate(parse_registry(table(
        row("reshiram-01", "Reshiram", conf="photo", set_="", num="109/100"),
    )))
    assert any("reshiram-01" in e and "set" in e for e in errors)


def test_photo_row_with_blank_number_is_an_error():
    errors = validate(parse_registry(table(
        row("lugia-03", "Lugia", conf="photo", set_="Base", num=""),
    )))
    assert any("lugia-03" in e and "number" in e for e in errors)


def test_photo_row_with_set_and_number_has_no_error():
    errors = validate(parse_registry(table(
        # lugia-01 included so the counter run stays contiguous from 01.
        row("lugia-01", "Lugia", conf="photo", set_="s11", num="078/098"),
        row("lugia-02", "Lugia", conf="photo", set_="s12", num="079/098"),
    )))
    assert errors == []


def test_uncertain_row_with_blanks_has_no_confidence_error():
    errors = validate(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="uncertain", set_="", num=""),
    )))
    assert errors == []


def test_confirmed_row_with_blanks_has_no_confidence_error():
    errors = validate(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed", set_="", num=""),
    )))
    assert errors == []


def test_contiguous_counters_starting_at_01_have_no_error():
    errors = validate(parse_registry(table(
        row("gengar-01", "Gengar"),
        row("gengar-02", "Gengar"),
        row("gengar-03", "Gengar"),
    )))
    assert errors == []


def test_gap_in_counters_is_an_error_naming_the_missing_number():
    errors = validate(parse_registry(table(
        row("gengar-01", "Gengar"),
        row("gengar-02", "Gengar"),
        row("gengar-04", "Gengar"),
    )))
    assert any("gengar" in e and "03" in e for e in errors)


def test_counters_not_starting_at_01_is_an_error():
    errors = validate(parse_registry(table(
        row("gengar-02", "Gengar"),
        row("gengar-03", "Gengar"),
    )))
    assert any("gengar" in e and "01" in e for e in errors)


def test_compound_slug_does_not_count_toward_prefix_species():
    # gengar-mimikyu-01 must never be treated as a fourth Gengar counter --
    # species_slug() splits on the last hyphen only, so this must group
    # separately from gengar-01..03 and neither sequence should error.
    errors = validate(parse_registry(table(
        row("gengar-01", "Gengar"),
        row("gengar-02", "Gengar"),
        row("gengar-03", "Gengar"),
        row("gengar-mimikyu-01", "Gengar & Mimikyu"),
    )))
    assert errors == []
