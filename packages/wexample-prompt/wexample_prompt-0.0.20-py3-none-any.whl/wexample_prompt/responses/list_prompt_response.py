"""Response for displaying items in a bulleted list."""
from typing import List, Optional

from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.common.prompt_context import PromptContext


class ListPromptResponse(BasePromptResponse):
    """Response for displaying items in a bulleted list."""

    items: List[str]
    bullet: str = "•"

    @classmethod
    def create_list(
        cls,
        items: List[str],
        bullet: str = "•",
        context: Optional[PromptContext] = None
    ) -> 'ListPromptResponse':
        """Create a list response.
        
        Args:
            items: List of items to display
            bullet: Bullet character to use (default: •)
            context: Optional prompt context for formatting
            
        Returns:
            ListPromptResponse: A new list response
        """
        return cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.LIST,
            items=items,
            bullet=bullet,
            context=context
        )

    def render(self) -> str:
        """Render the list with bullets and indentation."""
        if not self.items:
            return ""

        lines = []
        for item in self.items:
            # Check if this is a sub-item by looking for leading spaces
            indent_level = 0
            content = item
            
            while content.startswith("  "):
                indent_level += 1
                content = content[2:]
                
            # Remove bullet if the content already has one
            if content.startswith(f"{self.bullet} "):
                content = content[2:]
                
            # Create line with proper indentation
            segments = [
                PromptResponseSegment(text="  " * indent_level + f"{self.bullet} "),
                PromptResponseSegment(text=content)
            ]
            lines.append(PromptResponseLine(segments=segments))

        # Update lines and render
        self.lines = lines
        return super().render()
