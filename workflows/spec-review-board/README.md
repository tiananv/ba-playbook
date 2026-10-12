# Specification review board

Use before agreement or build, when a draft specification needs challenge from several perspectives.

**Inputs:** a permitted specification with SEC headings, decision log and scope. The [fictional input](input.md) belongs to the Paper Lantern
Community Clinic case and was created for this exercise. It is not model output.
The [canonical prompt](prompt.md) defines the task. **Outputs:** independent role reviews and one consolidated findings table.
Model examples are pending; [examples/README.md](examples/README.md) explains why.

For Claude Code, Copilot or chat, follow the [shared setup instructions](../../docs/SETUP.md#the-same-workflow-in-three-tools).

## Independent reviews and consolidation

The four roles are tester, developer, risk and compliance, and end user. Their
[role prompts](reviewers/) share the [review format](review-format.md).
Claude Code uses the project reviewer subagents; Copilot uses the custom agents
in `.github/agents/`. Ask for parallel independent reviews of the same source.
If delegation is unavailable, use separate fresh conversations, one per role.
Keep each raw review. Do not label a sequential run parallel or describe one chat
role-playing every reviewer as independent agents.

Only after all roles finish, give the consolidator the original specification and
the four reviews. It merges equivalent issues, combines all contributing roles and
retains minority concerns. The checker catches repeated normalised text in a
section; paraphrased duplicates and questionable merges need human judgement.

## Check the consolidated findings

```sh
uv run review-check workflows/spec-review-board/input.md path/to/your-output.md
```

Replace the output path with the consolidated findings, using the
[supported table format](../../checks/README.md#specification-review). Save the
checker report beside the findings. Compare the table with the original reviews
before accepting any merges or priorities, and record that decision separately.
