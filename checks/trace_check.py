"""Build a requirement-to-test matrix and flag gaps or invalid references."""

import argparse
import re
from pathlib import Path

from checks.common import Issue, file_error, read, records, report


def analyse(requirements: str, tests: str) -> tuple[list[Issue], str]:
    """Return structural issues and a Markdown matrix, including unknown references."""
    requirement_items, issues = records(requirements, "REQ")
    test_items, test_issues = records(tests, "TC")
    issues.extend(test_issues)
    coverage = {identifier: [] for identifier, _ in requirement_items}
    unknown = {}
    for identifier, body in test_items:
        fields = re.findall(r"(?m)^Requirements:[ \t]*(.*)$", body)
        if len(fields) != 1 or not re.fullmatch(r"REQ-\d{3,}(?:\s*,\s*REQ-\d{3,})*", fields[0].strip()):
            issues.append(Issue("missing_reference", identifier, "Add Requirements: REQ-001, REQ-002 using comma-separated IDs."))
            references = []
        else:
            references = sorted(set(re.findall(r"REQ-\d{3,}", fields[0])))
        clauses = [bool(re.search(rf"(?m)^{word}:[ \t]*\S.*$", body)) for word in ("Given", "When", "Then")]
        if not all(clauses):
            issues.append(Issue("missing_step", identifier, "Include non-empty Given:, When: and Then: lines."))
        for reference in references:
            if reference not in coverage:
                issues.append(Issue("unknown_requirement", identifier, f"{reference} does not exist."))
                unknown.setdefault(reference, []).append(identifier)
            elif all(clauses):
                coverage[reference].append(identifier)
    for reference, test_ids in coverage.items():
        if not test_ids:
            issues.append(Issue("untraced_requirement", reference, "No complete Given/When/Then test references this requirement."))
    rows = ["# Traceability matrix", "", "| Requirement | Tests | Status |", "| --- | --- | --- |"]
    for reference, test_ids in coverage.items():
        rows.append(f"| {reference} | {', '.join(test_ids) or 'None'} | {'Linked' if test_ids else 'MISSING'} |")
    for reference, test_ids in sorted(unknown.items()):
        rows.append(f"| {reference} | {', '.join(test_ids)} | UNKNOWN REQUIREMENT |")
    rows.extend(["", "Links record references and complete steps. A person must check the test's meaning."])
    return issues, "\n".join(rows) + "\n"


def check(requirements: str, tests: str) -> list[Issue]:
    """Return traceability issues without writing files."""
    return analyse(requirements, tests)[0]


def main(argv: list[str] | None = None) -> int:
    """Run trace-check, writing a matrix even when the check finds gaps."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("requirements", type=Path)
    parser.add_argument("tests", type=Path)
    parser.add_argument("--matrix", type=Path, default=Path("traceability.md"))
    args = parser.parse_args(argv)
    try:
        if args.matrix.resolve() in {args.requirements.resolve(), args.tests.resolve()}:
            parser.error("--matrix must not overwrite an input document")
        issues, matrix = analyse(read(args.requirements), read(args.tests))
        args.matrix.parent.mkdir(parents=True, exist_ok=True)
        args.matrix.write_text(matrix, encoding="utf-8")
        print(f"Matrix: {args.matrix}")
        return report(issues)
    except (OSError, UnicodeError) as error:
        return file_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
