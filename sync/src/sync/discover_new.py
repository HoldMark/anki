"""discover-new: read-only, finds Anki notes with an empty _system_note_uuid (freshly imported, not yet stamped)."""

from src.anki.notes import get_notes_fields, get_notes_missing_uuid


def discover_new(deck: str) -> list[dict]:
    """Returns [{'anki_note_id': ..., 'word': ...}, ...] for notes in `deck` missing _system_note_uuid."""
    note_ids = get_notes_missing_uuid(deck)

    if not note_ids:
        return []

    fields = get_notes_fields(note_ids)
    return [{"anki_note_id": note_id, "word": fields[note_id].get("word", "")} for note_id in note_ids]
