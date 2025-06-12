"""
Text file utility functions for common file operations.

This module provides helper methods for working with text files, including
line counting and file previewing capabilities. The TextFileHelper class
implements static methods for efficient file operations without requiring
class instantiation.

Key features:
- Line counting for text files
- File previewing with configurable line limits
- Whitespace handling options

Copyright (c) 2023 Jim Schilling
All Rights Reserved.

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
    def line_count(file_name: Union[PathLike, str]) -> int:
        """Count the number of lines in a text file.

        This method efficiently counts lines by iterating through the file
        without loading it entirely into memory.

        Args:
            file_name: Path to the text file

        Returns:
            int: Number of lines in the file

        Raises:
            ValueError: If file_name is None
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there are issues reading the file
        """
        with open(file_name, 'r') as stream:
            # Use generator expression for memory efficiency
            return sum(1 for _ in stream)

    @staticmethod
    def preview(file_name: Union[PathLike, str], max_lines: int = 100, strip: bool = True) -> List[str]:
        """Preview the first N lines of a text file.

        This method reads up to max_lines from the beginning of the file,
        optionally stripping whitespace from each line.

        Args:
            file_name: Path to the text file
            max_lines: Maximum number of lines to read (default: 100)
            strip: Whether to strip whitespace from lines (default: True)

        Returns:
            List[str]: List of lines from the file

        Raises:
            ValueError: If max_lines < 1
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there are issues reading the file
        """        
        if max_lines < 1:
            raise ValueError("TextFileHelper.preview: max_lines is less than 1")

        lines = []
        with open(file_name, 'r') as stream:
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
    def load(file_name: Union[PathLike, str], strip: bool = True) -> List[str]:
        """Load the entire contents of a text file into a list of strings.

        This method reads the complete file into memory, with an option
        to strip whitespace from each line.

        Args:
            file_name: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)

        Returns:
            List[str]: List of all lines from the file

        Raises:
            FileNotFoundError: If the specified file doesn't exist
            IOError: If there are issues reading the file
        """
        with open(file_name, 'r') as stream:
            if strip:
                return [line.strip() for line in stream]
            return [line.rstrip('\n') for line in stream]