import spacy

_nlp = None


def _get_nlp():
    global _nlp
    if _nlp is None:
        _nlp = spacy.load("en_core_web_sm")
    return _nlp


def lemmatize(text: str) -> list[str]:
    """Return the base form of each word in text.

    Examples:
        lemmatize("cats")          → ["cat"]
        lemmatize("was running")   → ["be", "run"]
    """
    nlp = _get_nlp()
    doc = nlp(text)
    return [token.lemma_ for token in doc if not token.is_space]
