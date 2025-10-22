# /Users/markprodius/staff/anki/check_gramma_addon/libs/google/genai/_api_client.py

import urllib.request
import json


class GeminiClient:
    URL = "https://generativelanguage.googleapis.com/v1beta/models/"
    BASEMODEL = "gemini-2.5-flash"

    def generate_content(self, data: dict):
        data = json.dumps(data).encode("utf-8")
        print(f"data: {data}")
        req = urllib.request.Request(
            url=self.URL + self.BASEMODEL + ":generateContent",
            data=data,
            headers=self.headers,
            method="POST"
        )

        # Отправляем и читаем ответ
        with urllib.request.urlopen(req) as response:
            body = response.read().decode("utf-8")
            headers = response.headers
            status_code = response.status
            
            print(f"body: {body}")
            print(f"headers: {headers}")
            print(f"status_code: {status_code}")

            return json.loads(body)

    @property
    def headers(self):
        return {
                'Content-Type': 'application/json',
                'x-goog-api-key': "AIzaSyCzunUhJnQ-0QhCXZOD166ms0Zn5Lc58FE", 
                'user-agent': 'google-genai-sdk/1.43.0 gl-python/3.12.3', 
                'x-goog-api-client': 'google-genai-sdk/1.43.0 gl-python/3.12.3'
            }


gemini_client = GeminiClient()
