import os

from src.db.database import Database
from src.config.load_env import get_config
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.tables.note_definition_links import NoteDefinitionLinksTable
from src.db.tables.cambridge.cambridge_words import CambridgeWordsTable
from src.db.tables.cambridge.cambridge_senses import CambridgeSensesTable
from src.db.tables.cambridge.cambridge_examples import CambridgeExamplesTable
from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable
from src.db.tables.cambridge.cambridge_transcriptions import CambridgeTranscriptionsTable
from src.db.tables.cambridge.cambridge_parts_of_speech import CambridgePartsOfSpeechTable


def get_database() -> Database:
    """Returns a Database connected to the configured DB_PATH, creating its parent directory if needed."""
    db_path = get_config().db_path
    os.makedirs(os.path.dirname(db_path) or ".", exist_ok=True)
    return Database(db_path)


def all_tables(db: Database) -> list:
    """Returns every table this project owns, in FK-safe creation order (referenced tables first)."""
    return [
        AnkiNotesTable(db),
        CambridgeWordsTable(db),
        CambridgePartsOfSpeechTable(db),
        CambridgeTranscriptionsTable(db),
        CambridgeSensesTable(db),
        CambridgeDefinitionsTable(db),
        CambridgeExamplesTable(db),
        NoteDefinitionLinksTable(db),
    ]


def ensure_schema(db: Database) -> bool | None:
    """Creates every table (and the note_definition_links partial index) if not already present."""
    return db.create_tables(all_tables(db))
