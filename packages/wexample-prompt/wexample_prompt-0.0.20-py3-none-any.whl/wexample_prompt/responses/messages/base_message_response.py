from abc import abstractmethod
from typing import Optional, ClassVar

from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.responses.base_prompt_response import BasePromptResponse

from wexample_prompt.common.prompt_context import PromptContext


class BaseMessageResponse(BasePromptResponse):
    # Symbol to display before the message, override in subclasses
    SYMBOL: ClassVar[str] = ""

    @classmethod
    @abstractmethod
    def get_message_type(cls) -> MessageType:
        pass

    @classmethod
    def _create_symbol_message(
        cls,
        text: str,
        color: TerminalColor,
        symbol: Optional[str] = None,
        bold_symbol: bool = True,
        context: Optional[PromptContext] = None
    ) -> 'BaseMessageResponse':
        segments = []

        # Add symbol if present
        if symbol or cls.SYMBOL:
            symbol_text = f"{symbol or cls.SYMBOL} "
            symbol_segment = PromptResponseSegment(
                text=ColorManager.colorize(
                    symbol_text,
                    color,
                    TerminalColor.BOLD if bold_symbol else None
                )
            )
            segments.append(symbol_segment)

        # Add message text
        message = PromptResponseSegment(
            text=ColorManager.colorize(text, color)
        )
        segments.append(message)

        # Create line with segments
        line = PromptResponseLine(
            segments=segments,
            line_type=cls.get_message_type()
        )

        return cls._create(
            lines=[line],
            message_type=cls.get_message_type(),
            **({"context": context} if context is not None else {})
        )
