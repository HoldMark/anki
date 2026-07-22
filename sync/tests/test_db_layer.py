"""
Formalizes the manual smoke test run while building Phase 2 — now as real assertions.
Uses the `db` fixture (scratch DB_PATH, schema already created).
"""

from src.db.service.anki_note import AnkiNoteService
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.service.note_definition_link import NoteDefinitionLinkService
from src.db.tables.note_definition_links import NoteDefinitionLinksTable
from src.db.service.cambridge.cambridge_word import CambridgeWordService
from src.db.tables.cambridge.cambridge_words import CambridgeWordsTable
from src.db.service.cambridge.cambridge_sense import CambridgeSenseService
from src.db.tables.cambridge.cambridge_senses import CambridgeSensesTable
from src.db.tables.cambridge.cambridge_examples import CambridgeExamplesTable
from src.db.service.cambridge.cambridge_definition import CambridgeDefinitionService
from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable
from src.db.service.cambridge.cambridge_part_of_speech import CambridgePartOfSpeechService
from src.db.tables.cambridge.cambridge_parts_of_speech import CambridgePartsOfSpeechTable


def _note_data(anki_note_id: int, system_note_uuid: str, definition: str) -> dict:
    return {
        "anki_note_id": anki_note_id,
        "system_note_uuid": system_note_uuid,
        "system_hash": "hash",
        "source_deck": "test::deck",
        "word": "thick",
        "trans": "/θɪk/",
        "trans_type": "(uk)",
        "part_of_speech": "adjective",
        "sense": "(STUPID)",
        "definition": definition,
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


def test_ensure_schema_creates_every_table(db):
    expected = {
        "anki_notes",
        "cambridge_words",
        "cambridge_parts_of_speech",
        "cambridge_transcriptions",
        "cambridge_senses",
        "cambridge_definitions",
        "cambridge_examples",
        "note_definition_links",
    }
    assert expected.issubset(db.table_names())


def test_anki_note_service_creates_then_updates_by_uuid(db):
    table = AnkiNotesTable(db)

    created = AnkiNoteService(_note_data(111, "uuid-1", "stupid"), table).upsert()
    assert created == (1, "created")

    updated = AnkiNoteService(_note_data(111, "uuid-1", "stupid (edited)"), table).upsert()
    assert updated == (1, "updated")

    assert table.get_by_uuid("uuid-1")[0]["definition"] == "stupid (edited)"
    assert table.get_by_anki_note_id(111)[0]["definition"] == "stupid (edited)"


def test_cambridge_get_or_create_chain_is_idempotent(db):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)

    word_id_1 = CambridgeWordService("thick", words).add()
    word_id_2 = CambridgeWordService("thick", words).add()
    assert word_id_1 == word_id_2 == 1

    pos_id = CambridgePartOfSpeechService(word_id_1, "adjective", pos).add()
    sense_id_1 = CambridgeSenseService(pos_id, "(STUPID)", senses).add()
    sense_id_2 = CambridgeSenseService(pos_id, "(NOT FLOWING)", senses).add()
    assert sense_id_1 != sense_id_2

    def_id_1 = CambridgeDefinitionService(sense_id_1, "stupid", "B1", definitions).add()
    def_id_2 = CambridgeDefinitionService(sense_id_2, "not flowing easily", None, definitions).add()
    assert def_id_1 != def_id_2
    assert definitions.get_by_id(def_id_2)[0]["sense_id"] == sense_id_2


def test_cambridge_examples_allow_duplicates(db):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)
    examples = CambridgeExamplesTable(db)

    word_id = CambridgeWordService("thick", words).add()
    pos_id = CambridgePartOfSpeechService(word_id, "adjective", pos).add()
    sense_id = CambridgeSenseService(pos_id, "(STUPID)", senses).add()
    def_id = CambridgeDefinitionService(sense_id, "stupid", "B1", definitions).add()

    examples.add({"definition_id": def_id, "text": "he is thick"})
    examples.add({"definition_id": def_id, "text": "he is thick"})

    assert len(examples.get_for_definition(def_id)) == 2


def test_note_definition_link_lifecycle_and_partial_unique_index(db):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)
    links = NoteDefinitionLinksTable(db)

    AnkiNoteService(_note_data(111, "uuid-111", "stupid"), AnkiNotesTable(db)).upsert()

    word_id = CambridgeWordService("thick", words).add()
    pos_id = CambridgePartOfSpeechService(word_id, "adjective", pos).add()

    sense_id_1 = CambridgeSenseService(pos_id, "(STUPID)", senses).add()
    sense_id_2 = CambridgeSenseService(pos_id, "(NOT FLOWING)", senses).add()
    def_id_1 = CambridgeDefinitionService(sense_id_1, "stupid", "B1", definitions).add()
    def_id_2 = CambridgeDefinitionService(sense_id_2, "not flowing easily", None, definitions).add()

    service = NoteDefinitionLinkService(111, links)
    link_id_1 = service.propose_candidate(def_id_1, "word_transcription")
    link_id_2 = service.propose_candidate(def_id_2, "word_transcription")
    assert link_id_1 != link_id_2
    assert len(service.candidates()) == 2

    # ambiguous: more than one candidate, auto-single must refuse
    assert service.confirm_if_single_candidate() is None

    service.confirm(link_id_1)
    assert service.confirmed()["id"] == link_id_1

    # a second confirm for the same note must be rejected by the partial unique index
    assert links.confirm(link_id_2) is None
    assert service.confirmed()["id"] == link_id_1


def test_propose_candidate_does_not_duplicate_existing_pair(db):
    words = CambridgeWordsTable(db)
    pos = CambridgePartsOfSpeechTable(db)
    senses = CambridgeSensesTable(db)
    definitions = CambridgeDefinitionsTable(db)
    links = NoteDefinitionLinksTable(db)

    AnkiNoteService(_note_data(111, "uuid-111", "stupid"), AnkiNotesTable(db)).upsert()

    word_id = CambridgeWordService("thick", words).add()
    pos_id = CambridgePartOfSpeechService(word_id, "adjective", pos).add()
    sense_id = CambridgeSenseService(pos_id, "(STUPID)", senses).add()
    def_id = CambridgeDefinitionService(sense_id, "stupid", "B1", definitions).add()

    service = NoteDefinitionLinkService(111, links)
    first = service.propose_candidate(def_id, "word_transcription")
    second = service.propose_candidate(def_id, "word_transcription")

    assert first == second
    assert len(links.get_for_note(111)) == 1
