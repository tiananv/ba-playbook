"""Test the benchmark scoring independently of the checkers' own issue counts."""

import json
from pathlib import Path

from checks.common import Issue
from playbook import results

FIXTURES = Path(__file__).parent / "fixtures"


def test_benchmark_has_no_misses_or_unexpected_flags():
    """The labelled fixture suite must pass before results are published."""
    benchmark = results.benchmark(FIXTURES)
    for row in benchmark["totals"].values():
        assert row["caught"] == row["planted"] > 0
        assert row["missed"] == row["unexpected"] == row["good_flagged"] == 0
        assert row["good"] > 0


def test_wrong_issue_does_not_count_as_caught(monkeypatch, tmp_path):
    """A warning at the wrong item is both a miss and an unexpected flag."""
    (tmp_path / "source.md").write_text("Synthetic source.")
    (tmp_path / "output.md").write_text("Synthetic output.")
    (tmp_path / "manifest.json").write_text(json.dumps([
        {"checker": "quote", "source": "source.md", "output": "output.md", "expected": [["missing_source", "REQ-001"]]}]))
    monkeypatch.setitem(results.CHECKERS, "quote", lambda source, output: [Issue("missing_source", "REQ-999", "Wrong item.")])
    row = results.benchmark(tmp_path)["totals"]["quote"]
    assert row["planted"] == 1 and row["caught"] == 0
    assert row["missed"] == 1 and row["unexpected"] == 1


def test_duplicate_warnings_are_not_double_counted(monkeypatch, tmp_path):
    """Repeated warnings cannot inflate the number of planted defects caught."""
    (tmp_path / "source.md").write_text("Synthetic source.")
    (tmp_path / "output.md").write_text("Synthetic output.")
    (tmp_path / "manifest.json").write_text(json.dumps([
        {"checker": "quote", "source": "source.md", "output": "output.md", "expected": [["missing_source", "REQ-001"]]}]))
    monkeypatch.setitem(results.CHECKERS, "quote", lambda source, output: [Issue("missing_source", "REQ-001", "Repeated.")] * 2)
    row = results.benchmark(tmp_path)["totals"]["quote"]
    assert row["caught"] == 1 and row["unexpected"] == 1


def test_false_positive_on_good_document_is_counted(monkeypatch):
    """The benchmark reports false flags as well as caught planted defects."""
    monkeypatch.setitem(results.CHECKERS, "quote", lambda source, output: [Issue("format", "document", "False alarm.")])
    row = results.benchmark(FIXTURES)["totals"]["quote"]
    assert row["good_flagged"] == row["good"] and row["unexpected"] > 0

