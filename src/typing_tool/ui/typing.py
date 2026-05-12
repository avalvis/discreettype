from prompt_toolkit.layout.processors import Processor, Transformation, TransformationInput
from pygments.lexers import get_lexer_by_name
from pygments.lexers.python import PythonLexer
from pygments.util import ClassNotFound
import pygments

class TypingOverlayProcessor(Processor):
    """
    A processor that renders the target text 'under' the user's input,
    coloring characters based on correctness and retaining syntax highlighting.
    """
    def __init__(self, target_text: str, lexer_name: str = "python"):
        self.target_text = target_text
        try:
            self.lexer = get_lexer_by_name(lexer_name)
        except ClassNotFound:
            self.lexer = PythonLexer()
            
        # Pre-calculate syntax highlighting tokens for the target text
        self.tokens = list(pygments.lex(target_text, self.lexer))
        self.char_styles = []
        for token_type, value in self.tokens:
            token_str = str(token_type).replace("Token.", "").lower()
            style_class = f"class:pygments.{token_str}"
            for char in value:
                self.char_styles.append(style_class)

    def apply_transformation(self, ti: TransformationInput) -> Transformation:
        fragments = []
        user_text = ti.buffer_control.buffer.text
        
        for i, char in enumerate(self.target_text):
            syntax_style = self.char_styles[i] if i < len(self.char_styles) else ""
            
            if i < len(user_text):
                # Character has been typed
                if user_text[i] == char:
                    # Correct - Brightened syntax color or white
                    # For a professional look, let's use a "bright" version of the syntax color
                    # or a dedicated 'correct' style.
                    fragments.append((f"{syntax_style} class:typing.correct", char))
                else:
                    # Incorrect - Error highlight
                    display_char = char if char != "\n" else "↵\n"
                    fragments.append(("class:typing.incorrect", display_char))
            elif i == len(user_text):
                # Current cursor position
                # If the target char is a newline, we might want to show a hint
                display_char = char
                if char == "\n":
                    fragments.append(("class:typing.cursor", "↵"))
                    fragments.append(("", "\n"))
                else:
                    fragments.append((f"{syntax_style} class:typing.cursor", char))
            else:
                # Untyped character - Dimmed syntax highlighting
                fragments.append((f"{syntax_style} class:typing.untyped", char))
                
        return Transformation(fragments)

def get_typing_style():
    """Returns the style definitions for the typing area."""
    return {
        # Typing States
        "typing.correct": "#ffffff bold",        # Bright white
        "typing.incorrect": "bg:#880000 #ffffff", # Red background for mistakes
        "typing.untyped": "#444444",              # Default muted gray fallback
        "typing.cursor": "reverse #ffffff",       # Active position (Block cursor effect)
        
        # Professional Muted Pygments Styles (Subtle but distinct)
        "pygments.keyword": "#569cd6",           # Blue
        "pygments.name.function": "#dcdcaa",     # Yellowish
        "pygments.name.class": "#4ec9b0",        # Teal
        "pygments.string": "#ce9178",            # Orange/Brown
        "pygments.comment": "#6a9955",           # Green
        "pygments.operator": "#d4d4d4",          # Light Gray
        "pygments.punctuation": "#808080",       # Darker Gray
        "pygments.name": "#9cdcfe",              # Light Blue
        "pygments.literal.number": "#b5cea8",    # Light Green
        "pygments.keyword.declaration": "#569cd6",
        "pygments.name.builtin": "#569cd6",
    }
