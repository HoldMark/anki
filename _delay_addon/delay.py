import time
from aqt import gui_hooks




def sleep():
    time.sleep(3)


gui_hooks.reviewer_did_answer_card.append(sleep)

