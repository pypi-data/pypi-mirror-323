from typing import ClassVar

from wexample_prompt.common.prompt_context import PromptContext
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.enums.terminal_color import TerminalColor
from wexample_prompt.responses.messages.base_message_response import BaseMessageResponse


class TaskPromptResponse(BaseMessageResponse):
    """Response for task messages."""

    SYMBOL: ClassVar[str] = "⚡"

    @classmethod
    def create_task(
        cls: "TaskPromptResponse",
        message: str,
        context: PromptContext = None,
        **kwargs
    ) -> "TaskPromptResponse":
        return cls._create_symbol_message(
            text=message,
            context=context,
            color=TerminalColor.YELLOW,
            **kwargs
        )

    @classmethod
    def get_message_type(cls) -> MessageType:
        return MessageType.TASK
