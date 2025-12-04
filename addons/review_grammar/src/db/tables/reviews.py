import textwrap

from ._table import Table


class ReviewsTable(Table):
    _CREATION_QUERY = textwrap.dedent("""
        CREATE TABLE IF NOT EXISTS reviews (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            word_id INTEGER,
            condition_id INTEGER,
            is_word INTEGER DEFAULT 0,
            is_pos INTEGER DEFAULT 0,
            is_definition INTEGER DEFAULT 0,
            grammar_correctness INTEGER DEFAULT 0,
            grammar_errors TEXT,
            style_suggestions TEXT,
            full_text TEXT,
            created_at TIMESTAMP NOT NULL,
            FOREIGN KEY (word_id) REFERENCES words(id),
            FOREIGN KEY (condition_id) REFERENCES conditions(id)
        );
    """)

    _INSERT_QUERY = textwrap.dedent("""
        INSERT INTO reviews (
            word_id, condition_id, is_word, is_pos, is_definition, grammar_correctness,
            grammar_errors, style_suggestions, full_text, created_at
        ) VALUES (
            :word_id, :condition_id, :is_word, :is_pos, :is_definition, :grammar_correctness,
            :grammar_errors, :style_suggestions, :full_text, :created_at
        );
    """)

    _GET_ALL_QUERY = textwrap.dedent("""
        SELECT * FROM reviews;
    """)

    _GET_ALL_FULL_REVIEWS_QUERY = textwrap.dedent("""
        SELECT
            r.id,
            w.word,
            w.definition,
            w.pos,
            c.tense,
            c.usage,
            c.sentence_type,
            c.pronoun,
            r.is_word,
            r.is_pos,
            r.is_definition,
            r.grammar_correctness,
            r.grammar_errors,
            r.style_suggestions,
            r.full_text,
            r.created_at
        FROM reviews AS r
        JOIN words AS w ON r.word_id = w.id
        JOIN conditions AS c ON r.condition_id = c.id;
    """)

    def add(self, data: dict) -> int | None:
        """Add a new review to the database and return the id of the new row."""
        data["created_at"] = self.timestamp
        return self._db.execute(self._INSERT_QUERY, data)

    def all(self) -> list[dict] | None:
        """Return all reviews in the database."""
        return self._db.query(self._GET_ALL_QUERY)

    def all_full_reviews(self) -> list[dict] | None:
        """Return all reviews in the database."""
        return self._db.query(self._GET_ALL_FULL_REVIEWS_QUERY)
