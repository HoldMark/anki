import re
import random
import time


def remove_space_tabs(input_str: str) -> str:
    match = re.search(r'\(.*?\)', input_str)
    return match.group(0) if match else ""


def remove_colon(input_str: str) -> str:
    if ': ' in input_str:
        return input_str[:-2]
    return input_str


def remove_symbols(str_ws):
    str_wos = ''

    for sym in str_ws:
        if sym.isalpha():
            str_wos += sym

    return str_wos


def sleep_rand_time(min_sec=1, max_sec=5, log=True):
    secs = random.randint(min_sec, max_sec) + random.random()

    if log:
        print(f'sleep for: {round(secs, 2)}s.')

    time.sleep(secs)
    return secs
