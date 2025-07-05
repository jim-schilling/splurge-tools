"""
Tests for StreamingTabularDataModel.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import pytest
import tempfile
import os
from typing import Iterator

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

    def test_streaming_model_with_multi_row_headers(self) -> None:
        """Test StreamingTabularDataModel with multi-row headers."""
        # Create a temporary CSV file with multi-row headers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Personal,Personal,Location\n")
            f.write("Name,Age,City\n")
            f.write("John,25,New York\n")
            f.write("Jane,30,Los Angeles\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=2,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test column names (merged)
            assert model.column_names == ["Personal_Name", "Personal_Age", "Location_City"]
            assert model.column_count == 3

            # Test iteration
            rows = list(model.iter_rows())
            assert len(rows) == 2
            assert rows[0] == {"Personal_Name": "John", "Personal_Age": "25", "Location_City": "New York"}

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

            # Test with no data rows
            assert model.column_names == ["Name", "Age"]
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
        # Test with None stream
        with pytest.raises(ValueError, match="Stream is required"):
            StreamingTabularDataModel(None)

        # Test with invalid header rows
        with pytest.raises(ValueError, match="Header rows must be greater than or equal to 0"):
            StreamingTabularDataModel(iter([]), header_rows=-1)

        # Test with invalid chunk size
        with pytest.raises(ValueError, match="chunk_size must be at least 100"):
            StreamingTabularDataModel(iter([]), chunk_size=50)

    def test_streaming_model_large_dataset(self) -> None:
        """Test StreamingTabularDataModel with large dataset."""
        # Create a temporary CSV file with many rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("ID,Name,Value\n")
            for i in range(1000):
                f.write(f"{i},Person{i},{i * 10}\n")
            temp_file = f.name
            f.close()

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model with small buffer
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=1000  # Small buffer to test memory efficiency
            )

            # Test that we can iterate through all rows
            row_count = 0
            for row in model.iter_rows():
                assert "ID" in row
                assert "Name" in row
                assert "Value" in row
                row_count += 1

            assert row_count == 1000

            # Test that buffer is empty after iteration (streaming behavior)
            assert len(model._buffer) == 0

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

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

    def test_streaming_model_iteration_methods(self) -> None:
        """Test different iteration methods."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City\n")
            f.write("John,25,New York\n")
            f.write("Jane,30,Los Angeles\n")
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

            # Test basic iteration
            rows = list(model)
            assert len(rows) == 2
            assert rows[0] == ["John", "25", "New York"]
            assert rows[1] == ["Jane", "30", "Los Angeles"]

            # Create new model for dictionary iteration (since iterator is exhausted)
            stream2 = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            model2 = StreamingTabularDataModel(
                stream2,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test dictionary iteration
            dict_rows = list(model2.iter_rows())
            assert len(dict_rows) == 2
            assert dict_rows[0] == {"Name": "John", "Age": "25", "City": "New York"}
            assert dict_rows[1] == {"Name": "Jane", "Age": "30", "City": "Los Angeles"}

            # Create new model for tuple iteration
            stream3 = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            model3 = StreamingTabularDataModel(
                stream3,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test tuple iteration
            tuple_rows = list(model3.iter_rows_as_tuples())
            assert len(tuple_rows) == 2
            assert tuple_rows[0] == ("John", "25", "New York")
            assert tuple_rows[1] == ("Jane", "30", "Los Angeles")

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
                if 'model2' in locals():
                    list(getattr(model2, 'iter_rows', lambda: [])())
                if 'model3' in locals():
                    list(getattr(model3, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_skip_empty_rows(self) -> None:
        """Test StreamingTabularDataModel with empty rows."""
        # Create a temporary CSV file with empty rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City\n")
            f.write("John,25,New York\n")
            f.write(",,,\n")  # Empty row
            f.write("Jane,30,Los Angeles\n")
            f.write("\n")  # Another empty row
            f.write("Bob,35,Chicago\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model with skip_empty_rows=True
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test that empty rows are skipped
            rows = list(model.iter_rows())
            assert len(rows) == 3
            assert rows[0]["Name"] == "John"
            assert rows[1]["Name"] == "Jane"
            assert rows[2]["Name"] == "Bob"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_uneven_rows(self) -> None:
        """Test StreamingTabularDataModel with uneven row lengths."""
        # Create a temporary CSV file with uneven rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City,Country\n")
            f.write("John,25,New York\n")  # Missing Country
            f.write("Jane,30,Los Angeles,USA,Extra\n")  # Extra column
            f.write("Bob,35,Chicago,USA\n")  # Complete row
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

            # Test that rows are properly padded/truncated
            rows = list(model.iter_rows())
            assert len(rows) == 3
            
            # First row should be padded with empty strings
            assert rows[0]["Name"] == "John"
            assert rows[0]["Age"] == "25"
            assert rows[0]["City"] == "New York"
            assert rows[0]["Country"] == ""
            
            # Second row should have extra columns added
            assert rows[1]["Name"] == "Jane"
            assert rows[1]["Age"] == "30"
            assert rows[1]["City"] == "Los Angeles"
            assert rows[1]["Country"] == "USA"
            assert rows[1]["column_4"] == "Extra"
            
            # Third row should be complete
            assert rows[2]["Name"] == "Bob"
            assert rows[2]["Age"] == "35"
            assert rows[2]["City"] == "Chicago"
            assert rows[2]["Country"] == "USA"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_header_validation(self) -> None:
        """Test header validation."""
        # Test with negative header rows
        with pytest.raises(ValueError, match="Header rows must be greater than or equal to 0"):
            StreamingTabularDataModel(iter([]), header_rows=-1)

    def test_streaming_model_empty_headers(self) -> None:
        """Test StreamingTabularDataModel with empty headers."""
        # Create a temporary CSV file with empty headers
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,,City\n")  # Empty middle header
            f.write("John,25,New York\n")
            f.write("Jane,30,Los Angeles\n")
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

            # Test that empty headers are replaced with column_<index>
            assert model.column_names == ["Name", "column_1", "City"]
            assert model.column_count == 3

            # Test iteration
            rows = list(model.iter_rows())
            assert len(rows) == 2
            assert rows[0]["Name"] == "John"
            assert rows[0]["column_1"] == "25"
            assert rows[0]["City"] == "New York"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_reset_stream(self) -> None:
        """Test resetting the stream."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            f.write("John,25\n")
            f.write("Jane,30\n")
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

            # Test initial state
            assert model.column_names == ["Name", "Age"]
            assert model._is_initialized is True

            # Reset stream
            model.reset_stream()
            assert model._is_initialized is False
            assert len(model._buffer) == 0

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_buffer_size_limits(self) -> None:
        """Test buffer size limits."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            for i in range(50):
                f.write(f"Person{i},{20 + i}\n")
            temp_file = f.name
            f.close()

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model with small buffer (minimum allowed)
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100  # Minimum allowed
            )

            # Test that we can still iterate through all rows
            row_count = 0
            for row in model.iter_rows():
                assert "Name" in row
                assert "Age" in row
                row_count += 1

            assert row_count == 50

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_chunk_processing(self) -> None:
        """Test processing of data in chunks."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            for i in range(100):
                f.write(f"Person{i},{20 + i}\n")
            temp_file = f.name
            f.close()

        try:
            # Create stream from DsvHelper with minimum chunk size
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model
            model = StreamingTabularDataModel(
                stream,
                header_rows=1,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test that we can iterate through all rows
            row_count = 0
            for row in model.iter_rows():
                assert "Name" in row
                assert "Age" in row
                row_count += 1

            assert row_count == 100

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_initialization_early_return(self) -> None:
        """Test that initialization returns early if already initialized."""
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

            # Test that initialization is marked as complete
            assert model._is_initialized is True

            # Call initialization again - should return early
            model._initialize_from_stream()
            assert model._is_initialized is True

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_process_headers_empty_data(self) -> None:
        """Test process_headers with empty data."""
        result = StreamingTabularDataModel.process_headers([], header_rows=0)
        assert result == ([], [])

    def test_streaming_model_process_headers_empty_column_names(self) -> None:
        """Test process_headers with empty column names."""
        header_data = [["", "", ""]]
        result = StreamingTabularDataModel.process_headers(header_data, header_rows=1)
        assert result[1] == ["column_0", "column_1", "column_2"]

    def test_streaming_model_process_headers_mixed_empty_names(self) -> None:
        """Test process_headers with mixed empty and non-empty names."""
        header_data = [["Name", "", "City"]]
        result = StreamingTabularDataModel.process_headers(header_data, header_rows=1)
        assert result[1] == ["Name", "column_1", "City"]

    def test_streaming_model_process_headers_column_count_padding(self) -> None:
        """Test process_headers with column count padding."""
        header_data = [["Name", "Age"], ["John", "25", "Extra"]]  # Second row has more columns
        result = StreamingTabularDataModel.process_headers(header_data, header_rows=2)
        assert len(result[1]) == 3  # Should have 3 columns based on max row length

    def test_streaming_model_dynamic_column_expansion(self) -> None:
        """Test dynamic column expansion during iteration."""
        # Create a temporary CSV file with varying column counts
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            f.write("John,25,Extra1\n")  # Extra column
            f.write("Jane,30\n")  # Normal row
            f.write("Bob,35,Extra2,Extra3\n")  # More extra columns
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

            # Test initial column count
            assert model.column_count == 2
            assert model.column_names == ["Name", "Age"]

            # Iterate through rows to trigger dynamic expansion
            rows = list(model.iter_rows())
            assert len(rows) == 3

            # Check that columns were expanded
            assert model.column_count >= 4  # At least 4 columns after expansion
            assert "column_2" in model.column_names
            assert "column_3" in model.column_names

            # Check row data
            assert rows[0]["Name"] == "John"
            assert rows[0]["Age"] == "25"
            assert rows[0]["column_2"] == "Extra1"

            assert rows[1]["Name"] == "Jane"
            assert rows[1]["Age"] == "30"

            assert rows[2]["Name"] == "Bob"
            assert rows[2]["Age"] == "35"
            assert rows[2]["column_2"] == "Extra2"
            assert rows[2]["column_3"] == "Extra3"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_row_padding(self) -> None:
        """Test row padding during iteration."""
        # Create a temporary CSV file with short rows
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age,City,Country\n")
            f.write("John,25\n")  # Short row
            f.write("Jane,30,Los Angeles\n")  # Medium row
            f.write("Bob,35,Chicago,USA\n")  # Complete row
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

            # Test iteration with row padding
            rows = list(model.iter_rows())
            assert len(rows) == 3

            # First row should be padded
            assert rows[0]["Name"] == "John"
            assert rows[0]["Age"] == "25"
            assert rows[0]["City"] == ""
            assert rows[0]["Country"] == ""

            # Second row should be padded
            assert rows[1]["Name"] == "Jane"
            assert rows[1]["Age"] == "30"
            assert rows[1]["City"] == "Los Angeles"
            assert rows[1]["Country"] == ""

            # Third row should be complete
            assert rows[2]["Name"] == "Bob"
            assert rows[2]["Age"] == "35"
            assert rows[2]["City"] == "Chicago"
            assert rows[2]["Country"] == "USA"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_no_headers_with_empty_buffer(self) -> None:
        """Test no headers case with empty buffer."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("John,25,New York\n")
            f.write("Jane,30,Los Angeles\n")
            temp_file = f.name

        try:
            # Create stream from DsvHelper
            stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=100)
            
            # Create streaming model with no headers
            model = StreamingTabularDataModel(
                stream,
                header_rows=0,
                skip_empty_rows=True,
                chunk_size=100
            )

            # Test that column names are auto-generated
            assert model.column_names == ["column_0", "column_1", "column_2"]
            assert model.column_count == 3

            # Test iteration
            rows = list(model.iter_rows())
            assert len(rows) == 2
            assert rows[0]["column_0"] == "John"
            assert rows[0]["column_1"] == "25"
            assert rows[0]["column_2"] == "New York"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file)

    def test_streaming_model_process_headers_edge_cases(self) -> None:
        """Test process_headers with edge cases."""
        # Test with single empty row
        header_data = [[""]]
        result = StreamingTabularDataModel.process_headers(header_data, header_rows=1)
        assert result[1] == ["column_0"]

        # Test with multiple empty rows
        header_data = [[""], [""], [""]]
        result = StreamingTabularDataModel.process_headers(header_data, header_rows=3)
        assert result[1] == ["column_0"]

    def test_streaming_model_iteration_with_empty_chunks(self) -> None:
        """Test iteration with empty chunks in stream."""
        # Create a temporary CSV file
        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            f.write("Name,Age\n")
            f.write("John,25\n")
            f.write("Jane,30\n")
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

            # Test iteration
            rows = list(model.iter_rows())
            assert len(rows) == 2
            assert rows[0]["Name"] == "John"
            assert rows[1]["Name"] == "Jane"

        finally:
            # Ensure all file handles are closed before deletion
            try:
                if 'model' in locals():
                    list(getattr(model, 'iter_rows', lambda: [])())
            except Exception:
                pass
            os.unlink(temp_file) 