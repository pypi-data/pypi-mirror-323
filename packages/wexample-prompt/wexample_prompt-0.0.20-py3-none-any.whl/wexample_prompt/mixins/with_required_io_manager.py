from pydantic import Field

from wexample_prompt.common.io_manager import IoManager
from wexample_prompt.mixins.with_io_manager import WithIoManager


class WithRequiredIoManager(WithIoManager):
    """Mixin that requires an IoManager instance."""
    
    io_manager: IoManager = Field(
        ...,
        description="Required IoManager instance"
    )
