import typer

from src.sync.pull import pull
from src.sync.match import match
from src.sync.stamp import stamp
from src.sync.enrich import enrich
from src.sync.review import review
from src.sync.confirm import confirm_manual, confirm_auto_single
from src.utils.logging import get_logger
from src.config.load_env import get_config
from src.sync.discover_new import discover_new

app = typer.Typer()
logger = get_logger("main")


@app.command("discover-new")
def discover_new_command(
    deck: str = typer.Option(None, "--deck", help="Deck to search (defaults to DECK_NAME from config)"),
):
    """Find Anki notes with an empty _system_note_uuid — freshly imported, not yet stamped. Read-only, no writes."""
    deck = deck or get_config().deck_name
    notes = discover_new(deck)

    for note in notes:
        logger.info(f"{note['anki_note_id']}\t{note['word']}")

    logger.info(f"discover-new: {len(notes)} note(s) missing _system_note_uuid in deck '{deck}'")


@app.command("stamp")
def stamp_command(
    deck: str = typer.Option(None, "--deck", help="Deck to search (defaults to DECK_NAME from config)"),
    force: bool = typer.Option(False, "--force", help="Re-mint/re-stamp fields even if already non-empty"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview planned writes without touching Anki"),
):
    """Mint _system_note_uuid/_system_hash for notes in `deck` (Anki -> Anki, no DB). Safe to re-run broadly."""
    deck = deck or get_config().deck_name
    stamp(deck, force=force, dry_run=dry_run)


@app.command("pull")
def pull_command(
    deck: str = typer.Option(None, "--deck", help="Deck to search (defaults to DECK_NAME from config)"),
    skip_review: bool = typer.Option(False, "--skip-review", help="Apply changes without an interactive diff prompt"),
):
    """Mirror notes in `deck` into the local DB (Anki -> DB), one note at a time. Never aborts on a bad note."""
    deck = deck or get_config().deck_name
    pull(deck, skip_review=skip_review)


@app.command("match")
def match_command(
    deck: str = typer.Option(None, "--deck", help="Deck to search (defaults to DECK_NAME from config)"),
):
    """Propose candidate Cambridge links for already-pulled notes in `deck`. DB internal, safe to re-run."""
    deck = deck or get_config().deck_name
    match(deck)


@app.command("confirm")
def confirm_command(
    note: int = typer.Option(None, "--note", help="Anki note id to confirm (requires --definition)"),
    definition: int = typer.Option(None, "--definition", help="Cambridge definition id to confirm (requires --note)"),
    auto_single: bool = typer.Option(False, "--auto-single", help="Auto-confirm every note with exactly one candidate"),
):
    """Promote a candidate link to confirmed — either a specific (--note, --definition) pair, or --auto-single."""
    if auto_single:
        confirm_auto_single()
        return

    if note is None or definition is None:
        typer.echo("Provide either --auto-single, or both --note and --definition.", err=True)
        raise typer.Exit(code=1)

    confirm_manual(note, definition)


@app.command("review")
def review_command():
    """Read-only report: notes with zero candidates, notes with multiple unresolved candidates, pull errors."""
    report = review()

    logger.info(f"review: {len(report['zero_candidates'])} note(s) with zero candidates")
    for note in report["zero_candidates"]:
        logger.info(f"  zero-candidates\t{note['anki_note_id']}\t{note['word']}")

    logger.info(f"review: {len(report['multi_candidates'])} note(s) with multiple unresolved candidates")
    for row in report["multi_candidates"]:
        logger.info(f"  multi-candidates\t{row['anki_note_id']}\t{row['candidate_count']} candidates")

    logger.info(f"review: {len(report['pull_errors'])} note(s) with a pull error")
    for note in report["pull_errors"]:
        logger.info(f"  pull-error\t{note['anki_note_id']}\t{note['sync_issue']}")


@app.command("enrich")
def enrich_command(
    deck: str = typer.Option(None, "--deck", help="Deck to search (defaults to DECK_NAME from config)"),
    force: bool = typer.Option(False, "--force", help="Overwrite even if the Anki field is already non-empty"),
    dry_run: bool = typer.Option(False, "--dry-run", help="Preview planned writes without touching Anki"),
    skip_review: bool = typer.Option(False, "--skip-review", help="Apply changes without an interactive diff prompt"),
):
    """Write whitelisted DB-derived fields (currently just cefr) to Anki, sourced only from confirmed links."""
    deck = deck or get_config().deck_name
    enrich(deck, force=force, dry_run=dry_run, skip_review=skip_review)


if __name__ == "__main__":
    app()
