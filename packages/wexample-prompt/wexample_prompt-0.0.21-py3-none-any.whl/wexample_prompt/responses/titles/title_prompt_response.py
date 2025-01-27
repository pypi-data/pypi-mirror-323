"""Title response implementation."""
from typing import Optional

from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.titles.abstract_title_response import AbstractTitleResponse


class TitlePromptResponse(AbstractTitleResponse):
    """Response for main titles with arrow prefix."""

    @classmethod
    def create_title(
        cls,
        text: str,
        color: Optional[TerminalColor] = TerminalColor.CYAN,
        fill_char: Optional[str] = None
    ) -> 'TitlePromptResponse':
        return super()._create_title(text=text, color=color, fill_char=fill_char)
    
    @classmethod
    def get_prefix(cls) -> str:
        return "❯"
