import json
import pprint
import requests
from json import JSONDecodeError
from functools import wraps
from urllib.parse import parse_qs

from .logger import get_logger
from addons.review_grammar.src.config.config_loader import logger_config


logger = get_logger(__name__)


def logging_request(res: requests.Response) -> None:
    """
    Логирует заголовки и тело http запроса
    :param res: requests.Response
    :return: None
    """

    method = res.request.method
    url = res.request.url
    headers = res.request.headers
    body = res.request.body
    body_sep = ""

    if logger_config.log_req_headers:
        log_headers = "Request headers:\n{\n"

        for keys, values in headers.items():
            log_headers += f"\t{keys}: {values}\n"
        log_headers += "}"

        logger.debug(log_headers)

    log_request = f"Request method: {method}, url: {url}"

    if body is not None:
        content_type = headers.get("Content-Type")

        try:
            json_body = None

            match content_type:
                case "application/x-www-form-urlencoded":
                    parsed_body = {k: v[0] if v else "" for k, v in parse_qs(body).items()}
                    json_body = json.dumps(parsed_body, indent=4, ensure_ascii=False)
                case "application/json":
                    json_body = json.dumps(json.loads(body.decode("utf-8")), indent=4, ensure_ascii=False)

            if len(body) > 20:
                body_sep = "\n"

            log_request += f", body: {body_sep}{json_body or pprint.pformat(body)}"

        except (AttributeError, JSONDecodeError):
            log_request += f", body: {body}"

    logger.debug(log_request)


def logging_response(res: requests.Response) -> None:
    """
    Логирует заголовки и тело http ответа
    :param res: requests.Response
    :return: None
    """

    method = res.request.method
    url = res.request.url
    status = res.status_code
    headers = res.headers
    body = None

    try:
        body = res.json()
    except Exception as e:
        logger.debug(f"Got exception when trying to parse response body: {e}")
        logger.debug(f"Response body is not json: {res.content}")

    if logger_config.log_resp_headers:

        log_headers = "Response headers:\n{\n"

        for keys, values in headers.items():
            log_headers += f"\t{keys}: {values}\n"
        log_headers += "}"

        logger.debug(log_headers)

    log_response = f"Response method: {method}, url: {url}, status: {status}"

    if body is not None:
        try:
            if len(res.content) > 20:
                body_sep = "\n"
                bd = json.dumps(body, indent=4, ensure_ascii=False)
                log_response += f", body: {body_sep}{bd}"
            else:
                log_response += f", body: {json.dumps(body)}"
        except JSONDecodeError:
            if len(res.text) > 120:
                log_response += f", body: {res.text[:120]}..."
            else:
                log_response += f", body: {res.text}"
    else:
        log_response += " No Content"
    logger.debug(log_response)


def logging(message):
    def wrapper(function):
        @wraps(function)
        def inner(*args, **kwargs):
            logger.info(message)

            res = function(*args, **kwargs)

            logging_request(res)
            logging_response(res)

            return res

        return inner

    return wrapper
