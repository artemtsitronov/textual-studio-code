from textual.app import App, ComposeResult
from textual.widgets import TabbedContent, TabPane, Static, Footer
from textual.containers import Horizontal
from textual.reactive import var
from textual.binding import Binding
from textual.message import Message
from pathlib import Path
import uuid
import asyncio
import json
import shutil
from typing import Dict, Optional
from code_view import CodeView
from directory_tree import DirectoryTree
from markdown_view import MarkdownView

class App(App):
    CSS_PATH = [
        "styles/tabbed_content.tcss",
        "styles/directory_tree.tcss",
        "styles/screen.tcss",
    ]
    
    BINDINGS = [
        Binding("ctrl+w", "toggle_compact", "Toggle Compact Mode"),
        Binding("ctrl+b", "toggle_directory_tree", "Toggle Directory Tree"),
        Binding("ctrl+r", "remove_active_tab", "Remove Active Tab"),
        Binding("ctrl+l", "toggle_markdown_mode", "Toggle Markdown Mode"),
        Binding("ctrl+s", "save", "Save File")
    ]
    
    compact: var[bool] = var(False)
    
    def __init__(self, directory_path: str = "."):
        super().__init__()
        self.directory_path = directory_path
        # Cache for file contents to avoid re-reading
        self._file_cache: Dict[str, str] = {}
        # Cache for opened tabs to avoid duplicates
        self._open_tabs: Dict[str, str] = {}  # file_path -> tab_id
        # Maximum file size to load (10MB)
        self.max_file_size = 10 * 1024 * 1024
        # Load JSON language map
        self.language_map = self.load_language_map()
        # Markdown Mode
        self.markdown_mode = False
        # Welcome Text
        self.welcome = """
Hello everyone!
Welcome to Textul Studio Code!
This is a simple text editor, and I really hope it will become more and more popular.
I really hope you enjoy.

Here are some simple basic bindings:
    - Ctrl + P: Opens the Command Palette where you can
                change themes and view other bindings.
    - Ctrl + R: Removes the active tab.
    - Ctrl + L: Toggles view mode in Markdown.
    - Ctrl + W: Toggles compact mode.
    - Ctrl + B: Toggles directory tree.
    - Ctrl + S: Saves the current file.

Compact mode is perfect for small terminal windows, and it also affects the Markdown's view mode.
It changes it from MarkdownViewer to Markdown(removes the sidebar).

What it now has:
    - File saving functionality!
    - Optimized file loading and caching.
    - Smart content detection for different file types.
    - Markdown support!
    - Themes!
    - And many(or few) others.

I started this project 5 days ago, so, don't come to me asking why it doesn't have this and why it doesn't have that.

Artem Tsitronov. 2025.

        """
    
    def compose(self) -> ComposeResult:
        with Horizontal():
            yield DirectoryTree(self.directory_path)
                
            with TabbedContent(id="tabbed_content"):
                with TabPane("Welcome", id="welcome_tab"):
                    yield Static(self.welcome)
        
        yield Static("Ln ?, Col ?", id="footer")
    
    def on_directory_tree_file_selected(self, event: DirectoryTree.FileSelected) -> None:
        """Handle file selection from directory tree"""
        file_path = Path(event.path)
        
        # Check if file is already open
        file_path_str = str(file_path)
        if file_path_str in self._open_tabs:
            # Switch to existing tab
            tabbed_content = self.query_one("#tabbed_content", TabbedContent)
            tabbed_content.active = self._open_tabs[file_path_str]
            return
        
        # Open file synchronously but with optimizations
        self.open_file_optimized(file_path)
    
    def open_file_optimized(self, file_path: Path) -> None:
        """Open a file in a new tab with optimizations"""
        try:
            # Check file size first
            if file_path.stat().st_size > self.max_file_size:
                self.notify(f"File too large (>{self.max_file_size // (1024*1024)}MB)", severity="warning")
                return
            
            file_path_str = str(file_path)
            
            # Check cache first
            if file_path_str in self._file_cache:
                content = self._file_cache[file_path_str]
            else:
                # Load file content
                content = self.load_file_content_sync(file_path)
                if content is None:
                    return
                
                # Cache the content (limit cache size)
                if len(self._file_cache) > 50:  # Limit cache to 50 files
                    # Remove oldest entry
                    oldest_key = next(iter(self._file_cache))
                    del self._file_cache[oldest_key]
                
                self._file_cache[file_path_str] = content

            # Create tab
            self.create_tab_with_content(file_path, content)
                
        except Exception as e:
            self.notify(f"Error opening file: {e}", severity="error")

    def load_language_map(self) -> Dict[str, str]:
        """Load the language map stored in ./language_map.json"""
        try:
            with open("language_map.json", "r", encoding="utf-8") as f:
                language_map = json.load(f)
                return language_map

        except Exception as e:
            self.notify(f"Error loading language_map.json: {e}", severity="error")
            return {}
    
    def load_file_content_sync(self, file_path: Path) -> Optional[str]:
        """Load file content synchronously with proper error handling"""
        try:
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    return f.read()
            except UnicodeDecodeError:
                # Try with different encodings
                for encoding in ["latin-1", "cp1252", "iso-8859-1"]:
                    try:
                        with open(file_path, "r", encoding=encoding) as f:
                            return f.read()
                    except UnicodeDecodeError:
                        continue
                raise UnicodeDecodeError("Unable to decode file with any encoding")
            
        except UnicodeDecodeError:
            self.notify("Cannot open binary file", severity="error")
            return None
        except Exception as e:
            self.notify(f"Error reading file: {e}", severity="error")
            return None
    
    def create_tab_with_content(self, file_path: Path, content: str) -> None:
        """Create a new tab with the given content"""
        language = self.get_language_from_extension(file_path.suffix)
        tabbed_content = self.query_one("#tabbed_content", TabbedContent)
        tab_id = self.generate_valid_tab_id(file_path.name)

        new_pane = TabPane(file_path.name, id=tab_id)
        
        if language == "markdown":
            child = MarkdownView(content)
        else:
            child = CodeView(
                content,
                language=language,
                show_line_numbers=True
            )
        
        new_pane.compose_add_child(child)
        tabbed_content.add_pane(new_pane)
        tabbed_content.active = tab_id
        
        # Track opened tab
        self._open_tabs[str(file_path)] = tab_id
    
    def generate_valid_tab_id(self, filename: str) -> str:
        """Generate a valid CSS ID for tab from filename with UUID"""
        import re
        
        # Replace dots, spaces, and other special chars with underscores
        safe_name = re.sub(r"[^a-zA-Z0-9_-]", "_", filename)
        
        # Ensure it starts with a letter
        if safe_name and safe_name[0].isdigit():
            safe_name = f"file_{safe_name}"
        elif not safe_name or not safe_name[0].isalpha():
            safe_name = f"file_{safe_name}"
        
        # Add UUID to ensure uniqueness
        unique_id = str(uuid.uuid4()).replace("-", "")[:8]
        return f"tab_{safe_name}_{unique_id}"

    def get_language_from_extension(self, extension: str) -> str:
        """Get language identifier from file extension"""
        return self.language_map.get(extension.lower(), None)

    def action_save(self) -> None:
        """Save the content of the active tab to its corresponding file"""
        tabbed_content = self.query_one("#tabbed_content", TabbedContent)
        active_pane = tabbed_content.active_pane
        
        if active_pane is None:
            self.notify("No active tab to save", severity="warning")
            return
        
        # Skip saving the welcome tab
        if active_pane.id == "welcome_tab":
            self.notify("Cannot save welcome tab", severity="info")
            return
        
        # Find the file path for this tab
        file_path = None
        tab_id = active_pane.id
        
        for tracked_file_path, tracked_tab_id in self._open_tabs.items():
            if tracked_tab_id == tab_id:
                file_path = tracked_file_path
                break
        
        if file_path is None:
            self.notify("Cannot determine file path for current tab", severity="error")
            return
        
        try:
            # Check if this is a MarkdownView or CodeView
            content_widget = None
            is_markdown_view = False
            
            try:
                # Try to get MarkdownView first
                content_widget = active_pane.query_one(MarkdownView)
                is_markdown_view = True
            except:
                # If not found, try CodeView
                try:
                    content_widget = active_pane.query_one(CodeView)
                    is_markdown_view = False
                except Exception as e:
                    self.notify(f"Could not find content widget: {e}", severity="error")
                    return
            
            # Get content based on widget type
            if is_markdown_view:
                # For MarkdownView, get content from the CodeView inside it
                code_view = content_widget.query_one("#code_view", CodeView)
                content = code_view.text
            else:
                # For regular CodeView
                content = content_widget.text
            
            # Write to file with UTF-8 encoding
            file_path_obj = Path(file_path)
            with open(file_path_obj, "w", encoding="utf-8") as f:
                f.write(content)
            
            # Update cache with new content
            self._file_cache[file_path] = content
            
            # If this is a MarkdownView, update all its internal views
            if is_markdown_view:
                content_widget.update_content(content)
            
            # Success notification
            self.notify(f"Saved: {file_path_obj.name}", severity="info")
            
        except Exception as e:
            self.notify(f"Error saving file: {e}", severity="error")
    
    def action_toggle_compact(self) -> None:
        self.compact = not self.compact

        directory_tree = self.query_one(DirectoryTree)
        directory_tree.toggle_class("compact")
        if not self.compact:
            directory_tree.remove_class("hidden")

        if self.query("#markdown"):
            markdown_switcher = self.query_one("#markdown")
            markdown_switcher.show_table_of_contents = not markdown_switcher.show_table_of_contents
    
    def action_toggle_directory_tree(self) -> None:
        directory_tree = self.query_one(DirectoryTree)

        if self.compact:
            directory_tree.toggle_class("hidden")

    
    def action_remove_active_tab(self) -> None:
        tabbed_content = self.query_one("#tabbed_content", TabbedContent)
        active_pane = tabbed_content.active_pane

        if active_pane is not None and tabbed_content.tab_count > 1:
            # Remove from open tabs tracking
            tab_id = active_pane.id
            file_path_to_remove = None
            for file_path, tracked_tab_id in self._open_tabs.items():
                if tracked_tab_id == tab_id:
                    file_path_to_remove = file_path
                    break
            
            if file_path_to_remove:
                del self._open_tabs[file_path_to_remove]
                # Optionally remove from cache to free memory
                if file_path_to_remove in self._file_cache:
                    del self._file_cache[file_path_to_remove]
            
            tabbed_content.remove_pane(active_pane.id)

    def action_toggle_markdown_mode(self) -> None:
        self.markdown_mode = not self.markdown_mode

        markdown_view = self.query_one(MarkdownView)
        markdown_view.current = "markdown" if self.markdown_mode else "code_view"

    def setup_auto_save(self, interval_seconds: int = 5) -> None:
        """Setup auto-save functionality (optional enhancement)"""
        async def auto_save_task():
            while True:
                await asyncio.sleep(interval_seconds)
                try:
                    tabbed_content = self.query_one("#tabbed_content", TabbedContent)
                    if tabbed_content.active_pane and tabbed_content.active_pane.id != "welcome_tab":
                        self.action_save()
                except Exception:
                    pass  # Silently ignore auto-save errors
        
        # Uncomment the line below in __init__ if you want auto-save:
        # asyncio.create_task(auto_save_task())

def run_app(directory_path: str = "/home/evgenii"):
    app = App(directory_path)
    app.run()