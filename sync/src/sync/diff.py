"""diff: shared before/after review helper, used by pull and enrich."""


def compute_diff(old: dict | None, new: dict, fields: list[str]) -> dict[str, tuple]:
    """Returns {field: (old_value, new_value)} for every field in `fields` whose value differs."""
    changes = {}

    for field in fields:
        old_value = old.get(field) if old else None
        new_value = new.get(field)
        if old_value != new_value:
            changes[field] = (old_value, new_value)

    return changes


def format_diff(changes: dict[str, tuple]) -> str:
    """Human-readable one-line summary of a diff, e.g. 'definition: None -> \"stupid\"'."""
    return ", ".join(f"{field}: {old!r} -> {new!r}" for field, (old, new) in changes.items())


def confirm_diff(note_id: int, changes: dict[str, tuple]) -> bool:
    """Prints a note's proposed changes and prompts for confirmation. Returns True to proceed."""
    if not changes:
        return True

    print(f"\nNote {note_id} — proposed changes:")
    for field, (old, new) in changes.items():
        print(f"  {field}: {old!r} -> {new!r}")

    answer = input("Apply? [y/N]: ").strip().lower()
    return answer in ("y", "yes")
