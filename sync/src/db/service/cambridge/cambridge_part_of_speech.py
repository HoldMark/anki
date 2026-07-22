from copy import deepcopy

from src.db.tables.cambridge.cambridge_parts_of_speech import CambridgePartsOfSpeechTable


class CambridgePartOfSpeechService:
    """Service for database operations with Cambridge parts of speech."""

    def __init__(self, word_id: int, name: str, table: CambridgePartsOfSpeechTable):
        self.word_id = word_id
        self.name = name
        self._table = table

    @property
    def data(self) -> dict:
        """Return part-of-speech data as dict."""
        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def get(self) -> list[dict] | None:
        """Return part-of-speech data from database."""
        return self._table.get(self.data)

    def id(self) -> int | None:
        """Return part-of-speech id from database."""
        rows = self.get()

        if rows is None:
            return None

        elif len(rows) == 0:
            return 0

        else:
            return rows[0]["id"]

    def add(self) -> int | None:
        """Add part of speech to database and return its id."""

        pos_id = self.id()

        if pos_id is None:
            return None

        elif pos_id != 0:
            return pos_id

        elif pos_id == 0:
            pos_id = self._table.add(self.data)

        return pos_id
