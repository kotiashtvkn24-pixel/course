import os
from dataclasses import dataclass
from functools import lru_cache

from dotenv import load_dotenv


@dataclass(frozen=True)
class Settings:
    bot_token: str
    owner_id: int
    api_id: int
    api_hash: str
    webapp_url: str
    db_path: str
    session_path: str
    timezone: str
    host: str
    port: int


def _required(name: str) -> str:
    value = os.getenv(name, "")
    if not value:
        raise RuntimeError(f"{name} is not set")
    return value


@lru_cache(maxsize=1)
def get_settings() -> Settings:
    load_dotenv()
    return Settings(
        bot_token=_required("BOT_TOKEN"),
        owner_id=int(_required("OWNER_ID")),
        api_id=int(_required("API_ID")),
        api_hash=_required("API_HASH"),
        webapp_url=os.getenv("WEBAPP_URL", ""),
        db_path=os.getenv("DB_PATH", "greetings.db"),
        session_path=os.getenv("SESSION_PATH", "account"),
        timezone=os.getenv("TIMEZONE", "Europe/Kyiv"),
        host=os.getenv("HOST", "0.0.0.0"),
        port=int(os.getenv("PORT", "8000")),
    )
