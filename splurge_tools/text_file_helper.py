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

from collections import deque
from collections.abc import Iterator
from os import PathLike
from pathlib import Path

from splurge_tools.exceptions import SplurgeFileEncodingError, SplurgeParameterError
from splurge_tools.path_validator import PathValidator
from splurge_tools.resource_manager import safe_file_operation


class TextFileHelper:
    """
    Utility class for text file operations.
    All methods are static and memory efficient.
    """

    DEFAULT_ENCODING = "utf-8"
    DEFAULT_MAX_LINES = 100
    DEFAULT_CHUNK_SIZE = 500
    DEFAULT_MIN_CHUNK_SIZE = 100
    DEFAULT_SKIP_HEADER_ROWS = 0
    DEFAULT_SKIP_FOOTER_ROWS = 0
    DEFAULT_STRIP = True
    DEFAULT_MODE = "r"

    @classmethod
    def line_count(
        cls,
        file_path: PathLike[str] | str,
        *,
        encoding: str = DEFAULT_ENCODING,
    ) -> int:
        """
        Count the number of lines in a text file.

        This method efficiently counts lines by iterating through the file
        without loading it entirely into memory.

        Args:
            file_path: Path to the text file
            encoding: File encoding to use (default: 'utf-8')

        Returns:
            int: Number of lines in the file

        Raises:
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgePathValidationError: If file path validation fails
        """
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True,
        )

        with safe_file_operation(validated_path, encoding=encoding, mode=cls.DEFAULT_MODE) as stream:
            return sum(1 for _ in stream)

    @classmethod
    def preview(
        cls,
        file_path: PathLike[str] | str,
        *,
        max_lines: int = DEFAULT_MAX_LINES,
        strip: bool = DEFAULT_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
    ) -> list[str]:
        """
        Preview the first N lines of a text file.

        This method reads up to max_lines from the beginning of the file,
        optionally stripping whitespace from each line and skipping header rows.

        Args:
            file_path: Path to the text file
            max_lines: Maximum number of lines to read (default: 100)
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)

        Returns:
            list[str]: List of lines from the file

        Raises:
            SplurgeParameterError: If max_lines < 1
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgePathValidationError: If file path validation fails
        """
        if max_lines < 1:
            msg = "TextFileHelper.preview: max_lines is less than 1"
            raise SplurgeParameterError(
                msg,
                details="max_lines must be at least 1",
            )

        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True,
        )

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        lines: list[str] = []

        with safe_file_operation(validated_path, encoding=encoding, mode=cls.DEFAULT_MODE) as stream:
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

    @classmethod
    def read_as_stream(
        cls,
        file_path: PathLike[str] | str,
        *,
        strip: bool = DEFAULT_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
        chunk_size: int = DEFAULT_CHUNK_SIZE,
    ) -> Iterator[list[str]]:
        """
        Read a text file as a stream of line chunks.

        This method yields chunks of lines from the file, allowing for
        memory-efficient processing of large files. Each chunk contains
        up to chunk_size lines. Uses a sliding window approach to handle
        footer row skipping without loading the entire file into memory.

        Args:
            file_path: Path to the text file
            strip: Whether to strip whitespace from lines (default: True)
            encoding: File encoding to use (default: 'utf-8')
            skip_header_rows: Number of rows to skip from the start (default: 0)
            skip_footer_rows: Number of rows to skip from the end (default: 0)
            chunk_size: Number of lines per chunk (default: 500)

        Yields:
            List[str]: Chunks of lines from the file

        Raises:
            SplurgeFileNotFoundError: If the specified file doesn't exist
            SplurgeFilePermissionError: If there are permission issues
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding
            SplurgePathValidationError: If file path validation fails
        """
        # Ensure minimum chunk size
        chunk_size = max(chunk_size, cls.DEFAULT_MIN_CHUNK_SIZE)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True,
        )

        with safe_file_operation(validated_path, encoding=encoding, mode=cls.DEFAULT_MODE) as stream:
            # Skip header rows
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return

            # Use a sliding window to handle footer skipping efficiently
            if skip_footer_rows > 0:
                # Buffer to hold the last skip_footer_rows lines
                buffer: deque[str] = deque(maxlen=skip_footer_rows + 1)
                current_chunk: list[str] = []

                for line in stream:
                    processed_line = line.strip() if strip else line.rstrip("\n")

                    # Add current line to buffer
                    buffer.append(processed_line)

                    # Wait until the buffer is full (skip_footer_rows + 1 lines) before processing lines.
                    # This ensures we have enough lines to reliably identify and skip the footer rows at the end.
                    if len(buffer) < skip_footer_rows + 1:
                        continue

                    # Once the buffer contains more than skip_footer_rows lines, the oldest line (removed with popleft)
                    # is guaranteed not to be part of the footer and can be safely processed and added to the current chunk.
                    safe_line = buffer.popleft()
                    current_chunk.append(safe_line)

                    # Yield chunk when it reaches the desired size
                    if len(current_chunk) >= chunk_size:
                        yield current_chunk
                        current_chunk = []

                # At the end, the buffer contains exactly the footer rows to skip
                # All other lines have already been processed and yielded

                # Yield any remaining lines in the final chunk
                if current_chunk:
                    yield current_chunk
            else:
                # No footer skipping needed - simple streaming
                chunk: list[str] = []

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

    @classmethod
    def read(
        cls,
        file_path: PathLike[str] | str,
        *,
        strip: bool = DEFAULT_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
    ) -> list[str]:
        """
        Read the entire contents of a text file into a list of strings.

        This method reads the complete file into memory, with options to
        strip whitespace from each line and skip header/footer rows.

        Args:
            file_path: Path to the text file
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
            SplurgePathValidationError: If file path validation fails
        """
        # Validate file path
        validated_path = PathValidator.validate_path(
            Path(file_path),
            must_exist=True,
            must_be_file=True,
            must_be_readable=True,
        )

        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        with safe_file_operation(validated_path, encoding=encoding, mode=cls.DEFAULT_MODE) as stream:
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return []

            try:
                if skip_footer_rows > 0:
                    # Buffer to hold the last skip_footer_rows + 1 lines
                    buffer = deque(maxlen=skip_footer_rows + 1)
                    result: list[str] = []

                    for line in stream:
                        processed_line = line.strip() if strip else line.rstrip("\n")

                        # Add current line to buffer
                        buffer.append(processed_line)

                        # Wait until the buffer is full (skip_footer_rows + 1 lines) before processing lines.
                        # This ensures we have enough lines to reliably identify and skip the footer rows at the end.
                        if len(buffer) < skip_footer_rows + 1:
                            continue

                        # Once the buffer contains more than skip_footer_rows lines, the oldest line (removed with popleft)
                        # is guaranteed not to be part of the footer and can be safely processed and added to the result.
                        safe_line = buffer.popleft()
                        result.append(safe_line)

                    # At the end, the buffer contains exactly the footer rows to skip
                    # All other lines have already been processed and added to result
                    return result
                result: list[str] = []
                for line in stream:
                    processed_line = line.strip() if strip else line.rstrip("\n")
                    result.append(processed_line)
                return result
            except UnicodeDecodeError as e:
                msg = f"Encoding error reading file: {validated_path}"
                raise SplurgeFileEncodingError(
                    msg,
                    details=str(e),
                )
