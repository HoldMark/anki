"""
match's DB has no real Cambridge data yet (lexicon-scraper hasn't populated it) — every case
here is exercised against hand-seeded synthetic Cambridge rows, not real data. See
docs/test-coverage.md.
"""

from src.sync.match import match
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.tables.note_definition_links import NoteDefinitionLinksTable
from src.db.service.cambridge.cambridge_word import CambridgeWordService
from src.db.tables.cambridge.cambridge_words import CambridgeWordsTable
from src.db.service.cambridge.cambridge_sense import CambridgeSenseService
from src.db.tables.cambridge.cambridge_senses import CambridgeSensesTable
from src.db.service.cambridge.cambridge_definition import CambridgeDefinitionService
from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable
from src.db.service.cambridge.cambridge_transcription import CambridgeTranscriptionService
from src.db.tables.cambridge.cambridge_transcriptions import CambridgeTranscriptionsTable
from src.db.service.cambridge.cambridge_part_of_speech import CambridgePartOfSpeechService
from src.db.tables.cambridge.cambridge_parts_of_speech import CambridgePartsOfSpeechTable


def _insert_note(db, anki_note_id, word, trans, trans_type):
    AnkiNotesTable(db).add(
        {
            "anki_note_id": anki_note_id,
            "system_note_uuid": f"uuid-{anki_note_id}",
            "system_hash": "hash",
            "source_deck": "test::deck",
            "word": word,
            "trans": trans,
            "trans_type": trans_type,
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


def _seed_one_transcription_covering_n_senses(db, n: int, word="thick", trans="/θɪk/", trans_type="(uk)"):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    trans_table = CambridgeTranscriptionsTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)

    word_id = CambridgeWordService(word, words).add()
    pos_id = CambridgePartOfSpeechService(word_id, "adjective", pos).add()
    CambridgeTranscriptionService(pos_id, trans, trans_type, trans_table).add()

    def_ids = []
    for i in range(n):
        sense_id = CambridgeSenseService(pos_id, f"sense {i}", senses).add()
        def_ids.append(CambridgeDefinitionService(sense_id, f"definition {i}", None, definitions).add())
    return def_ids


def test_one_transcription_covering_three_senses_produces_three_candidates(db):
    """Explicit scenario from plan.md's verification checklist."""
    _seed_one_transcription_covering_n_senses(db, 3)
    _insert_note(db, 111, "thick", "/θɪk/", "(uk)")

    counts = match("test::deck")

    assert counts == {"matched": 1, "no-match": 0, "error": 0}
    assert len(NoteDefinitionLinksTable(db).get_candidates_for_note(111)) == 3


def test_no_matching_cambridge_word_produces_no_candidates(db):
    _insert_note(db, 111, "unknownword", "/x/", "(uk)")

    counts = match("test::deck")

    assert counts == {"matched": 0, "no-match": 1, "error": 0}
    assert NoteDefinitionLinksTable(db).get_candidates_for_note(111) == []


def test_wrong_transcription_type_produces_no_candidates(db):
    _seed_one_transcription_covering_n_senses(db, 1)
    _insert_note(db, 111, "thick", "/θɪk/", "(us)")  # different transcription_type than seeded

    counts = match("test::deck")

    assert counts == {"matched": 0, "no-match": 1, "error": 0}


def test_wrong_transcription_value_produces_no_candidates(db):
    _seed_one_transcription_covering_n_senses(db, 1)
    _insert_note(db, 111, "thick", "/different/", "(uk)")

    counts = match("test::deck")

    assert counts == {"matched": 0, "no-match": 1, "error": 0}


def test_match_is_idempotent_on_rerun(db):
    _seed_one_transcription_covering_n_senses(db, 3)
    _insert_note(db, 111, "thick", "/θɪk/", "(uk)")

    match("test::deck")
    match("test::deck")

    assert len(NoteDefinitionLinksTable(db).get_candidates_for_note(111)) == 3


def test_match_empty_note_set_reports_zero(db):
    assert match("test::deck") == {"matched": 0, "no-match": 0, "error": 0}
