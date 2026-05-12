from pydantic import BaseModel
from typing import List, Optional

class Snippet(BaseModel):
    id: str
    language: str
    title: str
    code: str
    difficulty: str  # easy, medium, hard
    tags: List[str] = []

class SessionResult(BaseModel):
    snippet_id: str
    timestamp: float
    wpm: float
    accuracy: float
    errors: int
    corrected_errors: int
    completion_time: float
    language: str
