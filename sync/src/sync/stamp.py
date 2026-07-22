"""stamp: Anki -> Anki, no DB. Mints _system_note_uuid/_system_hash for notes that don't have them yet."""

import uuid

from src.anki.notes import get_notes, get_notes_fields, update_note_fields
from src.utils.hashing import compute_content_hash
from src.utils.logging import get_logger, log_summary, log_progress

logger = get_logger(__name__)


def stamp(deck: str, force: bool = False, dry_run: bool = False) -> dict:
    """
    Stamps every note in `deck` with _system_hash/_system_note_uuid, skipping a field that's
    already non-empty unless `force`. Never writes to Anki when `dry_run` is True. Returns
    outcome counts.
    """
    note_ids = get_notes(deck)
    total = len(note_ids)
    counts = {"updated": 0, "skipped": 0, "error": 0}

    if total == 0:
        log_summary(logger, total=0, **counts)
        return counts

    fields_by_note = get_notes_fields(note_ids)

    for i, note_id in enumerate(note_ids, start=1):
        fields = fields_by_note.get(note_id)

        try:
            if not fields:
                raise ValueError("AnkiConnect returned no fields for this note")

            current_uuid = fields.get("_system_note_uuid", "")
            current_hash = fields.get("_system_hash", "")

            to_write = {}
            if force or not current_uuid:
                to_write["_system_note_uuid"] = str(uuid.uuid4())
            if force or not current_hash:
                to_write["_system_hash"] = compute_content_hash(fields)

            if not to_write:
                counts["skipped"] += 1
                log_progress(logger, i, total, note_id, "skipped", "already stamped")
                continue

            if not dry_run:
                update_note_fields(note_id, to_write)

            counts["updated"] += 1
            detail = ", ".join(sorted(to_write.keys()))
            if dry_run:
                detail += " (dry-run, not written)"
            log_progress(logger, i, total, note_id, "updated", detail)

        except Exception as exc:
            counts["error"] += 1
            log_progress(logger, i, total, note_id, "error", str(exc))
            logger.error(f"stamp failed for note {note_id}", exc_info=True)

    log_summary(logger, total=total, **counts)
    return counts
