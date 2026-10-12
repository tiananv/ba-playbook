"""Optional model backends with exact prompts, resumable files and run provenance."""

import hashlib
import json
import os
import subprocess
from datetime import datetime, timezone
from pathlib import Path

import httpx

BACKENDS = ("manual", "claude-cli", "anthropic", "openai", "openrouter")


class ModelError(Exception):
    """A model or configuration failure safe to show without a traceback."""


class PendingAnswer(ModelError):
    """A manual prompt is ready and is waiting for a pasted answer."""


def digest(text: str) -> str:
    """Return the SHA-256 of the exact UTF-8 text."""
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


def write_json(path: Path, data: dict) -> None:
    """Write readable JSON next to its corresponding run artefact."""
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def _api(prompt: str, backend: str, model: str) -> tuple[str, str]:
    key_name = {"anthropic": "ANTHROPIC_API_KEY", "openai": "OPENAI_API_KEY", "openrouter": "OPENROUTER_API_KEY"}[backend]
    key = os.environ.get(key_name, "").strip()
    if not key:
        raise ModelError(f"Set {key_name} in your environment, or use --backend manual.")
    headers = {"Content-Type": "application/json"}
    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}
    if backend == "anthropic":
        url = "https://api.anthropic.com/v1/messages"
        headers.update({"x-api-key": key, "anthropic-version": "2023-06-01"})
        payload["max_tokens"] = 6000
    else:
        headers["Authorization"] = f"Bearer {key}"
        url = "https://openrouter.ai/api/v1/chat/completions"
        payload["max_tokens"] = 6000
        if backend == "openai":
            url = "https://api.openai.com/v1/responses"
            payload = {"model": model, "input": prompt, "store": False, "max_output_tokens": 6000}
    try:
        with httpx.Client(timeout=180) as client:
            response = client.post(url, headers=headers, json=payload)
        response.raise_for_status()
        data = response.json()
        if backend == "anthropic":
            if data["stop_reason"] != "end_turn":
                raise ModelError("The provider did not finish a text answer. Start a new run with a suitable model.")
            text = "\n".join(item["text"] for item in data["content"] if item["type"] == "text")
        elif backend == "openai":
            if data["status"] != "completed":
                raise ModelError("The provider returned an incomplete response. Start a new run with a suitable model.")
            text = "\n".join(part["text"] for item in data["output"] if item["type"] == "message"
                             for part in item["content"] if part["type"] == "output_text")
        else:
            choice = data["choices"][0]
            if choice["finish_reason"] != "stop":
                raise ModelError("The provider did not finish a text answer. Start a new run with a suitable model.")
            text = choice["message"]["content"]
        return text, data.get("model") or model
    except httpx.HTTPStatusError as error:
        raise ModelError(f"{backend} returned HTTP {error.response.status_code}. Check access, model ID and quota.") from None
    except httpx.RequestError:
        raise ModelError(f"Could not reach {backend}. Check your connection and retry.") from None
    except (ValueError, KeyError, IndexError, TypeError, AttributeError):
        raise ModelError(f"{backend} returned an unreadable response. No example was accepted.") from None


def _claude(prompt: str, model: str) -> tuple[str, str]:
    try:
        result = subprocess.run(
            ["claude", "-p", "--model", model, "--output-format", "json", "--tools", "", "--disallowedTools", "mcp__*"],
            input=prompt, text=True, capture_output=True, timeout=240, check=False,
        )
        if result.returncode:
            raise ModelError("claude -p failed. Check Claude Code sign-in and the model ID.")
        data = json.loads(result.stdout)
        if data.get("is_error"):
            raise ModelError("Claude Code reported an error. No example was accepted.")
        models = list(data.get("modelUsage", {}))
        return data["result"], models[0] if len(models) == 1 else model
    except FileNotFoundError:
        raise ModelError("Install and sign in to Claude Code, or use --backend manual.") from None
    except subprocess.TimeoutExpired:
        raise ModelError("Claude Code timed out. Retry or use --backend manual.") from None
    except (ValueError, KeyError, TypeError, AttributeError):
        raise ModelError("Claude Code returned unreadable JSON. No example was accepted.") from None


def generate(prompt: str, output: Path, backend: str, model: str) -> Path:
    """Save a model answer with provenance, or prepare a manual prompt for later use."""
    if backend not in BACKENDS:
        raise ModelError(f"Choose a backend from: {', '.join(BACKENDS)}.")
    if not model.strip():
        raise ModelError("Set --model (or MODEL) to the actual model ID or chat model label.")
    output.parent.mkdir(parents=True, exist_ok=True)
    prompt_path = output.with_suffix(".prompt.md")
    metadata_path = output.with_suffix(".metadata.json")
    answer_path = output.with_suffix(".answer.md")
    identity = {"backend": backend, "requested_model": model, "prompt_sha256": digest(prompt)}
    previous = {}
    if metadata_path.exists():
        try:
            previous = json.loads(metadata_path.read_text(encoding="utf-8"))
            if not isinstance(previous, dict):
                raise ValueError("Expected a metadata object")
        except (ValueError, UnicodeError):
            raise ModelError("Run metadata is unreadable. Use a new --run name.") from None
        if any(previous.get(key) != value for key, value in identity.items()):
            raise ModelError("This run has different inputs or model settings. Use a new --run name.")
    if prompt_path.exists() and prompt_path.read_text(encoding="utf-8") != prompt:
        raise ModelError("Saved prompt differs from this request. Use a new --run name.")
    if output.exists():
        if previous.get("status") != "complete" or previous.get("output_sha256") != digest(output.read_text(encoding="utf-8")):
            raise ModelError("Existing output has no matching provenance or was edited. Use a new --run name.")
        return output
    prompt_path.write_text(prompt, encoding="utf-8")
    metadata = {**identity, "model_id": model, "model_id_source": "user-supplied",
                "timestamp_utc": datetime.now(timezone.utc).isoformat(), "status": "pending"}
    write_json(metadata_path, metadata)
    if backend == "manual" and not answer_path.exists():
        raise PendingAnswer(f"Paste {prompt_path} into your approved chat app. Save its full response to {answer_path}, then rerun.")
    try:
        if backend == "manual":
            answer, resolved_model = answer_path.read_text(encoding="utf-8"), model
        elif backend == "claude-cli":
            answer, resolved_model = _claude(prompt, model)
        else:
            answer, resolved_model = _api(prompt, backend, model)
        if not isinstance(answer, str) or not answer.strip():
            raise ModelError("The model answer is empty. No example was accepted.")
        output.write_text(answer, encoding="utf-8")
        metadata.update(status="complete", model_id=resolved_model, output_sha256=digest(answer),
                        model_id_source="user-supplied" if backend == "manual" or resolved_model == model else "provider-response")
        write_json(metadata_path, metadata)
        return output
    except ModelError:
        metadata["status"] = "error"
        write_json(metadata_path, metadata)
        raise
