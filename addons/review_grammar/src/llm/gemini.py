from json import JSONDecodeError

import requests
from requests import Response

from ..utils.logs.api import logging as log
from ..config.read_env import GOOGLE_API_KEY
from ..utils.logs.logger import get_logger

logger = get_logger(__name__)


class GeminiClient:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/"
    MODELS = [
        "gemini-2.5-flash",
        "gemini-2.5-flash-lite",
        "gemini-2.0-flash",
    ]
    ERROR = "Got an error"
    RATE_LIMIT_ERROR = "Rate limit exceeded"

    def __init__(self):
        self._model_index = 0

    @property
    def current_model(self) -> str:
        return self.MODELS[self._model_index]

    def _switch_to_next_model(self) -> bool:
        if self._model_index < len(self.MODELS) - 1:
            self._model_index += 1
            logger.warning(f"Rate limit reached, switching to model: {self.current_model}")
            return True
        logger.error("Rate limit reached on all available models")
        return False

    @log("Request (Gemini)")
    def _request(self, data: dict, url: str, headers: dict) -> Response:
        return requests.post(url=url, headers=headers, json=data)

    def _do_request(self, data: dict, model: str):
        url = self.URL + model + ":generateContent"
        result = self._request(data, url=url, headers=self.headers)

        if result.status_code == 429:
            logger.warning(f"Rate limit (429) for model: {model}")
            return None

        if result.status_code != 200:
            return self.ERROR

        try:
            return result.json()
        except JSONDecodeError:
            return self.ERROR

    def generate_content(self, data: dict):
        while True:
            result = self._do_request(data, self.current_model)
            if result is not None:
                return result
            if not self._switch_to_next_model():
                return self.RATE_LIMIT_ERROR

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": GOOGLE_API_KEY,
            "user-agent": "google-genai-sdk/1.43.0 gl-python/3.12.3",
            "x-goog-api-client": "google-genai-sdk/1.43.0 gl-python/3.12.3",
        }


gemini_client = GeminiClient()
