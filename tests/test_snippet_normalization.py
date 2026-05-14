from typing_tool.storage.models import Snippet, normalize_snippet_code


def test_tabs_expanded_to_four_spaces():
    raw = "def f():\n\treturn 1"
    assert normalize_snippet_code(raw) == "def f():\n    return 1"


def test_mixed_tab_and_space_indentation_is_expanded():
    raw = "if x:\n\t  pass"
    assert normalize_snippet_code(raw) == "if x:\n      pass"


def test_trailing_whitespace_per_line_is_stripped():
    raw = "a = 1   \nb = 2\t\nc = 3"
    assert normalize_snippet_code(raw) == "a = 1\nb = 2\nc = 3"


def test_crlf_line_endings_are_normalized():
    raw = "select 1;\r\nselect 2;\r\n"
    assert normalize_snippet_code(raw) == "select 1;\nselect 2;"


def test_surrounding_blank_lines_are_trimmed():
    raw = "\n\n   \n  body  \n\n\n"
    assert normalize_snippet_code(raw) == "  body"


def test_empty_input_returns_empty_string():
    assert normalize_snippet_code("") == ""


def test_snippet_model_normalizes_code_on_construction():
    snippet = Snippet(
        id="sql-1",
        language="SQL",
        title="indent test",
        code="SELECT 1\n\tFROM t\n\tWHERE a = 1   ",
        difficulty="easy",
        tags=[],
    )
    # No raw tab characters survive, so the BufferControl can never fall
    # back to caret notation and render "^I".
    assert "\t" not in snippet.code
    assert snippet.code == "SELECT 1\n    FROM t\n    WHERE a = 1"
