"""Check requirement source quotations against the supplied transcript."""

import argparse
import re
from pathlib import Path

from checks.common import QUOTES, Issue, file_error, normalise, read, records, report


def check(transcript: str, requirements: str) -> list[Issue]:
    """Find missing, malformed and non-verbatim sources for requirement headings."""
    items, issues = records(requirements, "REQ")
    source = normalise(transcript)
    if not source:
        issues.append(Issue("format", "transcript", "The transcript is empty."))
    for identifier, body in items:
        body = body.translate(QUOTES)
        labels = re.findall(r"(?m)^\s*Source:", body)
        if not labels:
            issues.append(Issue("missing_source", identifier, 'Add Source: "verbatim quote".'))
            continue
        field_start = re.search(r"(?m)^[ \t]*Source:[ \t]*", body)
        field = re.split(r"\n[ \t]*\n", body[field_start.end():], maxsplit=1)[0].strip() if field_start else ""
        if len(labels) != 1 or len(field) < 3 or not field.startswith('"') or not field.endswith('"') or not normalise(field[1:-1]):
            issues.append(Issue("source_format", identifier, "Use exactly one non-empty, double-quoted Source field."))
            continue
        if normalise(field[1:-1]) not in source:
            issues.append(Issue("altered_quote", identifier, "Source does not occur verbatim in the transcript."))
    return issues


def main(argv: list[str] | None = None) -> int:
    """Run quote-check on any two local Markdown documents."""
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("transcript", type=Path)
    parser.add_argument("requirements", type=Path)
    args = parser.parse_args(argv)
    try:
        return report(check(read(args.transcript), read(args.requirements)))
    except (OSError, UnicodeError) as error:
        return file_error(error)


if __name__ == "__main__":
    raise SystemExit(main())
