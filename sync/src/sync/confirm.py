"""confirm: DB internal. Promotes a candidate note_definition_link to confirmed."""

from src.db.setup import get_database, ensure_schema
from src.utils.logging import get_logger, log_summary, log_progress
from src.db.service.note_definition_link import NoteDefinitionLinkService
from src.db.tables.note_definition_links import NoteDefinitionLinksTable

logger = get_logger(__name__)


def confirm_manual(note_id: int, definition_id: int) -> bool:
    """Confirms the candidate link (note_id, definition_id) explicitly. Returns True on success."""
    db = get_database()
    ensure_schema(db)
    links_table = NoteDefinitionLinksTable(db)
    service = NoteDefinitionLinkService(note_id, links_table)

    candidates = service.candidates() or []
    match = next((c for c in candidates if c["cambridge_definition_id"] == definition_id), None)

    if match is None:
        logger.error(f"confirm: no candidate link for note {note_id} -> definition {definition_id}")
        db.close()
        return False

    result = service.confirm(match["id"])
    db.close()

    if result is None:
        logger.error(f"confirm: failed to confirm link {match['id']} for note {note_id}")
        return False

    logger.info(f"confirm: note {note_id} -> definition {definition_id} confirmed")
    return True


def confirm_auto_single() -> dict:
    """
    Auto-confirms every note that currently has exactly one non-resolved candidate link.
    Notes with zero or multiple candidates are left untouched for manual review.
    """
    db = get_database()
    ensure_schema(db)
    links_table = NoteDefinitionLinksTable(db)

    note_ids = links_table.get_note_ids_with_candidates() or []
    total = len(note_ids)
    counts = {"confirmed": 0, "ambiguous": 0, "error": 0}

    if total == 0:
        log_summary(logger, total=0, **counts)
        db.close()
        return counts

    for i, note_id in enumerate(note_ids, start=1):
        try:
            service = NoteDefinitionLinkService(note_id, links_table)
            result = service.confirm_if_single_candidate()

            if result is not None:
                counts["confirmed"] += 1
                log_progress(logger, i, total, note_id, "confirmed")
            else:
                counts["ambiguous"] += 1
                log_progress(logger, i, total, note_id, "ambiguous", "more than one candidate, left for manual review")

        except Exception as exc:
            counts["error"] += 1
            logger.error(f"confirm --auto-single failed for note {note_id}", exc_info=True)
            log_progress(logger, i, total, note_id, "error", str(exc))

    log_summary(logger, total=total, **counts)
    db.close()
    return counts
