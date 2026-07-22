"""Uses hand-seeded synthetic Cambridge/link data — no real Cambridge data exists yet."""

from src.sync.confirm import confirm_manual, confirm_auto_single
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


def _insert_note(db, anki_note_id):
    AnkiNotesTable(db).add(
        {
            "anki_note_id": anki_note_id,
            "system_note_uuid": f"uuid-{anki_note_id}",
            "system_hash": "hash",
            "source_deck": "test::deck",
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


def test_confirm_manual_confirms_the_named_pair(db):
    _insert_note(db, 111)
    def_ids = _make_definitions(db, 2)
    links = NoteDefinitionLinksTable(db)
    service = NoteDefinitionLinkService(111, links)
    for definition_id in def_ids:
        service.propose_candidate(definition_id, "word_transcription")

    assert confirm_manual(111, def_ids[0]) is True
    assert service.confirmed()["cambridge_definition_id"] == def_ids[0]


def test_confirm_manual_unknown_pair_returns_false(db):
    _insert_note(db, 111)
    def_ids = _make_definitions(db, 1)
    links = NoteDefinitionLinksTable(db)
    NoteDefinitionLinkService(111, links).propose_candidate(def_ids[0], "word_transcription")

    assert confirm_manual(111, 999999) is False


def test_confirm_auto_single_resolves_only_unambiguous_notes(db):
    """Explicit scenario from plan.md: confirm --auto-single only resolves 1:1 notes."""
    _insert_note(db, 111)
    _insert_note(db, 222)
    def_ids = _make_definitions(db, 3)

    links = NoteDefinitionLinksTable(db)
    NoteDefinitionLinkService(111, links).propose_candidate(def_ids[0], "word_transcription")
    NoteDefinitionLinkService(222, links).propose_candidate(def_ids[1], "word_transcription")
    NoteDefinitionLinkService(222, links).propose_candidate(def_ids[2], "word_transcription")

    counts = confirm_auto_single()

    assert counts == {"confirmed": 1, "ambiguous": 1, "error": 0}
    assert NoteDefinitionLinkService(111, links).confirmed() is not None
    assert NoteDefinitionLinkService(222, links).confirmed() is None


def test_confirm_auto_single_no_candidates_reports_zero(db):
    assert confirm_auto_single() == {"confirmed": 0, "ambiguous": 0, "error": 0}
