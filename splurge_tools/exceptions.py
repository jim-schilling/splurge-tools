"""
Custom exceptions for splurge-tools package.

This module provides a hierarchy of custom exceptions for better error handling
and more specific error messages throughout the package.

Copyright (c) 2025 Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

# No typing imports needed


class SplurgeToolsError(Exception):
    """Base exception for all splurge-tools errors."""

    def __init__(
        self,
        message: str,
        *,
        details: str | None = None,
    ) -> None:
        """
        Initialize SplurgeToolsError.

        Args:
            message: Primary error message
            details: Additional error details
        """
        self.message = message
        self.details = details
        super().__init__(self.message)


class SplurgeValidationError(SplurgeToolsError):
    """Raised when data validation fails."""


class SplurgeFileOperationError(SplurgeToolsError):
    """Base exception for file operation errors."""


class SplurgeFileNotFoundError(SplurgeFileOperationError):
    """Raised when a file is not found."""


class SplurgeFilePermissionError(SplurgeFileOperationError):
    """Raised when there are permission issues with file operations."""


class SplurgeFileEncodingError(SplurgeFileOperationError):
    """Raised when there are encoding issues with file operations."""


class SplurgePathValidationError(SplurgeFileOperationError):
    """Raised when file path validation fails."""


class SplurgeDataProcessingError(SplurgeToolsError):
    """Base exception for data processing errors."""


class SplurgeParsingError(SplurgeDataProcessingError):
    """Raised when data parsing fails."""


class SplurgeTypeConversionError(SplurgeDataProcessingError):
    """Raised when type conversion fails."""


class SplurgeStreamingError(SplurgeDataProcessingError):
    """Raised when streaming operations fail."""


class SplurgeConfigurationError(SplurgeToolsError):
    """Raised when configuration is invalid."""


class SplurgeResourceError(SplurgeToolsError):
    """Base exception for resource management errors."""


class SplurgeResourceAcquisitionError(SplurgeResourceError):
    """Raised when resource acquisition fails."""


class SplurgeResourceReleaseError(SplurgeResourceError):
    """Raised when resource release fails."""


class SplurgePerformanceWarning(SplurgeToolsError):
    """Warning for performance-related issues."""


class SplurgeParameterError(SplurgeValidationError):
    """Raised when function parameters are invalid."""


class SplurgeRangeError(SplurgeValidationError):
    """Raised when values are outside expected ranges."""


class SplurgeFormatError(SplurgeValidationError):
    """Raised when data format is invalid."""
