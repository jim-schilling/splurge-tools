"""
Tests for factory protocols.

Tests that factory functions return objects that implement the correct protocols.
"""

import os
import tempfile

import pytest

from splurge_tools.data_transformer import DataTransformer
from splurge_tools.data_validator import DataValidator
from splurge_tools.factory import create_in_memory_model, create_streaming_model
from splurge_tools.protocols import (
    DataTransformerProtocol,
    DataValidatorProtocol,
    StreamingTabularDataProtocol,
    TabularDataProtocol,
    TypeInferenceProtocol,
)
from splurge_tools.resource_manager import safe_file_operation
from splurge_tools.type_helper import DataType, TypeInference


class TestFactoryProtocols:
    """Test that factory methods return objects that implement the correct protocols."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        pass
        yield

    def test_data_model_factory_returns_protocol_compliant_objects(self):
        """Test that DataModelFactory returns TabularDataProtocol compliant objects."""
        # Test with list data
        data = [["name", "age"], ["John", "25"], ["Jane", "30"]]
        model = create_in_memory_model(data)

        # Verify it implements the protocol
        assert isinstance(model, TabularDataProtocol)

        # Test protocol methods exist
        assert hasattr(model, "column_names")
        assert hasattr(model, "row_count")
        assert hasattr(model, "column_count")
        assert hasattr(model, "iter_rows")

        # Test basic functionality
        assert model.column_count == 2
        assert model.row_count == 2
        assert model.column_names == ["name", "age"]

    def test_data_model_factory_with_iterator(self):
        """Test that DataModelFactory works with iterator data."""

        def data_iterator():
            yield [["name", "age"]]
            yield [["John", "25"]]
            yield [["Jane", "30"]]

        model = create_streaming_model(data_iterator())

        # Verify it implements the streaming protocol (iterator data creates streaming models)
        assert isinstance(model, StreamingTabularDataProtocol)

        # Test basic functionality
        assert model.column_count == 2
        assert model.column_names == ["name", "age"]

    def test_component_factory_validator(self):
        """Test that ComponentFactory.create_validator returns DataValidatorProtocol compliant objects."""
        validator = DataValidator()

        # Verify it implements the protocol
        assert isinstance(validator, DataValidatorProtocol)

        # Test protocol methods exist
        assert hasattr(validator, "validate")
        assert hasattr(validator, "get_errors")
        assert hasattr(validator, "clear_errors")

        # Test basic functionality
        validator.add_validator("name", lambda x: len(x) > 0)
        assert validator.validate({"name": "test"})
        assert not validator.validate({"name": ""})

    def test_component_factory_transformer(self):
        """Test that ComponentFactory.create_transformer returns DataTransformerProtocol compliant objects."""
        # Create a data model first
        data = [["name", "age"], ["John", "25"]]
        data_model = create_in_memory_model(data)
        transformer = DataTransformer(data_model)

        # Verify it implements the protocol
        assert isinstance(transformer, DataTransformerProtocol)

        # Test protocol methods exist
        assert hasattr(transformer, "transform")
        assert hasattr(transformer, "can_transform")

        # Test basic functionality
        assert transformer.can_transform(data_model)
        transformed = transformer.transform(data_model)
        assert isinstance(transformed, TabularDataProtocol)

    def test_type_inference_protocol_compliance(self):
        """Test that TypeInference implements TypeInferenceProtocol correctly."""
        type_inference = TypeInference()

        # Verify it implements the protocol
        assert isinstance(type_inference, TypeInferenceProtocol)

        # Test protocol methods exist
        assert hasattr(type_inference, "can_infer")
        assert hasattr(type_inference, "infer_type")
        assert hasattr(type_inference, "convert_value")

        # Test basic functionality
        assert type_inference.can_infer("123")
        assert not type_inference.can_infer("hello")

        assert type_inference.infer_type("123") == DataType.INTEGER
        assert type_inference.convert_value("123") == 123

    def test_resource_context_manager(self):
        """Test that safe_file_operation provides file handles."""
        # Create a temporary file for testing
        with tempfile.NamedTemporaryFile(mode="w", delete=False) as f:
            f.write("test content")
            temp_file_path = f.name

        try:
            with safe_file_operation(temp_file_path) as fh:
                assert fh is not None

        finally:
            # Clean up
            if os.path.exists(temp_file_path):
                os.unlink(temp_file_path)

    def test_construction_validation(self):
        """Basic validation on explicit constructors."""
        with pytest.raises(Exception):
            create_streaming_model(None)  # type: ignore[arg-type]
