"""Agent registry – declarative configuration for all agents.

To add a new agent:
1. Add an entry to AGENT_REGISTRY below.
2. Create a matching .prompty file in src/prompts/.
3. Run `python -m src.setup` to create all agents on the service.
"""

from src.tools import add

# Each entry maps a unique agent key to its configuration.
# - name:    Display name used when creating the agent on the service.
# - prompt:  Filename inside src/prompts/ (Prompty format).
# - model:   Model deployment name (can be overridden per agent).
# - tools:   Set of callable functions exposed via FunctionTool.
AGENT_REGISTRY: dict = {
    "default": {
        "name": "Agent",
        "prompt": "agent.prompty",
        "model": None,         # None → falls back to MODEL_NAME from config
        "tools": {add},
    },
}
