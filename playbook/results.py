"""Measure checker test cases and regenerate the README and setup tables."""

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
    return {"description": "Fictional test documents check specific errors; they do not measure model accuracy.",
            "cases": details, "totals": totals}


def self_test_section(result: dict) -> str:
    """Summarise the actual checker run without publishing test counts."""
    failed = any(row["missed"] or row["unexpected"] for row in result["totals"].values())
    status = ("The checker self-tests found a problem. Read the command output before using the checks."
              if failed else "The checker self-tests passed on the sample documents.")
    return (status + "\n\n"
            "This doesn't measure how well an AI model performs. A matching quote can support the wrong "
            "requirement, a cited section can be misread, and a linked test can check the wrong behaviour. "
            "I still need to compare a real draft with its source.")


def inventory_sections(root: Path) -> dict[str, str]:
    """Build the setup tool table and README check table, verifying linked files."""
    tools = ["| Workflow | Claude Code skill | Copilot prompt | Chat instructions |", "| --- | --- | --- | --- |"]
    checks = ["| What the AI does | What checks it |", "| --- | --- |"]
    descriptions = [
        ("Drafts requirements", "quote", "Matches quotes to the source. A person checks meaning and omissions."),
        ("Reviews a specification", "review", "Checks section IDs and repeated findings. A person checks the combined review."),
        ("Writes test cases", "trace", "Checks requirement links and complete steps. A person checks what each test covers."),
    ]
    for workflow, (action, checker, explanation) in zip(WORKFLOWS, descriptions):
        paths = [f".claude/skills/{workflow}/SKILL.md", f".github/prompts/{workflow}.prompt.md", f"chat/{workflow}.md"]
        for path in [*paths, f"workflows/{workflow}/README.md", f".github/skills/{workflow}/SKILL.md", f"checks/{checker}_check.py"]:
            if not (root / path).is_file():
                raise FileNotFoundError(f"Required packaging file is missing: {path}")
        tools.append(f"| [{workflow}](../workflows/{workflow}/README.md) | [SKILL.md](../{paths[0]}) | [prompt.md](../{paths[1]}) | [Paste guide](../{paths[2]}) |")
        checks.append(f"| {action} | [{checker}-check](checks/{checker}_check.py): {explanation} |")
    checks.append("| Produces a draft for discussion | A person makes the final decision in every workflow. |")
    return {"TOOLS": "\n".join(tools), "CHECKS": "\n".join(checks)}


def main() -> int:
    """Regenerate self-tests and setup tables without making a model call."""
    result = benchmark(ROOT / "tests" / "fixtures")
    inventory = inventory_sections(ROOT)
    documents = {
        "README.md": {"CHECKS": inventory["CHECKS"]},
        "docs/SETUP.md": {"TOOLS": inventory["TOOLS"], "RESULTS": self_test_section(result)},
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
