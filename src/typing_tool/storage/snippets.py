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
            "Algorithms & Basics",
            "Web Development (TS/JS)",
            "System & DevOps (Bash)",
            "Database & SQL",
            "GitHub Explorer",
            "Random Mix"
        ]

    def load_local_snippets(self) -> List[Snippet]:
        if not self.local_path.exists():
            alt_path = Path("../") / self.local_path
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
            return random.sample(local_snippets, min(len(local_snippets), 5))
            
        cat_map = {
            "Algorithms & Basics": ["basics", "algorithms"],
            "Web Development (TS/JS)": ["types", "frontend", "web", "typescript", "javascript"],
            "System & DevOps (Bash)": ["bash", "system", "cli"],
            "Database & SQL": ["sql", "database"]
        }
        
        tags = cat_map.get(category, [])
        filtered = [s for s in local_snippets if any(tag in s.tags for tag in tags)]
        return filtered if filtered else local_snippets

    def fetch_random_github_snippet(self, language: str) -> Optional[Snippet]:
        """
        Fetches a truly random snippet from GitHub using the client.
        Falls back to local if fetching fails.
        """
        snippet = self.gh_client.fetch_random_snippet(language)
        if snippet:
            return snippet
            
        # Fallback to a hard local snippet if online fails
        local_snippets = self.load_local_snippets()
        relevant = [s for s in local_snippets if s.language.lower() == language.lower()]
        return random.choice(relevant) if relevant else random.choice(local_snippets)
