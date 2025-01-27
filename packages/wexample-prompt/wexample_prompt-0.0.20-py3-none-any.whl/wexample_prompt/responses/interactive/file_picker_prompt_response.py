"""Response for displaying and handling file picker prompts."""
import os
from typing import Any, Dict, Optional

from wexample_prompt.responses.interactive.choice_dict_prompt_response import ChoiceDictPromptResponse
from wexample_helpers.helpers.dict import dict_merge, dict_sort_values


class FilePickerPromptResponse(ChoiceDictPromptResponse):
    """Response for displaying a file picker interface."""

    @classmethod
    def create_file_picker(
        cls,
        base_dir: Optional[str] = None,
        question: str = "Select a file:",
        abort: Optional[str] = "> Abort",
        **kwargs: Any
    ) -> 'FilePickerPromptResponse':
        """Create a file picker prompt response.
        
        Args:
            base_dir: Starting directory (defaults to current working directory)
            question: The question to display
            abort: Optional abort choice text
            **kwargs: Additional arguments for inquirer.select
            
        Returns:
            FilePickerPromptResponse: A new file picker prompt response
        """
        base_dir = base_dir or os.getcwd()
        
        # Separate directories and files for better organization
        choices_dirs: Dict[str, str] = {"..": ".."}
        choices_files: Dict[str, str] = {}
        
        # List directory contents
        for element in os.listdir(base_dir):
            full_path = os.path.join(base_dir, element)
            if os.path.isdir(full_path):
                element_label = f"📁 {element}"
                choices_dirs[element] = element_label
            else:
                choices_files[element] = element
                
        # Sort both dictionaries by their values
        choices_dirs = dict_sort_values(choices_dirs)
        choices_files = dict_sort_values(choices_files)
        
        # Create response with merged choices
        response = super().create_choice_dict(
            question=question,
            choices=dict_merge(choices_dirs, choices_files),
            abort=abort,
            **kwargs
        )
        
        # Store base directory for execute()
        response._base_dir = base_dir
        return response
        
    def execute(self) -> Optional[str]:
        """Execute the file picker prompt and get selected path.
        
        Returns:
            str: Full path to selected file, or None if aborted
        """
        selected = super().execute()
        if not selected:
            return None
            
        full_path = os.path.join(self._base_dir, selected)
        
        # If directory selected, create new picker for that directory
        if os.path.isdir(full_path):
            next_response = self.__class__.create_file_picker(
                base_dir=full_path,
                question=self.lines[0].render()  # Keep same question
            )
            return next_response.execute()
            
        # If file selected, return its full path
        return full_path
