"""HTTP-клиент для JSON-RPC API аддона AnkiConnect (addons/anki_connect)."""

import json
import urllib.error
import urllib.request

from src.config.load_env import get_config

ANKI_CONNECT_VERSION = 6


class AnkiConnectError(RuntimeError):
    """Ошибка запроса к AnkiConnect (сеть недоступна или action вернул error)."""


def invoke(action: str, **params) -> object:
    """
    Вызывает action AnkiConnect и возвращает result, либо бросает AnkiConnectError.

    Требует запущенный Anki с установленным аддоном anki_connect (слушает на ANKI_CONNECT_URL).
    """
    url = get_config().anki_connect_url
    payload = json.dumps({"action": action, "version": ANKI_CONNECT_VERSION, "params": params}).encode("utf-8")
    request = urllib.request.Request(url, data=payload, headers={"Content-Type": "application/json"})
    try:
        with urllib.request.urlopen(request) as response:
            body = json.loads(response.read().decode("utf-8"))
    except urllib.error.URLError as exc:
        message = f"Не удалось подключиться к AnkiConnect на {url} — Anki запущен? ({exc})"
        raise AnkiConnectError(message) from exc

    if "error" not in body or "result" not in body:
        raise AnkiConnectError(f"Неожиданный формат ответа AnkiConnect: {body}")
    if body["error"] is not None:
        raise AnkiConnectError(body["error"])
    return body["result"]
