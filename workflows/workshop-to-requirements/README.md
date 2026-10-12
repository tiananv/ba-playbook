# Workshop to requirements

Use after a workshop when you need a draft that carries its evidence with it.

**Inputs:** a permitted transcript or notes, plus a versioned project brief and glossary. The [fictional input](input.md) belongs to the Paper Lantern
Community Clinic case and was created for this exercise. It is not model output.
The [canonical prompt](prompt.md) defines the task. **Outputs:** draft REQ headings with exact Source quotations and a separate list of open questions.
Model examples are pending; [examples/README.md](examples/README.md) explains why.

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
