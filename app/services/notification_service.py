from app.config.settings import (
    TELEGRAM_CHAT_ID
)

from app.telegram.telegram_client import (
    send_message
)

from app.services.digest_service import (
    generate_email_digest
)

from app.database.connection import (
    SessionLocal
)

from app.database.repository import (
    mark_emails_digest_sent
)

from app.utils.logger import get_logger


logger = get_logger()


def send_email_digest():

    logger.info(
        "Generating email digest..."
    )


    # ==========================================
    # GENERATE DIGEST
    # ==========================================

    digest, email_ids = (
        generate_email_digest()
    )


    # ==========================================
    # NO NEW EMAILS
    # ==========================================

    if not digest:

        logger.info(

            "No new emails to send "
            "in Telegram digest."

        )

        return False


    logger.info(

        f"Sending digest containing "
        f"{len(email_ids)} emails."

    )


    # ==========================================
    # SEND TELEGRAM MESSAGE
    # ==========================================

    send_message(

        TELEGRAM_CHAT_ID,

        digest

    )


    # ==========================================
    # MARK EMAILS AS DIGEST SENT
    # ==========================================

    db = SessionLocal()


    try:

        mark_emails_digest_sent(

            db,

            email_ids

        )


        logger.success(

            "Emails marked as "
            "digest_sent = 1."

        )


    except Exception as e:

        db.rollback()


        logger.error(

            f"Failed to mark emails "
            f"as digest sent: {e}"

        )


        raise


    finally:

        db.close()


    logger.success(

        "Email digest sent successfully."

    )


    return True