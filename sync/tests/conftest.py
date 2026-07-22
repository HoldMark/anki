"""
Shared test fixtures.

Hard rule for this whole suite: never call the real AnkiConnect server and never touch the
real project DB (data/sync.sqlite). Every test gets its own scratch sqlite file (via DB_PATH)
and every Anki-touching code path goes through FakeAnkiConnect instead of a real HTTP call.
"""

import pytest

from src.db.setup import get_database, ensure_schema


class FakeAnkiConnect:
    """
    In-memory stand-in for AnkiConnect. Supports exactly the actions src/anki/notes.py uses:
    findNotes, notesInfo, updateNoteFields. Deck/query filtering is intentionally simplistic —
    real AnkiConnect search syntax is out of scope for this fake, already verified manually
    against the live server in earlier sessions (see checklist.md).
    """

    def __init__(self):
        self.notes: dict[int, dict[str, str]] = {}

    def invoke(self, action: str, **params) -> object:
        if action == "findNotes":
            query = params.get("query", "")
            if '"_system_note_uuid:"' in query:
                return [note_id for note_id, fields in self.notes.items() if not fields.get("_system_note_uuid")]
            return list(self.notes.keys())

        if action == "notesInfo":
            result = []
            for note_id in params["notes"]:
                fields = self.notes.get(note_id)
                if fields is None:
                    result.append(None)
                else:
                    result.append({"fields": {name: {"value": value} for name, value in fields.items()}})
            return result

        if action == "updateNoteFields":
            note = params["note"]
            self.notes.setdefault(note["id"], {}).update(note["fields"])
            return None

        raise ValueError(f"FakeAnkiConnect got an unexpected action: {action}")

    def add_note(self, note_id: int, **fields) -> None:
        """Test helper: register a note with the given fields, defaulting every known
        content/system field to '' so callers only need to specify what they care about."""
        defaults = {
            "word": "",
            "trans": "",
            "trans_type": "",
            "part_of_speech": "",
            "sense": "",
            "definition": "",
            "cefr": "",
            "example_1": "",
            "example_2": "",
            "example_3": "",
            "example_4": "",
            "example_5": "",
            "example_6": "",
            "example_7": "",
            "audio": "",
            "picture": "",
            "video": "",
            "hints": "",
            "_system_hash": "",
            "_system_note_uuid": "",
        }
        defaults.update(fields)
        self.notes[note_id] = defaults


@pytest.fixture(autouse=True)
def scratch_env(tmp_path, monkeypatch):
    """Every test gets its own DB file and non-interactive review by default."""
    monkeypatch.setenv("DB_PATH", str(tmp_path / "test.sqlite"))
    monkeypatch.setenv("DECK_NAME", "test::deck")
    monkeypatch.setenv("REQUIRE_REVIEW", "false")
    monkeypatch.setenv("ANKI_CONNECT_URL", "http://unused.invalid:0")
    yield


@pytest.fixture
def fake_anki(monkeypatch):
    """Patches src.anki.notes.invoke — the single point every Anki-touching command calls through."""
    fake = FakeAnkiConnect()
    monkeypatch.setattr("src.anki.notes.invoke", fake.invoke)
    return fake


@pytest.fixture
def db():
    """A Database connected to the scratch DB_PATH, with schema already created."""
    database = get_database()
    ensure_schema(database)
    yield database
    database.close()
