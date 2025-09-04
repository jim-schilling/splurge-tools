"""
string_tokenizer.py

A utility module for string tokenization operations.
Provides methods to split strings into tokens and manipulate string boundaries.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from splurge_tools.exceptions import SplurgeParameterError


class StringTokenizer:
    """
    Utility class for string tokenization operations.

    This class provides methods to:
    - Split strings into tokens based on delimiters
    - Process multiple strings into token lists
    - Remove matching characters from string boundaries
    """

    DEFAULT_STRIP = True

    @staticmethod
    def parse(
        content: str | None,
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
    ) -> list[str]:
        """
        Split a string into tokens based on a delimiter.

        Args:
            content (str | None): The input string to tokenize
            delimiter (str): The character(s) to split the string on
            strip (bool, optional): Whether to strip whitespace from tokens. Defaults to True.

        Returns:
            list[str]: List of tokens, preserving empty tokens

        Raises:
            SplurgeParameterError: If delimiter is empty or None

        Example:
            >>> StringTokenizer.parse("a,b,c", delimiter=",")
            ['a', 'b', 'c']
            >>> StringTokenizer.parse("a,,c", delimiter=",")
            ['a', '', 'c']
        """
        if content is None:
            return []

        if delimiter is None or delimiter == "":
            msg = "delimiter cannot be empty or None"
            raise SplurgeParameterError(msg)

        if strip and not content.strip():
            return []

        result: list[str] = content.split(delimiter)
        if strip:
            result = [token.strip() for token in result]
        return result

    @classmethod
    def parses(
        cls,
        content: list[str],
        *,
        delimiter: str,
        strip: bool = DEFAULT_STRIP,
    ) -> list[list[str]]:
        """
        Process multiple strings into lists of tokens.

        Args:
            content (list[str]): List of strings to tokenize
            delimiter (str): The character(s) to split each string on
            strip (bool, optional): Whether to strip whitespace from tokens. Defaults to True.

        Returns:
            list[list[str]]: List of token lists, one for each input string

        Raises:
            SplurgeParameterError: If delimiter is empty or None

        Example:
            >>> StringTokenizer.parses(["a,b", "c,d"], delimiter=",")
            [['a', 'b'], ['c', 'd']]
        """
        if delimiter is None or delimiter == "":
            msg = "delimiter cannot be empty or None"
            raise SplurgeParameterError(msg)

        return [cls.parse(text, delimiter=delimiter, strip=strip) for text in content]

    @staticmethod
    def remove_bookends(
        content: str,
        *,
        bookend: str,
        strip: bool = DEFAULT_STRIP,
    ) -> str:
        """
        Remove matching characters from both ends of a string.

        Args:
            content (str): The input string to process
            bookend (str): The character(s) to remove from both ends
            strip (bool, optional): Whether to strip whitespace first. Defaults to True.

        Returns:
            str: The string with matching bookends removed

        Raises:
            SplurgeParameterError: If bookend is empty or None

        Example:
            >>> StringTokenizer.remove_bookends("'hello'", bookend="'")
            'hello'
        """
        if bookend is None or bookend == "":
            msg = "bookend cannot be empty or None"
            raise SplurgeParameterError(msg)

        value: str = content.strip() if strip else content
        if value.startswith(bookend) and value.endswith(bookend) and len(value) > 2 * len(bookend) - 1:
            return value[len(bookend) : -len(bookend)]
        return value
