"""Base class for title responses."""
from abc import abstractmethod
import shutil
from typing import Optional

from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.base_prompt_response import BasePromptResponse


class AbstractTitleResponse(BasePromptResponse):
    """Abstract base class for title responses."""

    @classmethod
    def _create_title(
        cls,
        text: str,
        color: Optional[TerminalColor] = TerminalColor.CYAN,
        fill_char: Optional[str] = None
    ) -> 'AbstractTitleResponse':
        """Create a title response.
        
        Args:
            text (str): The title text
            color (Optional[TerminalColor]): Color for the title
            fill_char (str): Character to use for filling the line
            
        Returns:
            AbstractTitleResponse: A new title response
        """
        # Get terminal width, default to 80 if not available
        term_width = shutil.get_terminal_size().columns or 80
        
        # Get the prefix and text with padding
        prefix = cls.get_prefix()
        text_with_padding = f" {text} "
        fill_char = fill_char or "⫻"

        # Calculate remaining width for fill characters
        remaining_width = term_width - len(prefix) - len(text_with_padding)
        fill_text = fill_char * remaining_width
        
        # Combine all parts
        full_text = f"{prefix}{text_with_padding}{fill_text}"
        
        # Create colored segment
        title_segment = PromptResponseSegment(
            text=ColorManager.colorize(full_text, color) if color else full_text
        )
        
        # Add empty lines for spacing
        empty_line = PromptResponseLine(segments=[PromptResponseSegment(text="")])
        title_line = PromptResponseLine(segments=[title_segment])
        
        # Return with padding
        return cls(
            lines=[empty_line, title_line, empty_line],
            response_type=ResponseType.TITLE,
            message_type=MessageType.LOG
        )
    
    @classmethod
    @abstractmethod
    def get_prefix(cls) -> str:
        """Get the prefix for this title type.
        
        Returns:
            str: The prefix to use for this title type
        """
        pass
