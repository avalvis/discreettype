from pydantic import BaseModel, field_validator
from typing import List, Optional

# Number of spaces used to expand a tab when normalizing snippet code.
# Tabs are normalized because prompt_toolkit's BufferControl renders raw
# control characters (including \t) as caret notation (e.g. "^I") when the
# default input processors are disabled, which we do for typing accuracy.
SNIPPET_TAB_WIDTH = 4


def normalize_snippet_code(raw: str) -> str:
    """Make snippet source safe to render in the typing buffer.

    - Normalize line endings to "\\n".
    - Expand tabs to spaces so they render correctly and can be typed
      reliably with the space bar.
    - Strip trailing whitespace per line (irrelevant noise the user can't
      see but would still be required to type).
    - Trim surrounding blank lines so the snippet always begins on the
      first visible character.
    """
    if not raw:
        return ""
    # Unify line endings before any other processing.
    text = raw.replace("\r\n", "\n").replace("\r", "\n")
    lines = [line.expandtabs(SNIPPET_TAB_WIDTH).rstrip() for line in text.split("\n")]
    # Drop leading/trailing blank lines.
    start = 0
    end = len(lines)
    while start < end and not lines[start]:
        start += 1
    while end > start and not lines[end - 1]:
        end -= 1
    return "\n".join(lines[start:end])


class Snippet(BaseModel):
    id: str
    language: str
    title: str
    code: str
    difficulty: str  # easy, medium, hard
    tags: List[str] = []

    @field_validator("code", mode="before")
    @classmethod
    def _normalize_code(cls, value: object) -> str:
        if not isinstance(value, str):
            return value  # let pydantic surface the type error
        return normalize_snippet_code(value)

class SessionResult(BaseModel):
    snippet_id: str
    timestamp: float
    wpm: float
    accuracy: float
    errors: int
    corrected_errors: int
    completion_time: float
    language: str
