# Specification review board

Use before agreement or build, when a draft specification needs challenge from several perspectives.

**Inputs:** a permitted specification with SEC headings, decision log and scope. The [fictional input](input.md) belongs to the Paper Lantern
Community Clinic exercise and was written by the repo authors. It is not model output.
The [canonical prompt](prompt.md) defines the task. **Outputs:** independent role reviews and one consolidated findings table.
Model examples are pending; [examples/README.md](examples/README.md) explains why.

## Claude Code

Open this repository in Claude Code and invoke `/spec-review-board` with the source file path
and a separate output path. The [project skill](../../.claude/skills/spec-review-board/SKILL.md)
loads the shared prompt. Provide only approved context. Inspect the output and run
the checker below if the tool has not run it. Interactive skill use does not record
API harness metadata automatically.

## GitHub Copilot in VS Code

With the Local agent, invoke `/spec-review-board` from the
[prompt file](../../.github/prompts/spec-review-board.prompt.md) and attach the source file.
For an Agent Host session using the Copilot harness, load the
[skill](../../.github/skills/spec-review-board/SKILL.md) instead. Select the approved model
and provide an output path. If the command does not appear, inspect the customisation
view and use the chat route while checking your installed version. Do not assume
unloaded instructions were followed.

## ChatGPT or another chat app

Use [the paste guide](../../chat/spec-review-board.md) with an approved account. Paste the
source contents, not just a local filename. Save the unedited Markdown response.
Run the checker locally; a chat app cannot attest that a local checker passed.

## Independent reviews and consolidation

The four roles are tester, developer, risk and compliance, and end user. Their
[role prompts](reviewers/) share the [review contract](review-format.md).
Claude Code uses the project reviewer subagents; Copilot uses the custom agents
in `.github/agents/`. Ask for parallel independent reviews of the same source.
If delegation is unavailable, use separate fresh conversations, one per role.
Keep each raw review. Do not label a sequential run parallel or describe one chat
role-playing every reviewer as independent agents.

Only after all roles finish, give the consolidator the original specification and
the four reviews. It merges equivalent issues, combines all contributing roles and
retains minority concerns. The checker catches repeated normalised text in a
section; paraphrased duplicates and questionable merges need human judgement.

## Run and check

```sh
uv run playbook-examples --workflow spec-review-board --backend manual --model "your-chat-model" --run first-run
uv run review-check workflows/spec-review-board/input.md path/to/your-output.md
```

Replace the model label and output path. The first command prepares prompts, then
imports real answers on subsequent runs. See [the runner guide](../README.md) for
all backends and the exact answer-file steps. The second command checks a saved
Markdown file from any tool. See [the format contract](../../checks/README.md).
Passing a checker is structural evidence only. The responsible person checks meaning,
omissions and acceptance, records the decision and retains final sign-off.
