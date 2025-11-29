import inspect
from functools import wraps

from .logger import get_logger


logger = get_logger(__name__)


def log(function):
    sig = inspect.signature(function)  # Получаем сигнатуру функции

    @wraps(function)
    def inner(*args, **kwargs):

        bound_args = sig.bind(*args, **kwargs)  # Связываем аргументы с именами параметров
        bound_args.apply_defaults()  # Учитываем значения по умолчанию
        args_line = "\n".join([f"{name}: {value}" for name, value in bound_args.arguments.items()])

        logger.debug(f"Args, kwargs of {function.__name__}:\n{args_line}")
        res = function(*args, **kwargs)
        logger.debug(f"Result of {function.__name__}: {res}")

        return res

    return inner
