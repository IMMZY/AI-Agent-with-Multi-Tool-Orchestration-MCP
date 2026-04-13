"""
config.py — Load and expose all configuration values for the Research Assistant Agent.
API keys and settings are read from environment variables (or a .env file).
"""

import os
import sys

from dotenv import load_dotenv

load_dotenv()


def _require(key: str) -> str:
    """Return the value of an environment variable, or exit with a helpful message."""
    value = os.getenv(key)
    if not value:
        print(f"[config] ERROR: Required environment variable '{key}' is not set.", file=sys.stderr)
        print("[config] Copy .env.example to .env and fill in your keys.", file=sys.stderr)
        sys.exit(1)
    return value


# ── API keys ──────────────────────────────────────────────────────────────────
OPENAI_API_KEY: str = _require("OPENAI_API_KEY")

# ── LLM settings ─────────────────────────────────────────────────────────────
LLM_MODEL: str = os.getenv("LLM_MODEL", "gpt-4o-mini")
LLM_MAX_TOKENS: int = int(os.getenv("LLM_MAX_TOKENS", "1024"))

# ── Search settings ───────────────────────────────────────────────────────────
SEARCH_MAX_RESULTS: int = int(os.getenv("SEARCH_MAX_RESULTS", "5"))

# ── MCP server — points to src/mcp_server.py (same directory as this file) ───
MCP_SERVER_SCRIPT: str = os.path.join(os.path.dirname(__file__), "mcp_server.py")

# ── Database ──────────────────────────────────────────────────────────────────
DB_PATH: str = os.getenv("DB_PATH", "research.db")
