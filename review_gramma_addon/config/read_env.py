import os
from pathlib import Path


current_file = Path(__file__)
ROOT_DIR = current_file.parent.parent
env_path = ROOT_DIR / ".env"


def load_env(file_path):
    with open(file_path, "r") as f:
        for line in f:
            line = line.strip()
            if line and not line.startswith("#"):
                key, value = line.split("=", 1)
                os.environ[key] = value


load_env(env_path)
GOOGLE_API_KEY = os.environ.get("goog-api-key")
