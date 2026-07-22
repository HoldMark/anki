from src.utils.hashing import CONTENT_FIELDS, compute_content_hash


def _fields(**overrides) -> dict:
    base = {name: "" for name in CONTENT_FIELDS}
    base.update(overrides)
    return base


def test_same_content_produces_same_hash():
    a = compute_content_hash(_fields(word="thick", definition="stupid"))
    b = compute_content_hash(_fields(word="thick", definition="stupid"))
    assert a == b


def test_different_content_produces_different_hash():
    a = compute_content_hash(_fields(word="thick", definition="stupid"))
    b = compute_content_hash(_fields(word="thick", definition="not flowing easily"))
    assert a != b


def test_empty_string_and_missing_key_hash_the_same():
    """A field that's '' and a field that's absent from the dict must normalize identically."""
    with_empty = _fields(word="thick", definition="")
    missing = {k: v for k, v in _fields(word="thick").items() if k != "definition"}
    assert compute_content_hash(with_empty) == compute_content_hash(missing)


def test_none_and_empty_string_hash_the_same():
    a = compute_content_hash(_fields(word="thick", cefr=""))
    b = compute_content_hash(_fields(word="thick", cefr=None))
    assert a == b


def test_field_boundary_does_not_silently_collide():
    """Concatenation without a placeholder could let 'ab'+'' collide with 'a'+'b' across a field boundary."""
    a = compute_content_hash(_fields(word="ab", trans=""))
    b = compute_content_hash(_fields(word="a", trans="b"))
    assert a != b


def test_returns_hex_sha256():
    digest = compute_content_hash(_fields(word="thick"))
    assert len(digest) == 64
    assert all(c in "0123456789abcdef" for c in digest)
