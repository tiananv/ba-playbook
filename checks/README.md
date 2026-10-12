# Standalone Markdown checks

Run from the repository after `make setup`. Paths may point to any local UTF-8
Markdown file. The content must follow the small contract below. A different file
name is fine; an unsupported layout needs conversion. An empty or unrecognised
document fails. The commands do not send data to a model or network service.

```sh
uv run quote-check transcript.md requirements.md
uv run review-check spec.md findings.md
uv run trace-check requirements.md tests.md --matrix traceability.md
```

Exit status is `0` for no detected issues, `1` for checker findings and `2` for
usage or file errors. Trace-check writes a matrix even when there are gaps. It
refuses to overwrite either of its input files. The default matrix is
`traceability.md` in the current directory.

## Requirements and quotations

Each requirement starts with a Markdown heading such as `## REQ-001: Title`.
IDs have at least three digits and must be unique. Do not use a requirements table
or nested headings inside a requirement. The source field belongs to that heading's
body and must be exactly one `Source: "<verbatim quote>"` field in its own paragraph.
Quotations may wrap over lines but cannot contain a blank line. The checker
normalises whitespace and curly quote characters; it does
not change case, punctuation, spelling or words. It checks an exact substring, so
choose a complete, meaningful quotation and review the surrounding transcript.

## Specification review

The spec uses `## SEC-001: Title` style headings. Findings use a Markdown table with
columns `id`, `section`, `issue`, `severity`, `raised by`, in that order. Use F-001
style finding IDs, one section ID per row, and no pipe characters inside cells.
Severity is low, medium, high or critical. Raised by is a comma-separated list of
tester, developer, risk and compliance, end user. A header-only table must be
followed by the exact line `No findings.` to distinguish it from missing output.

The checker flags unknown sections, duplicate finding IDs and repeated issue text
in the same section, ignoring case, quote style and whitespace. It does not detect
paraphrased duplicates or verify that an issue is true. The AI consolidator proposes
semantic merges; a person reviews those decisions and the original role outputs.

## Test traceability

The requirement baseline uses REQ headings. Test cases use `## TC-001: Title`
headings with `Requirements: REQ-001, REQ-002`, `Given:`, `When:` and `Then:` fields
on separate lines. All steps must be non-empty. The matrix marks a requirement as
`Linked` when a test references its ID and has complete steps. It also shows missing
links and unknown references. Links do not prove behaviour, assertion quality,
execution or boundary coverage; a person must check the test's meaning.

Do not wrap documents in code fences. The checkers use line-based readers for this
contract, not a general Markdown parser. Reformat unfamiliar layouts before use.
