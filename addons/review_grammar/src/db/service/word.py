from copy import deepcopy

from ..tables.words import WordsTable


class WordService:
    """Service for database operations with words."""

    def __init__(self, word: str, definition: str, pos: str, table: WordsTable):
        self.word = word
        self.definition = definition
        self.pos = pos
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
        """Return word data from database."""
        return self._table.get(self.data)

    def id(self) -> int | None:
        """Return word id from database."""
        word_id = self.get()

        if word_id is None:
            return None

        elif len(word_id) == 0:
            return 0

        else:
            return word_id[0]["id"]

    def add(self) -> int | None:
        """Add word to database and return its id."""

        word_id = self.id()

        if word_id is None:
            return None

        elif word_id != 0:
            return word_id

        elif word_id == 0:
            word_id = self._table.add(self.data)

        return word_id
