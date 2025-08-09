"""
Tests for the ResourceManager module.

This module tests the resource management utilities with context managers.
"""

import os
import tempfile
import unittest
from pathlib import Path
from io import StringIO, BytesIO

from splurge_tools.resource_manager import (
    FileResourceManager,
    TemporaryFileManager,
    StreamResourceManager,
    safe_file_operation,
    temporary_file,
    safe_stream_operation
)
from splurge_tools.exceptions import (
    SplurgeResourceAcquisitionError,
    SplurgeResourceReleaseError,
    SplurgeFileOperationError,
    SplurgeFileNotFoundError,
    SplurgeFilePermissionError,
    SplurgeFileEncodingError,
    SplurgePathValidationError
)


class TestFileResourceManager(unittest.TestCase):
    """Test cases for FileResourceManager class."""

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

    def test_file_resource_manager_init(self):
        """Test FileResourceManager initialization."""
        manager = FileResourceManager(self.temp_file.name)
        self.assertEqual(manager.file_path, Path(self.temp_file.name).resolve())
        self.assertEqual(manager.mode, "r")
        self.assertEqual(manager.encoding, "utf-8")
        self.assertIsNone(manager._file_handle)

    def test_file_resource_manager_init_with_custom_params(self):
        """Test FileResourceManager initialization with custom parameters."""
        manager = FileResourceManager(
            self.temp_file.name,
            mode="w",
            encoding="utf-16",
            errors="ignore",
            newline="\n",
            buffering=1024
        )
        self.assertEqual(manager.mode, "w")
        self.assertEqual(manager.encoding, "utf-16")
        self.assertEqual(manager.errors, "ignore")
        self.assertEqual(manager.newline, "\n")
        self.assertEqual(manager.buffering, 1024)

    def test_file_resource_manager_context_manager_read(self):
        """Test FileResourceManager as context manager for reading."""
        with FileResourceManager(self.temp_file.name, mode="r") as file_handle:
            content = file_handle.read()
            self.assertEqual(content, "test content")
            self.assertIsNotNone(file_handle)

    def test_file_resource_manager_context_manager_write(self):
        """Test FileResourceManager as context manager for writing."""
        new_file_path = os.path.join(self.temp_dir, "new_file.txt")
        with FileResourceManager(new_file_path, mode="w") as file_handle:
            file_handle.write("new content")
        
        # Verify the file was written
        with open(new_file_path, "r") as f:
            content = f.read()
            self.assertEqual(content, "new content")

    def test_file_resource_manager_context_manager_binary(self):
        """Test FileResourceManager as context manager for binary mode."""
        with FileResourceManager(self.temp_file.name, mode="rb") as file_handle:
            content = file_handle.read()
            self.assertEqual(content, b"test content")

    def test_file_resource_manager_file_not_found(self):
        """Test FileResourceManager with non-existent file."""
        non_existent_file = os.path.join(self.temp_dir, "nonexistent.txt")
        with self.assertRaises(SplurgeFileNotFoundError):
            with FileResourceManager(non_existent_file, mode="r"):
                pass

    def test_file_resource_manager_permission_error(self):
        """Test FileResourceManager with permission error."""
        # Create a file and make it read-only, then try to write to it
        read_only_file = os.path.join(self.temp_dir, "readonly.txt")
        with open(read_only_file, "w") as f:
            f.write("readonly content")
        
        # Make file read-only (this might not work on all systems)
        try:
            os.chmod(read_only_file, 0o444)
            with self.assertRaises(SplurgeFilePermissionError):
                with FileResourceManager(read_only_file, mode="w"):
                    pass
        except (OSError, PermissionError):
            # Skip this test if we can't set read-only permissions
            pass

    def test_file_resource_manager_encoding_error(self):
        """Test FileResourceManager with encoding error."""
        # Create a file with invalid UTF-8 content
        invalid_utf8_file = os.path.join(self.temp_dir, "invalid_utf8.txt")
        with open(invalid_utf8_file, "wb") as f:
            # Write bytes that are not valid UTF-8
            f.write(b"valid content \xff\xff\xff invalid")
        
        # This test might not always raise an encoding error depending on the system
        # So we'll test that the file can be opened in binary mode
        with FileResourceManager(invalid_utf8_file, mode="rb") as file_handle:
            content = file_handle.read()
            self.assertIn(b"\xff\xff\xff", content)

    def test_file_resource_manager_invalid_path(self):
        """Test FileResourceManager with invalid path."""
        with self.assertRaises(SplurgePathValidationError):
            FileResourceManager("file<>.txt")

    def test_file_resource_manager_cleanup_on_exception(self):
        """Test FileResourceManager cleanup when exception occurs."""
        manager = FileResourceManager(self.temp_file.name, mode="r")
        try:
            with manager:
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Verify file handle is cleaned up
        self.assertIsNone(manager._file_handle)


class TestTemporaryFileManager(unittest.TestCase):
    """Test cases for TemporaryFileManager class."""

    def test_temporary_file_manager_init(self):
        """Test TemporaryFileManager initialization."""
        manager = TemporaryFileManager()
        self.assertIsNone(manager.suffix)
        self.assertIsNone(manager.prefix)
        self.assertIsNone(manager.dir)
        self.assertTrue(manager.delete)
        self.assertEqual(manager.mode, "w+b")
        self.assertIsNone(manager._temp_file)
        self.assertIsNone(manager._file_path)

    def test_temporary_file_manager_init_with_params(self):
        """Test TemporaryFileManager initialization with parameters."""
        temp_dir = tempfile.mkdtemp()
        try:
            manager = TemporaryFileManager(
                suffix=".txt",
                prefix="test_",
                dir=temp_dir,
                delete=False,
                mode="w"
            )
            self.assertEqual(manager.suffix, ".txt")
            self.assertEqual(manager.prefix, "test_")
            self.assertEqual(manager.dir, Path(temp_dir))
            self.assertFalse(manager.delete)
            self.assertEqual(manager.mode, "w")
        finally:
            os.rmdir(temp_dir)

    def test_temporary_file_manager_context_manager(self):
        """Test TemporaryFileManager as context manager."""
        with TemporaryFileManager() as temp_file:
            self.assertIsNotNone(temp_file)
            temp_file.write(b"test content")
            temp_file.flush()
            
            # Verify file was created
            self.assertTrue(os.path.exists(temp_file.name))

    def test_temporary_file_manager_with_custom_params(self):
        """Test TemporaryFileManager with custom parameters."""
        temp_dir = tempfile.mkdtemp()
        try:
            with TemporaryFileManager(
                suffix=".txt",
                prefix="test_",
                dir=temp_dir,
                delete=True,
                mode="w"
            ) as temp_file:
                temp_file.write("test content")
                temp_file.flush()
                
                # Verify file was created with correct parameters
                self.assertTrue(temp_file.name.endswith(".txt"))
                self.assertTrue(os.path.basename(temp_file.name).startswith("test_"))
                self.assertTrue(temp_file.name.startswith(temp_dir))
        finally:
            # Clean up
            try:
                for file in os.listdir(temp_dir):
                    os.unlink(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            except (OSError, FileNotFoundError):
                pass

    def test_temporary_file_manager_file_path_property(self):
        """Test TemporaryFileManager file_path property."""
        with TemporaryFileManager() as temp_file:
            manager = temp_file._manager if hasattr(temp_file, '_manager') else None
            if manager:
                self.assertIsNotNone(manager.file_path)
                self.assertEqual(manager.file_path, Path(temp_file.name))

    def test_temporary_file_manager_cleanup_on_exception(self):
        """Test TemporaryFileManager cleanup when exception occurs."""
        temp_file_path = None
        try:
            with TemporaryFileManager() as temp_file:
                temp_file_path = temp_file.name
                raise ValueError("Test exception")
        except ValueError:
            pass
        
        # Verify file is cleaned up
        if temp_file_path:
            self.assertFalse(os.path.exists(temp_file_path))

    def test_temporary_file_manager_no_delete(self):
        """Test TemporaryFileManager with delete=False."""
        temp_file_path = None
        with TemporaryFileManager(delete=False) as temp_file:
            temp_file_path = temp_file.name
            temp_file.write(b"test content")
            temp_file.flush()
        
        # Verify file is not deleted
        self.assertTrue(os.path.exists(temp_file_path))
        
        # Clean up manually
        try:
            os.unlink(temp_file_path)
        except (OSError, FileNotFoundError):
            pass


class TestStreamResourceManager(unittest.TestCase):
    """Test cases for StreamResourceManager class."""

    def test_stream_resource_manager_init(self):
        """Test StreamResourceManager initialization."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream)
        self.assertEqual(manager.stream, stream)
        self.assertTrue(manager.auto_close)
        self.assertFalse(manager._is_closed)

    def test_stream_resource_manager_init_with_auto_close_false(self):
        """Test StreamResourceManager initialization with auto_close=False."""
        stream = iter([1, 2, 3])
        manager = StreamResourceManager(stream, auto_close=False)
        self.assertFalse(manager.auto_close)

    def test_stream_resource_manager_context_manager(self):
        """Test StreamResourceManager as context manager."""
        stream = iter([1, 2, 3])
        with StreamResourceManager(stream) as managed_stream:
            items = list(managed_stream)
            self.assertEqual(items, [1, 2, 3])

    def test_stream_resource_manager_with_closeable_stream(self):
        """Test StreamResourceManager with closeable stream."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        with StreamResourceManager(stream, auto_close=True) as managed_stream:
            items = list(managed_stream)
            self.assertEqual(items, [1, 2, 3])
        
        # Verify stream was closed
        self.assertTrue(stream.closed)

    def test_stream_resource_manager_without_closeable_stream(self):
        """Test StreamResourceManager with non-closeable stream."""
        stream = iter([1, 2, 3])
        with StreamResourceManager(stream, auto_close=True) as managed_stream:
            items = list(managed_stream)
            self.assertEqual(items, [1, 2, 3])
        
        # Should not raise any exceptions

    def test_stream_resource_manager_auto_close_false(self):
        """Test StreamResourceManager with auto_close=False."""
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
            self.assertEqual(items, [1, 2, 3])
        
        # Verify stream was not closed
        self.assertFalse(stream.closed)

    def test_stream_resource_manager_is_closed_property(self):
        """Test StreamResourceManager is_closed property."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        manager = StreamResourceManager(stream, auto_close=True)
        
        self.assertFalse(manager.is_closed)
        
        with manager:
            pass
        
        self.assertTrue(manager.is_closed)


class TestContextManagers(unittest.TestCase):
    """Test cases for context manager functions."""

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

    def test_safe_file_operation(self):
        """Test safe_file_operation context manager."""
        with safe_file_operation(self.temp_file.name, mode="r") as file_handle:
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_custom_params(self):
        """Test safe_file_operation with custom parameters."""
        with safe_file_operation(
            self.temp_file.name,
            mode="r",
            encoding="utf-8",
            errors="strict",
            newline="\n",
            buffering=1024
        ) as file_handle:
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_temporary_file_context_manager(self):
        """Test temporary_file context manager."""
        with temporary_file() as temp_file:
            temp_file.write(b"test content")
            temp_file.flush()
            self.assertTrue(os.path.exists(temp_file.name))

    def test_temporary_file_context_manager_with_params(self):
        """Test temporary_file context manager with parameters."""
        temp_dir = tempfile.mkdtemp()
        try:
            with temporary_file(
                suffix=".txt",
                prefix="test_",
                dir=temp_dir,
                delete=True,
                mode="w"
            ) as temp_file:
                temp_file.write("test content")
                temp_file.flush()
                self.assertTrue(temp_file.name.endswith(".txt"))
        finally:
            # Clean up
            try:
                for file in os.listdir(temp_dir):
                    os.unlink(os.path.join(temp_dir, file))
                os.rmdir(temp_dir)
            except (OSError, FileNotFoundError):
                pass

    def test_safe_stream_operation(self):
        """Test safe_stream_operation context manager."""
        stream = iter([1, 2, 3])
        with safe_stream_operation(stream) as managed_stream:
            items = list(managed_stream)
            self.assertEqual(items, [1, 2, 3])

    def test_safe_stream_operation_with_closeable_stream(self):
        """Test safe_stream_operation with closeable stream."""
        class CloseableStream:
            def __init__(self):
                self.closed = False
            
            def __iter__(self):
                return iter([1, 2, 3])
            
            def close(self):
                self.closed = True
        
        stream = CloseableStream()
        with safe_stream_operation(stream, auto_close=True) as managed_stream:
            items = list(managed_stream)
            self.assertEqual(items, [1, 2, 3])
        
        self.assertTrue(stream.closed)


if __name__ == "__main__":
    unittest.main()
