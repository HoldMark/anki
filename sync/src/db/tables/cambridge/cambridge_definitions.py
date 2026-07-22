import textwrap

from src.db.tables._table import Table


class CambridgeDefinitionsTable(Table):
    """Populated externally by lexicon-scraper — this project only defines and reads the schema."""

    NAME = "cambridge_definitions"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS cambridge_definitions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            sense_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            cefr TEXT,
            FOREIGN KEY (sense_id) REFERENCES cambridge_senses(id),
            UNIQUE(sense_id, text)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO cambridge_definitions (sense_id, text, cefr) VALUES (:sense_id, :text, :cefr);
    """)

    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_definitions WHERE sense_id = :sense_id AND text = :text;
    """)

    _GET_FOR_SENSE_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_definitions WHERE sense_id = :sense_id;
    """)

    _GET_BY_ID_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_definitions WHERE id = :id;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new definition and return the id of the new row."""
        return self._db.execute(self._INSERT_QUERY, data)

    def get(self, data: dict) -> list[dict] | None:
        """Return definition data matching (sense_id, text) — the natural key."""
        return self._db.query(self._SEARCH_QUERY, data)

    def get_for_sense(self, sense_id: int) -> list[dict] | None:
        """Return all definitions belonging to a sense."""
        return self._db.query(self._GET_FOR_SENSE_QUERY, {"sense_id": sense_id})

    def get_by_id(self, definition_id: int) -> list[dict] | None:
        """Return a single definition row by its primary key."""
        return self._db.query(self._GET_BY_ID_QUERY, {"id": definition_id})
