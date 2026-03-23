"""DressMate CLI – interactive conversation loop."""

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from azure.identity import DefaultAzureCredential

from src.config import AZURE_AI_ENDPOINT
from src.agents import build_toolset, create_stylist_agent


def get_client() -> AgentsClient:
    """Return an authenticated AgentsClient."""
    return AgentsClient(
        endpoint=AZURE_AI_ENDPOINT,
        credential=DefaultAzureCredential(),
    )


def main() -> None:
    client = get_client()

    toolset = build_toolset(client)
    client.enable_auto_function_calls(toolset)

    agent = create_stylist_agent(client, toolset)
    print(f"\n  Agent created: {agent.id}")

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

            client.messages.create(
                thread_id=thread.id,
                role=MessageRole.USER,
                content=user_input,
            )

            client.runs.create_and_process(
                thread_id=thread.id,
                agent_id=agent.id,
                toolset=toolset,
            )

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
