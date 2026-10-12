# Running and recording the workflows

The fictional inputs are safe learning material written for this project. They are
not model outputs. Use the [context templates](../context/) for later work only after
checking [information handling](../WHAT-NEVER-GOES-INTO-AI.md). Work from the repository
root after `make setup`. The checkers themselves need no model or credentials.

## Recorded examples

```sh
make examples BACKEND=manual MODEL="your-chat-model" RUN=first-run
```

Replace the model label with the actual model shown in your chat app. This command
prepares prompts from the canonical workflow instructions and fictional inputs.
It deliberately does not read arbitrary context folders or local private files.
Copy each printed `.prompt.md` into a fresh chat and save the unedited response to
the matching `.answer.md`. Do not use a test document as a model answer. Rerun the
same command to import the answers and run the checkers. Use the same selected model
for the whole run, or start a new run name when you change it.

The review board prepares independent prompts for tester, developer, risk and
compliance, and end user. After all responses are saved, the next invocation
prepares the consolidator prompt with the original spec and all raw reviews. Save
that response and rerun again. Manual conversations can be run concurrently or in
turn; metadata establishes the supplied model label and import time, not the chat
app's execution time or actual independence. Record those details in the human review.

## Automated backends

| BACKEND | Prerequisite | MODEL |
| --- | --- | --- |
| manual | An approved chat app | Its displayed model label, supplied by you |
| claude-cli | Claude Code installed and signed in | A supported model ID or alias |
| anthropic | Export ANTHROPIC_API_KEY | An accessible Anthropic model ID |
| openai | Export OPENAI_API_KEY | An accessible OpenAI model ID |
| openrouter | Export OPENROUTER_API_KEY | A provider/model ID supported by your account |

Use `make examples BACKEND=openai MODEL="your-model-id" RUN=api-run` after exporting
the matching key. Other backends use the same command with their name and model.
`.env.example` documents variables, but `.env` is not loaded automatically. Never
put a real key in a command, tracked file, prompt or issue. Model availability and
cost depend on your account; this repo chooses no provider or default model for you.

API and CLI runs issue independent reviewer calls concurrently, then consolidate
only after every role completes. The other workflows each make a single call.
Claude CLI uses print mode with built-in and MCP tools disabled; the Python harness
supplies all source content and performs orchestration. It does not invoke the
interactive skills. The OpenAI backend uses Responses with `store: false`; this
setting is not a promise of zero retention or organisational approval.

## Files, resuming and failures

Each workflow writes to `workflows/<workflow>/examples/<run>/`:

- `<stage>.prompt.md`: the exact UTF-8 prompt submitted or prepared for copying.
- `<stage>.metadata.json`: backend, requested and reported model, UTC timestamp,
  prompt hash, status and the output hash when complete.
- `<stage>.answer.md`: the response you pasted when using the manual backend.
- `<stage>.md`: the untouched accepted text returned by the backend or imported.
- `check.json`: source and output hashes, deterministic findings and pending sign-off.
- `traceability.md`: the requirement matrix for the test workflow.

A completed stage is reused only when its inputs, settings and output hash match.
Changes require a new `RUN` name. Keep the original result, including failures.
Edit a copy for stakeholder review and rerun the standalone checker on that copy.
The metadata hash covers the saved workflow prompt, not hidden provider or CLI
system instructions. API/CLI timestamps mark the call attempt; manual timestamps
mark preparation or import. For pasted answers, the script cannot verify the model name you enter.

CLI exit `0` means generation and structural checks completed, `1` means findings
need attention, and `2` means a manual answer is pending or a configuration/input
error needs fixing. Make may display its own error status for any nonzero command.
Pending is an expected manual state, not evidence of generated examples.

Run only one workflow with
`uv run playbook-examples --workflow spec-review-board --backend manual --model "your-chat-model" --run first-run`.
Do not run two processes with the same run name simultaneously. Generated run
folders are gitignored. Check what the files contain and where they came from before sharing them.
A passing checker still requires a person to assess meaning,
completeness, priorities and acceptance.

## Tool format references

Packaging follows the official [Claude skills](https://code.claude.com/docs/en/skills)
and [subagents](https://code.claude.com/docs/en/sub-agents) formats, and VS Code
[instructions](https://code.visualstudio.com/docs/agent-customization/custom-instructions),
[prompt files](https://code.visualstudio.com/docs/agent-customization/prompt-files),
[custom agents](https://code.visualstudio.com/docs/agent-customization/custom-agents) and
[skills](https://code.visualstudio.com/docs/agent-customization/agent-skills).
Prompt files are supported by the Local agent and are not loaded by Agent Host.
The compatibility skill wrappers share the same canonical prompts. Tool access and
delegation depend on the installed version and organisational settings; interactive
loading still needs to be checked in the intended clients.
