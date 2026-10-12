"""Benchmark labelled fixtures and regenerate the README and setup tables."""

import json
from collections import Counter
from pathlib import Path

from checks import quote_check, review_check, trace_check
from checks.common import read
from llm import digest, write_json
from playbook.examples import WORKFLOWS

ROOT = Path(__file__).resolve().parents[1]
CHECKERS = {"quote": quote_check.check, "review": review_check.check, "trace": trace_check.check}


def benchmark(fixtures: Path) -> dict:
    """Count exact planted issue matches, misses and unexpected flags per checker."""
    cases = json.loads(read(fixtures / "manifest.json"))
    totals = {name: dict(planted=0, caught=0, missed=0, unexpected=0, good=0, good_flagged=0) for name in CHECKERS}
    details = []
    for case in cases:
        source, output = read(fixtures / case["source"]), read(fixtures / case["output"])
        actual = Counter((issue.code, issue.item) for issue in CHECKERS[case["checker"]](source, output))
        expected = Counter(tuple(pair) for pair in case["expected"])
        result = dict(planted=expected.total(), caught=(expected & actual).total(),
                      missed=(expected - actual).total(), unexpected=(actual - expected).total(),
                      good=int(not expected), good_flagged=int(not expected and bool(actual)))
        for key, value in result.items():
            totals[case["checker"]][key] += value
        details.append({**case, "source_sha256": digest(source), "output_sha256": digest(output),
                        "actual": [list(pair) for pair in actual.elements()], **result})
    return {"description": "Hand-authored structural checker fixtures, not a model evaluation.",
            "cases": details, "totals": totals}


def readme_section(result: dict) -> str:
    """Build the self-test counts and table with their limits beside them."""
    totals = result["totals"]
    planted = sum(row["planted"] for row in totals.values())
    caught = sum(row["caught"] for row in totals.values())
    good = sum(row["good"] for row in totals.values())
    flagged = sum(row["good_flagged"] for row in totals.values())
    lines = [f"The checkers caught **{caught} of {planted} planted structural issues** across "
             f"**{len(result['cases'])} fixture documents**. They flagged **{flagged} of {good} good documents**.", "",
             "| Checker | Planted | Caught | Missed | Unexpected flags | Good documents flagged |",
             "| --- | ---: | ---: | ---: | ---: | ---: |"]
    for name, row in totals.items():
        lines.append(f"| {name.capitalize()} | {row['planted']} | {row['caught']} | {row['missed']} | {row['unexpected']} | {row['good_flagged']} / {row['good']} |")
    lines.extend(["",
                  "These small, hand-authored fixtures exercise known structural defects. This is not evidence of model "
                  "accuracy or real-world detection rates. A quote can be real but irrelevant, a cited section can be "
                  "misread, and a linked test can miss the behaviour.", "",
                  "Measured using [labelled fixtures](tests/fixtures/README.md). "
                  "[Run details](results/checker-benchmark.json) include expected and actual issue IDs and input hashes; "
                  "[setup instructions](docs/SETUP.md#reproduce-the-checker-self-tests) explain how to reproduce them."])
    return "\n".join(lines)


def inventory_sections(root: Path) -> dict[str, str]:
    """Build the setup tool table and README check table, verifying linked files."""
    tools = ["| Workflow | Claude Code skill | Copilot prompt | Chat instructions |", "| --- | --- | --- | --- |"]
    checks = ["| What the AI does | What checks it |", "| --- | --- |"]
    descriptions = [
        ("Drafts requirements", "quote", "Verbatim source check, then a person checks meaning and omissions."),
        ("Reviews a specification", "review", "Section citations and repeated issue text, then a person checks the consolidation."),
        ("Writes test cases", "trace", "Requirement links and complete steps, then a person checks behaviour and coverage."),
    ]
    for workflow, (action, checker, explanation) in zip(WORKFLOWS, descriptions):
        paths = [f".claude/skills/{workflow}/SKILL.md", f".github/prompts/{workflow}.prompt.md", f"chat/{workflow}.md"]
        for path in [*paths, f"workflows/{workflow}/README.md", f".github/skills/{workflow}/SKILL.md", f"checks/{checker}_check.py"]:
            if not (root / path).is_file():
                raise FileNotFoundError(f"Required packaging file is missing: {path}")
        tools.append(f"| [{workflow}](../workflows/{workflow}/README.md) | [SKILL.md](../{paths[0]}) | [prompt.md](../{paths[1]}) | [Paste guide](../{paths[2]}) |")
        checks.append(f"| {action} | [{checker}-check](checks/{checker}_check.py): {explanation} |")
    checks.append("| Produces a draft for discussion | A person retains final sign-off on every workflow. |")
    return {"TOOLS": "\n".join(tools), "CHECKS": "\n".join(checks)}


def main() -> int:
    """Regenerate self-tests and setup tables without making a model call."""
    result = benchmark(ROOT / "tests" / "fixtures")
    inventory = inventory_sections(ROOT)
    documents = {
        "README.md": {"RESULTS": readme_section(result), "CHECKS": inventory["CHECKS"]},
        "docs/SETUP.md": {"TOOLS": inventory["TOOLS"]},
    }
    rendered = {}
    for filename, sections in documents.items():
        document = read(ROOT / filename)
        for name, content in sections.items():
            start, end = f"<!-- {name}:START -->", f"<!-- {name}:END -->"
            if document.count(start) != 1 or document.count(end) != 1 or document.index(start) > document.index(end):
                print(f"Results error: {filename} must contain one ordered pair of {name} markers.")
                return 2
            document = document.split(start)[0] + start + "\n" + content + "\n" + end + document.split(end)[1]
        rendered[filename] = document
    (ROOT / "results").mkdir(exist_ok=True)
    write_json(ROOT / "results" / "checker-benchmark.json", result)
    for filename, document in rendered.items():
        (ROOT / filename).write_text(document, encoding="utf-8")
    for name, row in result["totals"].items():
        print(f"{name}: planted={row['planted']} caught={row['caught']} missed={row['missed']} unexpected={row['unexpected']} good_flagged={row['good_flagged']}/{row['good']}")
    return int(any(row["missed"] or row["unexpected"] for row in result["totals"].values()))


if __name__ == "__main__":
    raise SystemExit(main())
