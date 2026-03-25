from aqt import gui_hooks, mw
from PyQt6.QtCore import QTimer


FREEZE_MS = 1000


def _get_allowed_decks() -> list[str]:
    config = mw.addonManager.getConfig(__name__)
    if not config:
        return []
    return config.get("decks", [])


_is_frozen = False
_penalty_served = False


def _disable_buttons(reviewer) -> None:
    reviewer.bottom.web.eval(
        "document.querySelectorAll('.ease').forEach(b => {"
        "  b.disabled = true;"
        "  b.style.opacity = '0.4';"
        "});"
    )


def _enable_buttons(reviewer) -> None:
    reviewer.bottom.web.eval(
        "document.querySelectorAll('.ease').forEach(b => {"
        "  b.disabled = false;"
        "  b.style.opacity = '1';"
        "});"
    )


def on_will_answer_card(handled, reviewer, card):  # noqa
    global _is_frozen, _penalty_served

    proceed, ease = handled

    if not proceed:
        return handled

    # Штраф уже отбыт — пропускаем без заморозки
    if _penalty_served:
        return handled

    # Заморозка уже идёт — блокируем повторное нажатие
    if _is_frozen:
        return False, ease

    # Фильтрация по колодам из конфига
    allowed = _get_allowed_decks()
    if allowed:
        deck_name = mw.col.decks.name(card.did)
        if not any(deck_name == d or deck_name.startswith(d + "::") for d in allowed):
            return handled

    # Только для карточек с {{type:FieldName}}
    if reviewer.typeCorrect is None:
        return handled

    typed = (reviewer.typedAnswer or "").strip()
    correct = reviewer.typeCorrect.strip()

    if typed.lower() == correct.lower() or ease == 1:
        return handled  # ответ верный или Again — не замораживаем

    # Ответ неверный — блокируем кнопки на FREEZE_MS мс, затем ждём нового нажатия
    _is_frozen = True
    _disable_buttons(reviewer)

    def resume() -> None:
        global _is_frozen, _penalty_served
        _is_frozen = False
        _penalty_served = True
        _enable_buttons(reviewer)

    QTimer.singleShot(FREEZE_MS, resume)
    return False, ease


def on_show_question(card) -> None:  # noqa
    global _is_frozen, _penalty_served
    _is_frozen = False
    _penalty_served = False


gui_hooks.reviewer_will_answer_card.append(on_will_answer_card)
gui_hooks.reviewer_did_show_question.append(on_show_question)
