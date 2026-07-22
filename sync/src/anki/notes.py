"""Чтение и изменение записей (notes) через AnkiConnect."""

from src.anki_client import invoke


def get_notes(deck: str, query: str | None = None, limit: int | None = None) -> list[int]:
    """
    Id записей в колоде (включая её подколоды — так работает Anki-поиск по deck:).

    query: дополнительные условия Anki-поиска, объединяются через AND с фильтром по колоде,
           например 'tag:leech', 'is:due'.
    limit: ограничить количество id (сначала самые новые записи).
    """
    search = f'deck:"{deck}"'
    if query:
        search += f" {query}"
    note_ids = invoke("findNotes", query=search)
    note_ids.sort(reverse=True)
    if limit is not None:
        note_ids = note_ids[:limit]
    return note_ids


def get_notes_fields(note_ids: list[int]) -> dict[int, dict[str, str]]:
    """Имя поля -> значение поля (HTML) для каждой записи, за один запрос к Anki."""
    infos = invoke("notesInfo", notes=note_ids)
    result = {}
    for note_id, info in zip(note_ids, infos, strict=True):
        result[note_id] = {name: field["value"] for name, field in info["fields"].items()} if info else {}
    return result


def update_note_fields(note_id: int, fields: dict[str, str]) -> None:
    """Перезаписывает указанные поля существующей записи; остальные поля не трогает."""
    invoke("updateNoteFields", note={"id": note_id, "fields": fields})


def get_notes_missing_uuid(deck: str) -> list[int]:
    """Id записей в колоде, у которых поле _system_note_uuid пустое (ещё не проштампованы)."""
    return get_notes(deck, query='"_system_note_uuid:"')
