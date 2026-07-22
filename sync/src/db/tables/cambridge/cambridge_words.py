import textwrap

from src.db.tables._table import Table


class CambridgeWordsTable(Table):
    """Populated externally by lexicon-scraper — this project only defines and reads the schema."""

    NAME = "cambridge_words"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS cambridge_words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            imported_at TIMESTAMP NOT NULL,
            UNIQUE(word)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO cambridge_words (word, imported_at) VALUES (:word, :imported_at);
    """)

    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_words WHERE word = :word;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new Cambridge word and return the id of the new row."""
        data["imported_at"] = self.timestamp
        return self._db.execute(self._INSERT_QUERY, data)

    def get(self, data: dict) -> list[dict] | None:
        """Return Cambridge word data matching (word,) — the natural key."""
        return self._db.query(self._SEARCH_QUERY, data)

    def all(self) -> list[dict] | None:
        """Return all Cambridge words."""
        return self._db.query("""SELECT * FROM cambridge_words;""")
