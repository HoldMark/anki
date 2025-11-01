from .base_response_mobel import BaseResponseModel


class ReviewResponseModel(BaseResponseModel):
    text: str
    is_word: bool
    is_part_of_speech: bool
    is_definition: bool
    is_tense: bool
    is_usage: bool
    is_sentence_type: bool
    is_pronoun: bool
    correct_version: str
    grammar_correctness: bool
    errors_with_grammar: list[str]
    style_suggestions: list[str]
    explanation_of_text: str
