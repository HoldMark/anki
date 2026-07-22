"""match: DB internal. Proposes candidate note_definition_links keyed on (word, transcription, transcription_type)."""

from src.db.setup import get_database, ensure_schema
from src.utils.logging import get_logger, log_summary, log_progress
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.service.note_definition_link import NoteDefinitionLinkService
from src.db.tables.note_definition_links import NoteDefinitionLinksTable
from src.db.tables.cambridge.cambridge_words import CambridgeWordsTable
from src.db.tables.cambridge.cambridge_senses import CambridgeSensesTable
from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable
from src.db.tables.cambridge.cambridge_transcriptions import CambridgeTranscriptionsTable
from src.db.tables.cambridge.cambridge_parts_of_speech import CambridgePartsOfSpeechTable

logger = get_logger(__name__)

MATCH_METHOD = "word_transcription"


def _find_candidate_definitions(note: dict, tables: dict) -> list[dict]:
    """Returns every cambridge_definitions row reachable from note's (word, trans, trans_type)."""
    word_rows = tables["words"].get({"word": note["word"]})
    if not word_rows:
        return []

    pos_rows = tables["pos"].get_for_word(word_rows[0]["id"])
    definitions = []

    for pos in pos_rows:
        trans_rows = tables["trans"].get(
            {"part_of_speech_id": pos["id"], "transcription_type": note["trans_type"]},
        )
        if not trans_rows or trans_rows[0]["transcription"] != note["trans"]:
            continue

        for sense in tables["senses"].get_for_part_of_speech(pos["id"]):
            definitions.extend(tables["definitions"].get_for_sense(sense["id"]))

    return definitions


def match(deck: str) -> dict:
    """
    Proposes candidate links for every already-pulled note in `deck`. Safe and cheap to
    re-run — existing candidate/confirmed/rejected links for a (note, definition) pair are
    never duplicated.
    """
    db = get_database()
    ensure_schema(db)

    tables = {
        "notes": AnkiNotesTable(db),
        "words": CambridgeWordsTable(db),
        "pos": CambridgePartsOfSpeechTable(db),
        "trans": CambridgeTranscriptionsTable(db),
        "senses": CambridgeSensesTable(db),
        "definitions": CambridgeDefinitionsTable(db),
        "links": NoteDefinitionLinksTable(db),
    }

    notes = tables["notes"].get_for_deck(deck) or []
    total = len(notes)
    counts = {"matched": 0, "no-match": 0, "error": 0}

    if total == 0:
        log_summary(logger, total=0, **counts)
        db.close()
        return counts

    for i, note in enumerate(notes, start=1):
        note_id = note["anki_note_id"]

        try:
            candidate_defs = _find_candidate_definitions(note, tables)
            service = NoteDefinitionLinkService(note_id, tables["links"])
            proposed_ids = [service.propose_candidate(d["id"], MATCH_METHOD) for d in candidate_defs]

            if any(pid is None for pid in proposed_ids) and candidate_defs:
                raise RuntimeError("failed to write one or more candidate links")

            if candidate_defs:
                counts["matched"] += 1
                log_progress(logger, i, total, note_id, "matched", f"{len(candidate_defs)} candidate(s)")
            else:
                counts["no-match"] += 1
                log_progress(logger, i, total, note_id, "no-match")

        except Exception as exc:
            counts["error"] += 1
            logger.error(f"match failed for note {note_id}", exc_info=True)
            log_progress(logger, i, total, note_id, "error", str(exc))

    log_summary(logger, total=total, **counts)
    db.close()
    return counts
