from textual.widgets import MarkdownViewer, Markdown, ContentSwitcher
from textual.containers import ScrollableContainer
from textual.app import ComposeResult
from code_view import CodeView

class MarkdownView(ContentSwitcher):
    def __init__(self, markdown_content: str):
        super().__init__(
            initial="code_view"
        )
        self.markdown_content = markdown_content
    
    def compose(self) -> ComposeResult:
        yield CodeView(
            self.markdown_content,
            language="markdown",
            show_line_numbers=True,
            id="code_view"
        )
        yield MarkdownViewer(
            markdown=self.markdown_content,
            id="markdown"
        )
    
    def update_content(self, new_content: str) -> None:
        """Update the markdown content in all views"""
        self.markdown_content = new_content
        
        # Update the MarkdownViewer - this is the key fix!
        markdown_viewer = self.query_one("#markdown", MarkdownViewer)
        markdown_viewer.document.update(new_content)
        
        # Refresh the markdown viewer to show the updated content
        markdown_viewer.refresh()