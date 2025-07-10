"""
Tests for StreamingTabularDataModel.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import pytest
import tempfile
import os

from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel


class TestStreamingTabularDataModel:
    """Test cases for StreamingTabularDataModel."""

    def test_streaming_model_with_headers(self) -> None:
        """Test StreamingTabularDataModel with header rows."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City\n")
            f.write("John,25,New York\n")
            f.write("Jane,30,Los Angeles\n")
            f.write("Bob,35,Chicago\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test column names
            assert model.column_names == ["Name", "Age", "City"]
            assert model.column_count == 3

            # Test column index
            assert model.column_index("Name") == 0
            assert model.column_index("Age") == 1
            assert model.column_index("City") == 2

            # Test iteration
            rows = list(model.iter_rows())
            assert len(rows) == 3
            assert rows[0] == {"Name": "John", "Age": "25", "City": "New York"}
            assert rows[1] == {"Name": "Jane", "Age": "30", "City": "Los Angeles"}
            assert rows[2] == {"Name": "Bob", "Age": "35", "City": "Chicago"}

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_without_headers(self) -> None:
        """Test StreamingTabularDataModel without header rows."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("John,25,New York\n")
            f.write("Jane,30,Los Angeles\n")
            f.write("Bob,35,Chicago\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=0,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test column names (auto-generated)
            assert model.column_names == ["column_0", "column_1", "column_2"]
            assert model.column_count == 3

            # Test iteration
            rows = list(model.iter_rows())
            assert len(rows) == 3
            assert rows[0] == {"column_0": "John", "column_1": "25", "column_2": "New York"}

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_buffer_operations(self) -> None:
        """Test StreamingTabularDataModel buffer operations."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            for i in range(10):
                f.write(f"Person{i},{20 + i}\n")
            temp_file = f.name
            # Ensure file is closed before opening for reading
            f.close()

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)

            # Create streaming model with small buffer
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test clearing buffer
            model.clear_buffer()
            assert len(model._buffer) == 0

            # Exhaust the iterator to ensure file is closed
            list(model.iter_rows())

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_empty_file(self) -> None:
        """Test StreamingTabularDataModel with empty file."""
        # Create a temporary empty CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test that no rows are returned
            rows = list(model.iter_rows())
            assert len(rows) == 0

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_invalid_parameters(self) -> None:
        """Test StreamingTabularDataModel with invalid parameters."""
        # Test invalid chunk size
        with pytest.raises(ValueError, match="chunk_size must be at least 100"):
            StreamingTabularDataModel(iter([]), chunk_size=50)

    def test_streaming_model_invalid_column_operations(self) -> None:
        """Test error handling for invalid column operations."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            f.write("John,25\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test invalid column name for column_index
            with pytest.raises(ValueError, match="Column name InvalidColumn not found"):
                model.column_index("InvalidColumn")

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_header_validation(self) -> None:
        """Test StreamingTabularDataModel header validation."""
        # Test with negative header rows
        with pytest.raises(ValueError, match="Header rows must be greater than or equal to 0"):
            StreamingTabularDataModel(iter([]), header_rows=-1)

    def test_streaming_model_empty_headers(self) -> None:
        """Test StreamingTabularDataModel with empty headers."""
        # Create a temporary CSV file with empty headers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write(",,,\n")  # Empty headers
            f.write("John,25,New York\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test that empty headers are handled
            assert model.column_names == ["column_0", "column_1", "column_2", "column_3"]
            assert model.column_count == 4

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file) 