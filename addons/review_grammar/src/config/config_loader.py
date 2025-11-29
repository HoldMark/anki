import tomllib

from ..utils.path import ROOT_PATH

with open(ROOT_PATH / "pyproject.toml", "rb") as f:
    data = tomllib.load(f)


class LoggerConfig:
    def __init__(self, config):
        logger_default = config["tool"]["logging"]["default"]

        self.format = {
            "fmt": logger_default["format"],
            "datefmt": logger_default["datefmt"],
            "style": logger_default["style"],
        }

        self.stream: bool = bool(int(logger_default.get("stream", 1)))
        self.log_req_headers: bool = bool(int(logger_default.get("request_headers", 1)))
        self.log_resp_headers: bool = bool(int(logger_default.get("response_headers", 0)))


logger_config = LoggerConfig(config=data)
