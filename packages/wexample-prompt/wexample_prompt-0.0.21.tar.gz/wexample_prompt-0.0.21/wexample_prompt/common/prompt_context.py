import shutil
from typing import Optional, Dict, Any

from pydantic import BaseModel, Field

from wexample_prompt.enums.verbosity_level import VerbosityLevel


class PromptContext(BaseModel):
    """Context for rendering responses, including terminal information."""
    terminal_width: int = Field(
        default_factory=lambda: shutil.get_terminal_size().columns
    )
    is_tty: bool = Field(
        default_factory=lambda: hasattr(shutil.sys.stdout, 'isatty')
                                and shutil.sys.stdout.isatty()
    )
    color_enabled: bool = Field(default=True)
    indentation: int = Field(default=0)  # Number of indentation levels
    verbosity: VerbosityLevel = Field(default=VerbosityLevel.DEFAULT)
    fatal: bool = Field(default=False, description="If True, process will exit after printing")
    exit_code: int = Field(default=1, description="Exit code to use when fatal is True")
    params: Optional[Dict[str, Any]] = None

    def get_effective_width(self) -> int:
        """Get the effective width considering terminal constraints."""
        return min(self.terminal_width, 120)  # Cap at reasonable width

    def should_use_color(self) -> bool:
        """Determine if color should be used."""
        return self.color_enabled and self.is_tty

    def get_indentation(self) -> str:
        """Get the current indentation string."""
        return " " * (self.indentation * 2)  # Two spaces per level

    def should_show_message(self, required_verbosity: VerbosityLevel) -> bool:
        """Check if a message should be shown based on verbosity level."""
        return required_verbosity <= self.verbosity

    def format_message(self, message: str) -> str:
        if self.params:
            return message.format(**self.params)
        return message
