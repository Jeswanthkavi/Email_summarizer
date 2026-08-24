from app.database.connection import (
    SessionLocal
)

from app.database.repository import (
    get_unprocessed_emails,
    get_email_analysis,
    save_email_analysis,
    mark_email_processed
)

from app.ai.gemini_client import (
    analyze_email
)

from app.utils.logger import get_logger


logger = get_logger()


def process_unprocessed_emails():

    db = SessionLocal()


    try:

        # ==========================================
        # GET ALL UNPROCESSED EMAILS
        # ==========================================

        emails = get_unprocessed_emails(
            db
        )


        if not emails:

            logger.info(
                "No unprocessed emails found."
            )

            return 0


        logger.info(

            f"Found {len(emails)} "
            f"unprocessed emails."

        )


        processed_count = 0


        # ==========================================
        # PROCESS EACH EMAIL
        # ==========================================

        for email in emails:

            logger.info(

                f"Processing email "
                f"{email.id}: "
                f"{email.subject}"

            )


            try:

                # ==================================
                # CHECK EXISTING ANALYSIS
                # ==================================

                existing_analysis = (
                    get_email_analysis(

                        db,

                        email.id

                    )
                )


                if existing_analysis:

                    logger.info(

                        f"Analysis already exists "
                        f"for email ID "
                        f"{email.id}. "
                        f"Marking as processed."

                    )


                    mark_email_processed(

                        db,

                        email.id

                    )


                    continue


                # ==================================
                # PREPARE EMAIL FOR GEMINI
                # ==================================

                email_data = {

                    "sender": email.sender,

                    "subject": email.subject,

                    "date": email.received_at,

                    "body": email.body

                }


                # ==================================
                # SEND TO GEMINI
                # ==================================

                logger.info(

                    f"Sending email ID "
                    f"{email.id} "
                    f"to Gemini."

                )


                analysis = analyze_email(

                    email_data

                )


                # ==================================
                # SAVE GEMINI RESULT
                # ==================================

                saved_analysis = (
                    save_email_analysis(

                        db,

                        email.id,

                        analysis

                    )
                )


                logger.success(

                    f"Analysis saved for "
                    f"email ID "
                    f"{email.id}."

                )


                # ==================================
                # MARK EMAIL AS PROCESSED
                # ==================================

                mark_email_processed(

                    db,

                    email.id

                )


                processed_count += 1


                logger.success(

                    f"Email ID "
                    f"{email.id} "
                    f"processed successfully."

                )


                print()

                print(
                    "=" * 70
                )

                print(
                    "EMAIL ANALYSIS"
                )

                print(
                    "=" * 70
                )

                print(
                    f"Email: "
                    f"{email.subject}"
                )

                print(
                    f"Summary: "
                    f"{analysis['summary']}"
                )

                print(
                    f"Category: "
                    f"{analysis['category']}"
                )

                print(
                    f"Priority: "
                    f"{analysis['priority']}"
                )

                print(
                    f"Action Required: "
                    f"{analysis['action_required']}"
                )

                print(
                    "=" * 70
                )


            except Exception as e:

                # ==================================
                # IMPORTANT
                # ==================================
                # Do NOT mark email as processed
                # if Gemini fails.
                #
                # processed remains 0.
                #
                # It can be retried later.
                # ==================================

                logger.error(

                    f"Failed to process "
                    f"email ID "
                    f"{email.id}: "
                    f"{e}"

                )


                db.rollback()


                continue


        logger.info(

            f"Total emails successfully "
            f"processed: "
            f"{processed_count}"

        )


        return processed_count


    finally:

        db.close()