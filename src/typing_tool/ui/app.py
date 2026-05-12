from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import Window, HSplit, VSplit, WindowAlign, ConditionalContainer
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.styles import Style
from prompt_toolkit.filters import Condition

from ..core.session import TypingSession
from .typing import TypingOverlayProcessor, get_typing_style

class TypingApp:
    def __init__(self, snippet):
        self.snippet = snippet
        self.session = TypingSession(snippet.id, snippet.code, snippet.language)
        
        # Key bindings
        self.kb = KeyBindings()
        self.setup_key_bindings()
        
        # Buffer for user input - EXPLICITLY MULTILINE
        self.buffer = Buffer(
            on_text_changed=self.on_text_changed,
            multiline=True
        )
        
        # UI Components
        self.typing_window = Window(
            content=BufferControl(
                buffer=self.buffer,
                input_processors=[TypingOverlayProcessor(snippet.code, snippet.language)]
            ),
            left_margins=[NumberedMargin()], # IDE-like line numbers
            wrap_lines=False, # Code should usually not wrap if we want IDE feel
            allow_scroll_beyond_bottom=True
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
        
        self.layout = Layout(HSplit([
            self.header,
            Window(height=1), # Spacer
            self.typing_window,
            Window(), # Spacer
            self.footer
        ]))
        
        self.style = Style.from_dict(get_typing_style())
        
        self.app = Application(
            layout=self.layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=True,
            mouse_support=False
        )
        
        self.boss_mode = False

    def setup_key_bindings(self):
        @self.kb.add("c-c")
        def _(event):
            event.app.exit()

        @self.kb.add("f12")
        def _(event):
            self.toggle_boss_mode()

    def toggle_boss_mode(self):
        self.boss_mode = not self.boss_mode
        if self.boss_mode:
            # Switch to fake screen
            self.header.content = FormattedTextControl(" [build] Building typing-tool v0.1.0... ")
            self.typing_window.content = FormattedTextControl(
                "Scanning dependencies...\n"
                "Done.\n"
                "Compiling src/typing_tool/core/session.py...\n"
                "Compiling src/typing_tool/ui/typing.py...\n"
                "Linking objects...\n"
                "Build successful. 0 errors, 2 warnings."
            )
        else:
            # Switch back
            self.header.content = FormattedTextControl(f" Language: {self.snippet.language} | Snippet: {self.snippet.title} ")
            self.typing_window.content = BufferControl(
                buffer=self.buffer,
                input_processors=[TypingOverlayProcessor(self.snippet.code, self.snippet.language)]
            )

    def on_text_changed(self, buffer):
        self.session.update_progress(buffer.text)
        
        # Basic progression check
        if len(buffer.text) >= len(self.snippet.code):
            self.session.end()
            self.app.exit(result=self.session.get_metrics())

    def run(self):
        return self.app.run()
