import os

from dotenv import load_dotenv
from pydantic import BaseModel

from src.utils.path import ROOT_PATH

load_dotenv()


class Config(BaseModel):
    anki_connect_url: str
    db_path: str
    deck_name: str
    require_review: bool


def get_config() -> Config:
    return Config(
        anki_connect_url=os.environ.get("ANKI_CONNECT_URL", "http://127.0.0.1:8765"),
        db_path=os.environ.get("DB_PATH", str(ROOT_PATH / "data" / "sync.sqlite")),
        deck_name=os.environ.get("DECK_NAME", "1_english::without_group::definition"),
        require_review=os.environ.get("REQUIRE_REVIEW", "true").lower() == "true",
    )
