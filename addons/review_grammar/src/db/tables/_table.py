from datetime import datetime

from ..database import Database


class Table:
    """Base class for all tables"""

    _CREATION_QUERY = ""

    def __init__(self, database: Database):
        self._db = database

    @property
    def timestamp(self) -> str:
        """Returns timestamp in format DD.MM.YYYY HH:MM:SS:MS"""
        now = datetime.now()
        return now.strftime("%d.%m.%Y %H:%M:%S") + f":{int(now.microsecond / 1000):03d}"

    def create(self) -> int | None:
        """Creates table and returns 1 if successful, None otherwise"""
        return self._db.execute(self._CREATION_QUERY)
