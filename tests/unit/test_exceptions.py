"""
Tests for the exceptions module.

Tests all custom exception classes and their behavior including
message handling, details, and inheritance hierarchy.
"""

from splurge_tools.exceptions import (
    SplurgeConfigurationError,
    SplurgeDataProcessingError,
    SplurgeFileEncodingError,
    SplurgeFileNotFoundError,
    SplurgeFileOperationError,
    SplurgeFilePermissionError,
    SplurgeFormatError,
    SplurgeParameterError,
    SplurgeParsingError,
    SplurgePathValidationError,
    SplurgePerformanceWarning,
    SplurgeRangeError,
    SplurgeResourceAcquisitionError,
    SplurgeResourceError,
    SplurgeResourceReleaseError,
    SplurgeStreamingError,
    SplurgeToolsError,
    SplurgeTypeConversionError,
    SplurgeValidationError,
)


class TestSplurgeToolsError:
    """Test the base exception class."""

    def test_init_with_message_only(self) -> None:
        """Test initialization with only a message."""
        error = SplurgeToolsError("Test error message")
        assert error.message == "Test error message"
        assert error.details is None
        assert str(error) == "Test error message"

    def test_init_with_message_and_details(self) -> None:
        """Test initialization with message and details."""
        error = SplurgeToolsError("Test error", details="Additional details")
        assert error.message == "Test error"
        assert error.details == "Additional details"
        assert str(error) == "Test error"

    def test_inheritance(self) -> None:
        """Test that SplurgeToolsError inherits from Exception."""
        error = SplurgeToolsError("Test")
        assert isinstance(error, Exception)


class TestSplurgeValidationError:
    """Test validation error exceptions."""

    def test_parameter_error(self) -> None:
        """Test SplurgeParameterError."""
        error = SplurgeParameterError("Invalid parameter", details="Parameter 'x' must be positive")
        assert isinstance(error, SplurgeValidationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Invalid parameter"
        assert error.details == "Parameter 'x' must be positive"

    def test_range_error(self) -> None:
        """Test SplurgeRangeError."""
        error = SplurgeRangeError("Value out of range", details="Value 100 exceeds maximum of 50")
        assert isinstance(error, SplurgeValidationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Value out of range"
        assert error.details == "Value 100 exceeds maximum of 50"

    def test_format_error(self) -> None:
        """Test SplurgeFormatError."""
        error = SplurgeFormatError("Invalid format", details="Expected CSV format, got TSV")
        assert isinstance(error, SplurgeValidationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Invalid format"
        assert error.details == "Expected CSV format, got TSV"


class TestSplurgeFileOperationError:
    """Test file operation error exceptions."""

    def test_file_not_found_error(self) -> None:
        """Test SplurgeFileNotFoundError."""
        error = SplurgeFileNotFoundError("File not found", details="File '/path/to/file.txt' does not exist")
        assert isinstance(error, SplurgeFileOperationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "File not found"
        assert error.details == "File '/path/to/file.txt' does not exist"

    def test_file_permission_error(self) -> None:
        """Test SplurgeFilePermissionError."""
        error = SplurgeFilePermissionError("Permission denied", details="Cannot read '/path/to/file.txt'")
        assert isinstance(error, SplurgeFileOperationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Permission denied"
        assert error.details == "Cannot read '/path/to/file.txt'"

    def test_file_encoding_error(self) -> None:
        """Test SplurgeFileEncodingError."""
        error = SplurgeFileEncodingError("Encoding error", details="Cannot decode file with UTF-8 encoding")
        assert isinstance(error, SplurgeFileOperationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Encoding error"
        assert error.details == "Cannot decode file with UTF-8 encoding"

    def test_path_validation_error(self) -> None:
        """Test SplurgePathValidationError."""
        error = SplurgePathValidationError("Invalid path", details="Path contains dangerous characters")
        assert isinstance(error, SplurgeFileOperationError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Invalid path"
        assert error.details == "Path contains dangerous characters"


class TestSplurgeDataProcessingError:
    """Test data processing error exceptions."""

    def test_parsing_error(self) -> None:
        """Test SplurgeParsingError."""
        error = SplurgeParsingError("Parse failed", details="Invalid delimiter in line 5")
        assert isinstance(error, SplurgeDataProcessingError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Parse failed"
        assert error.details == "Invalid delimiter in line 5"

    def test_type_conversion_error(self) -> None:
        """Test SplurgeTypeConversionError."""
        error = SplurgeTypeConversionError("Conversion failed", details="Cannot convert 'abc' to integer")
        assert isinstance(error, SplurgeDataProcessingError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Conversion failed"
        assert error.details == "Cannot convert 'abc' to integer"

    def test_streaming_error(self) -> None:
        """Test SplurgeStreamingError."""
        error = SplurgeStreamingError("Stream failed", details="Connection lost during streaming")
        assert isinstance(error, SplurgeDataProcessingError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Stream failed"
        assert error.details == "Connection lost during streaming"


class TestSplurgeResourceError:
    """Test resource error exceptions."""

    def test_resource_acquisition_error(self) -> None:
        """Test SplurgeResourceAcquisitionError."""
        error = SplurgeResourceAcquisitionError("Acquisition failed", details="Database connection timeout")
        assert isinstance(error, SplurgeResourceError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Acquisition failed"
        assert error.details == "Database connection timeout"

    def test_resource_release_error(self) -> None:
        """Test SplurgeResourceReleaseError."""
        error = SplurgeResourceReleaseError("Release failed", details="Cannot close file handle")
        assert isinstance(error, SplurgeResourceError)
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Release failed"
        assert error.details == "Cannot close file handle"


class TestSplurgeConfigurationError:
    """Test configuration error exceptions."""

    def test_configuration_error(self) -> None:
        """Test SplurgeConfigurationError."""
        error = SplurgeConfigurationError("Invalid config", details="Missing required setting 'delimiter'")
        assert isinstance(error, SplurgeToolsError)
        assert error.message == "Invalid config"
        assert error.details == "Missing required setting 'delimiter'"


class TestSplurgePerformanceWarning:
    """Test performance warning exceptions."""

    def test_performance_warning(self) -> None:
        """Test SplurgePerformanceWarning."""
        warning = SplurgePerformanceWarning("Performance issue", details="Large file may cause memory issues")
        assert isinstance(warning, SplurgeToolsError)
        assert warning.message == "Performance issue"
        assert warning.details == "Large file may cause memory issues"


class TestExceptionHierarchy:
    """Test the exception hierarchy and inheritance."""

    def test_exception_hierarchy(self) -> None:
        """Test that all exceptions properly inherit from the base class."""
        exceptions = [
            SplurgeValidationError("test"),
            SplurgeFileOperationError("test"),
            SplurgeDataProcessingError("test"),
            SplurgeConfigurationError("test"),
            SplurgeResourceError("test"),
            SplurgePerformanceWarning("test"),
            SplurgeParameterError("test"),
            SplurgeRangeError("test"),
            SplurgeFormatError("test"),
            SplurgeFileNotFoundError("test"),
            SplurgeFilePermissionError("test"),
            SplurgeFileEncodingError("test"),
            SplurgePathValidationError("test"),
            SplurgeParsingError("test"),
            SplurgeTypeConversionError("test"),
            SplurgeStreamingError("test"),
            SplurgeResourceAcquisitionError("test"),
            SplurgeResourceReleaseError("test"),
        ]

        for exc in exceptions:
            assert isinstance(exc, SplurgeToolsError)
            assert isinstance(exc, Exception)

    def test_specific_inheritance(self) -> None:
        """Test specific inheritance relationships."""
        # Test validation errors
        param_error = SplurgeParameterError("test")
        range_error = SplurgeRangeError("test")
        format_error = SplurgeFormatError("test")

        assert isinstance(param_error, SplurgeValidationError)
        assert isinstance(range_error, SplurgeValidationError)
        assert isinstance(format_error, SplurgeValidationError)

        # Test file operation errors
        file_not_found = SplurgeFileNotFoundError("test")
        file_permission = SplurgeFilePermissionError("test")
        file_encoding = SplurgeFileEncodingError("test")
        path_validation = SplurgePathValidationError("test")

        assert isinstance(file_not_found, SplurgeFileOperationError)
        assert isinstance(file_permission, SplurgeFileOperationError)
        assert isinstance(file_encoding, SplurgeFileOperationError)
        assert isinstance(path_validation, SplurgeFileOperationError)

        # Test data processing errors
        parsing_error = SplurgeParsingError("test")
        type_error = SplurgeTypeConversionError("test")
        streaming_error = SplurgeStreamingError("test")

        assert isinstance(parsing_error, SplurgeDataProcessingError)
        assert isinstance(type_error, SplurgeDataProcessingError)
        assert isinstance(streaming_error, SplurgeDataProcessingError)

        # Test resource errors
        acquisition_error = SplurgeResourceAcquisitionError("test")
        release_error = SplurgeResourceReleaseError("test")

        assert isinstance(acquisition_error, SplurgeResourceError)
        assert isinstance(release_error, SplurgeResourceError)
