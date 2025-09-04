"""
Example demonstrating the three different handle_empty_value decorators.

This example shows how to use:
- handle_empty_value_classmethod: For @classmethod decorated methods
- handle_empty_value_instancemethod: For instance methods (self as first parameter)
- handle_empty_value: For standalone methods and @staticmethod decorated methods
"""

from splurge_tools.decorators import (
    deprecated_method,
    handle_empty_value,
    handle_empty_value_classmethod,
    handle_empty_value_instancemethod,
)


class StringProcessor:
    """Example class demonstrating different decorator usage patterns."""

    def __init__(self, prefix: str = "processed_"):
        self.prefix = prefix

    @classmethod
    @handle_empty_value_classmethod
    def class_process_string(cls, value: str) -> str:
        """Class method that processes strings."""
        return f"class:{value.upper()}"

    @handle_empty_value_instancemethod
    def instance_process_string(self, value: str) -> str:
        """Instance method that processes strings."""
        return f"{self.prefix}{value.upper()}"


@handle_empty_value
def standalone_process_string(value: str) -> str:
    """Standalone function that processes strings."""
    return f"function:{value.upper()}"


@deprecated_method("new_process_method", "2.0.0")
def deprecated_process_string(value: str) -> str:
    """Deprecated method that processes strings."""
    return f"deprecated:{value.upper()}"


def demonstrate_decorators():
    """Demonstrate all three decorator types."""

    # Test class method

    # Test instance method
    StringProcessor("custom_")

    # Test standalone function

    # Test deprecated method


if __name__ == "__main__":
    demonstrate_decorators()
