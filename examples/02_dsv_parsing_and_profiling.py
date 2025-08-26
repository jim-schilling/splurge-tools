#!/usr/bin/env python3
"""
DSV Parsing and Profiling Examples

This example demonstrates the comprehensive DSV (Delimited Separated Values) parsing
capabilities of splurge-tools, including file parsing, streaming, and data profiling.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import tempfile
from pathlib import Path
from splurge_tools.dsv_helper import DsvHelper
from splurge_tools.type_helper import profile_values


def create_sample_data_files():
    """Create sample CSV files for demonstration."""
    # Create a temporary directory for our examples
    temp_dir = Path(tempfile.mkdtemp())
    
    # Sample CSV data
    csv_content = """Name,Age,City,Salary,Join Date,Active
John Doe,30,New York,75000.50,2023-01-15,true
Jane Smith,25,Los Angeles,65000.00,2023-03-20,true
Bob Johnson,45,Chicago,85000.75,2022-11-10,false
Alice Brown,35,Houston,72000.25,2023-05-05,true
Charlie Wilson,28,Phoenix,68000.00,2023-02-14,true"""
    
    # Large CSV for streaming demonstration
    large_csv_content = "ID,Value,Category,Timestamp\n"
    for i in range(1000):
        large_csv_content += f"{i},{i * 10.5},Category{i % 5},2023-{(i % 12) + 1:02d}-{(i % 28) + 1:02d}\n"
    
    # CSV with special characters and bookends
    special_csv_content = '''"Product Name","Description","Price","In Stock"
"Widget ""Pro""","High-quality widget with ""advanced"" features","$29.99","Yes"
"Gadget, Standard","Basic gadget, nothing special","$15.50","No"
"Tool Set","Complete tool set, includes: hammer, screwdriver, wrench","$45.00","Yes"'''
    
    # Write files
    files = {}
    files['basic'] = temp_dir / "employees.csv"
    files['large'] = temp_dir / "large_dataset.csv"
    files['special'] = temp_dir / "products.csv"
    
    files['basic'].write_text(csv_content)
    files['large'].write_text(large_csv_content)
    files['special'].write_text(special_csv_content)
    
    return temp_dir, files


def basic_dsv_parsing_examples(files):
    """Demonstrate basic DSV parsing capabilities."""
    print("=== Basic DSV Parsing Examples ===\n")
    
    # Parse simple string
    simple_data = "apple,banana,cherry"
    parsed = DsvHelper.parse(simple_data, delimiter=",")
    print(f"Simple string: '{simple_data}'")
    print(f"Parsed: {parsed}")
    print()
    
    # Parse multiple lines
    multi_line_data = [
        "Name,Age,City",
        "John,30,New York", 
        "Jane,25,Los Angeles"
    ]
    parsed_lines = DsvHelper.parses(multi_line_data, delimiter=",")
    print("Multi-line data:")
    for line in multi_line_data:
        print(f"  '{line}'")
    print("Parsed:")
    for i, row in enumerate(parsed_lines):
        print(f"  Row {i}: {row}")
    print()
    
    # Parse file
    print(f"Parsing file: {files['basic']}")
    file_data = DsvHelper.parse_file(files['basic'], delimiter=",")
    print("File contents (first 3 rows):")
    for i, row in enumerate(file_data[:3]):
        print(f"  Row {i}: {row}")
    print()


def advanced_dsv_parsing_examples(files):
    """Demonstrate advanced DSV parsing with bookends and special handling."""
    print("=== Advanced DSV Parsing Examples ===\n")
    
    # Parse with bookends (quoted fields)
    print(f"Parsing file with quotes: {files['special']}")
    quoted_data = DsvHelper.parse_file(
        files['special'], 
        delimiter=",",
        bookend='"',
        bookend_strip=True
    )
    
    print("Quoted CSV data (first 3 rows):")
    for i, row in enumerate(quoted_data[:3]):
        print(f"  Row {i}: {row}")
    print()
    
    # Parse with different delimiters
    tab_data = "Name\tAge\tCity\nJohn\t30\tNew York\nJane\t25\tLos Angeles"
    print("Tab-delimited data: '" + tab_data.replace(chr(9), '\\t') + "'")
    
    # Create temporary tab file
    temp_tab_file = files['basic'].parent / "temp_tab.tsv"
    temp_tab_file.write_text(tab_data)
    
    tab_parsed = DsvHelper.parse_file(temp_tab_file, delimiter="\t")
    print("Parsed tab data:")
    for i, row in enumerate(tab_parsed):
        print(f"  Row {i}: {row}")
    print()
    
    # Clean up temp file
    temp_tab_file.unlink()
    
    # Parse with whitespace handling
    messy_data = " apple , banana , cherry "
    print(f"Messy data: '{messy_data}'")
    
    parsed_no_strip = DsvHelper.parse(messy_data, delimiter=",", strip=False)
    parsed_with_strip = DsvHelper.parse(messy_data, delimiter=",", strip=True)
    
    print(f"Without stripping: {parsed_no_strip}")
    print(f"With stripping: {parsed_with_strip}")
    print()


def streaming_dsv_examples(files):
    """Demonstrate streaming DSV parsing for large files."""
    print("=== Streaming DSV Examples ===\n")
    
    print(f"Streaming large file: {files['large']}")
    print("Processing in chunks...")
    
    # Stream the large file in chunks
    chunk_count = 0
    total_rows = 0
    
    for chunk in DsvHelper.parse_stream(files['large'], delimiter=",", chunk_size=100):
        chunk_count += 1
        rows_in_chunk = len(chunk)
        total_rows += rows_in_chunk
        
        print(f"  Chunk {chunk_count}: {rows_in_chunk} rows")
        
        # Show first row of first chunk as example
        if chunk_count == 1 and chunk:
            print(f"    Sample row: {chunk[0]}")
        
        # Stop after a few chunks for demonstration
        if chunk_count >= 5:
            break
    
    print(f"Processed {chunk_count} chunks with {total_rows} total rows")
    print("Note: Streaming allows processing files larger than available RAM")
    print()


def dsv_profiling_examples(files):
    """Demonstrate DSV data profiling capabilities."""
    print("=== DSV Data Profiling Examples ===\n")
    
    # Parse and profile the basic employee data
    print(f"Profiling data from: {files['basic']}")
    employee_data = DsvHelper.parse_file(files['basic'], delimiter=",")
    
    # Profile columns using DsvHelper
    # Note: We need to extract the data without headers for profiling
    data_without_headers = employee_data[1:]  # Skip header row
    
    print("Column Analysis:")
    print("Column".ljust(15) + "Sample Values")
    print("-" * 50)
    
    # Analyze each column
    if data_without_headers:
        num_columns = len(data_without_headers[0])
        column_names = employee_data[0]  # Header row
        
        for col_idx in range(num_columns):
            col_name = column_names[col_idx]
            col_values = [row[col_idx] for row in data_without_headers if len(row) > col_idx]
            
            print(f"{col_name.ljust(15)}{col_values[:3]}")  # Show first 3 values
    
    print()
    
    # Demonstrate type inference on columns
    
    print("Type Inference by Column:")
    print("Column".ljust(15) + "Inferred Type".ljust(15) + "Sample Values")
    print("-" * 60)
    
    if data_without_headers:
        for col_idx in range(num_columns):
            col_name = column_names[col_idx]
            col_values = [row[col_idx] for row in data_without_headers if len(row) > col_idx]
            
            if col_values:
                inferred_type = profile_values(col_values)
                sample_vals = col_values[:2]  # Show first 2 values
                print(f"{col_name.ljust(15)}{inferred_type.name.ljust(15)}{sample_vals}")
    
    print()


def error_handling_examples(files):
    """Demonstrate error handling in DSV parsing."""
    print("=== Error Handling Examples ===\n")
    
    # Test various error conditions
    error_scenarios = [
        ("Empty delimiter", lambda: DsvHelper.parse("a,b,c", delimiter="")),
        ("None delimiter", lambda: DsvHelper.parse("a,b,c", delimiter=None)),
        ("Non-existent file", lambda: DsvHelper.parse_file("nonexistent.csv", delimiter=",")),
    ]
    
    for scenario_name, test_func in error_scenarios:
        print(f"Testing: {scenario_name}")
        try:
            result = test_func()
            print(f"  Unexpected success: {result}")
        except Exception as e:
            print(f"  Expected error: {type(e).__name__}: {e}")
        print()
    
    # Test malformed CSV handling
    malformed_csv = '''Name,Age,City
John,30,New York
Jane,25  # Missing city
Bob,45,Chicago,Extra Field'''
    
    temp_malformed = files['basic'].parent / "malformed.csv"
    temp_malformed.write_text(malformed_csv)
    
    print("Parsing malformed CSV:")
    try:
        malformed_data = DsvHelper.parse_file(temp_malformed, delimiter=",")
        print("Parsed successfully (with inconsistent row lengths):")
        for i, row in enumerate(malformed_data):
            print(f"  Row {i}: {row} (length: {len(row)})")
    except Exception as e:
        print(f"  Error: {e}")
    
    # Clean up
    temp_malformed.unlink()
    print()


def cleanup_temp_files(temp_dir):
    """Clean up temporary files."""
    import shutil
    shutil.rmtree(temp_dir)
    print(f"Cleaned up temporary files in: {temp_dir}")


if __name__ == "__main__":
    """Run all DSV parsing and profiling examples."""
    print("Splurge-Tools: DSV Parsing and Profiling Examples")
    print("=" * 60)
    print()
    
    # Create sample data files
    temp_dir, files = create_sample_data_files()
    print(f"Created sample files in: {temp_dir}")
    print()
    
    try:
        basic_dsv_parsing_examples(files)
        advanced_dsv_parsing_examples(files)
        streaming_dsv_examples(files)
        dsv_profiling_examples(files)
        error_handling_examples(files)
        
        print("Examples completed successfully!")
        print("\nKey Takeaways:")
        print("• DsvHelper.parse() handles single strings with delimiters")
        print("• DsvHelper.parses() processes lists of strings")
        print("• DsvHelper.parse_file() reads and parses entire files")
        print("• DsvHelper.parse_stream() enables memory-efficient processing")
        print("• Bookend handling supports quoted fields with embedded delimiters")
        print("• Built-in error handling for common parsing issues")
        print("• Integration with type inference for data profiling")
        
    finally:
        cleanup_temp_files(temp_dir)
