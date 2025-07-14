from textual.widgets import TextArea
from textual.reactive import reactive
from textual import events


class CodeView(TextArea):
    cursor_pos = reactive((0, 0))

    CLOSING_CHARACTERS = {
        "\"": "\"\"",
        "'": "''",
        "(": "()",
        "[": "[]",
        "{": "{}",
        "<": "<>"
    }

    def on_mount(self) -> None:
        # Use a less frequent interval for better performance
        self.set_interval(0.2, self.check_cursor)
    
    def check_cursor(self):
        current = self.cursor_location
        if current != self.cursor_pos:
            self.cursor_pos = current

    def watch_cursor_pos(self, new_pos):
        """Update footer with cursor position"""
        line, col = new_pos
        try:
            footer = self.app.query_one("#footer")
            footer.update(f"Ln {line + 1}, Col {col + 1}")
        except Exception:
            # Silently handle any errors
            pass

    async def on_key(self, event: events.Key) -> None:
        # Only process closing characters for better performance
        if event.character in self.CLOSING_CHARACTERS:
            pair = self.CLOSING_CHARACTERS[event.character]
            self.insert(pair)
            self.move_cursor_relative(columns=-1)
            event.prevent_default()