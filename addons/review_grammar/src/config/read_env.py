import os

from ..utils.path import ROOT_PATH

env_path = ROOT_PATH / ".env"


def load_env(file_path):
    with open(file_path) as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key] = value


load_env(env_path)
GOOGLE_API_KEY = os.environ.get("goog-api-key")
