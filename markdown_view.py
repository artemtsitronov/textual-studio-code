from textual.widgets import MarkdownViewer, Markdown, ContentSwitcher
from textual.containers import Vertical
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
		with Vertical(id="markdown"):
			with ContentSwitcher(initial="normal", id="markdown_switcher"):
				yield MarkdownViewer(
					self.markdown_content,
					id="normal"
				)
				yield Markdown(
					self.markdown_content,
					id="compact"
				)