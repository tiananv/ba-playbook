# Requirements to tests

I want to see which requirements have test cases and where the gaps are.

Use requirements you're allowed to share, with REQ headings and agreed business
rules. The [practice requirements](input.md) are fictional rules for Paper Lantern
Community Clinic. They don't represent a real stakeholder agreement or AI output.

The [prompt](prompt.md) asks for Given/When/Then cases linked to REQ IDs. The checker
turns those links into a traceability matrix. A reviewed set of AI test cases is
[still pending](examples/README.md).

For Claude Code, Copilot or chat, follow the [shared setup instructions](../../docs/SETUP.md#the-same-workflow-in-three-tools).

Compare each test with its requirement, including boundary cases and failure paths.
A linked test can still check the wrong behaviour; leave missing business rules as
questions for the decision owner.

## Check test links

```sh
uv run trace-check workflows/requirements-to-tests/input.md path/to/your-output.md --matrix .cache/traceability.md
```

Replace the output path with the saved test cases in the
[supported format](../../checks/README.md#test-traceability). Open the matrix even
when the checker reports gaps. It shows requirement links and complete steps;
it does not show that a test has been run or that its expected result is correct.
Record the review decision separately.
