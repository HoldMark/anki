from copy import deepcopy

from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable


class CambridgeDefinitionService:
    """Service for database operations with Cambridge definitions."""

    def __init__(self, sense_id: int, text: str, cefr: str | None, table: CambridgeDefinitionsTable):
        self.sense_id = sense_id
        self.text = text
        self.cefr = cefr
        self._table = table

    @property
    def data(self) -> dict:
        """Return definition data as dict."""
        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def get(self) -> list[dict] | None:
        """Return definition data from database, matching the (sense_id, text) natural key."""
        return self._table.get({"sense_id": self.sense_id, "text": self.text})

    def id(self) -> int | None:
        """Return definition id from database."""
        rows = self.get()

        if rows is None:
            return None

        elif len(rows) == 0:
            return 0

        else:
            return rows[0]["id"]

    def add(self) -> int | None:
        """Add definition to database and return its id."""

        definition_id = self.id()

        if definition_id is None:
            return None

        elif definition_id != 0:
            return definition_id

        elif definition_id == 0:
            definition_id = self._table.add(self.data)

        return definition_id
