from google import genai

from app.config.settings import GEMINI_API_KEY


client = genai.Client(
    api_key=GEMINI_API_KEY
)


def main():

    print("\nAvailable Gemini models:\n")

    for model in client.models.list():

        supported_actions = getattr(
            model,
            "supported_actions",
            []
        )

        if (
            "generateContent"
            in supported_actions
        ):

            print(
                f"Model: {model.name}"
            )

            print(
                f"Display Name: "
                f"{model.display_name}"
            )

            print(
                f"Supported Actions: "
                f"{supported_actions}"
            )

            print("-" * 60)


if __name__ == "__main__":

    main()