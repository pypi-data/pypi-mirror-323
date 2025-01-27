import shutil
import sys
import logging
from logging import Logger
from typing import Any, List, Optional, TextIO, Dict, Union, TYPE_CHECKING
from pydantic import BaseModel, ConfigDict, Field, PrivateAttr

from wexample_prompt.mixins.with_indent import WithIndent
from wexample_prompt.common.error_context import ErrorContext
from wexample_prompt.responses import BasePromptResponse
from wexample_prompt.themes.default.abstract_prompt_theme import AbstractPromptTheme
from wexample_prompt.themes.default.default_prompt_theme import DefaultPromptTheme

if TYPE_CHECKING:
    from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse
    from wexample_prompt.responses.messages.warning_prompt_response import WarningPromptResponse
    from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse
    from wexample_prompt.responses.messages.info_prompt_response import InfoPromptResponse
    from wexample_prompt.responses.messages.debug_prompt_response import DebugPromptResponse
    from wexample_prompt.responses.titles.title_prompt_response import TitlePromptResponse
    from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse

class IoManager(BaseModel, WithIndent):
    model_config = ConfigDict(arbitrary_types_allowed=True)

    theme: AbstractPromptTheme = Field(
        default_factory=DefaultPromptTheme,
        description="Theme for customizing colors and styles"
    )
    log_level: int = Field(
        default=logging.INFO,
        description="Minimum log level for file logging"
    )
    log_file: Optional[str] = Field(
        default=None,
        description="Path to log file. If None, file logging is disabled"
    )

    _logger: Logger = PrivateAttr()
    _tty_width: int = PrivateAttr(default_factory=lambda: shutil.get_terminal_size().columns)
    _stdout: TextIO = PrivateAttr(default_factory=lambda: sys.stdout)
    _stdin: TextIO = PrivateAttr(default_factory=lambda: sys.stdin)
    _last_context: Optional[str] = PrivateAttr(default=None)

    def __init__(self, **data):
        super().__init__(**data)
        self._tty_width = shutil.get_terminal_size().columns
        self._stdout = sys.stdout
        self._stdin = sys.stdin
        self._last_context = None
        self._setup_logger()

    def _setup_logger(self) -> None:
        """Configure the Python logger with proper formatting and handlers."""
        self._logger = logging.getLogger("prompt")
        self._logger.setLevel(self.log_level)

        # Clear any existing handlers
        self._logger.handlers.clear()

        # Only add file handler if log_file is specified
        if self.log_file:
            file_handler = logging.FileHandler(self.log_file)
            file_handler.setFormatter(
                logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
            )
            self._logger.addHandler(file_handler)

    def error(
        self,
        message: Optional[Union[str, Exception]] = None,
        params: Optional[Dict[str, Any]] = None,
        exception = None,
        fatal: bool = True,
    ) -> "ErrorPromptResponse":
        from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse

        # Create context and response
        context = ErrorContext(
            fatal=fatal,
            params=params,
            indentation=self.log_indent
        )
        response = ErrorPromptResponse.create_error(
            message=message,
            context=context,
            exception=exception
        )
        
        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.error(message, extra={"params": params} if params else None)
        
        # Display formatted message
        self.print_response(response)
        return response

    def warning(
        self,
        message: str,
        params: Optional[Dict[str, Any]] = None,
        trace: bool = False
    ) -> "WarningPromptResponse":
        from wexample_prompt.responses.messages.warning_prompt_response import WarningPromptResponse
        context = ErrorContext(
            fatal=False,
            params=params,
            indentation=self.log_indent
        )
        response = WarningPromptResponse.create_warning(message, context)
        
        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.warning(message, extra={"params": params} if params else None)
        
        self.print_response(response)
        return response

    def success(self, message: str) -> "SuccessPromptResponse":
        from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse

        response = SuccessPromptResponse.create_success(message)
        
        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.info(f"SUCCESS: {message}")
        
        self.print_response(response)
        return response

    def info(self, message: str) -> "InfoPromptResponse":
        from wexample_prompt.responses.messages.info_prompt_response import InfoPromptResponse

        response = InfoPromptResponse.create_info(message)
        
        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.info(message)
        
        self.print_response(response)
        return response

    def debug(self, message: str) -> "DebugPromptResponse":
        from wexample_prompt.responses.messages.debug_prompt_response import DebugPromptResponse

        response = DebugPromptResponse.create_debug(message)
        
        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.debug(message)
        
        self.print_response(response)
        return response

    def title(self, message: str) -> "TitlePromptResponse":
        from wexample_prompt.responses.titles.title_prompt_response import TitlePromptResponse

        response = TitlePromptResponse.create_title(message)

        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.debug(message)

        self.print_response(response)
        return response

    def subtitle(self, message: str) -> "TitlePromptResponse":
        from wexample_prompt.responses.titles.subtitle_prompt_response import SubtitlePromptResponse

        response = SubtitlePromptResponse.create_subtitle(message)

        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.debug(message)

        self.print_response(response)
        return response


    def log(self, message: str) -> "TitlePromptResponse":
        from wexample_prompt.responses.messages.log_prompt_response import LogPromptResponse

        response = LogPromptResponse.create_log(message)

        # Log to file/system if configured
        if self._logger.handlers:
            self._logger.debug(message)

        self.print_response(response)
        return response

    def log_raw(self, level: int, message: str, extra: Optional[Dict[str, Any]] = None) -> None:
        """
        Log a message directly to the logger without UI formatting.
        Useful for internal logging or passing data between processes.
        """
        if self._logger.handlers:
            self._logger.log(level, message, extra=extra)

    def print_responses(self, responses: List[BasePromptResponse]) -> None:
        for response in responses:
            self.print_response(response)

    def print_response(self, response: BasePromptResponse) -> None:
        """Print a response using its own context."""
        # If response has a context but no indentation, set it
        if response.context.indentation == 0 and self.log_indent > 0:
            response.context.indentation = self.log_indent

        response.print(output=self._stdout)

    def get_input(self, prompt: str = "") -> str:
        return input(prompt)

    def print(self, message: Any, **kwargs: Any) -> None:
        # Convert message to response if it's not already one
        if isinstance(message, BasePromptResponse):
            response = message
        else:
            response = InfoPromptResponse.create_info(str(message))
        
        self.print_response(response)

    def update_terminal_width(self) -> None:
        self._tty_width = shutil.get_terminal_size().columns

    @property
    def terminal_width(self) -> int:
        return self._tty_width
