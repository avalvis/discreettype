from typing_tool.ui.app import find_optional_whitespace_skip_target


def test_finds_skip_target_after_spaces():
    template = "a    bc"
    assert find_optional_whitespace_skip_target(template, 1, "b") == 5


def test_finds_skip_target_after_tabs():
    template = "a\t\tbc"
    assert find_optional_whitespace_skip_target(template, 1, "b") == 3


def test_returns_none_for_non_matching_char():
    template = "a    bc"
    assert find_optional_whitespace_skip_target(template, 1, "x") is None


def test_returns_none_when_not_on_whitespace():
    template = "abc"
    assert find_optional_whitespace_skip_target(template, 1, "c") is None


def test_returns_none_for_whitespace_input():
    template = "a    bc"
    assert find_optional_whitespace_skip_target(template, 1, " ") is None
