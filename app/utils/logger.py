import sys
from pathlib import Path

from loguru import logger


# Project root
BASE_DIR = Path(__file__).resolve().parents[2]

# Log directory
LOG_DIR = BASE_DIR / "logs"

LOG_DIR.mkdir(
    parents=True,
    exist_ok=True
)


# Remove default logger
logger.remove()


# Console logging
logger.add(
    sys.stdout,
    level="INFO",
    format=(
        "<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
        "<level>{level}</level> | "
        "{message}"
    ),
)


# File logging
logger.add(
    LOG_DIR / "application.log",
    rotation="10 MB",
    retention="30 days",
    compression="zip",
    level="INFO",
)


def get_logger():
    """
    Returns the application logger.
    """

    return logger