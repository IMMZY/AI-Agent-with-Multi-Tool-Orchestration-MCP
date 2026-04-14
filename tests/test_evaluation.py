"""
test_evaluation.py — Tests for the evaluation module.
"""

from src.evaluation.evaluator import evaluate_research, EvaluationResult
from src.graph.state import ResearchState


def _make_state(**kwargs) -> ResearchState:
    base: ResearchState = {
        "query": "test",
        "search_results": [],
        "extracted_content": "",
        "summary": "",
        "status": "",
    }
    return {**base, **kwargs}


class TestEvaluateResearch:

    def test_passes_with_complete_summary(self):
        state = _make_state(summary=(
            "SUMMARY:\nThis is a test summary that is long enough to pass.\n\n"
            "KEY POINTS:\n- Point one\n- Point two\n\n"
            "SOURCES:\n- https://example.com\n- https://other.com"
        ))
        result: EvaluationResult = evaluate_research(state)
        assert result.passed is True
        assert result.completeness is True
        assert result.source_count >= 1

    def test_fails_when_summary_missing(self):
        state = _make_state(summary="KEY POINTS:\n- p\nSOURCES:\n- https://x.com")
        result = evaluate_research(state)
        assert result.completeness is False
        assert result.passed is False
        assert "SUMMARY" in result.feedback

    def test_fails_with_empty_summary(self):
        state = _make_state(summary="")
        result = evaluate_research(state)
        assert result.passed is False

    def test_source_count_is_correct(self):
        state = _make_state(summary=(
            "SUMMARY:\nok\nKEY POINTS:\n- p\n"
            "SOURCES:\n- https://a.com\n- https://b.com\n- https://c.com"
        ))
        result = evaluate_research(state)
        assert result.source_count == 3

        