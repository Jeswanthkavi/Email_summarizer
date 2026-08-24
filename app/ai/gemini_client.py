import json
import time

from google import genai

from app.config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL
)

from app.utils.logger import get_logger


logger = get_logger()


client = genai.Client(
    api_key=GEMINI_API_KEY
)


FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite"
]
# ==================================================
# EMAIL ANALYSIS PROMPT
# ==================================================
EMAIL_ANALYSIS_PROMPT = """
You are an AI email analysis assistant.

Analyze the email provided below.

Your job is to identify:

1. A concise summary of the email.
2. The category of the email.
3. The priority level.
4. Whether the user needs to take action.
5. If action is required, clearly explain what action is needed.

Allowed categories:

- Work
- Education
- Finance
- Personal
- Meeting
- Shopping
- Travel
- Security
- Promotion
- Newsletter
- Social
- Other

Allowed priority levels:

- High
- Medium
- Low

Return ONLY valid JSON.

The JSON must follow exactly this structure:

{{
    "summary": "Short summary of the email",
    "category": "One category from the allowed categories",
    "priority": "High, Medium, or Low",
    "action_required": "Describe the required action, or say None"
}}

Do not add markdown.
Do not add ```json.
Do not add explanations outside the JSON.

EMAIL:

From:
{sender}

Subject:
{subject}

Date:
{date}

Body:
{body}
"""
# ==================================================
# ANALYZE EMAIL
# ==================================================

def analyze_email(email):

    sender = email.get(
        "sender",
        ""
    )

    subject = email.get(
        "subject",
        ""
    )

    date = email.get(
        "date",
        ""
    )

    body = email.get(
        "body",
        ""
    )


    body = body[:15000]


    prompt = EMAIL_ANALYSIS_PROMPT.format(

        sender=sender,

        subject=subject,

        date=date,

        body=body

    )


    logger.info(

        f"Analyzing email with Gemini: "
        f"{subject}"

    )


    models_to_try = []


    if GEMINI_MODEL:

        models_to_try.append(
            GEMINI_MODEL
        )


    for model_name in FALLBACK_MODELS:

        if model_name not in models_to_try:

            models_to_try.append(
                model_name
            )


    response = None

    last_error = None


    for model_name in models_to_try:

        try:

            logger.info(

                f"Trying Gemini model: "
                f"{model_name}"

            )


            response = (
                client.models.generate_content(

                    model=model_name,

                    contents=prompt

                )
            )


            logger.success(

                f"Gemini response received "
                f"from {model_name}"

            )


            break


        except Exception as e:

            last_error = e


            logger.error(

                f"Model {model_name} failed: "
                f"{e}"

            )


            continue


    if response is None:

        logger.error(

            "All Gemini models failed."

        )


        raise RuntimeError(

            f"All Gemini models failed. "
            f"Last error: {last_error}"

        )


    response_text = (
        response.text.strip()
    )


    # Remove markdown code block

    if response_text.startswith(
        "```json"
    ):

        response_text = (

            response_text
            .replace(
                "```json",
                "",
                1
            )
            .strip()

        )


    if response_text.endswith(
        "```"
    ):

        response_text = (

            response_text[:-3]
            .strip()

        )


    # Parse JSON

    analysis = json.loads(
        response_text
    )


    required_fields = [

        "summary",

        "category",

        "priority",

        "action_required"

    ]


    for field in required_fields:

        if field not in analysis:

            raise ValueError(

                f"Gemini response missing "
                f"field: {field}"

            )


    return analysis