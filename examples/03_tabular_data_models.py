#!/usr/bin/env python3
"""
Tabular Data Models Examples

This example demonstrates the tabular data model capabilities of splurge-tools,
including in-memory TabularDataModel and memory-efficient StreamingTabularDataModel.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import tempfile
from pathlib import Path
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.streaming_tabular_data_model import StreamingTabularDataModel
from splurge_tools.dsv_helper import DsvHelper


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
    with open(large_file, 'w') as f:
        f.write("ID,Name,Category,Value,Timestamp\n")
        for i in range(5000):
            f.write(f"{i},Item_{i},Category_{i % 10},{i * 1.5},2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}\n")
    
    return employee_data, multi_header_data, large_file, temp_dir


def basic_tabular_model_examples(employee_data):
    """Demonstrate basic TabularDataModel functionality."""
    print("=== Basic TabularDataModel Examples ===\n")
    
    # Create a basic tabular data model
    model = TabularDataModel(employee_data, header_rows=1)
    
    print(f"Dataset dimensions: {model.row_count} rows × {model.column_count} columns")
    print(f"Column names: {model.column_names}")
    print()
    
    # Access individual cells and rows
    print("Data Access Examples:")
    print(f"Cell ['Name', 0]: {model.cell_value('Name', 0)}")
    print(f"Cell ['Age', 1]: {model.cell_value('Age', 1)}")  # By name and row index
    print()
    
    # Get entire rows in different formats
    print("Row Access Examples:")
    print(f"Row 0 as list: {model.row_as_list(0)}")
    print(f"Row 1 as tuple: {model.row_as_tuple(1)}")
    print(f"Row 2 as dict: {model.row(2)}")
    print()
    
    # Column operations
    print("Column Operations:")
    print(f"Column 'Age' values: {model.column_values('Age')}")
    print(f"Column 'Department' unique values: {list(set(model.column_values('Department')))}")
    print()
    
    # Iterate through all rows
    print("Iteration Examples (first 3 rows):")
    for i, row in enumerate(model):
        if i >= 3:
            break
        print(f"  Row {i}: {row}")
    print()


def multi_header_examples(multi_header_data):
    """Demonstrate multi-row header handling."""
    print("=== Multi-Row Header Examples ===\n")
    
    print("Original multi-row header data:")
    for i, row in enumerate(multi_header_data[:3]):  # Show headers + 1 data row
        print(f"  Row {i}: {row}")
    print()
    
    # Process with multi-row headers
    model = TabularDataModel(multi_header_data, header_rows=2)
    
    print(f"Processed column names: {model.column_names}")
    print(f"Data dimensions: {model.row_count} rows × {model.column_count} columns")
    print()
    
    # Show how headers were merged
    print("Header processing details:")
    print("  Header rows: 2")
    print(f"  Raw header data: {multi_header_data[:2]}")
    print(f"  Merged column names: {model.column_names}")
    print()
    
    # Access data with merged headers
    print("Data access with merged headers:")
    print(f"First row as dict: {model.row(0)}")
    print()


def typed_tabular_model_examples(employee_data):
    """Demonstrate typed view with schema validation."""
    print("=== Typed View Examples ===\n")
    
    # Create typed view (automatically infers types)
    typed_model = TabularDataModel(
        employee_data, 
        header_rows=1
    ).to_typed()
    
    print("Typed model created successfully!")
    print(f"Dimensions: {typed_model.row_count} rows × {typed_model.column_count} columns")
    print()
    
    # Access typed data
    print("Typed data access:")
    for i in range(min(3, typed_model.row_count)):
        row_dict = typed_model.row(i)
        print(f"  Row {i}:")
        for col_name, value in row_dict.items():
            print(f"    {col_name}: {value} ({type(value).__name__})")
        print()
    
    # Demonstrate type inference
    print("Automatic type inference:")
    for col_name in typed_model.column_names:
        col_type = TabularDataModel(employee_data, header_rows=1).column_type(col_name)
        print(f"  {col_name}: Inferred as {col_type.name}")
    print()


def streaming_model_examples(large_file):
    """Demonstrate StreamingTabularDataModel for large datasets."""
    print("=== StreamingTabularDataModel Examples ===\n")
    
    print(f"Processing large file: {large_file}")
    print(f"File size: {large_file.stat().st_size / 1024 / 1024:.1f} MB")
    print()
    
    # Create streaming model
    stream = DsvHelper.parse_stream(large_file, delimiter=",", chunk_size=500)
    streaming_model = StreamingTabularDataModel(
        stream, 
        header_rows=1,
        chunk_size=1000
    )
    
    print(f"Column names: {streaming_model.column_names}")
    print(f"Column count: {streaming_model.column_count}")
    print()
    
    # Process data in streaming fashion
    print("Streaming data processing (first 10 rows):")
    row_count = 0
    for row in streaming_model:
        if row_count >= 10:
            break
        print(f"  Row {row_count}: {row}")
        row_count += 1
    
    print(f"Processed {row_count} rows (streaming continues...)")
    print()
    
    # Reset stream and demonstrate dictionary iteration
    streaming_model.reset_stream()
    
    print("Dictionary iteration (first 5 rows):")
    dict_count = 0
    for row_dict in streaming_model.iter_rows():
        if dict_count >= 5:
            break
        print(f"  Row {dict_count}: {dict_count} -> {row_dict['Name']}, {row_dict['Category']}")
        dict_count += 1
    
    print()
    
    # Demonstrate memory efficiency
    print("Memory Efficiency Benefits:")
    print("• Processes files larger than available RAM")
    print("• Configurable chunk sizes for optimal performance")
    print("• Forward-only iteration minimizes memory usage")
    print("• Automatic stream reset capability")
    print()


def data_model_comparison():
    """Compare different data model types and their use cases."""
    print("=== Data Model Comparison ===\n")
    
    comparison_data = [
        ["Model Type", "Memory Usage", "Random Access", "Best Use Case"],
        ["TabularDataModel", "High", "Yes", "Small to medium datasets, analysis"],
        ["StreamingTabularDataModel", "Low", "No", "Large datasets, ETL processing"],
        ["Typed View", "High", "Yes", "Type-safe data with validation"],
    ]
    
    print("Data Model Comparison:")
    for row in comparison_data:
        print("  " + " | ".join(f"{cell:25}" for cell in row))
    print()
    
    print("Selection Guidelines:")
    print("• Use TabularDataModel for datasets < 100MB that fit in memory")
    print("• Use StreamingTabularDataModel for datasets > 100MB or limited memory")
    print("• Use TabularDataModel.to_typed() when type safety and validation are critical")
    print("• All models support multi-row headers and empty row handling")
    print()


def advanced_features_examples(employee_data):
    """Demonstrate advanced tabular data model features."""
    print("=== Advanced Features Examples ===\n")
    
    # Create model with advanced options
    model = TabularDataModel(
        employee_data, 
        header_rows=1,
        skip_empty_rows=True
    )
    
    # Column type inference
    print("Column Type Inference:")
    for col_name in model.column_names:
        col_type = model.column_type(col_name)
        print(f"  {col_name}: {col_type.name}")
    print()
    
    # Data validation and error handling
    print("Data Validation Examples:")
    
    # Test accessing non-existent columns/rows
    error_scenarios = [
        ("Non-existent column", lambda: model.column_values("NonExistent")),
        ("Row index out of bounds", lambda: model.row(999)),
        ("Column index out of bounds", lambda: model.cell_value("NonExistentColumn", 0)),
    ]
    
    for scenario_name, test_func in error_scenarios:
        try:
            result = test_func()
            print(f"  {scenario_name}: Unexpected success - {result}")
        except Exception as e:
            print(f"  {scenario_name}: {type(e).__name__} - {e}")
    
    print()
    
    # Demonstrate row iteration methods
    print("Different Iteration Methods:")
    print("  Standard iteration (lists):")
    for i, row in enumerate(model):
        if i >= 2:
            break
        print(f"    {row}")
    
    print("  Dictionary iteration:")
    for i, row_dict in enumerate(model.iter_rows()):
        if i >= 2:
            break
        print(f"    {row_dict}")
    
    print("  Tuple iteration:")
    for i, row_tuple in enumerate(model.iter_rows_as_tuples()):
        if i >= 2:
            break
        print(f"    {row_tuple}")
    
    print()


def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    import shutil
    shutil.rmtree(temp_dir)
    print(f"Cleaned up temporary files in: {temp_dir}")


if __name__ == "__main__":
    """Run all tabular data model examples."""
    print("Splurge-Tools: Tabular Data Models Examples")
    print("=" * 60)
    print()
    
    # Create sample datasets
    employee_data, multi_header_data, large_file, temp_dir = create_sample_datasets()
    
    try:
        basic_tabular_model_examples(employee_data)
        multi_header_examples(multi_header_data)
        typed_tabular_model_examples(employee_data)
        streaming_model_examples(large_file)
        data_model_comparison()
        advanced_features_examples(employee_data)
        
        print("Examples completed successfully!")
        print("\nKey Takeaways:")
        print("• TabularDataModel provides full random access to in-memory data")
        print("• StreamingTabularDataModel enables processing of large datasets")
        print("• TabularDataModel.to_typed() adds type safety and validation")
        print("• Multi-row headers are automatically merged into column names")
        print("• Multiple iteration methods (list, dict, tuple) available")
        print("• Built-in type inference for automatic column type detection")
        print("• Comprehensive error handling for invalid access patterns")
        
    finally:
        cleanup_temp_files(temp_dir)
