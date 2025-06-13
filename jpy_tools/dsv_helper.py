"""
A utility module for working with DSV (Delimited String Values) files.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""
from os import PathLike
from typing import Union
from jpy_tools.string_tokenizer import StringTokenizer

class DSVHelper:
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
    def parse(content: str, delimiter: str, strip: bool = True, bookend: str = None, bookend_strip: bool = True) -> list[str]:
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
            >>> DSVHelper.parse("a,b,c", ",")
            ['a', 'b', 'c']
            >>> DSVHelper.parse('"a","b","c"', ",", bookend='"')
            ['a', 'b', 'c']
        """
        # First parse the content into tokens
        tokens = StringTokenizer.parse(content, delimiter, strip)
        
        # Then remove bookends if specified
        if bookend:
            tokens = [StringTokenizer.remove_bookends(token, bookend, bookend_strip) for token in tokens]
            
        return tokens
    
    @staticmethod
    def parses(content: list[str], delimiter: str, strip: bool = True, bookend: str = None, bookend_strip: bool = True) -> list[list[str]]:
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
            >>> DSVHelper.parses(["a,b,c", "d,e,f"], ",")
            [['a', 'b', 'c'], ['d', 'e', 'f']]
        """
        return [DSVHelper.parse(item, delimiter, strip, bookend, bookend_strip) for item in content]

    @staticmethod
    def parse_file(file_path: Union[PathLike, str], delimiter: str, strip: bool = True, bookend: str = None, bookend_strip: bool = True) -> list[list[str]]:
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
            >>> DSVHelper.parse_file("data.csv", ",")
            [['header1', 'header2'], ['value1', 'value2']]
        """
        with open(file_path, 'r') as file:
            content = file.readlines()
        return DSVHelper.parses(content, delimiter, strip, bookend, bookend_strip)