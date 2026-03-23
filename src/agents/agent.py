"""Generic agent factory – builds toolsets, creates, and retrieves agents."""

from pathlib import Path

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    BingGroundingTool,
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    ToolSet,
)

from src.config import BING_CONNECTION_ID, MODEL_NAME, PROMPTS_DIR


def load_system_prompt(prompt_file: str) -> str:
    """Read the system block from a Prompty file, skipping YAML frontmatter."""
    prompty_path = PROMPTS_DIR / prompt_file
    text = prompty_path.read_text()
    parts = text.split("---")
    if len(parts) >= 3:
        body = "---".join(parts[2:]).strip()
        if body.lower().startswith("system:"):
            body = body[len("system:"):].strip()
        return body
    return text


def build_toolset(client: AgentsClient, agent_cfg: dict) -> ToolSet:
    """Build a ToolSet from an agent config entry."""
    toolset = ToolSet()

    functions = agent_cfg.get("tools")
    if functions:
        toolset.add(FunctionTool(functions=functions))

    toolset.add(CodeInterpreterTool())

    agent_name = agent_cfg.get("name", "Agent")
    vector_store = client.vector_stores.create(name=f"{agent_name}-catalog")
    toolset.add(FileSearchTool(vector_store_ids=[vector_store.id]))

    if BING_CONNECTION_ID:
        toolset.add(BingGroundingTool(connection_id=BING_CONNECTION_ID))

    return toolset


def create_agent(client: AgentsClient, agent_cfg: dict, toolset: ToolSet):
    """Create a new agent on the service from a config entry and return it."""
    model = agent_cfg.get("model") or MODEL_NAME
    return client.create_agent(
        model=model,
        name=agent_cfg["name"],
        instructions=load_system_prompt(agent_cfg["prompt"]),
        toolset=toolset,
    )


def get_agent(client: AgentsClient, agent_id: str):
    """Retrieve an existing agent by ID."""
    return client.get_agent(agent_id=agent_id)
