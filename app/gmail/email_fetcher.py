import base64

from bs4 import BeautifulSoup

from app.gmail.gmail_client import (
    get_gmail_service
)

from app.utils.logger import get_logger


logger = get_logger()


# ==================================================
# DECODE EMAIL BODY
# ==================================================

def decode_body(data):

    """
    Decode Gmail's Base64 encoded email body.
    """

    try:

        decoded_bytes = base64.urlsafe_b64decode(
            data
        )

        return decoded_bytes.decode(
            "utf-8",
            errors="ignore"
        )

    except Exception as e:

        logger.error(
            f"Failed to decode email body: {e}"
        )

        return ""


# ==================================================
# HTML TO TEXT
# ==================================================

def html_to_text(html):

    """
    Convert HTML email content
    into readable plain text.
    """

    soup = BeautifulSoup(
        html,
        "lxml"
    )

    return soup.get_text(
        separator=" ",
        strip=True
    )


# ==================================================
# EXTRACT EMAIL BODY
# ==================================================

def extract_email_body(payload):

    """
    Extract the text body from
    Gmail message payload.
    """

    # --------------------------------------------------
    # Direct body
    # --------------------------------------------------

    body_data = payload.get(
        "body",
        {}
    ).get(
        "data"
    )


    if body_data:

        decoded = decode_body(
            body_data
        )

        return html_to_text(
            decoded
        )


    # --------------------------------------------------
    # Multipart email
    # --------------------------------------------------

    parts = payload.get(
        "parts",
        []
    )


    for part in parts:

        mime_type = part.get(
            "mimeType",
            ""
        )


        # Text/plain
        if mime_type == "text/plain":

            data = part.get(
                "body",
                {}
            ).get(
                "data"
            )


            if data:

                return decode_body(
                    data
                )


        # Text/html
        elif mime_type == "text/html":

            data = part.get(
                "body",
                {}
            ).get(
                "data"
            )


            if data:

                html = decode_body(
                    data
                )

                return html_to_text(
                    html
                )


        # Nested multipart
        elif part.get(
            "parts"
        ):

            result = extract_email_body(
                part
            )


            if result:

                return result


    return ""


# ==================================================
# GET HEADER
# ==================================================

def get_header(
    headers,
    header_name
):

    """
    Extract a specific email header.
    """

    for header in headers:

        if (
            header.get(
                "name",
                ""
            ).lower()
            == header_name.lower()
        ):

            return header.get(
                "value",
                ""
            )


    return ""


# ==================================================
# GET EMAIL BY ID
# ==================================================

def get_email_by_id(
    service,
    message_id
):

    """
    Fetch complete email information
    using Gmail message ID.
    """

    message = (
        service.users()
        .messages()
        .get(

            userId="me",

            id=message_id,

            format="full"

        )
        .execute()
    )


    payload = message.get(
        "payload",
        {}
    )


    headers = payload.get(
        "headers",
        []
    )


    sender = get_header(
        headers,
        "From"
    )


    subject = get_header(
        headers,
        "Subject"
    )


    date = get_header(
        headers,
        "Date"
    )


    body = extract_email_body(
        payload
    )


    return {

        "gmail_message_id": message.get(
            "id"
        ),

        "thread_id": message.get(
            "threadId"
        ),

        "sender": sender,

        "subject": subject,

        "date": date,

        "body": body

    }


# ==================================================
# FETCH LATEST EMAILS
# ==================================================

def fetch_latest_emails(
    max_results=5
):

    """
    Fetch the latest emails from Gmail.
    """

    service = (
        get_gmail_service()
    )


    logger.info(
        f"Fetching latest {max_results} emails..."
    )


    results = (

        service.users()
        .messages()
        .list(

            userId="me",

            maxResults=max_results,

            labelIds=[
                "INBOX"
            ]

        )
        .execute()

    )


    messages = results.get(
        "messages",
        []
    )


    logger.info(
        f"Found {len(messages)} emails."
    )


    emails = []


    for message in messages:

        message_id = message.get(
            "id"
        )


        try:

            email = get_email_by_id(

                service,

                message_id

            )


            emails.append(
                email
            )


        except Exception as e:

            logger.error(

                f"Failed to fetch email "
                f"{message_id}: {e}"

            )


    return emails