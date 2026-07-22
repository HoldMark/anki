import textwrap

from src.db.tables._table import Table


class NoteDefinitionLinksTable(Table):
    """Candidate -> confirmed -> rejected lifecycle linking anki_notes to cambridge_definitions."""

    NAME = "note_definition_links"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS note_definition_links (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anki_note_id INTEGER NOT NULL,
            cambridge_definition_id INTEGER NOT NULL,
            match_method TEXT NOT NULL,
            status TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            confirmed_at TIMESTAMP,
            FOREIGN KEY (anki_note_id) REFERENCES anki_notes(anki_note_id),
            FOREIGN KEY (cambridge_definition_id) REFERENCES cambridge_definitions(id),
            UNIQUE(anki_note_id, cambridge_definition_id)
        );
    """)

    _CREATE_CONFIRMED_INDEX_QUERY = textwrap.dedent("""
        CREATE UNIQUE INDEX IF NOT EXISTS idx_note_definition_links_confirmed
        ON note_definition_links(anki_note_id)
        WHERE status = 'confirmed';
    """)

    _INSERT_CANDIDATE_QUERY = textwrap.dedent("""
        INSERT INTO note_definition_links (
            anki_note_id, cambridge_definition_id, match_method, status, created_at
        ) VALUES (
            :anki_note_id, :cambridge_definition_id, :match_method, 'candidate', :created_at
        );
    """)

    _GET_FOR_NOTE_QUERY = textwrap.dedent("""
        SELECT * FROM note_definition_links WHERE anki_note_id = :anki_note_id;
    """)

    _GET_CANDIDATES_FOR_NOTE_QUERY = textwrap.dedent("""
        SELECT * FROM note_definition_links WHERE anki_note_id = :anki_note_id AND status = 'candidate';
    """)

    _GET_CONFIRMED_FOR_NOTE_QUERY = textwrap.dedent("""
        SELECT * FROM note_definition_links WHERE anki_note_id = :anki_note_id AND status = 'confirmed';
    """)

    _CONFIRM_QUERY = textwrap.dedent("""
        UPDATE note_definition_links SET status = 'confirmed', confirmed_at = :confirmed_at WHERE id = :id;
    """)

    _REJECT_QUERY = textwrap.dedent("""
        UPDATE note_definition_links SET status = 'rejected' WHERE id = :id;
    """)

    _GET_NOTE_IDS_WITH_CANDIDATES_QUERY = textwrap.dedent("""
        SELECT DISTINCT anki_note_id FROM note_definition_links WHERE status = 'candidate';
    """)

    _GET_NOTE_IDS_WITH_ANY_LINK_QUERY = textwrap.dedent("""
        SELECT DISTINCT anki_note_id FROM note_definition_links;
    """)

    _GET_MULTI_CANDIDATE_NOTE_IDS_QUERY = textwrap.dedent("""
        SELECT anki_note_id, COUNT(*) as candidate_count
        FROM note_definition_links
        WHERE status = 'candidate'
        GROUP BY anki_note_id
        HAVING COUNT(*) > 1;
    """)

    def create(self) -> int | None:
        """Creates the table and its partial-unique index enforcing at most one confirmed link per note."""
        table_created = self._db.execute(self._CREATION_QUERY)
        if not table_created:
            return None
        return self._db.execute(self._CREATE_CONFIRMED_INDEX_QUERY)

    def add_candidate(self, data: dict) -> int | None:
        """Add a new candidate link and return the id of the new row."""
        data["created_at"] = self.timestamp
        return self._db.execute(self._INSERT_CANDIDATE_QUERY, data)

    def get_for_note(self, anki_note_id: int) -> list[dict] | None:
        """Return every link (any status) for a note."""
        return self._db.query(self._GET_FOR_NOTE_QUERY, {"anki_note_id": anki_note_id})

    def get_candidates_for_note(self, anki_note_id: int) -> list[dict] | None:
        """Return non-resolved candidate links for a note."""
        return self._db.query(self._GET_CANDIDATES_FOR_NOTE_QUERY, {"anki_note_id": anki_note_id})

    def get_confirmed_for_note(self, anki_note_id: int) -> list[dict] | None:
        """Return the confirmed link for a note, if any (at most one, enforced by partial unique index)."""
        return self._db.query(self._GET_CONFIRMED_FOR_NOTE_QUERY, {"anki_note_id": anki_note_id})

    def confirm(self, link_id: int) -> int | None:
        """Promote a candidate link to confirmed."""
        return self._db.execute(self._CONFIRM_QUERY, {"id": link_id, "confirmed_at": self.timestamp})

    def reject(self, link_id: int) -> int | None:
        """Mark a candidate link as rejected."""
        return self._db.execute(self._REJECT_QUERY, {"id": link_id})

    def get_note_ids_with_candidates(self) -> list[int] | None:
        """Return anki_note_ids that currently have at least one non-resolved candidate link."""
        rows = self._db.query(self._GET_NOTE_IDS_WITH_CANDIDATES_QUERY)
        return [row["anki_note_id"] for row in rows] if rows is not None else None

    def get_note_ids_with_any_link(self) -> list[int] | None:
        """Return anki_note_ids that have at least one link row (any status) — used to find zero-candidate notes."""
        rows = self._db.query(self._GET_NOTE_IDS_WITH_ANY_LINK_QUERY)
        return [row["anki_note_id"] for row in rows] if rows is not None else None

    def get_multi_candidate_note_ids(self) -> list[dict] | None:
        """Return [{'anki_note_id': ..., 'candidate_count': ...}, ...] for notes with >1 unresolved candidate."""
        return self._db.query(self._GET_MULTI_CANDIDATE_NOTE_IDS_QUERY)
