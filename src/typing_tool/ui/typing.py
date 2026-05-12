from prompt_toolkit.layout.processors import Processor, Transformation, TransformationInput
from typing import Dict

class TypingStateProcessor(Processor):
    """
    A processor that styles the buffer based on the user's typing progress.
    It displays the WRONG character if a mistake was made, otherwise the original.
    """
    def __init__(self, mistakes: Dict[int, str]):
        self.mistakes = mistakes

    def apply_transformation(self, ti: TransformationInput) -> Transformation:
        new_fragments = []
        # CORRECT way to get the absolute index of the start of the current line
        line_start_index = ti.buffer_control.buffer.document.translate_row_col_to_index(ti.lineno, 0)
        cursor_pos = ti.buffer_control.buffer.cursor_position
        
        current_abs_pos = line_start_index
        
        # ti.fragments contains the syntax-highlighted fragments for the current line
        for style, text in ti.fragments:
            for char in text:
                # Determine typing state style
                if current_abs_pos < cursor_pos:
                    if current_abs_pos in self.mistakes:
                        # Error: Red background
                        state_style = "class:typing.incorrect"
                        display_char = self.mistakes[current_abs_pos]
                        if display_char == " ": display_char = "·"
                    else:
                        # Correct: Bold the original syntax color
                        state_style = "class:typing.correct"
                        display_char = char
                elif current_abs_pos == cursor_pos:
                    # Cursor: Highlight this character
                    state_style = "class:typing.cursor"
                    display_char = char
                else:
                    # Untyped: Use standard syntax highlighting ONLY
                    state_style = "" 
                    display_char = char
                
                # Combine the lexer style with our state class
                combined_style = f"{style} {state_style}".strip()
                new_fragments.append((combined_style, display_char))
                current_abs_pos += 1
        
        # Handle trailing cursor (at the end of a line)
        if current_abs_pos == cursor_pos:
            new_fragments.append(("class:typing.cursor", " "))
                
        return Transformation(new_fragments)

def get_typing_style():
    """Returns the style definitions for the typing area."""
    return {
        # Typing States
        "typing.correct": "bold #ffffff",           # Bold white for typed text
        "typing.incorrect": "bg:#cc3333 #ffffff bold", # Bright red for mistakes
        "typing.cursor": "reverse #ffffff",         # Block cursor
        
        # VS Code-like Muted Syntax Colors (Dark Theme)
        "pygments.keyword": "#569cd6",
        "pygments.keyword.declaration": "#569cd6",
        "pygments.name.function": "#dcdcaa",
        "pygments.name.class": "#4ec9b0",
        "pygments.string": "#ce9178",
        "pygments.comment": "#6a9955 italic",
        "pygments.operator": "#d4d4d4",
        "pygments.punctuation": "#cccccc",
        "pygments.name": "#9cdcfe",
        "pygments.literal.number": "#b5cea8",
        
        # UI Elements
        "line-number": "#5a5a5a",
        "line-number.current": "#c6c6c6",
    }
