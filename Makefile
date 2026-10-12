.PHONY: setup test results examples

BACKEND ?= manual
MODEL ?=
RUN ?= first-run

setup:
	uv sync --locked

test:
	uv run pytest

results:
	uv run playbook-results

examples:
	uv run playbook-examples --backend "$(BACKEND)" --model "$(MODEL)" --run "$(RUN)"

