from typing import Optional
from pydantic import BaseModel, Field

from wexample_prompt.common.io_manager import IoManager


class WithIoManager:
    io_manager: Optional[IoManager] = Field(
        default=None,
        description="IoManager instance that can be injected via constructor"
    )
    
    @property
    def io(self) -> IoManager:
        """Get the IoManager instance. Creates one if none exists."""
        if self.io_manager is None:
            self.io_manager = IoManager()
        return self.io_manager
    
    @io.setter
    def io(self, manager: IoManager) -> None:
        """Set the IoManager instance."""
        self.io_manager = manager
