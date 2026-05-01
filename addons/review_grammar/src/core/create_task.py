import random
from datetime import datetime

from ..utils.logs.func import log
from ..data.english_data import usages, pronouns, obsidian_links, weights


def string_to_number(s: str) -> int:
    r = 0
    for i in s:
        r += ord(i)
    return r


@log
def create_task(data: dict) -> dict:
    """
    Create a task for learning English words and grammar.
    """

    word = data["word"]
    # pos = kwargs["pos"]
    definition = data["definition"]

    # create a seed
    today = datetime.today()
    day = today.day
    month = today.month

    seed = string_to_number(word) + string_to_number(definition) + day + month
    random.seed(seed)

    # tense
    tenses = list(weights.keys())
    chances_of_tenses = [i["chance"] for i in weights.values()]
    chosen_tense = random.choices(tenses, weights=chances_of_tenses, k=1)[0]
    res_obsidian_link = obsidian_links[chosen_tense]

    # type_or_usage
    chances_of_type_or_usage = [
        weights[chosen_tense]["usage"],
        weights[chosen_tense]["type"]
    ]
    type_or_usage = random.choices(["usage", "type"], weights=chances_of_type_or_usage, k=1)[0]

    # sentence types & usages
    if type_or_usage == "type":
        stk = list(weights[chosen_tense]["sentence_types"].keys())
        stv = list(weights[chosen_tense]["sentence_types"].values())
        res_sentence_type = random.choices(stk, weights=stv, k=1)[0]
        res_usage = None
    else:
        ku = list(usages[chosen_tense].keys())
        vu = list(usages[chosen_tense].values())
        res_usage = random.choices(ku, weights=vu, k=1)[0]
        res_sentence_type = None

    # pronouns
    pk = list(pronouns.keys())
    pv = list(pronouns.values())
    res_pronoun = random.choices(pk, weights=pv, k=1)[0]

    res = {
        "pronoun": res_pronoun,
        "sentence_type": res_sentence_type,
        "usage": res_usage,
        "tense": chosen_tense,
        "obsidian_link": res_obsidian_link,
    }

    return res
