"""DressMate - Azure AI Agent Service prototype."""

import os

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

SYSTEM_INSTRUCTIONS = (
    "You are DressMate, a friendly personal styling assistant. "
    "Help users pick outfits based on the occasion, weather, and "
    "their wardrobe. Keep answers concise and fashion-forward."
)


def get_client() -> AzureOpenAI:
    credential = DefaultAzureCredential()
    token = credential.get_token("https://cognitiveservices.azure.com/.default")
    return AzureOpenAI(
        azure_endpoint=os.environ["AZURE_AI_ENDPOINT"],
        api_key=token.token,
        api_version="2025-03-01-preview",
    )


def chat(client: AzureOpenAI, user_message: str, previous_response_id=None) -> tuple:
    """Send a message and return (response_text, response_id) for chaining."""
    response = client.responses.create(
        model="gpt-4o",
        instructions=SYSTEM_INSTRUCTIONS,
        input=user_message,
        previous_response_id=previous_response_id,
    )
    text = response.output_text
    return text, response.id


def main():
    client = get_client()
    previous_id = None
    print("\nDressMate Agent is ready! Type 'quit' to exit.\n")
    while True:
        user_input = input("You: ").strip()
        if not user_input:
            continue
        if user_input.lower() in ("quit", "exit", "q"):
            break
        response_text, previous_id = chat(client, user_input, previous_id)
        print(f"\nDressMate: {response_text}\n")


if __name__ == "__main__":
    main()
