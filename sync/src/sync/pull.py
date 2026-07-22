"""pull: Anki -> DB, resilient per-note upsert into anki_notes."""

from src.db.setup import get_database, ensure_schema
from src.sync.diff import format_diff, compute_diff, confirm_diff
from src.anki.notes import get_notes, get_notes_fields
from src.utils.hashing import CONTENT_FIELDS, compute_content_hash
from src.utils.logging import get_logger, log_summary, log_progress
from src.config.load_env import get_config
from src.db.service.anki_note import AnkiNoteService
from src.db.tables.anki_notes import AnkiNotesTable

logger = get_logger(__name__)


def _build_row(note_id: int, fields: dict, deck: str, timestamp: str) -> dict:
    row = {name: (fields.get(name) or None) for name in CONTENT_FIELDS}
    row["anki_note_id"] = note_id
    row["system_note_uuid"] = fields.get("_system_note_uuid") or None
    row["system_hash"] = fields.get("_system_hash") or None
    row["source_deck"] = deck
    row["sync_status"] = "ok"
    row["sync_issue"] = None
    row["last_pulled_at"] = timestamp
    return row


def pull(deck: str, skip_review: bool = False) -> dict:
    """
    Fetches every note in `deck` and upserts it into anki_notes one at a time — a problem with
    one note is recorded as sync_status='error' and never aborts the run. Shows a before/after
    diff for confirmation unless skip_review or REQUIRE_REVIEW=false.
    """
    db = get_database()
    ensure_schema(db)
    anki_notes_table = AnkiNotesTable(db)
    require_review = get_config().require_review and not skip_review

    note_ids = get_notes(deck)
    total = len(note_ids)
    counts = {"created": 0, "updated": 0, "unchanged": 0, "error": 0}

    if total == 0:
        log_summary(logger, total=0, **counts)
        db.close()
        return counts

    fields_by_note = get_notes_fields(note_ids)

    for i, note_id in enumerate(note_ids, start=1):
        fields = fields_by_note.get(note_id) or {}
        row = _build_row(note_id, fields, deck, anki_notes_table.timestamp)

        if not fields:
            row["sync_status"] = "error"
            row["sync_issue"] = "AnkiConnect returned no fields for this note"

        try:
            service = AnkiNoteService(row, anki_notes_table)
            existing = service.existing()
            changes = compute_diff(existing, row, CONTENT_FIELDS)

            if existing and not changes and row["sync_status"] == "ok":
                counts["unchanged"] += 1
                log_progress(logger, i, total, note_id, "unchanged")
                continue

            detail = format_diff(changes)

            if row["sync_status"] == "ok":
                if fields.get("_system_hash") and compute_content_hash(fields) != fields["_system_hash"]:
                    detail += " [content changed since last stamp]"

                if require_review and not confirm_diff(note_id, changes):
                    log_progress(logger, i, total, note_id, "skipped", "declined by reviewer")
                    continue

            result = service.upsert()
            if result is None:
                raise RuntimeError("database upsert failed")

            _, outcome = result

            if row["sync_status"] == "error":
                counts["error"] += 1
                log_progress(logger, i, total, note_id, "error", row["sync_issue"])
            else:
                counts[outcome] += 1
                log_progress(logger, i, total, note_id, outcome, detail)

        except Exception as exc:
            counts["error"] += 1
            logger.error(f"pull failed for note {note_id}", exc_info=True)
            log_progress(logger, i, total, note_id, "error", str(exc))

    log_summary(logger, total=total, **counts)
    db.close()
    return counts
