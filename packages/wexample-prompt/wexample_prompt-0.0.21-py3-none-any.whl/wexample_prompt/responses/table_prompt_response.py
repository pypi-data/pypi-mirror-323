"""Table response for displaying data in a formatted table layout."""
from typing import List, Any, Optional

from wexample_prompt.common.prompt_response_line import PromptResponseLine
from wexample_prompt.common.prompt_response_segment import PromptResponseSegment
from wexample_prompt.enums.response_type import ResponseType
from wexample_prompt.responses.base_prompt_response import BasePromptResponse
from wexample_prompt.common.prompt_context import PromptContext


class TablePromptResponse(BasePromptResponse):
    """Response for displaying data in a table layout with borders and formatting."""

    data: List[List[Any]]
    headers: Optional[List[str]] = None
    title: Optional[str] = None

    @classmethod
    def create_table(
        cls,
        data: List[List[Any]],
        headers: Optional[List[str]] = None,
        title: Optional[str] = None,
        context: Optional[PromptContext] = None
    ) -> 'TablePromptResponse':
        return cls(
            lines=[],  # Lines will be generated in render()
            response_type=ResponseType.TABLE,
            data=data,
            headers=headers,
            title=title,
            context=context
        )

    def render(self) -> str:
        """Render the table with borders and formatting."""
        if not self.data and not self.headers:
            return ""

        # Combine headers and data for width calculation
        all_rows = []
        if self.headers:
            all_rows.append(self.headers)
        all_rows.extend(self.data)

        # Calculate column widths
        max_widths = self._calculate_max_widths(all_rows)
        
        # Calculate total line length for borders
        total_width = sum(max_widths) + (len(max_widths) * 3) - 1
        
        lines = []
        
        # Add title if provided
        if self.title:
            title_padding = (total_width - len(self.title)) // 2
            title_line = PromptResponseLine(segments=[
                PromptResponseSegment(text="+" + "-" * title_padding),
                PromptResponseSegment(text=f" {self.title} "),
                PromptResponseSegment(text="-" * (total_width - title_padding - len(self.title) - 2) + "+")
            ])
            lines.append(title_line)
        else:
            # Top border
            lines.append(self._create_border_line(total_width))
            
        # Add headers if provided
        if self.headers:
            header_segments = self._create_row_segments(self.headers, max_widths)
            lines.append(PromptResponseLine(segments=header_segments))
            lines.append(self._create_border_line(total_width))
            
        # Add data rows
        for row in self.data:
            row_segments = self._create_row_segments(row, max_widths)
            lines.append(PromptResponseLine(segments=row_segments))
            
        # Bottom border
        lines.append(self._create_border_line(total_width))
        
        # Update lines and render
        self.lines = lines
        return super().render()
    
    @staticmethod
    def _calculate_max_widths(rows: List[List[Any]]) -> List[int]:
        """Calculate the maximum width needed for each column.
        
        Args:
            rows: List of all rows including headers
            
        Returns:
            List of maximum widths for each column
        """
        if not rows:
            return []
            
        # Find the maximum number of columns
        num_columns = max(len(row) for row in rows)
        
        # Initialize max widths
        max_widths = [0] * num_columns
        
        # Calculate max width for each column
        for row in rows:
            for i in range(num_columns):
                cell_content = str(row[i]) if i < len(row) else ""
                max_widths[i] = max(max_widths[i], len(cell_content))
                
        return max_widths
    
    @staticmethod
    def _create_row_segments(
        row: List[Any],
        widths: List[int]
    ) -> List[PromptResponseSegment]:
        """Create segments for a table row with proper formatting.
        
        Args:
            row: List of cell values
            widths: List of column widths
            
        Returns:
            List of formatted segments for the row
        """
        segments = [PromptResponseSegment(text="|")]
        
        for i in range(len(widths)):
            cell_content = str(row[i]) if i < len(row) else ""
            cell_text = f" {cell_content:<{widths[i]}} |"
            segments.append(PromptResponseSegment(text=cell_text))
            
        return segments
    
    @staticmethod
    def _create_border_line(width: int) -> PromptResponseLine:
        """Create a horizontal border line.
        
        Args:
            width: Total width of the table
            
        Returns:
            PromptResponseLine with border
        """
        return PromptResponseLine(segments=[
            PromptResponseSegment(text="+" + "-" * width + "+")
        ])
