"""Known-answer tests for structural defects, formatting and checker boundaries."""

import json
from collections import Counter
from pathlib import Path

import pytest

from checks import quote_check, review_check, trace_check
from checks.common import read

FIXTURES = Path(__file__).parent / "fixtures"
CASES = json.loads(read(FIXTURES / "manifest.json"))
CHECKERS = {"quote": quote_check.check, "review": review_check.check, "trace": trace_check.check}


@pytest.mark.parametrize("case", CASES, ids=[case["output"] for case in CASES])
def test_labelled_fixtures(case):
    """Require the exact labelled issue and item pairs, not just a matching count."""
    issues = CHECKERS[case["checker"]](read(FIXTURES / case["source"]), read(FIXTURES / case["output"]))
    assert Counter((issue.code, issue.item) for issue in issues) == Counter(tuple(pair) for pair in case["expected"])


@pytest.mark.parametrize("checker", CHECKERS.values())
@pytest.mark.parametrize("output", ["", "Here is a summary.", "| ID | Text |\n| --- | --- |\n| REQ-001 | A rule |"])
def test_unrecognised_documents_fail(checker, output):
    """An empty or unsupported document must never produce a green check."""
    assert any(issue.code == "format" for issue in checker("", output))


def test_quote_does_not_ignore_case_or_words():
    """Normalisation must not turn an altered source into a verbatim match."""
    output = '## REQ-001: Slots\nShow slots.\nSource: "show only available slots."\n'
    assert quote_check.check("Show only available slots.", output)[0].code == "altered_quote"


def test_quote_cannot_borrow_source_from_another_heading():
    """A source under an unrelated heading cannot certify an unsourced requirement."""
    output = '## REQ-001: Slots\nShow slots.\n## Notes\nSource: "Show slots."\n'
    assert quote_check.check("Show slots.", output)[0].code == "missing_source"


def test_quote_with_internal_quotes_and_windows_newlines():
    """Internal quotes, curly punctuation and line breaks normalise consistently."""
    source = 'The status is “pending” until it’s reviewed.'
    output = '## REQ-001: State\r\nSource: “The status is "pending"\r\n until it\'s reviewed.”\r\n'
    assert not quote_check.check(source, output)


def test_quote_does_not_stop_at_an_internal_quote_before_a_newline():
    """Check the entire quotation even when an inner quoted word ends a line."""
    source = 'The status is "pending" until the review is recorded.'
    output = '## REQ-001: State\nSource: "The status is "pending"\n until the booking is deleted."'
    assert quote_check.check(source, output)[0].code == "altered_quote"


@pytest.mark.parametrize("heading", ["REQ-one", "REQ-001"])
def test_invalid_and_repeated_ids_fail(heading):
    """Malformed IDs and duplicate IDs cannot silently collapse into one record."""
    output = f'## REQ-001: A\nSource: "A"\n## {heading}: B\nSource: "B"\n'
    assert quote_check.check("A B", output)


def test_code_fences_fail():
    """Reject an output pasted as a code block, with instructions for fixing it."""
    output = '```md\n## REQ-001: Slots\nSource: "Show slots."\n```'
    assert any(issue.code == "format" for issue in quote_check.check("Show slots.", output))


def test_review_same_issue_different_sections_is_not_duplicate():
    """The same question can legitimately apply to separate sections."""
    findings = read(FIXTURES / "review/good.md").replace("Cancellation feedback is unspecified.", "Competing submissions have no defined outcome.")
    assert not review_check.check(read(FIXTURES / "review/spec.md"), findings)


@pytest.mark.parametrize("replacement", ["| F-001 |", "| F-001 | SEC-001 | Gap | urgent | tester |", "| F-001 | SEC-001 | Gap | high | stranger |"])
def test_review_malformed_rows_fail(replacement):
    """Truncated rows and unknown severity or role labels need correction."""
    findings = "| id | section | issue | severity | raised by |\n| --- | --- | --- | --- | --- |\n" + replacement
    assert review_check.check(read(FIXTURES / "review/spec.md"), findings)


def test_review_empty_table_requires_explicit_no_findings():
    """Distinguish a considered no-findings answer from missing table rows."""
    findings = read(FIXTURES / "review/no-findings.md").replace("No findings.", "")
    assert review_check.check(read(FIXTURES / "review/spec.md"), findings)


def test_incomplete_tests_do_not_cover_a_requirement():
    """A linked but incomplete case leaves the requirement missing in the matrix."""
    issues, matrix = trace_check.analyse(read(FIXTURES / "trace/requirements.md"), read(FIXTURES / "trace/incomplete.md"))
    assert "| REQ-002 | None | MISSING |" in matrix
    assert any(issue.code == "missing_step" for issue in issues)


def test_unknown_references_stay_visible_in_matrix():
    """An invalid test reference remains visible alongside legitimate coverage gaps."""
    _, matrix = trace_check.analyse(read(FIXTURES / "trace/requirements.md"), read(FIXTURES / "trace/flawed.md"))
    assert "| REQ-999 | TC-002 | UNKNOWN REQUIREMENT |" in matrix


def test_ids_in_prose_do_not_count_as_references():
    """Only a valid Requirements field can link a test to its baseline."""
    tests = "## TC-001: Example REQ-001\nGiven: A state.\nWhen: An event.\nThen: A result."
    issues = trace_check.check("## REQ-001: Rule\nA rule.", tests)
    assert {issue.code for issue in issues} == {"missing_reference", "untraced_requirement"}


def test_known_semantic_limits():
    """Document important false assurances that require human judgement."""
    misleading = '## REQ-001: Cancel\nDelete every booking.\nSource: "Show only available slots."'
    assert not quote_check.check("Show only available slots.", misleading)
    irrelevant = "## TC-001: Colour\nRequirements: REQ-001\nGiven: A page.\nWhen: It loads.\nThen: The heading is blue."
    assert not trace_check.check("## REQ-001: Slots\nShow only available slots.", irrelevant)
    paraphrases = "| id | section | issue | severity | raised by |\n| --- | --- | --- | --- | --- |\n| F-001 | SEC-001 | No retry rule. | high | tester |\n| F-002 | SEC-001 | Retrying has unspecified behaviour. | high | developer |"
    assert not review_check.check("## SEC-001: Retry\nThe page may retry.", paraphrases)


@pytest.mark.parametrize("entrypoint", [quote_check.main, review_check.main, trace_check.main])
def test_missing_file_errors_are_friendly(entrypoint, tmp_path, capsys):
    """Filesystem errors return status two without a Python traceback."""
    assert entrypoint([str(tmp_path / "missing.md"), str(tmp_path / "also-missing.md")]) == 2
    assert "Input error:" in capsys.readouterr().out


def test_trace_cli_writes_matrix_when_failing(tmp_path, capsys):
    """A failed trace check still produces the review artefact in a chosen folder."""
    matrix = tmp_path / "nested" / "matrix.md"
    status = trace_check.main([str(FIXTURES / "trace/requirements.md"), str(FIXTURES / "trace/flawed.md"), "--matrix", str(matrix)])
    assert status == 1 and "MISSING" in read(matrix)
    assert "FAIL" in capsys.readouterr().out


def test_trace_cli_refuses_input_overwrite(tmp_path):
    """Matrix generation must preserve both input documents."""
    original = "## REQ-001: Rule\nA rule."
    source = tmp_path / "source.md"
    source.write_text(original)
    with pytest.raises(SystemExit) as error:
        trace_check.main([str(source), str(source), "--matrix", str(source)])
    assert error.value.code == 2 and read(source) == original
