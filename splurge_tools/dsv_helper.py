"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from os import PathLike
from collections import deque
from typing import Iterator

from splurge_tools.string_tokenizer import StringTokenizer
from splurge_tools.text_file_helper import TextFileHelper
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.validation_utils import Validator
from splurge_tools.common_utils import validate_data_structure, create_error_context


# Module-level constants for DSV parsing
_DEFAULT_CHUNK_SIZE = 100  # Default chunk size for streaming operations
_DEFAULT_ENCODING = "utf-8"  # Default text encoding for file operations
_DEFAULT_HEADER_ROWS = 0  # Default number of header rows to skip
_DEFAULT_FOOTER_ROWS = 0  # Default number of footer rows to skip


class DsvHelper:
    """
    Utility class for working with DSV (Delimited String Values) files.

    Provides methods to parse DSV content from strings, lists of strings, and files.
    Supports configurable delimiters, text bookends, and whitespace handling options.
    """

    @staticmethod
    def parse(
        content: str,
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True
    ) -> list[str]:
        """
        Parse a string into a list of strings.

        Args:
            content (str): The string to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str | None): The bookend to use for text fields.
            bookend_strip (bool): Whether to strip whitespace from the bookend.

        Returns:
            list[str]: The list of strings.

        Raises:
            ValueError: If delimiter is empty or None.

        Example:
            >>> DsvHelper.parse("a,b,c", ",")
            ['a', 'b', 'c']
            >>> DsvHelper.parse('"a","b","c"', ",", bookend='"')
            ['a', 'b', 'c']
        """
        delimiter = Validator.is_delimiter(delimiter)

        tokens: list[str] = StringTokenizer.parse(content, delimiter, strip=strip)

        if bookend:
            tokens = [
                StringTokenizer.remove_bookends(token, bookend, strip=bookend_strip)
                for token in tokens
            ]

        return tokens

    @classmethod
    def parses(
        cls,
        content: list[str],
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True
    ) -> list[list[str]]:
        """
        Parse a list of strings into a list of lists of strings.

        Args:
            content (list[str]): The list of strings to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str | None): The bookend to use for text fields.
            bookend_strip (bool): Whether to strip whitespace from the bookend.

        Returns:
            list[list[str]]: The list of lists of strings.

        Raises:
            ValueError: If delimiter is empty or None.
            TypeError: If content is not a list of strings.

        Example:
            >>> DsvHelper.parses(["a,b,c", "d,e,f"], ",")
            [['a', 'b', 'c'], ['d', 'e', 'f']]
        """
        content = validate_data_structure(content, expected_type=list, param_name="content")
        if not all(isinstance(item, str) for item in content):
            raise TypeError("Content must be a list of strings.")

        return [
            cls.parse(item, delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip)
            for item in content
        ]

    @classmethod
    def parse_file(
        cls,
        file_path: PathLike[str] | str,
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True,
        encoding: str = _DEFAULT_ENCODING,
        skip_header_rows: int = _DEFAULT_HEADER_ROWS,
        skip_footer_rows: int = _DEFAULT_FOOTER_ROWS
    ) -> list[list[str]]:
        """
        Parse a file into a list of lists of strings.

        Args:
            file_path (PathLike[str] | str): The path to the file to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str | None): The bookend to use for text fields.
            bookend_strip (bool): Whether to strip whitespace from the bookend.
            encoding (str): The file encoding.
            skip_header_rows (int): Number of header rows to skip.
            skip_footer_rows (int): Number of footer rows to skip.

        Returns:
            list[list[str]]: The list of lists of strings.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If delimiter is empty or None.
            PermissionError: If the file cannot be accessed.

        Example:
            >>> DsvHelper.parse_file("data.csv", ",")
            [['header1', 'header2'], ['value1', 'value2']]
        """
        lines: list[str] = TextFileHelper.read(
            file_path,
            encoding=encoding,
            skip_header_rows=skip_header_rows,
            skip_footer_rows=skip_footer_rows
        )

        return cls.parses(
            lines,
            delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip
        )

    @classmethod
    def _process_stream_chunk(
        cls,
        chunk: list[str],
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True
    ) -> list[list[str]]:
        """
        Process a chunk of lines from the stream.
        
        Args:
            chunk: List of lines to process
            delimiter: Delimiter to use for parsing
            strip: Whether to strip whitespace
            bookend: Bookend character for text fields
            bookend_strip: Whether to strip whitespace from bookends
            
        Returns:
            List of parsed rows
        """
        return cls.parses(
            chunk,
            delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip
        )

    @classmethod
    def _handle_footer_skipping(
        cls,
        stream: Iterator[str],
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True,
        skip_footer_rows: int = 0,
        chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> Iterator[list[list[str]]]:
        """
        Handle streaming with footer row skipping.
        
        Args:
            stream: File stream iterator
            delimiter: Delimiter to use for parsing
            strip: Whether to strip whitespace
            bookend: Bookend character for text fields
            bookend_strip: Whether to strip whitespace from bookends
            skip_footer_rows: Number of footer rows to skip
            chunk_size: Size of chunks to process
            
        Yields:
            Chunks of parsed rows
        """
        buffer: deque[str] = deque()
        chunk = []
        
        for line in stream:
            processed_line = line.strip() if strip else line.rstrip("\n")
            buffer.append(processed_line)
            
            if len(buffer) > skip_footer_rows:
                chunk.append(buffer.popleft())
                if len(chunk) == chunk_size:
                    yield cls._process_stream_chunk(
                        chunk,
                        delimiter,
                        strip=strip,
                        bookend=bookend,
                        bookend_strip=bookend_strip
                    )
                    chunk = []
        
        # Yield any remaining chunk (excluding footer rows)
        if chunk:
            yield cls._process_stream_chunk(
                chunk,
                delimiter,
                strip=strip,
                bookend=bookend,
                bookend_strip=bookend_strip
            )

    @classmethod
    def _handle_simple_streaming(
        cls,
        stream: Iterator[str],
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True,
        chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> Iterator[list[list[str]]]:
        """
        Handle simple streaming without footer skipping.
        
        Args:
            stream: File stream iterator
            delimiter: Delimiter to use for parsing
            strip: Whether to strip whitespace
            bookend: Bookend character for text fields
            bookend_strip: Whether to strip whitespace from bookends
            chunk_size: Size of chunks to process
            
        Yields:
            Chunks of parsed rows
        """
        chunk = []
        
        for line in stream:
            processed_line = line.strip() if strip else line.rstrip("\n")
            chunk.append(processed_line)
            
            if len(chunk) == chunk_size:
                yield cls._process_stream_chunk(
                    chunk,
                    delimiter,
                    strip=strip,
                    bookend=bookend,
                    bookend_strip=bookend_strip
                )
                chunk = []
        
        if chunk:
            yield cls._process_stream_chunk(
                chunk,
                delimiter,
                strip=strip,
                bookend=bookend,
                bookend_strip=bookend_strip
            )

    @classmethod
    def parse_stream(
        cls,
        file_path: PathLike[str] | str,
        delimiter: str,
        *,
        strip: bool = True,
        bookend: str | None = None,
        bookend_strip: bool = True,
        encoding: str = _DEFAULT_ENCODING,
        skip_header_rows: int = _DEFAULT_HEADER_ROWS,
        skip_footer_rows: int = _DEFAULT_FOOTER_ROWS,
        chunk_size: int = _DEFAULT_CHUNK_SIZE
    ) -> Iterator[list[list[str]]]:
        """
        Stream-parse a DSV file in chunks of lines.

        Args:
            file_path (PathLike[str] | str): The path to the file to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str | None): The bookend to use for text fields.
            bookend_strip (bool): Whether to strip whitespace from the bookend.
            encoding (str): The file encoding.
            skip_header_rows (int): Number of header rows to skip.
            skip_footer_rows (int): Number of footer rows to skip.
            chunk_size (int): Number of lines per chunk (default: 100).

        Yields:
            list[list[str]]: Parsed rows for each chunk.

        Raises:
            FileNotFoundError: If the file does not exist.
            ValueError: If delimiter is empty or None.
            PermissionError: If the file cannot be accessed.
        """
        delimiter = Validator.is_delimiter(delimiter)
        chunk_size = Validator.is_positive_integer(chunk_size, "chunk_size", min_value=100)
        skip_header_rows = Validator.is_non_negative_integer(skip_header_rows, "skip_header_rows")
        skip_footer_rows = Validator.is_non_negative_integer(skip_footer_rows, "skip_footer_rows")

        with open(file_path, "r", encoding=encoding) as stream:
            # Skip header rows
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return

            # Choose appropriate streaming method based on footer skipping
            if skip_footer_rows > 0:
                yield from cls._handle_footer_skipping(
                    stream,
                    delimiter,
                    strip=strip,
                    bookend=bookend,
                    bookend_strip=bookend_strip,
                    skip_footer_rows=skip_footer_rows,
                    chunk_size=chunk_size
                )
            else:
                yield from cls._handle_simple_streaming(
                    stream,
                    delimiter,
                    strip=strip,
                    bookend=bookend,
                    bookend_strip=bookend_strip,
                    chunk_size=chunk_size
                )

    @classmethod
    def profile_columns(
        cls,
        data: list[list[str]],
        *,
        header_rows: int = 1,
        skip_empty_rows: bool = True
    ) -> list[dict[str, str]]:
        """
        Generate a simple data profile from parsed DSV data.

        Args:
            data (list[list[str]]): Parsed DSV data (including header row).
            header_rows (int): Number of header rows (default: 1).
            skip_empty_rows (bool): Whether to skip empty rows (default: True).

        Returns:
            list[dict[str, str]]: List of dicts with column name and inferred datatype.
                Example: [{"name": "Column_1", "datatype": "STRING"}, ...]
        """
        model = TabularDataModel(
            data,
            header_rows=header_rows,
            skip_empty_rows=skip_empty_rows
        )

        profile: list[dict[str, str]] = []
        for col in model.column_names:
            dtype = model.column_type(col)
            profile.append({"name": col, "datatype": dtype.name.upper()})
        return profile
