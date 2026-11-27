import json
import re

from google import genai
from google.genai import types
from tenacity import retry, retry_if_exception, stop_after_attempt, wait_exponential

from app.config.settings import (
    GEMINI_API_KEY,
    GEMINI_MODEL,
)

from app.utils.logger import get_logger


logger = get_logger()


client = genai.Client(
    api_key=GEMINI_API_KEY,
    http_options=types.HttpOptions(timeout=30000),
)


FALLBACK_MODELS = [
    "gemini-3.5-flash",
    "gemini-3.1-flash-lite",
    "gemini-2.5-flash-lite",
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

{
    "summary": "Short summary of the email",
    "category": "One category from the allowed categories",
    "priority": "High, Medium, or Low",
    "action_required": "Describe the required action, or say None"
}

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


def _is_transient_error(exc: BaseException) -> bool:
    """Retry brief rate limits/timeouts; let 503 UNAVAILABLE fall back to the next model immediately."""
    msg = str(exc).lower()
    if "503" in msg or "unavailable" in msg:
        return False
    transient_markers = ("429", "500", "502", "504", "resource_exhausted", "timeout", "timed out")
    return any(marker in msg for marker in transient_markers)


def _get_models_to_try() -> list[str]:
    models_to_try = []
    if GEMINI_MODEL:
        models_to_try.append(GEMINI_MODEL)
    for model_name in FALLBACK_MODELS:
        if model_name not in models_to_try:
            models_to_try.append(model_name)
    return models_to_try


@retry(
    retry=retry_if_exception(_is_transient_error),
    stop=stop_after_attempt(2),
    wait=wait_exponential(multiplier=1, min=2, max=6),
    reraise=True,
)
def _call_model(model_name: str, prompt: str) -> str:
    response = client.models.generate_content(
        model=model_name,
        contents=prompt,
    )
    text = getattr(response, "text", None)
    if not text or not text.strip():
        raise RuntimeError(f"Model {model_name} returned an empty response.")
    return text.strip()


def generate_response(prompt: str) -> str:
    """Generate a text response from Gemini using configured primary + fallback models."""
    last_error = None
    for model_name in _get_models_to_try():
        try:
            logger.info(f"Trying Gemini model: {model_name}")
            text = _call_model(model_name, prompt)
            logger.success(f"Gemini response received from {model_name}")
            return text
        except Exception as e:
            last_error = e
            logger.error(f"Model {model_name} failed: {e}")
            continue

    logger.error("All Gemini models failed.")
    raise RuntimeError(f"All Gemini models failed. Last error: {last_error}")


def _build_analysis_prompt(sender: str, subject: str, date: str, body: str) -> str:
    """Substitute email fields in one pass so '{' and '}' inside email content cannot break formatting."""
    values = {
        "sender": sender,
        "subject": subject,
        "date": date,
        "body": body,
    }
    return re.sub(
        r"\{(sender|subject|date|body)\}",
        lambda match: values[match.group(1)],
        EMAIL_ANALYSIS_PROMPT,
    )


def _strip_markdown_fences(response_text: str) -> str:
    text = response_text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        if lines and lines[0].startswith("```"):
            lines = lines[1:]
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


# ==================================================
# ANALYZE EMAIL
# ==================================================

def analyze_email(email):
    sender = str(email.get("sender") or "")
    subject = str(email.get("subject") or "")
    date = str(email.get("date") or "")
    body = str(email.get("body") or "")[:15000]

    prompt = _build_analysis_prompt(
        sender=sender,
        subject=subject,
        date=date,
        body=body,
    )

    logger.info(f"Analyzing email with Gemini: {subject}")

    response_text = _strip_markdown_fences(generate_response(prompt))
    analysis = json.loads(response_text)

    required_fields = [
        "summary",
        "category",
        "priority",
        "action_required",
    ]

    for field in required_fields:
        if field not in analysis:
            raise ValueError(f"Gemini response missing field: {field}")

    return analysis