import textwrap

from src.db.tables._table import Table


class CambridgeExamplesTable(Table):
    """Populated externally by lexicon-scraper — this project only defines and reads the schema."""

    NAME = "cambridge_examples"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS cambridge_examples (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            definition_id INTEGER NOT NULL,
            text TEXT,
            FOREIGN KEY (definition_id) REFERENCES cambridge_definitions(id)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO cambridge_examples (definition_id, text) VALUES (:definition_id, :text);
    """)

    _GET_FOR_DEFINITION_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_examples WHERE definition_id = :definition_id;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new example and return the id of the new row."""
        return self._db.execute(self._INSERT_QUERY, data)

    def get_for_definition(self, definition_id: int) -> list[dict] | None:
        """Return all examples belonging to a definition."""
        return self._db.query(self._GET_FOR_DEFINITION_QUERY, {"definition_id": definition_id})
