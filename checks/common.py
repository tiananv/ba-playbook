"""Small Markdown readers and shared command-line reporting."""

import re
from dataclasses import dataclass
from pathlib import Path

QUOTES = str.maketrans({"“": '"', "”": '"', "„": '"', "‘": "'", "’": "'"})


@dataclass(frozen=True)
class Issue:
    """A stable issue code and the document item needing attention."""

    code: str
    item: str
    message: str


def normalise(text: str) -> str:
    """Collapse whitespace and typographic quote variants, preserving words and case."""
    return " ".join(text.translate(QUOTES).split())


def records(markdown: str, prefix: str) -> tuple[list[tuple[str, str]], list[Issue]]:
    """Read ID headings and their bodies; reject empty, duplicate or malformed IDs."""
    issues = []
    if re.search(r"(?m)^\s*(```|~~~)", markdown):
        issues.append(Issue("format", "document", "Remove code fences around the Markdown."))
    headings = list(re.finditer(r"(?m)^#{1,6}[ \t]+([^\n]+)", markdown))
    items, seen = [], set()
    for index, heading in enumerate(headings):
        title = heading[1].strip()
        if not title.startswith(prefix + "-"):
            continue
        identifier = re.split(r"[\s:]", title, maxsplit=1)[0]
        if not re.fullmatch(prefix + r"-\d{3,}", identifier):
            issues.append(Issue("format", identifier, f"Use {prefix}- followed by at least three digits."))
            continue
        if identifier in seen:
            issues.append(Issue("duplicate_id", identifier, "ID appears more than once."))
        seen.add(identifier)
        end = headings[index + 1].start() if index + 1 < len(headings) else len(markdown)
        items.append((identifier, markdown[heading.end():end].strip()))
    if not items:
        issues.append(Issue("format", "document", f"No {prefix}-001 style headings found."))
    return items, issues


def read(path: Path) -> str:
    """Read a UTF-8 document without swallowing filesystem or encoding errors."""
    return path.read_text(encoding="utf-8")


def report(issues: list[Issue]) -> int:
    """Print actionable findings and return the checker exit status."""
    for issue in issues:
        print(f"{issue.code}: {issue.item}: {issue.message}")
    print(f"FAIL: {len(issues)} issue(s)." if issues else "PASS: no structural issues found.")
    return int(bool(issues))


def file_error(error: Exception) -> int:
    """Return a friendly input error without exposing document contents."""
    if isinstance(error, OSError):
        print(f"Input error: {error.strerror}: {error.filename}")
    else:
        print("Input error: documents must be valid UTF-8.")
    return 2

