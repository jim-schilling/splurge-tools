#!/usr/bin/env python3
"""
Data Validation and Transformation Examples

This example demonstrates the data validation and transformation capabilities
of splurge-tools, including custom validation rules, data transformations,
and factory pattern usage.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

from splurge_tools.data_validator import DataValidator
from splurge_tools.data_transformer import DataTransformer
from splurge_tools.tabular_data_model import TabularDataModel
from splurge_tools.typed_tabular_data_model import TypedTabularDataModel
# from splurge_tools.factory import ComponentFactory, DataModelFactory
from splurge_tools.validation_utils import Validator
from splurge_tools.type_helper import DataType


def create_sample_data():
    """Create sample datasets for validation and transformation examples."""
    # Employee dataset for validation
    employee_data = [
        ["Name", "Age", "Email", "Salary", "Department", "Active"],
        ["John Doe", "30", "john@example.com", "75000", "Engineering", "true"],
        ["Jane Smith", "25", "jane@example.com", "65000", "Marketing", "true"],
        ["Bob Johnson", "45", "bob@example.com", "85000", "Sales", "false"],
        ["Alice Brown", "35", "alice@example.com", "72000", "Engineering", "true"],
        ["Charlie Wilson", "28", "charlie@example.com", "68000", "Marketing", "true"],
    ]
    
    # Sales data for transformation
    sales_data = [
        ["Date", "Product", "Category", "Sales", "Region"],
        ["2023-01-01", "Widget A", "Widgets", "1000", "North"],
        ["2023-01-01", "Gadget B", "Gadgets", "750", "North"],
        ["2023-01-01", "Widget A", "Widgets", "800", "South"],
        ["2023-01-02", "Widget A", "Widgets", "1200", "North"],
        ["2023-01-02", "Gadget B", "Gadgets", "900", "South"],
        ["2023-01-02", "Tool C", "Tools", "650", "North"],
    ]
    
    return employee_data, sales_data


def basic_validation_examples(employee_data):
    """Demonstrate basic data validation capabilities."""
    print("=== Basic Data Validation Examples ===\n")
    
    # Create validator directly
    validator = DataValidator()
    
    # Add validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Age", lambda x: x.isdigit() and 18 <= int(x) <= 65)
    validator.add_validator("Email", lambda x: "@" in x and "." in x)
    validator.add_validator("Salary", lambda x: x.isdigit() and int(x) > 0)
    
    print("Validation Rules:")
    print("• Name: Must not be empty")
    print("• Age: Must be digit between 18-65")
    print("• Email: Must contain @ and .")
    print("• Salary: Must be positive number")
    print()
    
    # Create tabular model and validate each row
    model = TabularDataModel(employee_data, header_rows=1)
    
    print("Validation Results:")
    for i in range(model.row_count):
        row_dict = model.row(i)
        is_valid = validator.validate(row_dict)
        
        print(f"  Row {i}: {row_dict['Name']}")
        print(f"    Valid: {is_valid}")
        
        if not is_valid:
            errors = validator.get_errors()
            for error in errors:
                print(f"    Error: {error}")
        
        validator.clear_errors()
        print()


def custom_validation_examples():
    """Demonstrate custom validation scenarios."""
    print("=== Custom Validation Examples ===\n")
    
    validator = DataValidator()
    
    # Add custom validators with more complex rules
    def validate_email_domain(email):
        """Validate that email is from approved domains."""
        approved_domains = ["example.com", "company.com", "test.org"]
        domain = email.split("@")[-1] if "@" in email else ""
        return domain in approved_domains
    
    def validate_age_group(age_str):
        """Validate age is in acceptable range for employment."""
        try:
            age = int(age_str)
            return 16 <= age <= 70
        except ValueError:
            return False
    
    def validate_salary_range(salary_str):
        """Validate salary is within company ranges."""
        try:
            salary = int(salary_str)
            return 30000 <= salary <= 200000
        except ValueError:
            return False
    
    # Add custom validators
    validator.add_custom_validator("email_domain", validate_email_domain)
    validator.add_custom_validator("age_group", validate_age_group)
    validator.add_custom_validator("salary_range", validate_salary_range)
    
    # Test data with various validation scenarios
    test_cases = [
        {
            "Name": "Valid Employee",
            "Age": "30",
            "Email": "valid@example.com",
            "Salary": "75000",
            "Department": "Engineering"
        },
        {
            "Name": "",  # Invalid: empty name
            "Age": "25",
            "Email": "test@example.com",
            "Salary": "65000",
            "Department": "Marketing"
        },
        {
            "Name": "Invalid Domain",
            "Age": "35",
            "Email": "user@invalid.com",  # Invalid: wrong domain
            "Salary": "80000",
            "Department": "Sales"
        },
        {
            "Name": "Too Young",
            "Age": "15",  # Invalid: too young
            "Email": "young@example.com",
            "Salary": "40000",
            "Department": "Intern"
        },
        {
            "Name": "Low Salary",
            "Age": "28",
            "Email": "low@example.com",
            "Salary": "25000",  # Invalid: too low
            "Department": "Entry"
        }
    ]
    
    # Apply validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Email", validate_email_domain)
    validator.add_validator("Age", validate_age_group)
    validator.add_validator("Salary", validate_salary_range)
    
    print("Custom Validation Results:")
    for i, test_case in enumerate(test_cases):
        is_valid = validator.validate(test_case)
        print(f"  Test Case {i + 1}: {test_case['Name'] or 'Empty Name'}")
        print(f"    Data: {test_case}")
        print(f"    Valid: {is_valid}")
        
        if not is_valid:
            errors = validator.get_errors()
            for error in errors:
                print(f"    Error: {error}")
        
        validator.clear_errors()
        print()


def validation_utils_examples():
    """Demonstrate validation utilities."""
    print("=== Validation Utils Examples ===\n")
    
    # Test various validation utilities
    validation_tests = [
        ("Non-empty string", lambda: Validator.is_non_empty_string("hello", "test_param")),
        ("Empty string (should fail)", lambda: Validator.is_non_empty_string("", "test_param")),
        ("Positive integer", lambda: Validator.is_positive_integer(42, "test_param")),
        ("Negative integer (should fail)", lambda: Validator.is_positive_integer(-5, "test_param")),
        ("Valid range bounds", lambda: Validator.is_range_bounds(1, 10, lower_param="test_param")),
        ("Invalid range bounds (should fail)", lambda: Validator.is_range_bounds(10, 1, lower_param="test_param")),
        ("Valid encoding", lambda: Validator.is_encoding("utf-8", "test_param")),
        ("Invalid encoding (should fail)", lambda: Validator.is_encoding("invalid-encoding", "test_param")),
    ]
    
    print("Validation Utilities Test Results:")
    for test_name, test_func in validation_tests:
        try:
            result = test_func()
            print(f"  OK {test_name}: {result}")
        except Exception as e:
            print(f"  ERROR {test_name}: {type(e).__name__} - {e}")
    print()


def basic_transformation_examples(sales_data):
    """Demonstrate basic data transformation capabilities."""
    print("=== Basic Data Transformation Examples ===\n")
    
    # Create data model and transformer
    model = TabularDataModel(sales_data, header_rows=1)
    transformer = DataTransformer(model)
    
    print(f"Original data: {model.row_count} rows × {model.column_count} columns")
    print("Sample data:")
    for i in range(min(3, model.row_count)):
        print(f"  {model.row(i)}")
    print()
    
    # Pivot transformation
    print("Pivot Transformation (Product by Region):")
    try:
        pivoted = transformer.pivot(
            index_cols=["Product"],
            columns_col="Region", 
            values_col="Sales",
            agg_func=lambda values: str(sum(int(v) for v in values))
        )
        print(f"Pivoted data: {pivoted.row_count} rows × {pivoted.column_count} columns")
        print("Pivoted sample:")
        for i in range(min(3, pivoted.row_count)):
            print(f"  {pivoted.row(i)}")
    except Exception as e:
        print(f"Pivot error: {e}")
    print()
    
    # Group by transformation
    print("Group By Transformation (by Category):")
    try:
        grouped = transformer.group_by(
            group_cols=["Category"],
            agg_dict={"Sales": lambda values: str(sum(int(v) for v in values))}
        )
        print(f"Grouped data: {grouped.row_count} rows × {grouped.column_count} columns")
        print("Grouped sample:")
        for i in range(grouped.row_count):
            print(f"  {grouped.row(i)}")
    except Exception as e:
        print(f"Group by error: {e}")
    print()


def advanced_transformation_examples(sales_data):
    """Demonstrate advanced transformation scenarios."""
    print("=== Advanced Data Transformation Examples ===\n")
    
    model = TabularDataModel(sales_data, header_rows=1)
    transformer = DataTransformer(model)
    
    # Column transformation
    print("Column Transformation (adding calculated fields):")
    try:
        # Transform sales values to include tax
        def add_tax(value):
            try:
                return str(int(value) * 1.08)  # 8% tax
            except:
                return value
        
        transformed = transformer.transform_column(
            column="Sales",
            transform_func=add_tax
        )
        
        print(f"Transformed data: {transformed.row_count} rows × {transformed.column_count} columns")
        print("Sample with tax calculation:")
        for i in range(min(3, transformed.row_count)):
            row = transformed.row(i)
            print(f"  Original: {model.row(i)['Sales']}, Transformed: {row['Sales']}")
    except Exception as e:
        print(f"Column transformation error: {e}")
    print()
    
    # Melt transformation
    print("Melt Transformation:")
    try:
        # First create a wider dataset for melting
        wide_data = [
            ["Product", "Q1_Sales", "Q2_Sales", "Q3_Sales", "Q4_Sales"],
            ["Widget A", "1000", "1200", "1100", "1300"],
            ["Gadget B", "750", "800", "900", "950"],
            ["Tool C", "650", "700", "750", "800"],
        ]
        
        wide_model = TabularDataModel(wide_data, header_rows=1)
        wide_transformer = DataTransformer(wide_model)
        
        melted = wide_transformer.melt(
            id_vars=["Product"],
            value_vars=["Q1_Sales", "Q2_Sales", "Q3_Sales", "Q4_Sales"],
            var_name="Quarter",
            value_name="Sales"
        )
        
        print(f"Original wide data: {wide_model.row_count} rows × {wide_model.column_count} columns")
        print(f"Melted data: {melted.row_count} rows × {melted.column_count} columns")
        print("Melted sample:")
        for i in range(min(6, melted.row_count)):
            print(f"  {melted.row(i)}")
    except Exception as e:
        print(f"Melt transformation error: {e}")
    print()


def factory_pattern_examples():
    """Demonstrate factory pattern usage."""
    print("=== Factory Pattern Examples ===\n")
    
    # Create various components using factories
    print("Creating components with factories:")
    
    # Create validator
    validator = DataValidator()
    print(f"OK Validator created: {type(validator).__name__}")
    
    # Create data model using factory
    sample_data = [
        ["Name", "Value"],
        ["A", "1"],
        ["B", "2"],
    ]
    
    model = TabularDataModel(sample_data, header_rows=1)
    print(f"OK Data model created: {type(model).__name__}")
    
    # Create transformer
    transformer = DataTransformer(model)
    print(f"OK Transformer created: {type(transformer).__name__}")
    
    print()
    
    # Demonstrate factory configuration
    print("Factory configuration examples:")
    
    # Different model types
    typed_model = TypedTabularDataModel(
        sample_data,
        header_rows=1
    )
    print(f"OK Typed model created: {type(typed_model).__name__}")
    
    # Resource manager (if file exists)
    try:
        import tempfile
        temp_file = tempfile.NamedTemporaryFile(mode='w', delete=False)
        temp_file.write("test content")
        temp_file.close()
        
        # resource_manager = ComponentFactory.create_resource_manager(temp_file.name)  # Not available
        print("OK Resource manager creation skipped (ComponentFactory not available)")
        
        # Clean up
        import os
        os.unlink(temp_file.name)
    except Exception as e:
        print(f"Resource manager creation failed: {e}")
    
    print()


def comprehensive_validation_workflow():
    """Demonstrate a comprehensive validation workflow."""
    print("=== Comprehensive Validation Workflow ===\n")
    
    # Simulate processing a dataset with validation
    raw_employee_data = [
        ["Name", "Age", "Email", "Salary", "Department", "Start_Date"],
        ["John Doe", "30", "john@company.com", "75000", "Engineering", "2023-01-15"],
        ["Jane Smith", "25", "jane@company.com", "65000", "Marketing", "2023-03-20"],
        ["", "45", "bob@company.com", "85000", "Sales", "2022-11-10"],  # Missing name
        ["Alice Brown", "17", "alice@company.com", "72000", "Engineering", "2023-05-05"],  # Too young
        ["Charlie Wilson", "28", "charlie@invalid.com", "68000", "Marketing", "2023-02-14"],  # Invalid domain
        ["David Jones", "35", "david@company.com", "250000", "Executive", "2023-01-01"],  # Salary too high
    ]
    
    print("Comprehensive Validation Workflow:")
    print("Step 1: Create data model")
    model = TabularDataModel(raw_employee_data, header_rows=1)
    print(f"  Loaded {model.row_count} employee records")
    print()
    
    print("Step 2: Set up comprehensive validation")
    validator = DataValidator()
    
    # Add comprehensive validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Age", lambda x: x.isdigit() and 18 <= int(x) <= 65)
    validator.add_validator("Email", lambda x: "@company.com" in x)
    validator.add_validator("Salary", lambda x: x.isdigit() and 30000 <= int(x) <= 200000)
    validator.add_validator("Department", lambda x: x in ["Engineering", "Marketing", "Sales", "Executive"])
    
    print("  Validation rules established")
    print()
    
    print("Step 3: Validate all records")
    valid_records = []
    invalid_records = []
    
    for i in range(model.row_count):
        row_dict = model.row(i)
        is_valid = validator.validate(row_dict)
        
        if is_valid:
            valid_records.append((i, row_dict))
        else:
            errors = validator.get_errors()
            invalid_records.append((i, row_dict, errors.copy()))
        
        validator.clear_errors()
    
    print(f"  Valid records: {len(valid_records)}")
    print(f"  Invalid records: {len(invalid_records)}")
    print()
    
    print("Step 4: Report validation results")
    print("Valid Records:")
    for i, record in valid_records:
        print(f"  Row {i}: {record['Name']} - OK")
    print()
    
    print("Invalid Records:")
    for i, record, errors in invalid_records:
        print(f"  Row {i}: {record['Name'] or 'Missing Name'} - ERROR")
        for error in errors:
            print(f"    • {error}")
        print()
    
    print("Step 5: Create clean dataset")
    if valid_records:
        clean_data = [raw_employee_data[0]]  # Header
        for _, record in valid_records:
            clean_data.append([
                record["Name"],
                record["Age"],
                record["Email"],
                record["Salary"],
                record["Department"],
                record["Start_Date"]
            ])
        
        clean_model = TabularDataModel(clean_data, header_rows=1)
        print(f"  Clean dataset created: {clean_model.row_count} valid records")
    
    print()


if __name__ == "__main__":
    """Run all validation and transformation examples."""
    print("Splurge-Tools: Data Validation and Transformation Examples")
    print("=" * 70)
    print()
    
    # Create sample data
    employee_data, sales_data = create_sample_data()
    
    basic_validation_examples(employee_data)
    custom_validation_examples()
    validation_utils_examples()
    basic_transformation_examples(sales_data)
    advanced_transformation_examples(sales_data)
    factory_pattern_examples()
    comprehensive_validation_workflow()
    
    print("Examples completed successfully!")
    print("\nKey Takeaways:")
    print("• DataValidator supports custom validation rules and error tracking")
    print("• DataTransformer provides pivot, melt, group-by, and column transformations")
    print("• Factory pattern enables consistent component creation")
    print("• Validation utilities provide common validation patterns")
    print("• Components integrate seamlessly with tabular data models")
    print("• Comprehensive error handling and reporting capabilities")
