"""Centralised configuration loaded from environment / .env."""

import os
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()

# ── Azure AI Foundry ────────────────────────────────────────────────
AZURE_AI_ENDPOINT: str = os.environ["AZURE_AI_ENDPOINT"]
BING_CONNECTION_ID: str = os.environ.get("BING_CONNECTION_ID", "")
MODEL_NAME: str = os.environ.get("MODEL_NAME", "gpt-4o")

# ── Paths ───────────────────────────────────────────────────────────
ROOT_DIR = Path(__file__).resolve().parent.parent
PROMPTS_DIR = ROOT_DIR / "src" / "prompts"
