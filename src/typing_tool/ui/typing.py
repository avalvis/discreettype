from prompt_toolkit.layout.processors import Processor, Transformation, TransformationInput
from typing import Dict, Set

class TypingStateProcessor(Processor):
    """
    A processor that styles the buffer based on the user's typing progress.
    It displays the WRONG character if a mistake was made, otherwise the original.
    """
    def __init__(self, mistakes: Dict[int, str], auto_completed: Set[int] = None):
        self.mistakes = mistakes
        self.auto_completed = auto_completed or set()

    def apply_transformation(self, ti: TransformationInput) -> Transformation:
        new_fragments = []
        line_start_index = ti.buffer_control.buffer.document.translate_row_col_to_index(ti.lineno, 0)
        cursor_pos = ti.buffer_control.buffer.cursor_position
        
        current_abs_pos = line_start_index
        
        for style, text in ti.fragments:
            for char in text:
                if current_abs_pos < cursor_pos:
                    if current_abs_pos in self.mistakes:
                        state_style = "class:typing.incorrect"
                        display_char = self.mistakes[current_abs_pos]
                        if display_char == " ": display_char = "·"
                    else:
                        state_style = "class:typing.correct"
                        display_char = char
                elif current_abs_pos == cursor_pos:
                    state_style = "class:typing.cursor"
                    display_char = char
                elif current_abs_pos in self.auto_completed:
                    # Visually indicate this is already "taken care of"
                    state_style = "class:typing.correct"
                    display_char = char
                else:
                    state_style = "class:typing.untyped"
                    display_char = char
                
                combined_style = f"{style} {state_style}".strip()
                new_fragments.append((combined_style, display_char))
                current_abs_pos += 1
        
        if current_abs_pos == cursor_pos:
            new_fragments.append(("class:typing.cursor", " "))
                
        return Transformation(new_fragments)

def get_typing_style():
    """Returns the high-contrast style definitions for the typing area."""
    return {
        # Typing States
        "typing.correct": "bold #ffffff",
        "typing.incorrect": "bg:#cc3333 #ffffff bold",
        "typing.cursor": "bg:#333333 #dddddd blink",
        "typing.untyped": "",
        
        # High-Contrast IDE Syntax Colors (Optimized for readability)
        "pygments.keyword": "#569cd6 bold",           # Bright Blue
        "pygments.keyword.declaration": "#569cd6 bold",
        "pygments.name.function": "#dcdcaa",          # Light Yellow
        "pygments.name.class": "#4ec9b0",             # Teal
        "pygments.string": "#ce9178",                 # Muted Orange
        "pygments.comment": "#6a9955 italic",         # Green
        "pygments.operator": "#d4d4d4",               # Light Gray
        "pygments.punctuation": "#cccccc",            # Light Gray
        "pygments.name": "#9cdcfe",                   # Light Blue
        "pygments.literal.number": "#b5cea8",         # Light Green
        
        # Fixing hard-to-read dark colors
        "pygments.name.variable": "#9cdcfe",          # Ensure variables aren't dark
        "pygments.name.builtin": "#569cd6",           # Ensure builtins are bright
        "pygments.keyword.pseudo": "#569cd6",
        "pygments.name.constant": "#4fc1ff",          # Bright light blue
        
        # UI Elements
        "line-number": "#5a5a5a",
        "line-number.current": "#c6c6c6",
    }
