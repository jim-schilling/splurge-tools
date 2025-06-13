"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""
import re
from os import PathLike
from typing import Union
from jpy_tools.string_tokenizer import StringTokenizer
from jpy_tools.text_file_helper import TextFileHelper

class DsvHelper:
    """A utility class for working with DSV (Delimited String Values) files.
    
    This class provides methods to parse DSV content from strings, lists of strings,
    and files. It supports configurable delimiters, text bookends, and whitespace
    handling options.
    
    Features:
        - Parse single strings into token lists
        - Parse multiple strings into lists of token lists
        - Parse files directly into lists of token lists
        - Configurable delimiter and text bookend handling
        - Optional whitespace stripping
    """
    @staticmethod
    def parse(
        content: str, 
        delimiter: str, 
        strip: bool = True, 
        bookend: str = None, 
        bookend_strip: bool = True
    ) -> list[str]:
        """Parse a string into a list of strings.

        Args:
            content (str): The string to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str): The bookend to use for text fields.
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
        # First parse the content into tokens
        tokens = StringTokenizer.parse(content, delimiter, strip)
        
        # Then remove bookends if specified
        if bookend:
            tokens = [StringTokenizer.remove_bookends(token, bookend, bookend_strip) for token in tokens]
            
        return tokens
    
    @staticmethod
    def parses(
        content: list[str], 
        delimiter: str, 
        strip: bool = True, 
        bookend: str = None, 
        bookend_strip: bool = True
    ) -> list[list[str]]:
        """Parse a list of strings into a list of lists of strings.

        Args:
            content (list[str]): The list of strings to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str): The bookend to use for text fields.
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
        return [DsvHelper.parse(item, delimiter, strip, bookend, bookend_strip) for item in content]

    @staticmethod
    def parse_file(
        file_path: Union[PathLike, str], 
        delimiter: str, 
        strip: bool = True, 
        bookend: str = None, 
        bookend_strip: bool = True,
        encoding: str = 'utf-8',
        skip_header_rows: int = 0,
        skip_footer_rows: int = 0
    ) -> list[list[str]]:
        """Parse a file into a list of lists of strings.

        Args:
            file_path (str): The path to the file to parse.
            delimiter (str): The delimiter to use.
            strip (bool): Whether to strip whitespace from the strings.
            bookend (str): The bookend to use for text fields.
            bookend_strip (bool): Whether to strip whitespace from the bookend.

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
        return DsvHelper.parses(
            TextFileHelper.load(file_path, encoding=encoding, skip_header_rows=skip_header_rows, skip_footer_rows=skip_footer_rows), 
            delimiter, 
            strip, 
            bookend, 
            bookend_strip
        )
    
    def __init__(
            self, 
            data: list[list[str]],
            header_rows: int = 1,
            column_names_span: int = 1,
            skip_empty_rows: bool = True
    ):
        if data is None or len(data) == 0:
            raise ValueError("Data is required")
        if header_rows < 0:
            raise ValueError("Header rows must be greater than or equal to 0")
        if header_rows > 0 and column_names_span > header_rows:
            raise ValueError("Column names span must be less than or equal to header rows")
        if header_rows > 0 and column_names_span == 0:
            raise ValueError("Column names span must be greater than 0 if header rows are greater than 0")
        
        self._raw_data = data
        self._header_rows = header_rows
        self._column_names_span = column_names_span
        self._header_data = data[:header_rows] if header_rows > 0 else []
        self._data = self._normalize_data_model(data[header_rows:], skip_empty_rows) if header_rows > 0 else self._normalize_data_model(data, skip_empty_rows)
        self._header_columns = len(self._header_data[0]) if len(self._header_data) > 0 else 0
        self._columns = len(self._data[0]) if len(self._data) > 0 else 0
        self._rows = len(self._data) if len(self._data) > 0 else 0
        
        # Get column names from header data
        if len(self._header_data) > 0:
            # For multi-row headers, combine the first column_names_span rows
            self._column_names = []
            for i in range(min(column_names_span, len(self._header_data))):
                row = self._header_data[i]
                # Extend column names if needed
                while len(self._column_names) < len(row):
                    self._column_names.append('')
                # Combine with existing names
                for j, name in enumerate(row):
                    if self._column_names[j]:
                        self._column_names[j] = f"{self._column_names[j]}_{name}"
                    else:
                        self._column_names[j] = name
        else:
            self._column_names = []
            
        # strip away 2 or more spaces from the column names
        self._column_names = [re.sub(r'\s+', ' ', name).strip() for name in self._column_names]
        
        # If no headers, generate column names
        if len(self._column_names) == 0:
            self._column_names = [f"column_{i}" for i in range(self._columns)]
        # ensure column_names matches the number of columns and replace empty names
        while len(self._column_names) < self._columns:
            self._column_names.append(f"column_{len(self._column_names)}")
        # Replace any empty column names with column_n
        self._column_names = [name if name else f"column_{i}" for i, name in enumerate(self._column_names)]
            
        self._column_index_map = {name: i for i, name in enumerate(self._column_names)}    
    
    
    