"""End-to-end workflow tests using fixture answers and mocked independent calls."""

import json
import shutil
import threading
from pathlib import Path

import pytest

from checks.common import read
from playbook import examples

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "tests" / "fixtures"


@pytest.fixture
def workspace(tmp_path, monkeypatch):
    """Copy only workflow instructions and replace sources with labelled test inputs."""
    shutil.copytree(ROOT / "workflows", tmp_path / "workflows", ignore=shutil.ignore_patterns("examples"))
    sources = ["quote/transcript.md", "review/spec.md", "trace/requirements.md"]
    for name, source in zip(examples.WORKFLOWS, sources):
        (tmp_path / "workflows" / name / "input.md").write_text(read(FIXTURES / source))
    monkeypatch.setattr(examples, "ROOT", tmp_path)
    return tmp_path


def test_manual_pipeline_prepares_imports_consolidates_and_resumes(workspace, capsys):
    """Manual mode requires real answer files at each stage and never fabricates one."""
    args = ["--backend", "manual", "--model", "fixture-model", "--run", "test-run"]
    assert examples.main(args) == 2
    prompts = list(workspace.glob("workflows/*/examples/test-run/*.prompt.md"))
    assert len(prompts) == 6
    for prompt in prompts:
        workflow = prompt.parts[-4]
        fixture = {"workshop-to-requirements": "quote/good.md", "spec-review-board": "review/good.md", "requirements-to-tests": "trace/good.md"}[workflow]
        prompt.with_name(prompt.name.replace(".prompt.md", ".answer.md")).write_text(read(FIXTURES / fixture))
    assert examples.main(args) == 2
    board = workspace / "workflows/spec-review-board/examples/test-run"
    assert not (board / "output.md").exists()
    assert all(f'<review role="{role}">' in read(board / "output.prompt.md") for role in examples.ROLES)
    (board / "output.answer.md").write_text(read(FIXTURES / "review/good.md"))
    assert examples.main(args) == 0
    before = {path: path.read_bytes() for path in workspace.glob("workflows/*/examples/test-run/*.metadata.json")}
    assert examples.main(args) == 0
    assert all(path.read_bytes() == content for path, content in before.items())
    for path in workspace.glob("workflows/*/examples/test-run/check.json"):
        check = json.loads(read(path))
        assert check["issues"] == [] and check["human_sign_off"] == "pending"
    assert "Human sign-off is still pending" in capsys.readouterr().out


def test_reviewers_run_concurrently_before_consolidation(workspace, monkeypatch):
    """A barrier proves the four independent reviewer calls overlap in time."""
    barrier = threading.Barrier(4)
    completed, calls = set(), []
    lock = threading.Lock()

    def generate(prompt, output, backend, model):
        """Record isolated reviewer prompts and return a known test fixture."""
        if output.stem in examples.ROLES:
            assert "<review role=" not in prompt
            barrier.wait(timeout=5)
            with lock:
                completed.add(output.stem)
        else:
            assert completed == set(examples.ROLES)
            assert prompt.count("<review role=") == 4
        with lock:
            calls.append(output.stem)
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(read(FIXTURES / "review/good.md"))
        return output

    monkeypatch.setattr(examples, "generate", generate)
    status, _ = examples.run_workflow(workspace, "spec-review-board", "openai", "fixture-model", "parallel")
    assert status == "complete" and len(calls) == 5 and calls[-1] == "output"


def test_checker_failure_is_a_failing_run(workspace, monkeypatch, capsys):
    """Save a flawed model answer for inspection but return a failing exit status."""
    def generate(prompt, output, backend, model):
        """Use an explicitly flawed synthetic fixture instead of a live model."""
        output.parent.mkdir(parents=True, exist_ok=True)
        output.write_text(read(FIXTURES / "quote/flawed.md"))
        return output

    monkeypatch.setattr(examples, "generate", generate)
    assert examples.main(["--workflow", "workshop-to-requirements", "--model", "fixture-model"]) == 1
    assert "checks failed" in capsys.readouterr().out


def test_changed_prompt_requires_new_run(workspace, capsys):
    """Do not attach an old manual answer to a different source or instruction set."""
    args = ["--workflow", "workshop-to-requirements", "--model", "fixture-model"]
    assert examples.main(args) == 2
    source = workspace / "workflows/workshop-to-requirements/input.md"
    source.write_text(read(source) + "\nAn extra source line.\n")
    assert examples.main(args) == 2
    assert "different inputs" in capsys.readouterr().out


def test_missing_model_is_friendly(workspace, capsys):
    """An invalid invocation should explain how to proceed without a traceback."""
    assert examples.main(["--model", ""]) == 2
    text = capsys.readouterr().out
    assert "Set --model" in text and "Traceback" not in text


def test_run_name_cannot_escape_examples(workspace):
    """A run identifier cannot become an arbitrary filesystem path."""
    with pytest.raises(SystemExit) as error:
        examples.main(["--run", "../../outside", "--model", "fixture-model"])
    assert error.value.code == 2

