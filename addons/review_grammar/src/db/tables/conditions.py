import textwrap

from ._table import Table


class ConditionsTable(Table):
    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS conditions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            tense TEXT,
            usage TEXT,
            sentence_type TEXT,
            pronoun TEXT,
            created_at TIMESTAMP NOT NULL,
            UNIQUE(tense, usage, sentence_type, pronoun)
        );
    """)
    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO conditions (tense, usage, sentence_type, pronoun, created_at) VALUES (
            :tense, :usage, :sentence_type, :pronoun, :created_at
        );
    """)
    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM conditions WHERE
            tense = :tense AND
            usage = :usage AND
            sentence_type = :sentence_type AND
            pronoun = :pronoun;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new condition to the database and return the id of the new row."""
        data["created_at"] = self.timestamp
        last_row_id = self._db.execute(self._INSERT_QUERY, data)
        return last_row_id

    def get(self, data: dict) -> list[dict] | None:
        """Return data about a condition from the database."""
        return self._db.query(self._SEARCH_QUERY, data)
