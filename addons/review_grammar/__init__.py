import json

from aqt import gui_hooks

from .src.llm.gemini import gemini_client
from .src.data.parse_data import DataToReview
from .src.core.create_task import create_task
from .src.utils.logs.logger import get_logger
from .src.data.base_request_data import get_base_request_data

logger = get_logger("init")


def task_router(handled, message, context):
    """Получение данных из JS и обработка их в Python"""
    if handled[0]:
        return handled

    try:
        data = json.loads(message)
    except Exception:
        return handled  # пробрасываем дальше

    action = data.pop("action")

    if action == "task_for_card_with_eng_word":
        result = create_task(**data)
        if hasattr(context, "web"):
            context.web.eval(f"receiveTask({json.dumps(result)});")
        return True, None

    if action == "check grammar and other":
        logger.info("Received data to review from JS")
        logger.debug(f"Received data: {data}")

        data_to_review = DataToReview(**data)
        data = get_base_request_data(data_to_review.dict_view())
        content = gemini_client.generate_content(data)

        if content == "Got an error":
            text_json = {"result": "Error"}
        else:
            text_raw = content["candidates"][0]["content"]["parts"][0]["text"]
            text_json = json.loads(text_raw)

        if hasattr(context, "web"):
            result = json.dumps(text_json)
            logger.info("Sending review response to JS")
            logger.debug(f"Review response: {result}")
            context.web.eval(f"receiveReviewResponse({result});")

        return True, None

    return handled


gui_hooks.webview_did_receive_js_message.append(task_router)
