"""
case_helper.py

A utility module for case conversion operations.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

from functools import wraps
from typing import Callable, Any


def handle_empty_value(
    func: Callable[[str, Any], str]
) -> Callable[[str, Any], str]:
    """
    Decorator to handle empty value checks for case conversion methods.
    Returns empty string if input value is None or empty.
    """
    @wraps(func)
    def wrapper(
        value: str,
        *args: Any,
        **kwargs: Any
    ) -> str:
        if value is None or not value:
            return ""
        return func(value, *args, **kwargs)

    return wrapper


class CaseHelper:
    """
    A utility class for case conversion operations.

    This class provides methods to:
    - Convert strings to different cases (train, sentence, camel, snake, kebab, pascal)
    - Handle case-insensitive comparisons
    - Normalize string formatting by converting separators to spaces

    All methods support an optional normalize parameter (default: True) that:
    - Converts underscores and hyphens to spaces before processing
    - Ensures consistent handling of mixed input formats
    """

    @staticmethod
    @handle_empty_value
    def normalize(
        value: str
    ) -> str:
        """
        Normalize a string by converting underscores and hyphens to spaces.
        This ensures consistent handling of mixed input formats.

        Args:
            value: Input string that may contain underscores or hyphens

        Returns:
            String with underscores and hyphens converted to spaces

        Example:
            "hello_world" -> "hello world"
            "hello-world" -> "hello world"
        """
        return value.replace("_", " ").replace("-", " ")

    @classmethod
    @handle_empty_value
    def to_train(
        cls,
        value: str,
        *,
        normalize: bool = True
    ) -> str:
        """
        Convert a string to train case (capitalized words separated by hyphens).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first

        Returns:
            String in train case format

        Example:
            "hello world" -> "Hello-World"
            "hello_world" -> "Hello-World"
        """
        if normalize:
            value = cls.normalize(value)
        return value.title().replace(" ", "-")

    @classmethod
    @handle_empty_value
    def to_sentence(
        cls,
        value: str,
        *,
        normalize: bool = True
    ) -> str:
        """
        Convert a string to sentence case (first word capitalized, rest lowercase).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first

        Returns:
            String in sentence case format

        Example:
            "hello world" -> "Hello world"
            "hello_world" -> "Hello world"
        """
        if normalize:
            value = cls.normalize(value)
        return value.capitalize()

    @classmethod
    @handle_empty_value
    def to_camel(
        cls,
        value: str,
        *,
        normalize: bool = True
    ) -> str:
        """
        Convert a string to camel case (first word lowercase, subsequent words capitalized).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first

        Returns:
            String in camel case format

        Example:
            "hello world" -> "helloWorld"
            "hello_world" -> "helloWorld"
        """
        if normalize:
            value = cls.normalize(value)

        words: list[str] = value.split()
        if not words:
            return ""
        
        return words[0].lower() + "".join(word.title() for word in words[1:])

    @classmethod
    @handle_empty_value
    def to_snake(
        cls,
        value: str,
        *,
        normalize: bool = True
    ) -> str:
        """
        Convert a string to snake case (all lowercase with underscore separators).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first

        Returns:
            String in snake case format

        Example:
            "hello world" -> "hello_world"
            "hello-world" -> "hello_world"
        """
        if normalize:
            value = cls.normalize(value)            
        return value.lower().replace(" ", "_")

    @classmethod
    @handle_empty_value
    def to_kebab(
        cls,
        value: str,
        *,
        normalize: bool = True
    ) -> str:
        """
        Convert a string to kebab case (all lowercase with hyphen separators).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first

        Returns:
            String in kebab case format

        Example:
            "hello world" -> "hello-world"
            "hello_world" -> "hello-world"
        """
        if normalize:
            value = cls.normalize(value)
        return value.lower().replace(" ", "-")

    @classmethod
    @handle_empty_value
    def to_pascal(
        cls,
        value: str,
        *,
        normalize: bool = True
    ) -> str:
        """
        Convert a string to pascal case (all words capitalized, no separators).

        Args:
            value: Input string to convert
            normalize: If True, converts underscores and hyphens to spaces first

        Returns:
            String in pascal case format

        Example:
            "hello world" -> "HelloWorld"
            "hello_world" -> "HelloWorld"
        """
        if normalize:
            value = cls.normalize(value)
        return "".join(word.title() for word in value.split())
