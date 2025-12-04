import textwrap

from ._table import Table


class WordsTable(Table):
    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS words (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word TEXT NOT NULL,
            definition TEXT NOT NULL,
            pos TEXT NOT NULL,
            created_at TIMESTAMP NOT NULL,
            UNIQUE(word, definition, pos)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO words (word, definition, pos, created_at) VALUES (
            :word, :definition, :pos, :created_at
        );
    """)

    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM words WHERE word = :word AND definition = :definition AND pos = :pos;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new word to the database and return the id of the new row."""

        data["created_at"] = self.timestamp
        last_row_id = self._db.execute(self._INSERT_QUERY, data)

        return last_row_id

    def get(self, data: dict) -> list[dict] | None:
        """Return data about a word from the database"""
        return self._db.query(self._SEARCH_QUERY, data)

    def all(self) -> list[dict] | None:
        """Return all words in the database"""
        return self._db.query("""SELECT * FROM words;""")
