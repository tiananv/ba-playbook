# Setup and running the playbook

Use the fictional clinic inputs to try the workflows. Before using any other
material, follow the [information-handling guide](../WHAT-NEVER-GOES-INTO-AI.md)
and [method](../METHOD.md). Return to the [playbook overview](../README.md) for the
BA problem and the limits of the checks.

## How to run it

Install [uv](https://docs.astral.sh/uv/getting-started/installation/) and Python 3.11.
Run the commands from the repository folder. uv sets up the Python environment
when you run a command.

Prepare a workshop prompt for your chosen chat app. Replace the model label with
the one shown in the app:

```sh
uv run playbook-examples --workflow workshop-to-requirements --backend manual --model "your-chat-model" --run first-run
```

The command prints where the prompt is saved and where to put the real answer.
Paste the prompt into a fresh chat, save the unedited answer at that path, then
rerun the same command. Until an answer is saved, the run stays pending.
For interactive Claude Code or Copilot use, follow the [tool instructions below](#the-same-workflow-in-three-tools).

Check the saved draft against the original transcript:

```sh
uv run quote-check workflows/workshop-to-requirements/input.md workflows/workshop-to-requirements/examples/first-run/output.md
```

Run the checker self-tests and refresh the tables in this guide and the README:

```sh
uv run playbook-results
```

There are some automatic checks in `tests/` to make sure the scripts work:

```sh
uv run pytest
```

### Checker self-tests

<!-- RESULTS:START -->
The checker self-tests passed on the sample documents.

This doesn't measure how well an AI model performs. A matching quote can support the wrong requirement, a cited section can be misread, and a linked test can check the wrong behaviour. I still need to compare a real draft with its source.
<!-- RESULTS:END -->

## The same workflow in three tools

<!-- TOOLS:START -->
| Workflow | Claude Code skill | Copilot prompt | Chat instructions |
| --- | --- | --- | --- |
| [workshop-to-requirements](../workflows/workshop-to-requirements/README.md) | [SKILL.md](../.claude/skills/workshop-to-requirements/SKILL.md) | [prompt.md](../.github/prompts/workshop-to-requirements.prompt.md) | [Paste guide](../chat/workshop-to-requirements.md) |
| [spec-review-board](../workflows/spec-review-board/README.md) | [SKILL.md](../.claude/skills/spec-review-board/SKILL.md) | [prompt.md](../.github/prompts/spec-review-board.prompt.md) | [Paste guide](../chat/spec-review-board.md) |
| [requirements-to-tests](../workflows/requirements-to-tests/README.md) | [SKILL.md](../.claude/skills/requirements-to-tests/SKILL.md) | [prompt.md](../.github/prompts/requirements-to-tests.prompt.md) | [Paste guide](../chat/requirements-to-tests.md) |
<!-- TOOLS:END -->

The [.github/skills](../.github/skills/) folder also provides the workflows for
Copilot Agent Host sessions. Check that the instructions and reviewer roles load
in your installed tool before relying on them.

### Claude Code

Open the repository and invoke the workflow's command, such as
`/workshop-to-requirements`, with the source file path and a separate output path.
The skill reads the shared prompt. Provide only approved context and run the
workflow's checker if the tool has not run it. Use the command above when you want
the prompt, answer and model details saved together.

### GitHub Copilot in VS Code

With the Local agent, invoke the workflow's prompt command and attach the source
file. For an Agent Host session, load the matching skill from `.github/skills/`.
Select an approved model and provide an output path. If the command does not
appear, use the chat instructions while checking your tool's settings. Confirm
that the intended instructions were loaded.

### ChatGPT or another chat app

Follow the workflow's paste guide using an approved account. Paste the source
contents as well as the prompt; a local filename alone is not enough. Save the
unedited Markdown answer, then run the checker locally. A chat answer cannot prove
that a local checker passed. The manual command above saves the prompt and answer
alongside the model label you supplied and the time the answer was imported.

## Record a worked example

I haven't recorded a reviewed example yet. The workshop command in
[How to run it](#how-to-run-it) is the starting point for saving one.

1. Paste the saved prompt into a fresh conversation. The first invocation prints
   the prompt and answer paths and exits with status `2`, meaning an answer is
   pending. Save the real, unedited answer to the printed answer path.
2. Rerun the same command to import the answer and record the structural checks.
   Keep the prompt, original answer, model details and checker report together.
   Read any findings before proceeding; a checker pass alone is not sign-off.
3. Compare every requirement with the transcript, including qualifiers, omissions
   and open decisions. Put corrections in a separate `reviewed.md` in the run folder
   and explain each correction with its source. Keep the original output unchanged.
4. Check the corrected draft with the command below. Keep its report alongside the
   original check, including any findings still awaiting resolution.
5. Record the actual review decision in a separate `review.md`: what you checked,
   why you changed it, open questions, the source and draft versions, who reviewed
   them and the sign-off date if accepted. The script leaves `human_sign_off` pending.
6. Before sharing an example, check the files and link the original draft,
   corrections and real review decision from the README. Run folders stay local
   until you choose what to share. Leave the example pending until those records exist.

For the run name above, check the corrected draft from the repository root:

```sh
uv run quote-check workflows/workshop-to-requirements/input.md workflows/workshop-to-requirements/examples/first-run/reviewed.md > workflows/workshop-to-requirements/examples/first-run/reviewed-check.txt
```

Read `reviewed-check.txt` even if the command exits with status `1`, which means
findings need attention. Keep the model fixed for a named run. Start a new run name
if you change the source, prompt, backend or model. See the
[runner guide](../workflows/README.md) for saved files and restarting a run.

## Run all workflows or choose another backend

To prepare all workflows with the same approved chat model:

```sh
uv run playbook-examples --backend manual --model "your-chat-model" --run first-run
```

Paste each saved prompt, save the real answers to the printed paths, then rerun the
same command. The review board needs a further consolidation pass after its role
responses are saved. Preserve the original role responses as well as the final draft.

For an API or Claude Code command, see the [backend options](../workflows/README.md#automated-backends).
Choose a model available to your approved account. [.env.example](../.env.example)
lists the optional settings. Never put a real key in a command, prompt or shared file.
