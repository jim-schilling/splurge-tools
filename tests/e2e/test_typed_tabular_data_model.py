"""
Unit tests for TypedTabularDataModel.

Copyright (c) 2025, Jim Schilling

Please keep the copyright notice in this file and in the source code files.

This module is licensed under the MIT License.
"""

import unittest
from datetime import date, datetime, time

import pytest

from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.type_helper import DataType


class TestTypedView(unittest.TestCase):
    """Test cases for typed view via TabularDataModel.to_typed()."""

    def setUp(self):
        """Set up test data."""
        self.test_data = [
            ["name", "age", "is_active", "score", "birth_date", "created_at", "login_time"],
            ["John", "25", "true", "95.5", "1998-01-01", "2024-01-01T12:00:00", "14:30:45"],
            ["Jane", "", "false", "", "1993-05-15", "2024-01-02T13:00:00", "2:30 PM"],
            ["Bob", "none", "none", "none", "none", "none", "none"],
            ["Alice", "30", "true", "88.0", "1995-12-31", "2024-01-03T14:00:00", ""],
        ]

        # Custom type configurations
        self.custom_configs = {
            DataType.BOOLEAN: True,
            DataType.INTEGER: -1,
            DataType.FLOAT: 0.0,
            DataType.DATE: date(1900, 1, 1),
            DataType.DATETIME: datetime(1900, 1, 1),
            DataType.TIME: time(0, 0, 0),
        }

        base = TabularDataModel(self.test_data)
        self.default_model = base.to_typed()
        self.custom_model = base.to_typed(type_configs=self.custom_configs)

    def test_column_types(self):
        """Test that column types are correctly inferred."""
        assert self.default_model.column_type("name") == DataType.STRING
        assert self.default_model.column_type("age") == DataType.INTEGER
        assert self.default_model.column_type("is_active") == DataType.BOOLEAN
        assert self.default_model.column_type("score") == DataType.FLOAT
        assert self.default_model.column_type("birth_date") == DataType.DATE
        assert self.default_model.column_type("created_at") == DataType.DATETIME
        assert self.default_model.column_type("login_time") == DataType.TIME

    def test_default_conversions(self):
        """Test type conversions with default configurations."""
        # Test normal values
        assert self.default_model.cell_value("name", 0) == "John"
        assert self.default_model.cell_value("age", 0) == 25
        assert self.default_model.cell_value("is_active", 0)
        assert self.default_model.cell_value("score", 0) == 95.5
        assert self.default_model.cell_value("birth_date", 0) == date(1998, 1, 1)
        assert self.default_model.cell_value("created_at", 0) == datetime(2024, 1, 1, 12, 0)
        assert self.default_model.cell_value("login_time", 0) == time(14, 30, 45)

        # Test empty values
        assert self.default_model.cell_value("age", 1) == 0  # empty_default for INTEGER
        assert self.default_model.cell_value("score", 1) == 0.0  # empty_default for FLOAT
        assert not self.default_model.cell_value("is_active", 1)  # empty_default for BOOLEAN
        assert self.default_model.cell_value("login_time", 3) is None  # none_default for TIME
        assert self.default_model.cell_value("login_time", 1) == time(14, 30)  # 12-hour format
        assert self.default_model.cell_value("login_time", 2) is None  # none_default for TIME
        assert self.default_model.cell_value("login_time", 4 - 1) is None  # empty string, default is None

        # Test none-like values
        assert self.default_model.cell_value("age", 2) == 0  # none_default for INTEGER
        assert self.default_model.cell_value("score", 2) == 0.0  # none_default for FLOAT
        assert not self.default_model.cell_value("is_active", 2)  # none_default for BOOLEAN
        assert self.default_model.cell_value("login_time", 2) is None  # none_default for TIME

    def test_custom_conversions(self):
        """Test type conversions with custom configurations."""
        # Test normal values (should be same as default)
        assert self.custom_model.cell_value("name", 0) == "John"
        assert self.custom_model.cell_value("age", 0) == 25
        assert self.custom_model.cell_value("is_active", 0)
        assert self.custom_model.cell_value("score", 0) == 95.5
        assert self.custom_model.cell_value("birth_date", 0) == date(1998, 1, 1)
        assert self.custom_model.cell_value("created_at", 0) == datetime(2024, 1, 1, 12, 0)
        assert self.custom_model.cell_value("login_time", 0) == time(14, 30, 45)

        # Test empty values with custom defaults
        assert self.custom_model.cell_value("age", 1) == -1  # custom empty_default for INTEGER
        assert self.custom_model.cell_value("score", 1) == 0.0  # custom empty_default for FLOAT
        assert not self.custom_model.cell_value("is_active", 1)  # custom empty_default for BOOLEAN
        assert self.custom_model.cell_value("birth_date", 1) == date(1993, 5, 15)  # actual date value
        assert self.custom_model.cell_value("login_time", 3) == time(0, 0, 0)  # custom empty_default for TIME
        assert self.custom_model.cell_value("login_time", 1) == time(14, 30)  # 12-hour format
        assert self.custom_model.cell_value("login_time", 2) is None  # custom none_default for TIME
        assert self.custom_model.cell_value("login_time", 4 - 1) == time(0, 0, 0)  # custom empty_default for TIME

        # Test none-like values with custom defaults
        assert self.custom_model.cell_value("age", 2) == 0  # custom none_default for INTEGER
        assert self.custom_model.cell_value("score", 2) == 0.0  # custom none_default for FLOAT
        assert self.custom_model.cell_value("is_active", 2)  # custom none_default for BOOLEAN
        assert self.custom_model.cell_value("birth_date", 2) is None  # custom none_default for DATE
        assert self.custom_model.cell_value("login_time", 2) is None  # custom none_default for TIME

    def test_column_values(self):
        """Test getting all values for a column."""
        # Test with default configuration
        ages = self.default_model.column_values("age")
        assert ages == [25, 0, 0, 30]

        scores = self.default_model.column_values("score")
        assert scores == [95.5, 0.0, 0.0, 88.0]

        login_times = self.default_model.column_values("login_time")
        assert login_times == [time(14, 30, 45), time(14, 30), None, None]

        # Test with custom configuration
        ages = self.custom_model.column_values("age")
        assert ages == [25, -1, 0, 30]

        scores = self.custom_model.column_values("score")
        assert scores == [95.5, 0.0, 0.0, 88.0]

        login_times = self.custom_model.column_values("login_time")
        assert login_times == [time(14, 30, 45), time(14, 30), None, time(0, 0, 0)]

    def test_row_access(self):
        """Test accessing rows in different formats."""
        # Test dictionary access
        row = self.default_model.row(0)
        assert row["name"] == "John"
        assert row["age"] == 25
        assert row["is_active"]
        assert row["score"] == 95.5
        assert row["birth_date"] == date(1998, 1, 1)
        assert row["created_at"] == datetime(2024, 1, 1, 12, 0)
        assert row["login_time"] == time(14, 30, 45)

        # Test list access
        row_list = self.default_model.row_as_list(0)
        assert row_list[0] == "John"
        assert row_list[1] == 25
        assert row_list[2]
        assert row_list[3] == 95.5
        assert row_list[4] == date(1998, 1, 1)
        assert row_list[5] == datetime(2024, 1, 1, 12, 0)
        assert row_list[6] == time(14, 30, 45)

        # Test tuple access
        row_tuple = self.default_model.row_as_tuple(0)
        assert row_tuple[0] == "John"
        assert row_tuple[1] == 25
        assert row_tuple[2]
        assert row_tuple[3] == 95.5
        assert row_tuple[4] == date(1998, 1, 1)
        assert row_tuple[5] == datetime(2024, 1, 1, 12, 0)
        assert row_tuple[6] == time(14, 30, 45)

    def test_iterators(self):
        """Test row iterators."""
        # Test dictionary iterator
        rows = list(self.default_model.iter_rows())
        assert len(rows) == 4  # 4 data rows
        assert rows[0]["name"] == "John"
        assert rows[0]["age"] == 25
        assert rows[0]["login_time"] == time(14, 30, 45)

        # Test tuple iterator
        rows = list(self.default_model.iter_rows_as_tuples())
        assert len(rows) == 4  # 4 data rows
        assert rows[0][0] == "John"
        assert rows[0][1] == 25
        assert rows[0][6] == time(14, 30, 45)

    def test_invalid_column(self):
        """Test handling of invalid column names."""
        with pytest.raises(ValueError):
            self.default_model.column_values("invalid_column")

        with pytest.raises(ValueError):
            self.default_model.cell_value("invalid_column", 0)

    def test_invalid_row_index(self):
        """Test handling of invalid row indices."""
        with pytest.raises(ValueError):
            self.default_model.cell_value("name", -1)

        with pytest.raises(ValueError):
            self.default_model.cell_value("name", 10)

        with pytest.raises(ValueError):
            self.default_model.row(-1)

        with pytest.raises(ValueError):
            self.default_model.row(10)

    def test_mixed_type_handling(self):
        """Test handling of MIXED type values."""
        # Create test data with a MIXED type column
        mixed_data = [
            ["id", "mixed_col"],
            ["1", "123"],  # integer-like
            ["2", "abc"],  # string
            ["3", ""],  # empty
            ["4", "none"],  # none-like
        ]

        # Create model with custom config for MIXED type
        mixed_configs = {DataType.MIXED: "NONE"}
        base = TabularDataModel(mixed_data)
        mixed_model = base.to_typed(type_configs=mixed_configs)

        # Test that MIXED type values are preserved
        assert mixed_model.cell_value("mixed_col", 0) == "123"  # integer-like preserved as string
        assert mixed_model.cell_value("mixed_col", 1) == "abc"  # string preserved
        assert mixed_model.cell_value("mixed_col", 2) == ""  # empty value preserved
        assert mixed_model.cell_value("mixed_col", 3) == "NONE"  # none-like uses none_default

        # Test column values
        mixed_values = mixed_model.column_values("mixed_col")
        assert mixed_values == ["123", "abc", "", "NONE"]


if __name__ == "__main__":
    unittest.main()
