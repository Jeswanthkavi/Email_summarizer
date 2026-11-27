import os
from pathlib import Path
from urllib.parse import quote_plus

from dotenv import load_dotenv


BASE_DIR = Path(__file__).resolve().parents[2]
ENV_FILE = BASE_DIR / ".env"

load_dotenv(dotenv_path=ENV_FILE)


def _resolve_project_path(env_var: str, default_rel: str) -> Path:
    """Resolve a path from env relative to BASE_DIR, falling back to default_rel if needed."""
    raw = os.getenv(env_var, "").strip()
    default_path = BASE_DIR / default_rel
    if not raw:
        return default_path
    candidate = Path(raw)
    if not candidate.is_absolute():
        candidate = BASE_DIR / candidate
    if candidate.exists() or not default_path.exists():
        return candidate
    return default_path


# ==========================================
# GEMINI
# ==========================================

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
GEMINI_MODEL = os.getenv("GEMINI_MODEL", "gemini-3.5-flash")


# ==========================================
# GMAIL
# ==========================================

GMAIL_CREDENTIALS_FILE = _resolve_project_path(
    "GMAIL_CREDENTIALS_FILE",
    "credentials/gmail_credentials.json",
)
GMAIL_TOKEN_FILE = _resolve_project_path(
    "GMAIL_TOKEN_FILE",
    "credentials/gmail_token.json",
)


# ==========================================
# MYSQL
# ==========================================

DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    db_host = os.getenv("DB_HOST", "localhost")
    db_port = os.getenv("DB_PORT", "3306")
    db_name = os.getenv("DB_NAME")
    db_user = os.getenv("DB_USER")
    db_password = os.getenv("DB_PASSWORD", "")
    if db_name and db_user:
        encoded_user = quote_plus(db_user)
        encoded_password = quote_plus(db_password)
        DATABASE_URL = (
            f"mysql+pymysql://{encoded_user}:{encoded_password}"
            f"@{db_host}:{db_port}/{db_name}"
        )


# ==========================================
# TELEGRAM
# ==========================================

TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.getenv("TELEGRAM_CHAT_ID")


# ==========================================
# SCHEDULER / TIMEZONE
# ==========================================

TIMEZONE = os.getenv("TIMEZONE", "Asia/Kolkata")


# ==========================================
# VALIDATION
# ==========================================

if not GEMINI_API_KEY:
    raise ValueError("GEMINI_API_KEY is missing")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing")

if not TELEGRAM_BOT_TOKEN:
    raise ValueError("TELEGRAM_BOT_TOKEN is missing")

if not TELEGRAM_CHAT_ID:
    raise ValueError("TELEGRAM_CHAT_ID is missing")