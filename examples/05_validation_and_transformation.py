#!/usr/bin/env python3
"""
Data Validation and Transformation Examples

This example demonstrates the data validation and transformation capabilities
of splurge-tools, including custom validation rules, data transformations,
and factory pattern usage.

Copyright (c) 2025 Jim Schilling
Licensed under the MIT License.
"""

import contextlib

from splurge_tools.data_transformer import DataTransformer
from splurge_tools.data_validator import DataValidator
from splurge_tools.exceptions import SplurgeParameterError, SplurgeRangeError
from splurge_tools.tabular_data_model import TabularDataModel


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

    # Create validator directly
    validator = DataValidator()

    # Add validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Age", lambda x: x.isdigit() and 18 <= int(x) <= 65)
    validator.add_validator("Email", lambda x: "@" in x and "." in x)
    validator.add_validator("Salary", lambda x: x.isdigit() and int(x) > 0)

    # Create tabular model and validate each row
    model = TabularDataModel(employee_data, header_rows=1)

    for i in range(model.row_count):
        row_dict = model.row(i)
        is_valid = validator.validate(row_dict)

        if not is_valid:
            errors = validator.get_errors()
            for _error in errors:
                pass

        validator.clear_errors()


def custom_validation_examples():
    """Demonstrate custom validation scenarios."""

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
            "Department": "Engineering",
        },
        {
            "Name": "",  # Invalid: empty name
            "Age": "25",
            "Email": "test@example.com",
            "Salary": "65000",
            "Department": "Marketing",
        },
        {
            "Name": "Invalid Domain",
            "Age": "35",
            "Email": "user@invalid.com",  # Invalid: wrong domain
            "Salary": "80000",
            "Department": "Sales",
        },
        {
            "Name": "Too Young",
            "Age": "15",  # Invalid: too young
            "Email": "young@example.com",
            "Salary": "40000",
            "Department": "Intern",
        },
        {
            "Name": "Low Salary",
            "Age": "28",
            "Email": "low@example.com",
            "Salary": "25000",  # Invalid: too low
            "Department": "Entry",
        },
    ]

    # Apply validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Email", validate_email_domain)
    validator.add_validator("Age", validate_age_group)
    validator.add_validator("Salary", validate_salary_range)

    for _i, test_case in enumerate(test_cases):
        is_valid = validator.validate(test_case)

        if not is_valid:
            errors = validator.get_errors()
            for _error in errors:
                pass

        validator.clear_errors()


def validation_utils_examples():
    """Demonstrate validation utilities."""

    # Test various validation utilities
    def test_non_empty_string():
        value = "hello"
        if not isinstance(value, str):
            msg = "test_param must be a string"
            raise SplurgeParameterError(msg)
        if not value.strip():
            msg = "test_param must be a non-empty string"
            raise SplurgeParameterError(msg)
        return value

    def test_empty_string():
        value = ""
        if not isinstance(value, str):
            msg = "test_param must be a string"
            raise SplurgeParameterError(msg)
        if not value.strip():
            msg = "test_param must be a non-empty string"
            raise SplurgeParameterError(msg)
        return value

    def test_positive_integer():
        value = 42
        if not isinstance(value, int):
            msg = "test_param must be an integer"
            raise SplurgeParameterError(msg)
        if value < 1:
            msg = "test_param must be >= 1"
            raise SplurgeRangeError(msg)
        return value

    def test_negative_integer():
        value = -5
        if not isinstance(value, int):
            msg = "test_param must be an integer"
            raise SplurgeParameterError(msg)
        if value < 1:
            msg = "test_param must be >= 1"
            raise SplurgeRangeError(msg)
        return value

    def test_valid_range():
        lower, upper = 1, 10
        if lower >= upper:
            msg = "lower must be < upper"
            raise SplurgeRangeError(msg)
        return (lower, upper)

    def test_invalid_range():
        lower, upper = 10, 1
        if lower >= upper:
            msg = "lower must be < upper"
            raise SplurgeRangeError(msg)
        return (lower, upper)

    def test_valid_encoding():
        value = "utf-8"
        if not isinstance(value, str):
            msg = "test_param must be a string"
            raise SplurgeParameterError(msg)
        if not value.strip():
            msg = "test_param must be a non-empty string"
            raise SplurgeParameterError(msg)
        return value

    def test_invalid_encoding():
        value = "invalid-encoding"
        if not isinstance(value, str):
            msg = "test_param must be a string"
            raise SplurgeParameterError(msg)
        if not value.strip():
            msg = "test_param must be a non-empty string"
            raise SplurgeParameterError(msg)
        return value

    validation_tests = [
        ("Non-empty string", test_non_empty_string),
        ("Empty string (should fail)", test_empty_string),
        ("Positive integer", test_positive_integer),
        ("Negative integer (should fail)", test_negative_integer),
        ("Valid range bounds", test_valid_range),
        ("Invalid range bounds (should fail)", test_invalid_range),
        ("Valid encoding", test_valid_encoding),
        ("Invalid encoding (should fail)", test_invalid_encoding),
    ]

    for _test_name, test_func in validation_tests:
        with contextlib.suppress(Exception):
            test_func()


def basic_transformation_examples(sales_data):
    """Demonstrate basic data transformation capabilities."""

    # Create data model and transformer
    model = TabularDataModel(sales_data, header_rows=1)
    transformer = DataTransformer(model)

    for _i in range(min(3, model.row_count)):
        pass

    # Pivot transformation
    try:
        pivoted = transformer.pivot(
            index_cols=["Product"],
            columns_col="Region",
            values_col="Sales",
            agg_func=lambda values: str(sum(int(v) for v in values)),
        )
        for _i in range(min(3, pivoted.row_count)):
            pass
    except Exception:
        pass

    # Group by transformation
    try:
        grouped = transformer.group_by(
            group_cols=["Category"],
            agg_dict={"Sales": lambda values: str(sum(int(v) for v in values))},
        )
        for _i in range(grouped.row_count):
            pass
    except Exception:
        pass


def advanced_transformation_examples(sales_data):
    """Demonstrate advanced transformation scenarios."""

    model = TabularDataModel(sales_data, header_rows=1)
    transformer = DataTransformer(model)

    # Column transformation
    try:
        # Transform sales values to include tax
        def add_tax(value):
            try:
                return str(int(value) * 1.08)  # 8% tax
            except (ValueError, TypeError):
                return value

        transformed = transformer.transform_column(
            column="Sales",
            transform_func=add_tax,
        )

        for i in range(min(3, transformed.row_count)):
            transformed.row(i)
    except Exception:
        pass

    # Melt transformation
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
            value_name="Sales",
        )

        for i in range(min(6, melted.row_count)):
            pass
    except Exception:
        pass


def factory_pattern_examples():
    """Demonstrate simple explicit construction usage (no factories)."""
    DataValidator()
    sample_data = [["Name", "Value"], ["A", "1"], ["B", "2"]]
    model = TabularDataModel(sample_data, header_rows=1)
    DataTransformer(model)


def comprehensive_validation_workflow():
    """Demonstrate a comprehensive validation workflow."""

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

    model = TabularDataModel(raw_employee_data, header_rows=1)

    validator = DataValidator()

    # Add comprehensive validation rules
    validator.add_validator("Name", lambda x: len(x.strip()) > 0)
    validator.add_validator("Age", lambda x: x.isdigit() and 18 <= int(x) <= 65)
    validator.add_validator("Email", lambda x: "@company.com" in x)
    validator.add_validator("Salary", lambda x: x.isdigit() and 30000 <= int(x) <= 200000)
    validator.add_validator("Department", lambda x: x in ["Engineering", "Marketing", "Sales", "Executive"])

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

    for i, record in valid_records:
        pass

    for i, record, errors in invalid_records:
        for _error in errors:
            pass

    if valid_records:
        clean_data = [raw_employee_data[0]]  # Header
        for _, record in valid_records:
            clean_data.append(
                [
                    record["Name"],
                    record["Age"],
                    record["Email"],
                    record["Salary"],
                    record["Department"],
                    record["Start_Date"],
                ],
            )

        TabularDataModel(clean_data, header_rows=1)


if __name__ == "__main__":
    """Run all validation and transformation examples."""

    # Create sample data
    employee_data, sales_data = create_sample_data()

    basic_validation_examples(employee_data)
    custom_validation_examples()
    validation_utils_examples()
    basic_transformation_examples(sales_data)
    advanced_transformation_examples(sales_data)
    factory_pattern_examples()
    comprehensive_validation_workflow()
