"""
Tests for factory pattern with protocol compliance.
"""

import unittest
from typing import Iterator

from splurge_tools.factory import DataModelFactory, ComponentFactory
from splurge_tools.protocols import (
    TabularDataProtocol,
    DataValidatorProtocol,
    DataTransformerProtocol,
    ResourceManagerProtocol,
    TypeInferenceProtocol
)
from splurge_tools.type_helper import TypeInference


class TestFactoryProtocols(unittest.TestCase):
    """Test that factory methods return objects that implement the correct protocols."""
    
    def setUp(self):
        self.data_model_factory = DataModelFactory()
        self.component_factory = ComponentFactory()
    
    def test_data_model_factory_returns_protocol_compliant_objects(self):
        """Test that DataModelFactory returns TabularDataProtocol compliant objects."""
        # Test with list data
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        model = self.data_model_factory.create_model(data)
        
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
        
        model = self.data_model_factory.create_model(data_iterator())
        
        # Verify it implements the protocol
        self.assertIsInstance(model, TabularDataProtocol)
        
        # Test basic functionality
        self.assertEqual(model.column_count, 2)
        self.assertEqual(model.column_names, ["name", "age"])
    
    def test_component_factory_validator(self):
        """Test that ComponentFactory.create_validator returns DataValidatorProtocol compliant objects."""
        validator = self.component_factory.create_validator()
        
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
        data_model = self.data_model_factory.create_model(data)
        
        transformer = self.component_factory.create_transformer(data_model)
        
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
        
        from splurge_tools.type_helper import DataType
        self.assertEqual(type_inference.infer_type("123"), DataType.INTEGER)
        self.assertEqual(type_inference.convert_value("123"), 123)
    
    def test_component_factory_resource_manager(self):
        """Test that ComponentFactory.create_resource_manager returns ResourceManagerProtocol compliant objects."""
        import tempfile
        import os
        
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode='w', delete=False) as f:
            f.write("test content")
            temp_file_path = f.name
        
        try:
            resource_manager = self.component_factory.create_resource_manager(temp_file_path)
            
            # Verify it implements the protocol
            self.assertIsInstance(resource_manager, ResourceManagerProtocol)
            
            # Test protocol methods exist
            self.assertTrue(hasattr(resource_manager, 'acquire'))
            self.assertTrue(hasattr(resource_manager, 'release'))
            self.assertTrue(hasattr(resource_manager, 'is_acquired'))
            
            # Test basic functionality
            self.assertFalse(resource_manager.is_acquired())
            
            # Acquire the resource
            file_handle = resource_manager.acquire()
            self.assertTrue(resource_manager.is_acquired())
            self.assertIsNotNone(file_handle)
            
            # Release the resource
            resource_manager.release()
            self.assertFalse(resource_manager.is_acquired())
            
        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)
    
    def test_factory_validation(self):
        """Test that factory validation works correctly."""
        # Test that invalid data raises appropriate errors
        with self.assertRaises(Exception):
            self.data_model_factory.create_model(None)
        
        # Test that conflicting requirements raise errors
        with self.assertRaises(Exception):
            self.data_model_factory.create_model(
                [["name"], ["John"]], 
                force_typed=True, 
                force_streaming=True
            )


if __name__ == "__main__":
    unittest.main()
