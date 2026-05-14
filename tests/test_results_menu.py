from rich.console import Console

from typing_tool.main import show_results
from typing_tool.storage.models import SessionResult


class _HistoryStub:
    def save_result(self, result):
        return None

    def get_stats(self):
        return None


def test_results_menu_does_not_use_fullscreen_selector(monkeypatch):
    captured_kwargs = {}

    def fake_select_item(*args, **kwargs):
        captured_kwargs.update(kwargs)
        return "Exit"

    monkeypatch.setattr("typing_tool.main.select_item", fake_select_item)

    result = SessionResult(
        snippet_id="s1",
        timestamp=1.0,
        wpm=42.0,
        accuracy=96.5,
        errors=2,
        corrected_errors=1,
        completion_time=12.4,
        language="python",
    )

    keep_going = show_results(Console(record=True), result, _HistoryStub())
    assert keep_going is False
    assert captured_kwargs["full_screen"] is False
    assert captured_kwargs["erase_when_done"] is False
