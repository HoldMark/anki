import json
import urllib.request

from .config.read_env import GOOGLE_API_KEY
from .utils.logs.logger import get_logger


logger = get_logger(__name__)


class GeminiClient:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/"
    BASEMODEL = "gemini-2.5-flash"

    def generate_content(self, data: dict):
        data = json.dumps(data).encode("utf-8")
        logger.debug(f"Got data in generate_content: {data}")
        req = urllib.request.Request(
            url=self.URL + self.BASEMODEL + ":generateContent", data=data, headers=self.headers, method="POST"
        )

        # Отправляем и читаем ответ
        try:
            with urllib.request.urlopen(req) as response:
                body = response.read().decode("utf-8")
                headers = response.headers
                status_code = response.status

                logger.debug(f"body: {body}")
                logger.debug(f"headers: {headers}")
                logger.debug(f"status_code: {status_code}")

                return json.loads(body)
        except Exception as e:
            logger.debug("Got an error while reading the response")
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
