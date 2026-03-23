"""Setup – create (or recreate) all agents on Azure AI Foundry Agent Service.

Run once after provisioning infrastructure:
    python -m src.setup

Writes agent IDs to .env so that `python -m src.main` can reuse them.
"""

import json

from azure.ai.agents import AgentsClient
from azure.identity import DefaultAzureCredential

from src.config import AGENT_IDS, AZURE_AI_ENDPOINT, ROOT_DIR
from src.agents import AGENT_REGISTRY, build_toolset, create_agent


def _save_agent_ids(agent_ids: dict) -> None:
    """Write the AGENT_IDS JSON blob to .env."""
    env_path = ROOT_DIR / ".env"
    lines = env_path.read_text().splitlines() if env_path.exists() else []

    new_lines = [l for l in lines if not l.startswith("AGENT_IDS=")]
    new_lines.append(f"AGENT_IDS={json.dumps(agent_ids)}")
    env_path.write_text("\n".join(new_lines) + "\n")


def main() -> None:
    client = AgentsClient(
        endpoint=AZURE_AI_ENDPOINT,
        credential=DefaultAzureCredential(),
    )

    # Delete previously created agents to avoid orphans
    for key, old_id in AGENT_IDS.items():
        try:
            client.delete_agent(agent_id=old_id)
            print(f"  Deleted previous '{key}' agent: {old_id}")
        except Exception:
            pass

    new_ids: dict = {}

    for key, cfg in AGENT_REGISTRY.items():
        toolset = build_toolset(client, cfg)
        agent = create_agent(client, cfg, toolset)
        new_ids[key] = agent.id
        print(f"  Created '{key}' agent: {agent.id} ({agent.name})")

    _save_agent_ids(new_ids)
    print(f"\n  AGENT_IDS written to .env")
    print(f"  Registered agents: {', '.join(new_ids.keys())}")
    print(f"\n  Run with:  python -m src.main <agent-key>\n")


if __name__ == "__main__":
    main()
