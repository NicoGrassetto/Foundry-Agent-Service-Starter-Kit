"""CLI – interactive conversation loop.

Usage:
    python -m src.main [agent-key]

If agent-key is omitted and only one agent is registered, it is used automatically.
Expects AGENT_IDS to be set in .env (written by `python -m src.setup`).
"""

import sys

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import MessageRole
from azure.identity import DefaultAzureCredential

from src.config import AGENT_IDS, AZURE_AI_ENDPOINT
from src.agents import AGENT_REGISTRY, build_toolset, get_agent


def get_client() -> AgentsClient:
    """Return an authenticated AgentsClient."""
    return AgentsClient(
        endpoint=AZURE_AI_ENDPOINT,
        credential=DefaultAzureCredential(),
    )


def _resolve_agent_key() -> str:
    """Determine which agent to run from CLI args or default."""
    if not AGENT_IDS:
        print("ERROR: No agents registered. Run `python -m src.setup` first.")
        sys.exit(1)

    if len(sys.argv) > 1:
        key = sys.argv[1]
    elif len(AGENT_IDS) == 1:
        key = next(iter(AGENT_IDS))
    else:
        keys = ", ".join(AGENT_IDS.keys())
        print(f"ERROR: Multiple agents registered. Specify one: python -m src.main <{keys}>")
        sys.exit(1)

    if key not in AGENT_IDS:
        keys = ", ".join(AGENT_IDS.keys())
        print(f"ERROR: Unknown agent '{key}'. Available: {keys}")
        sys.exit(1)

    return key


def main() -> None:
    key = _resolve_agent_key()
    agent_cfg = AGENT_REGISTRY[key]
    agent_id = AGENT_IDS[key]

    client = get_client()

    toolset = build_toolset(client, agent_cfg)
    client.enable_auto_function_calls(toolset)

    agent = get_agent(client, agent_id)
    agent_name = agent_cfg["name"]
    print(f"\n  Using agent: {agent.id} ({agent_name})")

    thread = client.threads.create()
    print(f"  Thread created: {thread.id}")
    print(f"\n{agent_name} is ready! Type 'quit' to exit.\n")

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
        print(f"\n{agent_name}: {last.text.value if last else '(no response)'}\n")

    print("Goodbye.")


if __name__ == "__main__":
    main()
