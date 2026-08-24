import json
from pathlib import Path

from google.auth.transport.requests import Request
from google.oauth2.credentials import Credentials
from google_auth_oauthlib.flow import InstalledAppFlow

from app.utils.logger import get_logger


logger = get_logger()


# ==================================================
# PROJECT DIRECTORIES
# ==================================================

BASE_DIR = Path(__file__).resolve().parents[2]

CREDENTIALS_DIR = BASE_DIR / "credentials"

CLIENT_SECRET_FILE = (
    CREDENTIALS_DIR / "gmail_credentials.json"
)

TOKEN_FILE = (
    CREDENTIALS_DIR / "gmail_token.json"
)


# ==================================================
# GMAIL PERMISSION
# ==================================================

SCOPES = [
    "https://www.googleapis.com/auth/gmail.readonly"
]


# ==================================================
# DELETE INVALID TOKEN
# ==================================================

def delete_invalid_token():

    if TOKEN_FILE.exists():

        logger.warning(
            "Deleting invalid Gmail token..."
        )

        TOKEN_FILE.unlink()

        logger.info(
            "Invalid Gmail token deleted."
        )


# ==================================================
# AUTHENTICATION
# ==================================================

def get_gmail_credentials():

    """
    Authenticate the application with Gmail.

    First run:
        Opens browser for Google OAuth login.

    Later runs:
        Uses saved gmail_token.json.

    If token is invalid or corrupted:
        Deletes token and starts OAuth again.
    """

    credentials = None


    # ==================================================
    # CHECK TOKEN
    # ==================================================

    if TOKEN_FILE.exists():

        logger.info(
            "Existing Gmail token found."
        )

        try:

            # Check if file is empty

            if TOKEN_FILE.stat().st_size == 0:

                raise ValueError(
                    "Gmail token file is empty."
                )


            # Check if valid JSON

            with open(
                TOKEN_FILE,
                "r"
            ) as token_file:

                json.load(
                    token_file
                )


            # Load credentials

            credentials = (
                Credentials.from_authorized_user_file(

                    str(TOKEN_FILE),

                    SCOPES

                )
            )


        except (
            json.JSONDecodeError,
            ValueError,
            KeyError
        ) as e:

            logger.warning(
                f"Invalid Gmail token detected: {e}"
            )

            delete_invalid_token()

            credentials = None


    # ==================================================
    # REFRESH TOKEN
    # ==================================================

    if credentials:

        if credentials.expired:

            if credentials.refresh_token:

                logger.info(
                    "Refreshing expired Gmail token..."
                )

                try:

                    credentials.refresh(
                        Request()
                    )

                except Exception as e:

                    logger.warning(
                        "Failed to refresh Gmail token: "
                        f"{e}"
                    )

                    delete_invalid_token()

                    credentials = None


    # ==================================================
    # NEW OAUTH LOGIN
    # ==================================================

    if not credentials or not credentials.valid:

        if not CLIENT_SECRET_FILE.exists():

            raise FileNotFoundError(

                "Gmail credentials file not found:\n"

                f"{CLIENT_SECRET_FILE}\n\n"

                "Please download your OAuth credentials "
                "from Google Cloud Console and place "
                "them in the credentials folder."

            )


        logger.info(
            "Starting Gmail OAuth authentication..."
        )


        flow = (
            InstalledAppFlow
            .from_client_secrets_file(

                str(CLIENT_SECRET_FILE),

                SCOPES

            )
        )


        credentials = (
            flow.run_local_server(

                port=0

            )
        )


        # ==================================================
        # SAVE TOKEN
        # ==================================================

        with open(
            TOKEN_FILE,
            "w"
        ) as token_file:

            token_file.write(
                credentials.to_json()
            )


        logger.success(
            "Gmail authentication successful."
        )


        logger.info(
            f"Gmail token saved to: "
            f"{TOKEN_FILE}"
        )


    return credentials