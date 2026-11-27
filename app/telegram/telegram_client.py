import requests

from app.config.settings import (
    TELEGRAM_BOT_TOKEN
)

from app.utils.logger import get_logger


logger = get_logger()


def get_updates():

    url = (

        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"getUpdates"

    )


    response = requests.get(
        url,
        timeout=30
    )


    response.raise_for_status()


    return response.json()


TELEGRAM_MAX_MESSAGE_LENGTH = 4096


def split_message(
    message: str,
    max_length: int = TELEGRAM_MAX_MESSAGE_LENGTH,
) -> list[str]:
    """Split a long message into chunks within Telegram's 4096-character limit."""
    if not message:
        return []
    if len(message) <= max_length:
        return [message]

    chunks = []
    current_lines = []
    current_len = 0

    for line in message.splitlines(keepends=True):
        if len(line) > max_length:
            if current_lines:
                chunks.append("".join(current_lines).rstrip("\n"))
                current_lines = []
                current_len = 0
            for start in range(0, len(line), max_length):
                chunks.append(line[start:start + max_length])
            continue

        if current_len + len(line) > max_length:
            chunks.append("".join(current_lines).rstrip("\n"))
            current_lines = [line]
            current_len = len(line)
        else:
            current_lines.append(line)
            current_len += len(line)

    if current_lines:
        chunks.append("".join(current_lines).rstrip("\n"))

    return [c for c in chunks if c]


def send_message(
    chat_id: str,
    message: str,
):
    url = (
        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"sendMessage"
    )

    chunks = split_message(message)
    if not chunks:
        raise ValueError("Cannot send an empty Telegram message.")

    last_result = None
    for idx, chunk in enumerate(chunks, start=1):
        payload = {
            "chat_id": chat_id,
            "text": chunk,
        }

        response = requests.post(
            url,
            json=payload,
            timeout=30,
        )
        response.raise_for_status()
        result = response.json()

        if not result.get("ok"):
            raise RuntimeError(f"Telegram API error: {result}")

        last_result = result
        if len(chunks) > 1:
            logger.info(f"Telegram message part {idx}/{len(chunks)} sent.")

    logger.success("Telegram message sent.")
    return last_result