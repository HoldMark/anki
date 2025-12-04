from copy import deepcopy
from ..tables.conditions import ConditionsTable


class ConditionService:
    """Service for database operations with conditions."""

    def __init__(self, tense, usage, sentence_type, pronoun, table: ConditionsTable):
        self.tense = tense
        self.usage = usage
        self.sentence_type = sentence_type
        self.pronoun = pronoun
        self._table = table

    @property
    def data(self) -> dict:
        """Return review data as dict."""

        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def get(self) -> list[dict] | None:
        """Return condition data from database."""
        return self._table.get(self.data)

    def id(self) -> int | None:
        """Return condition id from database."""

        condition_id = self.get()

        if condition_id is None:
            return None

        elif len(condition_id) == 0:
            return 0

        else:
            return condition_id[0]["id"]

    def add(self) -> int | None:
        """Add condition to database and returns its id."""

        condition_id = self.id()

        if condition_id is None:
            return None

        elif condition_id != 0:
            return condition_id

        elif condition_id == 0:
            condition_id = self._table.add(self.data)

        return condition_id
