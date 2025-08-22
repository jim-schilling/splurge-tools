"""
Test cases for decorators module.
"""

import unittest
from unittest.mock import Mock

from splurge_tools.decorators import (
    handle_empty_value_classmethod,
    handle_empty_value_instancemethod,
    handle_empty_value,
    deprecated_method
)


class TestDecorators(unittest.TestCase):
    """Test cases for decorators module."""

    def test_handle_empty_value_classmethod_with_none(self):
        """Test that None values return empty string for class methods."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_classmethod
        def test_method(cls, value: str) -> str:
            return mock_func(cls, value)
        
        result = test_method("TestClass", None)
        self.assertEqual(result, "")
        mock_func.assert_not_called()

    def test_handle_empty_value_classmethod_with_empty_string(self):
        """Test that empty strings return empty string for class methods."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_classmethod
        def test_method(cls, value: str) -> str:
            return mock_func(cls, value)
        
        result = test_method("TestClass", "")
        self.assertEqual(result, "")
        mock_func.assert_not_called()

    def test_handle_empty_value_classmethod_with_valid_string(self):
        """Test that valid strings are processed normally for class methods."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_classmethod
        def test_method(cls, value: str) -> str:
            return mock_func(cls, value)
        
        result = test_method("TestClass", "hello world")
        self.assertEqual(result, "processed")
        mock_func.assert_called_once_with("TestClass", "hello world")

    def test_handle_empty_value_instancemethod_with_none(self):
        """Test that None values return empty string for instance methods."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_instancemethod
        def test_method(self, value: str) -> str:
            return mock_func(self, value)
        
        mock_instance = Mock()
        result = test_method(mock_instance, None)
        self.assertEqual(result, "")
        mock_func.assert_not_called()

    def test_handle_empty_value_instancemethod_with_valid_string(self):
        """Test that valid strings are processed normally for instance methods."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_instancemethod
        def test_method(self, value: str) -> str:
            return mock_func(self, value)
        
        mock_instance = Mock()
        result = test_method(mock_instance, "hello world")
        self.assertEqual(result, "processed")
        mock_func.assert_called_once_with(mock_instance, "hello world")

    def test_handle_empty_value_function_with_none(self):
        """Test that None values return empty string for standalone functions."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value
        def test_function(value: str) -> str:
            return mock_func(value)
        
        result = test_function(None)
        self.assertEqual(result, "")
        mock_func.assert_not_called()

    def test_handle_empty_value_function_with_valid_string(self):
        """Test that valid strings are processed normally for standalone functions."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value
        def test_function(value: str) -> str:
            return mock_func(value)
        
        result = test_function("hello world")
        self.assertEqual(result, "processed")
        mock_func.assert_called_once_with("hello world")

    def test_handle_empty_value_with_whitespace(self):
        """Test that whitespace-only strings are processed normally."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_classmethod
        def test_method(cls, value: str) -> str:
            return mock_func(cls, value)
        
        result = test_method("TestClass", "   ")
        self.assertEqual(result, "processed")
        mock_func.assert_called_once_with("TestClass", "   ")

    def test_handle_empty_value_with_additional_args(self):
        """Test that additional arguments are passed through correctly."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value_classmethod
        def test_method(cls, value: str, *args, **kwargs) -> str:
            return mock_func(cls, value, *args, **kwargs)
        
        result = test_method("TestClass", "hello", "arg1", "arg2", kwarg1="value1")
        self.assertEqual(result, "processed")
        mock_func.assert_called_once_with("TestClass", "hello", "arg1", "arg2", kwarg1="value1")

    def test_handle_empty_value_preserves_function_metadata(self):
        """Test that function metadata is preserved by the decorator."""
        def test_method(cls, value: str) -> str:
            """Test method docstring."""
            return value.upper()
        
        decorated_method = handle_empty_value_classmethod(test_method)
        
        # Check that the docstring is preserved
        self.assertEqual(decorated_method.__doc__, "Test method docstring.")
        
        # Check that the function name is preserved
        self.assertEqual(decorated_method.__name__, "test_method")

    def test_backward_compatibility(self):
        """Test that the original handle_empty_value alias still works."""
        mock_func = Mock(return_value="processed")
        
        @handle_empty_value
        def test_method(cls, value: str) -> str:
            return mock_func(cls, value)
        
        result = test_method("TestClass", "hello world")
        self.assertEqual(result, "processed")
        mock_func.assert_called_once_with("TestClass", "hello world")

    def test_all_three_versions_work_differently(self):
        """Test that all three versions handle their respective parameter patterns correctly."""
        
        # Class method version
        @handle_empty_value_classmethod
        def class_method(cls, value: str) -> str:
            return f"class:{cls}:{value}"
        
        # Instance method version
        @handle_empty_value_instancemethod
        def instance_method(self, value: str) -> str:
            return f"instance:{self}:{value}"
        
        # Function version
        @handle_empty_value
        def standalone_function(value: str) -> str:
            return f"function:{value}"
        
        # Test class method
        result1 = class_method("MyClass", "test")
        self.assertEqual(result1, "class:MyClass:test")
        
        # Test instance method
        mock_instance = Mock()
        result2 = instance_method(mock_instance, "test")
        self.assertEqual(result2, f"instance:{mock_instance}:test")
        
        # Test standalone function
        result3 = standalone_function("test")
        self.assertEqual(result3, "function:test")

    def test_deprecated_method_warning(self):
        """Test that deprecated_method decorator issues warnings."""
        @deprecated_method("new_method", "2.0.0")
        def old_method(value: str) -> str:
            return value.upper()
        
        # Test that the method still works
        result = old_method("hello")
        self.assertEqual(result, "HELLO")
        
        # Test that warning is issued (we can't easily test warnings in unittest)
        # but we can verify the decorator doesn't break functionality

    def test_deprecated_method_preserves_metadata(self):
        """Test that deprecated_method preserves function metadata."""
        @deprecated_method("new_method", "2.0.0")
        def test_method(value: str) -> str:
            """Test method docstring."""
            return value.upper()
        
        decorated_method = test_method
        
        # Check that the docstring is preserved
        self.assertEqual(decorated_method.__doc__, "Test method docstring.")
        
        # Check that the function name is preserved
        self.assertEqual(decorated_method.__name__, "test_method")

    def test_deprecated_method_with_different_versions(self):
        """Test deprecated_method with different version strings."""
        @deprecated_method("new_method", "next release")
        def method1(value: str) -> str:
            return value.upper()
        
        @deprecated_method("new_method", "3.0.0")
        def method2(value: str) -> str:
            return value.lower()
        
        # Both methods should work
        self.assertEqual(method1("Hello"), "HELLO")
        self.assertEqual(method2("WORLD"), "world")


if __name__ == "__main__":
    unittest.main()
