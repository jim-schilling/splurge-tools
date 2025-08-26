#!/usr/bin/env python3
"""
Streaming data processing example demonstrating memory-efficient data handling.

This example shows how to process large datasets using streaming techniques
that don't require loading the entire dataset into memory.

Copyright (c) 2025, Jim Schilling

Please preserve this header and all related material when sharing!

This module is licensed under the MIT License.
"""

import os
import tempfile
from typing import Dict

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
    num_rows: int = _DEFAULT_NUM_ROWS
) -> None:
    """
    Create a large CSV file for testing.
    
    Args:
        file_path: Path to create the CSV file.
        num_rows: Number of data rows to create.
    """
    with open(file_path, 'w', encoding='utf-8') as f:
        # Write header
        f.write("ID,Name,Age,City,Salary,Department\n")
        
        # Write data rows
        for i in range(num_rows):
            f.write(
                f"{i},Person{i},{_DEFAULT_AGE_MIN + (i % _DEFAULT_AGE_RANGE)},"
                f"{['NYC', 'LA', 'CHI', 'HOU'][i % 4]},"
                f"{_DEFAULT_SALARY_BASE + (i * _DEFAULT_SALARY_INCREMENT)},"
                f"{['IT', 'HR', 'Sales', 'Marketing'][i % 4]}\n"
            )


def process_large_dataset_streaming(
    file_path: str
) -> None:
    """
    Process a large dataset using streaming approach.
    
    Args:
        file_path: Path to the CSV file to process.
    """
    print(f"Processing large dataset: {file_path}")
    
    # Create stream from DsvHelper
    stream = DsvHelper.parse_stream(
        file_path,
        delimiter=",",
        chunk_size=_DEFAULT_CHUNK_SIZE,  # Process 500 lines at a time
        skip_header_rows=0  # We'll handle headers in the model
    )
    
    # Create streaming model
    model = StreamingTabularDataModel(
        stream,
        header_rows=1,
        skip_empty_rows=True,
        chunk_size=_DEFAULT_BUFFER_SIZE  # Keep only 100 rows in memory at a time
    )
    
    print(f"Column names: {model.column_names}")
    print(f"Number of columns: {model.column_count}")
    
    # Process data in streaming fashion
    total_rows = 0
    total_salary = 0
    department_counts: Dict[str, int] = {}
    
    print("Processing rows...")
    for row in model.iter_rows():
        total_rows += 1
        
        # Calculate total salary
        salary = int(row['Salary'])
        total_salary += salary
        
        # Count departments
        dept = row['Department']
        department_counts[dept] = department_counts.get(dept, 0) + 1
        
        # Print progress every 1000 rows
        if total_rows % _PROGRESS_INTERVAL == 0:
            print(f"Processed {total_rows} rows...")
    
    print("\nProcessing complete!")
    print(f"Total rows processed: {total_rows}")
    print(f"Average salary: ${total_salary / total_rows:,.2f}")
    print(f"Department distribution: {department_counts}")
    
    # Demonstrate buffer operations
    print(f"\nBuffer size after processing: {len(model._buffer)}")
    model.clear_buffer()
    print(f"Buffer size after clearing: {len(model._buffer)}")


def process_large_dataset_traditional(
    file_path: str
) -> None:
    """
    Process a large dataset using traditional approach (loads everything into memory).
    
    Args:
        file_path: Path to the CSV file to process.
    """
    print(f"Processing large dataset (traditional): {file_path}")
    
    # Load entire file into memory
    data = DsvHelper.parse_file(file_path, ",")
    
    # Create traditional model
    from splurge_tools.tabular_data_model import TabularDataModel
    model = TabularDataModel(
        data,
        header_rows=1,
        skip_empty_rows=True
    )
    
    print(f"Column names: {model.column_names}")
    print(f"Number of columns: {model.column_count}")
    print(f"Total rows loaded into memory: {model.row_count}")
    
    # Process data
    total_salary = 0
    department_counts: Dict[str, int] = {}
    
    print("Processing rows...")
    for row in model.iter_rows():
        # Calculate total salary
        salary = int(row['Salary'])
        total_salary += salary
        
        # Count departments
        dept = row['Department']
        department_counts[dept] = department_counts.get(dept, 0) + 1
    
    print("\nProcessing complete!")
    print(f"Total rows processed: {model.row_count}")
    print(f"Average salary: ${total_salary / model.row_count:,.2f}")
    print(f"Department distribution: {department_counts}")


def compare_memory_usage() -> None:
    """
    Compare memory usage between streaming and traditional approaches.
    """
    print("=== Memory Usage Comparison ===\n")
    
    # Create a temporary large CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        temp_file = f.name
    
    try:
        # Create a moderately large dataset
        print("Creating test dataset...")
        create_large_csv_file(temp_file, num_rows=5000)  # Using smaller dataset for demo
        
        print("File size:", os.path.getsize(temp_file), "bytes")
        print()
        
        # Process with streaming approach
        print("=== Streaming Approach ===")
        process_large_dataset_streaming(temp_file)
        print()
        
        # Process with traditional approach
        print("=== Traditional Approach ===")
        process_large_dataset_traditional(temp_file)
        print()
        
        print("Note: The streaming approach uses significantly less memory")
        print("because it only keeps a small buffer of rows in memory at a time.")
        
    finally:
        os.unlink(temp_file)


def demonstrate_column_operations() -> None:
    """
    Demonstrate column operations with streaming model.
    """
    print("=== Column Operations Demo ===\n")
    
    fd, temp_file = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("Name,Age,City,Salary\n")
            f.write("John,25,NYC,50000\n")
            f.write("Jane,30,LA,60000\n")
            f.write("Bob,35,CHI,55000\n")
        stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=_DEFAULT_BUFFER_SIZE)
        model = StreamingTabularDataModel(
            stream,
            header_rows=1,
            skip_empty_rows=True,
            chunk_size=_DEFAULT_BUFFER_SIZE
        )
        print(f"Column names: {model.column_names}")
        print(f"Column count: {model.column_count}")
        print(f"\nColumn 'Name' index: {model.column_index('Name')}")
        print("Note: StreamingTabularDataModel doesn't support column_values()")
        print("or column_type() as it doesn't keep all data in memory.")
        print("\nFirst few rows:")
        row_count = 0
        for row in model.iter_rows():
            print(f"Row {row_count}: {row}")
            row_count += 1
            if row_count >= 3:
                break
    finally:
        try:
            os.unlink(temp_file)
        except PermissionError:
            pass


def demonstrate_data_profiling() -> None:
    """
    Demonstrate data profiling capabilities.
    """
    print("=== Data Profiling Demo ===\n")
    fd, temp_file = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("ID,Name,Age,Salary,Active,Date\n")
            f.write("1,John,25,50000,true,2024-01-01\n")
            f.write("2,Jane,30,60000,false,2024-01-02\n")
            f.write("3,Bob,35,55000,true,2024-01-03\n")
            f.write("4,Alice,28,52000,true,2024-01-04\n")
        data = DsvHelper.parse_file(temp_file, ",")
        from splurge_tools.tabular_data_model import TabularDataModel
        model = TabularDataModel(
            data,
            header_rows=1,
            skip_empty_rows=True
        )
        print("Data Profile:")
        for column_name in model.column_names:
            column_type = model.column_type(column_name)
            print(f"  {column_name}: {column_type.name}")
        print(f"\nAge values: {model.column_values('Age')}")
        print(f"Active values: {model.column_values('Active')}")
    finally:
        try:
            os.unlink(temp_file)
        except PermissionError:
            pass


def demonstrate_error_handling() -> None:
    """
    Demonstrate error handling with streaming data.
    """
    print("=== Error Handling Demo ===\n")
    fd, temp_file = tempfile.mkstemp(suffix='.csv')
    try:
        with os.fdopen(fd, 'w', encoding='utf-8') as f:
            f.write("ID,Name,Age,Salary\n")
            f.write("1,John,25,50000\n")
            f.write("2,Jane,invalid_age,60000\n")  # Invalid age
            f.write("3,Bob,35,invalid_salary\n")   # Invalid salary
            f.write("4,Alice,28,52000\n")
        stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=_DEFAULT_BUFFER_SIZE)
        model = StreamingTabularDataModel(
            stream,
            header_rows=1,
            skip_empty_rows=True,
            chunk_size=_DEFAULT_BUFFER_SIZE
        )
        print("Processing rows with error handling:")
        total_rows = 0
        valid_salaries = 0
        total_salary = 0
        for row in model.iter_rows():
            total_rows += 1
            try:
                salary = int(row['Salary'])
                total_salary += salary
                valid_salaries += 1
            except ValueError:
                print(f"  Warning: Invalid salary in row {total_rows}: {row['Salary']}")
            try:
                # age = int(row['Age'])  # Unused variable
                pass
            except ValueError:
                print(f"  Warning: Invalid age in row {total_rows}: {row['Age']}")
        print("\nProcessing complete!")
        print(f"Total rows processed: {total_rows}")
        print(f"Valid salaries: {valid_salaries}")
        if valid_salaries > 0:
            print(f"Average valid salary: ${total_salary / valid_salaries:,.2f}")
    finally:
        try:
            os.unlink(temp_file)
        except PermissionError:
            pass


if __name__ == "__main__":
    print("StreamingTabularDataModel Example")
    print("=" * 40)
    print()
    
    # Demonstrate column operations
    demonstrate_column_operations()
    print()
    
    # Demonstrate data profiling
    demonstrate_data_profiling()
    print()
    
    # Demonstrate error handling
    demonstrate_error_handling()
    print()
    
    # Compare memory usage
    compare_memory_usage() 