import os
from aqt import mw


from .database import Database

from .tables.words import WordsTable
from .tables.reviews import ReviewsTable
from .tables.conditions import ConditionsTable

from .service.word import WordService
from .service.review import ReviewService
from .service.condition import ConditionService

from ..data.parse_data import DataToReview
from ..data.models import ReviewResponseModel


db_path = "anki.sqlite"

if not __name__ == "__main__":
    addon_path = os.path.join(mw.addonManager.addonsFolder(), "review_task_addon")
    db_path = os.path.join(addon_path, "anki.sqlite")


db = Database(db_path)

word_table = WordsTable(db)
condition_table = ConditionsTable(db)
review_table = ReviewsTable(db)

tables_to_create = [word_table, condition_table, review_table]


def store(data: DataToReview, review: ReviewResponseModel):
    """
    Stores data in the database
    """
    if db.create_tables(tables_to_create) is None:
        return None

    word = WordService(data.word, data.definition, data.pos, word_table)
    word_id = word.add()

    condition = ConditionService(data.tense, data.usage, data.sentence_type, data.pronoun, condition_table)
    condition_id = condition.add()

    review = ReviewService(word_id, condition_id, review, review_table)
    review.add()

    db.close()


if __name__ == "__main__":

    """ Just for local testing """
