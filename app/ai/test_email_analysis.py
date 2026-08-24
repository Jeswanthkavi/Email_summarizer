from app.database.connection import (
    SessionLocal
)

from app.database.repository import (
    get_unprocessed_emails
)

from app.ai.gemini_client import (
    analyze_email
)


def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "GEMINI EMAIL ANALYSIS TEST"
    )

    print(
        "=" * 70
    )


    db = SessionLocal()


    try:

        emails = get_unprocessed_emails(
            db
        )


        if not emails:

            print(
                "\nNo unprocessed emails found."
            )

            return


        email = emails[0]


        print(
            "\nTesting email:"
        )


        print(
            f"From: {email.sender}"
        )


        print(
            f"Subject: {email.subject}"
        )


        email_data = {

            "sender": email.sender,

            "subject": email.subject,

            "date": email.received_at,

            "body": email.body

        }


        print(
            "\nSending email to Gemini..."
        )


        analysis = analyze_email(
            email_data
        )


        print(
            "\n"
            + "-" * 70
        )


        print(
            "GEMINI ANALYSIS"
        )


        print(
            "-" * 70
        )


        print(
            f"\nSummary:"
        )

        print(
            analysis["summary"]
        )


        print(
            f"\nCategory:"
        )

        print(
            analysis["category"]
        )


        print(
            f"\nPriority:"
        )

        print(
            analysis["priority"]
        )


        print(
            f"\nAction Required:"
        )

        print(
            analysis["action_required"]
        )


        print(
            "\n"
            + "=" * 70
        )


        print(
            "GEMINI EMAIL ANALYSIS SUCCESSFUL"
        )


        print(
            "=" * 70
        )


    finally:

        db.close()


if __name__ == "__main__":

    main()