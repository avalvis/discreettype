from typing_tool.storage.models import Snippet
from typing_tool.ui.app import TypingApp


def test_wrong_character_does_not_advance_cursor(monkeypatch):
    class _DummyApplication:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            return None

    # Avoid requiring a real interactive console during tests.
    monkeypatch.setattr("typing_tool.ui.app.Application", _DummyApplication)

    snippet = Snippet(
        id="t1",
        language="python",
        title="cursor test",
        code="abc",
        difficulty="easy",
        tags=[],
    )
    app = TypingApp(snippet, mode="standard")

    app.handle_char("n")
    assert app.buffer.cursor_position == 0
    assert app.session.errors == 1
    assert app.mistakes[0] == "n"

    app.handle_char("a")
    assert app.buffer.cursor_position == 1
    assert app.session.corrected_errors == 1
