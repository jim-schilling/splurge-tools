"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""

from os import PathLike
from collections import deque
from typing import Optional, Union, Iterator

from splurge_tools.string_tokenizer import StringTokenizer
from splurge_tools.text_file_helper import TextFileHelper
from splurge_tools.tabular_data_model import TabularDataModel


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
        bookend: Optional[str] = None,
        bookend_strip: bool = True
    ) -> list[str]:
        """
        Parse a string into a list of strings.

        Args:
            content (str): The string to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (Optional[str]): The bookend to use for text fields.
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
        if not delimiter:
            raise ValueError("Delimiter must not be empty or None.")

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
        bookend: Optional[str] = None,
        bookend_strip: bool = True
    ) -> list[list[str]]:
        """
        Parse a list of strings into a list of lists of strings.

        Args:
            content (list[str]): The list of strings to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (Optional[str]): The bookend to use for text fields.
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
        if not isinstance(content, list) or not all(isinstance(item, str) for item in content):
            raise TypeError("Content must be a list of strings.")

        return [
            cls.parse(item, delimiter, strip=strip, bookend=bookend, bookend_strip=bookend_strip)
            for item in content
        ]

    @classmethod
    def parse_file(
        cls,
        file_path: Union[PathLike, str],
        delimiter: str,
        *,
        strip: bool = True,
        bookend: Optional[str] = None,
        bookend_strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0
    ) -> list[list[str]]:
        """
        Parse a file into a list of lists of strings.

        Args:
            file_path (Union[PathLike, str]): The path to the file to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (Optional[str]): The bookend to use for text fields.
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
        lines: list[str] = TextFileHelper.load(
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
    def parse_stream(
        cls,
        file_path: Union[PathLike, str],
        delimiter: str,
        *,
        strip: bool = True,
        bookend: Optional[str] = None,
        bookend_strip: bool = True,
        encoding: str = "utf-8",
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0,
        chunk_size: int = 100
    ) -> Iterator[list[list[str]]]:
        """
        Stream-parse a DSV file in chunks of lines.

        Args:
            file_path (Union[PathLike, str]): The path to the file to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (Optional[str]): The bookend to use for text fields.
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
        if not delimiter:
            raise ValueError("Delimiter must not be empty or None.")
        if chunk_size < 100:
            raise ValueError("chunk_size must be at least 100.")
        if skip_header_rows < 0 or skip_footer_rows < 0:
            raise ValueError("skip_header_rows and skip_footer_rows must be >= 0.")

        with open(file_path, "r", encoding=encoding) as stream:
            # Skip header rows
            for _ in range(skip_header_rows):
                if not stream.readline():
                    return

            # If skipping footer rows, use a buffer
            if skip_footer_rows > 0:
                buffer = deque()  
                chunk = []  
                for line in stream:
                    buffer.append(line.strip() if strip else line.rstrip("\n"))
                    if len(buffer) > skip_footer_rows:
                        chunk.append(buffer.popleft())
                        if len(chunk) == chunk_size:
                            yield cls.parses(
                                chunk,
                                delimiter,
                                strip=strip,
                                bookend=bookend,
                                bookend_strip=bookend_strip
                            )
                            chunk = []
                # Yield any remaining chunk (excluding footer rows)
                if chunk:
                    yield cls.parses(
                        chunk,
                        delimiter,
                        strip=strip,
                        bookend=bookend,
                        bookend_strip=bookend_strip
                    )
            else:
                chunk = []
                for line in stream:
                    chunk.append(line.strip() if strip else line.rstrip("\n"))
                    if len(chunk) == chunk_size:
                        yield cls.parses(
                            chunk,
                            delimiter,
                            strip=strip,
                            bookend=bookend,
                            bookend_strip=bookend_strip
                        )
                        chunk = []
                if chunk:
                    yield cls.parses(
                        chunk,
                        delimiter,
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
        multi_row_headers: int = 1,
        skip_empty_rows: bool = True
    ) -> list[dict[str, str]]:
        """
        Generate a simple data profile from parsed DSV data.

        Args:
            data (list[list[str]]): Parsed DSV data (including header row).
            header_rows (int): Number of header rows (default: 1).
            multi_row_headers (int): Number of rows to merge for column names (default: 1).
            skip_empty_rows (bool): Whether to skip empty rows (default: True).

        Returns:
            list[dict[str, str]]: List of dicts with column name and inferred datatype.
                Example: [{"name": "Column_1", "datatype": "STRING"}, ...]
        """
        model = TabularDataModel(
            data,
            header_rows=header_rows,
            multi_row_headers=multi_row_headers,
            skip_empty_rows=skip_empty_rows
        )

        profile: list[dict[str, str]] = []
        for col in model.column_names:
            dtype = model.column_type(col)
            profile.append({"name": col, "datatype": dtype.name.upper()})
        return profile
