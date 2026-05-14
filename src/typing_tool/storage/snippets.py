import json
import random
from pathlib import Path
from typing import List, Optional
from .models import Snippet
from .github_api import GitHubClient

class SnippetManager:
    def __init__(self, local_path: Path = Path("data/snippets/curated.json")):
        self.local_path = local_path
        self.gh_client = GitHubClient()

    def get_categories(self) -> List[str]:
        return [
            "Algorithms & Basics (Python)",
            "Web Development (TS/JS)",
            "System & Low-Level (Rust/Go/Cpp)",
            "Shell & DevOps (Bash)",
            "Database & SQL",
            "GitHub Explorer",
            "Random Mix"
        ]

    def load_local_snippets(self) -> List[Snippet]:
        if not self.local_path.exists():
            # Try absolute path or project relative
            alt_path = Path(__file__).parent.parent.parent.parent / self.local_path
            if alt_path.exists():
                self.local_path = alt_path
            else:
                return []
        with open(self.local_path, "r") as f:
            data = json.load(f)
            return [Snippet(**s) for s in data]

    def get_snippets_by_category(self, category: str) -> List[Snippet]:
        local_snippets = self.load_local_snippets()
        
        if category == "Random Mix":
            return random.sample(local_snippets, min(len(local_snippets), 10))
            
        cat_map = {
            "Algorithms & Basics (Python)": ["basics", "algorithms", "decorators", "advanced"],
            "Web Development (TS/JS)": ["types", "frontend", "web", "typescript", "javascript", "async"],
            "System & Low-Level (Rust/Go/Cpp)": ["rust", "enums", "patterns", "go", "concurrency", "cpp", "templates"],
            "Shell & DevOps (Bash)": ["bash", "system", "cli"],
            "Database & SQL": ["sql", "database"]
        }
        
        tags = cat_map.get(category, [])
        filtered = [s for s in local_snippets if any(tag in s.tags for tag in tags)]
        return filtered if filtered else local_snippets

    def fetch_random_github_snippet(self, language: str) -> Optional[Snippet]:
        """
        Fetch a random snippet from GitHub. On failure, fall back to a local
        snippet that matches the requested language. Returns ``None`` only
        when nothing is available (offline AND no curated snippet exists for
        the language).
        """
        snippet = self.gh_client.fetch_random_snippet(language)
        if snippet:
            return snippet

        local_snippets = self.load_local_snippets()
        relevant = [s for s in local_snippets if s.language.lower() == language.lower()]
        if relevant:
            return random.choice(relevant)
        return None
