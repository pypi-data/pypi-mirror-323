from typing import ClassVar, TYPE_CHECKING

from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.common.prompt_context import PromptContext

if TYPE_CHECKING:
    from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse


class FailurePromptResponse(BaseMessageResponse):
    """Response for failure messages."""
    
    SYMBOL: ClassVar[str] = "❌"
    
    @classmethod
    def create_failure(
        cls: "FailurePromptResponse",
        message: str,
        context: PromptContext = None,
        **kwargs
    ) -> "AbstractPromptResponse":
        return cls._create_symbol_message(
            text=message,
            context=context,
            color=TerminalColor.RED,
            **kwargs
        )
    
    @classmethod
    def get_message_type(cls) -> MessageType:
        """Get the message type for failure messages."""
        return MessageType.FAILURE
