# ba-playbook

How I use AI for everyday BA work. It's my prompts, the rules I stick to, and a few small checks for when the AI gets something wrong. I keep it here so I can reuse it on any project, whichever AI tool the company uses.

## What's in here

- [How I use AI](METHOD.md), step by step
- [What never goes into AI](WHAT-NEVER-GOES-INTO-AI.md)
- [Context templates](context/): a project brief, glossary and decisions log to give the AI before I ask it anything
- Three workflows, each set up for Claude, Copilot and ChatGPT:
  - [Workshop notes to requirements](workflows/workshop-to-requirements/README.md)
  - [Spec review](workflows/spec-review-board/README.md), where four AI "reviewers" (tester, developer, risk and an end user) read the same spec
  - [Requirements to test cases](workflows/requirements-to-tests/README.md)

The practice material is a made-up community clinic, so there's nothing from work in here.

## The checks

AI is good at sounding sure of itself, so each workflow has a small check:

<!-- CHECKS:START -->
| What the AI does | What checks it |
| --- | --- |
| Drafts requirements | [quote-check](checks/quote_check.py): Matches quotes to the source. A person checks meaning and omissions. |
| Reviews a specification | [review-check](checks/review_check.py): Checks section IDs and repeated findings. A person checks the combined review. |
| Writes test cases | [trace-check](checks/trace_check.py): Checks requirement links and complete steps. A person checks what each test covers. |
| Produces a draft for discussion | A person makes the final decision in every workflow. |
<!-- CHECKS:END -->

They only catch the obvious things. A real quote can still end up attached to the wrong requirement, so I still read the source myself.

## Example

Coming soon: a real AI draft next to my corrections.

## Using it

The prompts work if you paste them into any AI chat. To run the checks, see [docs/SETUP.md](docs/SETUP.md).

---

Built with help from AI coding tools. [MIT licence](LICENSE).
