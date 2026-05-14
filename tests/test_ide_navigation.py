from typing_tool.ui.app import (
    compute_post_char_skip_cursor,
    find_auto_completed_skip_target,
    find_comment_skip_span,
)


def test_post_char_skip_does_not_advance_on_regular_letter():
    template = "print(name)"
    cursor = 3
    assert compute_post_char_skip_cursor(template, cursor, "n", set()) == cursor


def test_post_char_skip_advances_through_repeated_whitespace():
    template = "a    b"
    cursor = 1
    assert compute_post_char_skip_cursor(template, cursor, " ", set()) == 5


def test_post_char_skip_advances_over_auto_completed_closer():
    template = "()"
    cursor = 1
    assert compute_post_char_skip_cursor(template, cursor, ")", {1}) == 2


def test_right_arrow_auto_completed_skip_single_closer():
    assert find_auto_completed_skip_target(5, 10, {5}) == 6


def test_right_arrow_auto_completed_skip_contiguous_block():
    assert find_auto_completed_skip_target(3, 10, {3, 4, 5}) == 6


def test_right_arrow_auto_completed_skip_returns_none_when_not_on_auto_completed():
    assert find_auto_completed_skip_target(2, 10, {3, 4}) is None


def test_comment_skip_span_python_comment_from_whitespace_before_comment():
    template = "value = 1    # explain this\nnext_line"
    cursor = template.index("#") - 2
    start, end = find_comment_skip_span(template, cursor, "python")
    assert start == cursor
    assert template[start:end] == "  # explain this"


def test_comment_skip_span_inside_comment():
    template = "value = 1  # explain this"
    cursor = template.index("#") + 2
    start, end = find_comment_skip_span(template, cursor, "python")
    assert start == cursor
    assert template[start:end] == "explain this"


def test_comment_skip_span_returns_none_when_non_whitespace_before_comment():
    template = "value = 1 + # not skippable from here"
    cursor = template.index("+")
    assert find_comment_skip_span(template, cursor, "python") is None
