#!/usr/bin/env python3
"""
Streaming data processing example demonstrating memory-efficient data handling.

This example shows how to process large datasets using streaming techniques
that don't require loading the entire dataset into memory.

Copyright (c) 2025, Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import contextlib
import os
import tempfile

from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel

# Module-level constants for streaming data processing
_DEFAULT_NUM_ROWS = 10000  # Default number of rows to generate
_DEFAULT_CHUNK_SIZE = 500  # Default chunk size for processing
_DEFAULT_BUFFER_SIZE = 100  # Default buffer size for streaming model
_PROGRESS_INTERVAL = 1000  # Interval for progress reporting
_DEFAULT_AGE_MIN = 20  # Minimum age for generated data
_DEFAULT_AGE_RANGE = 50  # Age range for generated data
_DEFAULT_SALARY_BASE = 50000  # Base salary for generated data
_DEFAULT_SALARY_INCREMENT = 100  # Salary increment per row


def create_large_csv_file(
    file_path: str,
    *,
    num_rows: int = _DEFAULT_NUM_ROWS,
) -> None:
    """
    Create a large CSV file for testing.

    Args:
        file_path: Path to create the CSV file.
        num_rows: Number of data rows to create.
    """
    with open(file_path, "w", encoding="utf-8") as f:
        # Write header
        f.write("ID,Name,Age,City,Salary,Department\n")

        # Write data rows
        f.writelines(
            f"{i},Person{i},{_DEFAULT_AGE_MIN + (i % _DEFAULT_AGE_RANGE)},"
            f"{['NYC', 'LA', 'CHI', 'HOU'][i % 4]},"
            f"{_DEFAULT_SALARY_BASE + (i * _DEFAULT_SALARY_INCREMENT)},"
            f"{['IT', 'HR', 'Sales', 'Marketing'][i % 4]}\n"
            for i in range(num_rows)
        )


def process_large_dataset_streaming(
    file_path: str,
) -> None:
    """
    Process a large dataset using streaming approach.

    Args:
        file_path: Path to the CSV file to process.
    """

    # Create stream from DsvHelper
    stream = DsvHelper.parse_stream(
        file_path,
        delimiter=",",
        chunk_size=_DEFAULT_CHUNK_SIZE,  # Process 500 lines at a time
        skip_header_rows=0,  # We'll handle headers in the model
    )

    # Create streaming model
    model = StreamingTabularDataModel(
        stream,
        header_rows=1,
        skip_empty_rows=True,
        chunk_size=_DEFAULT_BUFFER_SIZE,  # Keep only 100 rows in memory at a time
    )

    # Process data in streaming fashion
    total_rows = 0
    total_salary = 0
    department_counts: dict[str, int] = {}

    for row in model.iter_rows():
        total_rows += 1

        # Calculate total salary
        salary = int(row["Salary"])
        total_salary += salary

        # Count departments
        dept = row["Department"]
        department_counts[dept] = department_counts.get(dept, 0) + 1

        # Print progress every 1000 rows
        if total_rows % _PROGRESS_INTERVAL == 0:
            pass

    # Demonstrate buffer operations
    model.clear_buffer()


def process_large_dataset_traditional(
    file_path: str,
) -> None:
    """
    Process a large dataset using traditional approach (loads everything into memory).

    Args:
        file_path: Path to the CSV file to process.
    """

    # Load entire file into memory
    data = DsvHelper.parse_file(file_path, delimiter=",")

    # Create traditional model
    from splurge_tools.tabular_data_model import TabularDataModel

    model = TabularDataModel(
        data,
        header_rows=1,
        skip_empty_rows=True,
    )

    # Process data
    total_salary = 0
    department_counts: dict[str, int] = {}

    for row in model.iter_rows():
        # Calculate total salary
        salary = int(row["Salary"])
        total_salary += salary

        # Count departments
        dept = row["Department"]
        department_counts[dept] = department_counts.get(dept, 0) + 1


def compare_memory_usage() -> None:
    """
    Compare memory usage between streaming and traditional approaches.
    """

    # Create a temporary large CSV file
    with tempfile.NamedTemporaryFile(mode="w", suffix=".csv", delete=False) as f:
        temp_file = f.name

    try:
        # Create a moderately large dataset
        create_large_csv_file(temp_file, num_rows=5000)  # Using smaller dataset for demo

        # Process with streaming approach
        process_large_dataset_streaming(temp_file)

        # Process with traditional approach
        process_large_dataset_traditional(temp_file)

    finally:
        os.unlink(temp_file)


def demonstrate_column_operations() -> None:
    """
    Demonstrate column operations with streaming model.
    """

    fd, temp_file = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("Name,Age,City,Salary\n")
            f.write("John,25,NYC,50000\n")
            f.write("Jane,30,LA,60000\n")
            f.write("Bob,35,CHI,55000\n")
        stream = DsvHelper.parse_stream(temp_file, delimiter=",", chunk_size=_DEFAULT_BUFFER_SIZE)
        model = StreamingTabularDataModel(
            stream,
            header_rows=1,
            skip_empty_rows=True,
            chunk_size=_DEFAULT_BUFFER_SIZE,
        )
        row_count = 0
        for _row in model.iter_rows():
            row_count += 1
            if row_count >= 3:
                break
    finally:
        with contextlib.suppress(PermissionError):
            os.unlink(temp_file)


def demonstrate_data_profiling() -> None:
    """
    Demonstrate data profiling capabilities.
    """
    fd, temp_file = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("ID,Name,Age,Salary,Active,Date\n")
            f.write("1,John,25,50000,true,2024-01-01\n")
            f.write("2,Jane,30,60000,false,2024-01-02\n")
            f.write("3,Bob,35,55000,true,2024-01-03\n")
            f.write("4,Alice,28,52000,true,2024-01-04\n")
        data = DsvHelper.parse_file(temp_file, delimiter=",")
        from splurge_tools.tabular_data_model import TabularDataModel

        model = TabularDataModel(
            data,
            header_rows=1,
            skip_empty_rows=True,
        )
        for column_name in model.column_names:
            model.column_type(column_name)
    finally:
        with contextlib.suppress(PermissionError):
            os.unlink(temp_file)


def demonstrate_error_handling() -> None:
    """
    Demonstrate error handling with streaming data.
    """
    fd, temp_file = tempfile.mkstemp(suffix=".csv")
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as f:
            f.write("ID,Name,Age,Salary\n")
            f.write("1,John,25,50000\n")
            f.write("2,Jane,invalid_age,60000\n")  # Invalid age
            f.write("3,Bob,35,invalid_salary\n")  # Invalid salary
            f.write("4,Alice,28,52000\n")
        stream = DsvHelper.parse_stream(temp_file, delimiter=",", chunk_size=_DEFAULT_BUFFER_SIZE)
        model = StreamingTabularDataModel(
            stream,
            header_rows=1,
            skip_empty_rows=True,
            chunk_size=_DEFAULT_BUFFER_SIZE,
        )
        total_rows = 0
        valid_salaries = 0
        total_salary = 0
        for row in model.iter_rows():
            total_rows += 1
            try:
                salary = int(row["Salary"])
                total_salary += salary
                valid_salaries += 1
            except ValueError:
                pass
            try:
                # age = int(row['Age'])  # Unused variable
                pass
            except ValueError:
                pass
        if valid_salaries > 0:
            pass
    finally:
        with contextlib.suppress(PermissionError):
            os.unlink(temp_file)


if __name__ == "__main__":
    # Demonstrate column operations
    demonstrate_column_operations()

    # Demonstrate data profiling
    demonstrate_data_profiling()

    # Demonstrate error handling
    demonstrate_error_handling()

    # Compare memory usage
    compare_memory_usage()
