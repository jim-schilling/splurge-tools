"""Unit tests for DSVHelper class."""

import unittest

import pytest

from splurge_tools.exceptions import SplurgeParameterError, SplurgeRangeError, SplurgeValidationError
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.type_helper import DataType


class TestTabularDataModel(unittest.TestCase):
    """Test cases for TabularDataModel class."""

    def setUp(self):
        """Set up test data."""
        self.sample_data = [
            ["Name", "Age", "City"],  # Header
            ["John", "30", "New York"],
            ["Jane", "25", "Boston"],
            ["Bob", "35", "Chicago"],
        ]

        # Data with mixed types
        self.mixed_type_data = [
            ["Name", "Age", "Score", "IsActive", "Date"],
            ["John", "30", "95.5", "true", "2024-01-01"],
            ["Jane", "25", "88.0", "false", "2024-01-02"],
            ["Bob", "35", "92.5", "true", "2024-01-03"],
        ]

    def test_basic_initialization(self):
        """Test basic model initialization."""
        model = TabularDataModel(self.sample_data)
        assert model.column_names == ["Name", "Age", "City"]
        assert model.row_count == 3
        assert model.column_count == 3

    def test_column_index(self):
        """Test column index mapping."""
        model = TabularDataModel(self.sample_data)
        assert model.column_index("Name") == 0
        assert model.column_index("Age") == 1
        assert model.column_index("City") == 2

    def test_row_access(self):
        """Test row access methods."""
        model = TabularDataModel(self.sample_data)

        # Test row as dictionary
        row_dict = model.row(0)
        assert row_dict == {"Name": "John", "Age": "30", "City": "New York"}

        # Test row as list
        row_list = model.row_as_list(1)
        assert row_list == ["Jane", "25", "Boston"]

        # Test row as tuple
        row_tuple = model.row_as_tuple(2)
        assert row_tuple == ("Bob", "35", "Chicago")

    def test_iteration(self):
        """Test model iteration."""
        model = TabularDataModel(self.sample_data)
        rows = list(model)
        assert len(rows) == 3
        assert rows[0] == ["John", "30", "New York"]

    def test_data_normalization(self):
        """Test data normalization with uneven rows."""
        data = [
            ["Name", "Age", "City"],
            ["John", "30"],
            ["Jane", "25", "Boston", "Extra"],
            ["Bob"],
        ]
        model = TabularDataModel(data)
        assert model.column_count == 4
        assert model.row(0) == {"Name": "John", "Age": "30", "City": "", "column_3": ""}
        assert model.row(1) == {"Name": "Jane", "Age": "25", "City": "Boston", "column_3": "Extra"}
        assert model.row(2) == {"Name": "Bob", "Age": "", "City": "", "column_3": ""}

    def test_skip_empty_rows(self):
        """Test skipping empty rows."""
        data = [
            ["Name", "Age", "City"],
            ["John", "30", "New York"],
            ["", "", ""],
            ["Jane", "25", "Boston"],
        ]
        model = TabularDataModel(data, skip_empty_rows=True)
        assert model.row_count == 2

        model = TabularDataModel(data, skip_empty_rows=False)
        assert model.row_count == 3

    def test_no_header(self):
        """Test model without header."""
        data = [["John", "30", "New York"], ["Jane", "25", "Boston"]]
        model = TabularDataModel(data, header_rows=0)
        assert model.column_names == ["column_0", "column_1", "column_2"]
        assert model.row_count == 2
        assert model.row(0) == {"column_0": "John", "column_1": "30", "column_2": "New York"}
        assert model.row(1) == {"column_0": "Jane", "column_1": "25", "column_2": "Boston"}

    def test_invalid_initialization(self):
        """Test invalid initialization parameters."""
        with pytest.raises(SplurgeParameterError):
            TabularDataModel(None)

        with pytest.raises(SplurgeValidationError):
            TabularDataModel([])

        with pytest.raises(SplurgeRangeError):
            TabularDataModel(self.sample_data, header_rows=-1)

    def test_multi_row_headers(self):
        """Test multi-row header handling."""
        data = [
            ["Category", "Details", "Location"],  # First header row
            ["Name", "Age", "City"],  # Second header row
            ["John", "30", "New York"],
            ["Jane", "25", "Boston"],
        ]
        model = TabularDataModel(data, header_rows=2)
        assert model.column_names == ["Category_Name", "Details_Age", "Location_City"]
        assert model.row_count == 2
        assert model.row(0) == {"Category_Name": "John", "Details_Age": "30", "Location_City": "New York"}

    def test_iter_rows(self):
        """Test iteration over rows as dictionaries."""
        model = TabularDataModel(self.sample_data)
        rows = list(model.iter_rows())
        assert len(rows) == 3
        assert rows[0] == {"Name": "John", "Age": "30", "City": "New York"}
        assert rows[1] == {"Name": "Jane", "Age": "25", "City": "Boston"}
        assert rows[2] == {"Name": "Bob", "Age": "35", "City": "Chicago"}

    def test_iter_rows_as_tuples(self):
        """Test iteration over rows as tuples."""
        model = TabularDataModel(self.sample_data)
        rows = list(model.iter_rows_as_tuples())
        assert len(rows) == 3
        assert rows[0] == ("John", "30", "New York")
        assert rows[1] == ("Jane", "25", "Boston")
        assert rows[2] == ("Bob", "35", "Chicago")

    def test_column_type(self):
        """Test column type inference."""
        model = TabularDataModel(self.mixed_type_data)

        # Test string column
        assert model.column_type("Name") == DataType.STRING

        # Test integer column
        assert model.column_type("Age") == DataType.INTEGER

        # Test float column
        assert model.column_type("Score") == DataType.FLOAT

        # Test boolean column
        assert model.column_type("IsActive") == DataType.BOOLEAN

        # Test date column
        assert model.column_type("Date") == DataType.DATE

        # Test invalid column name
        with pytest.raises(SplurgeParameterError):
            model.column_type("InvalidColumn")

    def test_column_values(self):
        """Test getting column values."""
        model = TabularDataModel(self.sample_data)

        # Test valid column
        assert model.column_values("Name") == ["John", "Jane", "Bob"]
        assert model.column_values("Age") == ["30", "25", "35"]
        assert model.column_values("City") == ["New York", "Boston", "Chicago"]

        # Test invalid column name
        with pytest.raises(SplurgeParameterError):
            model.column_values("InvalidColumn")

    def test_cell_value(self):
        """Test getting cell values."""
        model = TabularDataModel(self.sample_data)

        # Test valid cells
        assert model.cell_value("Name", 0) == "John"
        assert model.cell_value("Age", 1) == "25"
        assert model.cell_value("City", 2) == "Chicago"

        # Test invalid column name
        with pytest.raises(SplurgeParameterError):
            model.cell_value("InvalidColumn", 0)

        # Test invalid row index
        with pytest.raises(SplurgeRangeError):
            model.cell_value("Name", -1)
        with pytest.raises(SplurgeRangeError):
            model.cell_value("Name", 3)

    def test_column_type_caching(self):
        """Test that column types are cached."""
        model = TabularDataModel(self.mixed_type_data)

        # First call should compute the type
        type1 = model.column_type("Age")

        # Second call should use cached value
        type2 = model.column_type("Age")

        assert type1 == type2
        assert type1 == DataType.INTEGER


if __name__ == "__main__":
    unittest.main()
