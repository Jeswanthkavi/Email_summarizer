from app.services.email_service import (
    fetch_and_save_emails
)


def main():

    print(
        "\n"
        + "=" * 70
    )

    print(
        "GMAIL TO MYSQL TEST"
    )

    print(
        "=" * 70
    )


    saved_count = (
        fetch_and_save_emails(
            max_results=10
        )
    )


    print(
        "\n"
        + "=" * 70
    )


    print(
        f"New emails saved: "
        f"{saved_count}"
    )


    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()