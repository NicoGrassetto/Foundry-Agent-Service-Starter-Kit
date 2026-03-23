"""Centralised configuration loaded from environment / .env."""

import json
import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Azure AI Foundry ────────────────────────────────────────────────
AZURE_AI_ENDPOINT: str = os.environ["AZURE_AI_ENDPOINT"]
BING_CONNECTION_ID: str = os.environ.get("BING_CONNECTION_ID", "")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "gpt-4o")

# Agent IDs persisted by `python -m src.setup`.
# Stored as JSON: {"math": "asst_abc", "other": "asst_xyz"}
AGENT_IDS: dict = json.loads(os.environ.get("AGENT_IDS", "{}"))

# ── Paths ───────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT_DIR / "src" / "prompts"
