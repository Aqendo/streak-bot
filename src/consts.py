from enum import Enum
import os

from dotenv import find_dotenv, load_dotenv

load_dotenv(find_dotenv())
POSTGRES_LOGIN = os.getenv("POSTGRES_LOGIN")
POSTGRES_PASSWORD = os.getenv("POSTGRES_PASSWORD")
POSTGRES_HOST = os.getenv("POSTGRES_HOST")
POSTGRES_DB = os.getenv("POSTGRES_DB")
SQLALCHEMY_ECHO = True if os.getenv("SQLALCHEMY_ECHO") == "true" else False
TIMEOUT_SCOREBOARD_IN_SECONDS = int(os.getenv("TIMEOUT_SCOREBOARD_IN_SECONDS") or 180)
TOKEN = os.getenv("TOKEN")
BASE_REPO = os.getenv("BASE_REPO") or "https://github.com/Aqendo/streak-bot"
SHOW_BASE_REPO_IN_HELP = (
    True if os.getenv("SHOW_BASE_REPO_IN_HELP") == "true" else False
)


class Emoji:
    TICK = "✅"
    CROSS = "❌"
    FIRE = "🔥"
    FORBIDDEN = "🚫"
    BIN = "🗑"
    TROPHY = "🏆"
    OK = "🆗"
    ARROW_RIGHT = "↪️"
