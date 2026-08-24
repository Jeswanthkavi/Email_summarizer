from app.config.settings import (
    TELEGRAM_CHAT_ID
)

from app.telegram.telegram_client import (
    send_message
)


def main():

    message = """

AI Email Agent Test

Your Telegram notification system
is working successfully.

Gmail -> Gemini -> MySQL -> Telegram

"""


    send_message(

        TELEGRAM_CHAT_ID,

        message

    )


    print(
        "Test message sent successfully."
    )


if __name__ == "__main__":

    main()