"""Uses hand-seeded synthetic data — no real Cambridge data exists yet."""

from src.sync.review import review
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


def _insert_note(db, anki_note_id, word="thick", sync_status="ok", sync_issue=None):
    AnkiNotesTable(db).add(
        {
            "anki_note_id": anki_note_id,
            "system_note_uuid": f"uuid-{anki_note_id}",
            "system_hash": "hash",
            "source_deck": "test::deck",
            "word": word,
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
            "sync_status": sync_status,
            "sync_issue": sync_issue,
            "last_pulled_at": "01.01.2026 00:00:00:000",
        }
    )


def _make_definitions(db, count):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)

    word_id = CambridgeWordService("thick", words).add()
    pos_id = CambridgePartOfSpeechService(word_id, "adjective", pos).add()

    def_ids = []
    for i in range(count):
        sense_id = CambridgeSenseService(pos_id, f"sense {i}", senses).add()
        def_ids.append(CambridgeDefinitionService(sense_id, f"definition {i}", None, definitions).add())
    return def_ids


def test_review_reports_zero_candidate_notes(db):
    _insert_note(db, 111)

    report = review()

    assert len(report["zero_candidates"]) == 1
    assert report["zero_candidates"][0]["anki_note_id"] == 111


def test_review_reports_multi_candidate_notes_and_excludes_them_from_zero_candidates(db):
    _insert_note(db, 111)
    def_ids = _make_definitions(db, 2)
    links = NoteDefinitionLinksTable(db)
    service = NoteDefinitionLinkService(111, links)
    for definition_id in def_ids:
        service.propose_candidate(definition_id, "word_transcription")

    report = review()

    assert report["multi_candidates"] == [{"anki_note_id": 111, "candidate_count": 2}]
    assert report["zero_candidates"] == []


def test_review_reports_pull_errors(db):
    _insert_note(db, 111, sync_status="error", sync_issue="AnkiConnect returned no fields for this note")

    report = review()

    assert len(report["pull_errors"]) == 1
    assert report["pull_errors"][0]["sync_issue"] == "AnkiConnect returned no fields for this note"


def test_review_confirmed_note_is_not_zero_candidates_and_not_multi_candidates(db):
    _insert_note(db, 111)
    def_ids = _make_definitions(db, 1)
    links = NoteDefinitionLinksTable(db)
    service = NoteDefinitionLinkService(111, links)
    service.propose_candidate(def_ids[0], "word_transcription")
    service.confirm_if_single_candidate()

    report = review()

    assert report["zero_candidates"] == []
    assert report["multi_candidates"] == []


def test_review_empty_db_reports_all_empty(db):
    assert review() == {"zero_candidates": [], "multi_candidates": [], "pull_errors": []}
