import pytest
import time
from typing_tool.core.session import TypingSession

def test_session_wpm_calculation():
    target = "Hello World" # 11 chars
    session = TypingSession("test", target, "text")
    
    session.start()
    # Mocking time passing: 11 chars in 6 seconds = 110 chars/min = 22 WPM
    session.start_time = time.time() - 6
    session.update_progress(target)
    session.end()
    
    metrics = session.get_metrics()
    # (11 / 5) / (6 / 60) = 2.2 / 0.1 = 22
    assert round(metrics.wpm) == 22

def test_session_accuracy():
    target = "abc"
    session = TypingSession("test", target, "text")
    
    session.start()
    session.update_progress("a")
    session.update_progress("ax") # 'a' correct, 'x' wrong. Mistakes = 1
    session.update_progress("a")  # backspace
    session.update_progress("ab") # 'a' correct, 'b' correct (corrected 'x'). Corrected = 1
    session.update_progress("abc") # all correct
    session.end()
    
    metrics = session.get_metrics()
    # Total attempts = 3 (target) + 1 (mistake) = 4
    # Accuracy = (4 - 1) / 4 = 75%
    assert metrics.accuracy == 75.0
    assert metrics.errors == 1
    assert metrics.corrected_errors == 1
