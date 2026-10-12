.PHONY: setup test results examples

BACKEND ?= manual
MODEL ?=
RUN ?= first-run

setup:
	uv sync --locked

test:
	uv run pytest

# Regenerate the README self-tests, setup tool table and benchmark details.
results:
	uv run playbook-results

examples:
	uv run playbook-examples --backend "$(BACKEND)" --model "$(MODEL)" --run "$(RUN)"

