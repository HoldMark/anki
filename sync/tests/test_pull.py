import src.sync.pull as pull_module
from src.sync.pull import pull
from src.db.tables.anki_notes import AnkiNotesTable


def test_pull_creates_new_notes(fake_anki, db):
    fake_anki.add_note(1, word="thick", definition="stupid", _system_note_uuid="uuid-1", _system_hash="hash-1")

    counts = pull("test::deck", skip_review=True)

    assert counts == {"created": 1, "updated": 0, "unchanged": 0, "error": 0}

    row = AnkiNotesTable(db).get_by_anki_note_id(1)[0]
    assert row["word"] == "thick"
    assert row["definition"] == "stupid"
    assert row["sync_status"] == "ok"
    assert row["system_note_uuid"] == "uuid-1"


def test_pull_twice_with_no_changes_reports_zero_diffs(fake_anki, db):
    fake_anki.add_note(1, word="thick", definition="stupid", _system_note_uuid="uuid-1", _system_hash="hash-1")

    pull("test::deck", skip_review=True)
    counts = pull("test::deck", skip_review=True)

    assert counts == {"created": 0, "updated": 0, "unchanged": 1, "error": 0}


def test_pull_detects_a_hand_edit(fake_anki, db):
    fake_anki.add_note(1, word="thick", definition="stupid", _system_note_uuid="uuid-1", _system_hash="hash-1")
    pull("test::deck", skip_review=True)

    fake_anki.notes[1]["definition"] = "stupid (edited)"
    counts = pull("test::deck", skip_review=True)

    assert counts == {"created": 0, "updated": 1, "unchanged": 0, "error": 0}
    assert AnkiNotesTable(db).get_by_anki_note_id(1)[0]["definition"] == "stupid (edited)"


def test_pull_content_hash_drift_does_not_prevent_the_write(fake_anki, db):
    """A stale _system_hash (content changed since stamp, stamp not re-run) is informational only."""
    fake_anki.add_note(1, word="thick", definition="stupid", _system_note_uuid="uuid-1", _system_hash="stale-hash")

    counts = pull("test::deck", skip_review=True)

    assert counts == {"created": 1, "updated": 0, "unchanged": 0, "error": 0}


def test_pull_records_error_row_for_note_missing_from_notes_info(fake_anki, db, monkeypatch):
    fake_anki.add_note(1, word="thick")

    real_get_notes = pull_module.get_notes
    monkeypatch.setattr(pull_module, "get_notes", lambda deck: real_get_notes(deck) + [999999])

    counts = pull("test::deck", skip_review=True)

    assert counts == {"created": 1, "updated": 0, "unchanged": 0, "error": 1}
    error_row = AnkiNotesTable(db).get_by_anki_note_id(999999)[0]
    assert error_row["sync_status"] == "error"
    assert error_row["sync_issue"]


def test_pull_review_decline_skips_the_note(fake_anki, db, monkeypatch):
    fake_anki.add_note(1, word="thick", definition="stupid", _system_note_uuid="uuid-1", _system_hash="hash-1")
    monkeypatch.setenv("REQUIRE_REVIEW", "true")
    monkeypatch.setattr("builtins.input", lambda _: "n")

    counts = pull("test::deck", skip_review=False)

    assert counts["created"] == 0
    assert AnkiNotesTable(db).get_by_anki_note_id(1) == []


def test_pull_skip_review_bypasses_confirmation_even_if_require_review_true(fake_anki, db, monkeypatch):
    fake_anki.add_note(1, word="thick", definition="stupid", _system_note_uuid="uuid-1", _system_hash="hash-1")
    monkeypatch.setenv("REQUIRE_REVIEW", "true")

    def fail_if_called(_):
        raise AssertionError("input() should not be called when --skip-review is set")

    monkeypatch.setattr("builtins.input", fail_if_called)

    counts = pull("test::deck", skip_review=True)
    assert counts["created"] == 1


def test_pull_empty_deck_reports_zero(fake_anki, db):
    assert pull("test::deck", skip_review=True) == {"created": 0, "updated": 0, "unchanged": 0, "error": 0}
