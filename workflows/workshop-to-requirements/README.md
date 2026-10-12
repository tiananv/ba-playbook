# Workshop to requirements

I want to turn workshop notes into a draft where I can see what each requirement
is based on.

Start with a transcript or notes you're allowed to use, plus a project brief and
glossary with their versions. The [practice transcript](input.md) is a fictional
Paper Lantern Community Clinic workshop, written for this repo.

The [prompt](prompt.md) asks for draft REQ headings, exact Source quotations and
a separate list of open questions. I haven't recorded a reviewed AI example yet;
the [example notes](examples/README.md) explain what I'll need to keep.

For Claude Code, Copilot or chat, follow the [shared setup instructions](../../docs/SETUP.md#the-same-workflow-in-three-tools).

Use the original source and output side by side when checking meaning. Treat open
questions as decisions to resolve, not permission to fill gaps with assumed rules.

## Check the draft

```sh
uv run quote-check workflows/workshop-to-requirements/input.md path/to/your-output.md
```

Replace the output path with the saved requirements draft. Use the
[supported headings and Source fields](../../checks/README.md#requirements-and-quotations).
The checker finds missing or altered quotes. A person still needs to check whether
each quote supports its requirement, note omissions and record the review decision.
