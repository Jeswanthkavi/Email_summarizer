from app.ai.gemini_client import (
    generate_response
)

from app.config.settings import (
    GEMINI_MODEL
)

from app.utils.logger import get_logger


logger = get_logger()


def main():

    logger.info(
        f"Testing Gemini model: "
        f"{GEMINI_MODEL}"
    )


    prompt = """
You are an AI assistant.

Explain what an AI email assistant does.

Requirements:

1. Explain it in exactly three sentences.
2. Use simple English.
3. Do not use bullet points.
"""


    try:

        response = generate_response(
            prompt
        )


        print(
            "\n"
            + "=" * 60
        )

        print(
            "GEMINI TEST SUCCESSFUL"
        )

        print(
            "=" * 60
        )


        print(
            "\nModel:"
        )

        print(
            GEMINI_MODEL
        )


        print(
            "\nGemini Response:"
        )

        print(
            response
        )


        print(
            "\n"
            + "=" * 60
        )


    except Exception as e:

        logger.error(
            f"Gemini test failed: {e}"
        )


if __name__ == "__main__":

    main()