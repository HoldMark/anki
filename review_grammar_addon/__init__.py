import json
from aqt import gui_hooks
from .data.parse_data import parse_data
from .data.base_request_data import get_base_request_data
from .gemini_client import gemini_client


def task_router(handled, message, context):
    """Получение данных из JS и обработка их в Python"""
    if handled[0]:
        return handled

    try:
        data = json.loads(message)
    except Exception as e:
        print("Ошибка JSON:", e)
        return handled  # пробрасываем дальше

    if data.pop("action") == "check grammar and other":

        parsed_data = parse_data(**data)
        data = get_base_request_data(parsed_data)
        content = gemini_client.generate_content(data)

        if content == "Got an error":
            text_json = {"result": "Error"}
        else:
            text_raw = content["candidates"][0]["content"]["parts"][0]["text"]
            text_json = json.loads(text_raw)
        
        if hasattr(context, "web"):
            context.web.eval(f'receiveReviewResponse({json.dumps(text_json)});')

        return True, None

    return handled


gui_hooks.webview_did_receive_js_message.append(task_router)
