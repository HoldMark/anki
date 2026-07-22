import textwrap

from src.db.tables._table import Table


class CambridgeSensesTable(Table):
    """Populated externally by lexicon-scraper — this project only defines and reads the schema."""

    NAME = "cambridge_senses"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS cambridge_senses (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_of_speech_id INTEGER NOT NULL,
            text TEXT NOT NULL,
            FOREIGN KEY (part_of_speech_id) REFERENCES cambridge_parts_of_speech(id),
            UNIQUE(part_of_speech_id, text)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO cambridge_senses (part_of_speech_id, text) VALUES (:part_of_speech_id, :text);
    """)

    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_senses WHERE part_of_speech_id = :part_of_speech_id AND text = :text;
    """)

    _GET_FOR_PART_OF_SPEECH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_senses WHERE part_of_speech_id = :part_of_speech_id;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new sense and return the id of the new row."""
        return self._db.execute(self._INSERT_QUERY, data)

    def get(self, data: dict) -> list[dict] | None:
        """Return sense data matching (part_of_speech_id, text) — the natural key."""
        return self._db.query(self._SEARCH_QUERY, data)

    def get_for_part_of_speech(self, part_of_speech_id: int) -> list[dict] | None:
        """Return all senses belonging to a part of speech."""
        return self._db.query(self._GET_FOR_PART_OF_SPEECH_QUERY, {"part_of_speech_id": part_of_speech_id})
