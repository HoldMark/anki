"""enrich: DB -> Anki, whitelisted + extensible fields, sourced only from confirmed links."""

from src.db.setup import get_database, ensure_schema
from src.sync.diff import confirm_diff
from src.anki.notes import get_notes_fields, update_note_fields
from src.utils.logging import get_logger, log_summary, log_progress
from src.config.load_env import get_config
from src.db.tables.anki_notes import AnkiNotesTable
from src.db.tables.note_definition_links import NoteDefinitionLinksTable
from src.db.tables.cambridge.cambridge_definitions import CambridgeDefinitionsTable

logger = get_logger(__name__)


def _resolve_cefr(confirmed_link: dict, tables: dict) -> str | None:
    rows = tables["definitions"].get_by_id(confirmed_link["cambridge_definition_id"])
    return rows[0]["cefr"] if rows else None


# Registry: Anki field name -> resolver(confirmed_link, tables) -> value or None.
# Add a new enriched field here, not by editing enrich()'s control flow.
FIELD_RESOLVERS = {
    "cefr": _resolve_cefr,
}


def enrich(deck: str, force: bool = False, dry_run: bool = False, skip_review: bool = False) -> dict:
    """
    For every already-pulled note in `deck` with a confirmed Cambridge link, writes whitelisted
    fields (currently just cefr) to Anki if currently empty (or always if force). Re-fetches
    live Anki fields immediately before writing to guard against a concurrent hand-edit.
    """
    db = get_database()
    ensure_schema(db)
    notes_table = AnkiNotesTable(db)
    links_table = NoteDefinitionLinksTable(db)
    definitions_table = CambridgeDefinitionsTable(db)
    require_review = get_config().require_review and not skip_review

    notes = notes_table.get_for_deck(deck) or []
    total = len(notes)
    counts = {"updated": 0, "unchanged": 0, "skipped": 0, "error": 0}

    if total == 0:
        log_summary(logger, total=0, **counts)
        db.close()
        return counts

    for i, note in enumerate(notes, start=1):
        note_id = note["anki_note_id"]

        try:
            confirmed = links_table.get_confirmed_for_note(note_id)
            if not confirmed:
                counts["skipped"] += 1
                log_progress(logger, i, total, note_id, "skipped", "no confirmed link")
                continue

            live_fields = get_notes_fields([note_id]).get(note_id) or {}
            if not live_fields:
                raise ValueError("AnkiConnect returned no fields for this note")

            to_write = {}
            changes = {}

            for field_name, resolver in FIELD_RESOLVERS.items():
                value = resolver(confirmed[0], {"definitions": definitions_table})
                if not value:
                    continue

                current = live_fields.get(field_name, "")
                if current and not force:
                    continue
                if current == value:
                    continue

                to_write[field_name] = value
                changes[field_name] = (current, value)

            if not to_write:
                counts["unchanged"] += 1
                log_progress(logger, i, total, note_id, "unchanged")
                continue

            if require_review and not confirm_diff(note_id, changes):
                counts["skipped"] += 1
                log_progress(logger, i, total, note_id, "skipped", "declined by reviewer")
                continue

            if not dry_run:
                update_note_fields(note_id, to_write)

            counts["updated"] += 1
            detail = ", ".join(f"{field}: {old!r} -> {new!r}" for field, (old, new) in changes.items())
            if dry_run:
                detail += " (dry-run, not written)"
            log_progress(logger, i, total, note_id, "updated", detail)

        except Exception as exc:
            counts["error"] += 1
            logger.error(f"enrich failed for note {note_id}", exc_info=True)
            log_progress(logger, i, total, note_id, "error", str(exc))

    log_summary(logger, total=total, **counts)
    db.close()
    return counts
