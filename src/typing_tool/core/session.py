import time
from typing import List, Optional, Set
from ..storage.models import SessionResult

class TypingSession:
    def __init__(self, snippet_id: str, target_text: str, language: str):
        self.snippet_id = snippet_id
        self.target_text = target_text
        self.language = language
        
        self.start_time: Optional[float] = None
        self.end_time: Optional[float] = None
        
        self.errors = 0
        self.corrected_errors = 0
        self.last_text = ""
        
        # Track which indices have been incorrectly typed at least once
        self.miskeyed_indices: Set[int] = set()
        
    def start(self):
        self.start_time = time.time()
        
    def end(self):
        self.end_time = time.time()
        
    def update_progress(self, current_text: str):
        if not self.start_time:
            self.start()
            
        # If text got shorter, user backspaced
        if len(current_text) < len(self.last_text):
            # We don't increment errors on backspace itself, 
            # but we can track if they corrected something.
            pass
        elif len(current_text) > len(self.last_text):
            # User typed new characters
            for i in range(len(self.last_text), len(current_text)):
                if i < len(self.target_text):
                    if current_text[i] != self.target_text[i]:
                        self.errors += 1
                        self.miskeyed_indices.add(i)
                    elif i in self.miskeyed_indices:
                        # They previously typed this wrong and now typed it right
                        self.corrected_errors += 1
                        # Remove from miskeyed so we don't count correction twice
                        self.miskeyed_indices.remove(i)
                        
        self.last_text = current_text

    @property
    def duration(self) -> float:
        if not self.start_time:
            return 0
        end = self.end_time or time.time()
        return end - self.start_time

    def get_metrics(self) -> SessionResult:
        duration_mins = self.duration / 60
        # WPM: (Total characters / 5) / time in minutes
        # We use the target text length for "correct" WPM
        char_count = len(self.target_text)
        wpm = (char_count / 5) / duration_mins if duration_mins > 0 else 0
        
        # Accuracy: (Total Attempts - Mistakes) / Total Attempts
        # Mistakes include uncorrected errors.
        total_attempts = len(self.target_text) + self.errors
        accuracy = ((total_attempts - self.errors) / total_attempts) * 100 if total_attempts > 0 else 0
        
        return SessionResult(
            snippet_id=self.snippet_id,
            timestamp=self.start_time or time.time(),
            wpm=wpm,
            accuracy=accuracy,
            errors=self.errors,
            corrected_errors=self.corrected_errors,
            completion_time=self.duration,
            language=self.language
        )
