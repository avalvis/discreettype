from types import SimpleNamespace

from typing_tool import main as main_module


def test_refresh_keeps_mode_and_language(monkeypatch):
    first_snippet = SimpleNamespace(id="s1", language="SQL", title="first", code="SELECT 1;")
    second_snippet = SimpleNamespace(id="s2", language="SQL", title="second", code="SELECT 2;")

    class _SnippetManagerStub:
        def __init__(self):
            self.refresh_calls = []

        def fetch_random_github_snippet(self, language: str):
            self.refresh_calls.append(language)
            return second_snippet

    manager = _SnippetManagerStub()

    selections = iter([(first_snippet, "SQL"), None])

    def fake_show_main_menu(console, snippet_manager):
        return next(selections)

    monkeypatch.setattr(main_module, "show_main_menu", fake_show_main_menu)
    monkeypatch.setattr(main_module, "SnippetManager", lambda: manager)
    monkeypatch.setattr(main_module, "HistoryManager", lambda: object())
    monkeypatch.setattr(main_module, "select_item", lambda *args, **kwargs: "ide")

    created_apps = []
    run_results = iter(["refresh_snippet", SimpleNamespace(dummy=True)])

    class _TypingAppStub:
        def __init__(self, snippet, mode="standard", allow_refresh=False):
            created_apps.append((snippet, mode, allow_refresh))

        def run(self):
            return next(run_results)

    monkeypatch.setattr(main_module, "TypingApp", _TypingAppStub)
    monkeypatch.setattr(main_module, "show_results", lambda console, result, history: False)

    main_module.main()

    assert manager.refresh_calls == ["SQL"]
    assert created_apps[0] == (first_snippet, "ide", True)
    assert created_apps[1] == (second_snippet, "ide", True)
