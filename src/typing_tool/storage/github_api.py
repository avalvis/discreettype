import requests
import random
import json
from pathlib import Path
from typing import List, Optional, Dict
from .models import Snippet

class GitHubClient:
    def __init__(self, cache_dir: Path = Path.home() / ".typing_tool" / "cache"):
        self.cache_dir = cache_dir
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.cache_file = self.cache_dir / "github_snippets.json"
        self.base_url = "https://api.github.com"
        self.headers = {"Accept": "application/vnd.github.v3+json"}

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
            data = random.choice(cache[language])
            return Snippet(**data)
            
        return None

    def _fetch_from_github(self, language: str) -> Optional[Snippet]:
        try:
            # Step 1: Search for popular repos in that language
            # We add a random page to get variety
            page = random.randint(1, 5)
            search_query = f"stars:>1000 language:{language}"
            search_url = f"{self.base_url}/search/repositories?q={search_query}&sort=stars&order=desc&per_page=10&page={page}"
            
            resp = requests.get(search_url, headers=self.headers, timeout=5)
            if resp.status_code != 200:
                return None
                
            repos = resp.json().get("items", [])
            if not repos:
                return None
                
            repo = random.choice(repos)
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
                
            file_path = random.choice(files)
            
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
                
            start_line = random.randint(0, max(0, len(lines) - 20))
            snippet_lines = lines[start_line : start_line + 20]
            code = "\n".join(snippet_lines)
            
            snippet_data = {
                "id": f"gh-{owner}-{name}-{hash(file_path)}",
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
