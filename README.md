<picture>
  <source media="(prefers-color-scheme: dark)" srcset="assets/banner-dark.svg">
  <img src="assets/banner-light.svg" alt="ba-playbook. BA workflows with AI, checked against the source." width="1200">
</picture>

## The problem

AI can draft a tidy requirement that was never agreed, cite a section that does not
exist or miss a test link. This playbook gives a business analyst a repeatable method
for using AI and small checks that make those mistakes visible.

## The method

```mermaid
flowchart LR
    A[Classify data] --> B[Use an approved tool]
    B --> C[Give it context]
    C --> D[Check the source]
    D --> E[Human sign-off]
```

Start with [what never goes into AI](WHAT-NEVER-GOES-INTO-AI.md) and the [method](METHOD.md).
Use permitted information in the [context templates](context/) and keep open decisions
visible. The fictional Paper Lantern Community Clinic case covers booking and referral
administration. Keep the original AI draft and checker report for a person to assess
against the source and sign off.

## Worked example

I haven't recorded a reviewed example yet. When I do, it will show the AI's first
draft, my corrections and why, and my sign-off. Follow the
[steps for recording a worked example](docs/SETUP.md#record-a-worked-example).

## What the AI does / What checks it

<!-- CHECKS:START -->
| What the AI does | What checks it |
| --- | --- |
| Drafts requirements | [quote-check](checks/quote_check.py): Verbatim source check, then a person checks meaning and omissions. |
| Reviews a specification | [review-check](checks/review_check.py): Section citations and repeated issue text, then a person checks the consolidation. |
| Writes test cases | [trace-check](checks/trace_check.py): Requirement links and complete steps, then a person checks behaviour and coverage. |
| Produces a draft for discussion | A person retains final sign-off on every workflow. |
<!-- CHECKS:END -->

The checkers use a [simple Markdown format](checks/README.md). A pass confirms only
the checks described there. A person decides whether the work is accurate and useful.

Each checker has [small built-in tests](docs/SETUP.md#checker-self-tests), including
cases where a check passes but the content is still wrong.

## Use it in your own tools

Follow the [setup guide](docs/SETUP.md) to use these workflows in Claude Code, Copilot or an approved chat app.

## Under the hood

```text
METHOD.md and WHAT-NEVER-GOES-INTO-AI.md  Method and information handling
context/                                  Empty project context templates
workflows/                                Prompts, fictional inputs and runner guide
.claude/, .github/ and chat/              Tool entry points and automated checks
checks/                                   Standalone Markdown checkers
llm.py and playbook/                      Model runner and self-test generator
tests/ and results/                       Test documents and measured counts
docs/SETUP.md                             Setup, self-tests and worked example steps
assets/                                   Light and dark banners
```

Commands for setup, self-tests and model runs are in [SETUP.md](docs/SETUP.md).

### Data

All clinic inputs were written for this repo and are explicitly fictional. They
are input exercises, not records of a real workshop or model outputs. Synthetic
checker test documents live only in [tests/fixtures](tests/fixtures/). The repository's
original code, documents and fictional material use the [MIT licence](LICENSE).
No external dataset or raw-data download is needed.

The [Australian Government staff guidance](https://www.digital.gov.au/policy/ai/staff-guidance-public-generative-ai)
is linked as further reading. It is not copied into the repo or used as legal advice.

## About this repo

This first version was built with AI coding assistants. The results come from the code in this repo.
