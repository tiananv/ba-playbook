# Requirements to tests

Use when agreed requirements need acceptance test coverage and gaps made visible.

**Inputs:** a permitted requirement baseline with REQ headings and agreed business rules. The [fictional input](input.md) belongs to the Paper Lantern
Community Clinic case and was created for this exercise. It is not model output.
The [canonical prompt](prompt.md) defines the task. **Outputs:** Given/When/Then test cases linked to REQ IDs and a generated traceability matrix.
Model examples are pending; [examples/README.md](examples/README.md) explains why.

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
