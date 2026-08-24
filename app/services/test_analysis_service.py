from app.services.analysis_service import (
    process_unprocessed_emails
)


def main():

    print()

    print(
        "=" * 70
    )

    print(
        "AI EMAIL PROCESSING TEST"
    )

    print(
        "=" * 70
    )


    processed_count = (
        process_unprocessed_emails()
    )


    print()

    print(
        "=" * 70
    )

    print(
        "PROCESSING COMPLETED"
    )

    print(
        "=" * 70
    )

    print(

        f"Successfully analyzed emails: "
        f"{processed_count}"

    )

    print(
        "=" * 70
    )


if __name__ == "__main__":

    main()