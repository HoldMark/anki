"""
error_freeze — Anki addon that temporarily freezes rating buttons
when the user types a wrong answer on a {{type:FieldName}} card.
After the freeze expires, the user picks the rating themselves.
"""
import anki.buildinfo

from aqt import gui_hooks, mw
from PyQt6.QtCore import QTimer


# Duration of the button freeze in milliseconds
FREEZE_MS = 1000


def _get_config():
    # Read the addon config managed by Anki's addon manager
    return mw.addonManager.getConfig(__name__) or {}


def _get_allowed_decks() -> list[str]:
    # Returns the list of deck names the freeze applies to (empty = all decks)
    return _get_config().get("decks", [])


def _version_check_enabled() -> bool:
    # Returns whether the Anki version check is active
    return _get_config().get("check_version", True)


def _is_supported_version() -> bool:
    # Returns True if the current Anki version is in required_versions,
    # or if the version check is disabled, or if required_versions is empty
    if not _version_check_enabled():
        return True
    required = _get_config().get("required_versions", [])
    return not required or anki.buildinfo.version in required


# State flags shared across hook calls for the current card
_is_frozen = False       # True while the freeze timer is running
_penalty_served = False  # True after the freeze has ended, until the next card


def _disable_buttons(reviewer) -> None:
    # Visually disable all ease buttons via JS
    reviewer.bottom.web.eval(
        "document.querySelectorAll('.ease').forEach(b => {"
        "  b.disabled = true;"
        "  b.style.opacity = '0.4';"
        "});"
    )


def _enable_buttons(reviewer) -> None:
    # Re-enable all ease buttons via JS
    reviewer.bottom.web.eval(
        "document.querySelectorAll('.ease').forEach(b => {"
        "  b.disabled = false;"
        "  b.style.opacity = '1';"
        "});"
    )


def on_will_answer_card(handled, reviewer, card):  # noqa
    """Hook: fires before Anki records the user's rating.

    Intercepts wrong-answer submissions on typing cards and starts a freeze:
    buttons are disabled for FREEZE_MS ms, then re-enabled so the user can
    pick a rating themselves.
    """
    global _is_frozen, _penalty_served

    proceed, ease = handled

    if not proceed:
        return handled

    # Skip if running on an unsupported Anki version
    if not _is_supported_version():
        return handled

    # Penalty already served — let the rating through without a new freeze
    if _penalty_served:
        return handled

    # Freeze in progress — block repeated clicks
    if _is_frozen:
        return False, ease

    # Filter by decks specified in config
    allowed = _get_allowed_decks()
    if allowed:
        deck_name = mw.col.decks.name(card.did)
        if not any(deck_name == d or deck_name.startswith(d + "::") for d in allowed):
            return handled

    # Only for cards with {{type:FieldName}} field
    if reviewer.typeCorrect is None:
        return handled

    typed = (reviewer.typedAnswer or "").strip()
    correct = reviewer.typeCorrect.strip()

    if typed.lower() == correct.lower() or ease == 1:
        return handled  # correct answer or Again — no freeze

    # Wrong answer — disable buttons for FREEZE_MS ms, then wait for user to re-rate
    _is_frozen = True
    _disable_buttons(reviewer)

    def resume() -> None:
        # Unfreeze after the timer fires and allow the user to pick a rating
        global _is_frozen, _penalty_served
        _is_frozen = False
        _penalty_served = True
        _enable_buttons(reviewer)

    QTimer.singleShot(FREEZE_MS, resume)
    return False, ease


def on_show_question(card) -> None:  # noqa
    # Reset freeze state when a new card is shown
    global _is_frozen, _penalty_served
    _is_frozen = False
    _penalty_served = False


gui_hooks.reviewer_will_answer_card.append(on_will_answer_card)
gui_hooks.reviewer_did_show_question.append(on_show_question)
