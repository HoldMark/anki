import json
from .models import ReviewResponseModel
from .prompts import check_grammar



def get_base_request_data(text) -> dict:
    request_data = {
        "contents": [
            {
                "parts": [
                    {
                        "text": json.dumps(text)
                    }
                ],
                "role": "user"
            }
        ],
        "systemInstruction": {
            "parts": [
                {
                    "text": check_grammar,
                }
            ],
            "role": "user"
        },
        "generationConfig": {
            "responseMimeType": "application/json",
            **ReviewResponseModel.schema(),
        }
    }
    return request_data
