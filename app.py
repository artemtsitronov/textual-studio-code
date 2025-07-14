from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Static, Footer
from textual.containers import Horizontal, Vertical
from textual.reactive import var
from textual.binding import Binding
from textual.message import Message
from pathlib import Path
import uuid
from code_view import CodeView
from directory_tree import DirectoryTree

class App(App):
    CSS_PATH = [
        "styles/tabbed_content.tcss",
        "styles/directory_tree.tcss",
        "styles/screen.tcss",
    ]
    
    BINDINGS = [
        Binding("ctrl+w", "toggle_compact", "Toggle Compact Mode", show=False),
        Binding("ctrl+b", "toggle_directory_tree", "Toggle Directory Tree", show=False),
        Binding("ctrl+r", "remove_active_tab", "Remove Active Tab", show=False),
    ]
    
    compact: var[bool] = var(False)
    
    def __init__(self, directory_path: str = "/home/evgenii"):
        super().__init__()
        self.directory_path = directory_path

    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield DirectoryTree(self.directory_path)
                
            with TabbedContent(id="tabbed_content"):
                with TabPane("Welcome", id="welcome_tab"):
                    yield Static("Click on a file in the directory tree to open it here.\n\nKeyboard shortcuts:\n- Ctrl+R: Close current tab\n- Ctrl+W: Toggle compact mode")
        
        yield Static("Ln ?, Col ?", id="footer")
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from directory tree"""
        file_path = Path(event.path)
        self.open_file_in_new_tab(file_path)
    
    def generate_valid_tab_id(self, filename: str) -> str:
        """Generate a valid CSS ID for tab from filename with UUID"""
        import re
        
        # Replace dots, spaces, and other special chars with underscores
        safe_name = re.sub(r'[^a-zA-Z0-9_-]', '_', filename)
        
        # Ensure it starts with a letter
        if safe_name and safe_name[0].isdigit():
            safe_name = f"file_{safe_name}"
        elif not safe_name or not safe_name[0].isalpha():
            safe_name = f"file_{safe_name}"
        
        # Add UUID to ensure uniqueness
        unique_id = str(uuid.uuid4()).replace('-', '')[:8]
        return f"tab_{safe_name}_{unique_id}"

    def open_file_in_new_tab(self, file_path: Path) -> None:
        """Open a file in a new tab"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()

            language = self.get_language_from_extension(file_path.suffix)
            tabbed_content = self.query_one("#tabbed_content", TabbedContent)
            tab_id = self.generate_valid_tab_id(file_path.name)

            new_pane = TabPane(file_path.name, id=tab_id)
            code_view = CodeView(
                content,
                language=language,
                show_line_numbers=True
            )
            
            new_pane.compose_add_child(code_view)
            tabbed_content.add_pane(new_pane)
            tabbed_content.active = tab_id
                
        except UnicodeDecodeError:
            self.notify("Cannot open binary file", severity="error")
        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")
    
    def get_language_from_extension(self, extension: str) -> str:
        """Get language identifier from file extension"""
        language_map = {
            '.py': 'python',
            '.js': 'javascript',
            '.ts': 'typescript',
            '.html': 'html',
            '.css': 'css',
            '.json': 'json',
            '.md': 'markdown',
            '.yaml': 'yaml',
            '.yml': 'yaml',
            '.xml': 'xml',
            '.sql': 'sql',
            '.sh': 'bash',
            '.rs': 'rust',
            '.go': 'go',
            '.java': 'java',
            '.cpp': 'cpp',
            '.c': 'c',
            '.h': 'c',
            '.hpp': 'cpp',
        }
        return language_map.get(extension.lower(), None)
    
    def action_toggle_compact(self) -> None:
        self.compact = not self.compact

        directory_tree = self.query_one(DirectoryTree)
        directory_tree.toggle_class("compact")
    
    def action_toggle_directory_tree(self) -> None:
        directory_tree = self.query_one(DirectoryTree)

        if self.compact:
            directory_tree.toggle_class("hidden")

    
    def action_remove_active_tab(self) -> None:
        tabbed_content = self.query_one("#tabbed_content", TabbedContent)
        active_pane = tabbed_content.active_pane

        if active_pane is not None and tabbed_content.tab_count > 1:
            tabbed_content.remove_pane(active_pane.id)

def run_app(directory_path: str = "/home/evgenii"):
    app = App(directory_path)
    app.run()