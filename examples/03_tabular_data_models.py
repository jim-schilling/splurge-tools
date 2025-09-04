#!/usr/bin/env python3
"""
Tabular Data Models Examples

This example demonstrates the tabular data model capabilities of splurge-tools,
including in-memory TabularDataModel and memory-efficient StreamingTabularDataModel.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import contextlib
import tempfile
from pathlib import Path

from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel
from splurge_tools.tabular_data_model import TabularDataModel


def create_sample_datasets():
    """Create sample datasets for demonstration."""
    # Basic employee dataset
    employee_data = [
        ["Name", "Age", "Department", "Salary", "Start Date", "Active"],
        ["John Doe", "30", "Engineering", "75000", "2023-01-15", "true"],
        ["Jane Smith", "25", "Marketing", "65000", "2023-03-20", "true"],
        ["Bob Johnson", "45", "Sales", "85000", "2022-11-10", "false"],
        ["Alice Brown", "35", "Engineering", "72000", "2023-05-05", "true"],
        ["Charlie Wilson", "28", "Marketing", "68000", "2023-02-14", "true"],
    ]

    # Multi-row header dataset
    multi_header_data = [
        ["Employee", "Employee", "Department", "Compensation", "Compensation", "Status"],
        ["First Name", "Last Name", "Name", "Base Salary", "Bonus", "Active"],
        ["John", "Doe", "Engineering", "75000", "5000", "true"],
        ["Jane", "Smith", "Marketing", "65000", "3000", "true"],
        ["Bob", "Johnson", "Sales", "85000", "8000", "false"],
    ]

    # Large dataset for streaming demonstration
    temp_dir = Path(tempfile.mkdtemp())
    large_file = temp_dir / "large_dataset.csv"

    # Generate large CSV file
    with open(large_file, "w") as f:
        f.write("ID,Name,Category,Value,Timestamp\n")
        f.writelines(
            f"{i},Item_{i},Category_{i % 10},{i * 1.5},2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}\n"
            for i in range(5000)
        )

    return employee_data, multi_header_data, large_file, temp_dir


def basic_tabular_model_examples(employee_data):
    """Demonstrate basic TabularDataModel functionality."""

    # Create a basic tabular data model
    model = TabularDataModel(employee_data, header_rows=1)

    # Access individual cells and rows

    # Get entire rows in different formats

    # Column operations

    # Iterate through all rows
    for i, _row in enumerate(model):
        if i >= 3:
            break


def multi_header_examples(multi_header_data):
    """Demonstrate multi-row header handling."""

    for _i, _row in enumerate(multi_header_data[:3]):  # Show headers + 1 data row
        pass

    # Process with multi-row headers
    TabularDataModel(multi_header_data, header_rows=2)

    # Show how headers were merged

    # Access data with merged headers


def typed_tabular_model_examples(employee_data):
    """Demonstrate typed view with schema validation."""

    # Create typed view (automatically infers types)
    typed_model = TabularDataModel(
        employee_data,
        header_rows=1,
    ).to_typed()

    # Access typed data
    for i in range(min(3, typed_model.row_count)):
        row_dict = typed_model.row(i)
        for col_name in row_dict:
            pass

    # Demonstrate type inference
    for col_name in typed_model.column_names:
        TabularDataModel(employee_data, header_rows=1).column_type(col_name)


def streaming_model_examples(large_file):
    """Demonstrate StreamingTabularDataModel for large datasets."""

    # Create streaming model
    stream = DsvHelper.parse_stream(large_file, delimiter=",", chunk_size=500)
    streaming_model = StreamingTabularDataModel(
        stream,
        header_rows=1,
        chunk_size=1000,
    )

    # Process data in streaming fashion
    row_count = 0
    for _row in streaming_model:
        if row_count >= 10:
            break
        row_count += 1

    # Reset stream and demonstrate dictionary iteration
    streaming_model.reset_stream()

    dict_count = 0
    for _row_dict in streaming_model.iter_rows():
        if dict_count >= 5:
            break
        dict_count += 1

    # Demonstrate memory efficiency


def data_model_comparison():
    """Compare different data model types and their use cases."""

    comparison_data = [
        ["Model Type", "Memory Usage", "Random Access", "Best Use Case"],
        ["TabularDataModel", "High", "Yes", "Small to medium datasets, analysis"],
        ["StreamingTabularDataModel", "Low", "No", "Large datasets, ETL processing"],
        ["Typed View", "High", "Yes", "Type-safe data with validation"],
    ]

    for _row in comparison_data:
        pass


def advanced_features_examples(employee_data):
    """Demonstrate advanced tabular data model features."""

    # Create model with advanced options
    model = TabularDataModel(
        employee_data,
        header_rows=1,
        skip_empty_rows=True,
    )

    # Column type inference
    for col_name in model.column_names:
        model.column_type(col_name)

    # Data validation and error handling

    # Test accessing non-existent columns/rows
    error_scenarios = [
        ("Non-existent column", lambda: model.column_values("NonExistent")),
        ("Row index out of bounds", lambda: model.row(999)),
        ("Column index out of bounds", lambda: model.cell_value("NonExistentColumn", 0)),
    ]

    for _scenario_name, test_func in error_scenarios:
        with contextlib.suppress(Exception):
            test_func()

    # Demonstrate row iteration methods
    for i, _row in enumerate(model):
        if i >= 2:
            break

    for i, _row_dict in enumerate(model.iter_rows()):
        if i >= 2:
            break

    for i, _row_tuple in enumerate(model.iter_rows_as_tuples()):
        if i >= 2:
            break


def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    import shutil

    shutil.rmtree(temp_dir)


if __name__ == "__main__":
    """Run all tabular data model examples."""

    # Create sample datasets
    employee_data, multi_header_data, large_file, temp_dir = create_sample_datasets()

    try:
        basic_tabular_model_examples(employee_data)
        multi_header_examples(multi_header_data)
        typed_tabular_model_examples(employee_data)
        streaming_model_examples(large_file)
        data_model_comparison()
        advanced_features_examples(employee_data)

    finally:
        cleanup_temp_files(temp_dir)
