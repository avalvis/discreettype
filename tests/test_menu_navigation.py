from rich.console import Console

from typing_tool.main import show_main_menu


class _Snippet:
    def __init__(self, language: str, title: str, difficulty: str):
        self.language = language
        self.title = title
        self.difficulty = difficulty


class _SnippetManagerStub:
    def __init__(self, snippet):
        self.snippet = snippet

    def get_categories(self):
        return ["Local Category"]

    def get_snippets_by_category(self, category):
        assert category == "Local Category"
        return [self.snippet]


def test_escape_from_snippet_selection_goes_back_to_category(monkeypatch):
    snippet = _Snippet("python", "Example", "easy")
    manager = _SnippetManagerStub(snippet)
    console = Console(record=True)

    selections = iter([
        "Local Category",  # Open local snippet list
        None,              # Esc -> go back to category selection
        "Local Category",  # Re-open local snippet list
        snippet,           # Pick a snippet
    ])

    def fake_select_item(*args, **kwargs):
        return next(selections)

    monkeypatch.setattr("typing_tool.main.select_item", fake_select_item)

    selected = show_main_menu(console, manager)
    assert selected == (snippet, None)
