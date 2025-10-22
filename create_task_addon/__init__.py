import json
from aqt import gui_hooks
from .create_task import create_task


def task_router(handled, message, context):
    """Получение данных из JS и обработка их в Python"""
    if handled[0]:
        return handled

    try:
        data = json.loads(message)
    except Exception as e:
        print("Ошибка JSON:", e)
        return handled  # пробрасываем дальше

    if data.pop("action") == "task_for_card_with_eng_word":

        result = create_task(**data)
        if hasattr(context, "web"):
            context.web.eval(f'receiveTask({json.dumps(result)});')
        return True, None

    return handled


gui_hooks.webview_did_receive_js_message.append(task_router)
