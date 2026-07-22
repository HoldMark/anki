from src.sync.diff import format_diff, compute_diff, confirm_diff


def test_compute_diff_no_existing_row_flags_all_non_empty_fields():
    new = {"word": "thick", "definition": "stupid", "cefr": None}
    changes = compute_diff(None, new, ["word", "definition", "cefr"])
    assert changes == {"word": (None, "thick"), "definition": (None, "stupid")}


def test_compute_diff_only_flags_changed_fields():
    old = {"word": "thick", "definition": "stupid"}
    new = {"word": "thick", "definition": "stupid (edited)"}
    changes = compute_diff(old, new, ["word", "definition"])
    assert changes == {"definition": ("stupid", "stupid (edited)")}


def test_compute_diff_no_changes_returns_empty():
    old = {"word": "thick", "definition": "stupid"}
    new = {"word": "thick", "definition": "stupid"}
    assert compute_diff(old, new, ["word", "definition"]) == {}


def test_format_diff_renders_every_change():
    text = format_diff({"definition": ("old", "new")})
    assert "definition" in text
    assert "'old'" in text
    assert "'new'" in text


def test_confirm_diff_no_changes_returns_true_without_prompting(monkeypatch):
    def fail_if_called(_):
        raise AssertionError("input() should not be called when there are no changes")

    monkeypatch.setattr("builtins.input", fail_if_called)
    assert confirm_diff(123, {}) is True


def test_confirm_diff_yes_returns_true(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "y")
    assert confirm_diff(123, {"word": ("old", "new")}) is True


def test_confirm_diff_no_returns_false(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "n")
    assert confirm_diff(123, {"word": ("old", "new")}) is False


def test_confirm_diff_empty_answer_defaults_to_false(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert confirm_diff(123, {"word": ("old", "new")}) is False
