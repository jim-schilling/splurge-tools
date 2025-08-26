"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from os import PathLike
from typing import Iterator

from splurge_tools.string_tokenizer import StringTokenizer
from splurge_tools.text_file_helper import TextFileHelper
from splurge_tools.exceptions import SplurgeParameterError
from splurge_tools.tabular_data_model import TabularDataModel


class DsvHelper:
    """
    Utility class for working with DSV (Delimited String Values) files.

    Provides methods to parse DSV content from strings, lists of strings, and files.
    Supports configurable delimiters, text bookends, and whitespace handling options.
    """

    DEFAULT_CHUNK_SIZE = 500  # Default chunk size for streaming operations
    DEFAULT_ENCODING = "utf-8"  # Default text encoding for file operations
    DEFAULT_SKIP_HEADER_ROWS = 0  # Default number of header rows to skip
    DEFAULT_SKIP_FOOTER_ROWS = 0  # Default number of footer rows to skip
    DEFAULT_MIN_CHUNK_SIZE = 100
    DEFAULT_STRIP = True
    DEFAULT_BOOKEND_STRIP = True

    @staticmethod
    def parse(
        content: str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP
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
            SplurgeParameterError: If delimiter is empty or None.

        Example:
            >>> DsvHelper.parse("a,b,c", delimiter=",")
            ['a', 'b', 'c']
            >>> DsvHelper.parse('"a","b","c"', delimiter=",", bookend='"')
            ['a', 'b', 'c']
        """
        if delimiter is None or delimiter == "":
            raise SplurgeParameterError("delimiter cannot be empty or None")

        tokens: list[str] = StringTokenizer.parse(content, delimiter=delimiter, strip=strip)

        if bookend:
            tokens = [
                StringTokenizer.remove_bookends(token, bookend=bookend, strip=bookend_strip)
                for token in tokens
            ]

        return tokens

    @classmethod
    def parses(
        cls,
        content: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP
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
            SplurgeParameterError: If delimiter is empty or None.
            SplurgeParameterError: If content is not a list of strings.

        Example:
            >>> DsvHelper.parses(["a,b,c", "d,e,f"], delimiter=",")
            [['a', 'b', 'c'], ['d', 'e', 'f']]
        """
        if not isinstance(content, list):
            raise SplurgeParameterError("content must be a list")
        
        if not all(isinstance(item, str) for item in content):
            raise SplurgeParameterError("content must be a list of strings")

        return [
            cls.parse(item, delimiter=delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip)
            for item in content
        ]

    @classmethod
    def parse_file(
        cls,
        file_path: PathLike[str] | str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS
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
            SplurgeParameterError: If delimiter is empty or None.
            SplurgeFileNotFoundError: If the file does not exist.
            SplurgeFilePermissionError: If the file cannot be accessed.
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding.

        Example:
            >>> DsvHelper.parse_file("data.csv", delimiter=",")
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
            delimiter=delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip
        )

    @classmethod
    def _process_stream_chunk(
        cls,
        chunk: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP
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
            list[list[str]]: Parsed rows
        """
        return cls.parses(
            chunk,
            delimiter=delimiter,
            strip=strip,
            bookend=bookend,
            bookend_strip=bookend_strip
        )

    @classmethod
    def parse_stream(
        cls,
        file_path: PathLike[str] | str,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
        bookend: str | None = None,
        bookend_strip: bool = DEFAULT_BOOKEND_STRIP,
        encoding: str = DEFAULT_ENCODING,
        skip_header_rows: int = DEFAULT_SKIP_HEADER_ROWS,
        skip_footer_rows: int = DEFAULT_SKIP_FOOTER_ROWS,
        chunk_size: int = DEFAULT_CHUNK_SIZE
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
            SplurgeParameterError: If delimiter is empty or None.
            SplurgeFileNotFoundError: If the file does not exist.
            SplurgeFilePermissionError: If the file cannot be accessed.
            SplurgeFileEncodingError: If the file cannot be decoded with the specified encoding.
        """
        if delimiter is None or delimiter == "":
            raise SplurgeParameterError("delimiter cannot be empty or None")

        chunk_size = max(chunk_size, cls.DEFAULT_MIN_CHUNK_SIZE)
        skip_header_rows = max(skip_header_rows, cls.DEFAULT_SKIP_HEADER_ROWS)
        skip_footer_rows = max(skip_footer_rows, cls.DEFAULT_SKIP_FOOTER_ROWS)

        # Use TextFileHelper.read_as_stream for consistent error handling
        for chunk in TextFileHelper.read_as_stream(
            file_path,
            encoding=encoding,
            skip_header_rows=skip_header_rows,
            skip_footer_rows=skip_footer_rows,
            chunk_size=chunk_size
        ):
            yield cls._process_stream_chunk(
                chunk,
                delimiter=delimiter,
                strip=strip,
                bookend=bookend,
                bookend_strip=bookend_strip
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
