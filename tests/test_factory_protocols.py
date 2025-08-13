"""
Tests for factory pattern with protocol compliance.
"""

import os
import tempfile
import unittest
from typing import Iterator

from splurge_tools.factory import create_in_memory_model, create_streaming_model
from splurge_tools.protocols import (
    TabularDataProtocol,
    StreamingTabularDataProtocol,
    DataValidatorProtocol,
    DataTransformerProtocol,
    ResourceManagerProtocol,
    TypeInferenceProtocol
)
from splurge_tools.type_helper import TypeInference, DataType


class TestFactoryProtocols(unittest.TestCase):
    """Test that factory methods return objects that implement the correct protocols."""
    
    def setUp(self):
        pass
    
    def test_data_model_factory_returns_protocol_compliant_objects(self):
        """Test that DataModelFactory returns TabularDataProtocol compliant objects."""
        # Test with list data
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        model = create_in_memory_model(data)
        
        # Verify it implements the protocol
        self.assertIsInstance(model, TabularDataProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(model, 'column_names'))
        self.assertTrue(hasattr(model, 'row_count'))
        self.assertTrue(hasattr(model, 'column_count'))
        self.assertTrue(hasattr(model, 'iter_rows'))
        
        # Test basic functionality
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.row_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])
    
    def test_data_model_factory_with_iterator(self):
        """Test that DataModelFactory works with iterator data."""
        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]
        
        model = create_streaming_model(data_iterator())
        
        # Verify it implements the streaming protocol (iterator data creates streaming models)
        self.assertIsInstance(model, StreamingTabularDataProtocol)
        
        # Test basic functionality
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])
    
    def test_component_factory_validator(self):
        """Test that ComponentFactory.create_validator returns DataValidatorProtocol compliant objects."""
        from splurge_tools.data_validator import DataValidator
        validator = DataValidator()
        
        # Verify it implements the protocol
        self.assertIsInstance(validator, DataValidatorProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(validator, 'validate'))
        self.assertTrue(hasattr(validator, 'get_errors'))
        self.assertTrue(hasattr(validator, 'clear_errors'))
        
        # Test basic functionality
        validator.add_validator("name", lambda x: len(x) > 0)
        self.assertTrue(validator.validate({"name": "test"}))
        self.assertFalse(validator.validate({"name": ""}))
    
    def test_component_factory_transformer(self):
        """Test that ComponentFactory.create_transformer returns DataTransformerProtocol compliant objects."""
        # Create a data model first
        data = [["name", "age"], ["John", "25"]]
        data_model = create_in_memory_model(data)
        from splurge_tools.data_transformer import DataTransformer
        transformer = DataTransformer(data_model)
        
        # Verify it implements the protocol
        self.assertIsInstance(transformer, DataTransformerProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(transformer, 'transform'))
        self.assertTrue(hasattr(transformer, 'can_transform'))
        
        # Test basic functionality
        self.assertTrue(transformer.can_transform(data_model))
        transformed = transformer.transform(data_model)
        self.assertIsInstance(transformed, TabularDataProtocol)
    
    def test_type_inference_protocol_compliance(self):
        """Test that TypeInference implements TypeInferenceProtocol correctly."""
        type_inference = TypeInference()
        
        # Verify it implements the protocol
        self.assertIsInstance(type_inference, TypeInferenceProtocol)
        
        # Test protocol methods exist
        self.assertTrue(hasattr(type_inference, 'can_infer'))
        self.assertTrue(hasattr(type_inference, 'infer_type'))
        self.assertTrue(hasattr(type_inference, 'convert_value'))
        
        # Test basic functionality
        self.assertTrue(type_inference.can_infer("123"))
        self.assertFalse(type_inference.can_infer("hello"))
        
        self.assertEqual(type_inference.infer_type("123"), DataType.INTEGER)
        self.assertEqual(type_inference.convert_value("123"), 123)
    
    def test_resource_context_manager(self):
        """Test that safe_file_operation provides file handles."""
        # Create a temporary file for testing
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
    
    def test_construction_validation(self):
        """Basic validation on explicit constructors."""
        with self.assertRaises(Exception):
            create_streaming_model(None)  # type: ignore[arg-type]


if __name__ == "__main__":
    unittest.main()
