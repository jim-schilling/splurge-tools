"""
Tests for the PathValidator module.

This module tests the path validation utilities for secure file operations.
"""

import os
import tempfile
import unittest
from pathlib import Path

from splurge_tools.path_validator import PathValidator
from splurge_tools.exceptions import (
    SplurgePathValidationError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError
)


class TestPathValidator(unittest.TestCase):
    """Test cases for PathValidator class."""

    def setUp(self):
        """Set up test fixtures."""
        self.temp_dir = tempfile.mkdtemp()
        self.temp_file = tempfile.NamedTemporaryFile(
            dir=self.temp_dir,
            delete=False,
            suffix='.txt'
        )
        self.temp_file.write(b"test content")
        self.temp_file.close()

    def tearDown(self):
        """Clean up test fixtures."""
        try:
            os.unlink(self.temp_file.name)
            os.rmdir(self.temp_dir)
        except (OSError, FileNotFoundError):
            pass

    def test_validate_path_basic_valid_path(self):
        """Test basic valid path validation."""
        result = PathValidator.validate_path(self.temp_file.name)
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path(self.temp_file.name).resolve())

    def test_validate_path_with_string_input(self):
        """Test path validation with string input."""
        result = PathValidator.validate_path(str(self.temp_file.name))
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path(self.temp_file.name).resolve())

    def test_validate_path_with_path_input(self):
        """Test path validation with Path input."""
        result = PathValidator.validate_path(Path(self.temp_file.name))
        self.assertIsInstance(result, Path)
        self.assertEqual(result, Path(self.temp_file.name).resolve())

    def test_validate_path_must_exist_true(self):
        """Test path validation with must_exist=True."""
        result = PathValidator.validate_path(
            self.temp_file.name,
            must_exist=True
        )
        self.assertIsInstance(result, Path)
        self.assertTrue(result.exists())

    def test_validate_path_must_exist_false(self):
        """Test path validation with must_exist=False."""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.txt")
        result = PathValidator.validate_path(
            non_existent_path,
            must_exist=False
        )
        self.assertIsInstance(result, Path)
        self.assertFalse(result.exists())

    def test_validate_path_must_exist_true_file_not_found(self):
        """Test path validation with must_exist=True for non-existent file."""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.txt")
        with self.assertRaises(SplurgeFileNotFoundError):
            PathValidator.validate_path(
                non_existent_path,
                must_exist=True
            )

    def test_validate_path_must_be_file_true(self):
        """Test path validation with must_be_file=True."""
        result = PathValidator.validate_path(
            self.temp_file.name,
            must_be_file=True
        )
        self.assertIsInstance(result, Path)
        self.assertTrue(result.is_file())

    def test_validate_path_must_be_file_true_directory(self):
        """Test path validation with must_be_file=True for directory."""
        with self.assertRaises(SplurgePathValidationError):
            PathValidator.validate_path(
                self.temp_dir,
                must_be_file=True
            )

    def test_validate_path_must_be_readable_true(self):
        """Test path validation with must_be_readable=True."""
        result = PathValidator.validate_path(
            self.temp_file.name,
            must_be_readable=True
        )
        self.assertIsInstance(result, Path)
        self.assertTrue(os.access(result, os.R_OK))

    def test_validate_path_must_be_readable_true_file_not_found(self):
        """Test path validation with must_be_readable=True for non-existent file."""
        non_existent_path = os.path.join(self.temp_dir, "nonexistent.txt")
        with self.assertRaises(SplurgeFileNotFoundError):
            PathValidator.validate_path(
                non_existent_path,
                must_be_readable=True
            )

    def test_validate_path_allow_relative_true(self):
        """Test path validation with allow_relative=True."""
        relative_path = "relative_file.txt"
        result = PathValidator.validate_path(
            relative_path,
            allow_relative=True
        )
        self.assertIsInstance(result, Path)

    def test_validate_path_allow_relative_false(self):
        """Test path validation with allow_relative=False."""
        relative_path = "relative_file.txt"
        with self.assertRaises(SplurgePathValidationError):
            PathValidator.validate_path(
                relative_path,
                allow_relative=False
            )

    def test_validate_path_with_base_directory(self):
        """Test path validation with base directory."""
        relative_path = "test_file.txt"
        result = PathValidator.validate_path(
            relative_path,
            base_directory=self.temp_dir
        )
        self.assertIsInstance(result, Path)
        self.assertTrue(str(result).startswith(str(Path(self.temp_dir).resolve())))

    def test_validate_path_with_base_directory_outside_base(self):
        """Test path validation with path outside base directory."""
        # Create a path that would resolve outside the base directory
        outside_path = os.path.join(self.temp_dir, "..", "outside.txt")
        with self.assertRaises(SplurgePathValidationError):
            PathValidator.validate_path(
                outside_path,
                base_directory=self.temp_dir
            )

    def test_validate_path_dangerous_characters(self):
        """Test path validation with dangerous characters."""
        dangerous_paths = [
            "file<.txt",
            "file>.txt",
            "file\".txt",
            "file|.txt",
            "file?.txt",
            "file*.txt",
            "file\x00.txt",
            "file\x01.txt",
        ]
        
        for path in dangerous_paths:
            with self.assertRaises(SplurgePathValidationError):
                PathValidator.validate_path(path)

    def test_validate_path_windows_drive_letter_valid(self):
        """Test path validation with valid Windows drive letters."""
        valid_drive_paths = [
            "C:",
            "C:\\",
            "C:\\file.txt",
            "D:file.txt",
        ]
        
        for path in valid_drive_paths:
            try:
                result = PathValidator.validate_path(path)
                self.assertIsInstance(result, Path)
            except SplurgePathValidationError:
                # On non-Windows systems, this might fail, which is expected
                pass

    def test_validate_path_windows_drive_letter_invalid(self):
        """Test path validation with invalid Windows drive letters."""
        invalid_drive_paths = [
            "1:file.txt",  # Invalid drive letter
            ":file.txt",   # No drive letter
            "file:txt",    # Colon in middle
        ]
        
        for path in invalid_drive_paths:
            with self.assertRaises(SplurgePathValidationError):
                PathValidator.validate_path(path)

    def test_validate_path_traversal_patterns(self):
        """Test path validation with path traversal patterns."""
        traversal_paths = [
            "file..txt",  # Contains '..'
            "..\\file.txt",  # Contains '..'
            "file~file.txt",  # Contains '~'
        ]
        
        for path in traversal_paths:
            with self.assertRaises(SplurgePathValidationError):
                PathValidator.validate_path(path)

    def test_validate_path_length_limit(self):
        """Test path validation with path length limit."""
        # Create a path that exceeds the maximum length
        long_path = "a" * 5000
        with self.assertRaises(SplurgePathValidationError):
            PathValidator.validate_path(long_path)

    def test_validate_path_resolution_error(self):
        """Test path validation with resolution error."""
        # This test might behave differently on different systems
        # We'll test with a path that might cause resolution issues
        problematic_path = "\\\\.\\COM1"  # Windows device path
        try:
            PathValidator.validate_path(problematic_path)
        except SplurgePathValidationError:
            # Expected on some systems
            pass

    def test_sanitize_filename_basic(self):
        """Test basic filename sanitization."""
        result = PathValidator.sanitize_filename("test_file.txt")
        self.assertEqual(result, "test_file.txt")

    def test_sanitize_filename_dangerous_characters(self):
        """Test filename sanitization with dangerous characters."""
        result = PathValidator.sanitize_filename("file<>.txt")
        self.assertEqual(result, "file__.txt")

    def test_sanitize_filename_control_characters(self):
        """Test filename sanitization with control characters."""
        result = PathValidator.sanitize_filename("file\x00\x01.txt")
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_leading_trailing_spaces(self):
        """Test filename sanitization with leading/trailing spaces."""
        result = PathValidator.sanitize_filename("  file.txt  ")
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_leading_trailing_dots(self):
        """Test filename sanitization with leading/trailing dots."""
        result = PathValidator.sanitize_filename("...file.txt...")
        self.assertEqual(result, "file.txt")

    def test_sanitize_filename_empty_after_sanitization(self):
        """Test filename sanitization with empty result."""
        result = PathValidator.sanitize_filename("...")
        self.assertEqual(result, "unnamed_file")

    def test_sanitize_filename_completely_empty(self):
        """Test filename sanitization with completely empty input."""
        result = PathValidator.sanitize_filename("")
        self.assertEqual(result, "unnamed_file")

    def test_is_safe_path_valid_path(self):
        """Test is_safe_path with valid path."""
        result = PathValidator.is_safe_path(self.temp_file.name)
        self.assertTrue(result)

    def test_is_safe_path_invalid_path(self):
        """Test is_safe_path with invalid path."""
        result = PathValidator.is_safe_path("file<>.txt")
        self.assertFalse(result)

    def test_is_safe_path_traversal_pattern(self):
        """Test is_safe_path with traversal pattern."""
        result = PathValidator.is_safe_path("file..txt")
        self.assertFalse(result)

    def test_is_safe_path_non_existent_file(self):
        """Test is_safe_path with non-existent file."""
        result = PathValidator.is_safe_path("nonexistent.txt")
        self.assertTrue(result)  # Should be True since we're not checking existence

    def test_is_safe_path_with_path_object(self):
        """Test is_safe_path with Path object."""
        result = PathValidator.is_safe_path(Path(self.temp_file.name))
        self.assertTrue(result)


if __name__ == "__main__":
    unittest.main()
