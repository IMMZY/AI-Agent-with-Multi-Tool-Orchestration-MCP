# Evaluation

The `src/evaluation/evaluator.py` module scores each research run using heuristic checks.

## Metrics

| Metric | Description | Pass Condition |
|---|---|---|
| `completeness` | All three sections present (SUMMARY, KEY POINTS, SOURCES) | All three found |
| `source_count` | Number of source URLs in the output | ≥ 1 |
| `summary_length` | Character length of the full summary | ≥ 100 chars |
| `passed` | Overall pass/fail | All above pass |

## Usage

```python
from src.evaluation.evaluator import evaluate_research

result = evaluate_research(final_state)
print(result.passed)     # True / False
print(result.feedback)   # "All checks passed." or list of issues
print(result.source_count)
```

## Running Evaluation Tests

```bash
pytest tests/test_evaluation.py -v
```
