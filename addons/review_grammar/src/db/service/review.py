from copy import deepcopy
from ..tables.reviews import ReviewsTable
from ...data.models import ReviewResponseModel


class ReviewService:
    """Service for database operations with reviews"""

    def __init__(self, word_id, condition_id, data: ReviewResponseModel, table: ReviewsTable):
        self.word_id: int = word_id
        self.condition_id: int = condition_id
        self.is_word: int = int(bool(data.is_word))
        self.is_pos: int = int(bool(data.is_part_of_speech))
        self.is_definition: int = int(bool(data.is_definition))
        self.grammar_correctness: int = int(bool(data.grammar_correctness))
        self.grammar_errors: str = "|".join(data.errors_with_grammar)
        self.style_suggestions: str = "|".join(data.style_suggestions)
        self.full_text: str = data.text
        self._table = table

    @property
    def data(self) -> dict:
        """Return review data as dict."""
        data = {}

        for key, value in self.__dict__.items():
            if not key.startswith("_"):
                data[key] = value

        return deepcopy(data)

    def add(self) -> int | None:
        """Add review to database and return its id."""
        result = self._table.add(self.data)
        return result

    def all(self) -> list[dict] | None:
        """Return all reviews from database."""
        return self._table.all()
