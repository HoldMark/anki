class DataToReview:
    def __init__(self, **kwargs):
        self.word = kwargs["word"]
        self.pos = kwargs["pos"]
        self.definition = kwargs["definition"]
        self.tense = kwargs["tense"]
        self.usage = kwargs["usage"]
        self.sentence_type = kwargs["sentence_type"]
        self.pronoun = kwargs["pronoun"]
        self.text = kwargs["text"]

    def dict_view(self) -> dict:
        return {
            "word": self.word,
            "part of speech": self.pos,
            "definition": self.definition,
            "tense": self.tense,
            "usage": self.usage,
            "sentence type": self.sentence_type,
            "pronoun": self.pronoun,
            "text": self.text,
        }
