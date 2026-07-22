import src.sync.stamp as stamp_module
from src.sync.stamp import stamp


def test_stamp_writes_both_fields_when_empty(fake_anki):
    fake_anki.add_note(1, word="thick")

    counts = stamp("test::deck")

    assert counts == {"updated": 1, "skipped": 0, "error": 0}
    assert fake_anki.notes[1]["_system_note_uuid"] != ""
    assert fake_anki.notes[1]["_system_hash"] != ""


def test_stamp_skips_already_stamped_note(fake_anki):
    fake_anki.add_note(1, word="thick", _system_note_uuid="existing-uuid", _system_hash="existing-hash")

    counts = stamp("test::deck")

    assert counts == {"updated": 0, "skipped": 1, "error": 0}
    assert fake_anki.notes[1]["_system_note_uuid"] == "existing-uuid"
    assert fake_anki.notes[1]["_system_hash"] == "existing-hash"


def test_stamp_only_writes_the_empty_field(fake_anki):
    """A note with a uuid already set but no hash yet must only get the hash written."""
    fake_anki.add_note(1, word="thick", _system_note_uuid="existing-uuid", _system_hash="")

    counts = stamp("test::deck")

    assert counts == {"updated": 1, "skipped": 0, "error": 0}
    assert fake_anki.notes[1]["_system_note_uuid"] == "existing-uuid"
    assert fake_anki.notes[1]["_system_hash"] != ""


def test_stamp_force_overwrites_existing_uuid_and_hash(fake_anki):
    fake_anki.add_note(1, word="thick", _system_note_uuid="old-uuid", _system_hash="old-hash")

    counts = stamp("test::deck", force=True)

    assert counts == {"updated": 1, "skipped": 0, "error": 0}
    assert fake_anki.notes[1]["_system_note_uuid"] != "old-uuid"
    assert fake_anki.notes[1]["_system_hash"] != "old-hash"


def test_stamp_dry_run_makes_no_writes(fake_anki):
    fake_anki.add_note(1, word="thick")

    counts = stamp("test::deck", dry_run=True)

    assert counts == {"updated": 1, "skipped": 0, "error": 0}
    assert fake_anki.notes[1]["_system_note_uuid"] == ""
    assert fake_anki.notes[1]["_system_hash"] == ""


def test_stamp_empty_deck_reports_zero(fake_anki):
    assert stamp("test::deck") == {"updated": 0, "skipped": 0, "error": 0}


def test_stamp_isolates_a_note_that_disappears_between_fetch_and_process(fake_anki, monkeypatch):
    """A note id present in findNotes but missing from notesInfo must not abort the batch."""
    fake_anki.add_note(1, word="thick")
    fake_anki.add_note(2, word="dull")

    real_get_notes = stamp_module.get_notes
    monkeypatch.setattr(stamp_module, "get_notes", lambda deck: real_get_notes(deck) + [999999])

    counts = stamp("test::deck")

    assert counts == {"updated": 2, "skipped": 0, "error": 1}
