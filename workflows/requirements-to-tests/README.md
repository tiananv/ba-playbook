# Requirements to tests

Use when agreed requirements need acceptance test coverage and gaps made visible.

**Inputs:** a permitted requirement baseline with REQ headings and agreed business rules. The [fictional input](input.md) belongs to the Paper Lantern
Community Clinic exercise and was written by the repo authors. It is not model output.
The [canonical prompt](prompt.md) defines the task. **Outputs:** Given/When/Then test cases linked to REQ IDs and a generated traceability matrix.
Model examples are pending; [examples/README.md](examples/README.md) explains why.

## Claude Code

Open this repository in Claude Code and invoke `/requirements-to-tests` with the source file path
and a separate output path. The [project skill](../../.claude/skills/requirements-to-tests/SKILL.md)
loads the shared prompt. Provide only approved context. Inspect the output and run
the checker below if the tool has not run it. Interactive skill use does not record
API harness metadata automatically.

## GitHub Copilot in VS Code

With the Local agent, invoke `/requirements-to-tests` from the
[prompt file](../../.github/prompts/requirements-to-tests.prompt.md) and attach the source file.
For an Agent Host session using the Copilot harness, load the
[skill](../../.github/skills/requirements-to-tests/SKILL.md) instead. Select the approved model
and provide an output path. If the command does not appear, inspect the customisation
view and use the chat route while checking your installed version. Do not assume
unloaded instructions were followed.

## ChatGPT or another chat app

Use [the paste guide](../../chat/requirements-to-tests.md) with an approved account. Paste the
source contents, not just a local filename. Save the unedited Markdown response.
Run the checker locally; a chat app cannot attest that a local checker passed.

Use the original source and output side by side when checking meaning. Treat open
questions as decisions to resolve, not permission to fill gaps with assumed rules.

## Run and check

```sh
uv run playbook-examples --workflow requirements-to-tests --backend manual --model "your-chat-model" --run first-run
uv run trace-check workflows/requirements-to-tests/input.md path/to/your-output.md --matrix .cache/traceability.md
```

Replace the model label and output path. The first command prepares prompts, then
imports real answers on subsequent runs. See [the runner guide](../README.md) for
all backends and the exact answer-file steps. The second command checks a saved
Markdown file from any tool. See [the format contract](../../checks/README.md).
Passing a checker is structural evidence only. The responsible person checks meaning,
omissions and acceptance, records the decision and retains final sign-off.
