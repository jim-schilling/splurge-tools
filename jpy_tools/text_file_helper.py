"""
Text file utility functions for common file operations.

This module provides helper methods for working with text files, including
line counting, file previewing, and file loading capabilities. The TextFileHelper 
class implements static methods for efficient file operations without requiring
class instantiation.

Key features:
- Line counting for text files
- File previewing with configurable line limits
- Complete file loading with header/footer skipping
- Configurable whitespace handling and encoding

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""

from os import PathLike
from typing import Union, List


class TextFileHelper:
    """Utility class for text file operations.
    
    This class provides static methods for common text file operations,
    making it easy to perform file operations without instantiating the class.
    All methods are designed to be memory efficient by processing files
    line by line rather than loading entire files into memory.
    """

    @staticmethod
    def line_count(file_name: Union[PathLike, str], encoding: str = 'utf-8') -> int:
        """Count the number of lines in a text file.

        This method efficiently counts lines by iterating through the file
        without loading it entirely into memory.

        Args:
            file_name: Path to the text file
            encoding: File encoding to use (default: 'utf-8')

        Returns:
            int: Number of lines in the file

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there are issues reading the file
            UnicodeDecodeError: If the file cannot be decoded with the specified encoding
        """
        with open(file_name, 'r', encoding=encoding) as stream:
            # Use generator expression for memory efficiency
            return sum(1 for _ in stream)

    @staticmethod
    def preview(
        file_name: Union[PathLike, str], 
        max_lines: int = 100, 
        strip: bool = True, 
        encoding: str = 'utf-8'
    ) -> List[str]:
        """Preview the first N lines of a text file.

        This method reads up to max_lines from the beginning of the file,
        optionally stripping whitespace from each line.

        Args:
            file_name: Path to the text file
            max_lines: Maximum number of lines to read (default: 100)
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')

        Returns:
            List[str]: List of lines from the file

        Raises:
            ValueError: If max_lines < 1
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there are issues reading the file
            UnicodeDecodeError: If the file cannot be decoded with the specified encoding
        """        
        if max_lines < 1:
            raise ValueError("TextFileHelper.preview: max_lines is less than 1")

        lines = []
        with open(file_name, 'r', encoding=encoding) as stream:
            # Read up to max_lines or until EOF
            for _ in range(max_lines):
                line = stream.readline()
                if not line:  # EOF reached
                    break
                # Strip newline but preserve other whitespace when strip=False
                if strip:
                    lines.append(line.strip())
                else:
                    lines.append(line.rstrip('\n'))
        return lines

    @staticmethod
    def load(
        file_name: Union[PathLike, str], 
        strip: bool = True, 
        encoding: str = 'utf-8',
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0
    ) -> List[str]:
        """Load the entire contents of a text file into a list of strings.

        This method reads the complete file into memory, with options to
        strip whitespace from each line and skip header/footer rows.

        Args:
            file_name: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)
            skip_footer_rows: Number of rows to skip from the end (default: 0)

        Returns:
            List[str]: List of all lines from the file, excluding skipped rows

        Raises:
            ValueError: If skip_header_rows + skip_footer_rows >= total lines
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there are issues reading the file
            UnicodeDecodeError: If the file cannot be decoded with the specified encoding
        """
        skip_header_rows = max(0, skip_header_rows)
        skip_footer_rows = max(0, skip_footer_rows)
        line_count = TextFileHelper.line_count(file_name, encoding)
        
        # Handle empty files
        if line_count == 0:
            return []
            
        # Validate skip parameters for non-empty files
        if skip_header_rows + skip_footer_rows >= line_count:
            raise ValueError("TextFileHelper.load: skip_header_rows + skip_footer_rows is greater than or equal to the number of lines in the file")
        
        lines = []
        with open(file_name, 'r', encoding=encoding) as stream:
            if strip:
                lines = [line.strip() for line in stream]
            else:
                lines = [line.rstrip('\n') for line in stream]
        return lines[skip_header_rows:-skip_footer_rows] if skip_footer_rows > 0 else lines[skip_header_rows:]