from app.gmail.email_fetcher import (
    fetch_latest_emails
)


def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "GMAIL EMAIL FETCH TEST"
    )

    print(
        "=" * 70
    )


    emails = fetch_latest_emails(
        max_results=5
    )


    if not emails:

        print(
            "\nNo emails found."
        )

        return


    for index, email in enumerate(
        emails,
        start=1
    ):

        print(
            "\n"
            + "-" * 70
        )


        print(
            f"EMAIL #{index}"
        )


        print(
            "-" * 70
        )


        print(
            f"Message ID: "
            f"{email['gmail_message_id']}"
        )


        print(
            f"From: "
            f"{email['sender']}"
        )


        print(
            f"Subject: "
            f"{email['subject']}"
        )


        print(
            f"Date: "
            f"{email['date']}"
        )


        print(
            "\nBody:"
        )


        body = email.get(
            "body",
            ""
        )


        if len(body) > 1000:

            body = (
                body[:1000]
                + "..."
            )


        print(
            body
        )


    print(
        "\n"
        + "=" * 70
    )


    print(
        "GMAIL TEST COMPLETED"
    )


    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()