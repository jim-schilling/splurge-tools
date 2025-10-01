"""Unit tests for DataTransformer class."""

from statistics import mean

import pytest

from splurge_tools.data_transformer import DataTransformer
from splurge_tools.tabular_data_model import TabularDataModel


class TestDataTransformer:
    """Test cases for DataTransformer class."""

    @pytest.fixture(autouse=True)
    def setup_method(self):
        """Set up test data."""
        self.sample_data = [
            ["Name", "Category", "Value", "Date"],
            ["John", "A", "10", "2024-01-01"],
            ["John", "B", "20", "2024-01-01"],
            ["Jane", "A", "15", "2024-01-01"],
            ["Jane", "B", "25", "2024-01-01"],
            ["Bob", "A", "12", "2024-01-02"],
            ["Bob", "B", "22", "2024-01-02"],
        ]
        self.model = TabularDataModel(self.sample_data)
        self.transformer = DataTransformer(self.model)
        self.duplicate_data = [
            ["Name", "Category", "Value", "Date"],
            ["John", "A", "10", "2024-01-01"],
            ["John", "A", "15", "2024-01-01"],  # Duplicate Category for John
            ["John", "B", "20", "2024-01-01"],
            ["Jane", "A", "15", "2024-01-01"],
            ["Jane", "B", "25", "2024-01-01"],
            ["Jane", "B", "30", "2024-01-01"],  # Duplicate Category for Jane
            ["Bob", "A", "12", "2024-01-02"],
            ["Bob", "B", "22", "2024-01-02"],
        ]
        self.duplicate_model = TabularDataModel(self.duplicate_data)
        self.duplicate_transformer = DataTransformer(self.duplicate_model)
        yield

    def test_pivot(self):
        """Test pivot operation."""
        # Pivot by Name and Category
        result = self.transformer.pivot(
            index_cols=["Name"],
            columns_col="Category",
            values_col="Value",
        )

        # Check header
        assert result.column_names == ["Name", "A", "B"]

        # Check data
        rows = list(result.iter_rows())
        assert len(rows) == 3  # 3 names

        # Check John's values
        john_row = next(row for row in rows if row["Name"] == "John")
        assert john_row["A"] == "10"
        assert john_row["B"] == "20"

    def test_melt(self):
        """Test melt operation."""
        # Melt Value and Date columns
        result = self.transformer.melt(
            id_vars=["Name", "Category"],
            value_vars=["Value", "Date"],
        )

        # Check header
        assert result.column_names == ["Name", "Category", "variable", "value"]

        # Check data
        rows = list(result.iter_rows())
        assert len(rows) == 12  # 6 data rows * 2 variables

        # Check first row
        assert rows[0]["Name"] == "John"
        assert rows[0]["Category"] == "A"
        assert rows[0]["variable"] == "Value"
        assert rows[0]["value"] == "10"

    def test_group_by(self):
        """Test group by operation."""
        # Group by Name and calculate mean Value
        result = self.transformer.group_by(
            group_cols=["Name"],
            agg_dict={"Value": lambda x: mean(float(v) for v in x)},
        )

        # Check header
        assert result.column_names == ["Name", "Value"]

        # Check data
        rows = list(result.iter_rows())
        assert len(rows) == 3  # 3 names

        # Check John's mean value
        john_row = next(row for row in rows if row["Name"] == "John")
        assert float(john_row["Value"]) == 15.0  # (10 + 20) / 2

    def test_transform_column(self):
        """Test column transformation."""
        # Double the Value column
        result = self.transformer.transform_column(
            column="Value",
            transform_func=lambda x: str(float(x) * 2),
        )

        # Check data
        rows = list(result.iter_rows())
        assert len(rows) == 6  # 6 data rows

        # Check first row
        assert rows[0]["Value"] == "20.0"  # 10 * 2

    def test_pivot_with_duplicates(self):
        """Test pivot operation with duplicate values."""
        # Test that pivot raises error when duplicates are found without agg_func
        with pytest.raises(ValueError) as context:
            self.duplicate_transformer.pivot(
                index_cols=["Name"],
                columns_col="Category",
                values_col="Value",
            )
        assert "Duplicate values found" in str(context.value)

        # Test pivot with mean aggregation
        result = self.duplicate_transformer.pivot(
            index_cols=["Name"],
            columns_col="Category",
            values_col="Value",
            agg_func=lambda x: mean(float(v) for v in x),
        )

        # Check header
        assert result.column_names == ["Name", "A", "B"]

        # Check data
        rows = list(result.iter_rows())
        assert len(rows) == 3  # 3 names

        # Check John's values (A should be mean of 10 and 15)
        john_row = next(row for row in rows if row["Name"] == "John")
        assert float(john_row["A"]) == 12.5  # (10 + 15) / 2
        assert float(john_row["B"]) == 20.0  # No duplicates

        # Check Jane's values (B should be mean of 25 and 30)
        jane_row = next(row for row in rows if row["Name"] == "Jane")
        assert float(jane_row["A"]) == 15.0  # No duplicates
        assert float(jane_row["B"]) == 27.5  # (25 + 30) / 2

        # Check Bob's values (no duplicates)
        bob_row = next(row for row in rows if row["Name"] == "Bob")
        assert float(bob_row["A"]) == 12.0
        assert float(bob_row["B"]) == 22.0

    def test_pivot_with_duplicates_and_custom_agg(self):
        """Test pivot operation with duplicate values and custom aggregation."""
        # Test pivot with max aggregation
        result = self.duplicate_transformer.pivot(
            index_cols=["Name"],
            columns_col="Category",
            values_col="Value",
            agg_func=lambda x: max(float(v) for v in x),
        )

        # Check data
        rows = list(result.iter_rows())

        # Check John's values (A should be max of 10 and 15)
        john_row = next(row for row in rows if row["Name"] == "John")
        assert float(john_row["A"]) == 15.0  # max(10, 15)
        assert float(john_row["B"]) == 20.0  # No duplicates

        # Check Jane's values (B should be max of 25 and 30)
        jane_row = next(row for row in rows if row["Name"] == "Jane")
        assert float(jane_row["A"]) == 15.0  # No duplicates
        assert float(jane_row["B"]) == 30.0  # max(25, 30)

        # Test pivot with min aggregation
        result = self.duplicate_transformer.pivot(
            index_cols=["Name"],
            columns_col="Category",
            values_col="Value",
            agg_func=lambda x: min(float(v) for v in x),
        )

        # Check data
        rows = list(result.iter_rows())

        # Check John's values (A should be min of 10 and 15)
        john_row = next(row for row in rows if row["Name"] == "John")
        assert float(john_row["A"]) == 10.0  # min(10, 15)
        assert float(john_row["B"]) == 20.0  # No duplicates

        # Check Jane's values (B should be min of 25 and 30)
        jane_row = next(row for row in rows if row["Name"] == "Jane")
        assert float(jane_row["A"]) == 15.0  # No duplicates
        assert float(jane_row["B"]) == 25.0  # min(25, 30)
