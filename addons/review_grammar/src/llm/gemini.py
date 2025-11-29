from json import JSONDecodeError

import requests
from requests import Response

from ..config.read_env import GOOGLE_API_KEY
from ..utils.logs.logger import get_logger
from ..utils.logs.api_logs import logging as log

logger = get_logger(__name__)


class GeminiClient:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/"
    BASEMODEL = "gemini-2.5-flash"

    @log("Request (Gemini)")
    def _request(self, data: dict, url: str, headers: dict) -> Response:
        logger.info("Sending request...")
        result = requests.post(
            url=url,
            headers=headers,
            json=data,
        )
        return result

    def generate_content(self, data: dict, model: str = None):
        model = model or self.BASEMODEL
        url = self.URL + model + ":generateContent"

        result = self._request(data, url=url, headers=self.headers)

        try:
            return result.json()
        except JSONDecodeError:
            return "Got an error"

    @property
    def headers(self):
        return {
            "Content-Type": "application/json",
            "x-goog-api-key": GOOGLE_API_KEY,
            "user-agent": "google-genai-sdk/1.43.0 gl-python/3.12.3",
            "x-goog-api-client": "google-genai-sdk/1.43.0 gl-python/3.12.3",
        }


gemini_client = GeminiClient()
