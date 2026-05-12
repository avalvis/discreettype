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
    def __init__(self, snippet):
        self.snippet = snippet
        self.session = TypingSession(snippet.id, snippet.code, snippet.language)
        
        self.template = snippet.code
        self.mistakes = {} # Position -> Wrong Char
        
        # Buffer initialized with the TARGET code
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
                input_processors=[TypingStateProcessor(self.mistakes)],
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
                
        @self.kb.add("enter")
        def _(event):
            self.handle_char("\n")

        @self.kb.add("tab")
        def _(event):
            # Intelligent Tab: handle indentation
            pos = self.buffer.cursor_position
            if pos < len(self.template):
                # Check if we are at indentation spaces
                target = self.template[pos:pos+4]
                if target == "    ": 
                    for _ in range(4): self.handle_char(" ")
                elif self.template[pos] == "\t":
                    self.handle_char("\t")
                elif self.template[pos] == " ":
                    # Skip single space or whatever indentation is there
                    self.handle_char(" ")

        @self.kb.add("<any>")
        def _(event):
            for char in event.data:
                self.handle_char(char)

    def handle_char(self, char: str):
        if not self.session.start_time:
            self.session.start()
            
        pos = self.buffer.cursor_position
        if pos >= len(self.template):
            return

        target_char = self.template[pos]
        
        if char == target_char:
            # Correct!
            pass
        else:
            # Mistake!
            self.mistakes[pos] = char
            self.session.errors += 1
        
        self.buffer.cursor_position += 1
        
        # Check if done
        if self.buffer.cursor_position >= len(self.template):
            self.session.end()
            self.app.exit(result=self.session.get_metrics())

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
                input_processors=[TypingStateProcessor(self.mistakes)],
                include_default_input_processors=False
            )

    def run(self):
        return self.app.run()
