# Running and recording the workflows

The clinic inputs are fictional practice material written for this project. They
aren't model outputs. For other inputs, start with [what stays out of AI](../WHAT-NEVER-GOES-INTO-AI.md)
and the [context templates](../context/). Run commands from the repository folder
with uv and Python 3.11 installed.

## Recorded examples

```sh
uv run playbook-examples --backend manual --model "your-chat-model" --run first-run
```

Replace the model label with the actual model shown in your chat app. This command
prepares prompts from the shared workflow instructions and fictional inputs.
It doesn't read other context folders or local files.
Copy each printed `.prompt.md` into a fresh chat and save the unedited response to
the matching `.answer.md`. Do not use a test document as a model answer. Rerun the
same command to import the answers and run the checkers. Use the same selected model
for the whole run, or start a new run name when you change it.

The review board prepares independent prompts for tester, developer, risk and
compliance, and end user. After all responses are saved, the next invocation
prepares the consolidator prompt with the original spec and all raw reviews. Save
that response and rerun again. Manual conversations can be run concurrently or in
turn. Record which you did in the review. The saved model name is the label you
entered, and the saved time is when you imported the answer.

## Automated backends

| Backend | What you need | Model |
| --- | --- | --- |
| manual | An approved chat app | Its displayed model label, supplied by you |
| claude-cli | Claude Code installed and signed in | A supported model ID or alias |
| anthropic | Export ANTHROPIC_API_KEY | An accessible Anthropic model ID |
| openai | Export OPENAI_API_KEY | An accessible OpenAI model ID |
| openrouter | Export OPENROUTER_API_KEY | A provider/model ID supported by your account |

For example, after exporting the matching key:

```sh
uv run playbook-examples --backend openai --model "your-model-id" --run api-run
```

Other backends use the same command with their name and model. For Claude Code,
use `--backend claude-cli` and a new run name.
`.env.example` documents variables, but `.env` is not loaded automatically. Never
put a real key in a command, tracked file, prompt or issue. Model availability and
cost depend on your account. There is no default model.

API and CLI runs issue independent reviewer calls concurrently, then consolidate
only after every role completes. The other workflows each make a single call.
The Claude Code command uses the saved prompts directly. It doesn't run the
interactive skills or give the model other tools.

## Files, resuming and failures

Each workflow writes to `workflows/<workflow>/examples/<run>/`:

- `<stage>.prompt.md`: the prompt sent to the model or prepared for copying.
- `<stage>.metadata.json`: the model, time, status and details used to spot changed files.
- `<stage>.answer.md`: the answer pasted from a chat app.
- `<stage>.md`: the original model answer saved by the script, still awaiting review.
- `check.json`: checker findings and pending sign-off.
- `traceability.md`: the requirement matrix for the test workflow.

A saved answer is reused if its inputs, settings and contents still match. Use a
new `--run` name if any of those change. Keep the original result, including
mistakes. Edit a copy for review and rerun the checker on that copy.

CLI exit `0` means generation and structural checks completed, `1` means findings
need attention, and `2` means a manual answer is pending or a configuration/input
error needs fixing. A pending run is waiting for an answer; no example has been generated.

Run only one workflow with
`uv run playbook-examples --workflow spec-review-board --backend manual --model "your-chat-model" --run first-run`.
Keep a separate run name for work happening at the same time. Run folders stay
local by default. Before sharing, check the files and where the answers came from.
A person still needs to check meaning, omissions and priorities, and decide
whether the draft is acceptable.

## Tool format references

Packaging follows the official [Claude skills](https://code.claude.com/docs/en/skills)
and [subagents](https://code.claude.com/docs/en/sub-agents) formats, and VS Code
[instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions),
[prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files),
[custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) and
[skills](https://code.visualstudio.com/docs/agent-customization/agent-skills).
Prompt files are supported by the Local agent and are not loaded by Agent Host.
The skill files use the same shared prompts. Which tools and reviewers load
depends on the installed version and organisation's settings. I still need to
check them in the tools I'll use.
