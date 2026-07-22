import textwrap

from src.db.tables._table import Table


class CambridgePartsOfSpeechTable(Table):
    """Populated externally by lexicon-scraper — this project only defines and reads the schema."""

    NAME = "cambridge_parts_of_speech"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS cambridge_parts_of_speech (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            FOREIGN KEY (word_id) REFERENCES cambridge_words(id),
            UNIQUE(word_id, name)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO cambridge_parts_of_speech (word_id, name) VALUES (:word_id, :name);
    """)

    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_parts_of_speech WHERE word_id = :word_id AND name = :name;
    """)

    _GET_FOR_WORD_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_parts_of_speech WHERE word_id = :word_id;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new part of speech and return the id of the new row."""
        return self._db.execute(self._INSERT_QUERY, data)

    def get(self, data: dict) -> list[dict] | None:
        """Return part-of-speech data matching (word_id, name) — the natural key."""
        return self._db.query(self._SEARCH_QUERY, data)

    def get_for_word(self, word_id: int) -> list[dict] | None:
        """Return all parts of speech belonging to a Cambridge word."""
        return self._db.query(self._GET_FOR_WORD_QUERY, {"word_id": word_id})
