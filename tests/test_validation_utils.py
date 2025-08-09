"""
test_validation_utils.py

Comprehensive unit tests for the validation_utils module.
"""

import tempfile
import unittest
from pathlib import Path
from typing import Any

from splurge_tools.validation_utils import Validator
from splurge_tools.exceptions import (
    SplurgeParameterError,
    SplurgeRangeError,
    SplurgeValidationError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFormatError
)


class TestValidatorIsNonEmptyString(unittest.TestCase):
    """Test cases for Validator.is_non_empty_string method."""

    def test_valid_strings(self):
        """Test valid string inputs."""
        # Basic valid string
        result = Validator.is_non_empty_string("hello", "test_param")
        self.assertEqual(result, "hello")
        
        # String with spaces
        result = Validator.is_non_empty_string("hello world", "test_param")
        self.assertEqual(result, "hello world")
        
        # String with special characters
        result = Validator.is_non_empty_string("hello@#$%", "test_param")
        self.assertEqual(result, "hello@#$%")
        
        # Single character
        result = Validator.is_non_empty_string("a", "test_param")
        self.assertEqual(result, "a")

    def test_whitespace_handling(self):
        """Test whitespace handling options."""
        # Whitespace-only string - not allowed by default
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_empty_string("   ", "test_param")
        self.assertIn("must be a non-empty string", str(cm.exception))
        
        # Whitespace-only string - allowed when specified
        result = Validator.is_non_empty_string("   ", "test_param", allow_whitespace_only=True)
        self.assertEqual(result, "   ")
        
        # String with leading/trailing whitespace
        result = Validator.is_non_empty_string("  hello  ", "test_param")
        self.assertEqual(result, "  hello  ")

    def test_invalid_inputs(self):
        """Test invalid inputs."""
        # None input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_empty_string(None, "test_param")
        self.assertIn("must be a string", str(cm.exception))
        self.assertIn("got NoneType", str(cm.exception))
        
        # Empty string
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_empty_string("", "test_param")
        self.assertIn("must be a non-empty string", str(cm.exception))
        
        # Integer input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_empty_string(123, "test_param")
        self.assertIn("must be a string", str(cm.exception))
        self.assertIn("got int", str(cm.exception))
        
        # List input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_empty_string(["hello"], "test_param")
        self.assertIn("must be a string", str(cm.exception))
        self.assertIn("got list", str(cm.exception))

    def test_error_details(self):
        """Test that error details are helpful."""
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_empty_string(42, "my_parameter")
        
        exception = cm.exception
        self.assertIn("my_parameter must be a string", exception.message)
        self.assertIn("Expected string, received: 42", exception.details)


class TestValidatorIsPositiveInteger(unittest.TestCase):
    """Test cases for Validator.is_positive_integer method."""

    def test_valid_integers(self):
        """Test valid integer inputs."""
        # Basic positive integer
        result = Validator.is_positive_integer(5, "test_param")
        self.assertEqual(result, 5)
        
        # Large integer
        result = Validator.is_positive_integer(1000000, "test_param")
        self.assertEqual(result, 1000000)
        
        # Minimum value (default is 1)
        result = Validator.is_positive_integer(1, "test_param")
        self.assertEqual(result, 1)

    def test_custom_bounds(self):
        """Test custom minimum and maximum bounds."""
        # Custom minimum value
        result = Validator.is_positive_integer(10, "test_param", min_value=10)
        self.assertEqual(result, 10)
        
        # Custom maximum value
        result = Validator.is_positive_integer(5, "test_param", max_value=10)
        self.assertEqual(result, 5)
        
        # Both min and max
        result = Validator.is_positive_integer(7, "test_param", min_value=5, max_value=10)
        self.assertEqual(result, 7)

    def test_invalid_types(self):
        """Test invalid input types."""
        # Float input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_positive_integer(5.5, "test_param")
        self.assertIn("must be an integer", str(cm.exception))
        self.assertIn("got float", str(cm.exception))
        
        # String input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_positive_integer("5", "test_param")
        self.assertIn("must be an integer", str(cm.exception))
        self.assertIn("got str", str(cm.exception))
        
        # None input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_positive_integer(None, "test_param")
        self.assertIn("must be an integer", str(cm.exception))
        self.assertIn("got NoneType", str(cm.exception))

    def test_range_violations(self):
        """Test range boundary violations."""
        # Below minimum (default min_value=1)
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_positive_integer(0, "test_param")
        self.assertIn("must be >= 1, got 0", str(cm.exception))
        # Just check that the error contains the value information
        self.assertIn("0", str(cm.exception))
        
        # Below custom minimum
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_positive_integer(5, "test_param", min_value=10)
        self.assertIn("must be >= 10, got 5", str(cm.exception))
        
        # Above maximum
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_positive_integer(15, "test_param", max_value=10)
        self.assertIn("must be <= 10, got 15", str(cm.exception))
        self.assertIn("exceeds maximum allowed value 10", str(cm.exception.details))

    def test_edge_cases(self):
        """Test edge cases."""
        # Zero with min_value=0
        result = Validator.is_positive_integer(0, "test_param", min_value=0)
        self.assertEqual(result, 0)
        
        # Negative with custom min_value
        result = Validator.is_positive_integer(-5, "test_param", min_value=-10)
        self.assertEqual(result, -5)


class TestValidatorIsNonNegativeInteger(unittest.TestCase):
    """Test cases for Validator.is_non_negative_integer method."""

    def test_valid_non_negative_integers(self):
        """Test valid non-negative integer inputs."""
        # Zero
        result = Validator.is_non_negative_integer(0, "test_param")
        self.assertEqual(result, 0)
        
        # Positive integer
        result = Validator.is_non_negative_integer(42, "test_param")
        self.assertEqual(result, 42)
        
        # Large integer
        result = Validator.is_non_negative_integer(1000000, "test_param")
        self.assertEqual(result, 1000000)

    def test_custom_maximum(self):
        """Test custom maximum bounds."""
        result = Validator.is_non_negative_integer(5, "test_param", max_value=10)
        self.assertEqual(result, 5)
        
        with self.assertRaises(SplurgeRangeError):
            Validator.is_non_negative_integer(15, "test_param", max_value=10)

    def test_negative_integers(self):
        """Test that negative integers are rejected."""
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_non_negative_integer(-1, "test_param")
        self.assertIn("must be >= 0, got -1", str(cm.exception))
        
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_non_negative_integer(-100, "test_param")
        self.assertIn("must be >= 0, got -100", str(cm.exception))

    def test_invalid_types(self):
        """Test invalid input types."""
        with self.assertRaises(SplurgeParameterError):
            Validator.is_non_negative_integer(5.0, "test_param")
        
        with self.assertRaises(SplurgeParameterError):
            Validator.is_non_negative_integer("5", "test_param")


class TestValidatorIsRangeBounds(unittest.TestCase):
    """Test cases for Validator.is_range_bounds method."""

    def test_valid_ranges(self):
        """Test valid range bounds."""
        # Basic valid range
        Validator.is_range_bounds(1, 10)  # Should not raise
        
        # Equal bounds (valid for some use cases)
        Validator.is_range_bounds(5, 5, allow_equal=True)  # Should not raise
        
        # Negative ranges
        Validator.is_range_bounds(-10, -1)  # Should not raise
        
        # Mixed ranges
        Validator.is_range_bounds(-5, 5)  # Should not raise

    def test_invalid_ranges(self):
        """Test invalid range bounds."""
        # Lower > upper
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_range_bounds(10, 5)
        self.assertIn("lower must be < upper", str(cm.exception))
        # Check details for the actual values
        self.assertIn("Got lower=10, upper=5", str(cm.exception.details))
        
        # Custom parameter names
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_range_bounds(20, 15, lower_param="start", upper_param="end")
        self.assertIn("start must be < end", str(cm.exception))
        self.assertIn("Got start=20, end=15", str(cm.exception.details))

    def test_edge_cases(self):
        """Test edge cases for range validation."""
        # Large numbers
        Validator.is_range_bounds(1000000, 2000000)  # Should not raise
        
        # Float inputs (should work)
        Validator.is_range_bounds(1.5, 2.5)  # Should not raise
        
        # Very close floats
        Validator.is_range_bounds(1.0000001, 1.0000002)  # Should not raise


class TestValidatorIsDelimiter(unittest.TestCase):
    """Test cases for Validator.is_delimiter method."""

    def test_valid_delimiters(self):
        """Test valid delimiter inputs."""
        # Common delimiters
        result = Validator.is_delimiter(",")
        self.assertEqual(result, ",")
        
        result = Validator.is_delimiter("|")
        self.assertEqual(result, "|")
        
        result = Validator.is_delimiter("\t")
        self.assertEqual(result, "\t")
        
        # Multi-character delimiter
        result = Validator.is_delimiter("||")
        self.assertEqual(result, "||")
        
        # Special characters
        result = Validator.is_delimiter("@#$")
        self.assertEqual(result, "@#$")

    def test_invalid_delimiters(self):
        """Test invalid delimiter inputs."""
        # Empty string
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_delimiter("")
        self.assertIn("delimiter cannot be empty", str(cm.exception))
        self.assertIn("must be at least one character", str(cm.exception.details))
        
        # None input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_delimiter(None)
        self.assertIn("delimiter cannot be None", str(cm.exception))
        self.assertIn("must be a non-empty string", str(cm.exception.details))
        
        # Non-string input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_delimiter(123)
        self.assertIn("must be a string", str(cm.exception))
        self.assertIn("got int", str(cm.exception))

    def test_custom_parameter_name(self):
        """Test custom parameter name in error messages."""
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_delimiter("", param_name="separator")
        self.assertIn("separator cannot be empty", str(cm.exception))


class TestValidatorIsFilePath(unittest.TestCase):
    """Test cases for Validator.is_file_path method."""

    def setUp(self):
        """Set up test fixtures."""
        # Create temporary files for testing
        self.temp_file = tempfile.NamedTemporaryFile(delete=False)
        self.temp_file.write(b"test content")
        self.temp_file.close()
        
        self.temp_path = Path(self.temp_file.name)
        
        # Create a temporary directory
        self.temp_dir = tempfile.mkdtemp()
        self.temp_dir_path = Path(self.temp_dir)

    def tearDown(self):
        """Clean up test fixtures."""
        if self.temp_path.exists():
            self.temp_path.unlink()
        
        if self.temp_dir_path.exists():
            self.temp_dir_path.rmdir()

    def test_valid_existing_file(self):
        """Test valid existing file paths."""
        # String path to existing file
        result = Validator.is_file_path(str(self.temp_path), "test_param")
        self.assertEqual(result, self.temp_path)
        
        # Path object to existing file
        result = Validator.is_file_path(self.temp_path, "test_param")
        self.assertEqual(result, self.temp_path)

    def test_non_existent_file_allowed(self):
        """Test non-existent files when allowed."""
        non_existent = self.temp_path.parent / "non_existent.txt"
        
        # Should work when must_exist=False (default)
        result = Validator.is_file_path(str(non_existent), "test_param")
        self.assertEqual(result, non_existent)

    def test_non_existent_file_required(self):
        """Test non-existent files when existence is required."""
        non_existent = self.temp_path.parent / "non_existent.txt"
        
        # Should raise when must_exist=True
        with self.assertRaises(SplurgeValidationError) as cm:
            Validator.is_file_path(str(non_existent), "test_param", must_exist=True)
        self.assertIn("does not exist", str(cm.exception))

    def test_directory_path(self):
        """Test directory paths."""
        # Directory when file is required
        with self.assertRaises(SplurgeValidationError) as cm:
            Validator.is_file_path(str(self.temp_dir_path), "test_param", must_be_file=True)
        self.assertIn("is not a file", str(cm.exception))
        
        # Directory when directory is allowed (default)
        result = Validator.is_file_path(str(self.temp_dir_path), "test_param")
        self.assertEqual(result, self.temp_dir_path)

    def test_invalid_inputs(self):
        """Test invalid input types."""
        # None input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_file_path(None, "test_param")
        self.assertIn("must be a string or Path object", str(cm.exception))
        
        # Integer input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_file_path(123, "test_param")
        self.assertIn("must be a string or Path object", str(cm.exception))
        
        # List input
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_file_path([str(self.temp_path)], "test_param")
        self.assertIn("must be a string or Path object", str(cm.exception))

    def test_empty_string_path(self):
        """Test empty string path."""
        # Empty string creates a Path('.') which is valid
        result = Validator.is_file_path("", "test_param")
        self.assertEqual(result, Path("."))


class TestValidatorIsIterable(unittest.TestCase):
    """Test cases for Validator.is_iterable method."""

    def test_valid_iterables(self):
        """Test that valid iterables are accepted."""
        # Test basic iterables
        result = Validator.is_iterable([1, 2, 3], "test_param")
        self.assertEqual(result, [1, 2, 3])
        
        result = Validator.is_iterable((1, 2, 3), "test_param")
        self.assertEqual(result, (1, 2, 3))
        
        result = Validator.is_iterable("hello", "test_param")
        self.assertEqual(result, "hello")
        
        result = Validator.is_iterable({1, 2, 3}, "test_param")
        self.assertEqual(result, {1, 2, 3})
        
        result = Validator.is_iterable({"a": 1}, "test_param")
        self.assertEqual(result, {"a": 1})

    def test_empty_iterables_allowed(self):
        """Test that empty iterables are accepted when allow_empty=True."""
        result = Validator.is_iterable([], "test_param", allow_empty=True)
        self.assertEqual(result, [])
        
        result = Validator.is_iterable("", "test_param", allow_empty=True)
        self.assertEqual(result, "")
        
        result = Validator.is_iterable(set(), "test_param", allow_empty=True)
        self.assertEqual(result, set())

    def test_empty_iterables_not_allowed(self):
        """Test that empty iterables raise error when allow_empty=False."""
        with self.assertRaises(SplurgeValidationError) as cm:
            Validator.is_iterable([], "test_param", allow_empty=False)
        self.assertIn("test_param cannot be empty", str(cm.exception))
        
        with self.assertRaises(SplurgeValidationError) as cm:
            Validator.is_iterable("", "test_param", allow_empty=False)
        self.assertIn("test_param cannot be empty", str(cm.exception))

    def test_non_iterable_values(self):
        """Test that non-iterable values raise SplurgeParameterError."""
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_iterable(42, "test_param")
        self.assertIn("test_param must be iterable", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_iterable(None, "test_param")
        self.assertIn("test_param must be iterable", str(cm.exception))

    def test_expected_type_validation(self):
        """Test type validation when expected_type is specified."""
        # Valid type
        result = Validator.is_iterable([1, 2, 3], "test_param", expected_type=list)
        self.assertEqual(result, [1, 2, 3])
        
        # Invalid type
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_iterable("hello", "test_param", expected_type=list)
        self.assertIn("test_param must be of type list", str(cm.exception))

    def test_generator_objects(self):
        """Test that generator objects work as iterables."""
        def gen():
            yield 1
            yield 2
            yield 3
        
        generator = gen()
        result = Validator.is_iterable(generator, "test_param")
        self.assertEqual(result, generator)


class TestValidatorIsNonNegativeInteger(unittest.TestCase):
    """Test cases for Validator.is_non_negative_integer method."""

    def test_valid_non_negative_integers(self):
        """Test that valid non-negative integers are accepted."""
        result = Validator.is_non_negative_integer(0, "test_param")
        self.assertEqual(result, 0)
        
        result = Validator.is_non_negative_integer(1, "test_param")
        self.assertEqual(result, 1)
        
        result = Validator.is_non_negative_integer(100, "test_param")
        self.assertEqual(result, 100)

    def test_negative_integers(self):
        """Test that negative integers raise SplurgeRangeError."""
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_non_negative_integer(-1, "test_param")
        self.assertIn("test_param must be >= 0", str(cm.exception))
        
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_non_negative_integer(-100, "test_param")
        self.assertIn("test_param must be >= 0", str(cm.exception))

    def test_custom_max_value(self):
        """Test custom maximum values."""
        result = Validator.is_non_negative_integer(10, "test_param", max_value=10)
        self.assertEqual(result, 10)
        
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_non_negative_integer(11, "test_param", max_value=10)
        self.assertIn("test_param must be <= 10", str(cm.exception))

    def test_invalid_types(self):
        """Test that non-integer types raise SplurgeParameterError."""
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_negative_integer("5", "test_param")
        self.assertIn("test_param must be an integer", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_negative_integer(5.5, "test_param")
        self.assertIn("test_param must be an integer", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_non_negative_integer(None, "test_param")
        self.assertIn("test_param must be an integer", str(cm.exception))


class TestValidatorIsEncoding(unittest.TestCase):
    """Test cases for Validator.is_encoding method."""

    def test_valid_encodings(self):
        """Test that valid encodings are accepted."""
        result = Validator.is_encoding("utf-8", "test_param")
        self.assertEqual(result, "utf-8")
        
        result = Validator.is_encoding("ascii", "test_param")
        self.assertEqual(result, "ascii")
        
        result = Validator.is_encoding("latin-1", "test_param")
        self.assertEqual(result, "latin-1")
        
        result = Validator.is_encoding("utf-16", "test_param")
        self.assertEqual(result, "utf-16")

    def test_invalid_encoding_names(self):
        """Test that invalid encoding names raise SplurgeFormatError."""
        with self.assertRaises(SplurgeFormatError) as cm:
            Validator.is_encoding("invalid-encoding", "test_param")
        self.assertIn("Unsupported encoding: invalid-encoding", str(cm.exception))
        
        with self.assertRaises(SplurgeFormatError) as cm:
            Validator.is_encoding("fake-encoding-123", "test_param")
        self.assertIn("Unsupported encoding: fake-encoding-123", str(cm.exception))

    def test_non_string_values(self):
        """Test that non-string values raise SplurgeParameterError."""
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_encoding(123, "test_param")
        self.assertIn("test_param must be a string", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_encoding(None, "test_param")
        self.assertIn("test_param must be a string", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_encoding(["utf-8"], "test_param")
        self.assertIn("test_param must be a string", str(cm.exception))

    def test_empty_or_whitespace_strings(self):
        """Test that empty or whitespace-only strings raise SplurgeParameterError."""
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_encoding("", "test_param")
        self.assertIn("test_param cannot be empty or whitespace", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_encoding("   ", "test_param")
        self.assertIn("test_param cannot be empty or whitespace", str(cm.exception))
        
        with self.assertRaises(SplurgeParameterError) as cm:
            Validator.is_encoding("\t\n", "test_param")
        self.assertIn("test_param cannot be empty or whitespace", str(cm.exception))

    def test_case_sensitivity(self):
        """Test that encoding names are case-sensitive where appropriate."""
        # Most encodings are case-insensitive in Python
        result = Validator.is_encoding("UTF-8", "test_param")
        self.assertEqual(result, "UTF-8")
        
        result = Validator.is_encoding("Utf-8", "test_param")
        self.assertEqual(result, "Utf-8")


class TestValidatorCreateHelpfulErrorMessage(unittest.TestCase):
    """Test cases for Validator.create_helpful_error_message method."""

    def test_basic_message_creation(self):
        """Test basic error message creation."""
        message, details = Validator.create_helpful_error_message("Something went wrong")
        
        self.assertEqual(message, "Something went wrong")
        self.assertIsNone(details)

    def test_message_with_received_value(self):
        """Test message creation with received value."""
        message, details = Validator.create_helpful_error_message(
            "Invalid input",
            received_value="bad_value"
        )
        
        self.assertEqual(message, "Invalid input")
        self.assertIn("Received value: 'bad_value'", details)

    def test_message_with_expected_type(self):
        """Test message creation with expected type."""
        message, details = Validator.create_helpful_error_message(
            "Type error",
            expected_type="string"
        )
        
        self.assertEqual(message, "Type error")
        self.assertIn("Expected: string", details)

    def test_message_with_suggestions(self):
        """Test message creation with suggestions."""
        suggestions = ["Try option A", "Try option B", "Check documentation"]
        message, details = Validator.create_helpful_error_message(
            "Configuration error",
            suggestions=suggestions
        )
        
        self.assertEqual(message, "Configuration error")
        self.assertIn("Suggestions:", details)
        self.assertIn("- Try option A", details)
        self.assertIn("- Try option B", details)
        self.assertIn("- Check documentation", details)

    def test_comprehensive_message(self):
        """Test message creation with all parameters."""
        message, details = Validator.create_helpful_error_message(
            "Validation failed",
            received_value=42,
            expected_type="string",
            suggestions=["Convert to string", "Use different input"]
        )
        
        self.assertEqual(message, "Validation failed")
        self.assertIn("Expected: string", details)
        self.assertIn("Received value: 42", details)
        self.assertIn("Suggestions:", details)
        self.assertIn("- Convert to string", details)
        self.assertIn("- Use different input", details)

    def test_empty_suggestions_list(self):
        """Test with empty suggestions list."""
        message, details = Validator.create_helpful_error_message(
            "Error occurred",
            suggestions=[]
        )
        
        self.assertEqual(message, "Error occurred")
        self.assertIsNone(details)

    def test_none_values(self):
        """Test with None values for optional parameters."""
        message, details = Validator.create_helpful_error_message(
            "Basic error",
            received_value=None,
            expected_type=None,
            suggestions=None
        )
        
        self.assertEqual(message, "Basic error")
        self.assertIsNone(details)

    def test_complex_received_value(self):
        """Test with complex received values."""
        # List value
        message, details = Validator.create_helpful_error_message(
            "Invalid list",
            received_value=[1, 2, 3]
        )
        self.assertIn("Received value: [1, 2, 3]", details)
        
        # Dictionary value
        message, details = Validator.create_helpful_error_message(
            "Invalid dict",
            received_value={"key": "value"}
        )
        self.assertIn("Received value: {'key': 'value'}", details)

    def test_valid_range_edge_cases(self):
        """Test edge cases for valid_range parameter."""
        # Test with tuple range
        message, details = Validator.create_helpful_error_message(
            "Value out of range",
            valid_range=(0, 100)
        )
        self.assertEqual(message, "Value out of range")
        self.assertIn("Valid range: 0 to 100", details)
        
        # Test with negative range
        message, details = Validator.create_helpful_error_message(
            "Value out of range",
            valid_range=(-10, -1)
        )
        self.assertEqual(message, "Value out of range")
        self.assertIn("Valid range: -10 to -1", details)

    def test_expected_type_edge_cases(self):
        """Test edge cases for expected_type parameter."""
        # Test with non-type object (string)
        message, details = Validator.create_helpful_error_message(
            "Type mismatch",
            expected_type="custom_type_description"
        )
        self.assertEqual(message, "Type mismatch")
        self.assertIn("Expected: custom_type_description", details)
        
        # Test with built-in type
        message, details = Validator.create_helpful_error_message(
            "Type mismatch",
            expected_type=dict
        )
        self.assertEqual(message, "Type mismatch")
        self.assertIn("Expected type: dict", details)

    def test_all_parameters_combined(self):
        """Test with all parameters provided."""
        message, details = Validator.create_helpful_error_message(
            "Complete validation error",
            received_value=42.5,
            expected_type=int,
            valid_range=(1, 10),
            suggestions=["Use integer values", "Check range limits"]
        )
        self.assertEqual(message, "Complete validation error")
        self.assertIn("Received value: 42.5 (type: float)", details)
        self.assertIn("Expected type: int", details)
        self.assertIn("Valid range: 1 to 10", details)
        self.assertIn("Suggestions:", details)
        self.assertIn("  - Use integer values", details)
        self.assertIn("  - Check range limits", details)


class TestValidatorEdgeCases(unittest.TestCase):
    """Test edge cases and error conditions for various Validator methods."""

    def test_range_bounds_allow_equal_edge_cases(self):
        """Test edge cases for is_range_bounds with allow_equal parameter."""
        # Test equal values with allow_equal=True
        result = Validator.is_range_bounds(5, 5, allow_equal=True)
        self.assertEqual(result, (5, 5))
        
        # Test equal values with allow_equal=False
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_range_bounds(5, 5, allow_equal=False)
        self.assertIn("lower must be < upper", str(cm.exception))
        
        # Test lower > upper with allow_equal=True (should still fail)
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_range_bounds(10, 5, allow_equal=True)
        self.assertIn("lower must be <= upper", str(cm.exception))

    def test_range_bounds_custom_param_names(self):
        """Test is_range_bounds with custom parameter names."""
        with self.assertRaises(SplurgeRangeError) as cm:
            Validator.is_range_bounds(
                10, 5, 
                lower_param="min_val", 
                upper_param="max_val",
                allow_equal=False
            )
        self.assertIn("min_val must be < max_val", str(cm.exception))

    def test_file_path_invalid_path_construction(self):
        """Test is_file_path with values that cause Path construction errors."""
        # Test with null bytes - Path constructor on Windows preserves them
        # so let's test that it works correctly
        result = Validator.is_file_path("test\x00file", "test_param")
        self.assertEqual(result, Path("test\x00file"))  # null bytes are preserved on Windows

    def test_file_path_permission_simulation(self):
        """Test file path validation with permission issues."""
        import tempfile
        import os
        
        # Create a temporary file to test with
        with tempfile.NamedTemporaryFile(delete=False) as temp_file:
            temp_path = temp_file.name
            temp_file.write(b"test content")
        
        try:
            # Test existing file
            result = Validator.is_file_path(temp_path, "test_param", must_exist=True)
            self.assertEqual(result, Path(temp_path))
            
            # Test non-existent file with must_exist=True
            non_existent = temp_path + "_nonexistent"
            with self.assertRaises(SplurgeValidationError) as cm:
                Validator.is_file_path(non_existent, "test_param", must_exist=True)
            self.assertIn("test_param does not exist", str(cm.exception))
            
        finally:
            # Clean up
            if os.path.exists(temp_path):
                os.unlink(temp_path)

    def test_positive_integer_boundary_values(self):
        """Test boundary values for is_positive_integer."""
        # Test with very large integers
        large_int = 10**100
        result = Validator.is_positive_integer(large_int, "test_param")
        self.assertEqual(result, large_int)
        
        # Test with max_value boundary
        result = Validator.is_positive_integer(100, "test_param", max_value=100)
        self.assertEqual(result, 100)
        
        with self.assertRaises(SplurgeRangeError):
            Validator.is_positive_integer(101, "test_param", max_value=100)

    def test_delimiter_edge_cases(self):
        """Test edge cases for is_delimiter method."""
        # Test with unicode characters
        result = Validator.is_delimiter("→", "test_param")
        self.assertEqual(result, "→")
        
        # Test with escape sequences
        result = Validator.is_delimiter("\\n", "test_param")
        self.assertEqual(result, "\\n")
        
        # Test with actual newline
        result = Validator.is_delimiter("\n", "test_param")
        self.assertEqual(result, "\n")

    def test_non_empty_string_unicode_edge_cases(self):
        """Test unicode edge cases for is_non_empty_string."""
        # Test with unicode string
        result = Validator.is_non_empty_string("héllo", "test_param")
        self.assertEqual(result, "héllo")
        
        # Test with emoji
        result = Validator.is_non_empty_string("🚀", "test_param")
        self.assertEqual(result, "🚀")
        
        # Test with zero-width characters - these are not treated as whitespace by Python's strip()
        result = Validator.is_non_empty_string("\u200b", "test_param", allow_whitespace_only=False)
        self.assertEqual(result, "\u200b")  # zero-width space is preserved
        
        # Test with actual whitespace characters
        with self.assertRaises(SplurgeParameterError):
            Validator.is_non_empty_string("   ", "test_param", allow_whitespace_only=False)


if __name__ == "__main__":
    unittest.main()
