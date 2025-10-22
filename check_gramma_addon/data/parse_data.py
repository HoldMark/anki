def parse_data(**kwargs):
    data = {
        "word": kwargs["word"],
        "part of speech": kwargs["pos"],
        "definition": kwargs["definition"],
        "tense": kwargs["tense"],
        "usage": kwargs["usage"],
        "sentence type": kwargs["sentence_type"],
        "pronoun": kwargs["card_pronoun"],
        "text": kwargs["sentence"],
    }
    return data
