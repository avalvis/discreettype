import requests
import random
import json
import os
import hashlib
import math
from pathlib import Path
from typing import List, Optional, Dict
from .models import Snippet

class GitHubClient:
    def __init__(self, cache_dir: Path = Path.home() / ".typing_tool" / "cache"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "github_snippets.json"
        self.base_url = "https://api.github.com"
        self.headers = {
            "Accept": "application/vnd.github.v3+json",
            "User-Agent": "discreet-code-typing-practice",
        }
        token = os.getenv("GITHUB_TOKEN")
        if token:
            self.headers["Authorization"] = f"Bearer {token}"
        self._recent_choices: Dict[str, List[str]] = {}

    def _remember_choice(self, language: str, key: str):
        lang = language.lower()
        recent = self._recent_choices.setdefault(lang, [])
        recent.append(key)
        if len(recent) > 12:
            recent.pop(0)

    def _choose_with_recent(self, language: str, options: List[str], key_prefix: str) -> Optional[str]:
        if not options:
            return None
        lang = language.lower()
        recent = set(self._recent_choices.get(lang, []))
        candidates = [option for option in options if f"{key_prefix}:{option}" not in recent]
        chosen = random.choice(candidates if candidates else options)
        self._remember_choice(language, f"{key_prefix}:{chosen}")
        return chosen

    def _get_cache(self) -> Dict[str, List[dict]]:
        if not self.cache_file.exists():
            return {}
        try:
            return json.loads(self.cache_file.read_text())
        except Exception:
            return {}

    def _save_to_cache(self, language: str, snippet_data: dict):
        cache = self._get_cache()
        if language not in cache:
            cache[language] = []
        
        # Keep only the last 50 snippets per language
        cache[language].append(snippet_data)
        if len(cache[language]) > 50:
            cache[language].pop(0)
            
        self.cache_file.write_text(json.dumps(cache, indent=4))

    def fetch_random_snippet(self, language: str) -> Optional[Snippet]:
        """
        Main entry point to get a random snippet from GitHub.
        """
        # 1. Try to fetch fresh from GitHub
        snippet = self._fetch_from_github(language)
        if snippet:
            return snippet
            
        # 2. Fallback to cache if GitHub fails (rate limit, offline)
        cache = self._get_cache()
        if language in cache and cache[language]:
            options = [json.dumps(item, sort_keys=True) for item in cache[language]]
            selected = self._choose_with_recent(language, options, "cache")
            if selected is None:
                return None
            data = json.loads(selected)
            return Snippet(**data)
            
        return None

    def _fetch_from_github(self, language: str) -> Optional[Snippet]:
        try:
            # Step 1: Search for popular repos in that language
            per_page = 30
            stars_floor = {
                "sql": 10,
                "bash": 50,
                "python": 100,
                "javascript": 100,
                "typescript": 100,
            }.get(language.lower(), 100)
            search_query = f"stars:>{stars_floor} language:{language}"
            first_page_url = (
                f"{self.base_url}/search/repositories?q={search_query}"
                f"&sort=updated&order=desc&per_page={per_page}&page=1"
            )
            first_resp = requests.get(first_page_url, headers=self.headers, timeout=5)
            if first_resp.status_code != 200:
                return None

            first_payload = first_resp.json()
            total_count = min(first_payload.get("total_count", 0), 1000)
            if total_count <= 0:
                return None

            max_pages = max(1, math.ceil(total_count / per_page))
            page = random.randint(1, min(max_pages, 10))
            if page == 1:
                repos = first_payload.get("items", [])
            else:
                search_url = (
                    f"{self.base_url}/search/repositories?q={search_query}"
                    f"&sort=updated&order=desc&per_page={per_page}&page={page}"
                )
                resp = requests.get(search_url, headers=self.headers, timeout=5)
                if resp.status_code != 200:
                    return None
                repos = resp.json().get("items", [])
            if not repos:
                return None
                
            repo_options = [f"{r['owner']['login']}/{r['name']}" for r in repos]
            selected_repo = self._choose_with_recent(language, repo_options, "repo")
            if selected_repo is None:
                return None
            owner, name = selected_repo.split("/", 1)
            repo = next((r for r in repos if r["owner"]["login"] == owner and r["name"] == name), None)
            if repo is None:
                return None
            owner = repo["owner"]["login"]
            name = repo["name"]
            
            # Step 2: Get the file tree
            # We use recursive=1 to find files deep in the repo
            tree_url = f"{self.base_url}/repos/{owner}/{name}/git/trees/{repo['default_branch']}?recursive=1"
            tree_resp = requests.get(tree_url, headers=self.headers, timeout=5)
            if tree_resp.status_code != 200:
                return None
                
            # Step 3: Filter for interesting source files
            ext_map = {
                "python": ".py",
                "typescript": ".ts",
                "javascript": ".js",
                "sql": ".sql",
                "bash": ".sh"
            }
            ext = ext_map.get(language.lower(), ".py")
            
            files = [
                item["path"] for item in tree_resp.json().get("tree", [])
                if item["type"] == "blob" and item["path"].endswith(ext)
                and not any(x in item["path"].lower() for x in ["test", "setup", "__init__", "license", "node_modules"])
            ]
            
            if not files:
                return None
                
            file_path = self._choose_with_recent(language, files, f"file:{owner}/{name}")
            if file_path is None:
                return None
            
            # Step 4: Fetch raw content
            raw_url = f"https://raw.githubusercontent.com/{owner}/{name}/{repo['default_branch']}/{file_path}"
            content_resp = requests.get(raw_url, timeout=5)
            if content_resp.status_code != 200:
                return None
                
            # Step 5: Extract a clean snippet
            lines = content_resp.text.splitlines()
            # Find a block that is at least 10 lines and not just comments
            if len(lines) < 10:
                return None
                
            window = min(max(14, random.randint(14, 28)), len(lines))
            start_line = random.randint(0, max(0, len(lines) - window))
            snippet_lines = lines[start_line : start_line + window]
            code = "\n".join(snippet_lines)
            snippet_uid = hashlib.sha1(
                f"{owner}/{name}:{file_path}:{start_line}:{window}".encode("utf-8")
            ).hexdigest()[:12]
            
            snippet_data = {
                "id": f"gh-{owner}-{name}-{snippet_uid}",
                "language": language,
                "title": f"{name}: {file_path.split('/')[-1]}",
                "code": code,
                "difficulty": "hard",
                "tags": ["github", "real-world", language]
            }
            
            # Save to cache for offline use
            self._save_to_cache(language, snippet_data)
            
            return Snippet(**snippet_data)

        except Exception:
            return None
