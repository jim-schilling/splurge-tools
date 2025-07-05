#!/usr/bin/env python3
"""
Example demonstrating StreamingTabularDataModel with large datasets.

This example shows how to process large CSV files without loading
the entire dataset into memory using DsvHelper.parse_stream and
StreamingTabularDataModel.

Copyright (c) 2025, Jim Schilling

This module is licensed under the MIT License.
"""

import tempfile
import os
from typing import Iterator

from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel


def create_large_csv_file(
    file_path: str,
    num_rows: int = 10000
) -> None:
    """
    Create a large CSV file for testing.
    
    Args:
        file_path (str): Path to create the CSV file.
        num_rows (int): Number of data rows to create.
    """
    with open(file_path, 'w') as f:
        # Write header
        f.write("ID,Name,Age,City,Salary,Department\n")
        
        # Write data rows
        for i in range(num_rows):
            f.write(f"{i},Person{i},{20 + (i % 50)},{['NYC', 'LA', 'CHI', 'HOU'][i % 4]},{50000 + (i * 100)},{['IT', 'HR', 'Sales', 'Marketing'][i % 4]}\n")


def process_large_dataset_streaming(
    file_path: str
) -> None:
    """
    Process a large dataset using streaming approach.
    
    Args:
        file_path (str): Path to the CSV file to process.
    """
    print(f"Processing large dataset: {file_path}")
    
    # Create stream from DsvHelper
    stream = DsvHelper.parse_stream(
        file_path,
        delimiter=",",
        chunk_size=500,  # Process 500 lines at a time
        skip_header_rows=0  # We'll handle headers in the model
    )
    
    # Create streaming model
    model = StreamingTabularDataModel(
        stream,
        header_rows=1,
        multi_row_headers=1,
        skip_empty_rows=True,
        chunk_size=100  # Keep only 100 rows in memory at a time
    )
    
    print(f"Column names: {model.column_names}")
    print(f"Number of columns: {model.column_count}")
    
    # Process data in streaming fashion
    total_rows = 0
    total_salary = 0
    department_counts = {}
    
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
        if total_rows % 1000 == 0:
            print(f"Processed {total_rows} rows...")
    
    print(f"\nProcessing complete!")
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
        file_path (str): Path to the CSV file to process.
    """
    print(f"Processing large dataset (traditional): {file_path}")
    
    # Load entire file into memory
    data = DsvHelper.parse_file(file_path, ",")
    
    # Create traditional model
    from splurge_tools.tabular_data_model import TabularDataModel
    model = TabularDataModel(
        data,
        header_rows=1,
        multi_row_headers=1,
        skip_empty_rows=True
    )
    
    print(f"Column names: {model.column_names}")
    print(f"Number of columns: {model.column_count}")
    print(f"Total rows loaded into memory: {model.row_count}")
    
    # Process data
    total_salary = 0
    department_counts = {}
    
    print("Processing rows...")
    for row in model.iter_rows():
        # Calculate total salary
        salary = int(row['Salary'])
        total_salary += salary
        
        # Count departments
        dept = row['Department']
        department_counts[dept] = department_counts.get(dept, 0) + 1
    
    print(f"\nProcessing complete!")
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
        create_large_csv_file(temp_file, 5000)
        
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
    
    # Create a temporary CSV file
    with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
        f.write("Name,Age,City,Salary\n")
        f.write("John,25,NYC,50000\n")
        f.write("Jane,30,LA,60000\n")
        f.write("Bob,35,CHI,55000\n")
        temp_file = f.name
    
    try:
        # Create stream and model
        stream = DsvHelper.parse_stream(temp_file, ",", chunk_size=2)
        model = StreamingTabularDataModel(
            stream,
            header_rows=1,
            multi_row_headers=1,
            skip_empty_rows=True,
            chunk_size=100
        )
        
        print(f"Column names: {model.column_names}")
        print(f"Column count: {model.column_count}")
        
        # Demonstrate column operations
        print(f"\nColumn 'Name' index: {model.column_index('Name')}")
        print(f"Column 'Age' values: {model.column_values('Age')}")
        print(f"Column 'Salary' type: {model.column_type('Salary')}")
        
        # Demonstrate row access
        print(f"\nFirst row: {model.row(0)}")
        print(f"Cell value (Name, row 1): {model.cell_value('Name', 1)}")
        
    finally:
        os.unlink(temp_file)


if __name__ == "__main__":
    print("StreamingTabularDataModel Example")
    print("=" * 40)
    print()
    
    # Demonstrate column operations
    demonstrate_column_operations()
    print()
    
    # Compare memory usage
    compare_memory_usage() 