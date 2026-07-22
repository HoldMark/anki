import textwrap

from src.db.tables._table import Table


class CambridgeTranscriptionsTable(Table):
    """Populated externally by lexicon-scraper — this project only defines and reads the schema."""

    NAME = "cambridge_transcriptions"

    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS cambridge_transcriptions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            part_of_speech_id INTEGER NOT NULL,
            transcription TEXT NOT NULL,
            transcription_type TEXT NOT NULL,
            FOREIGN KEY (part_of_speech_id) REFERENCES cambridge_parts_of_speech(id),
            UNIQUE(part_of_speech_id, transcription_type)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO cambridge_transcriptions (part_of_speech_id, transcription, transcription_type) VALUES (
            :part_of_speech_id, :transcription, :transcription_type
        );
    """)

    _SEARCH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_transcriptions
        WHERE part_of_speech_id = :part_of_speech_id AND transcription_type = :transcription_type;
    """)

    _GET_FOR_PART_OF_SPEECH_QUERY = textwrap.dedent("""
        SELECT * FROM cambridge_transcriptions WHERE part_of_speech_id = :part_of_speech_id;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new transcription and return the id of the new row."""
        return self._db.execute(self._INSERT_QUERY, data)

    def get(self, data: dict) -> list[dict] | None:
        """Return transcription data matching (part_of_speech_id, transcription_type) — the natural key."""
        return self._db.query(self._SEARCH_QUERY, data)

    def get_for_part_of_speech(self, part_of_speech_id: int) -> list[dict] | None:
        """Return all transcriptions belonging to a part of speech."""
        return self._db.query(self._GET_FOR_PART_OF_SPEECH_QUERY, {"part_of_speech_id": part_of_speech_id})
