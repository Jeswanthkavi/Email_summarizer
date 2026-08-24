from app.services.notification_service import (
    send_email_digest
)


def main():

    print()

    print(
        "=" * 70
    )

    print(
        "EMAIL DIGEST TELEGRAM TEST"
    )

    print(
        "=" * 70
    )


    digest = (
        send_email_digest()
    )


    print()

    print(
        "Generated Digest:"
    )

    print()

    print(
        digest
    )


    print()

    print(
        "=" * 70
    )

    print(
        "DIGEST SENT SUCCESSFULLY"
    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()