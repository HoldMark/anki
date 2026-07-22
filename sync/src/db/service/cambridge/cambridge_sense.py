from copy import deepcopy

from src.db.tables.cambridge.cambridge_senses import CambridgeSensesTable


class CambridgeSenseService:
    """Service for database operations with Cambridge senses."""

    def __init__(self, part_of_speech_id: int, text: str, table: CambridgeSensesTable):
        self.part_of_speech_id = part_of_speech_id
        self.text = text
        self._table = table

    @property
    def data(self) -> dict:
        """Return sense data as dict."""
        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def get(self) -> list[dict] | None:
        """Return sense data from database."""
        return self._table.get(self.data)

    def id(self) -> int | None:
        """Return sense id from database."""
        rows = self.get()

        if rows is None:
            return None

        elif len(rows) == 0:
            return 0

        else:
            return rows[0]["id"]

    def add(self) -> int | None:
        """Add sense to database and return its id."""

        sense_id = self.id()

        if sense_id is None:
            return None

        elif sense_id != 0:
            return sense_id

        elif sense_id == 0:
            sense_id = self._table.add(self.data)

        return sense_id
