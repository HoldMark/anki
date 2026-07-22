import hashlib

CONTENT_FIELDS = [
    "word",
    "trans",
    "trans_type",
    "part_of_speech",
    "sense",
    "definition",
    "cefr",
    "example_1",
    "example_2",
    "example_3",
    "example_4",
    "example_5",
    "example_6",
    "example_7",
    "audio",
    "picture",
    "video",
    "hints",
]


def _normalize(value: str | None) -> str:
    return value if value else "∅"


def compute_content_hash(fields: dict) -> str:
    """
    Computes a sha256 hash over an Anki note's human-owned content fields.
    Excludes _system_hash/_system_note_uuid (self-referential) and Anki metadata (note id, mod time).
    """
    raw = "".join(_normalize(fields.get(name)) for name in CONTENT_FIELDS)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()
