import os
import sys
import logging
from logging import Formatter, StreamHandler
from logging.handlers import RotatingFileHandler

from src.utils.path import LOGS_PATH

_FORMAT = "# {levelname:<8} | {asctime}.{msecs:03.0f} | {name:<15} | {lineno:^4} | {message}"
_DATEFMT = "%d.%m.%Y %H:%M:%S"

_formatter = Formatter(fmt=_FORMAT, datefmt=_DATEFMT, style="{")

os.makedirs(LOGS_PATH, exist_ok=True)

_stream_handler = StreamHandler(stream=sys.stdout)
_stream_handler.setFormatter(_formatter)

_file_handler = RotatingFileHandler(filename=str(LOGS_PATH / "sync.log"), mode="a", maxBytes=500_000, backupCount=2)
_file_handler.setFormatter(_formatter)


def get_logger(name: str) -> logging.Logger:
    logger = logging.getLogger(name)
    logger.propagate = False

    if not logger.hasHandlers():
        logger.setLevel(logging.DEBUG)
        logger.addHandler(_stream_handler)
        logger.addHandler(_file_handler)

    return logger


def log_progress(
    logger: logging.Logger, current: int, total: int, note_id: int, outcome: str, detail: str = ""
) -> None:
    """Logs one batch-progress line: [i/total] (pct%) note <id>: outcome — detail"""
    percent = (current / total * 100) if total else 0
    message = f"[{current}/{total}] ({percent:.0f}%) note {note_id}: {outcome}"
    if detail:
        message += f" — {detail}"
    logger.info(message)


def log_summary(logger: logging.Logger, **counts: int) -> None:
    """Logs a final summary line, e.g. log_summary(logger, total=10, created=2, updated=3, unchanged=4, error=1)."""
    summary = ", ".join(f"{key}={value}" for key, value in counts.items())
    logger.info(f"Summary: {summary}")
