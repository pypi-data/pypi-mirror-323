"""Subtitle response implementation."""
from typing import Optional

from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.titles.abstract_title_response import AbstractTitleResponse


class SubtitlePromptResponse(AbstractTitleResponse):
    """Response for subtitles with small arrow prefix."""

    @classmethod
    def create_subtitle(
        cls,
        text: str,
        color: Optional[TerminalColor] = TerminalColor.BLUE,
        fill_char: Optional[str] = None
    ) -> 'SubtitlePromptResponse':
        return super()._create_title(text=text, color=color, fill_char=fill_char)

    @classmethod
    def get_prefix(cls) -> str:
        return "  ❯"
