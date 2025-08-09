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
- Streaming file loading with configurable chunk sizes
- Configurable whitespace handling and encoding
- Secure file path validation
- Resource management with context managers

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import warnings
from collections import deque
from os import PathLike
from pathlib import Path
from typing import List, Iterator

from splurge_tools.exceptions import (
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError,
    SplurgeValidationError
)
from splurge_tools.path_validator import PathValidator
from splurge_tools.resource_manager import safe_file_operation


class TextFileHelper:
    """
    Utility class for text file operations.
    All methods are static and memory efficient.
    """

    @staticmethod
    def line_count(
        file_name: PathLike[str] | str,
        *,
        encoding: str = "utf-8"
    ) -> int:
        """
        Count the number of lines in a text file.

        This method efficiently counts lines by iterating through the file
        without loading it entirely into memory.

        Args:
            file_name: Path to the text file
            encoding: File encoding to use (default: 'utf-8')

        Returns:
            int: Number of lines in the file

        Raises:
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgeValidationError: If file path validation fails
        """
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_name),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True
        )
        
        with safe_file_operation(validated_path, encoding=encoding) as stream:
            return sum(1 for _ in stream)

    @staticmethod
    def preview(
        file_name: PathLike[str] | str,
        *,
        max_lines: int = 100,
        strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0
    ) -> List[str]:
        """
        Preview the first N lines of a text file.

        This method reads up to max_lines from the beginning of the file,
        optionally stripping whitespace from each line and skipping header rows.

        Args:
            file_name: Path to the text file
            max_lines: Maximum number of lines to read (default: 100)
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)

        Returns:
            List[str]: List of lines from the file

        Raises:
            SplurgeValidationError: If max_lines < 1 or file path validation fails
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
        """
        if max_lines < 1:
            raise SplurgeValidationError(
                "TextFileHelper.preview: max_lines is less than 1",
                details="max_lines must be at least 1"
            )
        
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_name),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True
        )
        
        skip_header_rows = max(0, skip_header_rows)
        lines: List[str] = []
        
        with safe_file_operation(validated_path, encoding=encoding) as stream:
            # Skip header rows
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return lines
            
            # Read up to max_lines after skipping headers
            for _ in range(max_lines):
                line = stream.readline()
                if not line:
                    break
                lines.append(line.strip() if strip else line.rstrip("\n"))
        
        return lines

    @staticmethod
    def read_as_stream(
        file_name: PathLike[str] | str,
        *,
        strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0,
        chunk_size: int = 500
    ) -> Iterator[List[str]]:
        """
        Read a text file as a stream of line chunks.

        This method yields chunks of lines from the file, allowing for
        memory-efficient processing of large files. Each chunk contains
        up to chunk_size lines. Uses a sliding window approach to handle
        footer row skipping without loading the entire file into memory.

        Args:
            file_name: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)
            skip_footer_rows: Number of rows to skip from the end (default: 0)
            chunk_size: Number of lines per chunk (default: 500)

        Yields:
            List[str]: Chunks of lines from the file

        Raises:
            SplurgeValidationError: If chunk_size < 100 or file path validation fails
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
        """
        if chunk_size < 100:
            raise SplurgeValidationError(
                "TextFileHelper.read_as_stream: chunk_size is less than 100",
                details="chunk_size must be at least 100 for efficient streaming"
            )
        
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_name),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True
        )
        
        skip_header_rows = max(0, skip_header_rows)
        skip_footer_rows = max(0, skip_footer_rows)
        
        with safe_file_operation(validated_path, encoding=encoding) as stream:
            # Skip header rows
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return
            
            # Use a sliding window to handle footer skipping efficiently
            if skip_footer_rows > 0:
                # Buffer to hold the last skip_footer_rows lines
                buffer: deque[str] = deque(maxlen=skip_footer_rows)
                current_chunk: List[str] = []
                
                for line in stream:
                    processed_line = line.strip() if strip else line.rstrip("\n")
                    
                    # Add to buffer for potential footer skipping
                    buffer.append(processed_line)
                    
                    # If buffer is full, move oldest line to current chunk
                    if len(buffer) == skip_footer_rows:
                        current_chunk.append(buffer.popleft())
                        
                        # Yield chunk when it reaches the desired size
                        if len(current_chunk) >= chunk_size:
                            yield current_chunk
                            current_chunk = []
                
                # Handle remaining lines (excluding the last skip_footer_rows)
                # The buffer now contains exactly the footer rows to skip
                # All other lines have already been processed and yielded
                
                # Yield any remaining lines in the final chunk
                if current_chunk:
                    yield current_chunk
            else:
                # No footer skipping needed - simple streaming
                chunk: List[str] = []
                
                for line in stream:
                    processed_line = line.strip() if strip else line.rstrip("\n")
                    chunk.append(processed_line)
                    
                    # Yield chunk when it reaches the desired size
                    if len(chunk) >= chunk_size:
                        yield chunk
                        chunk = []
                
                # Yield any remaining lines in the final chunk
                if chunk:
                    yield chunk

    @staticmethod
    def read(
        file_name: PathLike[str] | str,
        *,
        strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0
    ) -> List[str]:
        """
        Read the entire contents of a text file into a list of strings.

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
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgeValidationError: If file path validation fails
        """
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_name),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True
        )
        
        skip_header_rows = max(0, skip_header_rows)
        skip_footer_rows = max(0, skip_footer_rows)
        
        with safe_file_operation(validated_path, encoding=encoding) as stream:
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return []
            lines: List[str] = [line.strip() if strip else line.rstrip("\n") for line in stream]
            if skip_footer_rows > 0:
                if skip_footer_rows >= len(lines):
                    return []
                lines = lines[:-skip_footer_rows]
            return lines

    @staticmethod
    def load_as_stream(
        file_name: PathLike[str] | str,
        *,
        strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0,
        chunk_size: int = 500
    ) -> Iterator[List[str]]:
        """
        Load a text file as a stream of line chunks.

        This method yields chunks of lines from the file, allowing for
        memory-efficient processing of large files. Each chunk contains
        up to chunk_size lines. Uses a sliding window approach to handle
        footer row skipping without loading the entire file into memory.

        Args:
            file_name: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)
            skip_footer_rows: Number of rows to skip from the end (default: 0)
            chunk_size: Number of lines per chunk (default: 500)

        Yields:
            List[str]: Chunks of lines from the file

        Raises:
            SplurgeValidationError: If chunk_size < 100 or file path validation fails
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding

        Deprecated:
            This method is deprecated and will be removed in a future version.
            Use read_as_stream() instead.
        """
        warnings.warn(
            "TextFileHelper.load_as_stream is deprecated and will be removed in a future version. "
            "Use TextFileHelper.read_as_stream instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return TextFileHelper.read_as_stream(
            Path(file_name),
            strip=strip,
            encoding=encoding,
            skip_header_rows=skip_header_rows,
            skip_footer_rows=skip_footer_rows,
            chunk_size=chunk_size
        )

    @staticmethod
    def load(
        file_name: PathLike[str] | str,
        *,
        strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0
    ) -> List[str]:
        """
        Load the entire contents of a text file into a list of strings.

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
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgeValidationError: If file path validation fails

        Deprecated:
            This method is deprecated and will be removed in a future version.
            Use read() instead.
        """
        warnings.warn(
            "TextFileHelper.load is deprecated and will be removed in a future version. "
            "Use TextFileHelper.read instead.",
            DeprecationWarning,
            stacklevel=2
        )
        return TextFileHelper.read(
            Path(file_name),
            strip=strip,
            encoding=encoding,
            skip_header_rows=skip_header_rows,
            skip_footer_rows=skip_footer_rows
        )
