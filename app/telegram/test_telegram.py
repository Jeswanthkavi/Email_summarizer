from app.telegram.telegram_client import (
    get_updates
)


def main():

    print(
        "=" * 60
    )

    print(
        "TELEGRAM CHAT ID TEST"
    )

    print(
        "=" * 60
    )


    data = get_updates()


    print(
        "\nTelegram response:"
    )


    print(
        data
    )


    print(
        "\nLook for:"
    )


    print(
        '"chat": {"id": YOUR_CHAT_ID}'
    )


if __name__ == "__main__":

    main()