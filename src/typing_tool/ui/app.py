from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from prompt_toolkit.filters import Condition
from prompt_toolkit.document import Document

from ..core.session import TypingSession
from .typing import TypingStateProcessor, get_typing_style

class TypingApp:
    def __init__(self, snippet, mode: str = "standard"):
        self.snippet = snippet
        self.mode = mode
        self.session = TypingSession(snippet.id, snippet.code, snippet.language)
        
        self.template = snippet.code
        self.mistakes = {} # Position -> Wrong Char
        self.auto_pairs = {} # Opener Pos -> Closer Pos
        
        # Initialize buffer with the full code using a Document to avoid ReadOnly errors
        self.buffer = Buffer(
            document=Document(text=snippet.code, cursor_position=0),
            read_only=True,
            multiline=True
        )
        
        self.kb = KeyBindings()
        self.setup_key_bindings()
        
        # Explicitly initialize the lexer
        try:
            lexer = PygmentsLexer(get_lexer_by_name(snippet.language).__class__)
        except ClassNotFound:
            from pygments.lexers.python import PythonLexer
            lexer = PygmentsLexer(PythonLexer)

        # UI Components
        self.typing_window = Window(
            content=BufferControl(
                buffer=self.buffer,
                lexer=lexer,
                input_processors=[TypingStateProcessor(self.mistakes, set(self.auto_pairs.values()))],
                include_default_input_processors=False # We handle cursor visually
            ),
            left_margins=[NumberedMargin()],
            wrap_lines=False,
            allow_scroll_beyond_bottom=True,
        )
        
        self.header = Window(
            content=FormattedTextControl(f" Language: {snippet.language} | Snippet: {snippet.title} "),
            height=1,
            style="reverse"
        )
        
        self.footer = Window(
            content=FormattedTextControl(" [Ctrl+C] Exit | [F12] Boss Key "),
            height=1,
            style="reverse"
        )
        
        # Main layout with a consistent background style
        self.layout = Layout(HSplit([
            self.header,
            Window(height=1, style="bg:#1e1e1e"), # Padding
            self.typing_window,
            Window(style="bg:#1e1e1e"), # Fill remaining space
            self.footer
        ], style="bg:#1e1e1e"))
        
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=Style.from_dict(get_typing_style()),
            full_screen=True
        )
        
        self.boss_mode = False

    def setup_key_bindings(self):
        @self.kb.add("c-c")
        def _(event):
            event.app.exit()

        @self.kb.add("f12")
        def _(event):
            self.toggle_boss_mode()

        @self.kb.add("backspace")
        def _(event):
            if self.buffer.cursor_position > 0:
                self.buffer.cursor_position -= 1
                pos = self.buffer.cursor_position
                if pos in self.mistakes:
                    del self.mistakes[pos]
                
                # IDE Mode: If we backspace an opener, also un-auto-complete its closer
                if self.mode == "ide" and pos in self.auto_pairs:
                    del self.auto_pairs[pos]
                    self.update_ui_processors()
                
        @self.kb.add("enter")
        def _(event):
            self.handle_char("\n")

        @self.kb.add("tab")
        def _(event):
            # Intelligent Tab: handle indentation and jumping out of brackets
            pos = self.buffer.cursor_position
            if pos < len(self.template):
                # 1. Skip indentation
                if self.template[pos] in " \t":
                    if self.mode == "ide":
                        while self.buffer.cursor_position < len(self.template) and self.template[self.buffer.cursor_position] in " \t":
                            self.handle_char(self.template[self.buffer.cursor_position])
                    else:
                        # Standard mode: skip up to 4 spaces or 1 tab
                        target = self.template[pos:pos+4]
                        if target == "    ": 
                            for _ in range(4): self.handle_char(" ")
                        elif self.template[pos] == "\t":
                            self.handle_char("\t")
                        elif self.template[pos] == " ":
                            self.handle_char(" ")
                # 2. IDE Mode: Skip auto-completed closers
                elif self.mode == "ide" and pos in self.auto_pairs.values():
                    while self.buffer.cursor_position < len(self.template) and self.buffer.cursor_position in self.auto_pairs.values():
                        self.buffer.cursor_position += 1

        @self.kb.add("<any>")
        def _(event):
            for char in event.data:
                self.handle_char(char)

    def handle_char(self, char: str):
        if not self.session.start_time:
            self.session.start()

        is_sql = self.snippet.language.lower() == "sql"
        
        # IDE Mode: Flexible Whitespace & Assists
        if self.mode == "ide":
            # 1. Flexible Whitespace: If user types a space where there isn't one, just ignore it
            # This handles (a,b) -> (a, b) and a+b -> a + b
            if char in " \t" and self.buffer.cursor_position < len(self.template):
                target_char = self.template[self.buffer.cursor_position]
                if target_char not in " \t":
                    return # Just ignore the extra space
            
            # 2. Smart Skip / Flexible Whitespace: 
            # If we are at whitespace or auto-completed closers, and user types something LATER on the line
            # This handles (a, b) -> (a,b) and a + b -> a+b
            while (self.buffer.cursor_position < len(self.template) and 
                   (self.buffer.cursor_position in self.auto_pairs.values() or 
                    self.template[self.buffer.cursor_position] in " \t")):
                
                # If the character matches what we have here, don't skip
                target_here = self.template[self.buffer.cursor_position]
                match_here = (char == target_here)
                if not match_here and is_sql and char.lower() == target_here.lower():
                    match_here = True
                
                if match_here:
                    break
                
                # Check if 'char' matches something further ahead (on the same line)
                # This allows skipping through multiple brackets if you type the character AFTER them.
                found_match_ahead = False
                for i in range(self.buffer.cursor_position + 1, len(self.template)):
                    if self.template[i] == "\n": break
                    
                    target_ahead = self.template[i]
                    match_ahead = (target_ahead == char)
                    if not match_ahead and is_sql and target_ahead.lower() == char.lower():
                        match_ahead = True
                        
                    if match_ahead:
                        # Skip everything up to this character
                        self.buffer.cursor_position = i
                        found_match_ahead = True
                        break
                    # We can only skip if the characters we pass are auto-completed closers or whitespace
                    if not (i in self.auto_pairs.values() or self.template[i] in " \t"):
                        break
                
                if not found_match_ahead:
                    # Special case for Enter: if we press Enter and there's a newline ahead (only closers/spaces between)
                    if char == "\n":
                        for i in range(self.buffer.cursor_position, len(self.template)):
                            if self.template[i] == "\n":
                                self.buffer.cursor_position = i
                                found_match_ahead = True
                                break
                            if not (i in self.auto_pairs.values() or self.template[i] in " \t"):
                                break
                
                if not found_match_ahead:
                    break

        pos = self.buffer.cursor_position
        if pos >= len(self.template):
            return

        target_char = self.template[pos]
        
        is_correct = (char == target_char)
        
        # IDE Mode Improvement: Optional capitalization for SQL
        if not is_correct and self.mode == "ide" and is_sql:
            if char.lower() == target_char.lower():
                is_correct = True

        if is_correct:
            # Correct!
            pass
        else:
            # Mistake!
            self.mistakes[pos] = char
            self.session.errors += 1
        
        self.buffer.cursor_position += 1
        
        # IDE Mode Assists
        if self.mode == "ide":
            # 1. Indentation Assist: If we just typed a newline, jump past leading spaces
            if char == "\n":
                new_pos = self.buffer.cursor_position
                while new_pos < len(self.template) and self.template[new_pos] in " \t":
                    new_pos += 1
                self.buffer.cursor_position = new_pos
            
            # 2. Smart Auto-Pairing
            elif char in "([{<'\"":
                opener_pos = pos
                closer_pos = self.find_matching_closer(opener_pos, char)
                if closer_pos != -1:
                    self.auto_pairs[opener_pos] = closer_pos
                    self.update_ui_processors()
        
        # Check if done
        if self.buffer.cursor_position >= len(self.template):
            self.session.end()
            self.app.exit(result=self.session.get_metrics())

    def find_matching_closer(self, opener_pos: int, opener_char: str) -> int:
        pairs = {"(": ")", "[": "]", "{": "}", "<": ">", "'": "'", "\"": "\""}
        closer_char = pairs.get(opener_char)
        if not closer_char: return -1
        
        if opener_char in "'\"":
            # For quotes, just find the next one on the same line
            for i in range(opener_pos + 1, len(self.template)):
                if self.template[i] == "\n": break
                if self.template[i] == closer_char:
                    # Check if escaped
                    if i > 0 and self.template[i-1] == "\\": continue
                    return i
            return -1
        else:
            # For brackets, use a simple stack-based search
            stack = 1
            for i in range(opener_pos + 1, len(self.template)):
                if self.template[i] == opener_char:
                    stack += 1
                elif self.template[i] == closer_char:
                    stack -= 1
                    if stack == 0:
                        return i
            return -1

    def update_ui_processors(self):
        # Update the processor with new auto-pair values
        if hasattr(self, 'typing_window'):
            control = self.typing_window.content
            if isinstance(control, BufferControl):
                for p in control.input_processors:
                    if isinstance(p, TypingStateProcessor):
                        p.auto_completed = set(self.auto_pairs.values())
                        break

    def toggle_boss_mode(self):
        self.boss_mode = not self.boss_mode
        if self.boss_mode:
            self.header.content = FormattedTextControl(" [build] Building project... ")
            self.typing_window.content = FormattedTextControl("Compiling components...\nSuccess.")
        else:
            self.header.content = FormattedTextControl(f" Language: {self.snippet.language} | Snippet: {self.snippet.title} ")
            try:
                lexer = PygmentsLexer(get_lexer_by_name(self.snippet.language).__class__)
            except ClassNotFound:
                from pygments.lexers.python import PythonLexer
                lexer = PygmentsLexer(PythonLexer)
                
            self.typing_window.content = BufferControl(
                buffer=self.buffer,
                lexer=lexer,
                input_processors=[TypingStateProcessor(self.mistakes, set(self.auto_pairs.values()))],
                include_default_input_processors=False
            )

    def run(self):
        return self.app.run()
