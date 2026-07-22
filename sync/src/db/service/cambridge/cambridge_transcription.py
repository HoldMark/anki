from copy import deepcopy

from src.db.tables.cambridge.cambridge_transcriptions import CambridgeTranscriptionsTable


class CambridgeTranscriptionService:
    """Service for database operations with Cambridge transcriptions."""

    def __init__(
        self, part_of_speech_id: int, transcription: str, transcription_type: str, table: CambridgeTranscriptionsTable
    ):
        self.part_of_speech_id = part_of_speech_id
        self.transcription = transcription
        self.transcription_type = transcription_type
        self._table = table

    @property
    def data(self) -> dict:
        """Return transcription data as dict."""
        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def get(self) -> list[dict] | None:
        """Return transcription data from database, matching the (part_of_speech_id, transcription_type) natural key."""
        return self._table.get(
            {"part_of_speech_id": self.part_of_speech_id, "transcription_type": self.transcription_type}
        )

    def id(self) -> int | None:
        """Return transcription id from database."""
        rows = self.get()

        if rows is None:
            return None

        elif len(rows) == 0:
            return 0

        else:
            return rows[0]["id"]

    def add(self) -> int | None:
        """Add transcription to database and return its id."""

        transcription_id = self.id()

        if transcription_id is None:
            return None

        elif transcription_id != 0:
            return transcription_id

        elif transcription_id == 0:
            transcription_id = self._table.add(self.data)

        return transcription_id
