from copy import deepcopy

from src.db.tables.anki_notes import AnkiNotesTable


class AnkiNoteService:
    """
    Upserts a single anki_notes row.

    Identity comes only from system_note_uuid (primary anchor) / anki_note_id (fallback for
    notes not yet stamped) — never from content fields, since word/definition/part_of_speech/
    examples can legitimately change inside Anki over time.
    """

    def __init__(self, data: dict, table: AnkiNotesTable):
        self.data = deepcopy(data)
        self._table = table

    def existing(self) -> dict | None:
        """Return the existing row for this note's identity, if any."""
        system_note_uuid = self.data.get("system_note_uuid")

        if system_note_uuid:
            rows = self._table.get_by_uuid(system_note_uuid)
            if rows:
                return rows[0]

        rows = self._table.get_by_anki_note_id(self.data["anki_note_id"])
        return rows[0] if rows else None

    def upsert(self) -> tuple[int, str] | None:
        """
        Insert or update the row matching this note's identity.
        Returns (row_id, outcome) where outcome is 'created' or 'updated', or None on failure.
        """
        existing = self.existing()

        if existing is None:
            row_id = self._table.add(self.data)
            return (row_id, "created") if row_id else None

        result = self._table.update(existing["id"], self.data)
        return (existing["id"], "updated") if result else None
