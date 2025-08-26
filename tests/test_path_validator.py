"""
Tests for the path_validator module.

Tests all public methods of the PathValidator class including
path validation, security checks, and filename sanitization.
"""

import os
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from splurge_tools.exceptions import (
    SplurgePathValidationError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError
)
from splurge_tools.path_validator import PathValidator


class TestPathValidatorValidatePath:
    """Test the validate_path method."""

    def test_validate_existing_file(self, tmp_path: Path) -> None:
        """Test validating an existing file."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        result = PathValidator.validate_path(
            test_file,
            must_exist=True,
            must_be_file=True,
            must_be_readable=True
        )
        assert result == test_file.resolve()

    def test_validate_nonexistent_file_not_required(self, tmp_path: Path) -> None:
        """Test validating a non-existent file when not required."""
        test_file = tmp_path / "nonexistent.txt"
        
        result = PathValidator.validate_path(test_file, must_exist=False)
        assert result == test_file.resolve()

    def test_validate_nonexistent_file_required_raises_error(self, tmp_path: Path) -> None:
        """Test that validating non-existent file raises error when required."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            PathValidator.validate_path(test_file, must_exist=True)

    def test_validate_directory_as_file_raises_error(self, tmp_path: Path) -> None:
        """Test that validating directory as file raises error."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        
        with pytest.raises(SplurgePathValidationError):
            PathValidator.validate_path(test_dir, must_be_file=True)

    def test_validate_relative_path_allowed(self, tmp_path: Path) -> None:
        """Test validating relative path when allowed."""
        # Skip this test on Windows due to temp directory cleanup issues
        import platform
        if platform.system() == "Windows":
            pytest.skip("Relative path test not reliable on Windows")
        
        with tempfile.TemporaryDirectory() as temp_dir:
            os.chdir(temp_dir)
            test_file = Path("relative.txt")
            test_file.write_text("test")
            
            result = PathValidator.validate_path(test_file, allow_relative=True)
            assert result == test_file.resolve()

    def test_validate_relative_path_not_allowed_raises_error(self, tmp_path: Path) -> None:
        """Test that relative path raises error when not allowed."""
        test_file = Path("relative.txt")
        
        with pytest.raises(SplurgePathValidationError):
            PathValidator.validate_path(test_file, allow_relative=False)

    def test_validate_with_base_directory(self, tmp_path: Path) -> None:
        """Test validating path with base directory."""
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        
        test_file = base_dir / "test.txt"
        test_file.write_text("test content")
        
        relative_path = Path("test.txt")
        result = PathValidator.validate_path(
            relative_path,
            base_directory=base_dir,
            must_exist=True
        )
        assert result == test_file.resolve()

    def test_validate_path_outside_base_directory_raises_error(self, tmp_path: Path) -> None:
        """Test that path outside base directory raises error."""
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        
        outside_file = tmp_path / "outside.txt"
        outside_file.write_text("test")
        
        with pytest.raises(SplurgePathValidationError):
            PathValidator.validate_path(
                outside_file,
                base_directory=base_dir,
                must_exist=True
            )

    def test_validate_absolute_path_with_base_directory(self, tmp_path: Path) -> None:
        """Test validating absolute path with base directory."""
        base_dir = tmp_path / "base"
        base_dir.mkdir()
        
        test_file = base_dir / "test.txt"
        test_file.write_text("test content")
        
        result = PathValidator.validate_path(
            test_file,
            base_directory=base_dir,
            must_exist=True
        )
        assert result == test_file.resolve()

    def test_validate_path_too_long_raises_error(self) -> None:
        """Test that very long path raises error."""
        long_path = "a" * (PathValidator.MAX_PATH_LENGTH + 1)
        
        with pytest.raises(SplurgePathValidationError):
            PathValidator.validate_path(long_path)

    def test_validate_path_with_dangerous_characters_raises_error(self) -> None:
        """Test that path with dangerous characters raises error."""
        dangerous_paths = [
            "file<.txt",
            "file>.txt",
            "file\".txt",
            "file|.txt",
            "file?.txt",
            "file*.txt",
            "file\x00.txt",
            "file\x01.txt"
        ]
        
        for path in dangerous_paths:
            with pytest.raises(SplurgePathValidationError):
                PathValidator.validate_path(path)

    def test_validate_path_with_traversal_patterns_raises_error(self) -> None:
        """Test that path with traversal patterns raises error."""
        traversal_paths = [
            "../file.txt",
            "..\\file.txt",
            "file/../file.txt",
            "file\\..\\file.txt",
            "//file.txt",
            "\\\\file.txt",
            "~/.file.txt"
        ]
        
        for path in traversal_paths:
            with pytest.raises(SplurgePathValidationError):
                PathValidator.validate_path(path)

    def test_validate_windows_drive_letter(self) -> None:
        """Test validating Windows drive letter path."""
        with patch('pathlib.Path.resolve') as mock_resolve:
            mock_resolve.return_value = Path("C:/test/file.txt")
            
            result = PathValidator.validate_path("C:/test/file.txt")
            assert result == Path("C:/test/file.txt")

    def test_validate_invalid_colon_usage_raises_error(self) -> None:
        """Test that invalid colon usage raises error."""
        invalid_paths = [
            "file:name.txt",
            ":file.txt",
            "file.txt:",
            "C:file.txt",  # Missing slash
            "file:C.txt"
        ]
        
        for path in invalid_paths:
            with pytest.raises(SplurgePathValidationError):
                PathValidator.validate_path(path)

    def test_validate_unreadable_file_raises_error(self, tmp_path: Path) -> None:
        """Test that unreadable file raises error."""
        import platform
        
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        # Make file unreadable
        os.chmod(test_file, 0o000)
        
        try:
            with pytest.raises(SplurgeFilePermissionError):
                PathValidator.validate_path(test_file, must_be_readable=True)
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)

    def test_validate_nonexistent_file_readable_raises_error(self, tmp_path: Path) -> None:
        """Test that checking readability of non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            PathValidator.validate_path(test_file, must_be_readable=True)


class TestPathValidatorSanitizeFilename:
    """Test the sanitize_filename method."""

    def test_sanitize_windows_reserved_characters(self) -> None:
        """Test sanitizing Windows reserved characters."""
        test_cases = [
            ("file<name.txt", "file_name.txt"),
            ("file>name.txt", "file_name.txt"),
            ("file:name.txt", "file_name.txt"),
            ('file"name.txt', "file_name.txt"),
            ("file|name.txt", "file_name.txt"),
            ("file?name.txt", "file_name.txt"),
            ("file*name.txt", "file_name.txt")
        ]
        
        for original, expected in test_cases:
            result = PathValidator.sanitize_filename(original)
            assert result == expected

    def test_sanitize_control_characters(self) -> None:
        """Test sanitizing control characters."""
        result = PathValidator.sanitize_filename("file\x00\x01\x02name.txt")
        assert result == "filename.txt"

    def test_sanitize_leading_trailing_spaces_and_dots(self) -> None:
        """Test sanitizing leading/trailing spaces and dots."""
        test_cases = [
            ("  filename.txt  ", "filename.txt"),
            ("...filename.txt...", "filename.txt"),
            ("  ...filename.txt...  ", "filename.txt")
        ]
        
        for original, expected in test_cases:
            result = PathValidator.sanitize_filename(original)
            assert result == expected

    def test_sanitize_empty_string_returns_default(self) -> None:
        """Test that empty string returns default filename."""
        result = PathValidator.sanitize_filename("")
        assert result == "unnamed_file"

    def test_sanitize_whitespace_only_returns_default(self) -> None:
        """Test that whitespace-only string returns default filename."""
        result = PathValidator.sanitize_filename("   ")
        assert result == "unnamed_file"

    def test_sanitize_dots_only_returns_default(self) -> None:
        """Test that dots-only string returns default filename."""
        result = PathValidator.sanitize_filename("...")
        assert result == "unnamed_file"

    def test_sanitize_valid_filename_unchanged(self) -> None:
        """Test that valid filename is unchanged."""
        valid_names = [
            "filename.txt",
            "file-name.txt",
            "file_name.txt",
            "file123.txt",
            "file.txt",
            "file"
        ]
        
        for name in valid_names:
            result = PathValidator.sanitize_filename(name)
            assert result == name

    def test_sanitize_mixed_invalid_characters(self) -> None:
        """Test sanitizing filename with mixed invalid characters."""
        result = PathValidator.sanitize_filename("file<name>with:invalid|chars?.txt")
        assert result == "file_name_with_invalid_chars_.txt"


class TestPathValidatorIsSafePath:
    """Test the is_safe_path method."""

    def test_is_safe_path_valid_path(self, tmp_path: Path) -> None:
        """Test that valid path returns True."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        assert PathValidator.is_safe_path(test_file) is True

    def test_is_safe_path_dangerous_characters(self) -> None:
        """Test that path with dangerous characters returns False."""
        dangerous_paths = [
            "file<.txt",
            "file>.txt",
            "file\".txt",
            "file|.txt",
            "file?.txt",
            "file*.txt"
        ]
        
        for path in dangerous_paths:
            assert PathValidator.is_safe_path(path) is False

    def test_is_safe_path_traversal_patterns(self) -> None:
        """Test that path with traversal patterns returns False."""
        traversal_paths = [
            "../file.txt",
            "..\\file.txt",
            "file/../file.txt",
            "file\\..\\file.txt",
            "//file.txt",
            "\\\\file.txt"
        ]
        
        for path in traversal_paths:
            assert PathValidator.is_safe_path(path) is False

    def test_is_safe_path_too_long(self) -> None:
        """Test that very long path returns False."""
        long_path = "a" * (PathValidator.MAX_PATH_LENGTH + 1)
        assert PathValidator.is_safe_path(long_path) is False

    def test_is_safe_path_nonexistent_file(self, tmp_path: Path) -> None:
        """Test that non-existent file returns True (if path is safe)."""
        test_file = tmp_path / "nonexistent.txt"
        assert PathValidator.is_safe_path(test_file) is True

    def test_is_safe_path_invalid_colon_usage(self) -> None:
        """Test that invalid colon usage returns False."""
        invalid_paths = [
            "file:name.txt",
            ":file.txt",
            "file.txt:",
            "C:file.txt"
        ]
        
        for path in invalid_paths:
            assert PathValidator.is_safe_path(path) is False


class TestPathValidatorEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_validate_path_with_symlinks(self, tmp_path: Path) -> None:
        """Test validating path with symlinks."""
        import platform
        
        # Skip this test on Windows as symlink creation requires elevated privileges
        if platform.system() == "Windows":
            pytest.skip("Symlink test requires elevated privileges on Windows")
        
        original_file = tmp_path / "original.txt"
        original_file.write_text("original content")
        
        symlink_file = tmp_path / "symlink.txt"
        symlink_file.symlink_to(original_file)
        
        result = PathValidator.validate_path(symlink_file, must_exist=True)
        assert result == symlink_file.resolve()

    def test_validate_path_with_unicode_characters(self, tmp_path: Path) -> None:
        """Test validating path with Unicode characters."""
        unicode_file = tmp_path / "αβγ.txt"
        unicode_file.write_text("unicode content")
        
        result = PathValidator.validate_path(unicode_file, must_exist=True)
        assert result == unicode_file.resolve()

    def test_validate_path_with_spaces(self, tmp_path: Path) -> None:
        """Test validating path with spaces."""
        spaced_file = tmp_path / "file with spaces.txt"
        spaced_file.write_text("content with spaces")
        
        result = PathValidator.validate_path(spaced_file, must_exist=True)
        assert result == spaced_file.resolve()

    def test_sanitize_filename_with_unicode(self) -> None:
        """Test sanitizing filename with Unicode characters."""
        result = PathValidator.sanitize_filename("αβγ<>.txt")
        assert result == "αβγ__.txt"

    def test_sanitize_filename_with_mixed_unicode_and_invalid(self) -> None:
        """Test sanitizing filename with mixed Unicode and invalid characters."""
        result = PathValidator.sanitize_filename("αβγ<file>name:with|invalid?.txt")
        assert result == "αβγ_file_name_with_invalid_.txt"

    def test_validate_path_resolution_error(self) -> None:
        """Test handling of path resolution errors."""
        with patch('pathlib.Path.resolve') as mock_resolve:
            mock_resolve.side_effect = RuntimeError("Resolution failed")
            
            with pytest.raises(SplurgePathValidationError):
                PathValidator.validate_path("test.txt")

    def test_validate_path_os_error(self) -> None:
        """Test handling of OS errors during validation."""
        with patch('pathlib.Path.resolve') as mock_resolve:
            mock_resolve.side_effect = OSError("OS error")
            
            with pytest.raises(SplurgePathValidationError):
                PathValidator.validate_path("test.txt")
