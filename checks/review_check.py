"""Validate review section citations and flag repeated finding IDs or issues."""

import argparse
import re
from pathlib import Path

from checks.common import Issue, file_error, normalise, read, records, report

HEADER = ["id", "section", "issue", "severity", "raised by"]
ROLES = {"tester", "developer", "risk and compliance", "end user"}


def check(spec: str, findings: str) -> list[Issue]:
    """Check the findings table, using section plus normalised issue text for duplicates."""
    sections, issues = records(spec, "SEC")
    section_ids = {identifier for identifier, _ in sections}
    rows = [line.strip() for line in findings.splitlines() if line.strip().startswith("|")]
    if re.search(r"(?m)^\s*(```|~~~)", findings):
        issues.append(Issue("format", "findings", "Remove code fences around the table."))
    if len(rows) < 2 or [cell.strip().lower() for cell in rows[0].strip("|").split("|")] != HEADER:
        return issues + [Issue("format", "findings", "Use the id, section, issue, severity, raised by table header.")]
    separators = [cell.strip() for cell in rows[1].strip("|").split("|")]
    if len(separators) != 5 or any(not re.fullmatch(r":?-{3,}:?", cell) for cell in separators):
        issues.append(Issue("format", "findings", "Use a five-column Markdown separator row."))
    if len(rows) == 2 and "No findings." not in findings.splitlines():
        issues.append(Issue("format", "findings", "For an empty table, explicitly state No findings."))
    seen_ids, seen_issues = set(), set()
    for number, row in enumerate(rows[2:], start=1):
        cells = [cell.strip() for cell in row.strip("|").split("|")]
        if len(cells) != 5 or not all(cells):
            issues.append(Issue("format", f"row {number}", "Expected five non-empty cells; use words instead of pipe characters."))
            continue
        identifier, section, issue, severity, raised_by = cells
        if not re.fullmatch(r"F-\d{3,}", identifier):
            issues.append(Issue("format", identifier, "Use an F-001 style finding ID."))
        if identifier in seen_ids:
            issues.append(Issue("duplicate_id", identifier, "Finding ID appears more than once."))
        seen_ids.add(identifier)
        if section not in section_ids:
            issues.append(Issue("unknown_section", identifier, f"{section} is not a heading in the spec."))
        key = (section, normalise(issue).casefold())
        if key in seen_issues:
            issues.append(Issue("duplicate_finding", identifier, "The same issue text already appears for this section."))
        seen_issues.add(key)
        if severity.lower() not in {"low", "medium", "high", "critical"}:
            issues.append(Issue("format", identifier, "Severity must be low, medium, high or critical."))
        if not {name.strip().lower() for name in raised_by.split(",")} <= ROLES:
            issues.append(Issue("format", identifier, "Raised by must list the documented reviewer roles."))
    return issues


def main(argv: list[str] | None = None) -> int:
    """Run review-check against a spec and a Markdown findings table."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("spec", type=Path)
    parser.add_argument("findings", type=Path)
    args = parser.parse_args(argv)
    try:
        return report(check(read(args.spec), read(args.findings)))
    except (OSError, UnicodeError) as error:
        return file_error(error)


if __name__ == "__main__":
    raise SystemExit(main())

