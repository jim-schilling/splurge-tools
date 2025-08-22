"""
decorators.py

A utility module for common decorators used across the splurge_tools package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import warnings
from functools import wraps
from typing import Callable, Any, TypeVar

F = TypeVar('F', bound=Callable[..., Any])


def handle_empty_value_classmethod(
    func: Callable[..., str]
) -> Callable[..., str]:
    """
    Decorator to handle empty value checks for class methods that process string values.
    
    Returns empty string if input value is None or empty string.
    Designed specifically for @classmethod decorated methods.
    
    Args:
        func: The class method to decorate
        
    Returns:
        Decorated class method that handles empty values
        
    Example:
        @classmethod
        @handle_empty_value_classmethod
        def process_string(cls, value: str) -> str:
            return value.upper()
    """
    @wraps(func)
    def wrapper(
        cls: Any,
        value: str,
        *args: Any,
        **kwargs: Any
    ) -> str:
        if value is None or not value:
            return ""
        return func(cls, value, *args, **kwargs)

    return wrapper


def handle_empty_value_instancemethod(
    func: Callable[..., str]
) -> Callable[..., str]:
    """
    Decorator to handle empty value checks for instance methods that process string values.
    
    Returns empty string if input value is None or empty string.
    Designed specifically for instance methods (self as first parameter).
    
    Args:
        func: The instance method to decorate
        
    Returns:
        Decorated instance method that handles empty values
        
    Example:
        @handle_empty_value_instancemethod
        def process_string(self, value: str) -> str:
            return value.upper()
    """
    @wraps(func)
    def wrapper(
        self: Any,
        value: str,
        *args: Any,
        **kwargs: Any
    ) -> str:
        if value is None or not value:
            return ""
        return func(self, value, *args, **kwargs)

    return wrapper


def handle_empty_value(
    func: Callable[..., str]
) -> Callable[..., str]:
    """
    Decorator to handle empty value checks for standalone functions that process string values.
    
    Returns empty string if input value is None or empty string.
    Designed specifically for standalone functions (value as first parameter).
    
    Args:
        func: The function to decorate
        
    Returns:
        Decorated function that handles empty values
        
    Example:
        @handle_empty_value
        def process_string(value: str) -> str:
            return value.upper()
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


def deprecated_method(
    replacement: str,
    version: str = "future version"
) -> Callable[[F], F]:
    """
    Decorator to mark methods as deprecated.
    
    Args:
        replacement: Name of the replacement method/function
        version: Version when the method will be removed
        
    Returns:
        Decorated function that issues deprecation warning
        
    Example:
        @deprecated_method("new_method_name", "2.0.0")
        def old_method(self, value: str) -> str:
            return value.upper()
    """
    def decorator(func: F) -> F:
        @wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            warnings.warn(
                f"{func.__name__} is deprecated and will be removed in a {version}. "
                f"Use {replacement} instead.",
                DeprecationWarning,
                stacklevel=2
            )
            return func(*args, **kwargs)
        return wrapper
    return decorator
