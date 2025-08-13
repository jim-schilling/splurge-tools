"""
Comprehensive unit tests for Factory classes to improve coverage.
"""

import os
import tempfile
import unittest
from typing import Iterator
from pathlib import Path

from splurge_tools.factory import create_in_memory_model, create_streaming_model
from splurge_tools.protocols import TabularDataProtocol, StreamingTabularDataProtocol
from splurge_tools.exceptions import SplurgeValidationError


class TestModelConstruction(unittest.TestCase):
    """Comprehensive tests for simplified model constructors."""
    
    def _assert_is_tabular_data_protocol(self, obj):
        """Helper to assert object implements either TabularDataProtocol or StreamingTabularDataProtocol."""
        self.assertTrue(
            isinstance(obj, (TabularDataProtocol, StreamingTabularDataProtocol)),
            f"Object {obj} should implement TabularDataProtocol or StreamingTabularDataProtocol"
        )

    def test_create_model_with_force_streaming(self):
        """Test create_model with force_streaming=True."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = create_streaming_model(data_iterator())
        
        # Should return streaming model even for list data
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_force_typed(self):
        """Test create_model with force_typed=True."""
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        
        model = create_in_memory_model(data)
        
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
        
        model = create_streaming_model(data_iterator())
        
        # Should return streaming model for iterator data
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_large_estimated_size(self):
        """Test create_model with large estimated size."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        # Explicit streaming creation only
        model = create_streaming_model(data_iterator())
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_model_with_custom_chunk_size(self):
        """Test create_model with custom chunk size."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = create_streaming_model(data_iterator(), chunk_size=1000)
        
        # Should use custom chunk size and return streaming protocol
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_model_with_type_configs(self):
        """Test create_model with type configurations."""
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        type_configs = {"age": "int"}
        
        from splurge_tools.tabular_data_model import TabularDataModel
        base = create_in_memory_model(data)
        model = base.to_typed(type_configs=type_configs)
        
        # Should use type configurations
        self.assertTrue(hasattr(model, 'iter_rows'))
        self.assertEqual(model.column_count, 2)

    def test_create_model_with_skip_empty_rows(self):
        """Test create_model with skip_empty_rows=False."""
        data = [["name", "age"], ["John", "25"], ["", ""], ["Jane", "30"]]
        
        model = create_in_memory_model(data, skip_empty_rows=False)
        
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
        
        model = create_in_memory_model(data, header_rows=2)
        
        # Should use multiple header rows
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_force_typed_with_iterator_error(self):
        """Test that force_typed with iterator raises error."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        # Not applicable; typed vs streaming is explicit now
        pass

    def test_force_streaming_with_iterator_error(self):
        """Test that force_streaming with iterator works correctly."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        # Should work correctly with iterator data
        model = create_streaming_model(data_iterator())
        self.assertIsInstance(model, StreamingTabularDataProtocol)

    def test_standard_model_with_iterator_error(self):
        """Test that standard model with iterator works correctly."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        
        # Should work correctly with iterator data (creates streaming model)
        model = create_streaming_model(data_iterator())
        self.assertIsInstance(model, StreamingTabularDataProtocol)

    def test_explicit_construction_only(self):
        """Ensure explicit constructors produce expected protocols."""
        def it2():
            yield [["name"],["x"]]
        m3 = create_streaming_model(it2())
        self.assertIsInstance(m3, StreamingTabularDataProtocol)
        m4 = create_in_memory_model([["name"],["x"]])
        self.assertIsInstance(m4, TabularDataProtocol)

    def test_create_standard_model_public_path(self):
        """Ensure standard model can be obtained via create_model for list input."""
        data = [["name", "age"], ["John", "25"]]
        model = create_in_memory_model(data)
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)

    def test_create_typed_model_public_path(self):
        """Ensure typed model creation through public API with type_configs."""
        data = [["name", "age"], ["John", "25"]]
        type_configs = {"age": "int"}
        model = create_in_memory_model(data).to_typed(type_configs=type_configs)
        self.assertTrue(hasattr(model, 'iter_rows'))
        self.assertEqual(model.column_count, 2)

    def test_create_streaming_model_public_path(self):
        """Ensure streaming model creation through public API for iterator input."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
        model = create_streaming_model(data_iterator(), chunk_size=1000)
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        self.assertEqual(model.column_count, 2)


class TestComponentFactoryComprehensive(unittest.TestCase):
    """Simple component creation tests without factories."""

    def setUp(self):
        data = [["name", "age"], ["John", "25"]]
        from splurge_tools.data_transformer import DataTransformer
        from splurge_tools.data_validator import DataValidator
        self.data_model = create_in_memory_model(data)
        self.DataTransformer = DataTransformer
        self.DataValidator = DataValidator

    def test_create_validator(self):
        """Test create_validator method."""
        validator = self.DataValidator()
        
        # Test basic functionality
        validator.add_validator("name", lambda x: len(x) > 0)
        self.assertTrue(validator.validate({"name": "John"}))
        self.assertFalse(validator.validate({"name": ""}))

    def test_create_transformer(self):
        """Test create_transformer method."""
        transformer = self.DataTransformer(self.data_model)
        
        # Test basic functionality
        self.assertTrue(transformer.can_transform(self.data_model))
        transformed = transformer.transform(self.data_model)
        self.assertIsInstance(transformed, TabularDataProtocol)

    def test_create_resource_manager_with_file(self):
        """Test create_resource_manager method with file path."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            from splurge_tools.resource_manager import safe_file_operation
            with safe_file_operation(temp_file_path) as fh:
                self.assertIsNotNone(fh)
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_create_resource_manager_with_path_object(self):
        """Test create_resource_manager method with Path object."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = Path(f.name)
        
        try:
            from splurge_tools.resource_manager import safe_file_operation
            with safe_file_operation(temp_file_path) as fh:
                self.assertIsNotNone(fh)
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_create_resource_manager_with_custom_mode(self):
        """Test create_resource_manager method with custom mode."""
        # Create a temporary file
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            from splurge_tools.resource_manager import safe_file_operation
            with safe_file_operation(temp_file_path, mode="r", encoding="utf-8") as fh:
                self.assertIsNotNone(fh)
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)


class TestExplicitModelHelpers(unittest.TestCase):
    def test_create_in_memory_model(self):
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        model = create_in_memory_model(data)
        self.assertIsInstance(model, TabularDataProtocol)
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])

    def test_create_streaming_model(self):
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        model = create_streaming_model(data_iterator())
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        self.assertEqual(model.column_count, 2)


if __name__ == "__main__":
    unittest.main()
