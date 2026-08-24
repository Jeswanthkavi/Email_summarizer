from app.database.connection import (
    SessionLocal
)

from app.database.repository import (
    save_email
)

from app.gmail.email_fetcher import (
    fetch_latest_emails
)

from app.utils.logger import get_logger


logger = get_logger()


def fetch_and_save_emails(
    max_results=10
):

    logger.info(
        f"Fetching latest {max_results} emails..."
    )


    emails = fetch_latest_emails(
        max_results=max_results
    )


    if not emails:

        logger.info(
            "No emails found."
        )

        return 0


    db = SessionLocal()

    saved_count = 0


    try:

        for email_data in emails:

            try:

                email = save_email(

                    db,

                    email_data

                )


                if email is None:

                    logger.info(

                        "Email already exists. "
                        f"Skipping: "
                        f"{email_data.get('subject')}"

                    )

                    continue


                saved_count += 1


                logger.success(

                    "New email saved: "

                    f"{email.subject}"

                )


            except Exception as e:

                logger.error(

                    "Failed to save email: "

                    f"{e}"

                )

                db.rollback()


    finally:

        db.close()


    logger.info(

        f"New emails saved: "
        f"{saved_count}"

    )


    return saved_count