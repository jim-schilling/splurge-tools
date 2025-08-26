"""
Tests for the resource_manager module.

Tests all public classes and context managers including
file operations, temporary files, and stream management.
"""

import os
from pathlib import Path

import pytest

from splurge_tools.exceptions import (
    SplurgeResourceAcquisitionError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError,
    SplurgePathValidationError
)
from splurge_tools.resource_manager import (
    ResourceManager,
    FileResourceManager,
    StreamResourceManager,
    safe_file_operation,
    safe_stream_operation
)


class TestResourceManager:
    """Test the base ResourceManager class."""

    def test_init(self) -> None:
        """Test ResourceManager initialization."""
        manager = ResourceManager()
        assert not manager.is_acquired()
        assert manager._resource is None

    def test_acquire_not_implemented(self) -> None:
        """Test that acquire raises NotImplementedError when _create_resource is not implemented."""
        manager = ResourceManager()
        
        with pytest.raises(NotImplementedError):
            manager.acquire()

    def test_release_not_acquired(self) -> None:
        """Test releasing when not acquired."""
        manager = ResourceManager()
        # Should not raise an error
        manager.release()

    def test_is_acquired_initial_state(self) -> None:
        """Test initial acquired state."""
        manager = ResourceManager()
        assert not manager.is_acquired()


class TestFileResourceManager:
    """Test the FileResourceManager class."""

    def test_init_with_string_path(self, tmp_path: Path) -> None:
        """Test initialization with string path."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        manager = FileResourceManager(str(test_file))
        assert manager.file_path == test_file
        assert manager.mode == "r"
        assert manager.encoding == "utf-8"

    def test_init_with_path_object(self, tmp_path: Path) -> None:
        """Test initialization with Path object."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        manager = FileResourceManager(test_file)
        assert manager.file_path == test_file

    def test_init_with_custom_parameters(self, tmp_path: Path) -> None:
        """Test initialization with custom parameters."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("content")
        
        manager = FileResourceManager(
            test_file,
            mode="w",
            encoding="utf-16",
            errors="ignore",
            newline="\r\n",
            buffering=1024
        )
        assert manager.mode == "w"
        assert manager.encoding == "utf-16"
        assert manager.errors == "ignore"
        assert manager.newline == "\r\n"
        assert manager.buffering == 1024

    def test_context_manager_text_mode(self, tmp_path: Path) -> None:
        """Test context manager with text mode."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with FileResourceManager(test_file, mode="r") as file_handle:
            content = file_handle.read()
            assert content == "test content"

    def test_context_manager_binary_mode(self, tmp_path: Path) -> None:
        """Test context manager with binary mode."""
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"binary content")
        
        with FileResourceManager(test_file, mode="rb") as file_handle:
            content = file_handle.read()
            assert content == b"binary content"

    def test_context_manager_write_mode(self, tmp_path: Path) -> None:
        """Test context manager with write mode."""
        test_file = tmp_path / "write_test.txt"
        
        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write("written content")
        
        assert test_file.read_text() == "written content"

    def test_context_manager_append_mode(self, tmp_path: Path) -> None:
        """Test context manager with append mode."""
        test_file = tmp_path / "append_test.txt"
        test_file.write_text("original content")
        
        with FileResourceManager(test_file, mode="a") as file_handle:
            file_handle.write(" appended content")
        
        assert test_file.read_text() == "original content appended content"

    def test_nonexistent_file_read_mode_raises_error(self, tmp_path: Path) -> None:
        """Test that non-existent file raises error in read mode."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            with FileResourceManager(test_file, mode="r"):
                pass

    def test_nonexistent_file_write_mode_succeeds(self, tmp_path: Path) -> None:
        """Test that non-existent file succeeds in write mode."""
        test_file = tmp_path / "new_file.txt"
        
        with FileResourceManager(test_file, mode="w") as file_handle:
            file_handle.write("new content")
        
        assert test_file.read_text() == "new content"

    def test_file_permission_error(self, tmp_path: Path) -> None:
        """Test file permission error."""
        import platform
        
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")
        
        test_file = tmp_path / "permission_test.txt"
        test_file.write_text("content")

        # Make file unreadable
        os.chmod(test_file, 0o000)
        
        try:
            with pytest.raises(SplurgeFilePermissionError):
                with FileResourceManager(test_file, mode="r"):
                    pass
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)

    def test_encoding_error(self, tmp_path: Path) -> None:
        """Test encoding error."""
        import platform
        
        # Skip this test on Windows as encoding error handling may differ
        if platform.system() == "Windows":
            pytest.skip("Encoding error test not reliable on Windows")
        
        test_file = tmp_path / "encoding_test.txt"
        # Write binary data that's not valid UTF-8
        test_file.write_bytes(b"valid text\n\xff\xfe\nmore text")
        
        with pytest.raises(SplurgeFileEncodingError):
            with FileResourceManager(test_file, mode="r"):
                pass

    def test_invalid_path_raises_error(self) -> None:
        """Test that invalid path raises error."""
        with pytest.raises(SplurgePathValidationError):
            FileResourceManager("file<with>invalid:chars?.txt")

    def test_directory_path_raises_error(self, tmp_path: Path) -> None:
        """Test that directory path raises error."""
        test_dir = tmp_path / "testdir"
        test_dir.mkdir()
        
        with pytest.raises(SplurgePathValidationError):
            FileResourceManager(test_dir, mode="r")


class TestStreamResourceManager:
    """Test the StreamResourceManager class."""

    def test_init_default_parameters(self) -> None:
        """Test initialization with default parameters."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream)
        assert manager.stream == stream
        assert manager.auto_close is True
        assert not manager.is_closed

    def test_init_custom_parameters(self) -> None:
        """Test initialization with custom parameters."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream, auto_close=False)
        assert manager.stream == stream
        assert manager.auto_close is False

    def test_context_manager_basic(self) -> None:
        """Test basic context manager functionality."""
        stream = iter([1, 2, 3])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

    def test_context_manager_with_closeable_stream(self) -> None:
        """Test context manager with closeable stream."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]
        
        assert stream.closed

    def test_context_manager_without_auto_close(self) -> None:
        """Test context manager without auto close."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        with StreamResourceManager(stream, auto_close=False) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]
        
        assert not stream.closed

    def test_context_manager_with_non_closeable_stream(self) -> None:
        """Test context manager with non-closeable stream."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream)
        assert not manager.is_closed
        
        with manager as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]
        
        # Should be marked as closed after context manager exits
        assert manager.is_closed

    def test_is_closed_property(self) -> None:
        """Test is_closed property."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        manager = StreamResourceManager(stream)
        assert not manager.is_closed
        
        with manager:
            pass
        
        assert manager.is_closed


class TestSafeFileOperation:
    """Test the safe_file_operation context manager."""

    def test_safe_file_operation_read(self, tmp_path: Path) -> None:
        """Test safe file operation for reading."""
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with safe_file_operation(test_file, mode="r") as file_handle:
            content = file_handle.read()
            assert content == "test content"

    def test_safe_file_operation_write(self, tmp_path: Path) -> None:
        """Test safe file operation for writing."""
        test_file = tmp_path / "write_test.txt"
        
        with safe_file_operation(test_file, mode="w") as file_handle:
            file_handle.write("written content")
        
        assert test_file.read_text() == "written content"

    def test_safe_file_operation_with_encoding(self, tmp_path: Path) -> None:
        """Test safe file operation with custom encoding."""
        test_file = tmp_path / "utf16_test.txt"
        content = "test content"
        test_file.write_text(content, encoding='utf-16')
        
        with safe_file_operation(test_file, mode="r", encoding='utf-16') as file_handle:
            read_content = file_handle.read()
            assert read_content == content

    def test_safe_file_operation_nonexistent_file_raises_error(self, tmp_path: Path) -> None:
        """Test that non-existent file raises error."""
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            with safe_file_operation(test_file, mode="r"):
                pass


class TestSafeStreamOperation:
    """Test the safe_stream_operation context manager."""

    def test_safe_stream_operation_basic(self) -> None:
        """Test basic safe stream operation."""
        stream = iter([1, 2, 3])
        with safe_stream_operation(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]

    def test_safe_stream_operation_with_closeable_stream(self) -> None:
        """Test safe stream operation with closeable stream."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        with safe_stream_operation(stream) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]
        
        assert stream.closed

    def test_safe_stream_operation_without_auto_close(self) -> None:
        """Test safe stream operation without auto close."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        with safe_stream_operation(stream, auto_close=False) as managed_stream:
            items = list(managed_stream)
            assert items == [1, 2, 3]
        
        assert not stream.closed


class TestSafeOpenFile:
    """Test the _safe_open_file helper function."""

    def test_safe_open_file_text_mode(self, tmp_path: Path) -> None:
        """Test safe file opening in text mode."""
        from splurge_tools.resource_manager import _safe_open_file
        
        test_file = tmp_path / "test.txt"
        test_file.write_text("test content")
        
        with _safe_open_file(test_file, mode="r", encoding="utf-8") as file_handle:
            content = file_handle.read()
            assert content == "test content"

    def test_safe_open_file_binary_mode(self, tmp_path: Path) -> None:
        """Test safe file opening in binary mode."""
        from splurge_tools.resource_manager import _safe_open_file
        
        test_file = tmp_path / "test.bin"
        test_file.write_bytes(b"binary content")
        
        with _safe_open_file(test_file, mode="rb") as file_handle:
            content = file_handle.read()
            assert content == b"binary content"

    def test_safe_open_file_nonexistent_raises_error(self, tmp_path: Path) -> None:
        """Test that non-existent file raises SplurgeFileNotFoundError."""
        from splurge_tools.resource_manager import _safe_open_file
        
        test_file = tmp_path / "nonexistent.txt"
        
        with pytest.raises(SplurgeFileNotFoundError):
            with _safe_open_file(test_file, mode="r"):
                pass

    def test_safe_open_file_invalid_path_raises_error(self) -> None:
        """Test that invalid path raises SplurgeResourceAcquisitionError."""
        from splurge_tools.resource_manager import _safe_open_file
        
        # Invalid characters in filename cause OSError which gets converted to SplurgeResourceAcquisitionError
        with pytest.raises(SplurgeResourceAcquisitionError):
            with _safe_open_file(Path("file<with>invalid:chars?.txt"), mode="r"):
                pass


class TestResourceManagerEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_file_resource_manager_with_unicode_path(self, tmp_path: Path) -> None:
        """Test file resource manager with Unicode path."""
        unicode_file = tmp_path / "αβγ.txt"
        unicode_file.write_text("unicode content")
        
        with FileResourceManager(unicode_file) as file_handle:
            content = file_handle.read()
            assert content == "unicode content"

    def test_file_resource_manager_with_spaces_in_path(self, tmp_path: Path) -> None:
        """Test file resource manager with spaces in path."""
        spaced_file = tmp_path / "file with spaces.txt"
        spaced_file.write_text("content with spaces")
        
        with FileResourceManager(spaced_file) as file_handle:
            content = file_handle.read()
            assert content == "content with spaces"

    def test_stream_resource_manager_with_empty_stream(self) -> None:
        """Test stream resource manager with empty stream."""
        stream = iter([])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert items == []

    def test_stream_resource_manager_with_large_stream(self) -> None:
        """Test stream resource manager with large stream."""
        stream = iter(range(1000))
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            assert len(items) == 1000
            assert items[0] == 0
            assert items[-1] == 999

    def test_file_resource_manager_concurrent_access(self, tmp_path: Path) -> None:
        """Test file resource manager with concurrent access."""
        test_file = tmp_path / "concurrent.txt"
        test_file.write_text("original content")
        
        # This should work without issues
        with FileResourceManager(test_file, mode="r") as file1:
            with FileResourceManager(test_file, mode="r") as file2:
                content1 = file1.read()
                content2 = file2.read()
                assert content1 == content2 == "original content"

    def test_file_resource_manager_error_handling(self, tmp_path: Path) -> None:
        """Test file resource manager error handling."""
        import platform
        
        # Skip this test on Windows as chmod(0o000) doesn't make files unreadable
        if platform.system() == "Windows":
            pytest.skip("File permission test not reliable on Windows")
        
        test_file = tmp_path / "error_test.txt"
        test_file.write_text("content")
        
        # Make file unreadable
        os.chmod(test_file, 0o000)
        
        try:
            with pytest.raises(SplurgeFilePermissionError):
                with FileResourceManager(test_file, mode="r"):
                    pass
        finally:
            # Restore permissions
            os.chmod(test_file, 0o644)
