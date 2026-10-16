"""
new_card_marker — Anki addon that tells card templates the card's scheduling state.

Prepends a hidden marker element to the rendered question/answer HTML during review:
    <div class="card-state card-state-new" data-card-state="new" hidden></div>
States: new, learn, review, relearn. Templates style themselves via CSS `:has()`,
e.g. `#qa:has(> .card-state-new)`. A body class can't be used: the reviewer
resets document.body.className after inserting the card HTML.
"""

from aqt import gui_hooks
from anki.cards import Card
from anki.consts import CARD_TYPE_LRN, CARD_TYPE_NEW, CARD_TYPE_REV, CARD_TYPE_RELEARNING

_STATES = {
    CARD_TYPE_NEW: "new",
    CARD_TYPE_LRN: "learn",
    CARD_TYPE_REV: "review",
    CARD_TYPE_RELEARNING: "relearn",
}


def _on_card_will_show(text: str, card: Card, kind: str) -> str:
    # Only the reviewer: previews/browser show cards outside of a study session
    if kind not in ("reviewQuestion", "reviewAnswer"):
        return text
    state = _STATES.get(card.type)
    if state is None:
        return text
    marker = f'<div class="card-state card-state-{state}" data-card-state="{state}" hidden></div>'
    return marker + text


gui_hooks.card_will_show.append(_on_card_will_show)
