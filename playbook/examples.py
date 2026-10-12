"""Run the workflows and their checks, with independent parallel spec reviewers."""

import argparse
import os
import re
from concurrent.futures import ThreadPoolExecutor
from dataclasses import asdict
from pathlib import Path

from checks import quote_check, review_check, trace_check
from checks.common import read, report
from llm import BACKENDS, ModelError, PendingAnswer, digest, generate, write_json

ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ("workshop-to-requirements", "spec-review-board", "requirements-to-tests")
ROLES = ("tester", "developer", "risk-and-compliance", "end-user")


def _prompt(instructions: str, source: str) -> str:
    return instructions.rstrip() + "\n\n<source_document>\n" + source + "\n</source_document>\n"


def run_workflow(root: Path, workflow: str, backend: str, model: str, run: str) -> tuple[str, list[str]]:
    """Save each stage and run its checker; return complete, failed or pending status."""
    folder = root / "workflows" / workflow
    target = folder / "examples" / run
    source = read(folder / "input.md")
    prompt = _prompt(read(folder / "prompt.md"), source)
    if workflow == "spec-review-board":
        def reviewer(role: str) -> tuple[Path | None, str | None]:
            """Run an isolated role call or report its missing manual response."""
            try:
                role_prompt = _prompt(read(folder / "reviewers" / f"{role}.md") + "\n\n" + read(folder / "review-format.md"), source)
                return generate(role_prompt, target / f"{role}.md", backend, model), None
            except PendingAnswer as error:
                return None, str(error)

        with ThreadPoolExecutor(max_workers=4) as pool:
            reviews = list(pool.map(reviewer, ROLES))
        pending = [message for _, message in reviews if message]
        if pending:
            return "pending", pending
        review_text = "\n\n".join(f"<review role=\"{role}\">\n{read(path)}\n</review>" for role, (path, _) in zip(ROLES, reviews))
        prompt += "\n" + review_text + "\n"
    try:
        output = generate(prompt, target / "output.md", backend, model)
    except PendingAnswer as error:
        return "pending", [str(error)]
    if workflow == "requirements-to-tests":
        issues, matrix = trace_check.analyse(source, read(output))
        (target / "traceability.md").write_text(matrix, encoding="utf-8")
    else:
        checker = quote_check.check if workflow == "workshop-to-requirements" else review_check.check
        issues = checker(source, read(output))
    write_json(target / "check.json", {"workflow": workflow, "source_sha256": digest(source),
               "output_sha256": digest(read(output)), "issues": [asdict(issue) for issue in issues],
               "human_sign_off": "pending"})
    report(issues)
    return ("failed" if issues else "complete"), [f"{workflow}: {output}"]


def main(argv: list[str] | None = None) -> int:
    """Run all or one workflow without treating a waiting manual run as a success."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--backend", choices=BACKENDS, default=os.getenv("BACKEND", "manual"))
    parser.add_argument("--model", default=os.getenv("MODEL", ""))
    parser.add_argument("--run", default="first-run")
    parser.add_argument("--workflow", choices=(*WORKFLOWS, "all"), default="all")
    args = parser.parse_args(argv)
    if not re.fullmatch(r"[a-zA-Z0-9][a-zA-Z0-9_-]*", args.run):
        parser.error("--run must be a simple name, with no directory separators")
    statuses = []
    try:
        for workflow in WORKFLOWS if args.workflow == "all" else (args.workflow,):
            status, messages = run_workflow(ROOT, workflow, args.backend, args.model, args.run)
            statuses.append(status)
            for message in messages:
                print(message)
    except (ModelError, OSError, UnicodeError) as error:
        print(f"Examples error: {error}" if isinstance(error, ModelError) else "Examples error: could not read or write a UTF-8 run file.")
        return 2
    if "failed" in statuses:
        print("Examples saved, but checks failed. Inspect check.json before using them.")
        return 1
    if "pending" in statuses:
        print("Examples pending: prompts are ready. Rerun the same command after saving the answers.")
        return 2
    print("Examples generated and structurally checked. Human sign-off is still pending.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
