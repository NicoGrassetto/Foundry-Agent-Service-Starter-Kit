"""DressMate – Azure AI Agent Service prototype.

Uses the azure-ai-agents SDK to run a styling assistant on the
Azure Agent Service data-plane (threads, runs, tool execution).
"""

import os

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import FunctionTool, MessageRole
from azure.identity import DefaultAzureCredential
from dotenv import load_dotenv

from src.tools import query_wardrobe

load_dotenv()

SYSTEM_INSTRUCTIONS = (
    "You are DressMate, a friendly personal styling assistant. "
    "Help users pick outfits based on the occasion, weather, and "
    "their wardrobe. Keep answers concise and fashion-forward. "
    "Always call query_wardrobe before making outfit suggestions "
    "so you base your advice on what the user actually owns."
)


# ── Agent setup ─────────────────────────────────────────────────────

def get_client() -> AgentsClient:
    """Return an authenticated AgentsClient pointing at the AI Foundry project."""
    credential = DefaultAzureCredential()
    return AgentsClient(
        endpoint=os.environ["AZURE_AI_ENDPOINT"],
        credential=credential,
    )


def main() -> None:
    client = get_client()

    # Register user-defined functions so the SDK auto-executes tool calls.
    functions = FunctionTool(functions={query_wardrobe})
    client.enable_auto_function_calls(functions)

    # Create a persistent agent with the wardrobe tool.
    agent = client.create_agent(
        model="gpt-4o",
        name="DressMate",
        instructions=SYSTEM_INSTRUCTIONS,
        toolset=functions,
    )
    print(f"\n  Agent created: {agent.id}")

    # Create a single thread for the conversation.
    thread = client.threads.create()
    print(f"  Thread created: {thread.id}")
    print("\nDressMate Agent is ready! Type 'quit' to exit.\n")

    try:
        while True:
            user_input = input("You: ").strip()
            if not user_input:
                continue
            if user_input.lower() in ("quit", "exit", "q"):
                break

            # Add the user message to the thread.
            client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=user_input,
            )

            # Run the agent (polls to completion, auto-handles tool calls).
            client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
                toolset=functions,
            )

            # Retrieve the assistant's last response.
            last = client.messages.get_last_message_text_by_role(
                thread_id=thread.id,
                role=MessageRole.AGENT,
            )
            print(f"\nDressMate: {last.text.value if last else '(no response)'}\n")
    finally:
        client.delete_agent(agent.id)
        print("Agent cleaned up.")


if __name__ == "__main__":
    main()
