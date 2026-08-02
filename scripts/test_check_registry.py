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
render_worklist = check_registry.render_worklist

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


def test_worklist_includes_row_id_and_notes_for_uncertain_row():
    doc = render_worklist(parse_registry(table(
        row("mew-01", "Mew", conf="uncertain", set_="", num="",
            notes="footer illegible after crop attempt"),
    )))
    assert "mew-01" in doc
    assert "footer illegible after crop attempt" in doc


def test_worklist_excludes_confirmed_row():
    doc = render_worklist(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed", set_="Neo Discovery", num="13/75",
            notes="should not appear anywhere"),
    )))
    assert "umbreon-01" not in doc
    assert "should not appear anywhere" not in doc


def test_worklist_cluster_species_appear_before_singletons():
    doc = render_worklist(parse_registry(table(
        row("mew-01", "Mew", conf="uncertain", set_="", num=""),
        row("umbreon-01", "Umbreon", conf="uncertain", set_="", num=""),
        row("umbreon-02", "Umbreon", conf="uncertain", set_="", num=""),
    )))
    assert doc.index("umbreon-01") < doc.index("mew-01")


def test_worklist_header_totals_match_fixture():
    doc = render_worklist(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed", set_="A", num="1"),
        row("gengar-01", "Gengar", conf="photo", set_="B", num="2"),
        row("gengar-02", "Gengar", conf="uncertain", set_="", num="3"),
        row("mew-01", "Mew", conf="uncertain", set_="", num=""),
    )))
    assert "4 rows total" in doc
    assert "1 `photo` (25.0%)" in doc
    assert "2 `uncertain` (50.0%)" in doc
    assert "2 rows have both `set` and `number` read (50.0%)" in doc
    assert "1 have `number` only, 0 have `set` only, 1 have neither field" in doc
    assert "2 rows across 2 species: 0 clusters (0 rows) and 2 singletons" in doc


def test_worklist_does_not_derive_departed_cards_from_notes():
    # The registry records what a card IS, never where it sits. A notes marker
    # claiming a card has left must not be promoted into generated output --
    # that would make the registry a location index, which the design forbids.
    doc = render_worklist(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed", set_="A", num="1",
            notes="**NOT IN THE BINDER** — swapped out; check the holding box."),
    )))
    assert "NOT IN THE BINDER" not in doc


def test_worklist_points_at_the_ledger_for_movement():
    doc = render_worklist(parse_registry(table(
        row("umbreon-01", "Umbreon", conf="confirmed", set_="A", num="1"),
    )))
    assert "ledger.md" in doc
    assert "not derivable here" in doc.lower()


def test_worklist_has_handwritten_placeholder():
    doc = render_worklist(parse_registry(table(
        row("umbreon-01", "Umbreon"),
    )))
    assert "Gaps and known issues" in doc
    assert "Hand-written" in doc


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


def test_zero_counter_is_an_error():
    # Counters run from 01. A 00 counter matches ID_RE but breaks that invariant,
    # and the contiguity check alone does not catch it (range(1, 0+1) is empty).
    errors = validate(parse_registry(table(row("foo-00", "Foo"))))
    assert any("foo-00" in e for e in errors)


def test_zero_counter_is_an_error_alongside_valid_counters():
    errors = validate(parse_registry(table(row("foo-00", "Foo"), row("foo-01", "Foo"))))
    assert any("foo-00" in e for e in errors)


def test_valid_counters_starting_at_01_still_pass():
    assert validate(parse_registry(table(row("foo-01", "Foo"), row("foo-02", "Foo")))) == []


def test_confirmation_queue_groups_by_species_not_id_slug():
    # The never-rewrite rule freezes IDs but lets `species` be corrected, so an ID
    # slug is not a reliable species indicator. Clusters exist to surface possible
    # duplicate printings, which are defined by species -- so they must follow the
    # species column, not the slug.
    queue = confirmation_queue(parse_registry(table(
        row("marowak-01", "Cubone", num="", conf="uncertain"),
        row("cubone-01", "Cubone", num="", conf="uncertain"),
        row("marowak-02", "Marowak", num="", conf="uncertain"),
    )))
    groups = dict(queue)
    assert "cubone" in groups
    assert len(groups["cubone"]) == 2
    assert {r["id"] for r in groups["cubone"]} == {"marowak-01", "cubone-01"}
    assert "marowak" in groups
    assert {r["id"] for r in groups["marowak"]} == {"marowak-02"}


def test_counter_validation_still_uses_the_id_slug():
    # Counters are per-ID-sequence and must not follow a corrected species.
    # marowak-01/-02 remain one contiguous counter run even though -01 is a Cubone.
    assert validate(parse_registry(table(
        row("marowak-01", "Cubone"), row("marowak-02", "Marowak"),
    ))) == []


# --- by-page view (section 6) -------------------------------------------------

page_groups = check_registry.page_groups
PAGE_ORDER = check_registry.PAGE_ORDER
SWAP_INS = check_registry.SWAP_INS


def unc(id_, species, seen, notes="unreadable"):
    """An unresolved row -- uncertain confidence, so it reaches the queue."""
    return row(id_, species, conf="uncertain", set_="", num="", seen=seen,
               notes=notes)


def test_page_groups_orders_pages_by_binder_position():
    groups = page_groups(parse_registry(table(
        unc("zygarde-01", "Zygarde", "threshold_1.webp 2026-08-01"),
        unc("umbreon-01", "Umbreon", "calm_nature_1.webp 2026-08-01"),
        unc("celebi-01", "Celebi", "companions_1.webp 2026-08-01"),
    )))
    labels = [label for label, _ in groups]
    assert labels == [
        "V1 · Calm in Nature",
        "V2 · Companions p1",
        "V2 · Enduring Presence p2",
    ]


def test_page_groups_applies_the_volume_two_off_by_one_correction():
    # enduring_presence_1.webp actually photographs Quiet Familiarity p2.
    groups = page_groups(parse_registry(table(
        unc("ditto-01", "Ditto", "enduring_presence_1.webp 2026-08-01"),
    )))
    assert [label for label, _ in groups] == ["V2 · Quiet Familiarity p2"]


def test_page_groups_merges_a_swap_in_into_its_page():
    groups = page_groups(parse_registry(table(
        unc("ditto-01", "Ditto", "enduring_presence_1.webp 2026-08-01"),
        unc("cinccino-01", "Cinccino", "IMG_6860.HEIC 2026-08-01"),
    )))
    assert len(groups) == 1
    label, rows_ = groups[0]
    assert label == "V2 · Quiet Familiarity p2"
    assert sorted(r["id"] for r in rows_) == ["cinccino-01", "ditto-01"]


def test_img_6865_is_a_whole_page_not_a_swap_in():
    # It matches the IMG_*.HEIC shape but carries a full page of cards.
    groups = page_groups(parse_registry(table(
        unc("deoxys-01", "Deoxys", "IMG_6865.HEIC 2026-08-01"),
    )))
    assert [label for label, _ in groups] == ["V2 · Threshold"]


def test_page_with_no_unresolved_rows_is_omitted():
    groups = page_groups(parse_registry(table(
        row("umbreon-01", "Umbreon", seen="calm_nature_1.webp 2026-08-01"),
        unc("celebi-01", "Celebi", "at_rest_1.webp 2026-08-01"),
    )))
    assert [label for label, _ in groups] == ["V1 · At Rest"]


def test_unmapped_source_image_is_not_silently_dropped():
    groups = page_groups(parse_registry(table(
        unc("mew-01", "Mew", "some_new_shoot.webp 2026-09-01"),
    )))
    labels = [label for label, _ in groups]
    assert any("Unmapped" in label for label in labels)
    assert any("some_new_shoot.webp" in label for label in labels)


def test_unmapped_pages_sort_after_all_known_pages():
    groups = page_groups(parse_registry(table(
        unc("mew-01", "Mew", "some_new_shoot.webp 2026-09-01"),
        unc("zygarde-01", "Zygarde", "IMG_6865.HEIC 2026-08-01"),
    )))
    assert "Unmapped" in [label for label, _ in groups][-1]


def test_every_swap_in_target_is_a_real_page_label():
    assert set(SWAP_INS.values()) <= set(PAGE_ORDER.values())


def test_worklist_renders_the_by_page_section():
    doc = render_worklist(parse_registry(table(
        unc("ditto-01", "Ditto", "enduring_presence_1.webp 2026-08-01",
            notes="number illegible"),
    )))
    assert "## 6. Confirmation queue by page" in doc
    assert "### V2 · Quiet Familiarity p2" in doc
    assert "number illegible" in doc
    assert "ledger.md" in doc.split("## 6.")[1]


def test_by_page_section_follows_the_species_view():
    doc = render_worklist(parse_registry(table(
        unc("ditto-01", "Ditto", "enduring_presence_1.webp 2026-08-01"),
    )))
    assert doc.index("## 3.") < doc.index("## 6.")


# --- section 4 carry-forward --------------------------------------------------

def test_carries_section_four_forward_from_the_previous_document(tmp_path):
    prev = tmp_path / "registry-confirmation.md"
    prev.write_text(
        "# Registry confirmation worklist\n\n"
        "## 4. Gaps and known issues\n\n"
        "The set column is unreadable on vintage prints.\n\n"
        "## 5. Cards no longer in the binder\n\nx\n",
        encoding="utf-8",
    )
    doc = render_worklist(parse_registry(table(row("umbreon-01", "Umbreon"))),
                          previous=prev)
    assert "The set column is unreadable on vintage prints." in doc
    assert "Hand-written" not in doc.split("## 4.")[1].split("## 5.")[0]


def test_falls_back_to_placeholder_when_previous_document_is_missing(tmp_path):
    doc = render_worklist(parse_registry(table(row("umbreon-01", "Umbreon"))),
                          previous=tmp_path / "nope.md")
    assert "Gaps and known issues" in doc
    assert "Hand-written" in doc


def test_falls_back_to_placeholder_when_section_four_is_absent(tmp_path):
    prev = tmp_path / "registry-confirmation.md"
    prev.write_text("# Registry confirmation worklist\n\n## 5. Something\n\nx\n",
                    encoding="utf-8")
    doc = render_worklist(parse_registry(table(row("umbreon-01", "Umbreon"))),
                          previous=prev)
    assert "Hand-written" in doc


def test_carried_section_four_does_not_duplicate_the_heading(tmp_path):
    prev = tmp_path / "registry-confirmation.md"
    prev.write_text(
        "## 4. Gaps and known issues\n\nNarrative.\n\n## 5. Cards\n\nx\n",
        encoding="utf-8",
    )
    doc = render_worklist(parse_registry(table(row("umbreon-01", "Umbreon"))),
                          previous=prev)
    assert doc.count("## 4. Gaps and known issues") == 1
