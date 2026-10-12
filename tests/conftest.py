"""Keep tests offline and clear inherited model credentials."""

import socket

import pytest

import llm


@pytest.fixture(autouse=True)
def offline(monkeypatch):
    """Deny network sockets and live Claude calls, and clear inherited API credentials."""
    def denied(*args, **kwargs):
        """Fail if a test accidentally tries to reach a live service."""
        raise AssertionError("Tests must mock live model and network access.")

    monkeypatch.setattr(socket.socket, "connect", denied)
    monkeypatch.setattr(socket, "create_connection", denied)
    monkeypatch.setattr(llm, "_claude", denied)
    for name in ("ANTHROPIC_API_KEY", "OPENAI_API_KEY", "OPENROUTER_API_KEY"):
        monkeypatch.delenv(name, raising=False)
