from src.db.tables.note_definition_links import NoteDefinitionLinksTable


class NoteDefinitionLinkService:
    """Manages the candidate -> confirmed -> rejected lifecycle for one Anki note's Cambridge links."""

    def __init__(self, anki_note_id: int, table: NoteDefinitionLinksTable):
        self.anki_note_id = anki_note_id
        self._table = table

    def propose_candidate(self, cambridge_definition_id: int, match_method: str) -> int | None:
        """Add a candidate link, unless one already exists for this (note, definition) pair (any status)."""
        existing = self._table.get_for_note(self.anki_note_id)

        if existing is None:
            return None

        for row in existing:
            if row["cambridge_definition_id"] == cambridge_definition_id:
                return row["id"]

        return self._table.add_candidate(
            {
                "anki_note_id": self.anki_note_id,
                "cambridge_definition_id": cambridge_definition_id,
                "match_method": match_method,
            }
        )

    def candidates(self) -> list[dict] | None:
        """Return this note's non-resolved candidate links."""
        return self._table.get_candidates_for_note(self.anki_note_id)

    def confirmed(self) -> dict | None:
        """Return this note's confirmed link, if any (at most one, enforced by a partial unique index)."""
        rows = self._table.get_confirmed_for_note(self.anki_note_id)
        return rows[0] if rows else None

    def confirm(self, link_id: int) -> int | None:
        """Promote a specific candidate to confirmed."""
        return self._table.confirm(link_id)

    def confirm_if_single_candidate(self) -> int | None:
        """Auto-confirm only when exactly one non-rejected candidate currently exists for this note."""
        candidates = self.candidates()

        if not candidates or len(candidates) != 1:
            return None

        return self.confirm(candidates[0]["id"])
