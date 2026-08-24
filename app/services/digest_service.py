from app.database.connection import (
    SessionLocal
)

from app.database.repository import (
    get_unsent_digest_emails
)

from app.utils.logger import get_logger


logger = get_logger()


def generate_email_digest(
    limit: int = 50
):

    db = SessionLocal()


    try:

        # ==========================================
        # GET ONLY EMAILS NOT YET SENT TO TELEGRAM
        # ==========================================

        records = (
            get_unsent_digest_emails(

                db,

                limit

            )
        )


        logger.info(
            f"Found {len(records)} unsent emails."
        )


        # ==========================================
        # NO NEW EMAILS
        # ==========================================

        if not records:

            return None, []


        high_priority = []

        medium_priority = []

        low_priority = []


        # Store database IDs
        # so we can mark them as sent later

        email_ids = []


        # ==========================================
        # PROCESS EACH EMAIL
        # ==========================================

        for email, analysis in records:

            # Save email ID

            email_ids.append(
                email.id
            )


            email_data = {

                "id": email.id,

                "subject": (
                    email.subject
                    or "No Subject"
                ),

                "sender": (
                    email.sender
                    or "Unknown Sender"
                ),

                "summary": (
                    analysis.summary
                    or "No summary"
                ),

                "category": (
                    analysis.category
                    or "Other"
                ),

                "priority": (
                    analysis.priority
                    or "Low"
                ),

                "action_required": (
                    analysis.action_required
                    or "None"
                )

            }


            priority = (

                email_data[
                    "priority"
                ]
                .strip()
                .lower()

            )


            if priority == "high":

                high_priority.append(
                    email_data
                )

            elif priority == "medium":

                medium_priority.append(
                    email_data
                )

            else:

                low_priority.append(
                    email_data
                )


        logger.info(

            f"Email IDs included in digest: "
            f"{email_ids}"

        )


        # ==========================================
        # BUILD TELEGRAM MESSAGE
        # ==========================================

        message = []


        message.append(
            "AI EMAIL DIGEST"
        )


        message.append(
            "━━━━━━━━━━━━━━━━━━━━"
        )


        # ==========================================
        # HIGH PRIORITY
        # ==========================================

        if high_priority:

            message.append(
                "\nHIGH PRIORITY"
            )


            for index, email in enumerate(

                high_priority,

                start=1

            ):

                message.append(

                    f"\n{index}. "
                    f"{email['subject']}"

                )

                message.append(

                    f"From: "
                    f"{email['sender']}"

                )

                message.append(

                    f"Summary: "
                    f"{email['summary']}"

                )

                message.append(

                    f"Action: "
                    f"{email['action_required']}"

                )


        # ==========================================
        # MEDIUM PRIORITY
        # ==========================================

        if medium_priority:

            message.append(
                "\nMEDIUM PRIORITY"
            )


            for index, email in enumerate(

                medium_priority,

                start=1

            ):

                message.append(

                    f"\n{index}. "
                    f"{email['subject']}"

                )

                message.append(

                    f"From: "
                    f"{email['sender']}"

                )

                message.append(

                    f"Summary: "
                    f"{email['summary']}"

                )

                message.append(

                    f"Action: "
                    f"{email['action_required']}"

                )


        # ==========================================
        # LOW PRIORITY
        # ==========================================

        if low_priority:

            message.append(
                "\nLOW PRIORITY"
            )


            for index, email in enumerate(

                low_priority,

                start=1

            ):

                message.append(

                    f"\n{index}. "
                    f"{email['subject']}"

                )

                message.append(

                    f"From: "
                    f"{email['sender']}"

                )

                message.append(

                    f"Summary: "
                    f"{email['summary']}"

                )


        # ==========================================
        # STATISTICS
        # ==========================================

        total = (

            len(high_priority)

            + len(medium_priority)

            + len(low_priority)

        )


        message.append(
            "\n━━━━━━━━━━━━━━━━━━━━"
        )


        message.append(
            "SUMMARY"
        )


        message.append(

            f"Total emails: "
            f"{total}"

        )


        message.append(

            f"High: "
            f"{len(high_priority)}"

        )


        message.append(

            f"Medium: "
            f"{len(medium_priority)}"

        )


        message.append(

            f"Low: "
            f"{len(low_priority)}"

        )


        digest = "\n".join(
            message
        )


        # ==========================================
        # RETURN DIGEST + EMAIL IDs
        # ==========================================

        return digest, email_ids


    finally:

        db.close()