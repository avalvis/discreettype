import json
from pathlib import Path
from typing import List
from .models import SessionResult

class HistoryManager:
    def __init__(self, storage_path: Path = Path.home() / ".typing_tool" / "history.json"):
        self.storage_path = storage_path
        self.storage_path.parent.mkdir(parents=True, exist_ok=True)
        
    def save_result(self, result: SessionResult):
        history = self.load_history()
        history.append(result)
        
        with open(self.storage_path, "w") as f:
            # We use model_dump() for Pydantic v2
            data = [r.model_dump() for r in history]
            json.dump(data, f, indent=4)
            
    def load_history(self) -> List[SessionResult]:
        if not self.storage_path.exists():
            return []
            
        try:
            with open(self.storage_path, "r") as f:
                data = json.load(f)
                return [SessionResult(**item) for item in data]
        except (json.JSONDecodeError, KeyError):
            return []
            
    def get_stats(self):
        history = self.load_history()
        if not history:
            return None
            
        avg_wpm = sum(r.wpm for r in history) / len(history)
        avg_accuracy = sum(r.accuracy for r in history) / len(history)
        total_sessions = len(history)
        
        return {
            "avg_wpm": avg_wpm,
            "avg_accuracy": avg_accuracy,
            "total_sessions": total_sessions
        }
