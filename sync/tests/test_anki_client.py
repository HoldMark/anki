"""
Tests src/anki_client.py's invoke() in isolation by faking urllib.request.urlopen — never
opens a real socket, never talks to a real AnkiConnect server.
"""

import json
import urllib.error

import pytest

from src.anki_client import AnkiConnectError, invoke


class _FakeResponse:
    def __init__(self, body: dict):
        self._body = json.dumps(body).encode("utf-8")

    def read(self):
        return self._body

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False


def test_invoke_returns_result_on_success(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda request: _FakeResponse({"result": [1, 2, 3], "error": None}))
    assert invoke("findNotes", query="deck:x") == [1, 2, 3]


def test_invoke_raises_on_anki_error_field(monkeypatch):
    monkeypatch.setattr(
        "urllib.request.urlopen", lambda request: _FakeResponse({"result": None, "error": "something broke"})
    )
    with pytest.raises(AnkiConnectError, match="something broke"):
        invoke("findNotes")


def test_invoke_raises_on_unexpected_response_shape(monkeypatch):
    monkeypatch.setattr("urllib.request.urlopen", lambda request: _FakeResponse({"unexpected": "shape"}))
    with pytest.raises(AnkiConnectError):
        invoke("findNotes")


def test_invoke_raises_on_connection_failure(monkeypatch):
    def raise_url_error(request):
        raise urllib.error.URLError("connection refused")

    monkeypatch.setattr("urllib.request.urlopen", raise_url_error)
    with pytest.raises(AnkiConnectError, match="Anki запущен"):
        invoke("findNotes")
