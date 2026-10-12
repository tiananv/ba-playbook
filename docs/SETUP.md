# Setup and running the playbook

Use the fictional clinic inputs to try the workflows. Before using any other
material, follow the [information-handling guide](../WHAT-NEVER-GOES-INTO-AI.md)
and [method](../METHOD.md). Return to the [playbook overview](../README.md) for the
BA problem and the limits of the checks.

## Reproduce the checker self-tests

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11.
Run these commands from a local copy of the repository. No model account is needed.

```sh
make setup
make results
uv run pytest
```

`make setup` runs `uv sync --locked` to install the pinned dependencies into the
local `.venv`. `make results` runs the labelled checker fixtures, writes
[benchmark details](../results/checker-benchmark.json), and refreshes the generated
tables in the README and this guide. `uv run pytest` runs the offline test suite;
it makes no live model calls. `make test` runs the same suite.

## The same workflow in three tools

<!-- TOOLS:START -->
| Workflow | Claude Code skill | Copilot prompt | Chat instructions |
| --- | --- | --- | --- |
| [workshop-to-requirements](../workflows/workshop-to-requirements/README.md) | [SKILL.md](../.claude/skills/workshop-to-requirements/SKILL.md) | [prompt.md](../.github/prompts/workshop-to-requirements.prompt.md) | [Paste guide](../chat/workshop-to-requirements.md) |
| [spec-review-board](../workflows/spec-review-board/README.md) | [SKILL.md](../.claude/skills/spec-review-board/SKILL.md) | [prompt.md](../.github/prompts/spec-review-board.prompt.md) | [Paste guide](../chat/spec-review-board.md) |
| [requirements-to-tests](../workflows/requirements-to-tests/README.md) | [SKILL.md](../.claude/skills/requirements-to-tests/SKILL.md) | [prompt.md](../.github/prompts/requirements-to-tests.prompt.md) | [Paste guide](../chat/requirements-to-tests.md) |
<!-- TOOLS:END -->

Copilot prompt files work in VS Code's Local agent. Agent Host sessions use the
included [.github/skills](../.github/skills/) wrappers. Both use the same workflow
instructions. See the [official compatibility note](https://code.visualstudio.com/docs/agent-customization/prompt-files).
Check that skills and reviewer agents load in your installed clients and record
any version-specific differences before relying on them.

## Record a worked example

The public example is pending until a real model run and a human review exist.
Start with workshop-to-requirements on the fictional clinic transcript. After setup,
replace the model label with the actual label shown in your approved chat app:

```sh
uv run playbook-examples --workflow workshop-to-requirements --backend manual --model "your-chat-model" --run first-run
```

1. Paste the saved prompt into a fresh conversation. The first invocation prints
   the prompt and answer paths and exits with status `2`, meaning an answer is
   pending. Save the real, unedited answer to the printed answer path.
2. Rerun the same command to import the answer and record the structural checks.
   Keep the prompt, original answer, model metadata and checker report together.
   Inspect any findings before proceeding; a checker pass alone is not sign-off.
3. Compare every requirement with the transcript, including qualifiers, omissions
   and open decisions. Put corrections in a separate `reviewed.md` in the run folder
   and explain each correction with its source. Keep the original output unchanged.
4. Check the corrected draft with the command below. Keep its report alongside the
   original check, including any findings still awaiting resolution.
5. Record your actual review decision in a separate `review.md`: what you checked,
   why you changed it, unresolved questions, the source and reviewed draft versions,
   who reviewed them and the actual sign-off date if accepted. The runner leaves
   `human_sign_off` pending; only a person's recorded decision supplies acceptance.
6. Select the permitted evidence for publication and replace the README's pending
   section with links to the original draft, marked corrections and review decision.
   Run folders are gitignored, so selecting evidence for publication is a separate
   step. Leave the example pending until these records exist.

For the run name above, check the corrected draft from the repository root:

```sh
uv run quote-check workflows/workshop-to-requirements/input.md workflows/workshop-to-requirements/examples/first-run/reviewed.md > workflows/workshop-to-requirements/examples/first-run/reviewed-check.txt
```

Read `reviewed-check.txt` even if the command exits with status `1`, which means
findings need attention. Keep the model fixed for a named run. Start a new run name
if you change the source, prompt, backend or model. See the
[runner guide](../workflows/README.md) for file names, metadata, resuming and failures.

## Run all workflows or choose another backend

To prepare all workflows with the same approved chat model:

```sh
make examples BACKEND=manual MODEL="your-chat-model" RUN=first-run
```

Paste each saved prompt, save the real answers to the printed paths, then rerun the
same command. The review board needs a further consolidation pass after its role
responses are saved. Preserve the original role responses as well as the final draft.

An API or Claude Code run uses the same target with its backend and model ID:

```sh
make examples BACKEND=openai MODEL="your-model-id" RUN=api-run
make examples BACKEND=claude-cli MODEL="your-model-id" RUN=cli-run
```

Choose a backend and model available to your approved account. API backends need
the matching key exported in your environment; Claude Code needs an installed,
signed-in CLI. The [backend table](../workflows/README.md#automated-backends) covers
`manual`, `claude-cli`, `anthropic`, `openai` and `openrouter`.
[.env.example](../.env.example) documents the variables; `.env` is not loaded
automatically. Never put a real key in a command, prompt or tracked file.
