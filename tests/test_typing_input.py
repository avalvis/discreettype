from typing_tool.storage.models import Snippet
from typing_tool.ui.app import (
    CTRL_NAV_KEYS_TO_DISABLE,
    PAGER_KEYS_TO_RECLAIM,
    TypingApp,
)


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


def test_footer_shows_refresh_hint_only_when_enabled(monkeypatch):
    class _DummyApplication:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            return None

    monkeypatch.setattr("typing_tool.ui.app.Application", _DummyApplication)

    snippet = Snippet(
        id="t2",
        language="sql",
        title="footer test",
        code="select 1;",
        difficulty="easy",
        tags=[],
    )

    normal = TypingApp(snippet, mode="standard", allow_refresh=False)
    refreshable = TypingApp(snippet, mode="standard", allow_refresh=True)

    assert "F5" not in normal.footer.content.text
    assert "F5" in refreshable.footer.content.text


def _registered_keys(app):
    """Collect every single-key binding registered on the app's KeyBindings."""
    keys = set()
    for binding in app.kb.bindings:
        if len(binding.keys) == 1:
            keys.add(binding.keys[0])
    return keys


def test_pager_keys_are_reclaimed_from_emacs_read_only_bindings(monkeypatch):
    """Regression test for the 'n' key acting as cheat mode.

    prompt_toolkit's default emacs bindings turn n / N / ? / / into pager
    navigation when the focused buffer is read-only. We must register
    explicit single-key bindings so the typing handler wins.
    """

    class _DummyApplication:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            return None

    monkeypatch.setattr("typing_tool.ui.app.Application", _DummyApplication)

    snippet = Snippet(
        id="t3",
        language="python",
        title="binding test",
        code="abc",
        difficulty="easy",
        tags=[],
    )
    app = TypingApp(snippet, mode="ide")
    keys = _registered_keys(app)

    for pager_key in PAGER_KEYS_TO_RECLAIM:
        assert pager_key in keys, f"missing reclaim for {pager_key!r}"


def test_ctrl_navigation_keys_are_neutralized(monkeypatch):
    class _DummyApplication:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            return None

    monkeypatch.setattr("typing_tool.ui.app.Application", _DummyApplication)

    snippet = Snippet(
        id="t4",
        language="python",
        title="ctrl nav test",
        code="abc",
        difficulty="easy",
        tags=[],
    )
    app = TypingApp(snippet, mode="ide")
    keys = _registered_keys(app)

    for ctrl_key in CTRL_NAV_KEYS_TO_DISABLE:
        assert ctrl_key in keys, f"missing override for {ctrl_key!r}"


def test_pressing_n_advances_through_handle_char_only(monkeypatch):
    """When the template's next character is 'n', typing 'n' must record
    one correct keystroke and advance exactly one position - not jump to
    some later 'n' the way the prompt_toolkit pager binding would."""

    class _DummyApplication:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            return None

    monkeypatch.setattr("typing_tool.ui.app.Application", _DummyApplication)

    snippet = Snippet(
        id="t5",
        language="python",
        title="n typing test",
        code="name = None",
        difficulty="easy",
        tags=[],
    )
    app = TypingApp(snippet, mode="ide")

    app.handle_char("n")
    assert app.buffer.cursor_position == 1
    assert app.session.errors == 0


def test_boss_mode_suppresses_typing(monkeypatch):
    class _DummyApplication:
        def __init__(self, *args, **kwargs):
            pass

        def run(self):
            return None

    monkeypatch.setattr("typing_tool.ui.app.Application", _DummyApplication)

    snippet = Snippet(
        id="t6",
        language="python",
        title="boss mode test",
        code="abc",
        difficulty="easy",
        tags=[],
    )
    app = TypingApp(snippet, mode="standard")
    app.boss_mode = True

    app.handle_char("a")
    assert app.buffer.cursor_position == 0
    assert app.session.errors == 0
    assert app.session.start_time is None
