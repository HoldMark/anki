"""
Thin CLI wiring smoke test. Note: our shared logger's StreamHandler captured a reference to
sys.stdout at import time, so CliRunner's stdout redirection doesn't reliably capture it —
these tests check exit codes / no-exception, not output text. Behavioral correctness is
covered by the per-command test files (test_stamp.py, test_pull.py, etc.).
"""

from typer.testing import CliRunner

from main import app

runner = CliRunner()


def test_help_lists_every_command():
    result = runner.invoke(app, ["--help"])
    assert result.exit_code == 0
    for command in ["discover-new", "stamp", "pull", "match", "confirm", "review", "enrich"]:
        assert command in result.output


def test_discover_new_runs_through_the_cli_without_error(fake_anki):
    fake_anki.add_note(1, word="thick")
    result = runner.invoke(app, ["discover-new", "--deck", "test::deck"])
    assert result.exit_code == 0


def test_stamp_dry_run_through_the_cli_without_error(fake_anki):
    fake_anki.add_note(1, word="thick")
    result = runner.invoke(app, ["stamp", "--deck", "test::deck", "--dry-run"])
    assert result.exit_code == 0
    assert fake_anki.notes[1]["_system_note_uuid"] == ""  # dry-run must not write


def test_pull_through_the_cli_without_error(fake_anki, db):
    fake_anki.add_note(1, word="thick", _system_note_uuid="uuid-1", _system_hash="hash-1")
    result = runner.invoke(app, ["pull", "--deck", "test::deck", "--skip-review"])
    assert result.exit_code == 0


def test_match_through_the_cli_without_error(db):
    result = runner.invoke(app, ["match", "--deck", "test::deck"])
    assert result.exit_code == 0


def test_confirm_without_required_options_exits_with_error(db):
    result = runner.invoke(app, ["confirm"])
    assert result.exit_code == 1


def test_review_through_the_cli_without_error(db):
    result = runner.invoke(app, ["review"])
    assert result.exit_code == 0


def test_enrich_dry_run_through_the_cli_without_error(fake_anki, db):
    result = runner.invoke(app, ["enrich", "--deck", "test::deck", "--dry-run"])
    assert result.exit_code == 0
