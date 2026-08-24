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


def send_message(
    chat_id: str,
    message: str
):

    url = (

        f"https://api.telegram.org/"
        f"bot{TELEGRAM_BOT_TOKEN}/"
        f"sendMessage"

    )


    payload = {

        "chat_id": chat_id,

        "text": message

    }


    response = requests.post(

        url,

        json=payload,

        timeout=30

    )


    response.raise_for_status()


    result = response.json()


    if not result.get(
        "ok"
    ):

        raise RuntimeError(

            f"Telegram API error: "
            f"{result}"

        )


    logger.success(

        "Telegram message sent."

    )


    return result