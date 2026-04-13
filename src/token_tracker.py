"""
token_tracker.py — Per-node token usage tracking and agent activity logging.

Provides a module-level singleton `tracker` that any node can import and use
to record token counts and log activity messages.  Call tracker.reset() at
the start of each new run to clear previous data.
"""

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class TokenUsage:
    """Stores prompt and completion token counts for one LLM call."""
    prompt_tokens: int = 0
    completion_tokens: int = 0

    @property
    def total(self) -> int:
        """Total tokens used (prompt + completion)."""
        return self.prompt_tokens + self.completion_tokens


class TokenTracker:
    """Accumulates token usage and activity logs across pipeline nodes."""

    def __init__(self) -> None:
        self._usage: Dict[str, TokenUsage] = {}
        self._activity_log: List[str] = []

    # ── Activity log ──────────────────────────────────────────────────────────

    def log(self, node: str, message: str) -> None:
        """
        Append a message to the activity log.

        Args:
            node:    Name of the pipeline node (e.g. 'search_node').
            message: Human-readable description of what happened.
        """
        self._activity_log.append(f"[{node}] {message}")

    def get_log(self) -> List[str]:
        """Return a copy of all activity log entries."""
        return self._activity_log.copy()

    # ── Token recording ───────────────────────────────────────────────────────

    def record(self, node: str, prompt_tokens: int, completion_tokens: int) -> None:
        """
        Record token usage for a named pipeline node.

        Args:
            node:              Name of the node (e.g. 'summarize_node').
            prompt_tokens:     Tokens used in the prompt.
            completion_tokens: Tokens returned in the completion.
        """
        if node not in self._usage:
            self._usage[node] = TokenUsage()
        self._usage[node].prompt_tokens += prompt_tokens
        self._usage[node].completion_tokens += completion_tokens

    def total_tokens(self) -> int:
        """Return the grand total of all tokens used."""
        return sum(u.total for u in self._usage.values())

    # ── Reset ─────────────────────────────────────────────────────────────────

    def reset(self) -> None:
        """Clear all token records and activity log entries."""
        self._usage = {}
        self._activity_log = []

    # ── Display ───────────────────────────────────────────────────────────────

    def display_activity_log(self) -> str:
        """Return a formatted box showing all activity log entries."""
        title = " Agent Activity Log "
        entries = self._activity_log if self._activity_log else ["(no activity recorded)"]
        width = max(len(title) + 4, max(len(e) for e in entries) + 4)

        top    = "╭" + title.center(width, "─") + "╮"
        bottom = "╰" + "─" * width + "╯"
        rows   = [f"│ {e:<{width - 2}} │" for e in entries]

        return "\n".join([top] + rows + [bottom])

    def display_token_summary(self) -> str:
        """Return a formatted box showing per-node token usage."""
        if not self._usage:
            return ""

        title = " Token Usage Summary "
        col_node  = max(len("Node"),  max(len(n) for n in self._usage))
        col_p     = max(len("Prompt"),      7)
        col_c     = max(len("Completion"),  10)
        col_t     = max(len("Total"),       7)
        row_width = col_node + col_p + col_c + col_t + 9   # padding + separators

        width  = max(len(title) + 4, row_width + 2)
        top    = "╭" + title.center(width, "─") + "╮"
        bottom = "╰" + "─" * width + "╯"

        def row(node: str, prompt: str, completion: str, total: str) -> str:
            inner = (
                f" {node:<{col_node}}  "
                f"{prompt:>{col_p}}  "
                f"{completion:>{col_c}}  "
                f"{total:>{col_t}} "
            )
            return f"│{inner:<{width}}│"

        header    = row("Node", "Prompt", "Completion", "Total")
        separator = "│" + "─" * width + "│"
        data_rows = [
            row(n, f"{u.prompt_tokens:,}", f"{u.completion_tokens:,}", f"{u.total:,}")
            for n, u in self._usage.items()
        ]
        total_row = row(
            "TOTAL",
            f"{sum(u.prompt_tokens  for u in self._usage.values()):,}",
            f"{sum(u.completion_tokens for u in self._usage.values()):,}",
            f"{self.total_tokens():,}",
        )

        return "\n".join(
            [top, header, separator] + data_rows + [separator, total_row, bottom]
        )


# ── Module-level singleton ────────────────────────────────────────────────────
tracker = TokenTracker()
