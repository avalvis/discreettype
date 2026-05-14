from prompt_toolkit.application import Application
from prompt_toolkit.buffer import Buffer
from prompt_toolkit.layout.containers import Window, HSplit
from prompt_toolkit.layout.controls import BufferControl, FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.layout.margins import NumberedMargin
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.keys import Keys
from prompt_toolkit.styles import Style
from prompt_toolkit.lexers import PygmentsLexer
from pygments.lexers import get_lexer_by_name
from pygments.util import ClassNotFound
from prompt_toolkit.document import Document

from ..core.session import TypingSession
from .typing import TypingStateProcessor, get_typing_style


# prompt_toolkit registers several default emacs bindings that interfere with
# a read-only buffer used for typing practice. We must explicitly reclaim them.
#
# Read-only emacs "pager" bindings (see prompt_toolkit/key_binding/bindings/
# emacs.py): when a buffer is read_only=True, the keys below trigger search
# navigation / incremental search instead of inserting the character. That
# makes them feel like "cheat mode" - e.g. pressing 'n' jumps the cursor over
# arbitrary characters because emacs interprets it as "jump to next match".
PAGER_KEYS_TO_RECLAIM = ("n", "N", "?", "/")

# Emacs cursor-movement bindings that operate on any buffer regardless of
# read-only status. Left unchecked they would let the user accidentally
# desynchronize the typing cursor from the typed text.
CTRL_NAV_KEYS_TO_DISABLE = (
    "c-a",
    "c-b",
    "c-e",
    "c-f",
    "c-left",
    "c-right",
    "c-home",
    "c-end",
    "c-up",
    "c-down",
)


def find_optional_whitespace_skip_target(template: str, start_pos: int, typed_char: str):
    """Return the next matching index after contiguous spaces/tabs, if any."""
    if start_pos >= len(template) or typed_char in " \t\n":
        return None
    if template[start_pos] not in " \t":
        return None

    temp_pos = start_pos
    while temp_pos < len(template) and template[temp_pos] in " \t":
        temp_pos += 1

    if temp_pos < len(template) and template[temp_pos] == typed_char:
        return temp_pos
    return None


def find_comment_skip_span(template: str, cursor_pos: int, language: str):
    """Return (from_pos, to_pos) for a comment skip on the current line, if valid."""
    if cursor_pos < 0 or cursor_pos >= len(template):
        return None

    line_start = template.rfind("\n", 0, cursor_pos) + 1
    line_end = template.find("\n", cursor_pos)
    if line_end == -1:
        line_end = len(template)

    line = template[line_start:line_end]
    if not line:
        return None

    lang = language.lower()
    if lang in {"python", "bash"}:
        markers = ["#"]
    elif lang == "sql":
        markers = ["--"]
    else:
        markers = ["//", "#"]

    marker_rel_pos = -1
    marker_len = 0
    for marker in markers:
        pos = line.find(marker)
        if pos != -1 and (marker_rel_pos == -1 or pos < marker_rel_pos):
            marker_rel_pos = pos
            marker_len = len(marker)

    if marker_rel_pos == -1:
        return None

    comment_start = line_start + marker_rel_pos
    comment_end = line_end
    if comment_end <= comment_start:
        return None

    if cursor_pos < comment_start:
        between = template[cursor_pos:comment_start]
        if not all(ch in " \t" for ch in between):
            return None
        return (cursor_pos, comment_end)

    if comment_start <= cursor_pos < comment_end:
        return (cursor_pos, comment_end)

    # cursor after comment end (or exactly line end)
    if cursor_pos == comment_end and comment_start + marker_len < comment_end:
        return None

    return None


def compute_post_char_skip_cursor(
    template: str,
    cursor_pos: int,
    typed_char: str,
    auto_completed_indices: set[int],
) -> int:
    """Compute safe post-typing cursor skips for IDE assist behavior."""
    if cursor_pos >= len(template):
        return cursor_pos

    # Allow repeated whitespace presses to glide through contiguous indentation.
    if typed_char in " \t":
        while cursor_pos < len(template) and template[cursor_pos] == typed_char:
            cursor_pos += 1
        return cursor_pos

    # Allow typed closer/quote to jump over auto-completed closers only.
    if typed_char in ")]}>\"'":
        while (
            cursor_pos < len(template)
            and cursor_pos in auto_completed_indices
            and template[cursor_pos] == typed_char
        ):
            cursor_pos += 1
        return cursor_pos

    return cursor_pos


def find_auto_completed_skip_target(cursor_pos: int, text_length: int, auto_completed_indices: set[int]):
    """Return the cursor target when moving right over auto-completed indices."""
    if cursor_pos < 0 or cursor_pos >= text_length or cursor_pos not in auto_completed_indices:
        return None

    target = cursor_pos
    while target < text_length and target in auto_completed_indices:
        target += 1
    return target


class TypingApp:
    def __init__(self, snippet, mode: str = "standard", allow_refresh: bool = False):
        self.snippet = snippet
        self.mode = mode
        self.allow_refresh = allow_refresh
        self.session = TypingSession(snippet.id, snippet.code, snippet.language)
        
        self.template = snippet.code
        self.mistakes = {} # Position -> Wrong Char
        self.auto_pairs = {} # Opener Pos -> Closer Pos
        self.skipped_indices = set()
        self.comment_skip_history = []
        
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
                input_processors=[TypingStateProcessor(self.mistakes, self.get_auto_completed_indices())],
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
        
        footer_text = " [Ctrl+C] Exit | [F12] Boss Key "
        if self.allow_refresh:
            footer_text = " [F5] Next Snippet | [Ctrl+C] Exit | [F12] Boss Key "
        self.footer = Window(
            content=FormattedTextControl(footer_text),
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

    def get_auto_completed_indices(self):
        """Returns a set of all indices that were automatically handled."""
        return set(self.auto_pairs.values()) | self.skipped_indices

    def setup_key_bindings(self):
        @self.kb.add("c-c")
        def _(event):
            event.app.exit()

        @self.kb.add("f12")
        def _(event):
            self.toggle_boss_mode()

        if self.allow_refresh:
            @self.kb.add("f5")
            def _(event):
                event.app.exit(result="refresh_snippet")

        @self.kb.add("backspace")
        def _(event):
            if self.boss_mode:
                return
            if self.buffer.cursor_position > 0:
                self.buffer.cursor_position -= 1
                pos = self.buffer.cursor_position
                if pos in self.mistakes:
                    del self.mistakes[pos]
                
                # IDE Mode: If we backspace an opener, also un-auto-complete its closer
                if self.mode == "ide" and pos in self.auto_pairs:
                    del self.auto_pairs[pos]
                    self.update_ui_processors()

                # IDE Mode: If we backspace over skipped whitespace, restore it.
                if self.mode == "ide" and pos in self.skipped_indices:
                    self.skipped_indices.remove(pos)
                    self.update_ui_processors()
                
        @self.kb.add("enter")
        def _(event):
            self.handle_char("\n")

        # Disable most navigation keys to prevent unintended behavior
        @self.kb.add("up")
        @self.kb.add("down")
        @self.kb.add("pageup")
        @self.kb.add("pagedown")
        @self.kb.add("home")
        @self.kb.add("end")
        def _(event):
            pass

        @self.kb.add("right")
        def _(event):
            if self.boss_mode or self.mode != "ide":
                return

            auto_target = find_auto_completed_skip_target(
                self.buffer.cursor_position,
                len(self.template),
                self.get_auto_completed_indices(),
            )
            if auto_target is not None:
                self.buffer.cursor_position = auto_target
                return

            span = find_comment_skip_span(self.template, self.buffer.cursor_position, self.snippet.language)
            if not span:
                return
            from_pos, to_pos = span
            newly_skipped = set()
            for i in range(from_pos, to_pos):
                if i not in self.skipped_indices:
                    newly_skipped.add(i)
                self.skipped_indices.add(i)
            self.comment_skip_history.append((from_pos, to_pos, newly_skipped))
            self.buffer.cursor_position = to_pos
            self.update_ui_processors()

        @self.kb.add("left")
        def _(event):
            if self.boss_mode or self.mode != "ide" or not self.comment_skip_history:
                return
            from_pos, to_pos, newly_skipped = self.comment_skip_history[-1]
            if self.buffer.cursor_position != to_pos:
                return
            self.comment_skip_history.pop()
            for i in newly_skipped:
                self.skipped_indices.discard(i)
            self.buffer.cursor_position = from_pos
            self.update_ui_processors()

        @self.kb.add("tab")
        def _(event):
            if self.boss_mode:
                return
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
                elif self.mode == "ide" and pos in self.get_auto_completed_indices():
                    while (
                        self.buffer.cursor_position < len(self.template)
                        and self.buffer.cursor_position in self.get_auto_completed_indices()
                    ):
                        self.buffer.cursor_position += 1

        # Reclaim emacs read-only pager bindings (n, N, ?, /) so they behave
        # like normal typed characters instead of triggering search jumps.
        # A specific-key binding wins over our <any> fallback in
        # prompt_toolkit's matcher, so we have to register them explicitly.
        for pager_key in PAGER_KEYS_TO_RECLAIM:
            @self.kb.add(pager_key)
            def _(event):
                self.handle_char(event.data)

        # Neutralize emacs cursor-motion bindings that would otherwise allow
        # the user to silently desynchronize from the typing flow.
        for ctrl_key in CTRL_NAV_KEYS_TO_DISABLE:
            @self.kb.add(ctrl_key)
            def _(event):
                pass

        # Disallow paste during a practice session. Without this, the default
        # bracketed-paste handler tries to insert into the read-only buffer
        # and rings the terminal bell.
        @self.kb.add(Keys.BracketedPaste)
        def _(event):
            pass

        @self.kb.add("<any>")
        def _(event):
            for char in event.data:
                if not char.isprintable():
                    continue
                self.handle_char(char)

    def handle_char(self, char: str):
        # Ignore input while the boss-key disguise is showing; otherwise the
        # session keeps recording keystrokes against an invisible cursor.
        if self.boss_mode:
            return
        if not self.session.start_time:
            self.session.start()

        is_sql = self.snippet.language.lower() == "sql"
        
        # IDE Mode: Flexible Whitespace (Extra user space)
        if self.mode == "ide":
            if char in " \t" and self.buffer.cursor_position < len(self.template):
                if self.template[self.buffer.cursor_position] not in " \t":
                    return 

        pos = self.buffer.cursor_position
        if pos >= len(self.template):
            return

        target_char = self.template[pos]
        is_correct = (char == target_char)
        if not is_correct and self.mode == "ide" and is_sql:
            if char.lower() == target_char.lower():
                is_correct = True

        # IDE Mode: Allow skipping indentation-like whitespace naturally.
        if self.mode == "ide" and not is_correct:
            skip_target = find_optional_whitespace_skip_target(self.template, pos, char)
            if skip_target is not None:
                for i in range(pos, skip_target):
                    self.skipped_indices.add(i)
                self.buffer.cursor_position = skip_target
                pos = skip_target
                target_char = self.template[pos]
                is_correct = True
                self.update_ui_processors()

        if is_correct:
            # Correct!
            if pos in self.session.miskeyed_indices:
                self.session.corrected_errors += 1
                self.session.miskeyed_indices.remove(pos)
            if pos in self.mistakes:
                del self.mistakes[pos]
            # Advance cursor ONE step only on accepted input.
            self.buffer.cursor_position += 1
        else:
            # Mistake!
            if pos not in self.session.miskeyed_indices:
                self.session.errors += 1
                self.session.miskeyed_indices.add(pos)
            self.mistakes[pos] = char
        
        # IDE Mode: Assists (AFTER registration)
        if self.mode == "ide":
            # 1. Newline Indentation Assist
            if char == "\n":
                new_pos = self.buffer.cursor_position
                while new_pos < len(self.template) and self.template[new_pos] in " \t":
                    self.skipped_indices.add(new_pos)
                    new_pos += 1
                self.buffer.cursor_position = new_pos
                self.update_ui_processors()
            
            # 2. Smart Auto-Pairing
            elif char in "([{<'\"" and is_correct:
                opener_pos = pos
                closer_pos = self.find_matching_closer(opener_pos, char)
                if closer_pos != -1:
                    self.auto_pairs[opener_pos] = closer_pos
                    self.update_ui_processors()

            # 3. Safe post-char skips for whitespace/auto-completed closers
            self.buffer.cursor_position = compute_post_char_skip_cursor(
                self.template,
                self.buffer.cursor_position,
                char,
                self.get_auto_completed_indices(),
            )
        
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
        # Update the processor with new auto-pair/skipped values
        if hasattr(self, 'typing_window'):
            control = self.typing_window.content
            if isinstance(control, BufferControl):
                for p in control.input_processors:
                    if isinstance(p, TypingStateProcessor):
                        p.auto_completed = self.get_auto_completed_indices()
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
                input_processors=[TypingStateProcessor(self.mistakes, self.get_auto_completed_indices())],
                include_default_input_processors=False
            )

    def run(self):
        return self.app.run()
