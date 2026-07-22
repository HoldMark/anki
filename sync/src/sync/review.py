"""review: read-only report of notes needing attention. No --deck scoping — operates over every mirrored note."""

from src.db.setup import get_database, ensure_schema
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.tables.note_definition_links import NoteDefinitionLinksTable


def review() -> dict:
    """
    Returns a read-only report:
    - zero_candidates: mirrored notes with no note_definition_links row at all (any status)
    - multi_candidates: [{'anki_note_id', 'candidate_count'}, ...] for notes with >1 unresolved candidate
    - pull_errors: anki_notes rows currently in sync_status='error'
    """
    db = get_database()
    ensure_schema(db)
    notes_table = AnkiNotesTable(db)
    links_table = NoteDefinitionLinksTable(db)

    all_notes = notes_table.all() or []
    linked_note_ids = set(links_table.get_note_ids_with_any_link() or [])
    zero_candidates = [note for note in all_notes if note["anki_note_id"] not in linked_note_ids]

    multi_candidates = links_table.get_multi_candidate_note_ids() or []
    pull_errors = notes_table.get_errors() or []

    db.close()
    return {
        "zero_candidates": zero_candidates,
        "multi_candidates": multi_candidates,
        "pull_errors": pull_errors,
    }
