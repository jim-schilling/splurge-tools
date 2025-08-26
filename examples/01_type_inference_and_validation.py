#!/usr/bin/env python3
"""
Type Inference and Validation Examples

This example demonstrates the comprehensive type inference and validation capabilities
of splurge-tools, including automatic type detection, conversion, and validation.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

from splurge_tools.type_helper import String, DataType, profile_values


def basic_type_inference_examples():
    """Demonstrate basic type inference capabilities."""
    print("=== Basic Type Inference Examples ===\n")
    
    # Various data types that can be automatically inferred
    test_values = [
        "123",           # INTEGER
        "123.45",        # FLOAT
        "true",          # BOOLEAN
        "false",         # BOOLEAN
        "2023-12-25",    # DATE
        "14:30:00",      # TIME
        "2023-12-25T14:30:00",  # DATETIME
        "hello world",   # STRING
        "",              # EMPTY
        None,            # NONE
    ]
    
    print("Value".ljust(25) + "Inferred Type")
    print("-" * 40)
    
    for value in test_values:
        inferred_type = String.infer_type(value)
        print(f"{str(value).ljust(25)}{inferred_type.name}")
    
    print()


def type_validation_examples():
    """Demonstrate type validation methods."""
    print("=== Type Validation Examples ===\n")
    
    # Test various validation methods
    validations = [
        ("123", "is_int_like", String.is_int_like),
        ("123.45", "is_float_like", String.is_float_like),
        ("true", "is_bool_like", String.is_bool_like),
        ("2023-12-25", "is_date_like", String.is_date_like),
        ("14:30:00", "is_time_like", String.is_time_like),
        ("2023-12-25T14:30:00", "is_datetime_like", String.is_datetime_like),
        ("", "is_empty_like", String.is_empty_like),
        (None, "is_none_like", String.is_none_like),
    ]
    
    print("Value".ljust(25) + "Validation Method".ljust(20) + "Result")
    print("-" * 50)
    
    for value, method_name, method in validations:
        try:
            result = method(value)
            print(f"{str(value).ljust(25)}{method_name.ljust(20)}{result}")
        except Exception as e:
            print(f"{str(value).ljust(25)}{method_name.ljust(20)}Error: {e}")
    
    print()


def type_conversion_examples():
    """Demonstrate type conversion with error handling."""
    print("=== Type Conversion Examples ===\n")
    
    # Safe type conversions with defaults
    conversions = [
        ("123", "to_int", lambda x: String.to_int(x, default=0)),
        ("123.45", "to_float", lambda x: String.to_float(x, default=0.0)),
        ("true", "to_bool", lambda x: String.to_bool(x)),
        ("2023-12-25", "to_date", lambda x: String.to_date(x)),
        ("14:30:00", "to_time", lambda x: String.to_time(x)),
        ("invalid_int", "to_int (with default)", lambda x: String.to_int(x, default=-1)),
        ("invalid_float", "to_float (with default)", lambda x: String.to_float(x, default=-1.0)),
    ]
    
    print("Value".ljust(20) + "Conversion".ljust(25) + "Result")
    print("-" * 60)
    
    for value, conversion_name, converter in conversions:
        try:
            result = converter(value)
            print(f"{str(value).ljust(20)}{conversion_name.ljust(25)}{result} ({type(result).__name__})")
        except Exception as e:
            print(f"{str(value).ljust(20)}{conversion_name.ljust(25)}Error: {e}")
    
    print()


def collection_type_profiling():
    """Demonstrate profiling collections of values."""
    print("=== Collection Type Profiling ===\n")
    
    # Different datasets with various type patterns
    datasets = {
        "Mixed Numbers": ["1", "2.5", "3", "4.0", "5"],
        "Dates": ["2023-01-01", "2023-12-25", "2024-03-15"],
        "Booleans": ["true", "false", "yes", "no", "1", "0"],
        "Mixed Types": ["123", "hello", "2023-01-01", "true", "45.67"],
        "Times": ["09:30:00", "14:45:30", "23:59:59"],
        "Empty and None": ["", None, "  ", "valid_data"],
    }
    
    for dataset_name, data in datasets.items():
        print(f"{dataset_name}:")
        print(f"  Data: {data}")
        
        # Profile the values to determine the dominant type
        profile_result = profile_values(data)
        print(f"  Profiled Type: {profile_result.name}")
        
        # Show individual type inferences
        individual_types = [String.infer_type(value).name for value in data]
        print(f"  Individual Types: {individual_types}")
        print()


def advanced_type_scenarios():
    """Demonstrate advanced type inference scenarios."""
    print("=== Advanced Type Scenarios ===\n")
    
    # Edge cases and special scenarios
    edge_cases = [
        "2023-02-29",     # Invalid date
        "25:00:00",       # Invalid time
        "123.45.67",      # Invalid float
        "+123",           # Positive integer
        "-456.78",        # Negative float
        "1.23e-4",        # Scientific notation
        "  123  ",        # Integer with whitespace
        "TRUE",           # Boolean in caps
        "Yes",            # Boolean variant
    ]
    
    print("Edge Case".ljust(20) + "Inferred Type".ljust(15) + "Can Convert?")
    print("-" * 50)
    
    for value in edge_cases:
        inferred_type = String.infer_type(value)
        
        # Try to convert based on inferred type
        can_convert = True
        try:
            if inferred_type == DataType.INTEGER:
                String.to_int(value)
            elif inferred_type == DataType.FLOAT:
                String.to_float(value)
            elif inferred_type == DataType.BOOLEAN:
                String.to_bool(value)
            elif inferred_type == DataType.DATE:
                String.to_date(value)
            elif inferred_type == DataType.TIME:
                String.to_time(value)
        except (ValueError, TypeError):
            can_convert = False
        
        print(f"{str(value).ljust(20)}{inferred_type.name.ljust(15)}{can_convert}")
    
    print()


def performance_considerations():
    """Demonstrate performance considerations with large datasets."""
    print("=== Performance Considerations ===\n")
    
    # Generate a large dataset for performance testing
    large_dataset = []
    
    # Add various types of data
    large_dataset.extend([str(i) for i in range(1000)])  # Integers
    large_dataset.extend([f"{i}.{i}" for i in range(100)])  # Floats
    large_dataset.extend(["true", "false"] * 50)  # Booleans
    large_dataset.extend([f"2023-{i:02d}-01" for i in range(1, 13)])  # Dates
    
    print(f"Profiling {len(large_dataset)} values...")
    
    # Profile the large dataset - this uses optimized incremental checking
    profile_result = profile_values(large_dataset, use_incremental_typecheck=True)
    print(f"Result: {profile_result.name}")
    print("Note: Large datasets use incremental type checking for better performance")
    print()


if __name__ == "__main__":
    """Run all type inference and validation examples."""
    print("Splurge-Tools: Type Inference and Validation Examples")
    print("=" * 60)
    print()
    
    basic_type_inference_examples()
    type_validation_examples()
    type_conversion_examples()
    collection_type_profiling()
    advanced_type_scenarios()
    performance_considerations()
    
    print("Examples completed successfully!")
    print("\nKey Takeaways:")
    print("• String.infer_type() automatically detects data types")
    print("• is_*_like() methods validate specific type formats")
    print("• to_*() methods safely convert with optional defaults")
    print("• profile_values() determines dominant type in collections")
    print("• Large datasets use optimized incremental type checking")
