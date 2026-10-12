"""Test backend request formats, failure handling and saved details without model calls."""

import json
import subprocess
from datetime import datetime
from types import SimpleNamespace

import httpx
import pytest

import llm

CLAUDE_CALL = llm._claude
HTTP_CLIENT = httpx.Client


def test_manual_round_trip_and_tampering(tmp_path):
    """Keep an exact prompt and raw answer, and refuse changed inputs or outputs."""
    output = tmp_path / "output.md"
    prompt = "A prompt with curly quotes: “source”.\n"
    with pytest.raises(llm.PendingAnswer):
        llm.generate(prompt, output, "manual", "test-chat-label")
    assert not output.exists()
    assert output.with_suffix(".prompt.md").read_text() == prompt
    answer = "A synthetic answer for this test only.\n"
    output.with_suffix(".answer.md").write_text(answer)
    llm.generate(prompt, output, "manual", "test-chat-label")
    metadata = json.loads(output.with_suffix(".metadata.json").read_text())
    assert metadata["prompt_sha256"] == llm.digest(prompt)
    assert metadata["output_sha256"] == llm.digest(answer)
    assert metadata["model_id"] == "test-chat-label"
    assert metadata["model_id_source"] == "user-supplied"
    assert datetime.fromisoformat(metadata["timestamp_utc"]).utcoffset().total_seconds() == 0
    assert output.read_text() == answer
    assert llm.generate(prompt, output, "manual", "test-chat-label") == output
    with pytest.raises(llm.ModelError, match="different inputs"):
        llm.generate(prompt + "Changed", output, "manual", "test-chat-label")
    output.write_text("Edited after generation.")
    with pytest.raises(llm.ModelError, match="edited"):
        llm.generate(prompt, output, "manual", "test-chat-label")


@pytest.mark.parametrize("backend", ["anthropic", "openai", "openrouter"])
def test_missing_key_is_friendly_and_recorded(backend, tmp_path):
    """An absent key makes no HTTP request and leaves a readable failure state."""
    output = tmp_path / "output.md"
    with pytest.raises(llm.ModelError, match="Set .*_API_KEY"):
        llm.generate("A synthetic test prompt.", output, backend, "test-model")
    assert json.loads(output.with_suffix(".metadata.json").read_text())["status"] == "error"
    assert not output.exists()


@pytest.mark.parametrize("backend", ["anthropic", "openai", "openrouter"])
def test_provider_request_and_response_contract(backend, monkeypatch, tmp_path):
    """Use mocked HTTP to check headers, prompt payloads and reported model IDs."""
    monkeypatch.setenv(backend.upper() + "_API_KEY", "test-placeholder")
    prompt = "A synthetic prompt, for tests only."

    def respond(request):
        """Validate one provider request and return a synthetic protocol response."""
        payload = json.loads(request.content)
        assert payload["model"] == "test-model"
        if backend == "openai":
            assert str(request.url) == "https://api.openai.com/v1/responses"
            assert payload["input"] == prompt and payload["store"] is False
            data = {"model": "resolved-test-model", "status": "completed", "output": [
                {"type": "reasoning"}, {"type": "message", "content": [{"type": "output_text", "text": "First."}]},
                {"type": "message", "content": [{"type": "output_text", "text": "Second."}]}]}
        elif backend == "anthropic":
            assert request.headers["x-api-key"] == "test-placeholder"
            assert request.headers["anthropic-version"] == "2023-06-01"
            assert payload["messages"][0]["content"] == prompt
            data = {"model": "resolved-test-model", "stop_reason": "end_turn", "content": [{"type": "text", "text": "First."}]}
        else:
            assert str(request.url) == "https://openrouter.ai/api/v1/chat/completions"
            assert payload["messages"][0]["content"] == prompt
            data = {"model": "resolved-test-model", "choices": [{"finish_reason": "stop", "message": {"content": "First."}}]}
        if backend != "anthropic":
            assert request.headers["Authorization"] == "Bearer test-placeholder"
        return httpx.Response(200, json=data)

    monkeypatch.setattr(llm.httpx, "Client", lambda **kwargs: HTTP_CLIENT(transport=httpx.MockTransport(respond), **kwargs))
    output = tmp_path / "output.md"
    llm.generate(prompt, output, backend, "test-model")
    metadata = json.loads(output.with_suffix(".metadata.json").read_text())
    assert metadata["model_id"] == "resolved-test-model"
    assert metadata["model_id_source"] == "provider-response"
    assert output.read_text() == ("First.\nSecond." if backend == "openai" else "First.")
    assert "test-placeholder" not in output.with_suffix(".metadata.json").read_text()


@pytest.mark.parametrize("status,body,match", [(401, {"error": "private provider diagnostic"}, "HTTP 401"), (429, {}, "HTTP 429"), (200, {}, "unreadable"), (200, [], "unreadable"), (200, {"status": "incomplete"}, "incomplete")])
def test_http_errors_do_not_expose_provider_bodies(status, body, match, monkeypatch, tmp_path):
    """Provider diagnostics may contain private information, so show safe summaries."""
    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    transport = httpx.MockTransport(lambda request: httpx.Response(status, json=body))
    monkeypatch.setattr(llm.httpx, "Client", lambda **kwargs: HTTP_CLIENT(transport=transport, **kwargs))
    with pytest.raises(llm.ModelError, match=match) as error:
        llm.generate("Synthetic test.", tmp_path / "output.md", "openai", "test-model")
    assert "private provider diagnostic" not in str(error.value)


def test_network_failure_is_friendly(monkeypatch, tmp_path):
    """Timeouts produce a useful error without dumping the HTTP request."""
    def timeout(request):
        """Simulate a connection timeout entirely in memory."""
        raise httpx.ConnectTimeout("private transport details")

    monkeypatch.setenv("OPENAI_API_KEY", "test-placeholder")
    monkeypatch.setattr(llm.httpx, "Client", lambda **kwargs: HTTP_CLIENT(transport=httpx.MockTransport(timeout), **kwargs))
    with pytest.raises(llm.ModelError, match="Could not reach"):
        llm.generate("Synthetic test.", tmp_path / "output.md", "openai", "test-model")


def test_claude_uses_stdin_without_shell_or_tools(monkeypatch):
    """Quote-like input stays data and the headless call requests no tool access."""
    def run(args, **kwargs):
        """Capture the CLI arguments without launching a subprocess."""
        assert args[:2] == ["claude", "-p"]
        assert args[args.index("--tools") + 1] == ""
        assert args[args.index("--disallowedTools") + 1] == "mcp__*"
        assert kwargs["input"] == "Synthetic $(not-a-command) prompt."
        assert "shell" not in kwargs
        return SimpleNamespace(returncode=0, stdout=json.dumps({"result": "Synthetic answer.", "modelUsage": {"resolved-model": {}}}))

    monkeypatch.setattr(llm.subprocess, "run", run)
    assert CLAUDE_CALL("Synthetic $(not-a-command) prompt.", "test-model") == ("Synthetic answer.", "resolved-model")


@pytest.mark.parametrize("failure", [FileNotFoundError(), subprocess.TimeoutExpired("claude", 1)])
def test_claude_unavailable_is_friendly(failure, monkeypatch):
    """Missing executables and timeouts return friendly model errors."""
    def fail(*args, **kwargs):
        """Simulate a subprocess failure without starting Claude."""
        raise failure

    monkeypatch.setattr(llm.subprocess, "run", fail)
    with pytest.raises(llm.ModelError):
        CLAUDE_CALL("Synthetic test.", "test-model")


def test_blank_manual_answer_is_not_accepted(tmp_path):
    """A blank pasted response must not become a recorded model output."""
    output = tmp_path / "output.md"
    output.with_suffix(".answer.md").write_text(" \n")
    with pytest.raises(llm.ModelError, match="empty"):
        llm.generate("Synthetic test.", output, "manual", "test-model")
    assert not output.exists()


def test_model_must_be_explicit(tmp_path):
    """Do not silently choose a model or invent recorded details for a manual answer."""
    with pytest.raises(llm.ModelError, match="Set --model"):
        llm.generate("Synthetic test.", tmp_path / "output.md", "manual", "")
