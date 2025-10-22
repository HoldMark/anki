import random
from datetime import datetime
from .english_data import tenses, usages, sentence_types, pronouns, obsidian_links



def string_to_number(s: str) -> int:
    r = 0
    for i in s:
        r += ord(i)
    return r


def create_task(**kwargs) -> dict:

    word = kwargs["word"]
    pos = kwargs["pos"]
    definition = kwargs["definition"]

    # create a seed
    today = datetime.today()
    day = today.day
    month = today.month

    seed = string_to_number(word) + string_to_number(definition) + day + month
    random.seed(seed)

    # tenses
    key_tenses = list(tenses.keys())
    value_tenses = list(tenses.values())
    res_tense = random.choices(key_tenses, weights=value_tenses, k=1)[0]
    res_obsidian_link = obsidian_links[res_tense]

    # sentence types & usages
    type_or_usage = random.choice([True, False])
    if type_or_usage:
        stk = list(sentence_types.keys())
        stv = list(sentence_types.values())
        res_sentence_type = random.choices(stk, weights=stv, k=1)[0]
        res_usage = None
    else:
        ku = list(usages[res_tense].keys())
        vu = list(usages[res_tense].values())
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
        "tense": res_tense,
        "obsidian_link": res_obsidian_link,
    }

    return res
