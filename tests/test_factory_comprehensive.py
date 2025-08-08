"""
Comprehensive unit tests for Factory classes to improve coverage.
"""

import unittest
from typing import Iterator
from pathlib import Path

from splurge_tools.factory import DataModelFactory, ComponentFactory, create_data_model
from splurge_tools.protocols import TabularDataProtocol
from splurge_tools.exceptions import SplurgeValidationError


class TestDataModelFactoryComprehensive(unittest.TestCase):
    """Comprehensive test cases for DataModelFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = DataModelFactory()

    def test_create_model_with_force_streaming(self):
        """Test create_model with force_streaming=True."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = self.factory.create_model(
            data_iterator(),
            force_streaming=True
        )
        
        # Should return streaming model even for list data
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_force_typed(self):
        """Test create_model with force_typed=True."""
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        
        model = self.factory.create_model(
            data,
            force_typed=True
        )
        
        # Should return typed model
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_iterator_data(self):
        """Test create_model with iterator data."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = self.factory.create_model(data_iterator())
        
        # Should return streaming model for iterator data
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_large_estimated_size(self):
        """Test create_model with large estimated size."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        # Set a very low memory threshold to force streaming
        factory = DataModelFactory(memory_threshold_mb=0.001)
        
        model = factory.create_model(
            data_iterator(),
            estimated_size_mb=1.0  # Much larger than threshold
        )
        
        # Should return streaming model due to size
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_custom_chunk_size(self):
        """Test create_model with custom chunk size."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = self.factory.create_model(
            data_iterator(),
            chunk_size=1000  # Use valid chunk size (minimum 100)
        )
        
        # Should use custom chunk size
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_model_with_type_configs(self):
        """Test create_model with type configurations."""
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        type_configs = {"age": "int"}
        
        model = self.factory.create_model(
            data,
            force_typed=True,
            type_configs=type_configs
        )
        
        # Should use type configurations
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_model_with_skip_empty_rows(self):
        """Test create_model with skip_empty_rows=False."""
        data = [["name", "age"], ["John", "25"], ["", ""], ["Jane", "30"]]
        
        model = self.factory.create_model(
            data,
            skip_empty_rows=False
        )
        
        # Should include empty rows
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_model_with_multiple_header_rows(self):
        """Test create_model with multiple header rows."""
        data = [
            ["Header1", "Header2"],
            ["SubHeader1", "SubHeader2"],
            ["John", "25"],
            ["Jane", "30"]
        ]
        
        model = self.factory.create_model(
            data,
            header_rows=2
        )
        
        # Should use multiple header rows
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_force_typed_with_iterator_error(self):
        """Test that force_typed with iterator raises error."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        with self.assertRaises(SplurgeValidationError):
            self.factory.create_model(
                data_iterator(),
                force_typed=True
            )

    def test_force_streaming_with_iterator_error(self):
        """Test that force_streaming with iterator works correctly."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        # Should work correctly with iterator data
        model = self.factory.create_model(
            data_iterator(),
            force_streaming=True
        )
        self.assertIsInstance(model, TabularDataProtocol)

    def test_standard_model_with_iterator_error(self):
        """Test that standard model with iterator works correctly."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        # Should work correctly with iterator data (creates streaming model)
        model = self.factory.create_model(
            data_iterator(),
            force_typed=False,
            force_streaming=False
        )
        self.assertIsInstance(model, TabularDataProtocol)

    def test_determine_model_type_logic(self):
        """Test the model type determination logic."""
        # Test force streaming
        model_type = self.factory._determine_model_type(
            [["name"]],
            force_typed=False,
            force_streaming=True,
            estimated_size_mb=None
        )
        self.assertEqual(model_type, "streaming")
        
        # Test force typed
        model_type = self.factory._determine_model_type(
            [["name"]],
            force_typed=True,
            force_streaming=False,
            estimated_size_mb=None
        )
        self.assertEqual(model_type, "typed")
        
        # Test iterator data
        def data_iterator():
            yield [["name"]]
        
        model_type = self.factory._determine_model_type(
            data_iterator(),
            force_typed=False,
            force_streaming=False,
            estimated_size_mb=None
        )
        self.assertEqual(model_type, "streaming")
        
        # Test large estimated size
        model_type = self.factory._determine_model_type(
            [["name"]],
            force_typed=False,
            force_streaming=False,
            estimated_size_mb=100.0  # Large size
        )
        self.assertEqual(model_type, "typed")  # List data defaults to typed, not streaming
        
        # Test list data (default to typed)
        model_type = self.factory._determine_model_type(
            [["name"]],
            force_typed=False,
            force_streaming=False,
            estimated_size_mb=None
        )
        self.assertEqual(model_type, "typed")

    def test_create_standard_model(self):
        """Test _create_standard_model method."""
        data = [["name", "age"], ["John", "25"]]
        
        model = self.factory._create_standard_model(
            data,
            header_rows=1,
            skip_empty_rows=True
        )
        
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_typed_model(self):
        """Test _create_typed_model method."""
        data = [["name", "age"], ["John", "25"]]
        type_configs = {"age": "int"}
        
        model = self.factory._create_typed_model(
            data,
            header_rows=1,
            skip_empty_rows=True,
            type_configs=type_configs
        )
        
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_streaming_model(self):
        """Test _create_streaming_model method."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        model = self.factory._create_streaming_model(
            data_iterator(),
            header_rows=1,
            skip_empty_rows=True,
            chunk_size=1000
        )
        
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)


class TestComponentFactoryComprehensive(unittest.TestCase):
    """Comprehensive test cases for ComponentFactory class."""

    def setUp(self):
        """Set up test fixtures."""
        self.factory = ComponentFactory()
        self.data_model_factory = DataModelFactory()
        
        # Create a data model for testing
        data = [["name", "age"], ["John", "25"]]
        self.data_model = self.data_model_factory.create_model(data)

    def test_create_validator(self):
        """Test create_validator method."""
        validator = self.factory.create_validator()
        
        # Test basic functionality
        validator.add_validator("name", lambda x: len(x) > 0)
        self.assertTrue(validator.validate({"name": "John"}))
        self.assertFalse(validator.validate({"name": ""}))

    def test_create_transformer(self):
        """Test create_transformer method."""
        transformer = self.factory.create_transformer(self.data_model)
        
        # Test basic functionality
        self.assertTrue(transformer.can_transform(self.data_model))
        transformed = transformer.transform(self.data_model)
        self.assertIsInstance(transformed, TabularDataProtocol)

    def test_create_resource_manager_with_file(self):
        """Test create_resource_manager method with file path."""
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            resource_manager = self.factory.create_resource_manager(temp_file_path)
            
            # Test basic functionality
            self.assertFalse(resource_manager.is_acquired())
            
            # Acquire resource
            file_handle = resource_manager.acquire()
            self.assertTrue(resource_manager.is_acquired())
            self.assertIsNotNone(file_handle)
            
            # Release resource
            resource_manager.release()
            self.assertFalse(resource_manager.is_acquired())
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_create_resource_manager_with_path_object(self):
        """Test create_resource_manager method with Path object."""
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = Path(f.name)
        
        try:
            resource_manager = self.factory.create_resource_manager(temp_file_path)
            
            # Test basic functionality
            self.assertFalse(resource_manager.is_acquired())
            
            # Acquire resource
            file_handle = resource_manager.acquire()
            self.assertTrue(resource_manager.is_acquired())
            self.assertIsNotNone(file_handle)
            
            # Release resource
            resource_manager.release()
            self.assertFalse(resource_manager.is_acquired())
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_create_resource_manager_with_custom_mode(self):
        """Test create_resource_manager method with custom mode."""
        import tempfile
        import os
        
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            resource_manager = self.factory.create_resource_manager(
                temp_file_path,
                mode="r",
                encoding="utf-8"
            )
            
            # Test basic functionality
            file_handle = resource_manager.acquire()
            self.assertIsNotNone(file_handle)
            resource_manager.release()
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


class TestCreateDataModelFunction(unittest.TestCase):
    """Test cases for the create_data_model function."""

    def test_create_data_model_basic(self):
        """Test create_data_model function with basic usage."""
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        
        model = create_data_model(data)
        
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_data_model_with_options(self):
        """Test create_data_model function with various options."""
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        
        model = create_data_model(
            data,
            header_rows=1,
            skip_empty_rows=True,
            force_typed=True,
            type_configs={"age": "int"}
        )
        
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_data_model_with_iterator(self):
        """Test create_data_model function with iterator data."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = create_data_model(data_iterator())
        
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)


if __name__ == "__main__":
    unittest.main()
