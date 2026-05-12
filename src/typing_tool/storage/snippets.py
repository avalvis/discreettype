import json
import random
import requests
from pathlib import Path
from typing import List, Optional
from .models import Snippet

class SnippetManager:
    def __init__(self, local_path: Path = Path("data/snippets/curated.json")):
        self.local_path = local_path
        # A curated list of raw GitHub URLs for interesting code
        self.github_sources = [
            {
                "id": "gh-py-req",
                "url": "https://raw.githubusercontent.com/psf/requests/main/src/requests/api.py",
                "language": "python",
                "title": "Requests: API implementation",
                "difficulty": "hard",
                "tags": ["python", "web", "api"]
            },
            {
                "id": "gh-ts-redux",
                "url": "https://raw.githubusercontent.com/reduxjs/redux/master/src/createStore.ts",
                "language": "typescript",
                "title": "Redux: createStore",
                "difficulty": "hard",
                "tags": ["typescript", "web", "state-management"]
            },
            {
                "id": "gh-sql-bench",
                "url": "https://raw.githubusercontent.com/timescale/tsbs/master/scripts/load_timescale.sh",
                "language": "bash",
                "title": "TSBS: Load Script",
                "difficulty": "medium",
                "tags": ["bash", "system", "database"]
            }
        ]

    def get_categories(self) -> List[str]:
        return [
            "Algorithms & Basics",
            "Web Development (TS/JS)",
            "System & DevOps (Bash)",
            "Database & SQL",
            "Real-World GitHub Code",
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

    def fetch_github_snippet(self, source_info: dict) -> Optional[Snippet]:
        try:
            response = requests.get(source_info["url"], timeout=3)
            if response.status_code == 200:
                # Take only a medium-sized chunk (first 20 lines) to keep it manageable
                lines = response.text.splitlines()[:20]
                code = "\n".join(lines)
                return Snippet(
                    id=source_info["id"],
                    language=source_info["language"],
                    title=source_info["title"],
                    code=code,
                    difficulty=source_info["difficulty"],
                    tags=source_info["tags"]
                )
        except Exception:
            return None
        return None

    def get_snippets_by_category(self, category: str) -> List[Snippet]:
        local_snippets = self.load_local_snippets()
        
        if category == "Real-World GitHub Code":
            online = []
            for src in self.github_sources:
                snippet = self.fetch_github_snippet(src)
                if snippet:
                    online.append(snippet)
            return online if online else [s for s in local_snippets if "hard" in s.difficulty]

        if category == "Random Mix":
            return random.sample(local_snippets, min(len(local_snippets), 5))
            
        cat_map = {
            "Algorithms & Basics": ["basics", "algorithms"],
            "Web Development (TS/JS)": ["types", "frontend", "web", "typescript"],
            "System & DevOps (Bash)": ["bash", "system", "cli"],
            "Database & SQL": ["sql", "database"]
        }
        
        tags = cat_map.get(category, [])
        filtered = [s for s in local_snippets if any(tag in s.tags for tag in tags)]
        return filtered if filtered else local_snippets
