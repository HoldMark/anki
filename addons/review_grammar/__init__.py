import json

from aqt import gui_hooks

from .src.core.create_task import create_task
from .src.core.review_task import review_task
from .src.utils.logs.logger import get_logger

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
        logger.info("Action: create task")
        result = create_task(data)

        if hasattr(context, "web"):
            context.web.eval(f"receiveTask({json.dumps(result)});")

        return True, None

    if action == "check grammar and other":
        logger.info("Action: review task")
        result = review_task(data)

        if hasattr(context, "web"):
            context.web.eval(f"receiveReviewResponse({json.dumps(result)});")

        return True, None

    return handled


gui_hooks.webview_did_receive_js_message.append(task_router)
