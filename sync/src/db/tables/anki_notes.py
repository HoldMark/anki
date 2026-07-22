import textwrap

from src.db.tables._table import Table


class AnkiNotesTable(Table):
    NAME = "anki_notes"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS anki_notes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            anki_note_id INTEGER NOT NULL,
            word TEXT,
            trans TEXT,
            trans_type TEXT,
            part_of_speech TEXT,
            sense TEXT,
            definition TEXT,
            cefr TEXT,
            example_1 TEXT,
            example_2 TEXT,
            example_3 TEXT,
            example_4 TEXT,
            example_5 TEXT,
            example_6 TEXT,
            example_7 TEXT,
            audio TEXT,
            picture TEXT,
            video TEXT,
            hints TEXT,
            system_note_uuid TEXT,
            system_hash TEXT,
            source_deck TEXT NOT NULL,
            sync_status TEXT NOT NULL,
            sync_issue TEXT,
            last_pulled_at TIMESTAMP NOT NULL,
            UNIQUE(anki_note_id),
            UNIQUE(system_note_uuid)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO anki_notes (
            anki_note_id,
            word, trans, trans_type, part_of_speech, sense, definition, cefr,
            example_1, example_2, example_3, example_4, example_5, example_6, example_7,
            audio, picture, video, hints,
            system_note_uuid, system_hash, source_deck,
            sync_status, sync_issue, last_pulled_at
        ) VALUES (
            :anki_note_id,
            :word, :trans, :trans_type, :part_of_speech, :sense, :definition, :cefr,
            :example_1, :example_2, :example_3, :example_4, :example_5, :example_6, :example_7,
            :audio, :picture, :video, :hints,
            :system_note_uuid, :system_hash, :source_deck,
            :sync_status, :sync_issue, :last_pulled_at
        );
    """)

    _UPDATE_QUERY = textwrap.dedent("""
        UPDATE anki_notes SET
            anki_note_id = :anki_note_id,
            word = :word,
            trans = :trans,
            trans_type = :trans_type,
            part_of_speech = :part_of_speech,
            sense = :sense,
            definition = :definition,
            cefr = :cefr,
            example_1 = :example_1,
            example_2 = :example_2,
            example_3 = :example_3,
            example_4 = :example_4,
            example_5 = :example_5,
            example_6 = :example_6,
            example_7 = :example_7,
            audio = :audio,
            picture = :picture,
            video = :video,
            hints = :hints,
            system_note_uuid = :system_note_uuid,
            system_hash = :system_hash,
            source_deck = :source_deck,
            sync_status = :sync_status,
            sync_issue = :sync_issue,
            last_pulled_at = :last_pulled_at
        WHERE id = :id;
    """)

    _GET_BY_UUID_QUERY = textwrap.dedent("""
        SELECT * FROM anki_notes WHERE system_note_uuid = :system_note_uuid;
    """)

    _GET_BY_ANKI_NOTE_ID_QUERY = textwrap.dedent("""
        SELECT * FROM anki_notes WHERE anki_note_id = :anki_note_id;
    """)

    _GET_FOR_DECK_QUERY = textwrap.dedent("""
        SELECT * FROM anki_notes WHERE source_deck = :source_deck;
    """)

    _GET_ERRORS_QUERY = textwrap.dedent("""
        SELECT * FROM anki_notes WHERE sync_status = 'error';
    """)

    def add(self, data: dict) -> int | None:
        """Insert a new anki_notes row and return its id."""
        return self._db.execute(self._INSERT_QUERY, data)

    def update(self, row_id: int, data: dict) -> int | None:
        """Update an existing anki_notes row identified by its primary key."""
        return self._db.execute(self._UPDATE_QUERY, {**data, "id": row_id})

    def get_by_uuid(self, system_note_uuid: str) -> list[dict] | None:
        """Look up a row by system_note_uuid — the durable identity anchor."""
        return self._db.query(self._GET_BY_UUID_QUERY, {"system_note_uuid": system_note_uuid})

    def get_by_anki_note_id(self, anki_note_id: int) -> list[dict] | None:
        """Look up a row by anki_note_id — fallback for notes not yet stamped."""
        return self._db.query(self._GET_BY_ANKI_NOTE_ID_QUERY, {"anki_note_id": anki_note_id})

    def get_for_deck(self, deck: str) -> list[dict] | None:
        """Return every mirrored note whose last pull used this deck for selection."""
        return self._db.query(self._GET_FOR_DECK_QUERY, {"source_deck": deck})

    def get_errors(self) -> list[dict] | None:
        """Return every mirrored note currently in an error state (sync_status='error')."""
        return self._db.query(self._GET_ERRORS_QUERY)

    def all(self) -> list[dict] | None:
        """Return every mirrored note."""
        return self._db.query("""SELECT * FROM anki_notes;""")
