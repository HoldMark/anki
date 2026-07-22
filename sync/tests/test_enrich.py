"""Uses hand-seeded synthetic Cambridge/link data plus a fake Anki backend — no real data touched."""

from src.sync.enrich import enrich
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.service.note_definition_link import NoteDefinitionLinkService
from src.db.tables.note_definition_links import NoteDefinitionLinksTable
from src.db.service.cambridge.cambridge_word import CambridgeWordService
from src.db.tables.cambridge.cambridge_words import CambridgeWordsTable
from src.db.service.cambridge.cambridge_sense import CambridgeSenseService
from src.db.tables.cambridge.cambridge_senses import CambridgeSensesTable
from src.db.service.cambridge.cambridge_definition import CambridgeDefinitionService
from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable
from src.db.service.cambridge.cambridge_part_of_speech import CambridgePartOfSpeechService
from src.db.tables.cambridge.cambridge_parts_of_speech import CambridgePartsOfSpeechTable


def _insert_note(db, anki_note_id, deck="test::deck"):
    AnkiNotesTable(db).add(
        {
            "anki_note_id": anki_note_id,
            "system_note_uuid": f"uuid-{anki_note_id}",
            "system_hash": "hash",
            "source_deck": deck,
            "word": "thick",
            "trans": "/θɪk/",
            "trans_type": "(uk)",
            "part_of_speech": "adjective",
            "sense": None,
            "definition": None,
            "cefr": None,
            "example_1": None,
            "example_2": None,
            "example_3": None,
            "example_4": None,
            "example_5": None,
            "example_6": None,
            "example_7": None,
            "audio": None,
            "picture": None,
            "video": None,
            "hints": None,
            "sync_status": "ok",
            "sync_issue": None,
            "last_pulled_at": "01.01.2026 00:00:00:000",
        }
    )


def _confirmed_link_with_cefr(db, anki_note_id, cefr_value):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)
    links = NoteDefinitionLinksTable(db)

    word_id = CambridgeWordService("thick", words).add()
    pos_id = CambridgePartOfSpeechService(word_id, "adjective", pos).add()
    sense_id = CambridgeSenseService(pos_id, "sense", senses).add()
    def_id = CambridgeDefinitionService(sense_id, "definition", cefr_value, definitions).add()

    service = NoteDefinitionLinkService(anki_note_id, links)
    service.propose_candidate(def_id, "word_transcription")
    service.confirm_if_single_candidate()
    return def_id


def test_enrich_writes_cefr_when_empty(fake_anki, db):
    _insert_note(db, 111)
    _confirmed_link_with_cefr(db, 111, "B1")
    fake_anki.add_note(111, cefr="")

    counts = enrich("test::deck", skip_review=True)

    assert counts == {"updated": 1, "unchanged": 0, "skipped": 0, "error": 0}
    assert fake_anki.notes[111]["cefr"] == "B1"


def test_enrich_does_not_overwrite_existing_cefr_without_force(fake_anki, db):
    _insert_note(db, 111)
    _confirmed_link_with_cefr(db, 111, "B1")
    fake_anki.add_note(111, cefr="A2")

    counts = enrich("test::deck", skip_review=True)

    assert counts == {"updated": 0, "unchanged": 1, "skipped": 0, "error": 0}
    assert fake_anki.notes[111]["cefr"] == "A2"


def test_enrich_force_overwrites_existing_cefr(fake_anki, db):
    _insert_note(db, 111)
    _confirmed_link_with_cefr(db, 111, "B1")
    fake_anki.add_note(111, cefr="A2")

    counts = enrich("test::deck", force=True, skip_review=True)

    assert counts == {"updated": 1, "unchanged": 0, "skipped": 0, "error": 0}
    assert fake_anki.notes[111]["cefr"] == "B1"


def test_enrich_skips_note_without_confirmed_link(fake_anki, db):
    _insert_note(db, 111)
    fake_anki.add_note(111, cefr="")

    counts = enrich("test::deck", skip_review=True)

    assert counts == {"updated": 0, "unchanged": 0, "skipped": 1, "error": 0}
    assert fake_anki.notes[111]["cefr"] == ""


def test_enrich_dry_run_makes_no_writes(fake_anki, db):
    _insert_note(db, 111)
    _confirmed_link_with_cefr(db, 111, "B1")
    fake_anki.add_note(111, cefr="")

    counts = enrich("test::deck", dry_run=True, skip_review=True)

    assert counts == {"updated": 1, "unchanged": 0, "skipped": 0, "error": 0}
    assert fake_anki.notes[111]["cefr"] == ""


def test_enrich_no_cefr_value_available_is_unchanged(fake_anki, db):
    _insert_note(db, 111)
    _confirmed_link_with_cefr(db, 111, None)
    fake_anki.add_note(111, cefr="")

    counts = enrich("test::deck", skip_review=True)

    assert counts == {"updated": 0, "unchanged": 1, "skipped": 0, "error": 0}


def test_enrich_records_error_for_note_missing_from_notes_info(fake_anki, db):
    _insert_note(db, 111)
    _confirmed_link_with_cefr(db, 111, "B1")
    # deliberately not registered in fake_anki -> get_notes_fields returns {}

    counts = enrich("test::deck", skip_review=True)

    assert counts == {"updated": 0, "unchanged": 0, "skipped": 0, "error": 1}


def test_enrich_empty_deck_reports_zero(fake_anki, db):
    assert enrich("test::deck", skip_review=True) == {"updated": 0, "unchanged": 0, "skipped": 0, "error": 0}
