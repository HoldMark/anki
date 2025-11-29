import os
import sys
import logging

from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

from ...config.config_loader import logger_config
from ..path import LOGS_PATH


formatter = Formatter(**logger_config.format)


def _numbered_namer(default_name: str) -> str:
    """
    Преобразует стандартное имя вида 'name.log.1' в 'name_1.log'
    """
    parts = default_name.rsplit(".", 2)  # разделяем на [name, log, 1]
    if len(parts) == 3 and parts[2].isdigit():
        return f"{parts[0]}_{parts[2]}.log"
    return default_name


# console logs
_stream_handler = StreamHandler(stream=sys.stdout)
_stream_handler.setFormatter(formatter)

# file logs
os.makedirs(LOGS_PATH, exist_ok=True)

# file logs for libs
_root_file_handler = RotatingFileHandler(filename=f"{LOGS_PATH}/libs.log", mode="a", maxBytes=500_000, backupCount=2)
_root_file_handler.setFormatter(formatter)


# file logs for project
_project_file_handler = RotatingFileHandler(
    filename=f"{LOGS_PATH}/project.log", mode="a", maxBytes=500_000, backupCount=2
)
_project_file_handler.setFormatter(formatter)
_project_file_handler.namer = _numbered_namer

# root logger
_root_logger = logging.getLogger()
_root_logger.setLevel(logging.INFO)

logger_config.stream and _root_logger.addHandler(_stream_handler)  # stream logs if enabled
_root_logger.addHandler(_root_file_handler)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        logger_config.stream and logger.addHandler(_stream_handler)  # stream logs if enabled
        logger.addHandler(_project_file_handler)

    return logger
