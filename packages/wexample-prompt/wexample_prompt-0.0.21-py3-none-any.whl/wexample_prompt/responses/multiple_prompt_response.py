"""A response that contains multiple responses of different types."""
from typing import List

from wexample_prompt.responses.abstract_prompt_response import AbstractPromptResponse
from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.common.prompt_response_line import PromptResponseLine


class MultiplePromptResponse(BasePromptResponse):
    """A response that contains multiple responses of different types."""

    responses: List[AbstractPromptResponse]
    response_type: ResponseType = ResponseType.MULTIPLE
    message_type: MessageType = MessageType.LOG

    def __init__(self, responses: List[AbstractPromptResponse], **data):
        # Initialize with empty lines, they will be rendered from responses
        data['lines'] = []
        data['response_type'] = ResponseType.MULTIPLE
        data['message_type'] = MessageType.LOG
        data['responses'] = responses
        super().__init__(**data)

    def render(self) -> str:
        """Render all contained responses in sequence."""
        return "\n".join(response.render() for response in self.responses)

    def print(self, *args, **kwargs) -> None:
        """Print all contained responses in sequence."""
        for response in self.responses:
            response.print(*args, **kwargs)

    @classmethod
    def create_multiple(cls, responses: List[AbstractPromptResponse]) -> 'MultiplePromptResponse':
        """Create a new MultiplePromptResponse from a list of responses."""
        return cls(responses=responses)

    @classmethod
    def create(cls, *args, **kwargs) -> 'MultiplePromptResponse':
        """Create a new MultiplePromptResponse instance."""
        return cls.create_multiple(*args, **kwargs)

    def append_response(self, response: AbstractPromptResponse) -> 'MultiplePromptResponse':
        """Add a new response to the list."""
        self.responses.append(response)
        return self

    def extend_responses(self, responses: List[AbstractPromptResponse]) -> 'MultiplePromptResponse':
        """Add multiple responses to the list."""
        self.responses.extend(responses)
        return self
