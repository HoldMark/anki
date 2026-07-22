import textwrap

import pytest

from src.db.database import Database
from src.db.tables._table import Table


class _DummyTable(Table):
    NAME = "dummy"
    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS dummy (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            value TEXT
        );
    """)


@pytest.fixture
def db(tmp_path):
    database = Database(str(tmp_path / "dummy.sqlite"))
    yield database
    database.close()


def test_execute_insert_returns_real_lastrowid_not_a_placeholder(db):
    """
    Regression test: Database.execute() must return cursor.lastrowid for INSERT statements.
    A textwrap.dedent()'d multi-line query starts with a leading '\\n', so a naive
    sql.startswith("INSERT") check is always False and silently falls back to a generic
    success indicator (1) instead of the real row id — this was a real bug found and fixed
    while building this project, carried over from the grammar_drill addon it was copied from.
    """
    table = _DummyTable(db)
    assert db.create_tables([table]) is True

    first_id = db.execute("INSERT INTO dummy (value) VALUES (:value);", {"value": "a"})
    second_id = db.execute("INSERT INTO dummy (value) VALUES (:value);", {"value": "b"})

    assert first_id == 1
    assert second_id == 2  # would incorrectly also be 1 (or None) if the bug regressed


def test_query_returns_list_of_dicts(db):
    table = _DummyTable(db)
    db.create_tables([table])
    db.execute("INSERT INTO dummy (value) VALUES ('x');")

    rows = db.query("SELECT * FROM dummy;")
    assert rows == [{"id": 1, "value": "x"}]


def test_query_on_bad_sql_returns_none_not_an_exception(db):
    assert db.query("SELECT * FROM table_that_does_not_exist;") is None


def test_execute_on_bad_sql_returns_none_not_an_exception(db):
    assert db.execute("INSERT INTO table_that_does_not_exist (x) VALUES (1);") is None


def test_are_tables_created_true_after_create(db):
    table = _DummyTable(db)
    assert db.create_tables([table]) is True
    assert db.are_tables_created([table]) is True
