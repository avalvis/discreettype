from typing_tool.storage.github_api import GitHubClient


def test_choose_with_recent_prefers_unseen_items(monkeypatch, tmp_path):
    client = GitHubClient(cache_dir=tmp_path)
    options = ["repo-a", "repo-b", "repo-c"]

    # Force deterministic choice from candidates for test stability.
    monkeypatch.setattr("typing_tool.storage.github_api.random.choice", lambda items: items[0])

    first = client._choose_with_recent("sql", options, "repo")
    second = client._choose_with_recent("sql", options, "repo")

    assert first == "repo-a"
    assert second == "repo-b"
