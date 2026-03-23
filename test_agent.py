"""Quick test of the DressMate agent."""
import os
import warnings

warnings.filterwarnings("ignore")

from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv
from openai import AzureOpenAI

load_dotenv()

credential = DefaultAzureCredential()
token = credential.get_token("https://cognitiveservices.azure.com/.default")
client = AzureOpenAI(
    azure_endpoint=os.environ["AZURE_AI_ENDPOINT"],
    api_key=token.token,
    api_version="2025-03-01-preview",
)

response = client.responses.create(
    model="gpt-4o",
    instructions="You are DressMate, a friendly personal styling assistant. Keep answers concise.",
    input="What should I wear to a summer wedding in NYC?",
)

print(f"Response ID: {response.id}")
print(f"\nDressMate: {response.output_text}")

