import json

from ..llm.gemini import gemini_client
from ..data.parse_data import DataToReview
from ..utils.logs.func import log
from ..data.base_request_data import get_base_request_data


@log
def review_task(data: dict) -> dict:
    data_to_review = DataToReview(**data)
    data = get_base_request_data(data_to_review.dict_view())
    content = gemini_client.generate_content(data)

    result = {"result": "Error"}

    if content != "Got an error":
        raw_text = content["candidates"][0]["content"]["parts"][0]["text"]
        result = json.loads(raw_text)

    return result
