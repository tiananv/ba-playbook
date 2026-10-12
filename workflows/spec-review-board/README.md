# Specification review board

I want to look at a draft spec from different roles before asking someone to agree
to it. I'm not sure yet which role will add the most useful questions.

Start with a spec you're allowed to use, with SEC headings, a decision log and
scope. The [practice spec](input.md) describes fictional booking and referral work
at Paper Lantern Community Clinic; it was written as input for this repo.

The role prompts ask for separate reviews. The [consolidation prompt](prompt.md)
combines them into a findings table. I haven't recorded a reviewed board example
yet; the [example notes](examples/README.md) cover what I'll need to keep.

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
keeps concerns even when only one role raised them. The checker catches the same
issue text repeated in a section, ignoring case and spacing. A person still needs
to spot differently worded duplicates and check that combined findings keep the
original concern.

## Check the consolidated findings

```sh
uv run review-check workflows/spec-review-board/input.md path/to/your-output.md
```

Replace the output path with the consolidated findings, using the
[supported table format](../../checks/README.md#specification-review). Save the
checker report beside the findings. Compare the table with the original reviews
before accepting any merges or priorities, and record that decision separately.
