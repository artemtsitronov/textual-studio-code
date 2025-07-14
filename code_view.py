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
        self.set_interval(0.1, self.check_cursor)
    
    def check_cursor(self):
        current = self.cursor_location
        if current != self.cursor_pos:
            self.cursor_pos = current

    def watch_cursor_pos(self, new_pos):
        line, col = new_pos

        footer = self.app.query_one("#footer")
        footer.update(f"Ln {line + 1}, Col {col + 1}")

    async def on_key(self, event: events.Key) -> None:
        for character, pair in self.CLOSING_CHARACTERS.items():
            if event.character == character:
                self.insert(pair)
                self.move_cursor_relative(columns=-1)
                event.prevent_default()
                break
