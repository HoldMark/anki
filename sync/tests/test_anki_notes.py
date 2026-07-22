from src.anki.notes import get_notes, get_notes_fields, update_note_fields, get_notes_missing_uuid


def test_get_notes_returns_all_ids_sorted_descending(fake_anki):
    fake_anki.add_note(1)
    fake_anki.add_note(3)
    fake_anki.add_note(2)
    assert get_notes("test::deck") == [3, 2, 1]


def test_get_notes_respects_limit(fake_anki):
    fake_anki.add_note(1)
    fake_anki.add_note(2)
    fake_anki.add_note(3)
    assert get_notes("test::deck", limit=2) == [3, 2]


def test_get_notes_fields_maps_note_id_to_field_values(fake_anki):
    fake_anki.add_note(1, word="thick", definition="stupid")
    fields = get_notes_fields([1])
    assert fields[1]["word"] == "thick"
    assert fields[1]["definition"] == "stupid"


def test_get_notes_fields_missing_note_returns_empty_dict(fake_anki):
    fields = get_notes_fields([999])
    assert fields[999] == {}


def test_update_note_fields_writes_only_the_given_fields(fake_anki):
    fake_anki.add_note(1, word="thick", definition="old")
    update_note_fields(1, {"definition": "new"})
    assert fake_anki.notes[1]["definition"] == "new"
    assert fake_anki.notes[1]["word"] == "thick"


def test_get_notes_missing_uuid_returns_only_unstamped_notes(fake_anki):
    fake_anki.add_note(1, _system_note_uuid="")
    fake_anki.add_note(2, _system_note_uuid="already-stamped")
    fake_anki.add_note(3, _system_note_uuid="")

    missing = get_notes_missing_uuid("test::deck")
    assert set(missing) == {1, 3}
