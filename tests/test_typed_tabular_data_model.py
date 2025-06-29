"""
Unit tests for TypedTabularDataModel.

Copyright (c) 2025, Jim Schilling

Please keep the copyright notice in this file and in the source code files.

This module is licensed under the MIT License.
"""

import unittest
from datetime import date, datetime

from jpy_tools.type_helper import DataType
from jpy_tools.typed_tabular_data_model import TypeConfig, TypedTabularDataModel


class TestTypedTabularDataModel(unittest.TestCase):
    """Test cases for TypedTabularDataModel."""

    def setUp(self):
        """Set up test data."""
        self.test_data = [
            ["name", "age", "is_active", "score", "birth_date", "created_at"],
            ["John", "25", "true", "95.5", "1998-01-01", "2024-01-01T12:00:00"],
            ["Jane", "", "false", "", "1993-05-15", "2024-01-02T13:00:00"],
            ["Bob", "none", "none", "none", "none", "none"],
            ["Alice", "30", "true", "88.0", "1995-12-31", "2024-01-03T14:00:00"],
        ]

        # Custom type configurations
        self.custom_configs = {
            DataType.BOOLEAN: TypeConfig(empty_default=False, none_default=True),
            DataType.INTEGER: TypeConfig(empty_default=-1, none_default=0),
            DataType.FLOAT: TypeConfig(empty_default=0.0, none_default=0.0),
            DataType.DATE: TypeConfig(
                empty_default=date(1900, 1, 1), none_default=None
            ),
            DataType.DATETIME: TypeConfig(
                empty_default=datetime(1900, 1, 1), none_default=None
            ),
        }

        # Create models with default and custom configurations
        self.default_model = TypedTabularDataModel(self.test_data)
        self.custom_model = TypedTabularDataModel(
            self.test_data, type_configs=self.custom_configs
        )

    def test_column_types(self):
        """Test that column types are correctly inferred."""
        self.assertEqual(self.default_model.column_type("name"), DataType.STRING)
        self.assertEqual(self.default_model.column_type("age"), DataType.INTEGER)
        self.assertEqual(self.default_model.column_type("is_active"), DataType.BOOLEAN)
        self.assertEqual(self.default_model.column_type("score"), DataType.FLOAT)
        self.assertEqual(self.default_model.column_type("birth_date"), DataType.DATE)
        self.assertEqual(
            self.default_model.column_type("created_at"), DataType.DATETIME
        )

    def test_default_conversions(self):
        """Test type conversions with default configurations."""
        # Test normal values
        self.assertEqual(self.default_model.cell_value("name", 0), "John")
        self.assertEqual(self.default_model.cell_value("age", 0), 25)
        self.assertEqual(self.default_model.cell_value("is_active", 0), True)
        self.assertEqual(self.default_model.cell_value("score", 0), 95.5)
        self.assertEqual(
            self.default_model.cell_value("birth_date", 0), date(1998, 1, 1)
        )
        self.assertEqual(
            self.default_model.cell_value("created_at", 0), datetime(2024, 1, 1, 12, 0)
        )

        # Test empty values
        self.assertEqual(
            self.default_model.cell_value("age", 1), 0
        )  # empty_default for INTEGER
        self.assertEqual(
            self.default_model.cell_value("score", 1), 0.0
        )  # empty_default for FLOAT
        self.assertEqual(
            self.default_model.cell_value("is_active", 1), False
        )  # empty_default for BOOLEAN

        # Test none-like values
        self.assertEqual(
            self.default_model.cell_value("age", 2), 0
        )  # none_default for INTEGER
        self.assertEqual(
            self.default_model.cell_value("score", 2), 0.0
        )  # none_default for FLOAT
        self.assertEqual(
            self.default_model.cell_value("is_active", 2), False
        )  # none_default for BOOLEAN

    def test_custom_conversions(self):
        """Test type conversions with custom configurations."""
        # Test normal values (should be same as default)
        self.assertEqual(self.custom_model.cell_value("name", 0), "John")
        self.assertEqual(self.custom_model.cell_value("age", 0), 25)
        self.assertEqual(self.custom_model.cell_value("is_active", 0), True)
        self.assertEqual(self.custom_model.cell_value("score", 0), 95.5)
        self.assertEqual(
            self.custom_model.cell_value("birth_date", 0), date(1998, 1, 1)
        )
        self.assertEqual(
            self.custom_model.cell_value("created_at", 0), datetime(2024, 1, 1, 12, 0)
        )

        # Test empty values with custom defaults
        self.assertEqual(
            self.custom_model.cell_value("age", 1), -1
        )  # custom empty_default for INTEGER
        self.assertEqual(
            self.custom_model.cell_value("score", 1), 0.0
        )  # custom empty_default for FLOAT
        self.assertEqual(
            self.custom_model.cell_value("is_active", 1), False
        )  # custom empty_default for BOOLEAN
        self.assertEqual(
            self.custom_model.cell_value("birth_date", 1), date(1993, 5, 15)
        )  # actual date value

        # Test none-like values with custom defaults
        self.assertEqual(
            self.custom_model.cell_value("age", 2), 0
        )  # custom none_default for INTEGER
        self.assertEqual(
            self.custom_model.cell_value("score", 2), 0.0
        )  # custom none_default for FLOAT
        self.assertEqual(
            self.custom_model.cell_value("is_active", 2), True
        )  # custom none_default for BOOLEAN
        self.assertEqual(
            self.custom_model.cell_value("birth_date", 2), None
        )  # custom none_default for DATE

    def test_column_values(self):
        """Test getting all values for a column."""
        # Test with default configuration
        ages = self.default_model.column_values("age")
        self.assertEqual(ages, [25, 0, 0, 30])

        scores = self.default_model.column_values("score")
        self.assertEqual(scores, [95.5, 0.0, 0.0, 88.0])

        # Test with custom configuration
        ages = self.custom_model.column_values("age")
        self.assertEqual(ages, [25, -1, 0, 30])

        scores = self.custom_model.column_values("score")
        self.assertEqual(scores, [95.5, 0.0, 0.0, 88.0])

    def test_row_access(self):
        """Test accessing rows in different formats."""
        # Test dictionary access
        row = self.default_model.row(0)
        self.assertEqual(row["name"], "John")
        self.assertEqual(row["age"], 25)
        self.assertEqual(row["is_active"], True)
        self.assertEqual(row["score"], 95.5)
        self.assertEqual(row["birth_date"], date(1998, 1, 1))
        self.assertEqual(row["created_at"], datetime(2024, 1, 1, 12, 0))

        # Test list access
        row_list = self.default_model.row_as_list(0)
        self.assertEqual(row_list[0], "John")
        self.assertEqual(row_list[1], 25)
        self.assertEqual(row_list[2], True)
        self.assertEqual(row_list[3], 95.5)
        self.assertEqual(row_list[4], date(1998, 1, 1))
        self.assertEqual(row_list[5], datetime(2024, 1, 1, 12, 0))

        # Test tuple access
        row_tuple = self.default_model.row_as_tuple(0)
        self.assertEqual(row_tuple[0], "John")
        self.assertEqual(row_tuple[1], 25)
        self.assertEqual(row_tuple[2], True)
        self.assertEqual(row_tuple[3], 95.5)
        self.assertEqual(row_tuple[4], date(1998, 1, 1))
        self.assertEqual(row_tuple[5], datetime(2024, 1, 1, 12, 0))

    def test_iterators(self):
        """Test row iterators."""
        # Test dictionary iterator
        rows = list(self.default_model.iter_rows())
        self.assertEqual(len(rows), 4)  # 4 data rows
        self.assertEqual(rows[0]["name"], "John")
        self.assertEqual(rows[0]["age"], 25)

        # Test tuple iterator
        rows = list(self.default_model.iter_rows_as_tuples())
        self.assertEqual(len(rows), 4)  # 4 data rows
        self.assertEqual(rows[0][0], "John")
        self.assertEqual(rows[0][1], 25)

    def test_invalid_column(self):
        """Test handling of invalid column names."""
        with self.assertRaises(ValueError):
            self.default_model.column_values("invalid_column")

        with self.assertRaises(ValueError):
            self.default_model.cell_value("invalid_column", 0)

    def test_invalid_row_index(self):
        """Test handling of invalid row indices."""
        with self.assertRaises(ValueError):
            self.default_model.cell_value("name", -1)

        with self.assertRaises(ValueError):
            self.default_model.cell_value("name", 10)

        with self.assertRaises(ValueError):
            self.default_model.row(-1)

        with self.assertRaises(ValueError):
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
        mixed_configs = {
            DataType.MIXED: TypeConfig(empty_default="EMPTY", none_default="NONE")
        }
        mixed_model = TypedTabularDataModel(mixed_data, type_configs=mixed_configs)

        # Test that MIXED type values are preserved
        self.assertEqual(
            mixed_model.cell_value("mixed_col", 0), "123"
        )  # integer-like preserved as string
        self.assertEqual(
            mixed_model.cell_value("mixed_col", 1), "abc"
        )  # string preserved
        self.assertEqual(
            mixed_model.cell_value("mixed_col", 2), ""
        )  # empty value preserved
        self.assertEqual(
            mixed_model.cell_value("mixed_col", 3), "NONE"
        )  # none-like uses none_default

        # Test column values
        mixed_values = mixed_model.column_values("mixed_col")
        self.assertEqual(mixed_values, ["123", "abc", "", "NONE"])


if __name__ == "__main__":
    unittest.main()
