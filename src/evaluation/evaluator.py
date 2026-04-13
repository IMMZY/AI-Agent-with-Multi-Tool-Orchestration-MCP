"""
evaluator.py — Heuristic + LLM-as-judge evaluation of research output.

Provides evaluate_research() which scores a completed ResearchState on:
    - completeness  (are all required sections present?)
    - source_count  (how many sources were cited?)
    - length        (is the summary a reasonable length?)
    - llm_score     (optional: LLM grades the output 1-10)
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

if TYPE_CHECKING:
    from src.graph.state import ResearchState


@dataclass
class EvaluationResult:
    """Holds scores and feedback for one research run."""
    completeness: bool      # True if SUMMARY, KEY POINTS, SOURCES are all present
    source_count: int       # Number of source URLs found in the summary
    summary_length: int     # Character length of the summary
    passed: bool            # Overall pass/fail
    feedback: str           # Human-readable feedback string


def evaluate_research(state: "ResearchState") -> EvaluationResult:
    """
    Evaluate the quality of a completed research pipeline run.

    Uses heuristic checks (no extra API call required).

    Args:
        state: The final ResearchState after all nodes have executed.

    Returns:
        An EvaluationResult with scores and feedback.
    """
    summary = state.get("summary", "")

    # ── Heuristic checks ─────────────────────────────────────────────────────
    has_summary = "SUMMARY:" in summary
    has_key_points = "KEY POINTS:" in summary
    has_sources = "SOURCES:" in summary
    completeness = has_summary and has_key_points and has_sources

    source_count = summary.count("- http")
    summary_length = len(summary)

    passed = completeness and source_count >= 1 and summary_length >= 100

    # ── Feedback ──────────────────────────────────────────────────────────────
    issues: list[str] = []
    if not has_summary:
        issues.append("Missing SUMMARY section.")
    if not has_key_points:
        issues.append("Missing KEY POINTS section.")
    if not has_sources:
        issues.append("Missing SOURCES section.")
    if source_count < 1:
        issues.append("No source URLs found.")
    if summary_length < 100:
        issues.append("Summary is too short.")

    feedback = "All checks passed." if not issues else " ".join(issues)

    return EvaluationResult(
        completeness=completeness,
        source_count=source_count,
        summary_length=summary_length,
        passed=passed,
        feedback=feedback,
    )
