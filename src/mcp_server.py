"""
mcp_server.py — MCP (Model Context Protocol) server for the Research Assistant Agent.

This server acts as the standardized API layer between the LangGraph agent and the
SQLite database.  The agent never touches the database directly — it always goes
through these tools.  Swapping SQLite for another backend only requires changing
this file; the agent code stays untouched.

Run:
    python src/mcp_server.py

Tools exposed:
    save_research    — insert a new research note into SQLite
    list_research    — return all saved entries (title + date)
    search_research  — full-text search over title and summary
"""

import json
import os
import sqlite3
from datetime import datetime

from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP

# Load env directly — this script runs as a standalone subprocess from the project root.
load_dotenv()
DB_PATH: str = os.getenv("DB_PATH", "research.db")

# ── Server initialisation ─────────────────────────────────────────────────────
mcp = FastMCP("research-assistant-server")


# ── Database helpers ──────────────────────────────────────────────────────────

def _get_connection() -> sqlite3.Connection:
    """Open and return a SQLite connection with row_factory set."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    return conn


def _init_db() -> None:
    """Create the research table if it does not already exist."""
    conn = _get_connection()
    conn.execute(
        """
        CREATE TABLE IF NOT EXISTS research (
            id        INTEGER PRIMARY KEY AUTOINCREMENT,
            title     TEXT    NOT NULL,
            summary   TEXT    NOT NULL,
            sources   TEXT    NOT NULL,   -- JSON-encoded list of URLs
            timestamp TEXT    NOT NULL
        )
        """
    )
    conn.commit()
    conn.close()


_init_db()


# ── MCP tools ─────────────────────────────────────────────────────────────────

@mcp.tool()
def save_research(
    title: str,
    summary: str,
    sources: list[str],
    timestamp: str = "",
) -> str:
    """
    Save a research note to the SQLite database.

    Args:
        title:     Short title / research query that was investigated.
        summary:   LLM-generated summary text (plain text or markdown).
        sources:   List of source URLs that were consulted.
        timestamp: ISO-8601 timestamp.  Defaults to the current UTC time if empty.

    Returns:
        A confirmation message including the assigned row ID.
    """
    if not timestamp:
        timestamp = datetime.utcnow().isoformat()

    conn = _get_connection()
    cursor = conn.execute(
        "INSERT INTO research (title, summary, sources, timestamp) VALUES (?, ?, ?, ?)",
        (title, summary, json.dumps(sources), timestamp),
    )
    row_id = cursor.lastrowid
    conn.commit()
    conn.close()
    return f"Research note saved (id={row_id}): '{title}'"


@mcp.tool()
def list_research() -> list[dict]:
    """
    Return all saved research entries, ordered by most recent first.

    Returns:
        A list of dicts, each with keys: id, title, timestamp.
    """
    conn = _get_connection()
    rows = conn.execute(
        "SELECT id, title, timestamp FROM research ORDER BY id DESC"
    ).fetchall()
    conn.close()
    return [{"id": row["id"], "title": row["title"], "timestamp": row["timestamp"]} for row in rows]


@mcp.tool()
def search_research(keyword: str) -> list[dict]:
    """
    Search past research entries by keyword in title or summary.

    Args:
        keyword: The search term to look for (case-insensitive substring match).

    Returns:
        A list of matching entries, each with keys: id, title, summary, timestamp.
    """
    pattern = f"%{keyword}%"
    conn = _get_connection()
    rows = conn.execute(
        """
        SELECT id, title, summary, timestamp
        FROM   research
        WHERE  title   LIKE ?
        OR     summary LIKE ?
        ORDER  BY id DESC
        """,
        (pattern, pattern),
    ).fetchall()
    conn.close()
    return [
        {
            "id": row["id"],
            "title": row["title"],
            "summary": row["summary"],
            "timestamp": row["timestamp"],
        }
        for row in rows
    ]


# ── Entry point ───────────────────────────────────────────────────────────────

if __name__ == "__main__":
    mcp.run()
