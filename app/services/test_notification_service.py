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


    sent = send_email_digest()

    print()
    print("=" * 70)
    if sent:
        print("DIGEST SENT SUCCESSFULLY")
    else:
        print("NO UNSENT DIGEST EMAILS FOUND")
    print("=" * 70)


if __name__ == "__main__":

    main()