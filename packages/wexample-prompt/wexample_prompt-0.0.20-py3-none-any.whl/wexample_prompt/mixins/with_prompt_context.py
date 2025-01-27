from typing import Optional, Any

from wexample_prompt.mixins.with_io_manager import WithIoManager


class WithPromptContext(WithIoManager):
    prompt_context_parent: Optional[Any] = None
    _context_indent: int = 2  # Number of spaces for each indentation level

    def get_prompt_context_parent(self) -> Optional['WithPromptContext']:
        """Get the parent context for indentation. By default, returns None."""
        return self.prompt_context_parent

    def set_prompt_context_parent(self, parent: 'WithPromptContext') -> None:
        """Set the parent context for indentation."""
        self.prompt_context_parent = parent

    def get_context_indent_level(self) -> int:
        """Calculate the indentation level based on parent contexts."""
        parent = self.get_prompt_context_parent()
        if parent is None:
            return 0
        return parent.get_context_indent_level() + 1

    def format_message(self, message: str) -> str:
        """Format the message according to the bullet point style."""
        indent = " " * (self.get_context_indent_level() * self._context_indent)
        context_name = self.__class__.__name__

        if self.io._last_context != context_name:
            self.io._last_context = context_name
            return f"{indent}• {context_name}: {message}"

        return f"{indent}  ⋮ {message}"

    def log(self, message: str, **kwargs) -> None:
        """Format and send a message through the IO manager."""
        formatted_message = self.format_message(message)
        self.io.log(formatted_message, **kwargs)

    def debug(self, message: str, **kwargs) -> None:
        formatted_message = self.format_message(message)
        self.io.debug(formatted_message, **kwargs)

    def info(self, message: str, **kwargs) -> None:
        formatted_message = self.format_message(message)
        self.io.info(formatted_message, **kwargs)

    def warning(self, message: str, **kwargs) -> None:
        formatted_message = self.format_message(message)
        self.io.warning(formatted_message, **kwargs)

    def error(self, message: str, **kwargs) -> None:
        formatted_message = self.format_message(message)
        self.io.error(formatted_message, **kwargs)
