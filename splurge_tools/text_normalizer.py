"""
A utility module for text normalization operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This software is licensed under the MIT License.
"""

import re
import unicodedata
from functools import wraps
from typing import Any, Callable, Pattern

from splurge_tools.case_helper import CaseHelper


def handle_empty_value(
    func: Callable[[str, Any], str]
) -> Callable[[str, Any], str]:
    """Decorator to handle empty value checks for normalization methods."""
    @wraps(func)
    def wrapper(value: str, *args: Any, **kwargs: Any) -> str:
        if value is None or not value:
            return ""
        return func(value, *args, **kwargs)
    return wrapper


class TextNormalizer:
    """
    A utility class for text normalization operations.

    This class provides methods to:
    - Remove diacritics (accents)
    - Normalize whitespace
    - Remove special characters
    - Normalize line endings
    - Convert to ASCII
    - Remove control characters
    - Normalize quotes
    - Normalize dashes
    - Normalize spaces
    - Normalize case

    All methods support an optional normalize parameter (default: True) that:
    - Handles empty values
    - Preserves original string if no changes needed
    """

    _WHITESPACE_PATTERN: Pattern = re.compile(r"\s+")
    _CONTROL_CHARS_PATTERN: Pattern = re.compile(r"[\x00-\x1f\x7f-\x9f]")
    _SPECIAL_CHARS_PATTERN: Pattern = re.compile(r"[^\w\s-]")

    @classmethod
    @handle_empty_value
    def remove_accents(
        cls,
        value: str
    ) -> str:
        """
        Remove accents from text.

        Args:
            value: Input string to normalize

        Returns:
            String with diacritical marks removed

        Example:
            "café" -> "cafe"
            "résumé" -> "resume"
        """
        if value is None:
            return ""
        return "".join(
            c
            for c in unicodedata.normalize("NFKD", value)
            if not unicodedata.combining(c)
        )

    @classmethod
    @handle_empty_value
    def normalize_whitespace(
        cls,
        value: str,
        preserve_newlines: bool = False
    ) -> str:
        """
        Normalize whitespace in text.

        Args:
            value: Input string to normalize
            preserve_newlines: Whether to preserve newline characters

        Returns:
            String with normalized whitespace

        Example:
            "hello   world" -> "hello world"
            "hello\n\nworld" -> "hello world" (if preserve_newlines=False)
        """
        if preserve_newlines:
            value = re.sub(r"[^\S\n]+", " ", value)
            value = re.sub(r"\r\n|\r", "\n", value)
            value = re.sub(r"\n\s*\n", "\n\n", value)
            value = re.sub(r" +(\n)", r"\1", value)
            value = re.sub(r"(\n) +", r"\1", value)
        else:
            value = cls._WHITESPACE_PATTERN.sub(" ", value)
        return value.strip()

    @classmethod
    @handle_empty_value
    def remove_special_chars(
        cls,
        value: str,
        keep_chars: str = ""
    ) -> str:
        """
        Remove special characters from text.

        Args:
            value: Input string to normalize
            keep_chars: Additional characters to preserve

        Returns:
            String with special characters removed

        Example:
            "hello@world!" -> "helloworld"
            "hello@world!" (keep_chars="@") -> "hello@world"
        """
        if value is None:
            return ""
        pattern: str = f"[^\\w\\s{re.escape(keep_chars)}]"
        return re.sub(pattern, "", value)

    @classmethod
    @handle_empty_value
    def normalize_line_endings(
        cls,
        value: str,
        line_ending: str = "\n"
    ) -> str:
        """
        Normalize line endings in text.

        Args:
            value: Input string to normalize
            line_ending: Desired line ending character

        Returns:
            String with normalized line endings

        Example:
            "hello\r\nworld" -> "hello\nworld"
        """
        return re.sub(r"\r\n|\r|\n", line_ending, value)

    @classmethod
    @handle_empty_value
    def to_ascii(
        cls,
        value: str,
        *,
        replacement: str = ""
    ) -> str:
        """
        Convert text to ASCII, replacing non-ASCII characters.

        Args:
            value: Input string to normalize
            replacement: Character to use for non-ASCII characters

        Returns:
            ASCII string

        Example:
            "café" -> "cafe"
            "résumé" -> "resume"
        """
        value = cls.remove_accents(value)
        return (
            value.encode("ascii", "replace").decode("ascii").replace("?", replacement)
        )

    @classmethod
    @handle_empty_value
    def remove_control_chars(
        cls,
        value: str
    ) -> str:
        """
        Remove control characters from text.

        Args:
            value: Input string to normalize

        Returns:
            String with control characters removed

        Example:
            "hello\x00world" -> "helloworld"
        """
        return cls._CONTROL_CHARS_PATTERN.sub("", value)

    @classmethod
    @handle_empty_value
    def normalize_quotes(
        cls,
        value: str,
        *,
        quote_char: str = '"'
    ) -> str:
        """
        Normalize quote characters in text.

        Args:
            value: Input string to normalize
            quote_char: Desired quote character

        Returns:
            String with normalized quotes

        Example:
            'hello "world"' -> 'hello "world"'
            "hello 'world'" -> 'hello "world"'
            "hello 'world's" -> 'hello "world's"'
        """
        if value is None:
            return ""
        temp: str = re.sub(r"(\w)'(\w)", r"\1§APOS§\2", value)
        temp = temp.replace('"', quote_char).replace("'", quote_char)
        result: str = temp.replace("§APOS§", "'")
        return result

    @classmethod
    @handle_empty_value
    def normalize_dashes(
        cls,
        value: str,
        *,
        dash_char: str = "-"
    ) -> str:
        """
        Normalize dash characters in text.

        Args:
            value: Input string to normalize
            dash_char: Desired dash character

        Returns:
            String with normalized dashes

        Example:
            "hello–world" -> "hello-world"
            "hello—world" -> "hello-world"
        """
        return re.sub(r"[–—]", dash_char, value)

    @classmethod
    @handle_empty_value
    def normalize_spaces(
        cls,
        value: str
    ) -> str:
        """
        Normalize space characters in text.

        Args:
            value: Input string to normalize

        Returns:
            String with normalized spaces

        Example:
            "hello\u00a0world" -> "hello world"
        """
        return " ".join(value.split())

    @classmethod
    @handle_empty_value
    def normalize_case(
        cls,
        value: str,
        *,
        case: str = "lower"
    ) -> str:
        """
        Normalize text case.

        Args:
            value: Input string to normalize
            case: Desired case ('lower', 'upper', 'title', 'sentence')

        Returns:
            String with normalized case

        Example:
            "Hello World" (case='lower') -> "hello world"
            "hello world" (case='title') -> "Hello World"
        """
        case = case.lower()
        if case == "lower":
            return value.lower()
        if case == "upper":
            return value.upper()
        if case == "title":
            return value.title()
        if case == "sentence":
            return CaseHelper.to_sentence(value)
        return value

    @classmethod
    @handle_empty_value
    def remove_duplicate_chars(
        cls,
        value: str,
        *,
        chars: str = " -."
    ) -> str:
        """
        Remove embedded duplicate characters from text.

        Args:
            value: Input string to normalize
            chars: String of characters to deduplicate (default: space and dash)

        Returns:
            String with duplicate characters removed

        Example:
            "hello   world" -> "hello world"
            "hello--world" -> "hello-world"
            "hello...world" (chars='.') -> "hello.world"
        """
        result: str = value
        for char in chars:
            pattern: str = f"{re.escape(char)}{{2,}}"
            result = re.sub(pattern, char, result)
        return result
