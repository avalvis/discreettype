from prompt_toolkit.application import Application
from prompt_toolkit.key_binding import KeyBindings
from prompt_toolkit.layout.containers import Window, HSplit, VSplit
from prompt_toolkit.layout.controls import FormattedTextControl
from prompt_toolkit.layout.layout import Layout
from prompt_toolkit.styles import Style
from typing import List, Any, Optional

class InteractiveSelector:
    """
    A professional, keyboard-navigable selection menu.
    """
    def __init__(self, title: str, items: List[Any], labels: Optional[List[str]] = None):
        self.title = title
        self.items = items
        self.labels = labels or [str(i) for i in items]
        self.index = 0
        
        self.kb = KeyBindings()
        self.setup_key_bindings()
        
        self.style = Style.from_dict({
            "title": "bold #569cd6",
            "item": "#cccccc",
            "selected": "bold #ffffff bg:#333333",
            "instruction": "italic #6a9955",
        })
        
        self.result = None

    def setup_key_bindings(self):
        @self.kb.add("up")
        def _(event):
            self.index = (self.index - 1) % len(self.items)

        @self.kb.add("down")
        def _(event):
            self.index = (self.index + 1) % len(self.items)

        @self.kb.add("enter")
        def _(event):
            self.result = self.items[self.index]
            event.app.exit(result=self.result)

        @self.kb.add("escape")
        @self.kb.add("c-c")
        def _(event):
            event.app.exit(result=None)

    def get_tokens(self):
        tokens = [("class:title", f" {self.title}\n\n")]
        
        for i, label in enumerate(self.labels):
            if i == self.index:
                tokens.append(("class:selected", f" > {label} \n"))
            else:
                tokens.append(("class:item", f"   {label} \n"))
        
        tokens.append(("\nclass:instruction", " (Use ↑/↓ to navigate, Enter to select, Esc to go back)"))
        return tokens

    def run(self):
        content = FormattedTextControl(self.get_tokens)
        layout = Layout(HSplit([
            Window(height=1, style="class:item"), # Spacer
            Window(content=content, left_margins=[], right_margins=[])
        ]))
        
        app = Application(
            layout=layout,
            key_bindings=self.kb,
            style=self.style,
            full_screen=False # Don't take over the whole screen for simple menus
        )
        
        return app.run()

def select_item(title: str, items: List[Any], labels: Optional[List[str]] = None) -> Any:
    """Utility function to run the selector."""
    selector = InteractiveSelector(title, items, labels)
    return selector.run()
