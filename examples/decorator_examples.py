"""
Example demonstrating the three different handle_empty_value decorators.

This example shows how to use:
- handle_empty_value_classmethod: For @classmethod decorated methods
- handle_empty_value_instancemethod: For instance methods (self as first parameter)
- handle_empty_value_function: For standalone functions
"""

from splurge_tools.decorators import (
    handle_empty_value_classmethod,
    handle_empty_value_instancemethod,
    handle_empty_value,
    deprecated_method
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
    print("=== Handle Empty Value Decorator Examples ===\n")
    
    # Test class method
    print("1. Class Method Decorator:")
    print(f"   Normal input: {StringProcessor.class_process_string('hello')}")
    print(f"   None input: {repr(StringProcessor.class_process_string(None))}")
    print(f"   Empty input: {repr(StringProcessor.class_process_string(''))}")
    print()
    
    # Test instance method
    processor = StringProcessor("custom_")
    print("2. Instance Method Decorator:")
    print(f"   Normal input: {processor.instance_process_string('world')}")
    print(f"   None input: {repr(processor.instance_process_string(None))}")
    print(f"   Empty input: {repr(processor.instance_process_string(''))}")
    print()
    
    # Test standalone function
    print("3. Standalone Function Decorator:")
    print(f"   Normal input: {standalone_process_string('python')}")
    print(f"   None input: {repr(standalone_process_string(None))}")
    print(f"   Empty input: {repr(standalone_process_string(''))}")
    print()
    
    # Test deprecated method
    print("4. Deprecated Method Decorator:")
    print(f"   Normal input: {deprecated_process_string('legacy')}")
    print("   (Note: This will show a deprecation warning)")
    print()
    
    print("All decorators handle None and empty strings gracefully!")


if __name__ == "__main__":
    demonstrate_decorators()
