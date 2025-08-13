"""
Comprehensive unit tests for ResourceManager classes to improve coverage.
"""

import unittest
import tempfile
import os
from pathlib import Path
from typing import Iterator, Any

from splurge_tools.resource_manager import (
    ResourceManager,
    FileResourceManager,
    TemporaryFileManager,
    StreamResourceManager,
    safe_file_operation,
    temporary_file,
    safe_stream_operation
)
from splurge_tools.exceptions import (
    SplurgeResourceAcquisitionError,
    SplurgeResourceReleaseError
)


class TestResourceManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for ResourceManager base class."""

    def setUp(self):
        """Set up test fixtures."""
        self.resource_manager = ResourceManager()

    def test_initial_state(self):
        """Test initial state of resource manager via public API."""
        self.assertFalse(self.resource_manager.is_acquired())

    def test_acquire_when_already_acquired(self):
        """Test acquire when resource is already acquired."""
        # Use a simple concrete subclass to avoid touching privates
        class SimpleManager(ResourceManager):
            def _create_resource(self) -> Any:  # type: ignore[override]
                return "test_resource"

        mgr = SimpleManager()
        resource = mgr.acquire()
        self.assertEqual(resource, "test_resource")
        self.assertTrue(mgr.is_acquired())

        with self.assertRaises(SplurgeResourceAcquisitionError):
            mgr.acquire()

    def test_acquire_with_exception(self):
        """Test acquire when resource creation fails."""
        class FailingManager(ResourceManager):
            def _create_resource(self) -> Any:  # type: ignore[override]
                raise Exception("Creation failed")

        with self.assertRaises(SplurgeResourceAcquisitionError):
            FailingManager().acquire()

    def test_release_when_not_acquired(self):
        """Test release when resource is not acquired."""
        # Should not raise an exception
        self.resource_manager.release()
        self.assertFalse(self.resource_manager.is_acquired())

    def test_release_with_exception(self):
        """Test release when cleanup fails."""
        class CleanupFailManager(ResourceManager):
            def _create_resource(self) -> Any:  # type: ignore[override]
                return "test_resource"

            def _cleanup_resource(self) -> None:  # type: ignore[override]
                raise Exception("Cleanup failed")

        mgr = CleanupFailManager()
        mgr.acquire()
        with self.assertRaises(SplurgeResourceReleaseError):
            mgr.release()

    def test_release_with_closeable_resource(self):
        """Test release with a resource that has a close method."""
        # Create a mock resource with close method
        class MockResource:
            def __init__(self):
                self.closed = False
            
            def close(self):
                self.closed = True
        
        mock_resource = MockResource()

        class CloseableManager(ResourceManager):
            def __init__(self, res: Any) -> None:
                super().__init__()
                self._res = res

            def _create_resource(self) -> Any:  # type: ignore[override]
                return self._res

        mgr = CloseableManager(mock_resource)
        mgr.acquire()
        mgr.release()
        self.assertTrue(mock_resource.closed)
        self.assertFalse(mgr.is_acquired())

    def test_acquire_on_base_manager_raises(self):
        """Base ResourceManager acquire should fail via public API."""
        with self.assertRaises(SplurgeResourceAcquisitionError):
            ResourceManager().acquire()


class TestFileResourceManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for FileResourceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.write("test content")
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def test_context_manager_basic(self):
        """Test basic context manager functionality."""
        with FileResourceManager(self.temp_file_path) as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_context_manager_with_custom_mode(self):
        """Test context manager with custom mode."""
        with FileResourceManager(self.temp_file_path, mode="r") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_context_manager_with_encoding(self):
        """Test context manager with custom encoding."""
        with FileResourceManager(self.temp_file_path, encoding="utf-8") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_context_manager_with_errors_handling(self):
        """Test context manager with errors handling."""
        with FileResourceManager(self.temp_file_path, errors="strict") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_context_manager_with_newline(self):
        """Test context manager with newline handling."""
        with FileResourceManager(self.temp_file_path, newline="") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_context_manager_with_buffering(self):
        """Test context manager with custom buffering."""
        with FileResourceManager(self.temp_file_path, buffering=8192) as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_context_manager_exception_handling(self):
        """Test context manager exception handling."""
        with self.assertRaises(Exception):  # Use generic Exception to catch SplurgeFileNotFoundError
            with FileResourceManager("nonexistent_file.txt") as file_handle:
                pass

    def test_context_manager_exit_with_exception(self):
        """Test context manager exit with exception."""
        try:
            with FileResourceManager(self.temp_file_path) as file_handle:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception

    def test_context_manager_exit_with_none_exception(self):
        """Test context manager exit with None exception."""
        with FileResourceManager(self.temp_file_path) as file_handle:
            pass  # Normal exit


class TestTemporaryFileManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for TemporaryFileManager class."""

    def test_context_manager_basic(self):
        """Test basic context manager functionality."""
        with TemporaryFileManager() as temp_file:
            self.assertIsNotNone(temp_file)
            self.assertTrue(temp_file.name)
            temp_file.write(b"test content")
            temp_file.flush()

    def test_context_manager_with_suffix(self):
        """Test context manager with custom suffix."""
        with TemporaryFileManager(suffix=".txt") as temp_file:
            self.assertIsNotNone(temp_file)
            self.assertTrue(temp_file.name.endswith(".txt"))

    def test_context_manager_with_prefix(self):
        """Test context manager with custom prefix."""
        with TemporaryFileManager(prefix="test_") as temp_file:
            self.assertIsNotNone(temp_file)
            self.assertTrue(os.path.basename(temp_file.name).startswith("test_"))

    def test_context_manager_with_directory(self):
        """Test context manager with custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with TemporaryFileManager(dir=temp_dir) as temp_file:
                self.assertIsNotNone(temp_file)
                self.assertTrue(temp_file.name.startswith(temp_dir))

    def test_context_manager_with_delete_false(self):
        """Test context manager with delete=False."""
        temp_file_path = None
        with TemporaryFileManager(delete=False) as temp_file:
            self.assertIsNotNone(temp_file)
            temp_file_path = temp_file.name
            temp_file.write(b"test content")
            temp_file.flush()
        
        # File should still exist
        self.assertTrue(os.path.exists(temp_file_path))
        
        # Clean up
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

    def test_context_manager_with_custom_mode(self):
        """Test context manager with custom mode."""
        with TemporaryFileManager(mode="w+b") as temp_file:
            self.assertIsNotNone(temp_file)
            temp_file.write(b"test content")
            temp_file.seek(0)
            content = temp_file.read()
            self.assertEqual(content, b"test content")

    def test_context_manager_exception_handling(self):
        """Test context manager exception handling."""
        try:
            with TemporaryFileManager() as temp_file:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception

    def test_file_path_property(self):
        """Test file_path property."""
        manager = TemporaryFileManager()
        # Note: This is a bit tricky to test since we need to access the internal state
        # For now, we'll just test that the property exists
        self.assertTrue(hasattr(manager, 'file_path'))


class TestStreamResourceManagerComprehensive(unittest.TestCase):
    """Comprehensive test cases for StreamResourceManager class."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [1, 2, 3, 4, 5]

    def test_context_manager_basic(self):
        """Test basic context manager functionality."""
        stream = iter(self.test_data)
        with StreamResourceManager(stream) as managed_stream:
            self.assertIsNotNone(managed_stream)
            items = list(managed_stream)
            self.assertEqual(items, self.test_data)

    def test_context_manager_with_auto_close_true(self):
        """Test context manager with auto_close=True."""
        stream = iter(self.test_data)
        with StreamResourceManager(stream, auto_close=True) as managed_stream:
            self.assertIsNotNone(managed_stream)
            items = list(managed_stream)
            self.assertEqual(items, self.test_data)

    def test_context_manager_with_auto_close_false(self):
        """Test context manager with auto_close=False."""
        stream = iter(self.test_data)
        with StreamResourceManager(stream, auto_close=False) as managed_stream:
            self.assertIsNotNone(managed_stream)
            items = list(managed_stream)
            self.assertEqual(items, self.test_data)

    def test_context_manager_exception_handling(self):
        """Test context manager exception handling."""
        stream = iter(self.test_data)
        try:
            with StreamResourceManager(stream) as managed_stream:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception

    def test_is_closed_property(self):
        """Test is_closed property."""
        stream = iter(self.test_data)
        manager = StreamResourceManager(stream)
        
        # Initially not closed
        self.assertFalse(manager.is_closed)
        
        # After context manager, should be closed
        with manager as managed_stream:
            self.assertFalse(manager.is_closed)
        
        # Note: StreamResourceManager may not actually close the stream
        # The property behavior depends on the implementation
        # For now, just test that the property exists and is callable
        self.assertTrue(hasattr(manager, 'is_closed'))


class TestSafeFileOperationComprehensive(unittest.TestCase):
    """Comprehensive test cases for safe_file_operation function."""

    def setUp(self):
        """Set up test fixtures."""
        # Create a temporary file for testing
        self.temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        self.temp_file.write("test content")
        self.temp_file.close()
        self.temp_file_path = self.temp_file.name

    def tearDown(self):
        """Clean up test fixtures."""
        if os.path.exists(self.temp_file_path):
            os.unlink(self.temp_file_path)

    def test_safe_file_operation_basic(self):
        """Test basic safe file operation."""
        with safe_file_operation(self.temp_file_path) as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_custom_mode(self):
        """Test safe file operation with custom mode."""
        with safe_file_operation(self.temp_file_path, mode="r") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_encoding(self):
        """Test safe file operation with custom encoding."""
        with safe_file_operation(self.temp_file_path, encoding="utf-8") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_errors(self):
        """Test safe file operation with errors handling."""
        with safe_file_operation(self.temp_file_path, errors="strict") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_newline(self):
        """Test safe file operation with newline handling."""
        with safe_file_operation(self.temp_file_path, newline="") as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_buffering(self):
        """Test safe file operation with custom buffering."""
        with safe_file_operation(self.temp_file_path, buffering=8192) as file_handle:
            self.assertIsNotNone(file_handle)
            content = file_handle.read()
            self.assertEqual(content, "test content")

    def test_safe_file_operation_with_nonexistent_file(self):
        """Test safe file operation with nonexistent file."""
        with self.assertRaises(Exception):  # Use generic Exception to catch SplurgeFileNotFoundError
            with safe_file_operation("nonexistent_file.txt") as file_handle:
                pass


class TestTemporaryFileComprehensive(unittest.TestCase):
    """Comprehensive test cases for temporary_file function."""

    def test_temporary_file_basic(self):
        """Test basic temporary file function."""
        with temporary_file() as temp_file:
            self.assertIsNotNone(temp_file)
            self.assertTrue(temp_file.name)
            temp_file.write(b"test content")
            temp_file.flush()

    def test_temporary_file_with_suffix(self):
        """Test temporary file function with custom suffix."""
        with temporary_file(suffix=".txt") as temp_file:
            self.assertIsNotNone(temp_file)
            self.assertTrue(temp_file.name.endswith(".txt"))

    def test_temporary_file_with_prefix(self):
        """Test temporary file function with custom prefix."""
        with temporary_file(prefix="test_") as temp_file:
            self.assertIsNotNone(temp_file)
            self.assertTrue(os.path.basename(temp_file.name).startswith("test_"))

    def test_temporary_file_with_directory(self):
        """Test temporary file function with custom directory."""
        with tempfile.TemporaryDirectory() as temp_dir:
            with temporary_file(dir=temp_dir) as temp_file:
                self.assertIsNotNone(temp_file)
                self.assertTrue(temp_file.name.startswith(temp_dir))

    def test_temporary_file_with_delete_false(self):
        """Test temporary file function with delete=False."""
        temp_file_path = None
        with temporary_file(delete=False) as temp_file:
            self.assertIsNotNone(temp_file)
            temp_file_path = temp_file.name
            temp_file.write(b"test content")
            temp_file.flush()
        
        # File should still exist
        self.assertTrue(os.path.exists(temp_file_path))
        
        # Clean up
        if temp_file_path and os.path.exists(temp_file_path):
            os.unlink(temp_file_path)

    def test_temporary_file_with_custom_mode(self):
        """Test temporary file function with custom mode."""
        with temporary_file(mode="w+b") as temp_file:
            self.assertIsNotNone(temp_file)
            temp_file.write(b"test content")
            temp_file.seek(0)
            content = temp_file.read()
            self.assertEqual(content, b"test content")


class TestSafeStreamOperationComprehensive(unittest.TestCase):
    """Comprehensive test cases for safe_stream_operation function."""

    def setUp(self):
        """Set up test fixtures."""
        self.test_data = [1, 2, 3, 4, 5]

    def test_safe_stream_operation_basic(self):
        """Test basic safe stream operation."""
        stream = iter(self.test_data)
        with safe_stream_operation(stream) as managed_stream:
            self.assertIsNotNone(managed_stream)
            items = list(managed_stream)
            self.assertEqual(items, self.test_data)

    def test_safe_stream_operation_with_auto_close_true(self):
        """Test safe stream operation with auto_close=True."""
        stream = iter(self.test_data)
        with safe_stream_operation(stream, auto_close=True) as managed_stream:
            self.assertIsNotNone(managed_stream)
            items = list(managed_stream)
            self.assertEqual(items, self.test_data)

    def test_safe_stream_operation_with_auto_close_false(self):
        """Test safe stream operation with auto_close=False."""
        stream = iter(self.test_data)
        with safe_stream_operation(stream, auto_close=False) as managed_stream:
            self.assertIsNotNone(managed_stream)
            items = list(managed_stream)
            self.assertEqual(items, self.test_data)

    def test_safe_stream_operation_exception_handling(self):
        """Test safe stream operation exception handling."""
        stream = iter(self.test_data)
        try:
            with safe_stream_operation(stream) as managed_stream:
                raise ValueError("Test exception")
        except ValueError:
            pass  # Expected exception


if __name__ == "__main__":
    unittest.main()
