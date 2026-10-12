"""Test benchmark scoring and safe, repeatable documentation regeneration."""

import json
import re
import shutil
from pathlib import Path

import pytest

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


@pytest.fixture
def result_project(tmp_path, monkeypatch):
    """Give the generator isolated documents and its real fixture and link inputs."""
    root = results.ROOT
    for folder in ("tests/fixtures", ".claude", ".github", "chat", "checks"):
        shutil.copytree(root / folder, tmp_path / folder, ignore=shutil.ignore_patterns("__pycache__"))
    for workflow in results.WORKFLOWS:
        folder = tmp_path / "workflows" / workflow
        folder.mkdir(parents=True)
        shutil.copyfile(root / "workflows" / workflow / "README.md", folder / "README.md")
    (tmp_path / "README.md").write_text(
        "Overview.\n<!-- CHECKS:START -->\nstale checks\n<!-- CHECKS:END -->\nKeep the pending example.\n")
    (tmp_path / "docs").mkdir()
    (tmp_path / "docs/SETUP.md").write_text(
        "Setup.\n<!-- RESULTS:START -->\nstale counts\n<!-- RESULTS:END -->\n"
        "<!-- TOOLS:START -->\nstale tools\n<!-- TOOLS:END -->\nKeep the review steps.\n")
    monkeypatch.setattr(results, "ROOT", tmp_path)
    return tmp_path


def test_results_refreshes_both_documents_and_is_repeatable(result_project):
    """Regeneration must update moved sections, preserve prose and resolve tool links."""
    assert results.main() == 0
    readme = (result_project / "README.md").read_text()
    setup = (result_project / "docs/SETUP.md").read_text()
    assert "stale" not in readme + setup
    assert "What the AI does" in readme and "Claude Code skill" not in readme
    assert "Claude Code skill" in setup and "What the AI does" not in setup
    assert readme.startswith("Overview.\n") and readme.endswith("Keep the pending example.\n")
    assert setup.startswith("Setup.\n") and setup.endswith("Keep the review steps.\n")
    assert "planted structural issues" not in readme
    assert "planted structural issues" in setup and "not evidence of model accuracy" in setup
    assert "<picture>" not in readme
    for target in re.findall(r"\]\(([^)]+)\)", setup):
        filename = target.split("#", 1)[0] or "SETUP.md"
        assert (result_project / "docs" / filename).is_file()
    outputs = [result_project / name for name in ("README.md", "docs/SETUP.md", "results/checker-benchmark.json")]
    before = [path.read_bytes() for path in outputs]
    assert results.main() == 0
    assert [path.read_bytes() for path in outputs] == before
    assert not (result_project / "assets").exists()


@pytest.mark.parametrize("section", ["TOOLS", "RESULTS"])
@pytest.mark.parametrize("markers", [
    "<!-- TOOLS:START -->",
    "<!-- TOOLS:END -->\n<!-- TOOLS:START -->",
    "<!-- TOOLS:START -->\n<!-- TOOLS:START -->\n<!-- TOOLS:END -->",
])
def test_invalid_setup_markers_leave_all_outputs_unchanged(result_project, section, markers, capsys):
    """A malformed second document must not leave partially refreshed results."""
    setup = result_project / "docs/SETUP.md"
    markers = markers.replace("TOOLS", section)
    document = setup.read_text()
    start, end = f"<!-- {section}:START -->", f"<!-- {section}:END -->"
    document = document.split(start)[0] + markers + document.split(end)[1]
    setup.write_text(document)
    readme = (result_project / "README.md").read_bytes()
    assert results.main() == 2
    assert f"docs/SETUP.md must contain one ordered pair of {section} markers" in capsys.readouterr().out
    assert (result_project / "README.md").read_bytes() == readme
    assert setup.read_text() == document
    assert not (result_project / "results").exists()
