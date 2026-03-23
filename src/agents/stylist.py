"""DressMate stylist agent – wiring, toolset, and factory."""

from azure.ai.agents import AgentsClient
from azure.ai.agents.models import (
    BingGroundingTool,
    CodeInterpreterTool,
    FileSearchTool,
    FunctionTool,
    ToolSet,
)

from src.config import BING_CONNECTION_ID, MODEL_NAME, PROMPTS_DIR
from src.tools import query_wardrobe


def _load_system_prompt() -> str:
    """Read the system block from the Prompty file, skipping YAML frontmatter."""
    prompty_path = PROMPTS_DIR / "stylist.prompty"
    text = prompty_path.read_text()
    # Split on --- delimiters; content after the second --- is the prompt body
    parts = text.split("---")
    if len(parts) >= 3:
        body = "---".join(parts[2:]).strip()
        # Remove the leading "system:" marker if present
        if body.lower().startswith("system:"):
            body = body[len("system:"):].strip()
        return body
    return text


def build_toolset(client: AgentsClient) -> ToolSet:
    """Build a ToolSet with all four tools."""
    toolset = ToolSet()
    toolset.add(FunctionTool(functions={query_wardrobe}))
    toolset.add(CodeInterpreterTool())

    vector_store = client.vector_stores.create(name="DressMate-catalog")
    toolset.add(FileSearchTool(vector_store_ids=[vector_store.id]))

    if BING_CONNECTION_ID:
        toolset.add(BingGroundingTool(connection_id=BING_CONNECTION_ID))

    return toolset


def create_stylist_agent(client: AgentsClient, toolset: ToolSet):
    """Create the DressMate stylist agent and return it."""
    return client.create_agent(
        model=MODEL_NAME,
        name="DressMate",
        instructions=_load_system_prompt(),
        toolset=toolset,
    )
