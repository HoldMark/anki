from .base_response_mobel import BaseResponseModel


class ReviewResponseModel(BaseResponseModel):
    text: str = None
    is_word: bool = None
    is_part_of_speech: bool = None
    is_definition: bool = None
    is_tense: bool = None
    is_usage: bool = None
    is_sentence_type: bool = None
    is_pronoun: bool = None
    correct_version: str = None
    grammar_correctness: bool = None
    errors_with_grammar: list[str] = None
    style_suggestions: list[str] = None
    explanation_of_text: str = None

    def __init__(self, **data):
        for key, value in data.items():
            setattr(self, key, value)
