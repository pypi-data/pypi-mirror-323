from typing import ClassVar, Optional, Any

from wexample_prompt.common.error_context import ErrorContext
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse


class ErrorPromptResponse(BaseMessageResponse):
    SYMBOL: ClassVar[str] = "❌"
    exception: Optional[Any] = None

    @classmethod
    def create_error(
        cls: "ErrorPromptResponse",
        message: Optional[str] = None,
        context: Optional[ErrorContext] = None,
        exception: Optional[Any] = None,
        **kwargs
    ) -> "ErrorPromptResponse":
        # Create response with context
        response = cls._create_symbol_message(
            text=message or "Undefined error",
            color=TerminalColor.RED,
            context=context,
            **kwargs
        )

        response.exception = exception

        return response

    def _on_fatal(self):
        if self.exception:
            raise self.exception

    @classmethod
    def get_message_type(cls) -> MessageType:
        """Get the message type for error messages."""
        return MessageType.ERROR
