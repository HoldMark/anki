"""
focus_alert — Anki addon that plays a sound when Anki loses focus
(the user switches to another app: browser, Telegram, etc.)
and when a review card stays unanswered for too long.
"""

import os
import sys
import time
import subprocess

from aqt import mw, gui_hooks
from PyQt6.QtCore import Qt, QUrl, QTimer
from PyQt6.QtWidgets import QApplication

SOUND_PATH = os.path.join(os.path.dirname(__file__), "notification.mp3")

_player = None  # QMediaPlayer, created lazily
_audio_output = None  # QAudioOutput, must stay referenced while playing
_last_played = 0.0  # monotonic time of the last alert
_repeats_left = 0  # repeat alerts remaining for the current absence
_repeat_timer = QTimer()
_repeat_timer.timeout.connect(lambda: _on_repeat_timeout())
_idle_alerts_left = 0  # idle alerts remaining for the current card
_idle_timer = QTimer()
_idle_timer.timeout.connect(lambda: _on_idle_timeout())


def _get_config():
    # Read the addon config managed by Anki's addon manager
    return mw.addonManager.getConfig(__name__) or {}


def _init_player() -> bool:
    # Creates the Qt media player; returns False if QtMultimedia is unavailable
    global _player, _audio_output
    if _player is not None:
        return True
    try:
        from PyQt6.QtMultimedia import QAudioOutput, QMediaPlayer
    except ImportError:
        return False
    _audio_output = QAudioOutput()
    _player = QMediaPlayer()
    _player.setAudioOutput(_audio_output)
    _player.setSource(QUrl.fromLocalFile(SOUND_PATH))
    return True


def _play_sound(volume: float):
    # Plays the alert via QtMultimedia, falls back to afplay on macOS
    if _init_player():
        _audio_output.setVolume(volume)
        _player.stop()
        _player.play()
    elif sys.platform == "darwin":
        subprocess.Popen(["afplay", "-v", str(volume), SOUND_PATH])


def _on_repeat_timeout():
    # Re-alerts while Anki stays unfocused, up to repeat_count times
    global _repeats_left
    config = _get_config()
    _play_sound(float(config.get("volume", 1.0)))
    _repeats_left -= 1
    if _repeats_left <= 0:
        _repeat_timer.stop()


def _on_app_state_changed(state):
    """Fires when the whole application becomes active/inactive."""
    global _last_played, _repeats_left

    if state == Qt.ApplicationState.ApplicationActive:
        _repeat_timer.stop()
        # Back in Anki: idle countdown starts over
        if mw.state == "review":
            _start_idle_timer()
        return

    # Unfocused time is covered by the focus alerts
    _idle_timer.stop()

    # Already alerting for the current absence
    if _repeat_timer.isActive():
        return

    config = _get_config()
    if not config.get("enabled", True):
        return

    # Optionally alert only while a review session is open
    if config.get("only_in_review", False) and mw.state != "review":
        return

    # Debounce: macOS can emit several inactive/hidden states in a row
    # (skips only the sound, repeats are still scheduled)
    now = time.monotonic()
    if now - _last_played >= config.get("cooldown_seconds", 2):
        _last_played = now
        _play_sound(float(config.get("volume", 1.0)))

    _repeats_left = int(config.get("repeat_count", 2))
    if _repeats_left > 0:
        _repeat_timer.start(int(config.get("repeat_interval_seconds", 30) * 1000))


def _start_idle_timer():
    # (Re)starts the "no answer yet" countdown for the current review card
    global _idle_alerts_left
    _idle_timer.stop()
    config = _get_config()
    if not config.get("idle_enabled", True):
        return
    if QApplication.applicationState() != Qt.ApplicationState.ApplicationActive:
        return
    _idle_alerts_left = int(config.get("idle_count", 3))
    if _idle_alerts_left > 0:
        _idle_timer.start(int(config.get("idle_interval_seconds", 30) * 1000))


def _on_idle_timeout():
    # Alerts while the card stays unanswered, up to idle_count times
    global _idle_alerts_left
    if mw.state != "review":
        _idle_timer.stop()
        return
    _play_sound(float(_get_config().get("volume", 1.0)))
    _idle_alerts_left -= 1
    if _idle_alerts_left <= 0:
        _idle_timer.stop()


def _on_show_card(card):
    _start_idle_timer()


def _on_state_change(new_state, old_state):
    if new_state != "review":
        _idle_timer.stop()


def _on_main_window_init():
    QApplication.instance().applicationStateChanged.connect(_on_app_state_changed)


gui_hooks.main_window_did_init.append(_on_main_window_init)
gui_hooks.reviewer_did_show_question.append(_on_show_card)
gui_hooks.reviewer_did_show_answer.append(_on_show_card)
gui_hooks.state_did_change.append(_on_state_change)
