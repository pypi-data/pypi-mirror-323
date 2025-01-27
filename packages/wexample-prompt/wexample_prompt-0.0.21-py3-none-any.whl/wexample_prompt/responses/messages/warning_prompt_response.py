from typing import ClassVar, TYPE_CHECKING

from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.common.error_context import ErrorContext

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class WarningPromptResponse(BaseMessageResponse):
    """Response for warning messages."""

    SYMBOL: ClassVar[str] = "⚠️"

    @classmethod
    def create_warning(
        cls: "WarningPromptResponse",
        message: str,
        context: ErrorContext = None,
        **kwargs
    ) -> "AbstractPromptResponse":
        return cls._create_symbol_message(
            text=message,
            context=context or ErrorContext(),
            color=TerminalColor.YELLOW,
            **kwargs
        )

    @classmethod
    def get_message_type(cls) -> MessageType:
        """Get the message type for warning messages."""
        return MessageType.WARNING
