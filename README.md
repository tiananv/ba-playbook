# ba-playbook

- Reusable AI prompts, context templates and checks for business analysis.
- Three workflows, with instructions for Claude Code, Copilot and chat tools.
- Fictional community clinic examples; no employer or client material.

## Workflows

- [Workshop notes to requirements](workflows/workshop-to-requirements/README.md): draft requirements with links to source quotes.
- [Specification review](workflows/spec-review-board/README.md): review from testing, development, risk and end-user perspectives.
- [Requirements to test cases](workflows/requirements-to-tests/README.md): link test cases to requirements and check for missing steps.

## Validation results

- **13 of 13 planted issues detected** across quote, review and traceability checks.
- **Six valid test documents accepted**, with no unexpected warnings across the 12 test cases.
- [Saved benchmark](results/checker-benchmark.json): fictional test documents, measuring checker behaviour rather than AI accuracy.
- [Example datasets](tests/fixtures/README.md) · Reproduce: `uv run pytest -q tests/test_checks.py::test_labelled_fixtures`.
- Meaning, omissions and test coverage still need human review. A real model draft with corrections is pending.

<details>
<summary>Checker reference</summary>

<!-- CHECKS:START -->

| What the AI does                | What checks it                                                                                                            |
| ------------------------------- | ------------------------------------------------------------------------------------------------------------------------- |
| Drafts requirements             | [quote-check](checks/quote_check.py): Matches quotes to the source. A person checks meaning and omissions.                |
| Reviews a specification         | [review-check](checks/review_check.py): Checks section IDs and repeated findings. A person checks the combined review.    |
| Writes test cases               | [trace-check](checks/trace_check.py): Checks requirement links and complete steps. A person checks what each test covers. |
| Produces a draft for discussion | A person makes the final decision in every workflow.                                                                      |

<!-- CHECKS:END -->

</details>

## Published research — external results

- **15% more issues resolved per hour** with AI assistance in a study of 5,172 customer-support agents; benefits varied by experience and skill. This was a customer-support study, not a test of these BA workflows. [Brynjolfsson, Li and Raymond, 2025](https://academic.oup.com/qje/article/140/2/889/7990658).

## Use

- [Method](METHOD.md) and [context templates](context/): project brief, glossary and decision log.
- [Information handling](WHAT-NEVER-GOES-INTO-AI.md): what to keep out of AI tools.
- [Setup and commands](docs/SETUP.md): run the workflows and checks.

---

Built with help from AI coding tools. [MIT licence](LICENSE).
