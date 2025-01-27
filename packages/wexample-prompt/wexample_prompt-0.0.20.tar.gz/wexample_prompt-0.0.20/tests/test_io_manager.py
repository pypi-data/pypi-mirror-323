"""Tests for IoManager."""
import io
import sys
import unittest
from unittest.mock import patch

from wexample_prompt.common.io_manager import IoManager
from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.responses.messages.success_prompt_response import SuccessPromptResponse
from wexample_prompt.responses.messages.error_prompt_response import ErrorPromptResponse
from wexample_prompt.responses.messages.warning_prompt_response import WarningPromptResponse
from wexample_prompt.common.color_manager import ColorManager
from wexample_prompt.enums.message_type import MessageType
from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.common.error_context import ErrorContext


class TestIoManager(unittest.TestCase):
    """Test cases for IoManager."""
    
    def setUp(self):
        """Set up test cases."""
        # Mock stdout with StringIO
        self.stdout = io.StringIO()
        sys.stdout = self.stdout
        self.io_manager = IoManager()
        self.io_manager._stdout = self.stdout
        
        # Force color support for tests
        self.original_supports_color = ColorManager.supports_color
        ColorManager.supports_color = lambda: True
    
    def tearDown(self):
        """Clean up after tests."""
        sys.stdout = sys.__stdout__
        self.stdout.close()
        # Restore original color support check
        ColorManager.supports_color = self.original_supports_color
    
    def test_print_responses(self):
        """Test printing multiple responses."""
        # Create test responses
        responses = [
            SuccessPromptResponse.create_success("Success"),
            ErrorPromptResponse.create_error("Error")
        ]
        
        # Print responses
        self.io_manager.print_responses(responses)
        
        # Check output
        output = self.stdout.getvalue()
        self.assertIn("Success", output)
        self.assertIn("Error", output)
    
    def test_indentation(self):
        """Test indentation functionality."""
        # Create a test response with a simple text segment
        line = PromptResponseLine(segments=[
            PromptResponseSegment(text="Test message")
        ])
        response = BasePromptResponse(
            lines=[line],
            message_type=MessageType.SUCCESS
        )
        
        # Set indentation level to 2 (4 spaces)
        self.io_manager.log_indent = 2
        
        # Print response
        self.io_manager.print_response(response)
        
        # Check output has correct indentation (4 spaces)
        output = self.stdout.getvalue()
        self.assertTrue(any(line.startswith("    ") for line in output.splitlines()))

    def test_theme_color_application(self):
        """Test that theme colors are properly applied."""
        # Create a test response
        response = SuccessPromptResponse.create_success("Test message")
        
        # Print response
        self.io_manager.print_response(response)
        
        # Check output contains color codes
        output = self.stdout.getvalue()
        self.assertIn("\033[", output)  # ANSI color code
        self.assertIn("Test message", output)

    def test_fatal_error(self):
        class TestFatalError(Exception):
            pass

        """Test fatal error handling."""
        with self.assertRaises(TestFatalError) as context:
            self.io_manager.error("Fatal error", fatal=True, exception=TestFatalError)

        output = self.stdout.getvalue()
        self.assertIn("Fatal error", output)

    def test_terminal_width_update(self):
        """Test terminal width update."""
        original_width = self.io_manager._tty_width
        with patch('shutil.get_terminal_size') as mock_size:
            mock_size.return_value = type('Size', (), {'columns': 100})()
            self.io_manager.update_terminal_width()
            self.assertEqual(self.io_manager._tty_width, 100)
            self.assertNotEqual(self.io_manager._tty_width, original_width)
