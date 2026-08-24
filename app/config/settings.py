import os

from pathlib import Path

from dotenv import load_dotenv


BASE_DIR = Path(
    __file__
).resolve().parents[2]


ENV_FILE = BASE_DIR / ".env"


load_dotenv(
    dotenv_path=ENV_FILE
)


# ==========================================
# GEMINI
# ==========================================

GEMINI_API_KEY = os.getenv(
    "GEMINI_API_KEY"
)

GEMINI_MODEL = os.getenv(
    "GEMINI_MODEL",
    "gemini-3.5-flash"
)


# ==========================================
# MYSQL
# ==========================================

DATABASE_URL = os.getenv(
    "DATABASE_URL"
)


# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_BOT_TOKEN = os.getenv(
    "TELEGRAM_BOT_TOKEN"
)

TELEGRAM_CHAT_ID = os.getenv(
    "TELEGRAM_CHAT_ID"
)
# ==========================================
# VALIDATION
# ==========================================

if not GEMINI_API_KEY:

    raise ValueError(
        "GEMINI_API_KEY is missing"
    )


if not DATABASE_URL:

    raise ValueError(
        "DATABASE_URL is missing"
    )


if not TELEGRAM_BOT_TOKEN:

    raise ValueError(
        "TELEGRAM_BOT_TOKEN is missing"
    )


if not TELEGRAM_CHAT_ID:

    raise ValueError(
        "TELEGRAM_CHAT_ID is missing"
    )