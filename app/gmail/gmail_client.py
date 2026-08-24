from googleapiclient.discovery import build

from app.gmail.auth import get_gmail_credentials
from app.utils.logger import get_logger


logger = get_logger()


# ==================================================
# CREATE GMAIL SERVICE
# ==================================================

def get_gmail_service():

    """
    Creates and returns an authenticated
    Gmail API service.
    """

    try:

        credentials = (
            get_gmail_credentials()
        )


        service = build(

            "gmail",

            "v1",

            credentials=credentials

        )


        logger.success(
            "Gmail API service created successfully."
        )


        return service


    except Exception as e:

        logger.error(
            f"Failed to create Gmail service: {e}"
        )

        raise