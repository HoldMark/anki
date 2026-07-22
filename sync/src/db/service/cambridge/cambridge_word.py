from copy import deepcopy

from src.db.tables.cambridge.cambridge_words import CambridgeWordsTable


class CambridgeWordService:
    """Service for database operations with Cambridge words."""

    def __init__(self, word: str, table: CambridgeWordsTable):
        self.word = word
        self._table = table

    @property
    def data(self) -> dict:
        """Return word data as dict."""
        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def get(self) -> list[dict] | None:
        """Return Cambridge word data from database."""
        return self._table.get(self.data)

    def id(self) -> int | None:
        """Return Cambridge word id from database."""
        rows = self.get()

        if rows is None:
            return None

        elif len(rows) == 0:
            return 0

        else:
            return rows[0]["id"]

    def add(self) -> int | None:
        """Add Cambridge word to database and return its id."""

        word_id = self.id()

        if word_id is None:
            return None

        elif word_id != 0:
            return word_id

        elif word_id == 0:
            word_id = self._table.add(self.data)

        return word_id
